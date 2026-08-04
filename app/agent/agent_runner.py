# Database se job load karna.
# Initial state banana.
# LangGraph workflow start karna.
# Har node ka updated state collect karna.
# Final report return karna.

"""
Agent Runner

Creates the initial state,
runs the LangGraph workflow,
and returns the final report.
"""
# graph sa import
from app.agent.agent_graph import agent_graph
# database 
from app.database import SessionLocal, Job

# first agent start
def run_agent(
    job_id: int,
    goal: str,
    run_id: str,
    RUNS: dict
):

    # ==========================================
    # Job description ko DB se fetch karo — source of truth
    # ==========================================
    db = SessionLocal()
    job = db.query(Job).filter(Job.id == job_id).first()
    db.close()

    if not job:
        RUNS[run_id] = {
            "status": "failed",
            "report": {},
            "trace": [f"Job ID {job_id} not found in database."]
        }
        return RUNS[run_id]

    job_description = job.description or ""
    # ya state bad ma har node use kara gya

    initial_state = {

        "run_id": run_id,

        "job_id": job_id,
        "goal": goal,
        "job_description": job_description,

        "candidates": [],
        "shortlisted_candidates": [],

        "summaries": [],
        "interview_questions": [],

        "improved_job": "",

        "report": {},

        "status": "planning",

        "trace": [
            f"Job loaded: '{job.title}' (ID: {job_id})"
        ],
    }


    RUNS[run_id] = {

        "status": "planning",
        "report": {},
        "trace": []
    }

# intial state graph ko dia gata han 
# ab graph apna nodes ko execute kara gya
# stream: har node execute ka bad update state wapis do
    for event in agent_graph.stream(initial_state):

        for node_name, state in event.items():

            RUNS[run_id] = {

                "status": state.get("status", "running"),

                "report": state.get("report", {}),

                "trace": state.get("trace", [])
            }


    return RUNS[run_id]