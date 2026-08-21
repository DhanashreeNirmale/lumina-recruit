import streamlit as st
import pandas as pd

from database.repositories import (
    get_application_by_id,
    get_candidate_by_id,
    get_job_by_id,
    get_assessments_by_application,
    update_application_status,
    assign_assessment
)

from messaging.messaging_service import MessagingService
from scheduling.interview_service import InterviewService
from services.notification_service import NotificationService


def show_candidate_detail_page(application_id: int):

    # ========================================================
    # FETCH APPLICATION / CANDIDATE / JOB DETAILS
    # ========================================================

    app = get_application_by_id(application_id)

    if not app:
        st.error("Application not found.")

        if st.button("Back to Workspace"):
            st.session_state.pop("view_app_detail_id", None)
            st.rerun()

        return

    candidate = get_candidate_by_id(app["candidate_id"])
    job = get_job_by_id(app["job_id"])

    if not candidate:
        st.error("Candidate information not found.")
        return

    if not job:
        st.error("Job information not found.")
        return


    # ========================================================
    # HEADER
    # ========================================================

    st.markdown(
        f"""
        <div style="
            background-color:#1e293b;
            padding:20px;
            border-radius:12px;
            margin-bottom:20px;
            border:1px solid rgba(255,255,255,0.05);
        ">
            <h2 style="margin:0; color:white;">
                👤 Application Detail: {candidate.get('name', 'Unknown Candidate')}
            </h2>

            <p style="margin:5px 0 0 0; color:#94a3b8;">
                Applying for:
                <b>{job.get('title', 'Unknown Position')}</b>
                |
                Status:
                <b>{app.get('status', 'Unknown')}</b>
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )


    # ========================================================
    # BACK BUTTON
    # ========================================================

    if st.button(
        "⬅️ Back to Recruiter Portal",
        type="secondary"
    ):
        st.session_state.pop("view_app_detail_id", None)
        st.rerun()

    st.write("")


    # ========================================================
    # TWO COLUMN LAYOUT
    # ========================================================

    col1, col2 = st.columns([1, 1])


    # ========================================================
    # LEFT COLUMN
    # CANDIDATE PROFILE + PARSED RESUME + ASSESSMENTS
    # ========================================================

    with col1:

        # ====================================================
        # PARSED RESUME
        # ====================================================

        st.subheader("📄 Parsed Resume")

        # ----------------------------------------------------
        # Personal Information
        # ----------------------------------------------------

        st.markdown("### 👤 Personal Information")

        with st.container(border=True):

            personal_col1, personal_col2 = st.columns(2)

            with personal_col1:
                st.write(
                    f"**Name:** "
                    f"{candidate.get('name') or 'Not Available'}"
                )

                st.write(
                    f"**Email:** "
                    f"{candidate.get('email') or 'Not Available'}"
                )

                st.write(
                    f"**Phone:** "
                    f"{candidate.get('phone') or 'Not Available'}"
                )

            with personal_col2:
                st.write(
                    f"**Location:** "
                    f"{candidate.get('location') or 'Not Available'}"
                )

                relocation = candidate.get("relocation")

                if relocation:
                    relocation_text = "Willing"
                else:
                    relocation_text = "Not Willing"

                st.write(
                    f"**Relocation:** {relocation_text}"
                )


        # ----------------------------------------------------
        # Education
        # ----------------------------------------------------

        st.markdown("### 🎓 Education")

        with st.container(border=True):

            st.write(
                f"**Degree:** "
                f"{candidate.get('degree') or 'Not Available'}"
            )

            st.write(
                f"**Branch:** "
                f"{candidate.get('branch') or 'Not Available'}"
            )

            st.write(
                f"**College:** "
                f"{candidate.get('college') or 'Not Available'}"
            )

            graduation_year = candidate.get("graduation_year")

            st.write(
                f"**Graduation Year:** "
                f"{graduation_year if graduation_year else 'Not Available'}"
            )


        # ----------------------------------------------------
        # Skills
        # ----------------------------------------------------

        st.markdown("### 🛠️ Skills")

        skills = candidate.get("skills", [])

        if skills:

            if isinstance(skills, list):

                skill_text = " • ".join(
                    str(skill) for skill in skills
                    if skill
                )

            else:
                skill_text = str(skills)

            st.markdown(
                f"""
                <div style="
                    padding:12px;
                    border-radius:8px;
                    background-color:rgba(255,255,255,0.03);
                    border:1px solid rgba(255,255,255,0.06);
                ">
                    {skill_text}
                </div>
                """,
                unsafe_allow_html=True
            )

        else:
            st.info("No skills found in the parsed resume.")


        # ----------------------------------------------------
        # Experience
        # ----------------------------------------------------

        st.markdown("### 💼 Experience")

        with st.container(border=True):

            experience_years = candidate.get("experience_years")

            if experience_years is not None:
                st.write(
                    f"**Experience:** {experience_years} years"
                )
            else:
                st.write(
                    "**Experience:** Not Available"
                )

            experience = candidate.get("experience")

            if experience:

                if isinstance(experience, list):

                    for exp in experience:
                        st.write(f"• {exp}")

                else:
                    st.write(str(experience))

            else:
                st.write("No detailed experience information available.")


        # ----------------------------------------------------
        # Projects
        # ----------------------------------------------------

        st.markdown("### 🚀 Projects")

        projects = candidate.get("projects", [])

        if projects:

            if isinstance(projects, list):

                for project in projects:

                    if isinstance(project, dict):

                        project_name = (
                            project.get("name")
                            or project.get("title")
                            or "Project"
                        )

                        project_description = (
                            project.get("description")
                            or project.get("details")
                            or ""
                        )

                        st.markdown(
                            f"**🔹 {project_name}**"
                        )

                        if project_description:
                            st.write(project_description)

                    else:
                        st.write(f"• {project}")

            else:
                st.write(str(projects))

        else:
            st.info("No projects found in the parsed resume.")


        # ----------------------------------------------------
        # Certifications
        # ----------------------------------------------------

        st.markdown("### 🏆 Certifications")

        certifications = candidate.get(
            "certifications",
            []
        )

        if certifications:

            if isinstance(certifications, list):

                for certification in certifications:

                    if isinstance(certification, dict):

                        cert_name = (
                            certification.get("name")
                            or certification.get("title")
                            or "Certification"
                        )

                        st.write(f"• {cert_name}")

                    else:
                        st.write(f"• {certification}")

            else:
                st.write(str(certifications))

        else:
            st.info(
                "No certifications found in the parsed resume."
            )


        # ----------------------------------------------------
        # Candidate Preferences
        # ----------------------------------------------------

        st.markdown("### ⚙️ Candidate Preferences")

        with st.container(border=True):

            st.write(
                f"**Notice Period:** "
                f"{candidate.get('notice_period') or 'Not Available'} days"
            )

            st.write(
                f"**Expected Salary:** "
                f"{candidate.get('expected_salary') or 'Not Available'} LPA"
            )

            preferred_roles = candidate.get(
                "preferred_roles",
                []
            )

            if preferred_roles:

                if isinstance(preferred_roles, list):
                    roles_text = ", ".join(
                        str(role)
                        for role in preferred_roles
                    )
                else:
                    roles_text = str(preferred_roles)

            else:
                roles_text = "Not Available"

            st.write(
                f"**Preferred Roles:** {roles_text}"
            )


            preferred_locations = candidate.get(
                "preferred_locations",
                []
            )

            if preferred_locations:

                if isinstance(preferred_locations, list):
                    locations_text = ", ".join(
                        str(location)
                        for location in preferred_locations
                    )
                else:
                    locations_text = str(preferred_locations)

            else:
                locations_text = "Not Available"

            st.write(
                f"**Preferred Locations:** {locations_text}"
            )

            relocation = candidate.get("relocation")

            st.write(
                f"**Relocation:** "
                f"{'Willing' if relocation else 'Not Willing'}"
            )


        # ----------------------------------------------------
        # RAW RESUME TEXT
        # ----------------------------------------------------

        with st.expander("📄 View Raw Extracted Resume Text"):

            resume_text = candidate.get(
                "resume_text",
                ""
            )

            if resume_text:

                st.code(
                    resume_text,
                    language="text"
                )

            else:

                st.info(
                    "No extracted resume text available."
                )


        st.write("---")


        # ====================================================
        # ASSESSMENTS SECTION
        # ====================================================

        st.subheader("⚙️ Assessments Assigned")

        asms = get_assessments_by_application(
            application_id
        )

        if not asms:

            st.info(
                "No assessments assigned yet."
            )

        else:

            for asm in asms:

                score_str = (
                    f"{asm['score']}%"
                    if asm["score"] is not None
                    else "Pending"
                )

                st.markdown(
                    f"""
                    <div style="
                        background-color:rgba(255,255,255,0.02);
                        padding:10px 15px;
                        border-radius:8px;
                        border:1px solid rgba(255,255,255,0.05);
                        margin-bottom:10px;
                    ">
                        <b>{asm['type']} Test:</b>
                        {score_str}
                        ({asm['status']})
                    </div>
                    """,
                    unsafe_allow_html=True
                )


                # --------------------------------------------
                # Coding Test Details
                # --------------------------------------------

                if (
                    asm["status"] == "Completed"
                    and asm["type"] == "Technical"
                ):

                    try:

                        import json

                        details = json.loads(
                            asm["details"]
                        )

                        with st.expander(
                            "🔍 View Coding Test Cases"
                        ):

                            for q_id, q_res in details.items():

                                st.write(
                                    f"**Question:** "
                                    f"{q_res.get('question')}"
                                )

                                st.write(
                                    f"Score: "
                                    f"{q_res.get('score')} points"
                                )

                                if "results" in q_res:

                                    for t_idx, tr in enumerate(
                                        q_res["results"]
                                    ):

                                        status_emoji = (
                                            "✅"
                                            if tr.get("passed")
                                            else "❌"
                                        )

                                        st.write(
                                            f" - Testcase "
                                            f"{t_idx + 1}: "
                                            f"{status_emoji} "
                                            f"(Expected: "
                                            f"`{tr.get('expected')}`, "
                                            f"Got: "
                                            f"`{tr.get('stdout')}`)"
                                        )

                    except Exception:
                        pass


        st.write("")

        st.write("**Assign New Assessment:**")

        col_c1, col_c2 = st.columns(2)


        # ----------------------------------------------------
        # Aptitude Test
        # ----------------------------------------------------

        with col_c1:

            if st.button(
                "⚡ Assign Aptitude Test",
                key="assign_apt",
                use_container_width=True
            ):

                assign_assessment(
                    application_id,
                    "Aptitude"
                )

                ns = NotificationService()

                ns.send_email_notification(
                    candidate["email"],
                    "Aptitude Assessment Assigned",
                    "Please log in to take your test."
                )

                st.success(
                    "Aptitude test assigned!"
                )

                st.rerun()


        # ----------------------------------------------------
        # Technical Test
        # ----------------------------------------------------

        with col_c2:

            if st.button(
                "💻 Assign Technical Test",
                key="assign_tech",
                use_container_width=True
            ):

                assign_assessment(
                    application_id,
                    "Technical"
                )

                ns = NotificationService()

                ns.send_email_notification(
                    candidate["email"],
                    "Coding Assessment Assigned",
                    "Please log in to complete your technical sandbox challenge."
                )

                st.success(
                    "Technical test assigned!"
                )

                st.rerun()


    # ========================================================
    # RIGHT COLUMN
    # PIPELINE + AI REPORT + INTERVIEW
    # ========================================================

    with col2:

        # ====================================================
        # APPLICATION PIPELINE
        # ====================================================

        st.subheader(
            "🎯 Application Pipeline Movement"
        )

        statuses = [
            "Applied",
            "Screening",
            "Shortlisted",
            "Assessment",
            "Assessment Completed",
            "Interview",
            "Selected",
            "Rejected"
        ]

        try:

            cur_idx = statuses.index(
                app["status"]
            )

        except Exception:

            cur_idx = 0


        new_status = st.selectbox(
            "Pipeline Status",
            statuses,
            index=cur_idx
        )

        if new_status != app["status"]:

            update_application_status(
                application_id,
                new_status
            )

            st.success(
                f"Status updated to {new_status}"
            )

            st.rerun()


        st.write("---")


        # ====================================================
        # AI MATCH BREAKDOWN
        # ====================================================

        st.subheader(
            "🤖 AI Compatibility Report"
        )

        match_score = app.get(
            "match_score"
        )

        if match_score is not None:

            st.metric(
                "Compatibility Score",
                f"{match_score}%"
            )

        else:

            st.metric(
                "Compatibility Score",
                "N/A"
            )


        explanation = app.get(
            "matching_explanation",
            "No AI analysis report generated yet."
        )

        st.markdown(
            explanation,
            unsafe_allow_html=True
        )


        st.write("---")


        # ====================================================
        # SCHEDULE INTERVIEW
        # ====================================================

        st.subheader(
            "📅 Schedule Interview"
        )

        with st.form("interview_form"):

            int_date = st.date_input(
                "Date"
            )

            int_time = st.time_input(
                "Time"
            )

            int_mode = st.selectbox(
                "Interview Mode",
                [
                    "Online",
                    "In-person",
                    "Phone"
                ]
            )

            int_link = st.text_input(
                "Meeting Link / Venue Address",
                value="https://meet.google.com/abc-defg-hij"
            )

            int_notes = st.text_area(
                "Interview Instructions/Notes"
            )


            if st.form_submit_button(
                "Book Interview"
            ):

                service = InterviewService()

                service.book_interview(
                    candidate_id=candidate["id"],
                    job_id=job["id"],
                    date_str=str(int_date),
                    time_str=str(int_time),
                    mode=int_mode,
                    venue_link=int_link,
                    notes=int_notes
                )


                # --------------------------------------------
                # Send email notification
                # --------------------------------------------

                ns = NotificationService()

                ns.send_email_notification(
                    candidate["email"],
                    "Interview Scheduled",
                    f"""
Hi {candidate['name']},

We have scheduled your interview on
{int_date} at {int_time}.

Join link:
{int_link}

Regards,
Lumina Recruit
"""
                )


                # --------------------------------------------
                # Update status
                # --------------------------------------------

                update_application_status(
                    application_id,
                    "Interview"
                )


                st.success(
                    "Interview booked successfully!"
                )

                st.rerun()


    # ========================================================
    # BOTTOM SECTION
    # CHAT WITH CANDIDATE
    # ========================================================

    st.write("---")

    st.subheader(
        "💬 Chat with Candidate"
    )

    ms_service = MessagingService()

    history = ms_service.fetch_chat_history(
        application_id
    )


    chat_box = st.container(
        height=280
    )

    with chat_box:

        if not history:

            st.write(
                "*No chat history yet. "
                "Send a message below to coordinate.*"
            )

        else:

            for msg in history:

                align = (
                    "right"
                    if msg["sender_role"] == "recruiter"
                    else "left"
                )

                color = (
                    "#6366f1"
                    if msg["sender_role"] == "recruiter"
                    else "#1e293b"
                )


                st.markdown(
                    f"""
                    <div style="
                        text-align:{align};
                        margin-bottom:10px;
                    ">

                        <div style="
                            display:inline-block;
                            padding:10px 14px;
                            border-radius:12px;
                            background-color:{color};
                            color:white;
                            max-width:70%;
                            text-align:left;
                        ">

                            <b>{msg['sender_name']}</b>
                            ({msg['sender_role'].capitalize()}):
                            <br>

                            {msg['message']}

                        </div>

                    </div>
                    """,
                    unsafe_allow_html=True
                )


    # ========================================================
    # SEND MESSAGE
    # ========================================================

    new_msg = st.text_input(
        "Type recruiter message...",
        key="recruiter_chat_input"
    )


    if st.button(
        "Send Message",
        key="recruiter_send_btn"
    ):

        if new_msg.strip():

            ms_service.post_message(
                application_id,
                st.session_state.user["id"],
                "recruiter",
                new_msg
            )

            st.rerun()