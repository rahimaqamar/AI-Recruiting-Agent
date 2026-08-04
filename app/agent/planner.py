# Its job is to understand the recruiter's goal, create an adaptive plan, 
# store it in AgentState, 
# and pass the updated state to the next node (search.py).
# extract skills experience and education and experience all nodes use this plan
"""
Planner Node
First node of the recruiting workflow.
Initializes the workflow, parses the goal (Adaptive Planning),
and updates live status.
"""

import re
# import the shared state
from app.agent.agent_state import AgentState

# Ye function recruiter ke goal ko read karta hai aur us se instructions nikalta hai.
def parse_goal(goal: str) -> dict:
    """
    Goal text se recruiter ki instructions nikalta hai.
    Ye hi Adaptive Planning ka core hai — hardcoded values
    ki jagah goal text khud decide karta hai agent ka behavior.
    """
# create a default plan if recuriter not give goal then plan execute
    plan = {
        "min_candidates_to_review": 10,
        "priority_skills": [],
        "auto_broaden": False,
        "required_skills": [],
        "min_experience_years": None
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

    # "skill in X" / "skills that is X" / "with skills X" / "skilled in X"
    skill_match = re.search(
        r"skills?\s*(?:that is|that are|in|is|are|:)?\s*([a-zA-Z0-9\.\+\#\s,/]+?)(?:\.|$)",
        goal_lower
    )
    if skill_match:
        skills_text = skill_match.group(1)
        plan["required_skills"] = [
            s.strip() for s in re.split(r",|and", skills_text) if s.strip()
        ]

    # "N years of experience" / "N years experience"
    exp_match = re.search(
        r"(\d+)\s*\+?\s*years?\s*(?:of\s*)?experience",
        goal_lower
    )
    if exp_match:
        plan["min_experience_years"] = int(exp_match.group(1))

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
    # yaha planner goal ko read karta han
    plan = parse_goal(state["goal"])
    # plan bana han state ma save karta han
    state["plan"] = plan
#  what plan the planner node created
    state["trace"].append(
        f"Adaptive plan: min_candidates={plan['min_candidates_to_review']}, "
        f"priority_skills={plan['priority_skills']}, "
        f"required_skills={plan['required_skills']}, "
        f"min_experience_years={plan['min_experience_years']}, "
        f"auto_broaden={plan['auto_broaden']}"
    )

    return state