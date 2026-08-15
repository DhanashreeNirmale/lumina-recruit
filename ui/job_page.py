import json

import streamlit as st

from agents.job_agent import JobAgent
from database.models import (
    create_job,
    get_jobs,
    decode_json_fields,
)


def _as_list(value):

    if isinstance(value, list):
        return value

    if isinstance(value, str):

        try:

            parsed = json.loads(value)

            if isinstance(parsed, list):
                return parsed

        except json.JSONDecodeError:
            pass

        return [
            item.strip()
            for item in value.split(",")
            if item.strip()
        ]

    return []


def show_job_page():

    st.title("💼 Job Requirements")

    st.caption(
        "AI-powered job requirement extraction"
    )

    tab1, tab2 = st.tabs(
        [
            "➕ Create Job",
            "📋 Saved Jobs",
        ]
    )

    # ========================================================
    # CREATE JOB
    # ========================================================

    with tab1:

        st.subheader(
            "Create New Job"
        )

        title = st.text_input(
            "Job Title *",
            placeholder="e.g. Java Developer"
        )

        description = st.text_area(
            "Job Description *",
            height=300,
            placeholder=(
                "Paste the complete job description here..."
            ),
        )

        if st.button(
            "🤖 Analyze Job with AI",
            type="primary",
        ):

            if not title.strip():

                st.error(
                    "Job title is required."
                )

            elif not description.strip():

                st.error(
                    "Job description is required."
                )

            else:

                try:

                    result = JobAgent().analyze(
                        description
                    )

                    st.session_state[
                        "job_analysis"
                    ] = result

                    st.success(
                        "Job requirements extracted successfully."
                    )

                except Exception as exc:

                    st.error(
                        f"Job analysis failed: {exc}"
                    )

        analysis = st.session_state.get(
            "job_analysis"
        )

        # ====================================================
        # SHOW AI ANALYSIS
        # ====================================================

        if analysis:

            st.subheader(
                "🔍 Extracted Requirements"
            )

            col1, col2 = st.columns(2)

            with col1:

                st.write(
                    "**Job Title:**",
                    analysis.get(
                        "job_title",
                        title
                    )
                )

                st.write(
                    "**Experience:**",
                    analysis.get(
                        "experience",
                        ""
                    )
                )

                st.write(
                    "**Notice Period:**",
                    analysis.get(
                        "notice_period",
                        ""
                    )
                )

                st.write(
                    "**Location:**",
                    analysis.get(
                        "location",
                        ""
                    )
                )

            with col2:

                st.write(
                    "**Salary:**",
                    f"{analysis.get('salary_min_lpa', '-')} "
                    f"to "
                    f"{analysis.get('salary_max_lpa', '-')} LPA"
                )

                st.write(
                    "**Regional Preference:**",
                    analysis.get(
                        "regional_preference",
                        ""
                    )
                )

                st.write(
                    "**Relocation:**",
                    analysis.get(
                        "relocation_willingness",
                        ""
                    )
                )

            st.write(
                "**Required Skills:**"
            )

            st.write(
                ", ".join(
                    _as_list(
                        analysis.get(
                            "required_skills"
                        )
                    )
                )
            )

            st.write(
                "**Preferred Skills:**"
            )

            st.write(
                ", ".join(
                    _as_list(
                        analysis.get(
                            "preferred_skills"
                        )
                    )
                )
            )

            st.write(
                "**Education:**"
            )

            st.write(
                ", ".join(
                    _as_list(
                        analysis.get(
                            "education"
                        )
                    )
                )
            )

            st.write(
                "**Responsibilities:**"
            )

            for responsibility in _as_list(
                analysis.get(
                    "responsibilities"
                )
            ):

                st.write(
                    f"• {responsibility}"
                )

            # =================================================
            # SAVE
            # =================================================

            if st.button(
                "💾 Save Job",
                type="primary",
            ):

                data = {

                    "title": (
                        title.strip()
                        or analysis.get(
                            "job_title",
                            "Untitled Job"
                        )
                    ),

                    "description": description,

                    "required_skills": _as_list(
                        analysis.get(
                            "required_skills"
                        )
                    ),

                    "preferred_skills": _as_list(
                        analysis.get(
                            "preferred_skills"
                        )
                    ),

                    "experience": analysis.get(
                        "experience",
                        ""
                    ),

                    "education": _as_list(
                        analysis.get(
                            "education"
                        )
                    ),

                    "notice_period": analysis.get(
                        "notice_period",
                        ""
                    ),

                    "salary_min_lpa": analysis.get(
                        "salary_min_lpa"
                    ),

                    "salary_max_lpa": analysis.get(
                        "salary_max_lpa"
                    ),

                    "location": analysis.get(
                        "location",
                        ""
                    ),

                    "regional_preference": analysis.get(
                        "regional_preference",
                        ""
                    ),

                    "relocation_willingness": analysis.get(
                        "relocation_willingness",
                        ""
                    ),
                }

                try:

                    job_id = create_job(
                        data
                    )

                    st.success(
                        f"Job saved successfully. "
                        f"Job ID: {job_id}"
                    )

                    st.session_state.pop(
                        "job_analysis",
                        None
                    )

                except Exception as exc:

                    st.error(
                        f"Could not save job: {exc}"
                    )

    # ========================================================
    # SAVED JOBS
    # ========================================================

    with tab2:

        st.subheader(
            "📋 Saved Jobs"
        )

        jobs = get_jobs()

        if not jobs:

            st.info(
                "No jobs saved yet."
            )

            return

        for job in jobs:

            item = decode_json_fields(
                job
            )

            with st.expander(
                f"#{item['id']} — {item['title']}"
            ):

                st.write(
                    "**Description:**"
                )

                st.write(
                    item["description"]
                )

                st.write(
                    "**Required Skills:**",
                    ", ".join(
                        item["required_skills"]
                    )
                )

                st.write(
                    "**Preferred Skills:**",
                    ", ".join(
                        item["preferred_skills"]
                    )
                )

                st.write(
                    "**Experience:**",
                    item["experience"]
                )

                st.write(
                    "**Education:**",
                    ", ".join(
                        item["education"]
                    )
                )

                st.write(
                    "**Notice Period:**",
                    item["notice_period"]
                )

                st.write(
                    "**Salary:**",
                    f"{item['salary_min'] or '-'} "
                    f"to "
                    f"{item['salary_max'] or '-'} LPA"
                )

                st.write(
                    "**Location:**",
                    item["location"]
                )

                st.write(
                    "**Regional Preference:**",
                    item["regional_preference"]
                )

                st.write(
                    "**Relocation:**",
                    item["relocation_willingness"]
                )