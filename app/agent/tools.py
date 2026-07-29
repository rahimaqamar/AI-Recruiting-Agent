"""
Week 3 Agent Tools

Wrapper functions around the existing Week 2 services.
The LangGraph agent uses these functions instead of calling
services.py directly.
"""

from app.services import (
    search_candidates,
    candidate_summary,
    interview_questions,
    improve_job,
    get_candidate_detail,
)

from app.schemas import SearchRequest, SearchFilters


# ==========================================
# Search Candidates
# ==========================================

def search_candidates_tool(
    job_description: str,
    goal: str,
    filters: dict = None
):
    """
    Search candidates using job description + recruiter goal.
    Ab semantic (query) + filtered (structured filters) dono support karta hai.
    """

    query = f"""
    Job Description:
    {job_description}

    Recruiter Goal:
    {goal}
    """

    # ↓↓↓ Filtered search — job ke required_skills, experience, location ↓↓↓
    search_filters = None
    if filters:
        try:
            search_filters = SearchFilters(**filters)
        except Exception as e:
            print(f"[search_candidates_tool] Invalid filters, skipping: {e}", flush=True)
            search_filters = None
    # ↑↑↑

    request = SearchRequest(
        query=query,
        filters=search_filters
    )

    result = search_candidates(request)

    if isinstance(result, dict):
        return result.get("results", [])

    return getattr(result, "results", result)


# ==========================================
# Candidate Summary
# ==========================================

def candidate_summary_tool(candidate_id: int):
    """Generate a candidate summary."""

    return candidate_summary(candidate_id)


# ==========================================
# Interview Questions
# ==========================================

def interview_questions_tool(job_id: int, candidate_id: int):
    """Generate interview questions."""

    return interview_questions(job_id, candidate_id)


# ==========================================
# Improve Job Description
# ==========================================

def improve_job_tool(job_id: int):
    """Improve the job description."""

    return improve_job(job_id)


# ==========================================
# Candidate Details
# ==========================================

def candidate_detail_tool(candidate_id: int, job_description: str):
    """Return detailed candidate analysis."""

    return get_candidate_detail(candidate_id, job_description)