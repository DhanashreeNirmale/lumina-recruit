import streamlit as st

from database.models import (
    get_applications,
    get_candidates,
    get_interviews,
    get_jobs,
)


def show_dashboard():

    st.header("📊 Recruitment Dashboard")

    candidates = get_candidates()
    jobs = get_jobs()
    applications = get_applications()
    interviews = get_interviews()

    # --------------------------------------------------
    # KPI CARDS
    # --------------------------------------------------

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total Candidates",
        len(candidates)
    )

    col2.metric(
        "Active Jobs",
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

    # --------------------------------------------------
    # RECRUITMENT PIPELINE
    # --------------------------------------------------

    st.subheader("Recruitment Pipeline")

    shortlisted = sum(
        1
        for application in applications
        if application.get("recommendation")
        == "Shortlisted"
    )

    review = sum(
        1
        for application in applications
        if application.get("recommendation")
        == "Review"
    )

    rejected = sum(
        1
        for application in applications
        if application.get("recommendation")
        == "Not Shortlisted"
    )

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Shortlisted",
        shortlisted
    )

    col2.metric(
        "Needs Review",
        review
    )

    col3.metric(
        "Not Shortlisted",
        rejected
    )

    st.divider()

    # --------------------------------------------------
    # TOP CANDIDATES
    # --------------------------------------------------

    st.subheader("🏆 Top Candidates")

    if not applications:

        st.info(
            "No candidate applications available yet."
        )

        return

    top_candidates = applications[:10]

    rows = []

    for index, application in enumerate(
        top_candidates,
        start=1
    ):

        rows.append(
            {
                "Rank": index,
                "Candidate": application.get(
                    "candidate_name",
                    "-"
                ),
                "Job": application.get(
                    "job_title",
                    "-"
                ),
                "Match Score": application.get(
                    "overall_score",
                    0
                ),
                "Recommendation": application.get(
                    "recommendation",
                    "-"
                ),
                "Status": application.get(
                    "status",
                    "-"
                ),
            }
        )

    st.dataframe(
        rows,
        use_container_width=True,
        hide_index=True,
    )