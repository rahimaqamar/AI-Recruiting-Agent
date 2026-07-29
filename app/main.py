# ==========================================
# app.py
# FastAPI Application
# ==========================================

import os
import threading
import uuid
import traceback
from typing import List
from fastapi import FastAPI, UploadFile, File, HTTPException
from app.config import UPLOAD_FOLDER
from app.utils import extract_text_from_pdf
from app.agent.agent_runner import run_agent

from app.schemas import (
    ResumeResponse,
    UploadJobResponse,
    JobRequest,
    JobResponse,
    SearchRequest,
    SearchResponse,
    SummaryResponse,
    InterviewResponse,
    JobReviewResponse,
    SessionRequest,
    SessionResponse,
    ProcessJobResponse,
    MatchResponse,
    CandidateDetailResponse,
    JobQualityResponse,
    FilterRequest,
    FilterResponse,
    FillRoleRequest,
    FillRoleResponse,

)

from app.services import (
    upload_resume,
    upload_job,
    create_job,
    search_candidates,
    candidate_summary,
    interview_questions,
    improve_job,
    create_session,
    get_sessions,
    save_chat,
    get_chat_history,
    process_job,
    run_match,
    get_candidate_detail,
    get_job_quality,
    apply_filter,
    get_all_jobs
)

# ==========================================
# Create FastAPI App
# ==========================================

app = FastAPI(
    title="TalentMatch AI",
    version="2.0"
)

# ==========================================
# Home
# ==========================================

@app.get("/")
def home():
    return {
        "message": "TalentMatch AI API is Running"
    }


# ==========================================
# Upload Resume
# ==========================================

@app.post(
    "/resume",
    response_model=ResumeResponse
)
def upload_resume_api(
    file: UploadFile = File(...)
):
    return upload_resume(file)


# ==========================================
# Upload Job Description
# ==========================================

@app.post(
    "/upload-job",
    response_model=UploadJobResponse
)
def upload_job_api(
    file: UploadFile = File(...)
):
    return upload_job(file)


# ==========================================
# Manual Create Job
# ==========================================

@app.post(
    "/jobs",
    response_model=JobResponse
)
def create_job_api(
    job: JobRequest
):
    return create_job(job)


# ==========================================
# Search Candidates
# ==========================================

@app.post(
    "/search",
    response_model=SearchResponse
)
def search_api(
    request: SearchRequest
):
    return search_candidates(request)


# ==========================================
# Candidate Summary
# ==========================================

@app.get(
    "/candidate/{candidate_id}/summary",
    response_model=SummaryResponse
)
def summary_api(
    candidate_id: int
):
    result = candidate_summary(candidate_id)

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Candidate not found."
        )

    return result


# ==========================================
# Interview Questions
# ==========================================

@app.get(
    "/jobs/{job_id}/candidates/{candidate_id}/interview-questions",
    response_model=InterviewResponse
)
def interview_api(
    job_id: int,
    candidate_id: int
):
    result = interview_questions(
        job_id,
        candidate_id
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Candidate or Job not found."
        )

    return result


# ==========================================
# Improve Job Description
# ==========================================

@app.get(
    "/jobs/{job_id}/improve",
    response_model=JobReviewResponse
)
def improve_job_api(
    job_id: int
):
    result = improve_job(job_id)

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Job not found."
        )

    return result


# ==========================================
# Create Chat Session
# ==========================================

@app.post("/sessions")
def create_chat_session():
    session_id = create_session()
    return {
        "session_id": session_id
    }


# ==========================================
# Get All Sessions
# ==========================================

@app.get("/sessions")
def list_sessions():
    return get_sessions()


# ==========================================
# Recruiter Chat
# ==========================================

@app.post(
    "/sessions/{session_id}/ask",
    response_model=SessionResponse
)
@app.post("/sessions/{session_id}/ask")
def recruiter_chat(
    session_id: int,
    request: SessionRequest
):
    save_chat(
        session_id,
        "Recruiter",          # changed
        request.message
    )

    response = "Conversation saved successfully."

    save_chat(
        session_id,
     "TalentMatch AI",     # changed
        response
    )

    return {
        "session_id": session_id,
        "response": response
    }

# ==========================================
# Chat History
# ==========================================

@app.get("/sessions/{session_id}")
def history(
    session_id: int
):
    return get_chat_history(session_id)


# ==========================================
# Process Job
# ==========================================

@app.post(
    "/process-job",
    response_model=ProcessJobResponse
)
def process_job_api(job: JobRequest):
    return process_job(job)


