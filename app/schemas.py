from typing import List, Optional
from pydantic import BaseModel
from typing import Any

# ==========================================
# Resume
# ==========================================

class ResumeResponse(BaseModel):
    id: int
    message: str


# ==========================================
# Upload Job Response
# ==========================================

class UploadJobResponse(BaseModel):
    id: int
    message: str


# ==========================================
# Manual Job Creation
# ==========================================

class JobRequest(BaseModel):
    title: str
    description: str
    required_skills: List[str]
    experience: float
    education: str
    location: str
    category: Optional[str] = "General"


class JobResponse(BaseModel):
    id: int
    message: str


# ==========================================
# Search Filters
# ==========================================

class SearchFilters(BaseModel):
    min_experience_years: Optional[float] = None
    required_skills: Optional[List[str]] = None
    education_level: Optional[str] = None
    location: Optional[str] = None
    category: Optional[str] = None


# ==========================================
# Search Request
# ==========================================

class SearchRequest(BaseModel):
    query: Optional[str] = None
    filters: Optional[SearchFilters] = None


# ==========================================
# Candidate Result
# ==========================================

class CandidateResult(BaseModel):
    candidate_id: int
    name: str
    similarity_score: float
    meets_filters: bool
    why_matched: str
    skills: List[str] = []
    experience: Optional[float] = None
    education: Optional[str] = None
    location: Optional[str] = None


# ==========================================
# Search Response
# ==========================================

class SearchResponse(BaseModel):
    query: Optional[str]
    filters_applied: Optional[dict]
    results: List[CandidateResult]


# ==========================================
# Candidate Summary
# ==========================================

class SummaryResponse(BaseModel):
    candidate_id: int
    summary: str


# ==========================================
# Interview Questions
# ==========================================

class InterviewResponse(BaseModel):
    candidate_id: int
    job_id: int
    questions: List[str]


# ==========================================
# Job Review
# ==========================================

class JobReviewResponse(BaseModel):
    job_id: int
    review: str


# ==========================================
# Chat Session
# ==========================================

class SessionRequest(BaseModel):
    message: str


class SessionResponse(BaseModel):
    session_id: int
    response: str


# ==========================================
# Job Information Extracted From PDF/DOCX
# ==========================================

class JobInfo(BaseModel):
    title: str
    description: str
    required_skills: List[str]
    experience: float
    education: str
    location: str
    category: str


# ==========================================
# Recruiter Dashboard Statistics
# ==========================================

class DashboardResponse(BaseModel):
    total_resumes: int
    total_jobs: int
    total_sessions: int
    total_searches: int


# =====================================================
# NEW MODELS FOR AUTOMATIC JOB PROCESSING
# =====================================================

class ProcessCandidate(BaseModel):
    candidate_id: int
    name: str
    similarity_score: float
    why_matched: str
    summary: str
    interview_questions: List[str]


class MatchCandidate(BaseModel):
    id: int
    name: str
    score: float
    snippet: str
    skills: List[str]


class MatchResponse(BaseModel):
    job_id: int              # ← naya add kiya, run_match() ab ye return karta hai
    candidates: List[MatchCandidate]


class ProcessJobResponse(BaseModel):
    job_id: int
    improved_job_description: str
    total_candidates: int
    candidates: List[ProcessCandidate]


class CandidateDetailResponse(BaseModel):

    candidate_id: int
    candidate_name: str
    match_score: float

    why_matched: str

    why_not_matched: str

    summary: str

    skills: List[str]

    missing_skills: List[str]

    experience: float

    education: str

    interview_questions: List[str]

    resume_file: str


class JobQualityResponse(BaseModel):
    feedback: str


class FilterRequest(BaseModel):
    query: Optional[str] = None
    min_experience_years: Optional[int] = None
    required_skills: Optional[List[str]] = None
    education_level: Optional[str] = None
    location: Optional[str] = None
    category: Optional[str] = None


# ==========================================
# Filter Candidate — MatchCandidate se alag,
# kyunki isme "why_not_matched" extra field hai
# jo /match ke candidates me nahi hota
# ==========================================

class FilterCandidate(BaseModel):
    id: int
    name: str
    score: float
    snippet: str
    skills: List[str]
    why_not_matched: str = ""       # ← naya, default khaali string


class FilterResponse(BaseModel):
    candidates: List[FilterCandidate]
    weak_match: bool = False        # ← naya, warna ye field gayab ho jaati

# =====================================================
# Week 3 - Autonomous Recruiting Agent
# =====================================================

from typing import Any, Dict


class FillRoleRequest(BaseModel):
    """
    Request to start the autonomous recruiting agent.
    """

    job_id: Optional[int]=None
    goal: str
    

class FillRoleResponse(BaseModel):
    """
    Response after starting the agent.
    """

    run_id: str
    job_id: int   
    status: str


class AgentReport(BaseModel):

    job_id: int
    goal: str

    total_candidates: int

    top_candidates: List[Dict[str, Any]]

    candidate_summaries: List[Dict[str, Any]]

    interview_questions: List[Dict[str, Any]]

    improved_job_description: Any

    summary: str

    workflow_status: str

    trace: List[str]

    job_bottleneck_flag: bool   

class AgentRunResponse(BaseModel):
    """
    Response for GET /agent/runs/{run_id}
    """

    status: str

    report: AgentReport

    trace: List[str]