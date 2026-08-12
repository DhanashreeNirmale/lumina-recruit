import streamlit as st

from database.database import initialize_database

from ui.dashboard import show_dashboard
from ui.job_page import show_job_page
from ui.candidate_page import show_candidate_page
from ui.ranking_page import show_ranking_page
from ui.interview_page import show_interview_page
from ui.report_page import show_report_page


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="IndiaTech Recruiter AI",
    page_icon="🇮🇳",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# INITIALIZE DATABASE
# =========================================================

try:
    initialize_database()

except Exception as e:
    st.error(
        f"Database initialization failed: {e}"
    )
    st.stop()


# =========================================================
# APPLICATION HEADER
# =========================================================

st.sidebar.title(
    "🇮🇳 IndiaTech Recruiter AI"
)

st.sidebar.caption(
    "AI-Powered Technology Recruitment Platform"
)

st.sidebar.divider()


# =========================================================
# NAVIGATION
# =========================================================

page = st.sidebar.radio(
    "Navigation",
    [
        "📊 Dashboard",
        "💼 Jobs",
        "👤 Screen Candidate",
        "🏆 Rankings",
        "📅 Interviews",
        "📈 Reports",
    ],
)


# =========================================================
# PROJECT INFORMATION
# =========================================================

st.sidebar.divider()

st.sidebar.markdown(
    """
    **Project Track:** Track A  
    **Option:** Option A  
    **Platform:** India Technology Recruitment
    """
)


# =========================================================
# PAGE ROUTING
# =========================================================

if page == "📊 Dashboard":

    show_dashboard()


elif page == "💼 Jobs":

    show_job_page()


elif page == "👤 Screen Candidate":

    show_candidate_page()


elif page == "🏆 Rankings":

    show_ranking_page()


elif page == "📅 Interviews":

    show_interview_page()


elif page == "📈 Reports":

    show_report_page()