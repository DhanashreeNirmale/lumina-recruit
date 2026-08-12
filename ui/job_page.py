import streamlit as st

from agents.job_agent import JobAgent
from database.models import (
    get_jobs,
    save_job,
)


def show_job_page():

    st.header("💼 Job Management")

    tab1, tab2 = st.tabs(
        [
            "Create Job",
            "Existing Jobs",
        ]
    )

    # ==================================================
    # CREATE JOB
    # ==================================================

    with tab1:

        st.subheader(
            "Create New Technology Job"
        )

        job_title = st.text_input(
            "Job Title",
            placeholder="Python Developer"
        )

        job_description = st.text_area(
            "Job Description",
            height=250,
            placeholder=(
                "Enter complete job description..."
            )
        )

        if st.button(
            "🤖 Analyze & Create Job",
            type="primary"
        ):

            if not job_title.strip():

                st.error(
                    "Job title is required."
                )

                st.stop()

            if not job_description.strip():

                st.error(
                    "Job description is required."
                )

                st.stop()

            try:

                with st.spinner(
                    "AI is analyzing job requirements..."
                ):

                    agent = JobAgent()

                    job = agent.analyze(
                        job_description
                    )

                # Ensure manually entered title
                # remains the source of truth.

                job["title"] = job_title

                job_id = save_job(
                    job,
                    job_description
                )

                st.success(
                    f"Job created successfully! "
                    f"Job ID: {job_id}"
                )

                # --------------------------------------
                # DISPLAY EXTRACTED REQUIREMENTS
                # --------------------------------------

                st.subheader(
                    "AI Extracted Requirements"
                )

                col1, col2 = st.columns(2)

                with col1:

                    st.write(
                        "**Required Skills**"
                    )

                    skills = job.get(
                        "required_skills",
                        []
                    )

                    if skills:

                        st.write(
                            ", ".join(skills)
                        )

                    else:

                        st.info(
                            "No skills extracted."
                        )

                    st.write(
                        "**Experience Required**"
                    )

                    st.write(
                        f"{job.get('experience_required', 0)} years"
                    )

                    st.write(
                        "**Education**"
                    )

                    st.write(
                        job.get(
                            "education_required",
                            "-"
                        )
                    )

                with col2:

                    st.write(
                        "**Location**"
                    )

                    st.write(
                        job.get(
                            "location",
                            "-"
                        )
                    )

                    st.write(
                        "**Salary Range**"
                    )

                    minimum = job.get(
                        "min_salary"
                    )

                    maximum = job.get(
                        "max_salary"
                    )

                    if minimum or maximum:

                        st.write(
                            f"{minimum or '-'} - "
                            f"{maximum or '-'} LPA"
                        )

                    else:

                        st.write("-")

                    st.write(
                        "**Maximum Notice Period**"
                    )

                    st.write(
                        job.get(
                            "max_notice_period",
                            "-"
                        )
                    )

            except Exception as exc:

                st.error(
                    f"Unable to create job: {exc}"
                )

    # ==================================================
    # EXISTING JOBS
    # ==================================================

    with tab2:

        st.subheader(
            "Existing Jobs"
        )

        jobs = get_jobs()

        if not jobs:

            st.info(
                "No jobs have been created yet."
            )

            return

        for job in jobs:

            with st.expander(
                f"💼 {job.get('title', 'Untitled Job')}"
            ):

                col1, col2 = st.columns(2)

                with col1:

                    st.write(
                        f"**Location:** "
                        f"{job.get('location') or '-'}"
                    )

                    st.write(
                        f"**Experience:** "
                        f"{job.get('experience_required', 0)} years"
                    )

                    st.write(
                        f"**Education:** "
                        f"{job.get('education_required') or '-'}"
                    )

                with col2:

                    st.write(
                        f"**Salary:** "
                        f"{job.get('min_salary') or '-'} - "
                        f"{job.get('max_salary') or '-'} LPA"
                    )

                    st.write(
                        f"**Notice Period:** "
                        f"{job.get('max_notice_period') or '-'} days"
                    )

                st.write(
                    "**Required Skills:**"
                )

                skills = job.get(
                    "required_skills",
                    "[]"
                )

                st.code(
                    str(skills)
                )

                st.write(
                    "**Job Description:**"
                )

                st.write(
                    job.get(
                        "description",
                        "-"
                    )
                )