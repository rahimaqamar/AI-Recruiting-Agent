# The Summary node receives the shortlisted candidates from the Evaluator node 
# and generates concise summaries highlighting each candidate's qualifications, 
# skills, experience, and suitability for the job. 
# These summaries are stored in AgentState and passed to the Interview node.

"""
Summary Node

Generates candidate summaries.
"""
# state that updated
from app.agent.agent_state import AgentState
#  tool use for generate summary
from app.agent.tools import candidate_summary_tool


def summary_node(state: AgentState) -> AgentState:
    """
    Generate summaries for shortlisted candidates.
    """

    state["status"] = "summaries"
    # add a log message to the execution history
    # useful for debugging and tracing

    state["trace"].append(
        "Generating candidate summaries..."
    )

    summaries = []

    shortlisted = state.get("shortlisted_candidates", [])

    # ↓↓↓ Adaptive Planning: hardcoded limit ki jagah goal-based plan se lo ↓↓↓
    # read the adaptive plan
    max_candidates = state.get("plan", {}).get("min_candidates_to_review", 10)

    if len(shortlisted) > max_candidates:
        state["trace"].append(
            f"Capped processing at {max_candidates} candidates (from adaptive plan, based on goal)."
        )
        shortlisted = shortlisted[:max_candidates]
    # ↑↑↑ Adaptive Planning ↑↑↑

    print(f"[summary_node] Starting summaries for {len(shortlisted)} candidate(s)...", flush=True)
    # Python's built-in enumerate() function to loop 
    # through a list while also keeping track of the position (index) of each item.
    # number ka sath name 
    for index, candidate in enumerate(shortlisted, start=1):

        if isinstance(candidate, dict):
            candidate_id = candidate.get("candidate_id")
        else:
            candidate_id = getattr(candidate, "candidate_id", None)

        print(f"[summary_node] ({index}/{len(shortlisted)}) Generating summary for candidate_id={candidate_id}...", flush=True)

        # ↓↓↓ Graceful Tool Failure Handling ↓↓↓
        try:
            summary = candidate_summary_tool(candidate_id)
        except Exception as e:
            print(f"[summary_node] FAILED for candidate_id={candidate_id}: {e}", flush=True)
            summary = f"Summary generation failed: {str(e)}"
            state["trace"].append(
                f"Warning: summary failed for candidate {candidate_id}, continuing with others."
            )
        # ↑↑↑ Graceful Tool Failure Handling ↑↑↑

        print(f"[summary_node] ({index}/{len(shortlisted)}) Done with candidate_id={candidate_id}", flush=True)

        summaries.append(
            {
                "candidate_id": candidate_id,
                "summary": summary
            }
        )

    state["summaries"] = summaries

    state["trace"].append(
        f"Generated {len(summaries)} candidate summaries."
    )

    print(f"[summary_node] Completed. Generated {len(summaries)} summaries.", flush=True)

    return state