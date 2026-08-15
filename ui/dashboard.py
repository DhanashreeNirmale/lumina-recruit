import streamlit as st
import pandas as pd

from database.models import (
    get_candidates,
    get_jobs,
    get_interviews,
)


def show_dashboard():

    st.title("📊 Recruitment Dashboard")

    st.caption(
        "Track A • Option A1 • Indian Tech Recruitment"
    )

    candidates = get_candidates()
    jobs = get_jobs()
    interviews = get_interviews()

    # ========================================================
    # METRICS
    # ========================================================

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Candidates",
        len(candidates)
    )

    col2.metric(
        "Jobs",
        len(jobs)
    )

    col3.metric(
        "Scheduled Interviews",
        len(interviews)
    )

    st.divider()

    # ========================================================
    # CANDIDATE PIPELINE
    # ========================================================

    st.subheader("👥 Candidate Pipeline")

    if candidates:

        df = pd.DataFrame(
            candidates
        )

        columns = [
            "id",
            "name",
            "email",
            "score",
            "status",
            "location",
        ]

        available_columns = [
            column
            for column in columns
            if column in df.columns
        ]

        st.dataframe(
            df[available_columns],
            use_container_width=True,
            hide_index=True,
        )

    else:

        st.info(
            "No candidates yet. "
            "Go to Candidates and upload resumes."
        )

    # ========================================================
    # UPCOMING INTERVIEWS
    # ========================================================

    st.subheader("📅 Upcoming Interviews")

    if interviews:

        df = pd.DataFrame(
            interviews
        )

        columns = [
            "candidate_name",
            "job_title",
            "interview_date",
            "interview_time",
            "mode",
            "status",
        ]

        available_columns = [
            column
            for column in columns
            if column in df.columns
        ]

        st.dataframe(
            df[available_columns],
            use_container_width=True,
            hide_index=True,
        )

    else:

        st.info(
            "No interviews scheduled."
        )