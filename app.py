import streamlit as st

# MUST BE FIRST Streamlit command
st.set_page_config(
    page_title="Lumina Recruit — Agentic AI Recruitment Platform",
    layout="wide",
    initial_sidebar_state="expanded"
)

from database.models import initialize_database
from ui.landing import show_landing_page
from ui.auth import show_auth_page
from ui.student import show_student_portal
from ui.recruiter import show_recruiter_portal

# Initialize SQLite database
initialize_database()

# Manage state routing
if "page" not in st.session_state:
    st.session_state.page = "landing"

# Sidebar controls for authenticated users
if st.session_state.page not in ["landing", "auth"] and st.session_state.get("user"):
    user = st.session_state.user
    st.sidebar.title("LUMINA RECRUIT")
    st.sidebar.caption("Two-Sided Recruitment Platform")
    
    st.sidebar.markdown("---")
    st.sidebar.write(f"Logged in as: **{user['username']}**")
    st.sidebar.write(f"Role: `{user['role'].capitalize()}`")
    
    # Let recruiters clear applicant drill-down view
    if user['role'] == "recruiter" and st.session_state.get("view_app_detail_id"):
        if st.sidebar.button("📁 All Applications"):
            st.session_state.pop("view_app_detail_id", None)
            st.rerun()
            
    st.sidebar.markdown("---")
    if st.sidebar.button(" Log Out", type="primary", use_container_width=True):
        st.session_state.clear()
        st.session_state.page = "landing"
        st.rerun()

# Page Routing
if st.session_state.page == "landing":
    show_landing_page()
elif st.session_state.page == "auth":
    show_auth_page()
elif st.session_state.page == "student_dashboard":
    show_student_portal()
elif st.session_state.page == "recruiter_dashboard":
    show_recruiter_portal()