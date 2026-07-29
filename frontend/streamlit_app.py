import streamlit as st
import requests
import time

API_URL = "http://127.0.0.1:8000"
POLL_INTERVAL = 2


# ===========================================
# API FUNCTIONS
# ===========================================

def start_agent(goal):
    try:
        response = requests.post(
            f"{API_URL}/agent/fill-role",
            json={"goal": goal}
        )
        return response.json()
    except Exception as e:
        return {"error": str(e)}


def get_run(run_id):
    try:
        response = requests.get(
            f"{API_URL}/agent/runs/{run_id}"
        )
        return response.json()
    except Exception as e:
        return {"error": str(e)}


# ===========================================
# PROGRESS
# ===========================================

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

    if status == "error":
        st.error("❌ Agent execution failed.")
        return

    progress = {
        "planning": 10,
        "searching": 25,
        "evaluating": 45,
        "summaries": 65,
        "interview": 80,
        "self_check": 90,
        "completed": 100
    }

    st.progress(progress.get(status, 0))

    for stage in STAGES:

        if STAGES.index(stage) < STAGES.index(status):
            st.success(f"✅ {stage.title()}")

        elif stage == status:
            st.warning(f"⏳ {stage.title()}")

        else:
            st.write(f"⬜ {stage.title()}")


# ===========================================
# PAGE
# ===========================================

st.set_page_config(
    page_title="TalentMatch AI",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 TalentMatch AI Recruiting Agent")

left, right = st.columns([1, 2])

# =====================================================
# LEFT PANEL
# =====================================================

with left:

    st.subheader("Recruiter Goal")

    goal = st.text_area(
        "",
        height=180,
        placeholder="""Example:
Find the best Frontend React Developers.
Prioritize React and TypeScript.
Review at least 10 candidates."""
    )

    if st.button("🚀 Start Agent", use_container_width=True):

        if not goal.strip():
            st.error("Please enter a goal.")

        else:

            st.session_state.pop("run_id", None)

            response = start_agent(goal)

            if "run_id" in response:

                st.session_state.run_id = response["run_id"]

                st.success("Agent Started")

            else:

                st.error(response.get("detail", response.get("error")))


# =====================================================
# RIGHT PANEL
# =====================================================

with right:

    st.subheader("Agent Execution")

    if "run_id" in st.session_state:

        run = get_run(st.session_state.run_id)

        if "status" not in run:

            st.error(run.get("detail", "Run not found"))
            st.stop()

        status = run["status"]

        st.info(f"Run ID : {st.session_state.run_id}")

        show_progress(status)

        st.divider()

        # ===========================================
        # EXECUTION TRACE
        # ===========================================

        st.subheader("Execution Trace")

        trace = run.get("trace", [])

        if trace:

            for t in trace:
                st.write("•", t)

        else:

            st.info("Waiting for agent...")

        # ===========================================

        if status == "completed":

            report = run.get("report", {})

            st.divider()

            st.header("📋 Hiring Report")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Job ID", report.get("job_id", "-"))

            with col2:
                st.metric("Candidates", len(report.get("top_candidates", [])))

            with col3:
                st.metric(
                    "Status",
                    report.get("workflow_status", "Completed")
                )

            # ===========================================

            st.subheader("🏆 Top Candidates")

            summaries = {
                s["candidate_id"]: s["summary"]
                for s in report.get("candidate_summaries", [])
            }

            for candidate in report.get("top_candidates", []):

                with st.expander(
                    f"{candidate.get('name')} ({candidate.get('similarity_score',0):.2f})",
                    expanded=True
                ):

                    st.write(
                        "**Candidate ID:**",
                        candidate.get("candidate_id")
                    )

                    st.write(
                        "**Similarity Score:**",
                        candidate.get("similarity_score")
                    )

                    st.write(
                        "**Skills:**",
                        ", ".join(candidate.get("skills", []))
                    )

                    st.write(
                        "**Experience:**",
                        candidate.get("experience")
                    )

                    st.write(
                        "**Education:**",
                        candidate.get("education")
                    )

                    st.write(
                        "**Location:**",
                        candidate.get("location")
                    )

                    st.write(
                        "**Why Shortlisted:**",
                        candidate.get("why_matched", "")
                    )

                    st.write(
                        "**Summary:**",
                        summaries.get(
                            candidate.get("candidate_id"),
                            "Not available"
                        )
                    )

            # ===========================================

            st.subheader("🎯 Interview Questions")

            for interview in report.get("interview_questions", []):

                with st.expander(
                    f"Candidate {interview['candidate_id']}"
                ):

                    for q in interview.get("questions", []):

                        st.write("•", q)

            # ===========================================

            st.subheader("📝 Job Review")

            st.write(
                report.get(
                    "improved_job_description",
                    "No suggestions."
                )
            )

            if report.get("job_bottleneck_flag"):

                st.warning(
                    "⚠ Job description may reduce candidate quality."
                )

            else:

                st.success(
                    "✅ Job description looks good."
                )

            # ===========================================

            st.subheader("📄 Final Recommendation")

            st.write(
                report.get(
                    "summary",
                    "No final summary available."
                )
            )

        elif status == "error":

            st.error(run.get("error", "Unknown Error"))

        else:

            time.sleep(POLL_INTERVAL)
            st.rerun()