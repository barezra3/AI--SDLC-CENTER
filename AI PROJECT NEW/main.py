import os
import pandas as pd
import requests
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
from jira import JIRA
import time

load_dotenv()


def get_jira_connection():
    # אנחנו מגדירים לו מפורשות להשתמש בגרסה 3 החדשה של ג'ירה
    jira_options = {
        'server': os.getenv('JIRA_URL'),
        'rest_api_version': '3'
    }
    return JIRA(
        options=jira_options,
        basic_auth=(os.getenv('JIRA_EMAIL'), os.getenv('JIRA_TOKEN'))
    )


def fetch_tasks(project_key):
    jira = get_jira_connection()
    issues = jira.search_issues(f'project="{project_key}"', expand='changelog')
    tasks = []
    for issue in issues:
        priority = issue.fields.priority.name if issue.fields.priority else "Medium"
        assignee = str(issue.fields.assignee) if issue.fields.assignee else "Unassigned"
        status = issue.fields.status.name if issue.fields.status else "Unknown"
        all_comments = jira.comments(issue)
        comments_text = " | ".join([str(c.raw.get('body', '')) for c in all_comments]) if all_comments else "No comments"
        start_date = pd.to_datetime(issue.fields.created)
        due_date = pd.to_datetime(issue.fields.duedate) if issue.fields.duedate else start_date + timedelta(days=7)
        days_open = (pd.to_datetime('now', utc=True) - start_date).days
        tasks.append({
            "ID": issue.key,
            "Summary": issue.fields.summary,
            "Description": str(issue.fields.description) or "",
            "Status": status,
            "Priority": priority,
            "Days_Open": max(0, days_open),
            "Comments": comments_text,
            "Assignee": assignee,
            "Start": start_date,
            "Finish": due_date
        })
    return pd.DataFrame(tasks)


def ai_query(prompt, retries=3):
    api_key = os.getenv('GEMINI_API_KEY')
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    for i in range(retries):
        try:
            response = requests.post(url, headers={'Content-Type': 'application/json'}, data=json.dumps(payload))
            res_json = response.json()
            if 'candidates' in res_json:
                return res_json['candidates'][0]['content']['parts'][0]['text']
            if "high demand" in str(res_json).lower():
                time.sleep(2)
                continue
            return f"⚠️ AI Error: {res_json}"
        except Exception as e:
            return f"❌ Connection Error: {e}"
    return "❌ Server Busy."


def analyze_tasks_advanced(tasks_df, language="English"):
    """
    Multi-Agent prompt implementation using the original function name.
    """
    context = tasks_df[['ID', 'Summary', 'Status', 'Days_Open', 'Priority', 'Assignee']].to_string()
    lang_inst = "Hebrew" if language == "Hebrew" else "English"

    prompt = f"""
    You are an AI orchestrator managing a 'Board of Directors' meeting for a software sprint.
    Analyze the following Jira tasks:
    {context}

    I need 3 distinct expert agents to provide their analysis, followed by an executive summary.

    Act as these 3 personas:
    1. 🛡️ The CISO (Security Agent): Point out any tasks that sound like they have security implications, compliance risks, or need architectural review.
    2. ⏱️ The Scrum Master (Delivery Agent): Identify bottlenecks, overloaded developers (Assignees), and tasks that are open for too long.
    3. 🎯 The VP Product (Value Agent): Assess the priority alignment. Are we focusing on high-value items? What is the core value being delivered?

    Structure the output with clear headings for each Agent's report.
    Finally, add a '🧠 Executive Synthesis' section that combines their insights into 3 actionable bullet points.

    Write the entire response strictly in {lang_inst}.
    """
    return ai_query(prompt)


def generate_prd_for_task(task_summary, task_description, language="English"):
    lang_inst = "Hebrew" if language == "Hebrew" else "English"
    prompt = f"Write a professional PRD in {lang_inst} for: {task_summary}. Description: {task_description}."
    return ai_query(prompt)


def security_compliance_scan(tasks_df, language="English"):
    context = tasks_df[['ID', 'Summary', 'Description', 'Comments']].to_string()
    lang_inst = "Hebrew" if language == "Hebrew" else "English"
    prompt = f"""
    You are a Senior Cyber Security Analyst. Scan the following Jira data for security risks:
    {context}
    Identify: Leaked credentials, vulnerable protocols, or privacy issues.
    Return analysis in {lang_inst}. If safe, say 'No immediate security risks detected.'
    """
    return ai_query(prompt)


def generate_release_notes(tasks_df, language="English"):
    completed = tasks_df[tasks_df['Status'].str.contains('Done|Closed|Resolved', case=False, na=False)]
    if completed.empty:
        return "No completed tasks found in this sprint. Keep pushing! 🚀"

    context = completed[['ID', 'Summary', 'Description']].to_string()
    lang_inst = "Hebrew" if language == "Hebrew" else "English"
    prompt = f"""
    You are an expert Product Marketing Manager. We just finished a sprint. 
    Here are the completed Jira tasks:
    {context}

    Write an engaging, customer-facing 'Release Notes' update. 
    Structure it with:
    1. 🚀 What's New (Exciting features)
    2. 🛠️ Bug Fixes & Improvements

    Format as a ready-to-send Slack/Email message. Write entirely in {lang_inst}.
    """
    return ai_query(prompt)


def update_jira_task_description(issue_key, new_description):
    try:
        jira = get_jira_connection()
        issue = jira.issue(issue_key)
        issue.update(description=new_description)
        return True
    except:
        return False