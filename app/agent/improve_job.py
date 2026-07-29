"""
Improve Job Node

Improves the job description using the existing Week 2 service.
"""

from app.agent.agent_state import AgentState
from app.agent.tools import improve_job_tool


def improve_job_node(state: AgentState) -> AgentState:
    state["status"] = "improving_job"
    state["trace"].append("Improving job description...")

    try:
        improved_job = improve_job_tool(state["job_id"])
        state["improved_job"] = improved_job

        # Bottleneck flag: agar shortlist chhoti hai, job posting ko possible cause maano
        total_candidates = len(state.get("candidates", []))
        shortlisted_count = len(state.get("shortlisted_candidates", []))

        if total_candidates > 0 and shortlisted_count / total_candidates < 0.2:
            state["job_bottleneck_flag"] = True
            state["trace"].append(
                "Flagged: Job posting may be too narrow/restrictive — low shortlist rate suggests requirements might be filtering out good candidates."
            )
        else:
            state["job_bottleneck_flag"] = False

        state["trace"].append("Job description improved successfully.")

    except Exception as e:
        state["improved_job"] = ""
        state["trace"].append(f"Failed to improve job description: {str(e)}")

    return state