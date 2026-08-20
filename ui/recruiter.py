import streamlit as st
import pandas as pd
from database.repositories import (
    get_all_candidates,
    get_all_jobs,
    get_all_applications,
    get_all_interviews,
    delete_job
)
from services.job_service import JobService
from matching.ranker import rank_candidates_for_job
from agents.recruiter_agent import RecruiterAgent
from ui.candidate_detail import show_candidate_detail_page

def show_recruiter_portal():
    # If drilling down into a specific candidate's application detail, show that sub-page
    if st.session_state.get("view_app_detail_id"):
        show_candidate_detail_page(st.session_state.view_app_detail_id)
        return

    user = st.session_state.user
    
    st.markdown("""
    <style>
    .recruiter-header {
        font-family: 'Outfit', sans-serif;
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 24px;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    </style>
    """, unsafe_allow_html=True)

    # Header
    st.markdown(f"""
    <div class="recruiter-header">
        <h2 style="margin:0; color:white; font-size:28px;">💼 Recruiter Workspace</h2>
        <p style="margin:5px 0 0 0; color:#94a3b8;">Manage job listings, review applicants, track assessments, and schedule interviews.</p>
    </div>
    """, unsafe_allow_html=True)

    # Sub Navigation
    menu = ["Overview", "Post a Job", "Rankings & Reports", "Agent Playground", "Interview Calendar"]
    selected_tab = st.radio("Navigate Workspace", menu, horizontal=True, key="recruiter_nav")
    st.divider()

    # Load resources
    candidates = get_all_candidates()
    jobs = get_all_jobs()
    apps = get_all_applications()
    interviews = get_all_interviews()

    # ========================================================
    # 1. OVERVIEW TAB
    # ========================================================
    if selected_tab == "Overview":
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Candidates", len(candidates))
        col2.metric("Active Jobs", len(jobs))
        col3.metric("Applications Received", len(apps))
        col4.metric("Scheduled Interviews", len(interviews))
        
        st.write("### 📂 Applicant Pipeline")
        if not apps:
            st.info("No applications received yet.")
        else:
            # Table of applications
            df_apps = pd.DataFrame(apps)
            
            # Show search & filter
            status_filter = st.selectbox("Filter by Status", ["All"] + list(df_apps["status"].unique()))
            
            filtered_df = df_apps
            if status_filter != "All":
                filtered_df = df_apps[df_apps["status"] == status_filter]
                
            # Render a custom table with a "View" button for each row
            for idx, row in filtered_df.iterrows():
                col_name, col_job, col_score, col_status, col_btn = st.columns([2, 2, 1, 2, 1])
                col_name.write(f"**{row['candidate_name']}**")
                col_job.write(row["job_title"])
                col_score.write(f"{row['match_score']}%")
                col_status.write(f"`{row['status']}`")
                if col_btn.button("View Detail", key=f"view_btn_{row['id']}", type="secondary"):
                    st.session_state.view_app_detail_id = row["id"]
                    st.rerun()

    # ========================================================
    # 2. POST A JOB TAB
    # ========================================================
    elif selected_tab == "Post a Job":
        st.subheader("📝 Post a New Job Listing")
        
        manual_title = st.text_input("Job Title (Optional - AI will extract if empty)")
        jd_text = st.text_area("Job Description (Paste requirements, responsibilities, etc.)", height=250)
        
        if st.button("🚀 Publish Job Listing", type="primary"):
            if not jd_text.strip():
                st.error("Please provide a job description.")
            else:
                with st.spinner("Analyzing description and publishing..."):
                    try:
                        service = JobService()
                        job_data = service.parse_and_save_job(jd_text, manual_title)
                        st.success(f"Job '{job_data['title']}' published successfully!")
                        st.write("**Extracted Requirements:**")
                        st.json({
                            "title": job_data["title"],
                            "required_skills": job_data["required_skills"],
                            "min_experience": job_data["min_experience"],
                            "location": job_data["location"],
                            "min_salary": job_data["min_salary"],
                            "max_salary": job_data["max_salary"],
                            "max_notice_period": job_data["max_notice_period"]
                        })
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error publishing job: {e}")
                        
        st.write("---")
        st.write("### Active Listings")
        if not jobs:
            st.info("No active job listings.")
        else:
            for j in jobs:
                col_j1, col_j2 = st.columns([5, 1])
                col_j1.write(f"**{j['title']}** — {j['location']} ({j['min_experience']}y+ exp, {j['min_salary']}-{j['max_salary']} LPA)")
                if col_j2.button("Delete", key=f"del_job_{j['id']}"):
                    delete_job(j["id"])
                    st.success("Job deleted successfully.")
                    st.rerun()

    # ========================================================
    # 3. RANKINGS & REPORTS TAB
    # ========================================================
    elif selected_tab == "Rankings & Reports":
        st.subheader("🏆 Candidate Rankings")
        st.caption("Combined Score = 60% Job Match + 40% Assessments (Aptitude 30% / Technical 70%)")
        
        if not jobs:
            st.info("Please create a job first.")
        else:
            job_map = {f"#{j['id']} — {j['title']}": j for j in jobs}
            selected_job_lbl = st.selectbox("Rankings for Job", list(job_map.keys()))
            selected_job = job_map[selected_job_lbl]
            
            # Get applications for this job
            job_apps = [a for a in apps if a["job_id"] == selected_job["id"]]
            
            if not job_apps:
                st.info("No applications received for this job yet.")
            else:
                ranked_candidates = rank_candidates_for_job(selected_job["id"], job_apps)
                df_ranked = pd.DataFrame(ranked_candidates)
                
                # Show top match success message
                if not df_ranked.empty:
                    top_cand = df_ranked.iloc[0]
                    st.success(f"🏆 **Top Match Candidate:** {top_cand['candidate_name']} (Final Score: {top_cand['final_score']}/100)")
                
                # Rename columns for presentation
                disp_df = df_ranked.rename(columns={
                    "candidate_name": "Candidate",
                    "match_score": "Job Match %",
                    "aptitude_score": "Aptitude %",
                    "technical_score": "Technical %",
                    "assessment_score": "Assessment Combined %",
                    "final_score": "Final Combined Score",
                    "status": "Pipeline Status"
                })
                
                st.dataframe(
                    disp_df[["Candidate", "Job Match %", "Aptitude %", "Technical %", "Assessment Combined %", "Final Combined Score", "Pipeline Status"]],
                    use_container_width=True,
                    hide_index=True
                )
                
                # CSV Export
                csv_data = disp_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    "⬇️ Export Rankings CSV",
                    data=csv_data,
                    file_name=f"candidate_rankings_job_{selected_job['id']}.csv",
                    mime="text/csv",
                    type="primary"
                )

    # ========================================================
    # 4. AGENT PLAYGROUND TAB
    # ========================================================
    elif selected_tab == "Agent Playground":
        st.subheader("🤖 Recruiter Coordinator Agent Playground")
        st.caption("Ask our AI Recruiter questions about the database. Example: 'Who is the best match for python?' or 'Who has the highest coding score?'")
        
        # Initialize Agent
        if "recruiter_agent" not in st.session_state:
            st.session_state.recruiter_agent = RecruiterAgent()
            
        agent = st.session_state.recruiter_agent
        
        # Render chat logs
        for idx, chat in enumerate(agent.memory):
            if chat.startswith("User:"):
                st.markdown(f"**🧑‍💼 Recruiter:** {chat[5:]}")
            elif chat.startswith("Agent (Fallback):") or chat.startswith("Agent:"):
                st.markdown(f"**🤖 AI Agent:** {chat[chat.find(':')+1:]}")
            st.write("")
            
        # Chat Query Form
        with st.form("agent_query_form", clear_on_submit=True):
            query_input = st.text_input("Ask Agent", placeholder="Type your query...")
            if st.form_submit_button("Query Agent"):
                if query_input.strip():
                    with st.spinner("Agent is reasoning..."):
                        agent.answer_query(query_input)
                    st.rerun()

    # ========================================================
    # 5. INTERVIEW CALENDAR TAB
    # ========================================================
    elif selected_tab == "Interview Calendar":
        st.subheader("📅 Scheduled Interviews")
        
        if not interviews:
            st.info("No upcoming interviews scheduled.")
        else:
            df_ints = pd.DataFrame(interviews)
            st.dataframe(
                df_ints[["candidate_name", "job_title", "interview_date", "interview_time", "mode", "status", "notes"]],
                use_container_width=True,
                hide_index=True
            )
