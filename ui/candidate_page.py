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


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def _decode(value):
    """
    Convert JSON string fields from the database into Python lists.
    """

    try:
        parsed = json.loads(value or "[]")

        if isinstance(parsed, list):
            return parsed

        return []

    except (TypeError, json.JSONDecodeError):
        return []


def _display_value(value):
    """
    Convert different data types into a readable string
    for the Streamlit UI.
    """

    if value is None:
        return "Not provided"

    if isinstance(value, list):

        if not value:
            return "Not provided"

        return ", ".join(
            str(item)
            for item in value
        )

    if isinstance(value, dict):

        return json.dumps(
            value,
            indent=2,
            ensure_ascii=False,
        )

    text = str(value).strip()

    if not text:
        return "Not provided"

    return text


def display_parsed_resume(data):
    """
    Display the information extracted from the resume.
    """

    st.markdown("---")

    st.subheader("📄 Parsed Resume Information")

    # ========================================================
    # BASIC INFORMATION
    # ========================================================

    st.markdown("### 👤 Personal Information")

    col1, col2 = st.columns(2)

    with col1:

        st.write(
            f"**Name:** {_display_value(data.get('name'))}"
        )

        st.write(
            f"**Email:** {_display_value(data.get('email'))}"
        )

        st.write(
            f"**Phone:** {_display_value(data.get('phone'))}"
        )

    with col2:

        st.write(
            f"**Location:** {_display_value(data.get('location'))}"
        )

        st.write(
            f"**Total Experience:** "
            f"{_display_value(data.get('experience'))}"
        )

        st.write(
            f"**Notice Period:** "
            f"{_display_value(data.get('notice_period'))}"
        )

    # ========================================================
    # SKILLS
    # ========================================================

    st.markdown("### 🛠️ Skills")

    skills = data.get("skills", [])

    if isinstance(skills, str):

        try:
            skills = json.loads(skills)
        except json.JSONDecodeError:

            skills = [
                skill.strip()
                for skill in skills.split(",")
                if skill.strip()
            ]

    if skills:

        st.write(
            ", ".join(
                str(skill)
                for skill in skills
            )
        )

    else:

        st.write("Not provided")

    # ========================================================
    # EDUCATION
    # ========================================================

    st.markdown("### 🎓 Education")

    education = data.get(
        "education",
        []
    )

    if isinstance(education, list):

        if education:

            for item in education:

                if isinstance(item, dict):

                    st.write(
                        f"- {_display_value(item)}"
                    )

                else:

                    st.write(
                        f"- {item}"
                    )

        else:

            st.write("Not provided")

    elif education:

        st.write(
            _display_value(education)
        )

    else:

        st.write("Not provided")

    # ========================================================
    # EXPERIENCE DETAILS
    # ========================================================

    st.markdown("### 💼 Experience Details")

    experience_details = data.get(
        "experience_details",
        data.get(
            "work_experience",
            data.get(
                "experience_summary",
                None
            )
        )
    )

    if isinstance(
        experience_details,
        list
    ):

        if experience_details:

            for item in experience_details:

                if isinstance(item, dict):

                    st.write(
                        f"- {_display_value(item)}"
                    )

                else:

                    st.write(
                        f"- {item}"
                    )

        else:

            st.write("Not provided")

    elif experience_details:

        st.write(
            _display_value(
                experience_details
            )
        )

    else:

        st.write("Not provided")

    # ========================================================
    # PROJECTS
    # ========================================================

    st.markdown("### 🚀 Projects")

    projects = data.get(
        "projects",
        []
    )

    if isinstance(projects, list):

        if projects:

            for project in projects:

                if isinstance(project, dict):

                    st.write(
                        f"- {_display_value(project)}"
                    )

                else:

                    st.write(
                        f"- {project}"
                    )

        else:

            st.write("Not provided")

    elif projects:

        st.write(
            _display_value(projects)
        )

    else:

        st.write("Not provided")

    # ========================================================
    # CERTIFICATIONS
    # ========================================================

    st.markdown("### 🏆 Certifications")

    certifications = data.get(
        "certifications",
        []
    )

    if isinstance(
        certifications,
        list
    ):

        if certifications:

            for certification in certifications:

                st.write(
                    f"- {certification}"
                )

        else:

            st.write("Not provided")

    elif certifications:

        st.write(
            _display_value(
                certifications
            )
        )

    else:

        st.write("Not provided")

    # ========================================================
    # SALARY
    # ========================================================

    st.markdown("### 💰 Salary Information")

    col1, col2 = st.columns(2)

    with col1:

        st.write(
            f"**Current Salary:** "
            f"{_display_value(data.get('current_salary'))}"
        )

    with col2:

        st.write(
            f"**Expected Salary:** "
            f"{_display_value(data.get('expected_salary'))}"
        )

    # ========================================================
    # RESUME SUMMARY
    # ========================================================

    st.markdown("### 📝 Resume Summary")

    summary = data.get(
        "summary",
        data.get(
            "profile_summary",
            data.get(
                "professional_summary",
                None
            )
        )
    )

    if summary:

        st.info(
            _display_value(summary)
        )

    else:

        st.write("Not provided")

    # ========================================================
    # OTHER PARSED INFORMATION
    # ========================================================

    known_fields = {
        "name",
        "email",
        "phone",
        "location",
        "experience",
        "notice_period",
        "skills",
        "education",
        "experience_details",
        "work_experience",
        "experience_summary",
        "projects",
        "certifications",
        "current_salary",
        "expected_salary",
        "summary",
        "profile_summary",
        "professional_summary",
        "resume_filename",
        "resume_text",
    }

    additional_fields = {
        key: value
        for key, value in data.items()
        if key not in known_fields
    }

    if additional_fields:

        st.markdown(
            "### 🔎 Additional Parsed Information"
        )

        for key, value in additional_fields.items():

            readable_key = (
                key.replace("_", " ")
                .title()
            )

            st.write(
                f"**{readable_key}:** "
                f"{_display_value(value)}"
            )


