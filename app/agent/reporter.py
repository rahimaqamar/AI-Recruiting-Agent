"""
Reporter Node

Creates the final recruiter report.
"""

from app.agent.agent_state import AgentState


def reporter_node(state: AgentState) -> AgentState:
    """
    Generate the final report.
    """

    state["status"] = "completed"

    state["trace"].append(
        "Generating final report..."
    )

    report = {

        "job_id": state["job_id"],

        "goal": state["goal"],

        "total_candidates": len(
            state.get("candidates", [])
        ),

        "top_candidates": state.get(
            "shortlisted_candidates",
            []
        ),

        "candidate_summaries": state.get(
            "summaries",
            []
        ),

        "interview_questions": state.get(
            "interview_questions",
            []
        ),

        "improved_job_description": state.get(
            "improved_job",
            ""
        ),

        # ↓↓↓ YE NAYI LINE ADD KI ↓↓↓
        "job_bottleneck_flag": state.get(
            "job_bottleneck_flag",
            False
        ),
        # ↑↑↑ YE NAYI LINE ADD KI ↑↑↑

        "summary": (
            "Recruiting agent completed successfully. "
            "Candidates were searched, evaluated, "
            "summarized and interview questions were generated."
        ),

        "workflow_status": "completed",

        "trace": state.get(
            "trace",
            []
        )
    }

    state["report"] = report

    state["trace"].append(
        "Report generated successfully."
    )

    return state