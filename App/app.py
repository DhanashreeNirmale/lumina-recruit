import streamlit as st

from resume_parser import parse_resume, extract_text_from_pdf
from scoring_engine import (
    extract_job_skills,
    calculate_score,
    get_score_interpretation
)

from database import (
    init_database,
    save_screening_result,
    get_all_screenings,
    get_statistics
)

init_database()

st.set_page_config(
    page_title="Resume Screening Chatbot",
    layout="wide"
)

st.title("📄 Resume Screening Chatbot")

st.write(
    "Upload a resume and compare it with the Job Description."
)

tab1, tab2, tab3 = st.tabs(
    [
        "Resume Screening",
        "History",
        "Statistics"
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
            type=["pdf"]
        )

        if uploaded_file is not None:

            with st.spinner("Parsing Resume..."):

                resume_data = parse_resume(uploaded_file)

                uploaded_file.seek(0)
                resume_text = extract_text_from_pdf(uploaded_file)

            st.success("Resume Parsed Successfully")

            st.markdown("### Candidate Information")

            st.write(f"**👤 Name:** {resume_data['name'] or 'Not Found'}")

            st.write(f"**📧 Email:** {resume_data['email'] or 'Not Found'}")

            st.write(f"**📱 Phone:** {resume_data['phone'] or 'Not Found'}")

            education = ", ".join(resume_data["education"]) if resume_data["education"] else "Not Found"

            st.write(f"**🎓 Education:** {education}")

            st.write(f"**🏫 College:** {resume_data['college'] or 'Not Found'}")

            st.write(f"**💼 Experience:** {resume_data['experience']}")

            if resume_data["skills"]:

                st.write("### 🛠 Skills")

                st.success(", ".join(resume_data["skills"]))

            else:

                st.warning("No Skills Found")

            if resume_data["projects"]:

                st.write("### 📂 Projects")

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

                st.warning(
                    "No recognizable skills found."
                )

st.divider()

if resume_data and job_description and job_skills:

    if st.button("Calculate Match Score", use_container_width=True):

        score_result = calculate_score(
            resume_data["skills"],
            job_skills
        )

        st.subheader("Match Analysis")

        col1, col2, col3 = st.columns(3)

        interpretation, color = get_score_interpretation(
            score_result["score"]
        )

        with col1:

            st.metric(
                "Match Score",
                f"{score_result['score']}%"
            )

            st.write(interpretation)

        with col2:

            st.metric(
                "Skills Matched",
                f"{score_result['total_matched']} / {score_result['total_required']}"
            )

        with col3:

            st.metric(
                "Missing Skills",
                len(score_result["missing_skills"])
            )

        st.divider()

        left, middle, right = st.columns(3)

        with left:

            st.success("Matched Skills")

            if score_result["matched_skills"]:

                for skill in score_result["matched_skills"]:

                    st.write(f"✅ {skill}")

            else:

                st.write("No matched skills.")

        with middle:

            st.error("Missing Skills")

            if score_result["missing_skills"]:

                for skill in score_result["missing_skills"]:

                    st.write(f"❌ {skill}")

            else:

                st.write("No missing skills.")

        with right:

            st.info("Extra Skills")

            if score_result["extra_skills"]:

                for skill in score_result["extra_skills"]:

                    st.write(f"⭐ {skill}")

            else:

                st.write("No extra skills.")

        st.divider()

        if st.button(
            "Save Screening Result",
            use_container_width=True
        ):

            try:

                candidate_name = (
                    resume_data["name"]
                    if resume_data["name"]
                    else "Unknown"
                )

                save_screening_result(

                    candidate_name=candidate_name,

                    email=resume_data["email"],

                    phone=resume_data["phone"],

                    resume_text=resume_text,

                    job_description=job_description,

                    score_data=score_result

                )

                st.success(
                    "Screening Result Saved Successfully!"
                )

            except Exception as e:

                st.error(str(e))

elif resume_data or job_description:

    st.warning(
        "Please upload a resume and provide a job description."
    )


with tab2:

    st.subheader("Screening History")

    screenings = get_all_screenings()

    if screenings:

        st.info(f"Total Screenings: {len(screenings)}")

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

                    from database import delete_screening

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

        st.metric(
            "High Performers",
            stats["high_performers"]
        )

    st.divider()

    if stats["total_screenings"] > 0:

        st.success("Statistics Generated Successfully")

    else:

        st.info("No data available yet.")