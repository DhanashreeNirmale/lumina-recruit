import streamlit as st

from database.database import initialize_database
from ui.dashboard import show_dashboard
from ui.job_page import show_job_page
from ui.candidate_page import show_candidate_page
from ui.assessment_page import show_assessment_page
from ui.ranking_page import show_ranking_page


st.set_page_config(
    page_title="Lumina Recruit",
    page_icon="🤖",
    layout="wide",
)

initialize_database()

st.sidebar.title("🤖 Lumina Recruit")
st.sidebar.caption("Indian Tech Recruitment Assistant")

page = st.sidebar.radio(
    "Recruiter Workspace",
    [
        "Dashboard",
        "Jobs",
        "Candidates",
        "Technical Assessment",
        "Ranking",
    ],
)

if page == "Dashboard":
    show_dashboard()

elif page == "Jobs":
    show_job_page()

elif page == "Candidates":
    show_candidate_page()

elif page == "Technical Assessment":
    show_assessment_page()

elif page == "Ranking":
    show_ranking_page()