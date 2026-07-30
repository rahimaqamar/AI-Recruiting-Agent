# ==========================================
# llm.py
# Large Language Model Functions
# ==========================================

import json
import re

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage

from app.config import (
    GROQ_API_KEY,
    LLM_MODEL
)

# ------------------------------------------
# Initialize LLM
# ------------------------------------------

llm = ChatGroq(
    model=LLM_MODEL,
    api_key=GROQ_API_KEY,
    timeout= 10,
    max_retries=1,
    temperature=0
)


# ==========================================
# Candidate Summary
# ==========================================

def generate_candidate_summary(
    resume_text,
    search_query=""
):
    try:
        prompt = f"""
You are an HR recruiter.

Resume:

{resume_text}

Search Query:

{search_query}

Write a professional summary of this candidate.
Keep it within 100 words.
"""

        response = llm.invoke(
            [HumanMessage(content=prompt)]
        )

        return response.content

    except Exception as e:
        print(f"Candidate summary failed: {e}")
        return "Summary unavailable (rate limit reached)."


# ==========================================
# Explain Match
# ==========================================

def explain_match(
    query,
    resume_text
):
    try:
        prompt = f"""
Recruiter Search:

{query}

Candidate Resume:

{resume_text}

Explain why this candidate matches the search.
Mention matching skills, experience, and education.
Keep the answer under 80 words.
"""

        response = llm.invoke(
            [HumanMessage(content=prompt)]
        )

        return response.content

    except Exception as e:
        print(f"Explain match failed: {e}")
        return "Match explanation unavailable (rate limit reached)."

#  explain why not match
# ==========================================
# Explain NO Match — candidate kyun match nahi hua
# ==========================================

def explain_no_match(
    query,
    resume_text,
    missing_requirements=""
):
    try:
        prompt = f"""
You are an HR recruiter.

Recruiter Search / Job Requirement:

{query}

Candidate Resume:

{resume_text}

Missing Requirements (if known):

{missing_requirements}

Explain clearly why this candidate does NOT match the search well.
Mention specific missing skills, insufficient experience, or education gaps.
Be factual and grounded only in the resume text — do not invent information.
Keep the answer under 80 words.
"""

        response = llm.invoke(
            [HumanMessage(content=prompt)]
        )

        return response.content

    except Exception as e:
        print(f"Explain no-match failed: {e}")
        return "Mismatch explanation unavailable (rate limit reached)."
# ==========================================
# Interview Questions
# ==========================================

def generate_interview_questions(
    resume_text,
    job_description
):
    try:
        prompt = f"""
Job Description:
{job_description}

Candidate Resume:
{resume_text}

Generate exactly 5 interview questions.

Rules:
1. Return exactly 5 questions.
2. Number them from 1 to 5.
3. Focus on the candidate's weaknesses or missing skills relative to the job.
4. Do not include explanations, headings, or extra text.
"""

        response = llm.invoke(
            [HumanMessage(content=prompt)]
        )

        text = response.content.strip()

        questions = [
            line.strip()
            for line in text.split("\n")
            if line.strip()
        ]
        # slicing syntax han kis ma sa only 5 thing nikalna
        return questions[:5]

    except Exception as e:
        print(f"Interview questions failed: {e}")
        return ["Questions unavailable (rate limit reached)."]


# ==========================================
# Improve Job Description
# ==========================================

def improve_job_description(
    job_description,
    statistics
):
    try:
        prompt = f"""
Current Job Description:

{job_description}

Candidate Statistics:

{statistics}

Review the job description.

Suggest improvements.

Mention missing skills.

Recommend better wording.

Keep the response professional.
"""

        response = llm.invoke(
            [HumanMessage(content=prompt)]
        )

        return response.content

    except Exception as e:
        print(f"Job description improvement failed: {e}")
        return "Job quality feedback unavailable (rate limit reached)."


# ==========================================
# Query Rewriting (for filter/search)
# ==========================================
# Recruiter kabhi casual language me search karta hai jaise
#  "mujhe koi accha python developer chahiye jo 3 saal se kaam kar raha ho."
#  Ye function usse keyword-rich search phrase me convert karta hai 
# — jaise "Python developer, 3 years experience" 
# — taaki ChromaDB ka semantic search better match kare.
def rewrite_query_for_search(user_query: str) -> str:

    try:
        prompt = f"""
You are a search query optimizer for a resume-matching system.

Convert the user's input into a concise keyword-rich search phrase
focused on job role, skills, and experience.

Rules:
- Output ONLY the rewritten query.
- No explanations.
- No quotes.

User input:
{user_query}

Rewritten query:
"""

        response = llm.invoke(
            [
                HumanMessage(
                    content=prompt
                )
            ]
        )

        return response.content.strip()

    except Exception as e:
        print(f"Query rewrite failed, using original query: {e}")
        return user_query   # fallback — Groq fail ho toh bhi filter crash nahi hoga
    # suggest category
