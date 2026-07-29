"""
Evaluator Node

Evaluates candidates returned by search node,
ranks them, performs self-checking,
and decides whether search should be broadened.
"""

from app.agent.tools import search_candidates_tool
from app.agent.agent_state import AgentState


def evaluator_node(state: AgentState) -> AgentState:

    state["status"] = "evaluating"
    state["trace"].append("Evaluating candidates...")

    candidates = state.get("candidates", [])

    # Adaptive planning data
    plan = state.get("plan", {})

    priority_skills = [
        s.lower()
        for s in plan.get("priority_skills", [])
    ]

    # Goal based broadening instruction
    goal_auto_broaden = plan.get(
        "auto_broaden",
        False
    )


    shortlisted = []


    # ==========================================
    # Candidate Evaluation
    # ==========================================

    for candidate in candidates:

        if isinstance(candidate, dict):
            score = candidate.get(
                "similarity_score",
                0
            )
        else:
            score = getattr(
                candidate,
                "similarity_score",
                0
            )


        # ======================================
        # Priority Skills Boost
        # ======================================

        if priority_skills:

            if isinstance(candidate, dict):
                candidate_skills = candidate.get(
                    "skills",
                    []
                )
                candidate_id = candidate.get(
                    "candidate_id"
                )

            else:
                candidate_skills = getattr(
                    candidate,
                    "skills",
                    []
                )
                candidate_id = getattr(
                    candidate,
                    "candidate_id",
                    None
                )


            candidate_skills_lower = [
                s.lower()
                for s in candidate_skills
            ] if candidate_skills else []


            matched_priority = [
                skill
                for skill in priority_skills
                if any(
                    skill in cs
                    for cs in candidate_skills_lower
                )
            ]


            if matched_priority:

                score += (
                    0.05 *
                    len(matched_priority)
                )

                state["trace"].append(
                    f"Candidate {candidate_id} "
                    f"boosted for skills: "
                    f"{matched_priority}"
                )


        # ======================================
        # Strong Candidate Threshold
        # ======================================

        if score >= 0.65:

            shortlisted.append(candidate)


    # ==========================================
    # Autonomous Broadening Decision
    # ==========================================

    strong_matches = len(shortlisted)


    if strong_matches < 3:

        state["auto_broaden"] = True

        state["trace"].append(
            f"Only {strong_matches} strong "
            "candidate(s) found. "
            "Agent decided to broaden search."
        )


    else:

        state["auto_broaden"] = goal_auto_broaden

        state["trace"].append(
            f"{strong_matches} strong candidates "
            "found. No automatic broadening required."
        )


    should_broaden = state["auto_broaden"]


    # ==========================================
    # Broad Search
    # ==========================================

    if should_broaden:

        state["trace"].append(
            "Broadening search started. "
            "Lowering similarity threshold."
        )


        # Include weaker matches
        shortlisted = [

            c

            for c in candidates

            if (
                c.get(
                    "similarity_score",
                    0
                )
                if isinstance(c, dict)

                else getattr(
                    c,
                    "similarity_score",
                    0
                )

            ) >= 0.50

        ]


        # ======================================
        # Wider Re-search
        # ======================================

        if len(shortlisted) < 3:

            state["trace"].append(
                "Still insufficient matches. "
                "Running wider search."
            )


            try:

                broader_results = search_candidates_tool(

                    job_description=
                    state["job_description"]
                    .split(".")[0],

                    goal="broad search"

                )


                existing_ids = {
                    c.get(
                        "candidate_id"
                    )

                    for c in shortlisted
                }


                for candidate in broader_results:

                    candidate_id = candidate.get(
                        "candidate_id"
                    )


                    if (
                        candidate_id
                        not in existing_ids
                        and
                        candidate.get(
                            "similarity_score",
                            0
                        ) >= 0.40
                    ):

                        shortlisted.append(
                            candidate
                        )


                state["trace"].append(
                    f"Broad search added candidates. "
                    f"Total candidates: {len(shortlisted)}"
                )


            except Exception as e:

                state["trace"].append(
                    f"Broad search failed: {str(e)}"
                )


    else:

        state["trace"].append(
            "Broadening skipped. "
            "Candidate quality is sufficient."
        )


    # ==========================================
    # Final Shortlist
    # ==========================================

    state["shortlisted_candidates"] = shortlisted


    state["trace"].append(
        f"Final shortlisted candidates: "
        f"{len(shortlisted)}"
    )


    state["trace"].append(
        f"Auto broaden decision: "
        f"{state.get('auto_broaden')}"
    )


    return state