import json

import streamlit as st

from agents.recruiter_agent import RecruiterAgent
from database.database import initialize_database
from database.models import (
    get_applications,
    get_candidates,
    get_interviews,
    get_jobs,
    save_application,
    save_candidate,
    save_job,
)
from matching.matcher import match_candidate
from reports.report_generator import (
    applications_to_dataframe,
    dataframe_to_csv_bytes,
)
from resume_parser.docx_parser import extract_docx_text
from resume_parser.pdf_parser import extract_pdf_text
from resume_parser.resume_extractor import extract_candidate
from scheduling.scheduler import schedule_interview
from utils.validators import validate_resume_file


# ---------------------------------------------------------
# INITIALIZATION
# ---------------------------------------------------------

st.set_page_config(
    page_title="IndiaTech Recruiter AI",
    page_icon="🇮🇳",
    layout="wide",
)

initialize_database()


# ---------------------------------------------------------
# SESSION STATE
# ---------------------------------------------------------

if "current_candidate" not in st.session_state:
    st.session_state.current_candidate = None

if "current_job" not in st.session_state:
    st.session_state.current_job = None

if "current_match" not in st.session_state:
    st.session_state.current_match = None


# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------

st.sidebar.title("🇮🇳 IndiaTech Recruiter")

page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Screen Candidate",
        "Candidates",
        "Jobs",
        "Rankings",
        "Interviews",
        "Reports",
    ],
)


# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------

st.title("IndiaTech Recruiter AI")
st.caption(
    "AI-powered Indian technology recruitment assistant"
)


# =========================================================
# DASHBOARD
# =========================================================

if page == "Dashboard":

    candidates = get_candidates()
    jobs = get_jobs()
    applications = get_applications()
    interviews = get_interviews()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Candidates",
        len(candidates)
    )

    col2.metric(
        "Jobs",
        len(jobs)
    )

    col3.metric(
        "Applications",
        len(applications)
    )

    col4.metric(
        "Interviews",
        len(interviews)
    )

    st.divider()

    st.subheader("Top Candidates")

    if applications:

        display_columns = [
            "candidate_name",
            "job_title",
            "overall_score",
            "recommendation",
            "status",
        ]

        available = [
            column
            for column in display_columns
            if column in applications[0]
        ]

        st.dataframe(
            [
                {
                    column: application.get(column)
                    for column in available
                }
                for application in applications[:10]
            ],
            use_container_width=True,
        )

    else:

        st.info(
            "No candidate applications yet."
        )


# =========================================================
# SCREEN CANDIDATE
# =========================================================

