"""
Interview Node

Generates interview questions for shortlisted candidates.
"""

from app.agent.agent_state import AgentState
from app.agent.tools import interview_questions_tool


def interview_node(state: AgentState) -> AgentState:
    """
    Generate interview questions.
    """

    state["status"] = "interview"

    state["trace"].append(
        "Generating interview questions..."
    )

    questions = []

    shortlisted = state.get("shortlisted_candidates", [])

    # ↓↓↓ Adaptive Planning: hardcoded limit ki jagah goal-based plan se lo ↓↓↓
    max_candidates = state.get("plan", {}).get("min_candidates_to_review", 10)

    if len(shortlisted) > max_candidates:
        state["trace"].append(
            f"Capped interview generation at {max_candidates} candidates (from adaptive plan, based on goal)."
        )
        shortlisted = shortlisted[:max_candidates]
    # ↑↑↑ Adaptive Planning ↑↑↑

    for candidate in shortlisted:

        if isinstance(candidate, dict):
            candidate_id = candidate.get("candidate_id")
        else:
            candidate_id = getattr(candidate, "candidate_id", None)

        # ↓↓↓ Graceful Tool Failure Handling ↓↓↓
        try:
            result = interview_questions_tool(
                state["job_id"],
                candidate_id
            )
            actual_questions = result.get("questions", []) if result else []
        except Exception as e:
            print(f"[interview_node] FAILED for candidate_id={candidate_id}: {e}", flush=True)
            actual_questions = []
            state["trace"].append(
                f"Warning: interview questions failed for candidate {candidate_id}, continuing with others."
            )
        # ↑↑↑ Graceful Tool Failure Handling ↑↑↑

        questions.append(
            {
                "candidate_id": candidate_id,
                "questions": actual_questions
            }
        )

    state["interview_questions"] = questions

    state["trace"].append(
        f"Generated interview questions for {len(questions)} candidate(s)."
    )

    return state