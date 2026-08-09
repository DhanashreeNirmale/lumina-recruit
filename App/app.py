import streamlit as st

from resume_parser import parse_resume, extract_text_from_file

from scoring_engine import (
    extract_job_skills,
    calculate_score,
    get_score_interpretation
)

from database import (
    init_database,
    save_screening_result,
    get_all_screenings,
    get_statistics,
    delete_screening,
    schedule_interview,
    get_all_interviews,
    update_interview_status,
    delete_interview
)

init_database()

from App.communication.email_generator import (
    generate_shortlist_email,
    generate_rejection_email,
)

st.set_page_config(
    page_title="Resume Screening Chatbot",
    layout="wide"
)

st.title("Resume Screening Chatbot")

st.write(
    "Upload a resume and compare it with the Job Description."
)

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    [
        "Resume Screening",
        "History",
        "Statistics",
        "AI Communication",
        "Schedule Interview"
    ]
)

with tab1:

    left, right = st.columns(2)

    resume_data = None
    resume_text = None
    job_skills = []

    with left:

        st.subheader("Upload Resume")

        uploaded_file = st.file_uploader(
            "Choose Resume",
            type=["pdf","docx","txt"]
        )

        if uploaded_file is not None:

            with st.spinner("Parsing Resume..."):

                resume_data = parse_resume(uploaded_file)

                st.session_state.resume_data = resume_data
                uploaded_file.seek(0)
                resume_text = extract_text_from_file(uploaded_file)
                st.session_state.resume_text = resume_text
            st.success("Resume Parsed Successfully")
            

            st.markdown("### Candidate Information")

            st.write(f" Name: {resume_data['name'] or 'Not Found'}")

            st.write(f"Email: {resume_data['email'] or 'Not Found'}")

            st.write(f" Phone: {resume_data['phone'] or 'Not Found'}")

            education = ", ".join(resume_data["education"]) if resume_data["education"] else "Not Found"

            st.write(f"Education: {education}")

            st.write(f"College: {resume_data['college'] or 'Not Found'}")

            # st.write(f"Experience: {resume_data['experience']}")

            if resume_data["skills"]:

                st.write("### 🛠 Skills")

                st.success(", ".join(resume_data["skills"]))

            else:

                st.warning("No Skills Found")

            if resume_data["projects"]:

                st.write("###Projects")

                for project in resume_data["projects"]:

                    st.write(f"• {project}")

            with st.expander("View Resume Text"):

                st.text(resume_text)

    with right:

        st.subheader("Job Description")

        job_description = st.text_area(
            "Paste Job Description",
            height=350
        )

        if job_description:

            job_skills = extract_job_skills(job_description)

            if job_skills:

                st.success(
                    f"{len(job_skills)} Skills Found"
                )

                st.write("### Required Skills")

                for skill in job_skills:

                    st.write(f"• {skill}")

            else:
                st.warning("No recognized skills found in job description")
            
            # Store in session state (IMPORTANT!)
            st.session_state.job_description = job_description
            st.session_state.job_skills = job_skills
        else:
            st.info("Click to match the skills")
    
    # ============================================
    # SCORING SECTION
    # ============================================
    st.divider()
    
    # Get data from session state
    resume_data = st.session_state.get('resume_data')
    job_description = st.session_state.get('job_description')
    job_skills = st.session_state.get('job_skills', [])
    
    if resume_data and job_description and job_skills:
        if st.button("Calculate Match Score", use_container_width=True):
            # Calculate score
            score_result = calculate_score(resume_data['skills'], job_skills)
            
            # SAVE TO SESSION STATE (CRITICAL!)
            st.session_state.score_result = score_result
            
            # Display score
            col1, col2, col3 = st.columns([1, 1, 1])
            
            with col1:
                score_interpretation, _ = get_score_interpretation(score_result['score'])
                st.metric(
                    "Match Score",
                    f"{score_result['score']}%",
                    delta=score_interpretation
                )
            
            with col2:
                st.metric(
                    "Skills Matched",
                    f"{score_result['total_matched']}/{score_result['total_required']}"
                )
            
            with col3:
                st.metric(
                    "Missing Skills",
                    len(score_result['missing_skills'])
                )
            
            # Display matched/missing skills
            st.subheader("Detailed Analysis")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.success("Matched Skills")
                if score_result['matched_skills']:
                    for skill in score_result['matched_skills']:
                        st.write(f"  • {skill}")
                else:
                    st.write("None")
            
            with col2:
                st.error("Missing Skills")
                if score_result['missing_skills']:
                    for skill in score_result['missing_skills']:
                        st.write(f"  • {skill}")
                else:
                    st.write("All skills present!")
            
            with col3:
                st.info("Extra Skills")
                if score_result['extra_skills']:
                    for skill in score_result['extra_skills'][:5]:
                        st.write(f"  • {skill}")
                    if len(score_result['extra_skills']) > 5:
                        st.write(f"  • +{len(score_result['extra_skills']) - 5} more...")
                else:
                    st.write("None")
        
        # SAVE BUTTON (Now works because score_result is in session_state)
        st.divider()
        
        if st.session_state.get('score_result'):
            if st.button("Save Screening Result", use_container_width=True):
                try:
                    candidate_name = resume_data.get("name", "Unknown")
                    
                    save_screening_result(
                        candidate_name=candidate_name,
                        email=resume_data['email'],
                        phone=resume_data['phone'],
                        resume_text=st.session_state.resume_text,
                        job_description=st.session_state.job_description,
                        score_data=st.session_state.score_result
                    )
                    
                    st.success("Result saved to database!")
                    st.balloons()  # Celebration animation!
                except Exception as e:
                    st.error(f"Error saving to database: {str(e)}")
    
    elif resume_data or job_description:
        st.warning("Please provide both resume and job description to calculate score")