elif page == "Screen Candidate":

    st.header("📄 Candidate Screening")

    st.subheader("1. Job Requirements")

    job_title = st.text_input(
        "Job Title",
        placeholder="Python Developer"
    )

    job_description = st.text_area(
        "Job Description",
        height=250,
        placeholder=(
            "Example:\n"
            "We are looking for a Python Developer "
            "with 2+ years experience in Python, "
            "Django and SQL..."
        ),
    )

    st.subheader("2. Resume")

    uploaded_file = st.file_uploader(
        "Upload Candidate Resume",
        type=["pdf", "docx"],
    )

    analyze_button = st.button(
        "🚀 Analyze Candidate",
        type="primary",
    )

    if analyze_button:

        # ------------------------------
        # Validation
        # ------------------------------

        if not job_title.strip():
            st.error("Please enter a job title.")
            st.stop()

        if not job_description.strip():
            st.error(
                "Please enter the job description."
            )
            st.stop()

        valid, message = validate_resume_file(
            uploaded_file
        )

        if not valid:
            st.error(message)
            st.stop()

        # ------------------------------
        # Parse Resume
        # ------------------------------

        try:

            with st.spinner(
                "Extracting resume text..."
            ):

                if uploaded_file.name.lower().endswith(
                    ".pdf"
                ):
                    resume_text = extract_pdf_text(
                        uploaded_file
                    )

                else:
                    resume_text = extract_docx_text(
                        uploaded_file
                    )

            if not resume_text.strip():

                st.error(
                    "No readable text was found in "
                    "the resume."
                )

                st.stop()

            # ------------------------------
            # Extract Candidate
            # ------------------------------

            with st.spinner(
                "Extracting candidate information..."
            ):

                candidate = extract_candidate(
                    resume_text
                )

            # ------------------------------
            # Job analysis
            # ------------------------------

            agent = None

            try:

                with st.spinner(
                    "Analyzing job requirements with Gemini..."
                ):

                    from agents.job_agent import JobAgent

                    job_agent = JobAgent()

                    job = job_agent.analyze(
                        job_description
                    )

            except Exception as exc:

                st.warning(
                    "Gemini job analysis unavailable. "
                    "Using basic job information."
                )

                job = {
                    "title": job_title,
                    "required_skills": [],
                    "experience_required": 0,
                    "education_required": "",
                    "location": "",
                    "min_salary": None,
                    "max_salary": None,
                    "max_notice_period": None,
                    "relocation_required": None,
                }

            job["title"] = job_title

            # ------------------------------
            # Matching
            # ------------------------------

            with st.spinner(
                "Matching candidate with job..."
            ):

                result = match_candidate(
                    candidate,
                    job
                )

            # ------------------------------
            # Save candidate
            # ------------------------------

            candidate_id = save_candidate(
                candidate
            )

            job_id = save_job(
                job,
                job_description
            )

            save_application(
                candidate_id,
                job_id,
                result
            )

            # ------------------------------
            # Session state
            # ------------------------------

            st.session_state.current_candidate = (
                candidate
            )

            st.session_state.current_job = job

            st.session_state.current_match = result

            st.success(
                "Candidate analyzed successfully!"
            )

        except Exception as exc:

            st.error(
                f"Candidate analysis failed: {exc}"
            )

            st.stop()

    # -----------------------------------------------------
    # DISPLAY RESULT
    # -----------------------------------------------------

    candidate = st.session_state.current_candidate
    job = st.session_state.current_job
    result = st.session_state.current_match

    if candidate and result:

        st.divider()

        st.subheader(
            f"Candidate: {candidate.get('name', 'Unknown')}"
        )

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Overall Match",
            f"{result['overall_score']}%"
        )

        col2.metric(
            "Experience",
            f"{result['experience_score']}%"
        )

        col3.metric(
            "Skills",
            f"{result['skill_score']}%"
        )

        st.divider()

        left, right = st.columns(2)

        with left:

            st.markdown("### Candidate Information")

            st.write(
                f"**Email:** {candidate.get('email', '-')}"
            )

            st.write(
                f"**Phone:** {candidate.get('phone', '-')}"
            )

            st.write(
                f"**Education:** "
                f"{candidate.get('education', '-')}"
            )

            st.write(
                f"**Location:** "
                f"{candidate.get('location', '-')}"
            )

            st.write(
                f"**Experience:** "
                f"{candidate.get('experience', 0)} years"
            )

            st.write(
                f"**Notice Period:** "
                f"{candidate.get('notice_period', '-')}"
            )

            salary = candidate.get(
                "expected_salary"
            )

            st.write(
                f"**Expected Salary:** "
                f"{salary if salary is not None else '-'} LPA"
            )

            relocation = candidate.get(
                "relocation"
            )

            st.write(
                f"**Relocation:** "
                f"{relocation if relocation is not None else '-'}"
            )

        with right:

            st.markdown("### Matching Analysis")

            st.write(
                "**Matched Skills**"
            )

            if result["matched_skills"]:

                st.success(
                    ", ".join(
                        result["matched_skills"]
                    )
                )

            else:

                st.info(
                    "No matching skills found."
                )

            st.write(
                "**Missing Skills**"
            )

            if result["missing_skills"]:

                st.error(
                    ", ".join(
                        result["missing_skills"]
                    )
                )

            else:

                st.success(
                    "No major missing required skills."
                )

            st.metric(
                "Recommendation",
                result["recommendation"]
            )


