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
    # Fetch details
    app = get_application_by_id(application_id)
    if not app:
        st.error("Application not found.")
        if st.button("Back to Workspace"):
            st.session_state.pop("view_app_detail_id", None)
            st.rerun()
        return

    candidate = get_candidate_by_id(app["candidate_id"])
    job = get_job_by_id(app["job_id"])
    
    st.markdown(f"""
    <div style="background-color:#1e293b; padding: 20px; border-radius: 12px; margin-bottom: 20px; border: 1px solid rgba(255,255,255,0.05);">
        <h2 style="margin:0; color:white;">👤 Application Detail: {candidate['name']}</h2>
        <p style="margin:5px 0 0 0; color:#94a3b8;">Applying for: <b>{job['title']}</b> | Status: <b>{app['status']}</b></p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("⬅️ Back to Recruiter Portal", type="secondary"):
        st.session_state.pop("view_app_detail_id", None)
        st.rerun()
        
    st.write("")
    
    col1, col2 = st.columns([1, 1])
    
    # ========================================================
    # LEFT COLUMN: CANDIDATE INFO & RESUME
    # ========================================================
    with col1:
        st.subheader("📋 Candidate Profile")
        with st.container(border=True):
            st.write(f"**Email:** {candidate.get('email')}")
            st.write(f"**Phone:** {candidate.get('phone')}")
            st.write(f"**Location:** {candidate.get('location')}")
            st.write(f"**College:** {candidate.get('college')}")
            st.write(f"**Degree:** {candidate.get('degree')} in {candidate.get('branch')}")
            st.write(f"**Experience:** {candidate.get('experience_years')} years")
            st.write(f"**Notice Period:** {candidate.get('notice_period')} days")
            st.write(f"**Expected Salary:** {candidate.get('expected_salary')} LPA")
            st.write(f"**Relocation:** {'Willing' if candidate.get('relocation') else 'Not Willing'}")
            st.write(f"**Skills:** {', '.join(candidate.get('skills', []))}")
            
        with st.expander("📄 View Extracted Resume Text"):
            st.code(candidate.get("resume_text", "No text content available."), language="text")
            
        st.write("---")
        
        # Assessments Section
        st.subheader("⚙️ Assessments Assigned")
        asms = get_assessments_by_application(application_id)
        
        if not asms:
            st.info("No assessments assigned yet.")
        else:
            for asm in asms:
                score_str = f"{asm['score']}%" if asm["score"] is not None else "Pending"
                st.markdown(f"""
                <div style="background-color:rgba(255,255,255,0.02); padding:10px 15px; border-radius:8px; border:1px solid rgba(255,255,255,0.05); margin-bottom:10px;">
                    <b>{asm['type']} Test:</b> {score_str} ({asm['status']})
                </div>
                """, unsafe_allow_html=True)
                
                # If completed, show testcase breakdown details
                if asm["status"] == "Completed" and asm["type"] == "Technical":
                    try:
                        import json
                        details = json.loads(asm["details"])
                        with st.expander("🔍 View Coding Test Cases"):
                            for q_id, q_res in details.items():
                                st.write(f"**Question:** {q_res.get('question')}")
                                st.write(f"Score: {q_res.get('score')} points")
                                if "results" in q_res:
                                    for t_idx, tr in enumerate(q_res["results"]):
                                        status_emoji = "✅" if tr.get("passed") else "❌"
                                        st.write(f" - Testcase {t_idx+1}: {status_emoji} (Expected: `{tr.get('expected')}`, Got: `{tr.get('stdout')}`)")
                    except:
                        pass
        
        st.write("")
        st.write("**Assign New Assessment:**")
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            if st.button("⚡ Assign Aptitude Test", key="assign_apt", use_container_width=True):
                assign_assessment(application_id, "Aptitude")
                ns = NotificationService()
                ns.send_email_notification(candidate["email"], "Aptitude Assessment Assigned", "Please log in to take your test.")
                st.success("Aptitude test assigned!")
                st.rerun()
        with col_c2:
            if st.button("💻 Assign Technical Test", key="assign_tech", use_container_width=True):
                assign_assessment(application_id, "Technical")
                ns = NotificationService()
                ns.send_email_notification(candidate["email"], "Coding Assessment Assigned", "Please log in to complete your technical sandbox challenge.")
                st.success("Technical coding test assigned!")
                st.rerun()

    # ========================================================
    # RIGHT COLUMN: PIPELINE STATUS, MATCH BREAKDOWN & INTERVIEWS
    # ========================================================
    with col2:
        st.subheader("🎯 Application Pipeline Movement")
        statuses = ["Applied", "Screening", "Shortlisted", "Assessment", "Assessment Completed", "Interview", "Selected", "Rejected"]
        try:
            cur_idx = statuses.index(app["status"])
        except:
            cur_idx = 0
            
        new_status = st.selectbox("Pipeline Status", statuses, index=cur_idx)
        if new_status != app["status"]:
            update_application_status(application_id, new_status)
            st.success(f"Status updated to {new_status}")
            st.rerun()
            
        st.write("---")
        
        # AI Match Breakdown
        st.subheader("🤖 AI Compatibility Report")
        st.metric("Compatibility Score", f"{app['match_score']}%")
        st.markdown(app.get("matching_explanation", "No AI analysis report generated yet."), unsafe_allow_html=True)
        
        st.write("---")
        
        # Scheduling Section
        st.subheader("📅 Schedule Interview")
        with st.form("interview_form"):
            int_date = st.date_input("Date")
            int_time = st.time_input("Time")
            int_mode = st.selectbox("Interview Mode", ["Online", "In-person", "Phone"])
            int_link = st.text_input("Meeting Link / Venue Address", value="https://meet.google.com/abc-defg-hij")
            int_notes = st.text_area("Interview Instructions/Notes")
            
            if st.form_submit_button("Book Interview"):
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
                
                # Send email notification
                ns = NotificationService()
                ns.send_email_notification(
                    candidate["email"],
                    "Interview Scheduled",
                    f"Hi {candidate['name']},\n\nWe have scheduled your interview on {int_date} at {int_time}.\nJoin link: {int_link}\n\nRegards,\nLumina Recruit"
                )
                
                # Move candidate status to 'Interview' automatically
                update_application_status(application_id, "Interview")
                
                st.success("Interview booked successfully!")
                st.rerun()

    # ========================================================
    # BOTTOM SECTION: CONVERSATION / MESSAGE BOX
    # ========================================================
    st.write("---")
    st.subheader("💬 Chat with Candidate")
    ms_service = MessagingService()
    history = ms_service.fetch_chat_history(application_id)
    
    chat_box = st.container(height=280)
    with chat_box:
        if not history:
            st.write("*No chat history yet. Send a message below to coordinate.*")
        else:
            for msg in history:
                align = "right" if msg["sender_role"] == "recruiter" else "left"
                color = "#6366f1" if msg["sender_role"] == "recruiter" else "#1e293b"
                st.markdown(f"""
                <div style="text-align: {align}; margin-bottom: 10px;">
                    <div style="display: inline-block; padding: 10px 14px; border-radius: 12px; background-color: {color}; color: white; max-width: 70%; text-align: left;">
                        <b>{msg['sender_name']}</b> ({msg['sender_role'].capitalize()}):<br>
                        {msg['message']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
    new_msg = st.text_input("Type recruiter message...", key="recruiter_chat_input")
    if st.button("Send Message", key="recruiter_send_btn"):
        if new_msg.strip():
            # Send message
            ms_service.post_message(application_id, st.session_state.user["id"], "recruiter", new_msg)
            st.rerun()
