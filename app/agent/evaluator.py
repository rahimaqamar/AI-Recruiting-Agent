# The Evaluator node checks whether the Search node has returned accurate and relevant candidates. 
# It filters candidates based on the required skills, evaluates and ranks them 
# using similarity scores, and creates a shortlist. If there are not enough strong candidates, 
# it automatically broadens the search to find additional 
# suitable candidates.
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
# search wala candidates lo
    candidates = state.get("candidates", [])

    # Adaptive planning data
    # planner ka plan lo
    plan = state.get("plan", {})

    priority_skills = [
        s.lower()
        for s in plan.get("priority_skills", [])
    ]

    # Goal se nikale hue required skills (hard filter ke liye)
    required_skills = [
        s.lower()
        for s in plan.get("required_skills", [])
    ]

    # Goal based broadening instruction
    goal_auto_broaden = plan.get(
        "auto_broaden",
        False
    )

    # ==========================================
    # Required Skills Hard Filter (NEW)
    # ==========================================
    if required_skills:

        filtered_candidates = []

        for candidate in candidates:

            if isinstance(candidate, dict):
                candidate_skills = candidate.get("skills", [])
                candidate_id = candidate.get("candidate_id")
            else:
                candidate_skills = getattr(candidate, "skills", [])
                candidate_id = getattr(candidate, "candidate_id", None)

            # Agar skills string hai (comma-separated), list mein convert karo
            if isinstance(candidate_skills, str):
                candidate_skills_lower = [
                    s.strip().lower() for s in candidate_skills.split(",")
                ]
            elif candidate_skills:
                candidate_skills_lower = [s.lower() for s in candidate_skills]
            else:
                candidate_skills_lower = []

            has_all_required = all(
                any(req in cs for cs in candidate_skills_lower)
                for req in required_skills
            )

            if has_all_required:
                filtered_candidates.append(candidate)
            else:
                state["trace"].append(
                    f"Candidate {candidate_id} dropped — "
                    f"missing required skill(s): {required_skills}"
                )

        state["trace"].append(
            f"Hard filter on required_skills={required_skills}: "
            f"{len(candidates)} -> {len(filtered_candidates)} candidates"
        )

        candidates = filtered_candidates

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

            if isinstance(candidate_skills, str):
                candidate_skills_lower = [
                    s.strip().lower() for s in candidate_skills.split(",")
                ]
            elif candidate_skills:
                candidate_skills_lower = [s.lower() for s in candidate_skills]
            else:
                candidate_skills_lower = []

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

        # Include weaker matches (but still respect required_skills)
        weak_matches = [

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

        shortlisted = weak_matches

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

                    candidate_skills = candidate.get("skills", [])

                    if isinstance(candidate_skills, str):
                        candidate_skills_lower = [
                            s.strip().lower() for s in candidate_skills.split(",")
                        ]
                    elif candidate_skills:
                        candidate_skills_lower = [s.lower() for s in candidate_skills]
                    else:
                        candidate_skills_lower = []

                    # Required skills ka check yahan bhi lagao broad search mein
                    if required_skills:
                        has_all_required = all(
                            any(req in cs for cs in candidate_skills_lower)
                            for req in required_skills
                        )
                        if not has_all_required:
                            continue

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