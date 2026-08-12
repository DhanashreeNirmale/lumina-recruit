import json

import pandas as pd
import streamlit as st

from database.models import get_applications


def show_ranking_page():

    st.header("🏆 Candidate Ranking")

    applications = get_applications()

    if not applications:

        st.info(
            "No candidate applications available."
        )

        return

    # --------------------------------------------------
    # FILTERS
    # --------------------------------------------------

    col1, col2 = st.columns(2)

    with col1:

        minimum_score = st.slider(
            "Minimum Match Score",
            min_value=0,
            max_value=100,
            value=0,
        )

    with col2:

        recommendations = [
            "All",
            "Shortlisted",
            "Review",
            "Not Shortlisted",
        ]

        recommendation_filter = st.selectbox(
            "Recommendation",
            recommendations
        )

    # --------------------------------------------------
    # FILTER APPLICATIONS
    # --------------------------------------------------

    filtered = []

    for application in applications:

        score = application.get(
            "overall_score",
            0
        )

        recommendation = application.get(
            "recommendation",
            ""
        )

        if score < minimum_score:
            continue

        if (
            recommendation_filter != "All"
            and recommendation
            != recommendation_filter
        ):
            continue

        filtered.append(
            application
        )

    if not filtered:

        st.warning(
            "No candidates match the selected filters."
        )

        return

    # --------------------------------------------------
    # RANKED TABLE
    # --------------------------------------------------

    rows = []

    for rank, application in enumerate(
        filtered,
        start=1
    ):

        rows.append(
            {
                "Rank": rank,
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
                "Skills": application.get(
                    "skill_score",
                    0
                ),
                "Experience": application.get(
                    "experience_score",
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

    df = pd.DataFrame(rows)

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
    )

    # --------------------------------------------------
    # CANDIDATE DETAILS
    # --------------------------------------------------

    st.divider()

    st.subheader(
        "Candidate Details"
    )

    names = [
        application.get(
            "candidate_name",
            "Unknown"
        )
        for application in filtered
    ]

    selected_name = st.selectbox(
        "Select Candidate",
        names
    )

    selected = next(
        application
        for application in filtered
        if application.get(
            "candidate_name"
        ) == selected_name
    )

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "Overall Match",
            f"{selected.get('overall_score', 0)}%"
        )

        st.metric(
            "Skill Score",
            f"{selected.get('skill_score', 0)}%"
        )

        st.metric(
            "Experience Score",
            f"{selected.get('experience_score', 0)}%"
        )

    with col2:

        st.metric(
            "Education Score",
            f"{selected.get('education_score', 0)}%"
        )

        st.metric(
            "Notice Score",
            f"{selected.get('notice_score', 0)}%"
        )

        st.metric(
            "Salary Score",
            f"{selected.get('salary_score', 0)}%"
        )

    st.write(
        "**Matched Skills**"
    )

    try:

        matched = json.loads(
            selected.get(
                "matched_skills",
                "[]"
            )
        )

        st.write(
            ", ".join(matched)
            if matched
            else "None"
        )

    except Exception:

        st.write(
            selected.get(
                "matched_skills",
                "-"
            )
        )

    st.write(
        "**Missing Skills**"
    )

    try:

        missing = json.loads(
            selected.get(
                "missing_skills",
                "[]"
            )
        )

        st.write(
            ", ".join(missing)
            if missing
            else "None"
        )

    except Exception:

        st.write(
            selected.get(
                "missing_skills",
                "-"
            )
        )