# =========================================================
# CANDIDATES
# =========================================================

elif page == "Candidates":

    st.header("👥 Candidates")

    candidates = get_candidates()

    if candidates:

        st.dataframe(
            candidates,
            use_container_width=True,
        )

    else:

        st.info(
            "No candidates available."
        )


# =========================================================
# JOBS
# =========================================================

elif page == "Jobs":

    st.header("💼 Jobs")

    jobs = get_jobs()

    if jobs:

        st.dataframe(
            jobs,
            use_container_width=True,
        )

    else:

        st.info(
            "No jobs available."
        )


# =========================================================
# RANKINGS
# =========================================================

elif page == "Rankings":

    st.header("🏆 Candidate Rankings")

    applications = get_applications()

    if applications:

        rows = []

        for index, application in enumerate(
            applications,
            start=1
        ):

            rows.append(
                {
                    "Rank": index,
                    "Candidate": application[
                        "candidate_name"
                    ],
                    "Job": application[
                        "job_title"
                    ],
                    "Match %": application[
                        "overall_score"
                    ],
                    "Recommendation": application[
                        "recommendation"
                    ],
                    "Status": application[
                        "status"
                    ],
                }
            )

        st.dataframe(
            rows,
            use_container_width=True,
        )

    else:

        st.info(
            "No ranked candidates yet."
        )


# =========================================================
# INTERVIEWS
# =========================================================

elif page == "Interviews":

    st.header("📅 Interview Scheduling")

    candidates = get_candidates()
    jobs = get_jobs()

    if not candidates or not jobs:

        st.warning(
            "Create a candidate and job before "
            "scheduling an interview."
        )

    else:

        candidate_options = {
            f"{c['name']} ({c['email']})": c["id"]
            for c in candidates
        }

        job_options = {
            j["title"]: j["id"]
            for j in jobs
        }

        selected_candidate = st.selectbox(
            "Candidate",
            list(candidate_options.keys())
        )

        selected_job = st.selectbox(
            "Job",
            list(job_options.keys())
        )

        interview_date = st.date_input(
            "Interview Date"
        )

        interview_time = st.time_input(
            "Interview Time"
        )

        interview_type = st.selectbox(
            "Interview Type",
            [
                "Technical",
                "HR",
                "Managerial",
            ]
        )

        notes = st.text_area(
            "Notes"
        )

        if st.button(
            "Schedule Interview",
            type="primary"
        ):

            try:

                schedule_interview(
                    candidate_options[
                        selected_candidate
                    ],
                    job_options[
                        selected_job
                    ],
                    interview_date,
                    interview_time,
                    interview_type,
                    notes,
                )

                st.success(
                    "Interview scheduled successfully!"
                )

            except Exception as exc:

                st.error(
                    f"Unable to schedule interview: {exc}"
                )

    st.divider()

    st.subheader(
        "Scheduled Interviews"
    )

    interviews = get_interviews()

    if interviews:

        st.dataframe(
            interviews,
            use_container_width=True,
        )

    else:

        st.info(
            "No interviews scheduled."
        )


# =========================================================
# REPORTS
# =========================================================

elif page == "Reports":

    st.header("📊 Reports & Export")

    applications = get_applications()

    if not applications:

        st.info(
            "No application data available."
        )

    else:

        df = applications_to_dataframe(
            applications
        )

        st.dataframe(
            df,
            use_container_width=True,
        )

        csv_data = dataframe_to_csv_bytes(
            df
        )

        st.download_button(
            label="⬇️ Download Candidate Report",
            data=csv_data,
            file_name="candidate_report.csv",
            mime="text/csv",
        )