def suggest_category(resume_text):
    try:
        prompt = f"""
You are a recruitment expert.
Read the following resume and identify the candidate's primary job category.
Return ONLY one category.

Examples:
- Python Developer
- Java Developer
- Frontend Developer
- Backend Developer
- Full Stack Developer
- Data Scientist
- Machine Learning Engineer
- DevOps Engineer
- Business Development
- HR
- Accountant
- Sales
- Marketing
- Graphic Designer
- Teacher
- Doctor
- Civil Engineer
- Mechanical Engineer
- Electrical Engineer

Resume:

{resume_text}
"""
        response = llm.invoke([HumanMessage(content=prompt)])
        return response.content.strip()

    except Exception as e:
        print(f"Category suggestion failed: {e}")
        return "General"


# ==========================================
# Extract Result Count
# ==========================================

def extract_result_count_with_llm(query):

    prompt = f"""
    Extract the number of candidates requested from this query.

    Query:
    {query}

    Rules:
    - Return only the integer number.
    - If no number is mentioned return 5.

    Examples:
    "show me ten developers" -> 10
    "find five python developers" -> 5
    "give 20 resumes" -> 20
    """

    response = llm.invoke(prompt)

    text = response.content.strip()

    # First try direct integer
    if text.isdigit():
        return int(text)
#    regex expression:
    # Extract number from LLM response
    match = re.search(r"\d+", text)

    if match:
        return int(match.group())

    return 5


# ==========================================
# Extract Resume Info (Domain-Agnostic)
# ==========================================
# Purana approach: utils.py mein hardcoded SKILLS/EDUCATION list se
# keyword matching hoti thi — jo sirf tech resumes (Python, React,
# Docker...) ke liye kaam karti thi. Accounting/marketing/medical
# resumes pe fail ho jaati thi (name = "Unknown", skills = blank).
#
# Naya approach: ek hi LLM call se resume ko "samajh" kar name,
# education, experience, skills, location — sab kuch nikalta hai.
# Kisi bhi domain ke resume pe kaam karta hai, koi hardcoded list
# maintain nahi karni padti.

def extract_resume_info_with_llm(resume_text):
    try:
        prompt = f"""
You are an expert resume parser. Read the resume below and extract structured information.

Resume:
{resume_text}

Return ONLY a valid JSON object (no markdown, no code fences, no extra text) in exactly this format:
{{
  "name": "candidate's full name as written in the resume",
  "education": "highest degree/qualification, written naturally (e.g. 'B.Com in Accounting', 'ACCA', 'BS Computer Science')",
  "experience_years": 0.0,
  "skills": ["skill1", "skill2", "skill3"],
  "location": "city mentioned in the resume, or Unknown if not found"
}}

Rules:
- "experience_years" must be a number (float) — your best estimate of total years of professional experience based on the resume content.
- "skills" should list 5-15 relevant skills/tools mentioned in the resume, in the candidate's own domain (accounting, software, marketing, medical, etc.) — do not limit to any specific industry.
- If a field cannot be found, use "Unknown" for text fields, 0.0 for experience_years, and [] for skills.
- Do not invent information not present in the resume.
"""

        response = llm.invoke([HumanMessage(content=prompt)])
        text = response.content.strip()

        # Kabhi kabhi model ```json ... ``` fences add kar deta hai — hata do
        if text.startswith("```"):
            text = text.strip("`")
            text = text.replace("json\n", "", 1).replace("json", "", 1).strip()

        data = json.loads(text)

        return {
            "name": data.get("name") or "Unknown",
            "education": data.get("education") or "Unknown",
            "experience": float(data.get("experience_years") or 0.0),
            "skills": data.get("skills") or [],
            "location": data.get("location") or "Unknown",
        }

    except Exception as e:
        print(f"LLM resume info extraction failed: {e}")
        return {
            "name": "Unknown",
            "education": "Unknown",
            "experience": 0.0,
            "skills": [],
            "location": "Unknown",
        }