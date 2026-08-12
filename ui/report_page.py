import pandas as pd
import streamlit as st

from database.models import (
    get_applications,
    get_candidates,
    get_interviews,
    get_jobs,
)


def show_report_page():

    st.header("📈 Recruitment Reports")

    candidates = get_candidates()
    jobs = get_jobs()
    applications = get_applications()
    interviews = get_interviews()

    # ==================================================
    # SUMMARY
    # ==================================================

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

    # ==================================================
    # APPLICATION REPORT
    # ==================================================

    st.subheader(
        "Candidate Application Report"
    )

    if not applications:

        st.info(
            "No application data available."
        )

    else:

        df = pd.DataFrame(
            applications
        )

        # ----------------------------------------------
        # DISPLAY
        # ----------------------------------------------

        display_columns = [
            "candidate_name",
            "job_title",
            "overall_score",
            "skill_score",
            "experience_score",
            "recommendation",
            "status",
        ]

        available_columns = [
            column
            for column in display_columns
            if column in df.columns
        ]

        st.dataframe(
            df[available_columns],
            use_container_width=True,
            hide_index=True,
        )

        # ----------------------------------------------
        # CSV DOWNLOAD
        # ----------------------------------------------

        csv_data = df.to_csv(
            index=False
        ).encode("utf-8")

        st.download_button(
            label="⬇️ Download Full CSV Report",
            data=csv_data,
            file_name="recruitment_report.csv",
            mime="text/csv",
        )

    # ==================================================
    # SCORE DISTRIBUTION
    # ==================================================

    if applications:

        st.divider()

        st.subheader(
            "Match Score Distribution"
        )

        scores = [
            application.get(
                "overall_score",
                0
            )
            for application in applications
        ]

        score_df = pd.DataFrame(
            {
                "Match Score": scores
            }
        )

        st.bar_chart(
            score_df
        )

    # ==================================================
    # RECOMMENDATIONS
    # ==================================================

    if applications:

        st.divider()

        st.subheader(
            "Recommendation Summary"
        )

        shortlisted = sum(
            1
            for application in applications
            if application.get(
                "recommendation"
            ) == "Shortlisted"
        )

        review = sum(
            1
            for application in applications
            if application.get(
                "recommendation"
            ) == "Review"
        )

        rejected = sum(
            1
            for application in applications
            if application.get(
                "recommendation"
            ) == "Not Shortlisted"
        )

        summary = pd.DataFrame(
            {
                "Category": [
                    "Shortlisted",
                    "Review",
                    "Not Shortlisted",
                ],
                "Candidates": [
                    shortlisted,
                    review,
                    rejected,
                ],
            }
        )

        st.bar_chart(
            summary.set_index(
                "Category"
            )
        )