with tab2:

    st.subheader("Screening History")

    screenings = get_all_screenings()

    if screenings:
        st.info(f"Total screenings: {len(screenings)}")
        
        for screening in screenings:

            with st.expander(
                f"{screening['candidate_name']}  |  Score: {screening['score']}%"
            ):

                col1, col2 = st.columns(2)

                with col1:

                    st.write(f"**Email:** {screening['email'] or 'N/A'}")

                    st.write(f"**Phone:** {screening['phone'] or 'N/A'}")

                    st.write(f"**Date:** {screening['screening_date']}")

                with col2:

                    st.write(f"**Match Score:** {screening['score']}%")

                    st.write(
                        f"**Matched Skills:** {screening['total_matched']} / {screening['total_required']}"
                    )

                st.write("### Matched Skills")

                if screening["matched_skills"]:

                    st.success(", ".join(screening["matched_skills"]))

                else:

                    st.write("None")

                st.write("### Missing Skills")

                if screening["missing_skills"]:

                    st.error(", ".join(screening["missing_skills"]))

                else:

                    st.write("None")

                with st.expander("View Resume Text"):

                    st.text(screening["resume_text"])

                if st.button(
                    "Delete Record",
                    key=f"delete_{screening['id']}"
                ):


                    delete_screening(screening["id"])

                    st.rerun()

    else:

        st.info("No Screening History Found.")


with tab3:

    st.subheader("Statistics")

    stats = get_statistics()

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Total Screenings",
            stats["total_screenings"]
        )

    with col2:

        st.metric(
            "Average Score",
            f"{stats['average_score']}%"
        )

    with col3:
        st.metric("High Performers (70%+)", stats['high_performers'])
    
    if stats['total_screenings'] > 0:
        st.success("You have screening data. Great job!")
    else:

        st.info("No data available yet.")
        
