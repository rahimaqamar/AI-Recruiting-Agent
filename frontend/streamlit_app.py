import streamlit as st
import requests
import time

# =====================================================
# CONFIGURATION
# =====================================================

API_URL = "http://127.0.0.1:8000"
POLL_INTERVAL = 2

st.set_page_config(
    page_title="TalentMatch AI",
    page_icon="🤖",
    layout="wide"
)

# =====================================================
# API FUNCTIONS
# =====================================================

def start_agent(goal):

    try:

        response = requests.post(
            f"{API_URL}/agent/fill-role",
            json={"goal": goal}
        )

        return response.json()

    except Exception as e:

        return {
            "error": str(e)
        }


def get_run(run_id):

    try:

        response = requests.get(
            f"{API_URL}/agent/runs/{run_id}"
        )

        return response.json()

    except Exception as e:

        return {
            "error": str(e)
        }


# =====================================================
# STATUS PROGRESS
# =====================================================

STAGES = [
    "planning",
    "searching",
    "evaluating",
    "summaries",
    "interview",
    "self_check",
    "completed"
]


def show_progress(status):

    values = {
        "planning": 10,
        "searching": 25,
        "evaluating": 45,
        "summaries": 65,
        "interview": 80,
        "self_check": 90,
        "completed": 100
    }

    st.progress(values.get(status, 0))

    for stage in STAGES:

        if stage == status:

            st.warning(f"⏳ {stage.title()}")

        elif STAGES.index(stage) < STAGES.index(status):

            st.success(f"✅ {stage.title()}")

        else:

            st.write(f"⬜ {stage.title()}")


# =====================================================
# TITLE
# =====================================================

st.title("🤖 TalentMatch AI Recruiting Agent")

left, right = st.columns([1,2])

# =====================================================
# LEFT PANEL
# =====================================================

with left:

    st.header("Recruiter Goal")

    goal = st.text_area(
        "Recruiter Goal",
        label_visibility="collapsed",
        height=220,
        placeholder="""
Example:

Find the best Frontend React Developers.

Prioritize React, TypeScript and Docker.

Review at least 10 candidates.

Generate interview questions.

Return the best shortlist.
"""
    )

    if st.button(
        "🚀 Start Agent",
        use_container_width=True
    ):

        if not goal.strip():

            st.error("Please enter recruiter goal.")

        else:

            st.session_state.pop("run_id", None)
            st.session_state.pop("job_id", None)

            response = start_agent(goal)

            if "run_id" in response:

                st.session_state.run_id = response["run_id"]
                st.session_state.job_id = response["job_id"]

                st.success("✅ Agent Started Successfully")

            else:

                st.error(
                    response.get(
                        "detail",
                        response.get(
                            "error",
                            "Unable to start agent."
                        )
                    )
                )

    st.divider()

    if "run_id" in st.session_state:

        st.subheader("Current Run")

        st.info(f"Run ID : {st.session_state.run_id}")

        st.info(f"Job ID : {st.session_state.job_id}")

# =====================================================
# RIGHT PANEL
# =====================================================

