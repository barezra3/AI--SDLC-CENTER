import streamlit as st
import pandas as pd
import plotly.express as px
from main import fetch_tasks, analyze_tasks_advanced, generate_prd_for_task, update_jira_task_description, ai_query, \
    security_compliance_scan, generate_release_notes, map_tasks_to_iso27001

# --- CONFIGURATION ---
st.set_page_config(page_title="AI-SDLC Command Center", layout="wide", page_icon="🛡️")

# --- HEADER ---
st.title("🛡️ AI-SDLC Command Center")
st.markdown("Enterprise Grade AI for Agile Project Management")
st.markdown("---")

# --- SIDEBAR CONTROLS ---
with st.sidebar:
    st.header("🕹️ Controls")
    project_key = st.text_input("Jira Project Key", "KAN")
    selected_lang = st.selectbox("AI Response Language", ["English", "Hebrew"])
    view_option = st.radio("Navigation", ("Risk Heatmap", "Delivery Gantt Chart", "Task Distribution (Bar Chart)"))

    # שימוש בעיצוב כפתור מובנה של Streamlit (צבע הדגש של המערכת)
    fetch_button = st.button("🚀 Sync & Analyze", use_container_width=True, type="primary")

    st.divider()
    st.header("💬 Project AI Assistant")
    user_q = st.text_input("Ask AI about the project:")
    if user_q and 'df' in st.session_state:
        with st.spinner("Analyzing..."):
            context = st.session_state['df'].to_string()
            answer = ai_query(f"Context: {context}. Question: {user_q} (Answer in {selected_lang})")
            st.write(answer)

# --- MAIN CONTENT ---
if fetch_button:
    st.session_state['df'] = fetch_tasks(project_key)

