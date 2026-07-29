# TalentMatch AI – Autonomous Recruiting Agent

## Overview

TalentMatch AI is an intelligent recruitment platform that streamlines the hiring process using Artificial Intelligence, semantic search, and autonomous agent workflows. The system enables recruiters to upload resumes, manage job postings, search candidates using vector similarity, and automatically generate hiring recommendations.

The project integrates **FastAPI**, **LangGraph**, **ChromaDB**, **Streamlit**, and **Large Language Models (LLMs)** to build an end-to-end AI-powered recruitment assistant capable of planning, searching, evaluating, and reporting with minimal human intervention.

---

## Key Features

### Resume Management
- Upload and parse PDF resumes
- Extract candidate information automatically
- Generate and store vector embeddings in ChromaDB
- Semantic resume retrieval

### Job Management
- Create and manage job postings
- Upload job descriptions
- Evaluate job quality
- Generate AI-powered job improvement suggestions

### Intelligent Candidate Search
- Semantic candidate matching
- Metadata-based filtering
- Similarity score ranking
- Candidate profile summaries

### Autonomous Recruiting Agent
- Accepts recruiter goals in natural language
- Automatically selects the appropriate job posting
- Retrieves job requirements
- Searches candidates using semantic similarity
- Evaluates and ranks candidates
- Performs adaptive planning and search expansion
- Generates AI-based candidate summaries
- Creates tailored interview questions
- Performs self-validation before finalizing recommendations
- Reviews job posting quality
- Produces a comprehensive hiring report with execution trace

---

# System Architecture

```
Recruiter Goal
       │
       ▼
Job Selection
       │
       ▼
Requirement Extraction
       │
       ▼
Semantic Candidate Search
       │
       ▼
Candidate Evaluation
       │
       ▼
Candidate Summaries
       │
       ▼
Interview Question Generation
       │
       ▼
Self Validation
       │
       ▼
Hiring Report
```

---

# Technology Stack

## Backend
- Python
- FastAPI
- SQLAlchemy
- SQLite

## Artificial Intelligence
- LangGraph
- ChromaDB
- HuggingFace Embeddings
- Sentence Transformers
- Groq LLM

## Frontend
- Streamlit

## Vector Database
- ChromaDB

---

# Project Structure

```
TalentMatch-AI/
│
├── app/
│   ├── agent/
│   │   ├── planner_node.py
│   │   ├── search_node.py
│   │   ├── evaluator_node.py
│   │   ├── summary_node.py
│   │   ├── interview_node.py
│   │   ├── self_check_node.py
│   │   ├── report_node.py
│   │   ├── agent_runner.py
│   │   └── tools.py
│   │
│   ├── database.py
│   ├── services.py
│   ├── rag.py
│   ├── schemas.py
│   ├── utils.py
│   ├── config.py
│   └── main.py
│
├── chroma_db/
├── data/
├── frontend/
├── scripts/
├── tests/
├── uploads/
│
├── requirements.txt
├── README.md
└── .env
```

---

# Installation

## Clone the Repository

```bash
git clone https://github.com/your-username/TalentMatch-AI.git

cd TalentMatch-AI
```

---

## Create a Virtual Environment

```bash
python -m venv venv
```

Windows

```bash
venv\Scripts\activate
```

Linux/macOS

```bash
source venv/bin/activate
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Configure Environment Variables

Create a `.env` file in the project root.

```env
GROQ_API_KEY=your_api_key
```

---

# Running the Application

## Start the FastAPI Backend

```bash
uvicorn app.main:app --reload
```

Backend URL

```
http://127.0.0.1:8000
```

---

## Launch the Streamlit Interface

```bash
streamlit run frontend/streamlit_app.py
```

---

# API Endpoints

| Module | Endpoint |
|---------|----------|
| Upload Resume | POST `/resume` |
| Upload Job | POST `/upload-job` |
| Create Job | POST `/jobs` |
| Search Candidates | POST `/search` |
| Candidate Summary | GET `/candidate/{candidate_id}/summary` |
| Interview Questions | GET `/jobs/{job_id}/candidates/{candidate_id}/interview-questions` |
| Improve Job | GET `/jobs/{job_id}/improve` |
| Job Quality | POST `/job-quality` |
| AI Recruiting Agent | POST `/agent/fill-role` |
| Agent Status | GET `/agent/runs/{run_id}` |

---

# Autonomous Recruiting Workflow

The AI Recruiting Agent follows a structured multi-step workflow:

1. Recruiter submits a hiring goal.
2. The Planner Node analyzes the goal and creates an adaptive execution plan.
3. The Search Node retrieves the relevant job requirements and performs semantic candidate search.
4. The Evaluator Node ranks candidates based on similarity scores and recruiter priorities.
5. The Summary Node generates concise candidate summaries.
6. The Interview Node creates role-specific interview questions.
7. The Self-Check Node validates the shortlist and refines recommendations.
8. The Report Node compiles a comprehensive hiring report.

---

# Sample Hiring Report

```
Recruiter Goal
--------------
Hire an experienced Frontend React Developer.

Workflow Status
---------------
Completed

Top Candidates
--------------
Ali Ahmed
Similarity Score: 94%

Sara Khan
Similarity Score: 91%

Usman Ali
Similarity Score: 89%

Job Quality
-----------
Good

Execution Trace
---------------
✓ Planning
✓ Candidate Search
✓ Evaluation
✓ Summary Generation
✓ Interview Question Generation
✓ Self Validation
✓ Final Report
```

---

# Future Enhancements

- User authentication and authorization
- PostgreSQL integration
- Docker containerization
- Cloud deployment (AWS/Azure)
- OCR-based resume parsing
- Email interview scheduling
- Recruiter analytics dashboard
- Batch candidate evaluation
- Multi-language resume support

---

# Author

**Rahima Qamar**

Software Engineering Student

TalentMatch AI – Autonomous Recruiting Agent

---

# License

This project is intended for educational, research, and demonstration purposes.