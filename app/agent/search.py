"""
Search Node

Searches suitable candidates for the given job.
"""

from app.agent.agent_state import AgentState
from app.agent.tools import search_candidates_tool
from app.database import SessionLocal, Job


def search_node(state: AgentState) -> AgentState:
    """
    Search candidates using semantic (query) + filtered (structured) search.
    """

    state["status"] = "searching"

    state["trace"].append(
        "Searching candidates..."
    )

    # ↓↓↓ Job record se filters nikaalo — Filtered Search ke liye ↓↓↓
    filters = {}

    try:
        db = SessionLocal()
        job = db.query(Job).filter(Job.id == state["job_id"]).first()
        db.close()

        if job:
            if job.required_skills:
                filters["required_skills"] = [
                    s.strip() for s in job.required_skills.split(",") if s.strip()
                ]
            if job.experience:
                filters["min_experience_years"] = job.experience
            if job.location:
                filters["location"] = job.location
#    trace logging 
        if filters:
            state["trace"].append(f"Applying filters from job posting: {filters}")

    except Exception as e:
        print(f"[search_node] Failed to load job filters: {e}", flush=True)
        state["trace"].append(f"Warning: could not load job filters, proceeding with semantic search only.")
        filters = {}
    # ↑↑↑ Filtered Search setup ↑↑↑

    # ↓↓↓ Plan (goal text se nikale hue) required skills ko bhi merge karo ↓↓↓
    plan = state.get("plan", {})
    plan_required_skills = plan.get("required_skills", [])

    if plan_required_skills:
        existing = filters.get("required_skills", [])
        combined = list(set(
            [s.lower() for s in existing] +
            [s.lower() for s in plan_required_skills]
        ))
        filters["required_skills"] = combined
        state["trace"].append(f"Merged goal skills into filters: {combined}")

    plan_min_experience = plan.get("min_experience_years")
    if plan_min_experience and not filters.get("min_experience_years"):
        filters["min_experience_years"] = plan_min_experience
        state["trace"].append(f"Applied goal-based min_experience_years: {plan_min_experience}")
    # ↑↑↑

    # ↓↓↓ Graceful Tool Failure Handling ↓↓↓
    try:
        candidates = search_candidates_tool(
            state["job_description"],
            state["goal"],
            filters
        )
    except Exception as e:
        print(f"[search_node] Search FAILED: {e}", flush=True)
        state["trace"].append(f"Search failed: {str(e)}. Continuing with empty candidate list.")
        candidates = []
    # ↑↑↑

    state["candidates"] = candidates

    state["trace"].append(
        f"Found {len(candidates)} candidate(s) using semantic + filtered search."
    )

    return state