# ============================================================
# CANDIDATE PAGE
# ============================================================

def show_candidate_page():

    st.title("👥 Candidates")

    upload_tab, pipeline_tab, interview_tab = st.tabs(
        [
            "Resume Upload",
            "Pipeline",
            "Interviews",
        ]
    )

    # ========================================================
    # TAB 1 — RESUME UPLOAD
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
                "txt",
            ],
            accept_multiple_files=True,
            key="candidate_resume_uploader",
        )

        if st.button(
            "🤖 Parse & Add Resumes",
            type="primary",
            key="candidate_parse_resumes_button",
        ):

            if not files:

                st.error(
                    "Upload at least one resume."
                )

            else:

                success_count = 0

                progress = st.progress(0)

                total_files = len(files)

                for index, uploaded_file in enumerate(files):

                    try:

                        # ====================================
                        # EXTRACT RESUME TEXT
                        # ====================================

                        text = extract_text(
                            uploaded_file
                        )

                        if not text:

                            st.warning(
                                f"{uploaded_file.name}: "
                                "No readable text found."
                            )

                            continue

                        # ====================================
                        # AI RESUME ANALYSIS
                        # ====================================

                        parsed_data = ResumeAgent().analyze(
                            text
                        )

                        # ====================================
                        # VALIDATE RESULT
                        # ====================================

                        if not isinstance(
                            parsed_data,
                            dict
                        ):

                            raise ValueError(
                                "ResumeAgent did not return "
                                "a valid parsed dictionary."
                            )

                        # ====================================
                        # ADD ORIGINAL RESUME INFORMATION
                        # ====================================

                        parsed_data[
                            "resume_filename"
                        ] = uploaded_file.name

                        parsed_data[
                            "resume_text"
                        ] = text

                        # ====================================
                        # SAVE CANDIDATE
                        # ====================================

                        candidate_id = create_candidate(
                            parsed_data
                        )

                        success_count += 1

                        # ====================================
                        # SUCCESS MESSAGE
                        # ====================================

                        st.success(
                            f"✅ {uploaded_file.name} "
                            f"parsed and added successfully "
                            f"as Candidate #{candidate_id}"
                        )

                        # ====================================
                        # SHOW PARSED INFORMATION
                        # ====================================

                        display_parsed_resume(
                            parsed_data
                        )

                    except Exception as exc:

                        st.error(
                            f"❌ {uploaded_file.name}: "
                            f"{exc}"
                        )

                    finally:

                        progress.progress(
                            (index + 1) / total_files
                        )

                # ============================================
                # FINAL MESSAGE
                # ============================================

                st.success(
                    f"🎉 Successfully added "
                    f"{success_count} resume(s)."
                )

    # ========================================================
    # TAB 2 — CANDIDATE PIPELINE
    # ========================================================

    with pipeline_tab:

        candidates = get_candidates()

        jobs = get_jobs()

        if not candidates:

            st.info(
                "No candidates yet."
            )

        else:

            # =================================================
            # JOB MATCHING
            # =================================================

            if jobs:

                st.subheader(
                    "Candidate Matching"
                )

                job_options = {
                    f"#{j['id']} — {j['title']}": j
                    for j in jobs
                }

                selected_job_label = st.selectbox(
                    "Select job for matching",
                    list(
                        job_options.keys()
                    ),
                    key="candidate_matching_job_selector",
                )

                selected_job = job_options[
                    selected_job_label
                ]

                if st.button(
                    "⚡ Calculate Candidate Scores",
                    key="candidate_calculate_scores_button",
                ):

                    updated_count = 0

                    for candidate in candidates:

                        candidate_for_score = dict(
                            candidate
                        )

                        candidate_for_score[
                            "skills"
                        ] = _decode(
                            candidate.get(
                                "skills",
                                "[]"
                            )
                        )

                        score_result = score_candidate(
                            candidate_for_score,
                            selected_job,
                        )

                        if isinstance(
                            score_result,
                            dict
                        ):

                            score = float(
                                score_result.get(
                                    "score",
                                    0
                                )
                            )

                        else:

                            score = float(
                                score_result
                            )

                        if score >= 70:

                            status = "Shortlisted"

                        else:

                            status = "Screening"

                        update_candidate_score(
                            candidate["id"],
                            score,
                            status,
                        )

                        updated_count += 1

                    st.success(
                        f"Scores updated for "
                        f"{updated_count} candidate(s)."
                    )

            # =================================================
            # CANDIDATE TABLE
            # =================================================

            st.subheader(
                "Candidate Pipeline"
            )

            candidates = get_candidates()

            if candidates:

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
                    column
                    for column in display_cols
                    if column in df.columns
                ]

                if available_cols:

                    st.dataframe(
                        df[available_cols],
                        use_container_width=True,
                        hide_index=True,
                    )

            # =================================================
            # CHANGE CANDIDATE STATUS
            # =================================================

            st.subheader(
                "Update Candidate Status"
            )

            candidate_labels = {
                f"#{c['id']} — {c['name']}": c["id"]
                for c in candidates
            }

            selected_candidate_for_status = (
                st.selectbox(
                    "Candidate",
                    list(
                        candidate_labels.keys()
                    ),
                    key="candidate_status_candidate_selector",
                )
            )

            new_status = st.selectbox(
                "New status",
                [
                    "New",
                    "Screening",
                    "Shortlisted",
                    "Interview",
                    "Rejected",
                    "Hired",
                ],
                key="candidate_status_selector",
            )

            if st.button(
                "Update Status",
                key="candidate_update_status_button",
            ):

                update_candidate_status(
                    candidate_labels[
                        selected_candidate_for_status
                    ],
                    new_status,
                )

                st.success(
                    "Candidate status updated."
                )

    # ========================================================
    # TAB 3 — INTERVIEWS
    # ========================================================

    with interview_tab:

        candidates = get_candidates()

        jobs = get_jobs()

        if not candidates or not jobs:

            st.info(
                "Create at least one job and "
                "one candidate first."
            )

        else:

            st.subheader(
                "Schedule Interview"
            )

            # =================================================
            # CANDIDATE SELECTOR
            # =================================================

            candidate_map = {
                f"#{c['id']} — {c['name']}": c["id"]
                for c in candidates
            }

            selected_candidate = st.selectbox(
                "Candidate",
                list(
                    candidate_map.keys()
                ),
                key="interview_candidate_selector",
            )

            # =================================================
            # JOB SELECTOR
            # =================================================

            job_map = {
                f"#{j['id']} — {j['title']}": j["id"]
                for j in jobs
            }

            selected_interview_job = st.selectbox(
                "Job",
                list(
                    job_map.keys()
                ),
                key="interview_job_selector",
            )

            # =================================================
            # DATE
            # =================================================

            interview_date = st.date_input(
                "Interview date",
                value=date.today(),
                key="interview_date_selector",
            )

            # =================================================
            # TIME
            # =================================================

            interview_time = st.time_input(
                "Interview time",
                value=time(10, 0),
                key="interview_time_selector",
            )

            # =================================================
            # INTERVIEW MODE
            # =================================================

            mode = st.selectbox(
                "Mode",
                [
                    "Online",
                    "In-person",
                    "Phone",
                ],
                key="interview_mode_selector",
            )

            # =================================================
            # NOTES
            # =================================================

            notes = st.text_area(
                "Notes",
                key="interview_notes",
            )

            # =================================================
            # SCHEDULE
            # =================================================

            if st.button(
                "📅 Schedule Interview",
                key="schedule_interview_button",
            ):

                try:

                    schedule_interview(
                        candidate_map[
                            selected_candidate
                        ],
                        job_map[
                            selected_interview_job
                        ],
                        str(interview_date),
                        str(interview_time),
                        mode,
                        notes,
                    )

                    st.success(
                        "Interview scheduled successfully."
                    )

                except Exception as exc:

                    st.error(
                        f"Could not schedule interview: {exc}"
                    )

            # =================================================
            # COMMUNICATION TEMPLATE
            # =================================================

            st.subheader(
                "Communication Template"
            )

            st.code(
                "Subject: Interview Invitation\n\n"
                "Dear Candidate,\n\n"
                "Thank you for your application. "
                "We would like to invite you for an "
                "interview for the selected role.\n\n"
                "Regards,\n"
                "Lumina Recruit"
            )

            # =================================================
            # INTERVIEW LIST
            # =================================================

            interviews = get_interviews()

            if interviews:

                st.subheader(
                    "Scheduled Interviews"
                )

                st.dataframe(
                    pd.DataFrame(
                        interviews
                    ),
                    use_container_width=True,
                    hide_index=True,
                )

            else:

                st.info(
                    "No interviews scheduled yet."
                )