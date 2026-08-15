import json
from datetime import date, time

import pandas as pd
import streamlit as st

from agents.resume_agent import ResumeAgent

from database.models import (
    create_candidate,
    get_candidates,
    get_jobs,
    update_candidate_status,
    update_candidate_score,
    schedule_interview,
    get_interviews,
)

from matching.matcher import score_candidate

from resume_parser.parser import extract_text


def _decode(value):

    if isinstance(
        value,
        list
    ):

        return value

    try:

        parsed = json.loads(
            value or "[]"
        )

        if isinstance(
            parsed,
            list
        ):

            return parsed

    except (
        TypeError,
        json.JSONDecodeError
    ):

        pass

    return []


def show_candidate_page():

    st.title("👥 Candidates")

    st.caption(
        "Resume screening • Candidate pipeline • Interview scheduling"
    )

    upload_tab, pipeline_tab, interview_tab = st.tabs(
        [
            "📄 Resume Upload",
            "📊 Pipeline",
            "📅 Interviews",
        ]
    )

    # ========================================================
    # RESUME UPLOAD
    # ========================================================

    with upload_tab:

        st.subheader(
            "Batch Resume Processing"
        )

        files = st.file_uploader(
            "Upload resumes",
            type=[
                "pdf",
                "docx",
                "txt"
            ],
            accept_multiple_files=True,
        )

        if st.button(
            "🤖 Parse & Add Resumes",
            type="primary",
        ):

            if not files:

                st.error(
                    "Upload at least one resume."
                )

            else:

                success_count = 0

                progress = st.progress(
                    0
                )

                for index, uploaded_file in enumerate(
                    files
                ):

                    try:

                        # ------------------------------------
                        # Extract text
                        # ------------------------------------

                        text = extract_text(
                            uploaded_file
                        )

                        if not text:

                            st.warning(
                                f"{uploaded_file.name}: "
                                "no text found."
                            )

                            continue

                        # ------------------------------------
                        # AI analysis
                        # ------------------------------------

                        data = ResumeAgent().analyze(
                            text
                        )

                        data[
                            "resume_filename"
                        ] = uploaded_file.name

                        data[
                            "resume_text"
                        ] = text

                        # ------------------------------------
                        # Save candidate
                        # ------------------------------------

                        candidate_id = create_candidate(
                            data
                        )

                        success_count += 1

                        st.success(
                            f"{uploaded_file.name} "
                            f"→ Candidate #{candidate_id}"
                        )

                    except Exception as exc:

                        st.error(
                            f"{uploaded_file.name}: {exc}"
                        )

                    progress.progress(
                        (index + 1)
                        / len(files)
                    )

                st.info(
                    f"Successfully added "
                    f"{success_count} resume(s)."
                )

    # ========================================================
    # PIPELINE
    # ========================================================

    with pipeline_tab:

        candidates = get_candidates()

        jobs = get_jobs()

        if not candidates:

            st.info(
                "No candidates yet."
            )

        else:

            if jobs:

                job_options = {
                    f"#{job['id']} — {job['title']}": job
                    for job in jobs
                }

                selected_label = st.selectbox(
                    "Select job for matching",
                    list(
                        job_options.keys()
                    ),
                )

                selected_job = job_options[
                    selected_label
                ]

                if st.button(
                    "⚡ Calculate Candidate Scores",
                    type="primary",
                ):

                    for candidate in candidates:

                        candidate_for_score = dict(
                            candidate
                        )

                        candidate_for_score[
                            "skills"
                        ] = _decode(
                            candidate[
                                "skills"
                            ]
                        )

                        candidate_for_score[
                            "education"
                        ] = _decode(
                            candidate[
                                "education"
                            ]
                        )

                        score = score_candidate(
                            candidate_for_score,
                            selected_job
                        )

                        if score >= 75:

                            status = "Shortlisted"

                        elif score >= 50:

                            status = "Screening"

                        else:

                            status = "New"

                        update_candidate_score(
                            candidate["id"],
                            score,
                            status
                        )

                    st.success(
                        "Candidate scores updated."
                    )

                    st.rerun()

            # ------------------------------------------------
            # DISPLAY
            # ------------------------------------------------

            candidates = get_candidates()

            df = pd.DataFrame(
                candidates
            )

            display_cols = [
                "id",
                "name",
                "email",
                "score",
                "status",
                "notice_period",
                "expected_salary",
                "location",
            ]

            available_cols = [
                col
                for col in display_cols
                if col in df.columns
            ]

            st.dataframe(
                df[available_cols],
                use_container_width=True,
                hide_index=True,
            )

            # ------------------------------------------------
            # STATUS UPDATE
            # ------------------------------------------------

            candidate_labels = {
                f"#{candidate['id']} — {candidate['name']}":
                candidate["id"]

                for candidate in candidates
            }

            selected_candidate = st.selectbox(
                "Candidate",
                list(
                    candidate_labels.keys()
                ),
            )

            status = st.selectbox(
                "New Status",
                [
                    "New",
                    "Screening",
                    "Shortlisted",
                    "Interview",
                    "Rejected",
                    "Hired",
                ],
            )

            if st.button(
                "Update Status"
            ):

                update_candidate_status(
                    candidate_labels[
                        selected_candidate
                    ],
                    status
                )

                st.success(
                    "Candidate status updated."
                )

    # ========================================================
    # INTERVIEWS
    # ========================================================

    with interview_tab:

        candidates = get_candidates()

        jobs = get_jobs()

        if not candidates or not jobs:

            st.info(
                "Create at least one job "
                "and one candidate first."
            )

        else:

            st.subheader(
                "📅 Schedule Interview"
            )

            candidate_map = {
                f"#{candidate['id']} — {candidate['name']}":
                candidate["id"]

                for candidate in candidates
            }

            job_map = {
                f"#{job['id']} — {job['title']}":
                job["id"]

                for job in jobs
            }

            selected_candidate = st.selectbox(
                "Candidate",
                list(
                    candidate_map.keys()
                ),
            )

            selected_job = st.selectbox(
                "Job",
                list(
                    job_map.keys()
                ),
            )

            interview_date = st.date_input(
                "Interview Date",
                value=date.today()
            )

            interview_time = st.time_input(
                "Interview Time",
                value=time(
                    10,
                    0
                )
            )

            mode = st.selectbox(
                "Mode",
                [
                    "Online",
                    "In-person",
                    "Phone",
                ],
            )

            notes = st.text_area(
                "Notes"
            )

            if st.button(
                "📅 Schedule Interview",
                type="primary",
            ):

                schedule_interview(
                    candidate_map[
                        selected_candidate
                    ],

                    job_map[
                        selected_job
                    ],

                    str(
                        interview_date
                    ),

                    str(
                        interview_time
                    ),

                    mode,

                    notes,
                )

                st.success(
                    "Interview scheduled successfully."
                )

            # ------------------------------------------------
            # COMMUNICATION TEMPLATE
            # ------------------------------------------------

            st.subheader(
                "✉️ Communication Template"
            )

            st.code(
                """Subject: Interview Invitation

Dear Candidate,

Thank you for your application.

We would like to invite you for an interview
for the selected role.

Interview details:

Date: [Interview Date]
Time: [Interview Time]
Mode: [Online/In-person/Phone]

Please confirm your availability.

Regards,
Lumina Recruit
"""
            )

            # ------------------------------------------------
            # INTERVIEW LIST
            # ------------------------------------------------

            interviews = get_interviews()

            if interviews:

                st.subheader(
                    "Scheduled Interviews"
                )

                df = pd.DataFrame(
                    interviews
                )

                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True,
                )