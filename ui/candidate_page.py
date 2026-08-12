import streamlit as st

from database.models import (
    get_candidates,
    get_jobs,
    save_application,
    save_candidate,
    save_job,
)
from matching.matcher import match_candidate
from resume_parser.docx_parser import extract_docx_text
from resume_parser.pdf_parser import extract_pdf_text
from resume_parser.resume_extractor import extract_candidate
from utils.validators import validate_resume_file


def show_candidate_page():

    st.header("👤 AI Candidate Screening")

    st.write(
        "Upload a candidate resume and match it "
        "against an Indian technology job."
    )

    # ==================================================
    # JOB SELECTION
    # ==================================================

    jobs = get_jobs()

    if not jobs:

        st.warning(
            "No jobs available. "
            "Create a job first."
        )

        return

    job_names = [
        job["title"]
        for job in jobs
    ]

    selected_job_name = st.selectbox(
        "Select Job",
        job_names
    )

    selected_job = next(
        job
        for job in jobs
        if job["title"] == selected_job_name
    )

    st.divider()

    # ==================================================
    # RESUME UPLOAD
    # ==================================================

    uploaded_file = st.file_uploader(
        "Upload Resume",
        type=["pdf", "docx"]
    )

    analyze = st.button(
        "🚀 Screen Candidate",
        type="primary"
    )

    if analyze:

        # ------------------------------------------------
        # VALIDATION
        # ------------------------------------------------

        valid, message = validate_resume_file(
            uploaded_file
        )

        if not valid:

            st.error(message)

            return

        try:

            # ------------------------------------------------
            # RESUME PARSING
            # ------------------------------------------------

            with st.spinner(
                "Reading resume..."
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
                    "No readable text found in resume."
                )

                return

            # ------------------------------------------------
            # CANDIDATE EXTRACTION
            # ------------------------------------------------

            with st.spinner(
                "Extracting candidate information..."
            ):

                candidate = extract_candidate(
                    resume_text
                )

            # ------------------------------------------------
            # MATCHING
            # ------------------------------------------------

            with st.spinner(
                "Calculating job compatibility..."
            ):

                result = match_candidate(
                    candidate,
                    selected_job
                )

            # ------------------------------------------------
            # DATABASE
            # ------------------------------------------------

            candidate_id = save_candidate(
                candidate
            )

            application_id = save_application(
                candidate_id,
                selected_job["id"],
                result
            )

            # ------------------------------------------------
            # SAVE TO SESSION
            # ------------------------------------------------

            st.session_state[
                "screened_candidate"
            ] = candidate

            st.session_state[
                "screened_result"
            ] = result

            st.session_state[
                "screened_candidate_id"
            ] = candidate_id

            st.session_state[
                "screened_job_id"
            ] = selected_job["id"]

            st.success(
                "Candidate screened successfully!"
            )

        except Exception as exc:

            st.error(
                f"Screening failed: {exc}"
            )

            return

    # ==================================================
    # DISPLAY SCREENING RESULT
    # ==================================================

    candidate = st.session_state.get(
        "screened_candidate"
    )

    result = st.session_state.get(
        "screened_result"
    )

    if not candidate or not result:

        return

    st.divider()

    st.subheader(
        f"Candidate: {candidate.get('name', '-')}"
    )

    # ==================================================
    # SCORE
    # ==================================================

    score = result.get(
        "overall_score",
        0
    )

    if score >= 80:

        st.success(
            f"🎯 Strong Match — {score}%"
        )

    elif score >= 65:

        st.warning(
            f"⚠️ Needs Review — {score}%"
        )

    else:

        st.error(
            f"❌ Low Match — {score}%"
        )

    # ==================================================
    # CANDIDATE DETAILS
    # ==================================================

    col1, col2 = st.columns(2)

    with col1:

        st.subheader(
            "Candidate Information"
        )

        st.write(
            f"**Name:** "
            f"{candidate.get('name', '-')}"
        )

        st.write(
            f"**Email:** "
            f"{candidate.get('email', '-')}"
        )

        st.write(
            f"**Phone:** "
            f"{candidate.get('phone', '-')}"
        )

        st.write(
            f"**Education:** "
            f"{candidate.get('education', '-')}"
        )

        st.write(
            f"**Experience:** "
            f"{candidate.get('experience', 0)} years"
        )

        st.write(
            f"**Location:** "
            f"{candidate.get('location', '-')}"
        )

        st.write(
            f"**Notice Period:** "
            f"{candidate.get('notice_period', '-')}"
        )

    with col2:

        st.subheader(
            "Matching Breakdown"
        )

        st.metric(
            "Overall Score",
            f"{result.get('overall_score', 0)}%"
        )

        st.metric(
            "Skill Match",
            f"{result.get('skill_score', 0)}%"
        )

        st.metric(
            "Experience Match",
            f"{result.get('experience_score', 0)}%"
        )

        st.metric(
            "Education Match",
            f"{result.get('education_score', 0)}%"
        )

    # ==================================================
    # SKILLS
    # ==================================================

    st.divider()

    col1, col2 = st.columns(2)

    with col1:

        st.subheader(
            "✅ Matched Skills"
        )

        matched = result.get(
            "matched_skills",
            []
        )

        if matched:

            for skill in matched:

                st.success(
                    skill
                )

        else:

            st.info(
                "No matching skills."
            )

    with col2:

        st.subheader(
            "❌ Missing Skills"
        )

        missing = result.get(
            "missing_skills",
            []
        )

        if missing:

            for skill in missing:

                st.error(
                    skill
                )

        else:

            st.success(
                "No major missing skills."
            )

    # ==================================================
    # RAW RESUME
    # ==================================================

    with st.expander(
        "📄 View Extracted Resume Text"
    ):

        st.text(
            candidate.get(
                "resume_text",
                ""
            )
        )