with tab4:
    st.subheader("AI Candidate Communication")

    screenings = get_all_screenings()

    if screenings:

        candidate_options = [
            f"{s['candidate_name']} ({s['score']}%)"
            for s in screenings
        ]

        selected_idx = st.selectbox(
            "Select Candidate",
            range(len(screenings)),
            format_func=lambda x: candidate_options[x]
        )

        selected = screenings[selected_idx]

        score = selected["score"]

        if score >= 70:
            decision = "Shortlisted"
        else:
             decision = "Rejected"

        st.write(f"**AI Decision:** {decision}")

        if st.button("Generate Email"):

            if decision == "Shortlisted":

                email = generate_shortlist_email(
                    name=selected["candidate_name"],
                    role="Software Engineer",      # or selected job role
                    skills=", ".join(selected["matched_skills"])
                )

            else:

                email = generate_rejection_email(
                    name=selected["candidate_name"],
                    role="Software Engineer"
                )

            st.text_area(
                "Generated Email",
                email,
                height=350
            )

with tab5:
    st.subheader("Schedule Interview")

    # Only shortlisted candidates
    screenings = [
        s for s in get_all_screenings()
        if s["score"] >= 70
    ]

    if not screenings:
        st.warning("No shortlisted candidates available for interview scheduling.")
        st.stop()

    st.info(f"Found {len(screenings)} shortlisted candidate(s)")

    col1, col2 = st.columns(2)

    with col1:

        candidate_options = [
            f"{s['candidate_name']} (Score: {s['score']}%)"
            for s in screenings
        ]

        selected_idx = st.selectbox(
            "Choose candidate:",
            range(len(screenings)),
            format_func=lambda x: candidate_options[x]
        )

        selected_screening = screenings[selected_idx]

        st.write(f"**Email:** {selected_screening['email']}")
        st.write(f"**Score:** {selected_screening['score']}")

    with col2:

        st.write("**Interview Details**")

        interview_date = st.date_input("Interview Date:")

        interview_time = st.time_input("Interview Time:")

        interviewer_email = st.text_input(
            "Interviewer Email:",
            value="recruiter@company.com"
        )

        notes = st.text_area("Notes:", height=80)

    if st.button("Schedule Interview", use_container_width=True):

        try:

            schedule_interview(
                screening_id=selected_screening['id'],
                candidate_name=selected_screening['candidate_name'],
                candidate_email=selected_screening['email'],
                interview_date=str(interview_date),
                interview_time=str(interview_time),
                interviewer_email=interviewer_email,
                notes=notes
            )

            st.success(
                f"Interview scheduled for {selected_screening['candidate_name']}!"
            )
            st.balloons()

        except Exception as e:
            st.error(f"Error scheduling interview: {str(e)}")

    st.divider()
    st.subheader("Scheduled Interviews")

    interviews = get_all_interviews()

    if interviews:

        st.info(f"Total scheduled: {len(interviews)}")

        for interview in interviews:

            with st.expander(
                f"🔹 {interview['candidate_name']} - {interview['interview_date']} {interview['interview_time']}"
            ):

                col1, col2 = st.columns(2)

                with col1:
                    st.write(f"**Email:** {interview['candidate_email']}")
                    st.write(f"**Date:** {interview['interview_date']}")
                    st.write(f"**Time:** {interview['interview_time']}")

                with col2:
                    st.write(f"**Interviewer:** {interview['interviewer_email']}")
                    st.write(f"**Status:** {interview['status']}")
                    st.write(f"**Created:** {interview['created_date']}")

                if interview['notes']:
                    st.write(f"**Notes:** {interview['notes']}")

                new_status = st.selectbox(
                    "Update Status:",
                    ["Scheduled", "Completed", "Cancelled"],
                    index=["Scheduled", "Completed", "Cancelled"].index(interview['status']),
                    key=f"status_{interview['id']}"
                )

                col1, col2 = st.columns(2)

                with col1:
                    if st.button("Update Status", key=f"update_{interview['id']}"):
                        update_interview_status(interview['id'], new_status)
                        st.success(f"Status updated to {new_status}")
                        st.rerun()

                with col2:
                    if st.button("Delete", key=f"delete_interview_{interview['id']}"):
                        delete_interview(interview['id'])
                        st.success("Interview deleted")
                        st.rerun()

    else:
        st.info("No interviews scheduled yet")