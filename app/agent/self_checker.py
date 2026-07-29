"""
Self Checker Node

Validates the workflow before generating
the final report.
"""

from app.agent.agent_state import AgentState


def self_checker_node(state: AgentState) -> AgentState:
    state["status"] = "self_check"
    state["trace"].append("Performing self-check...")

    shortlisted = state.get("shortlisted_candidates", [])
    verified = []
    dropped = []

    for candidate in shortlisted:
        score = candidate.get("similarity_score", 0) if isinstance(candidate, dict) else getattr(candidate, "similarity_score", 0)
        # Re-check: agar score bahut weak hai (0.40 se kam) to drop karo self-check mein
        if score < 0.40:
            dropped.append(candidate)
        else:
            verified.append(candidate)

    if dropped:
        state["trace"].append(f"Self-check dropped {len(dropped)} weak candidate(s) below re-verification threshold.")
        state["shortlisted_candidates"] = verified

    if not verified:
        state["trace"].append("Self-check: no strong candidates remain after re-verification.")
        state["report_status"] = "warning"
    else:
        state["trace"].append("Self-check passed — shortlist verified.")
        state["report_status"] = "success"

    return state