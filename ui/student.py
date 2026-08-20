import streamlit as st
import pandas as pd
from datetime import date
from database.repositories import (
    get_candidate_by_user_id,
    create_or_update_candidate,
    get_all_jobs,
    create_application,
    get_applications_by_candidate,
    get_assessments_by_candidate,
    get_all_questions_by_type
)
from services.resume_service import ResumeService
from services.matching_service import MatchingService
from assessments.aptitude import evaluate_aptitude_test
from assessments.technical import evaluate_technical_test
from messaging.messaging_service import MessagingService
from scheduling.interview_service import InterviewService

def show_student_portal():
    user = st.session_state.user
    candidate = get_candidate_by_user_id(user["id"])
    
    # Custom CSS for the Candidate Dashboard
    st.markdown("""
    <style>
    .student-header {
        font-family: 'Outfit', sans-serif;
        background: linear-gradient(135deg, #1e1b4b 0%, #312e81 100%);
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 24px;
        border: 1px solid rgba(99, 102, 241, 0.2);
    }
    .profile-card {
        background: rgba(30, 41, 59, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

    # Header
    st.markdown(f"""
    <div class="student-header">
        <h2 style="margin:0; color:white; font-size:28px;">🙋‍♂️ Candidate Workspace</h2>
        <p style="margin:5px 0 0 0; color:#c7d2fe;">Welcome back, {user['username']}! Manage your profile, apply to jobs, and complete assessments.</p>
    </div>
    """, unsafe_allow_html=True)

    # Sub Navigation
    menu = ["Dashboard", "Resume & Profile", "Find Jobs", "My Applications", "Assessments", "Messages", "Interviews"]
    selected_tab = st.radio("Navigate Workspace", menu, horizontal=True, key="student_nav")
    st.divider()

    # ========================================================
    # 1. DASHBOARD TAB
    # ========================================================
    if selected_tab == "Dashboard":
        col1, col2 = st.columns([2, 1])
        with col1:
            st.subheader("🚀 Getting Started")
            st.write("Complete these simple steps to start applying for jobs:")
            
            # Check profile completeness
            has_resume = bool(candidate.get("resume_filename")) if candidate else False
            has_skills = len(candidate.get("skills", [])) > 0 if candidate else False
            has_experience = candidate.get("experience_years", 0) > 0 if candidate else False
            
            # Simple Checklist
            st.checkbox("Upload your Resume", value=has_resume, disabled=True)
            st.checkbox("Validate your extracted Skills", value=has_skills, disabled=True)
            st.checkbox("Apply to jobs", value=len(get_applications_by_candidate(candidate["id"] if candidate else 0)) > 0, disabled=True)
            
            # Completeness Progress
            steps = [has_resume, has_skills, has_experience]
            completeness = int((sum(steps) / len(steps)) * 100)
            
            st.write("### Profile Completeness")
            st.progress(completeness / 100.0)
            st.write(f"Your profile is **{completeness}%** complete.")
            
        with col2:
            st.subheader("💡 Tips for Success")
            st.info("💡 Keep your skills updated. The matching agent evaluates candidate skills directly against required job specifications.")
            st.info("💡 Once you apply, the recruiter might assign Aptitude or Coding assessments. Keep an eye on the **Assessments** tab!")

    # ========================================================
    # 2. RESUME & PROFILE TAB
    # ========================================================
    elif selected_tab == "Resume & Profile":
        st.subheader("📄 Resume Upload & Profile Parsing")
        
        uploaded_file = st.file_uploader("Upload your resume (PDF, DOCX, or TXT)", type=["pdf", "docx", "txt"])
        
        if uploaded_file is not None:
            if st.button("⚡ Parse Resume with AI"):
                with st.spinner("Extracting and analyzing resume..."):
                    try:
                        file_bytes = uploaded_file.getvalue()
                        service = ResumeService()
                        parsed_profile = service.process_and_save_resume(user["id"], uploaded_file.name, file_bytes)
                        st.success("Resume parsed and profile updated successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error parsing resume: {e}")
                        
        # Profile Editor Form
        st.write("---")
        st.subheader("✏️ Edit Profile Details")
        
        if candidate:
            with st.form("profile_form"):
                col_a, col_b = st.columns(2)
                with col_a:
                    cand_name = st.text_input("Full Name", value=candidate.get("name", ""))
                    cand_email = st.text_input("Email Address", value=candidate.get("email", ""))
                    cand_phone = st.text_input("Phone Number", value=candidate.get("phone", ""))
                    cand_loc = st.text_input("Current Location", value=candidate.get("location", ""))
                    cand_college = st.text_input("College / University", value=candidate.get("college", ""))
                with col_b:
                    cand_degree = st.text_input("Degree (e.g. B.Tech)", value=candidate.get("degree", ""))
                    cand_branch = st.text_input("Branch/Major (e.g. Computer Science)", value=candidate.get("branch", ""))
                    cand_grad_year = st.text_input("Graduation Year", value=candidate.get("graduation_year", ""))
                    cand_exp = st.number_input("Years of Experience", min_value=0.0, max_value=40.0, value=float(candidate.get("experience_years", 0.0) or 0.0), step=0.5)
                    cand_notice = st.number_input("Notice Period (Days)", min_value=0, max_value=180, value=int(candidate.get("notice_period", 0) or 0))
                
                col_c, col_d = st.columns(2)
                with col_c:
                    cand_salary = st.number_input("Expected Salary (LPA)", min_value=0.0, max_value=100.0, value=float(candidate.get("expected_salary", 0.0) or 0.0))
                    cand_reloc = st.checkbox("Willing to Relocate", value=bool(candidate.get("relocation", False)))
                with col_d:
                    # Parse lists safely
                    cand_skills_str = st.text_area("Skills (Comma separated)", value=", ".join(candidate.get("skills", [])))
                    cand_pref_locs_str = st.text_input("Preferred Locations (Comma separated)", value=", ".join(candidate.get("preferred_locations", [])))
                    
                if st.form_submit_button("Save Profile"):
                    updated_data = {
                        "name": cand_name,
                        "email": cand_email,
                        "phone": cand_phone,
                        "location": cand_loc,
                        "college": cand_college,
                        "degree": cand_degree,
                        "branch": cand_branch,
                        "graduation_year": cand_grad_year,
                        "experience_years": cand_exp,
                        "notice_period": cand_notice,
                        "expected_salary": cand_salary,
                        "relocation": 1 if cand_reloc else 0,
                        "skills": [s.strip() for s in cand_skills_str.split(",") if s.strip()],
                        "preferred_locations": [l.strip() for l in cand_pref_locs_str.split(",") if l.strip()],
                        # Preserve file details
                        "resume_filename": candidate.get("resume_filename", ""),
                        "resume_text": candidate.get("resume_text", "")
                    }
                    create_or_update_candidate(user["id"], updated_data)
                    st.success("Profile saved successfully!")
                    st.rerun()
        else:
            st.info("Please upload your resume to generate a profile, or fill in the details.")

    # ========================================================
    # 3. FIND JOBS TAB
    # ========================================================
    elif selected_tab == "Find Jobs":
        st.subheader("🔍 Active Job Openings")
        
        jobs = get_all_jobs()
        if not jobs:
            st.info("No job openings available currently.")
        else:
            for job in jobs:
                with st.expander(f"💼 {job['title']} — {job['location'] or 'Remote'}"):
                    st.write(f"**Experience Required:** {job['min_experience']} years")
                    st.write(f"**Salary Range:** {job['min_salary']} - {job['max_salary']} LPA")
                    st.write(f"**Max Notice Period:** {job['max_notice_period']} days")
                    st.write(f"**Required Skills:** {', '.join(job['required_skills'])}")
                    st.write("**Job Description:**")
                    st.write(job["description"])
                    
                    # Application Check
                    if candidate:
                        # Check if already applied
                        c_apps = get_applications_by_candidate(candidate["id"])
                        applied_job_ids = [a["job_id"] for a in c_apps]
                        
                        if job["id"] in applied_job_ids:
                            st.button("Applied", key=f"applied_{job['id']}", disabled=True)
                        else:
                            if st.button("Apply Now", key=f"apply_{job['id']}", type="primary"):
                                # Create Application
                                app_id = create_application(job["id"], candidate["id"])
                                if app_id:
                                    # Immediately run Matching Evaluation in background
                                    with st.spinner("Calculating application fit..."):
                                        try:
                                            ms = MatchingService()
                                            ms.evaluate_and_save_match(app_id)
                                            st.success("Successfully applied! Your profile has been matched.")
                                            st.rerun()
                                        except Exception as e:
                                            st.warning(f"Applied successfully, but compatibility matching is pending: {e}")
                                            st.rerun()
                                else:
                                    st.error("Error submitting application.")
                    else:
                        st.warning("Please upload a resume or create your candidate profile first.")

    # ========================================================
    # 4. MY APPLICATIONS TAB
    # ========================================================
    elif selected_tab == "My Applications":
        st.subheader("📁 My Applications")
        
        if not candidate:
            st.info("Please build your profile first.")
        else:
            apps = get_applications_by_candidate(candidate["id"])
            if not apps:
                st.info("You haven't applied to any jobs yet.")
            else:
                df_apps = pd.DataFrame(apps)
                # Keep interesting columns
                cols = ["job_title", "match_score", "status", "created_at"]
                st.dataframe(df_apps[cols], use_container_width=True, hide_index=True)

    # ========================================================
    # 5. ASSESSMENTS TAB
    # ========================================================
    elif selected_tab == "Assessments":
        st.subheader("✏️ Assigned Assessments")
        
        if not candidate:
            st.info("Profile not created.")
        else:
            asms = get_assessments_by_candidate(candidate["id"])
            pending_asms = [a for a in asms if a["status"] == "Pending"]
            completed_asms = [a for a in asms if a["status"] == "Completed"]
            
            st.write("### Pending Assessments")
            if not pending_asms:
                st.success("🎉 No pending assessments! You are up to date.")
            else:
                for asm in pending_asms:
                    with st.container():
                        st.markdown(f"""
                        <div class="profile-card">
                            <h4>{asm['type']} Assessment for <b>{asm['job_title']}</b></h4>
                            <p>Status: <span style="color:#f59e0b; font-weight:bold;">Pending</span></p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if st.button("Start Test", key=f"start_asm_{asm['id']}", type="primary"):
                            st.session_state.active_assessment = asm
                            st.rerun()
                            
            st.write("---")
            st.write("### Completed Assessments")
            if completed_asms:
                df_comp = pd.DataFrame(completed_asms)
                st.dataframe(df_comp[["job_title", "type", "score", "status"]], use_container_width=True, hide_index=True)
            else:
                st.info("No completed assessments yet.")
                
        # ASSESSMENT TAKING CLIENT MODAL/VIEW
        if st.session_state.get("active_assessment"):
            asm = st.session_state.active_assessment
            st.write("---")
            st.markdown(f"### 📝 Taking {asm['type']} Test for {asm['job_title']}")
            
            # Load Questions
            questions = get_all_questions_by_type(asm["type"])
            
            if not questions:
                st.error("No questions found in this assessment category.")
                if st.button("Close"):
                    st.session_state.pop("active_assessment", None)
                    st.rerun()
            else:
                if asm["type"] == "Aptitude":
                    # Render MCQ Form
                    answers = {}
                    with st.form("aptitude_test_form"):
                        for idx, q in enumerate(questions):
                            st.markdown(f"**Q{idx+1}: {q['question_text']}** (Category: {q['category']})")
                            options = q["options"] # list
                            ans = st.radio("Select Option", options, key=f"apt_ans_{q['id']}")
                            answers[str(q["id"])] = ans
                            st.write("")
                            
                        if st.form_submit_button("Submit Assessment"):
                            with st.spinner("Grading..."):
                                score = evaluate_aptitude_test(asm["id"], answers)
                                st.success(f"Assessment completed! You scored: {score}%")
                                st.session_state.pop("active_assessment", None)
                                st.rerun()
                                
                elif asm["type"] == "Technical":
                    # Render Coding IDE Form
                    # Let candidate take one coding question at a time or together
                    st.warning("Write python code in the fields below. Do not import external packages. Define the requested function.")
                    
                    code_submissions = {}
                    for idx, q in enumerate(questions):
                        st.markdown(f"#### Question {idx+1}: {q['question_text']}")
                        st.info(f"**Marks:** {q['marks']} points")
                        # Code Editor Text Area
                        code = st.text_area("Your Python Code", value=q["code_template"], height=200, key=f"tech_code_{q['id']}")
                        code_submissions[str(q["id"])] = code
                        st.write("")
                        
                    if st.button("Submit Coding Solutions", type="primary"):
                        with st.spinner("Running test cases on sandbox compiler..."):
                            try:
                                score = evaluate_technical_test(asm["id"], code_submissions)
                                st.success(f"Coding test graded! You scored: {score}%")
                                st.session_state.pop("active_assessment", None)
                                st.rerun()
                            except Exception as err:
                                st.error(f"Error submitting solutions: {err}")
                                
                if st.button("Cancel Assessment"):
                    st.session_state.pop("active_assessment", None)
                    st.rerun()

    # ========================================================
    # 6. MESSAGES TAB
    # ========================================================
    elif selected_tab == "Messages":
        st.subheader("💬 Recruiter Messaging")
        
        if not candidate:
            st.info("Profile not created.")
        else:
            apps = get_applications_by_candidate(candidate["id"])
            if not apps:
                st.info("You must apply for a job first to open a messaging channel.")
            else:
                # App Selector for Chat
                app_map = {f"{a['job_title']} (Status: {a['status']})": a for a in apps}
                selected_app_lbl = st.selectbox("Select Application Chat", list(app_map.keys()))
                selected_app = app_map[selected_app_lbl]
                
                # Chat History
                ms_service = MessagingService()
                history = ms_service.fetch_chat_history(selected_app["id"])
                
                # Container
                chat_box = st.container(height=350)
                with chat_box:
                    if not history:
                        st.write("*No messages exchanged yet. Send a message to start conversation.*")
                    else:
                        for msg in history:
                            align = "right" if msg["sender_role"] == "student" else "left"
                            color = "#3b82f6" if msg["sender_role"] == "student" else "#1e293b"
                            st.markdown(f"""
                            <div style="text-align: {align}; margin-bottom: 10px;">
                                <div style="display: inline-block; padding: 10px 14px; border-radius: 12px; background-color: {color}; color: white; max-width: 70%; text-align: left;">
                                    <b>{msg['sender_name']}</b> ({msg['sender_role'].capitalize()}):<br>
                                    {msg['message']}
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                # Input
                new_msg = st.text_input("Type your message...", key="new_message_input")
                if st.button("Send", key="send_msg_btn"):
                    if new_msg.strip():
                        ms_service.post_message(selected_app["id"], user["id"], "student", new_msg)
                        st.rerun()

    # ========================================================
    # 7. INTERVIEWS TAB
    # ========================================================
    elif selected_tab == "Interviews":
        st.subheader("📅 Scheduled Interviews")
        
        if not candidate:
            st.info("Profile not created.")
        else:
            ints = get_interviews_by_candidate(candidate["id"])
            if not ints:
                st.info("No interviews scheduled yet.")
            else:
                for item in ints:
                    st.markdown(f"""
                    <div class="profile-card">
                        <h3>💼 {item['job_title']}</h3>
                        <p><b>Date:</b> {item['interview_date']} | <b>Time:</b> {item['interview_time']}</p>
                        <p><b>Mode:</b> {item['mode']}</p>
                        <p><b>Link/Venue:</b> <a href="{item['venue_link']}" target="_blank">{item['venue_link']}</a></p>
                        <p><b>Notes:</b> {item['notes']}</p>
                        <p>Status: <span style="color:#10b981; font-weight:bold;">{item['status']}</span></p>
                    </div>
                    """, unsafe_allow_html=True)