# ==========================================
# Run Match
# ==========================================

from fastapi import Form

@app.post("/match", response_model=MatchResponse)
def run_match_api(
    job_file: UploadFile = File(...),
    resume_files: List[UploadFile] = File(...),
    session_id: int = Form(...)
):

    try:

        return run_match(
            job_file,
            resume_files
        )

    except Exception as e:

        import traceback

        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
    
# ==========================================
# Candidate Detail
# ==========================================

@app.get(
    "/candidate/{candidate_id}",
    response_model=CandidateDetailResponse
)
def candidate_detail_api(
    candidate_id: int,
    job_description: str = ""
):
    result = get_candidate_detail(
        candidate_id,
        job_description
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Candidate not found."
        )

    return result


# ==========================================
# Job Quality
# ==========================================

@app.post(
    "/job-quality",
    response_model=JobQualityResponse
)
def job_quality_api(
    job_file: UploadFile = File(...)
):
    # Standardize directory configuration using UPLOAD_FOLDER
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    file_path = os.path.join(UPLOAD_FOLDER, job_file.filename)

    with open(file_path, "wb") as f:
        f.write(job_file.file.read())

    job_description = extract_text_from_pdf(file_path)

    return get_job_quality(job_description)


# ==========================================
# Filter Candidates
# ==========================================

@app.post("/filter", response_model=FilterResponse)
def filter_api(request: FilterRequest):
    try:
        return apply_filter(request.query)

    except Exception as e:
        traceback.print_exc()  # Prints full traceback in terminal
        raise HTTPException(            status_code=500,
            detail=str(e)
        )
# ==========================================
# Week 3 - Autonomous Recruiting Agent
# ==========================================

# Temporary in-memory storage
# Later replace with database
RUNS = {}


# ==========================================
# Start Agent
# ==========================================
from app.database import SessionLocal, Job
def run_agent_background(
    run_id,
    job_id,
    goal,
    job_description
):
    print(f"[run_agent_background] Thread started for run_id={run_id}", flush=True)

    try:
        result = run_agent(
            job_id=job_id,
            goal=goal,
            run_id=run_id,
            RUNS=RUNS
        )

        RUNS[run_id] = result

        print(f"[run_agent_background] Thread finished for run_id={run_id}", flush=True)

    except Exception as e:
        import traceback
        print(f"[run_agent_background] CRASHED for run_id={run_id}: {e}", flush=True)
        traceback.print_exc()

        RUNS[run_id]["status"] = "error"
        RUNS[run_id]["error"] = str(e)
    # agen fill role
from app.agent.job_selector import select_job_from_goal
@app.post("/agent/fill-role", response_model=FillRoleResponse)
def fill_role(request: FillRoleRequest):

    db = SessionLocal()

    if request.job_id is not None:
        # Manual job_id diya gaya hai, DB se seedha fetch karo
        job = db.query(Job).filter(Job.id == request.job_id).first()

    else:
        # job_id nahi diya — goal se auto-detect karo
        selected_job_id, selected_title, confidence = select_job_from_goal(request.goal)

        if selected_job_id is None:
            db.close()
            raise HTTPException(
                status_code=404,
                detail="Goal se koi matching job database mein nahi mila."
            )

        job = db.query(Job).filter(Job.id == selected_job_id).first()
        print(f"[fill_role] Auto-selected job: '{selected_title}' (confidence: {confidence:.2f})")

    if job is None:
        db.close()
        raise HTTPException(status_code=404, detail="Job not found")

    run_id = f"run_{uuid.uuid4().hex[:8]}"

    RUNS[run_id] = {"status": "planning", "trace": [], "report": {}}

    threading.Thread(
        target=run_agent_background,
        args=(run_id, job.id, request.goal, job.description),
        daemon=True
    ).start()

    db.close()

    return FillRoleResponse(
        run_id=run_id,
        job_id=job.id,
        status="planning"
    )
# ==========================================
# Get Agent Run
# ==========================================

@app.get("/agent/runs/{run_id}")
def get_run(run_id: str):

    if run_id not in RUNS:
        raise HTTPException(
            status_code=404,
            detail="Run not found"
        )

    return RUNS[run_id]


# ==========================================
# List All Agent Runs
# ==========================================

@app.get("/agent/runs")
def list_runs():

    return {
        "total_runs": len(RUNS),
        "runs": list(RUNS.keys())
    }

@app.get("/jobs")
def list_jobs():
    return get_all_jobs()