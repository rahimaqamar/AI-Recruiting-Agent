from typing import TypedDict, List, Dict, Any
class AgentState(TypedDict):

    # =========================
    # Agent Tracking
    # =========================

    run_id: str
    RUNS: Dict[str, Any]


    # =========================
    # Input
    # =========================

    job_id: int

    goal: str

    job_description: str

    #  =====================
    # Adaptive planning
    # =======================
    plan: dict[str, any]
    # =========================
    # Candidate Data
    # =========================

    candidates: List[Dict[str, Any]]

    shortlisted_candidates: List[Dict[str, Any]]


    # =========================
    # Generated Results
    # =========================

    summaries: List[Dict[str, Any]]
    interview_questions: List[Dict[str, Any]]
    improved_job: str
    report: Dict[str, Any]


    # =========================
    # Workflow Tracking
    # =========================

    status: str
    report_status: str
    trace: List[str]