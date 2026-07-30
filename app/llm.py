# ==========================================
# llm.py
# Large Language Model Functions
# ==========================================

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
    # extract the numbers 
import re

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

    return 