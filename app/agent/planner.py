"""
Planner Node

First node of the recruiting workflow.
Initializes the workflow, parses the goal (Adaptive Planning),
and updates live status.
"""

import re
from app.agent.agent_state import AgentState


def parse_goal(goal: str) -> dict:
    """
    Goal text se recruiter ki instructions nikalta hai.
    Ye hi Adaptive Planning ka core hai — hardcoded values
    ki jagah goal text khud decide karta hai agent ka behavior.
    """

    plan = {
        "min_candidates_to_review": 10,
        "priority_skills": [],
        "auto_broaden": False
    }

    goal_lower = goal.lower()

    # "review at least N candidates" ya "minimum N candidates"
    match = re.search(r"(?:at least|minimum)\s+(\d+)\s+candidates?", goal_lower)
    if match:
        plan["min_candidates_to_review"] = int(match.group(1))

    # "prioritize X and Y"
    priority_match = re.search(r"prioritize\s+([a-zA-Z0-9,\s]+?)(?:\.|$)", goal_lower)
    if priority_match:
        skills_text = priority_match.group(1)
        plan["priority_skills"] = [
            s.strip() for s in re.split(r",|and", skills_text) if s.strip()
        ]

    # "broaden the search" jaisa koi instruction
    if "broaden" in goal_lower or "expand" in goal_lower or "fewer than" in goal_lower:
        plan["auto_broaden"] = True

    return plan


def planner_node(state: AgentState) -> AgentState:
    """
    Initialize recruiting workflow + create adaptive plan.
    """

    state["status"] = "planning"

    state["trace"].append("Planner started.")
    state["trace"].append(f"Goal: {state['goal']}")
    state["trace"].append(f"Job ID: {state['job_id']}")

    # ==========================================
    # Adaptive Planning
    # ==========================================
    plan = parse_goal(state["goal"])
    state["plan"] = plan

    state["trace"].append(
        f"Adaptive plan: min_candidates={plan['min_candidates_to_review']}, "
        f"priority_skills={plan['priority_skills']}, "
        f"auto_broaden={plan['auto_broaden']}"
    )

    return state