import streamlit as st

from database.models import (
    get_candidates,
    get_interviews,
    get_jobs,
)
from scheduling.scheduler import schedule_interview


def show_interview_page():

    st.header("📅 Interview Management")

    candidates = get_candidates()
    jobs = get_jobs()

    if not candidates:

        st.warning(
            "No candidates available."
        )

    elif not jobs:

        st.warning(
            "No jobs available."
        )

    else:

        st.subheader(
            "Schedule Interview"
        )

        candidate_options = {
            f"{candidate.get('name', 'Unknown')} "
            f"({candidate.get('email', '-')})":
            candidate.get("id")
            for candidate in candidates
        }

        job_options = {
            job.get("title", "Untitled"):
            job.get("id")
            for job in jobs
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
                "Final Round",
            ]
        )

        notes = st.text_area(
            "Interview Notes",
            placeholder=(
                "Optional instructions for the interviewer..."
            )
        )

        if st.button(
            "📅 Schedule Interview",
            type="primary"
        ):

            try:

                interview_id = schedule_interview(
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
                    f"Interview scheduled successfully! "
                    f"Interview ID: {interview_id}"
                )

            except Exception as exc:

                st.error(
                    f"Unable to schedule interview: {exc}"
                )

    # ==================================================
    # SCHEDULED INTERVIEWS
    # ==================================================

    st.divider()

    st.subheader(
        "Scheduled Interviews"
    )

    interviews = get_interviews()

    if not interviews:

        st.info(
            "No interviews scheduled."
        )

        return

    for interview in interviews:

        with st.expander(
            f"📅 "
            f"{interview.get('candidate_name', '-')}"
            f" — "
            f"{interview.get('job_title', '-')}"
        ):

            col1, col2 = st.columns(2)

            with col1:

                st.write(
                    f"**Date:** "
                    f"{interview.get('interview_date', '-')}"
                )

                st.write(
                    f"**Time:** "
                    f"{interview.get('interview_time', '-')}"
                )

            with col2:

                st.write(
                    f"**Type:** "
                    f"{interview.get('interview_type', '-')}"
                )

                st.write(
                    f"**Status:** "
                    f"{interview.get('status', '-')}"
                )

            if interview.get("notes"):

                st.write(
                    f"**Notes:** "
                    f"{interview.get('notes')}"
                )