if 'df' in st.session_state:
    df = st.session_state['df']

    # 1. Metrics
    st.subheader("📊 Sprint Overview")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Tasks", len(df))
    c2.metric("Avg Days Open", round(df['Days_Open'].mean(), 1))
    c3.metric("Critical Risks", len(df[df['Priority'] == 'High']))
    completed_tasks = len(df[df['Status'].str.contains('Done|Closed|Resolved', case=False, na=False)])
    c4.metric("Completed Tasks", completed_tasks)

    st.divider()

    # הנה תצוגת הנתונים המלאה והברורה!
    with st.expander("📁 View Raw Jira Data", expanded=True):
        st.dataframe(df, use_container_width=True)

    st.divider()

    # 2. Visualizations
    if view_option == "Risk Heatmap":
        st.subheader("🔥 Risk Heatmap")
        fig = px.density_heatmap(df, x="Status", y="Priority", z="Days_Open", histfunc="avg",
                                 color_continuous_scale="Reds", text_auto=True)
        st.plotly_chart(fig, use_container_width=True)

    elif view_option == "Delivery Gantt Chart":
        st.subheader("📅 Delivery Gantt Chart")
        gantt_df = df.copy()
        gantt_df['Start'] = pd.to_datetime(gantt_df['Start'], utc=True).dt.tz_localize(None)
        gantt_df['Finish'] = pd.to_datetime(gantt_df['Finish'], utc=True).dt.tz_localize(None)
        fig = px.timeline(gantt_df, x_start="Start", x_end="Finish", y="Summary", color="Assignee",
                          title="Project Schedule")
        fig.update_yaxes(autorange="reversed")
        st.plotly_chart(fig, use_container_width=True)

    elif view_option == "Task Distribution (Bar Chart)":
        st.subheader("📊 Task Distribution")
        fig = px.bar(df, x="Status", color="Priority", barmode="group", title="Task Count by Status")
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # 3. TABS
    t1, t2, t3, t4 = st.tabs(["🤖 Multi-Agent Board", "📝 PRD Generator", "🛡️ Security Scanner", "🚀 Release Notes"])

    with t1:
        st.subheader(f"🧠 AI Board of Directors ({selected_lang})")
        st.write(
            "This tab simulates 3 specialized AI agents (Security, Delivery, Product) analyzing your Jira board simultaneously.")
        if st.button("Convene Board Meeting", use_container_width=True):
            with st.spinner("Agents are analyzing the sprint data..."):
                board_report = analyze_tasks_advanced(df, language=selected_lang)
                st.markdown(board_report)

    with t2:
        st.subheader(f"AI PRD Generator ({selected_lang})")
        sel_task = st.selectbox("Select Task:", df['Summary'].tolist())

        c_prd1, c_prd2 = st.columns([3, 1])
        with c_prd1:
            if st.button("Generate & Review PRD", use_container_width=True):
                row = df[df['Summary'] == sel_task].iloc[0]
                st.session_state['current_id'] = row['ID']
                st.session_state['prd'] = generate_prd_for_task(row['Summary'], row['Description'],
                                                                language=selected_lang)

        if 'prd' in st.session_state:
            new_prd = st.text_area("Edit PRD Content:", st.session_state['prd'], height=300)

            c_prd3, c_prd4 = st.columns(2)
            with c_prd3:
                st.download_button(
                    label="📥 Download PRD (Markdown)",
                    data=new_prd,
                    file_name=f"PRD_{st.session_state['current_id']}.md",
                    mime="text/markdown",
                    use_container_width=True
                )
            with c_prd4:
                if st.button(f"Push to Jira ({st.session_state['current_id']})", use_container_width=True):
                    if update_jira_task_description(st.session_state['current_id'], new_prd):
                        st.success("Jira Updated Successfully!")
                    else:
                        st.error("Failed to sync.")

        # להוסיף את הייבוא למעלה:
        # from main import map_tasks_to_iso27001

        with t3:  # מחליף או משדרג את טאב האבטחה הקיים
            st.subheader(f"📋 ISO 27001 Audit Mapper ({selected_lang})")
            st.markdown("Automated Evidence Collection for GRC Teams. Maps sprint tasks to ISO controls.")

            if st.button("Generate Audit-Ready Report", use_container_width=True, type="primary"):
                with st.spinner("Analyzing Jira context against ISO 27001 framework..."):
                    audit_report = map_tasks_to_iso27001(df, language=selected_lang)
                    st.markdown(audit_report)

                    st.download_button(
                        label="📥 Download Evidence Report (Markdown)",
                        data=audit_report,
                        file_name="ISO27001_Sprint_Evidence.md",
                        mime="text/markdown",
                        use_container_width=True
                    )

    with t4:
        st.subheader(f"🚀 Marketing Release Notes ({selected_lang})")
        st.write("Automatically generate customer-facing release notes from completed sprint tasks.")
        if st.button("Generate Release Update", use_container_width=True):
            with st.spinner("Drafting release notes..."):
                release_notes = generate_release_notes(df, language=selected_lang)
                st.markdown(release_notes)
                st.download_button(
                    label="📥 Download Release Notes (Markdown)",
                    data=release_notes,
                    file_name="release_notes.md",
                    mime="text/markdown",
                    use_container_width=True
                )