with right:

    st.header("Agent Execution")

    if "run_id" not in st.session_state:

        st.info("Start an AI Agent from the left panel.")

    else:

        run = get_run(
            st.session_state.run_id
        )

        if "status" not in run:

            st.error(
                run.get(
                    "detail",
                    "Run not found."
                )
            )

            st.stop()

        status = run["status"]

        st.metric(
            "Current Status",
            status.upper()
        )

        show_progress(status)

        st.divider()
                # ===========================================
        # LIVE EXECUTION TRACE
        # ===========================================

        st.subheader("⚙️ Execution Trace")

        trace = run.get("trace", [])

        trace_container = st.container(border=True)

        with trace_container:

            if len(trace) == 0:

                st.info("Waiting for the agent to start...")

            else:

                for i, step in enumerate(trace, start=1):

                    st.write(f"**Step {i}:** {step}")

        st.divider()

        # ===========================================
        # AGENT STATUS CARD
        # ===========================================

        st.subheader("📊 Current Status")

        status_color = {
            "planning": "🟡",
            "searching": "🔍",
            "evaluating": "🟠",
            "summaries": "📝",
            "interview": "🎯",
            "self_check": "✅",
            "completed": "🎉",
            "error": "❌"
        }

        st.success(
            f"{status_color.get(status,'')}  {status.upper()}"
        )

        # ===========================================
        # LIVE METRICS
        # ===========================================

        report = run.get("report", {})

        c1, c2, c3 = st.columns(3)

        with c1:

            st.metric(
                "Job ID",
                report.get(
                    "job_id",
                    st.session_state.job_id
                )
            )

        with c2:

            st.metric(
                "Candidates Found",
                len(
                    report.get(
                        "top_candidates",
                        []
                    )
                )
            )

        with c3:

            st.metric(
                "Workflow",
                report.get(
                    "workflow_status",
                    status
                )
            )

        st.divider()

        # ===========================================
        # STILL RUNNING
        # ===========================================

        if status not in ["completed", "error"]:

            with st.spinner("Agent is working..."):

                time.sleep(POLL_INTERVAL)

                st.rerun()

        # ===========================================
        # ERROR
        # ===========================================

        elif status == "error":

            st.error(
                run.get(
                    "error",
                    "Unknown Error"
                )
            )

            st.stop()

        # ===========================================
        # COMPLETED
        # Part 3 starts here...
        # ===========================================

        else:

            report = run.get("report", {})

            st.success("✅ Agent completed successfully.")

            st.divider()
                    # ==========================================================
        # HIRING REPORT
        # ==========================================================

        st.header("📋 Hiring Report")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Job ID",
                report.get("job_id", "-")
            )

        with col2:
            st.metric(
                "Candidates",
                len(report.get("top_candidates", []))
            )

        with col3:
            st.metric(
                "Workflow",
                report.get("workflow_status", "Completed")
            )

        st.divider()

        # ==========================================================
        # TOP CANDIDATES
        # ==========================================================

        st.header("🏆 Top Candidates")

        summaries = {
            s["candidate_id"]: s["summary"]
            for s in report.get("candidate_summaries", [])
        }

        candidates = report.get("top_candidates", [])

        if len(candidates) == 0:

            st.warning("No candidates shortlisted.")

        else:

            for candidate in candidates:

                score = candidate.get(
                    "similarity_score",
                    candidate.get("score", 0)
                )

                with st.expander(
                    f"{candidate.get('name','Unknown')}   ⭐ {score:.2f}",
                    expanded=False
                ):

                    c1, c2 = st.columns(2)

                    with c1:

                        st.write(
                            "**Candidate ID:**",
                            candidate.get("candidate_id")
                        )

                        st.write(
                            "**Experience:**",
                            candidate.get("experience", "N/A")
                        )

                        st.write(
                            "**Education:**",
                            candidate.get("education", "N/A")
                        )

                    with c2:

                        st.write(
                            "**Location:**",
                            candidate.get("location", "N/A")
                        )

                        st.write(
                            "**Similarity Score:**",
                            score
                        )

                    st.write(
                        "**Skills**"
                    )

                    skills = candidate.get("skills", [])

                    if isinstance(skills, list):

                        st.write(", ".join(skills))

                    else:

                        st.write(skills)

                    st.write(
                        "**Why Shortlisted**"
                    )

                    st.info(
                        candidate.get(
                            "why_matched",
                            "No explanation available."
                        )
                    )

                    st.write(
                        "**Candidate Summary**"
                    )

                    st.success(
                        summaries.get(
                            candidate.get("candidate_id"),
                            "Summary not available."
                        )
                    )

        st.divider()

        # ==========================================================
        # INTERVIEW QUESTIONS
        # ==========================================================

        st.header("🎯 Interview Questions")

        interviews = report.get(
            "interview_questions",
            []
        )

        if len(interviews) == 0:

            st.info("No interview questions generated.")

        else:

            for interview in interviews:

                with st.expander(
                    f"Candidate {interview['candidate_id']}"
                ):

                    for index, question in enumerate(
                        interview.get("questions", []),
                        start=1
                    ):

                        st.write(
                            f"{index}. {question}"
                        )

        st.divider()

        # ==========================================================
        # JOB REVIEW
        # ==========================================================

        st.header("📝 Job Review")

        review = report.get(
            "improved_job_description",
            "No review available."
        )

        st.write(review)

        st.divider()

        # ==========================================================
        # JOB BOTTLENECK
        # ==========================================================

        st.header("🚩 Job Posting Analysis")

        if report.get("job_bottleneck_flag"):

            st.warning(
                "This job description may reduce the quality or number of candidates."
            )

        else:

            st.success(
                "The job description looks good."
            )

        st.divider()

        # ==========================================================
        # FINAL RECOMMENDATION
        # ==========================================================

        st.header("📄 Final Recommendation")

        st.write(
            report.get(
                "summary",
                "No recommendation generated."
            )
        )

        st.divider()

        # ==========================================================
        # COMPLETE EXECUTION TRACE
        # ==========================================================

        st.header("📜 Complete Execution Trace")

        for index, step in enumerate(
            report.get("trace", []),
            start=1
        ):

            st.write(f"{index}. {step}")

        st.balloons()