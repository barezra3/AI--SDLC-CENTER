# 🛡️ AI-Driven GRC & SDLC Command Center

An Enterprise-Grade AI Dashboard designed to bridge the gap between R&D execution (Jira) and external Compliance requirements (ISO 27001), while streamlining Product Management workflows. 

Built with **Python, Streamlit, and Gemini AI**, and fully containerized via **Docker** for secure, local deployment.

## 🎯 The Problem it Solves
In modern Enterprise and Scale-up environments, there is a massive disconnect between engineering activity and compliance tracking. GRC teams spend weeks manually chasing developers for "Evidence" prior to audits (SOC2, ISO 27001). Meanwhile, Product Managers drown in Jira chaos, struggling to extract strategic insights, write PRDs, and draft release notes manually.

## 💡 The Solution (Core Features)

### 1. 📋 Automated GRC Evidence Mapper (ISO 27001)
* **The Killer Feature:** Transforms raw Jira engineering tickets into Audit-Ready evidence.
* The AI filters out non-security tasks, identifies relevant infrastructure/security tickets, and **automatically maps them to specific ISO 27001 Annex A controls** (e.g., A.9.2.1, A.10.1).
* Generates a structured table with an "Auditor Justification" explaining exactly *why* the ticket serves as valid evidence.

### 2. 🧠 AI Board of Directors (Persona Multiplexing)
* Instead of standard AI summarization, this tool utilizes **Persona Multiplexing**. 
* A single API call splits the LLM into three distinct expert agents: a **CISO** (Security), a **Scrum Master** (Delivery), and a **VP Product** (Business Value). 
* They collaboratively analyze the active sprint and output actionable, cross-functional recommendations.

### 3. 📝 Instant Product & GTM Asset Generator
* **PRD Generator:** Select any high-level Jira epic/task, and the AI instantly generates a comprehensive Product Requirements Document.
* **Release Notes:** Automatically drafts customer-facing, marketing-ready release notes based on closed sprint tasks.
* **UX First:** All AI-generated assets are editable and can be downloaded instantly as structured Markdown (`.md`) files.

### 4. 📊 Real-Time Sprint Analytics
* Visualizes Jira workloads using dynamic Plotly charts (Risk Heatmaps, Gantt charts, Status distributions) for immediate situational awareness.

## 🏗️ Architecture & Tech Stack
* **Frontend:** Streamlit (Custom B2B clean UI)
* **Backend & Logic:** Python, Pandas (Data manipulation)
* **AI Engine:** Google Gemini AI (via API)
* **Integration:** Jira REST API (Atlassian)
* **Infrastructure:** Docker (Fully containerized for security and multi-environment consistency)

## 🚀 How to Run Locally (Docker)

To run this application securely on your local machine, ensure you have Docker Desktop installed and running.

**1. Clone the repository:**
```bash
git clone [https://github.com/YOUR_USERNAME/ai-sdlc-command-center.git](https://github.com/YOUR_USERNAME/ai-sdlc-command-center.git)
cd ai-sdlc-command-center
