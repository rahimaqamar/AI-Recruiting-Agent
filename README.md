# recruiter-match
this is our second project
# TalentMatch AI

TalentMatch AI is an AI-powered recruitment system that allows recruiters to search resumes using natural language instead of exact keywords.

The project uses:

- FastAPI
- Streamlit
- LangChain
- ChromaDB
- HuggingFace Embeddings
- Groq LLM
- SQLite
- RAG (Retrieval-Augmented Generation)

---

# Features

## Module 1 – Semantic Resume Search

- Upload PDF resumes
- Store embeddings in ChromaDB
- Semantic search
- Metadata filters
- Similarity score
- AI explanation

---

## Module 2 – Candidate Summary

Generate

- Candidate strengths
- Weaknesses
- Best roles

using Groq LLM.

---

## Module 3 – Interview Questions

Generate personalized interview questions based on

- Candidate Resume
- Job Description

---

## Module 4 – Job Description Improvement

Analyze a job description and suggest improvements using recruiter AI.

---

## Module 5

Reserved.

---

## Module 6 – Conversation Memory

Store recruiter conversations using SQLite.

---

# Technologies

- Python
- FastAPI
- Streamlit
- LangChain
- ChromaDB
- HuggingFace
- Groq
- SQLite
- PyMuPDF

---

# Project Structure

```
TalentMatch-AI/

│── app.py

│── config.py

│── database.py

│── llm.py

│── rag.py

│── schemas.py

│── services.py

│── streamlit_app.py

│── utils.py

│── requirements.txt

│── .env

│── uploads/

│── chroma_db/

│── data/

└── tests/
```

---

# Installation

## Create Virtual Environment

```
python -m venv venv
```

Activate

Windows

```
venv\Scripts\activate
```

Linux

```
source venv/bin/activate
```

---

## Install Packages

```
pip install -r requirements.txt
```

---

## Configure API Key

Create

```
.env
```

Add

```
GROQ_API_KEY=YOUR_GROQ_API_KEY
```

---

# Run FastAPI

```
uvicorn app:app --reload
```

Swagger

```
http://127.0.0.1:8000/docs
```

---

# Run Streamlit

```
streamlit run streamlit_app.py
```

---

# API Endpoints

| Method | Endpoint |
|---------|----------|
| POST | /resume |
| POST | /job |
| POST | /search |
| POST | /candidate/{id}/summary |
| POST | /jobs/{job_id}/candidate/{candidate_id}/interview-questions |
| POST | /jobs/{id}/improve |
| POST | /sessions/{id}/ask |
| GET | /sessions/{id} |

---

# Search Example

```
Find Python developers with Docker experience
and at least 3 years experience.
```

---

# Author

TalentMatch AI

Epazz Internship Week 2 Capstone Project