if 'df' in st.session_state:
    df = st.session_state['df']

    # 1. Metrics
    st.subheader("📊 Sprint Overview")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Tasks", len(df))
    c2.metric("Avg Days Open", round(df['Days_Open'].mean(), 1))
    c3.metric("Critical Risks", len(df[df['Priority'] == 'High']))
    completed_tasks = len(df[df['Status'].str.contains('Done|Closed|Resolved', case=False, na=False)])
    c4.metric("Completed Tasks", completed_tasks)

    st.divider()

    # הנה תצוגת הנתונים המלאה והברורה!
    with st.expander("📁 View Raw Jira Data", expanded=True):
        st.dataframe(df, use_container_width=True)

    st.divider()

    # 2. Visualizations
    if view_option == "Risk Heatmap":
        st.subheader("🔥 Risk Heatmap")
        fig = px.density_heatmap(df, x="Status", y="Priority", z="Days_Open", histfunc="avg",
                                 color_continuous_scale="Reds", text_auto=True)
        st.plotly_chart(fig, use_container_width=True)

    elif view_option == "Delivery Gantt Chart":
        st.subheader("📅 Delivery Gantt Chart")
        gantt_df = df.copy()
        gantt_df['Start'] = pd.to_datetime(gantt_df['Start'], utc=True).dt.tz_localize(None)
        gantt_df['Finish'] = pd.to_datetime(gantt_df['Finish'], utc=True).dt.tz_localize(None)
        fig = px.timeline(gantt_df, x_start="Start", x_end="Finish", y="Summary", color="Assignee",
                          title="Project Schedule")
        fig.update_yaxes(autorange="reversed")
        st.plotly_chart(fig, use_container_width=True)

    elif view_option == "Task Distribution (Bar Chart)":
        st.subheader("📊 Task Distribution")
        fig = px.bar(df, x="Status", color="Priority", barmode="group", title="Task Count by Status")
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # 3. TABS
    t1, t2, t3, t4 = st.tabs(["🤖 Multi-Agent Board", "📝 PRD Generator", "🛡️ Security Scanner", "🚀 Release Notes"])

    with t1:
        st.subheader(f"🧠 AI Board of Directors ({selected_lang})")
        st.write(
            "This tab simulates 3 specialized AI agents (Security, Delivery, Product) analyzing your Jira board simultaneously.")
        if st.button("Convene Board Meeting", use_container_width=True):
            with st.spinner("Agents are analyzing the sprint data..."):
                board_report = analyze_tasks_advanced(df, language=selected_lang)
                st.markdown(board_report)

    with t2:
        st.subheader(f"AI PRD Generator ({selected_lang})")
        sel_task = st.selectbox("Select Task:", df['Summary'].tolist())

        c_prd1, c_prd2 = st.columns([3, 1])
        with c_prd1:
            if st.button("Generate & Review PRD", use_container_width=True):
                row = df[df['Summary'] == sel_task].iloc[0]
                st.session_state['current_id'] = row['ID']
                st.session_state['prd'] = generate_prd_for_task(row['Summary'], row['Description'],
                                                                language=selected_lang)

        if 'prd' in st.session_state:
            new_prd = st.text_area("Edit PRD Content:", st.session_state['prd'], height=300)

            c_prd3, c_prd4 = st.columns(2)
            with c_prd3:
                st.download_button(
                    label="📥 Download PRD (Markdown)",
                    data=new_prd,
                    file_name=f"PRD_{st.session_state['current_id']}.md",
                    mime="text/markdown",
                    use_container_width=True
                )
            with c_prd4:
                if st.button(f"Push to Jira ({st.session_state['current_id']})", use_container_width=True):
                    if update_jira_task_description(st.session_state['current_id'], new_prd):
                        st.success("Jira Updated Successfully!")
                    else:
                        st.error("Failed to sync.")

    with t3:
        st.subheader(f"🛡️ Security & Compliance Audit ({selected_lang})")
        if st.button("Run Security Scan", use_container_width=True):
            with st.spinner("Auditing Jira data for vulnerabilities..."):
                report = security_compliance_scan(df, language=selected_lang)
                if "No immediate" in report:
                    st.success(report)
                else:
                    st.error("⚠️ Security Risks Identified:")
                    st.markdown(report)

    with t4:
        st.subheader(f"🚀 Marketing Release Notes ({selected_lang})")
        st.write("Automatically generate customer-facing release notes from completed sprint tasks.")
        if st.button("Generate Release Update", use_container_width=True):
            with st.spinner("Drafting release notes..."):
                release_notes = generate_release_notes(df, language=selected_lang)
                st.markdown(release_notes)
                st.download_button(
                    label="📥 Download Release Notes (Markdown)",
                    data=release_notes,
                    file_name="release_notes.md",
                    mime="text/markdown",
                    use_container_width=True
                )
