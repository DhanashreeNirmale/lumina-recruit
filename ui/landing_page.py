import streamlit as st
import textwrap


def show_landing_page():

    # =========================================================
    # PAGE CONFIG
    # =========================================================

    st.set_page_config(
        page_title="LUMINA-RECRUIT",
        page_icon="L",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    # =========================================================
    # CUSTOM CSS
    # =========================================================

    st.markdown(
        textwrap.dedent("""
        <style>

        /* ---------- GLOBAL ---------- */

        .stApp {
            background: #0b0f14;
            color: white;
        }

        .block-container {
            padding-top: 0rem;
            padding-left: 7%;
            padding-right: 7%;
            padding-bottom: 3rem;
        }

        #MainMenu {
            visibility: hidden;
        }

        footer {
            visibility: hidden;
        }

        header {
            background: transparent;
        }


        /* ---------- NAVBAR ---------- */

        .navbar {
            height: 75px;
            display: flex;
            align-items: center;
            justify-content: space-between;

            border-bottom: 1px solid rgba(255,255,255,0.08);

            margin-bottom: 20px;
        }

        .logo {
            font-size: 24px;
            font-weight: 750;
            letter-spacing: 2px;
            color: #ffffff;
        }

        .logo span {
            color: #6ea8fe;
        }

        .nav-subtitle {
            color: #8b93a1;
            font-size: 14px;
        }


        /* ---------- HERO ---------- */

        .hero {
            min-height: 560px;

            display: flex;
            align-items: center;

            gap: 70px;

            padding-top: 55px;
            padding-bottom: 70px;
        }

        .hero-left {
            flex: 1;
        }

        .hero-right {
            flex: 1;
        }

        .hero-label {
            color: #6ea8fe;

            font-size: 13px;
            font-weight: 700;

            letter-spacing: 2px;

            text-transform: uppercase;

            margin-bottom: 20px;
        }

        .hero-title {
            font-size: 62px;

            line-height: 1.05;

            font-weight: 750;

            margin: 0;

            color: #ffffff;
        }

        .hero-title span {
            color: #6ea8fe;
        }

        .hero-description {
            max-width: 610px;

            margin-top: 25px;

            color: #9ca3af;

            font-size: 17px;

            line-height: 1.7;
        }


        /* ---------- HERO IMAGE ---------- */

        .hero-image {
            width: 100%;
            height: 430px;

            object-fit: cover;

            border-radius: 20px;

            border: 1px solid rgba(255,255,255,0.10);

            box-shadow:
                0 25px 60px rgba(0,0,0,0.35);
        }


        /* ---------- SECTION ---------- */

        .section {
            padding-top: 65px;
            padding-bottom: 35px;
        }

        .section-title {
            text-align: center;

            font-size: 34px;

            font-weight: 700;

            color: white;

            margin-bottom: 10px;
        }

        .section-description {
            text-align: center;

            color: #8b93a1;

            font-size: 15px;

            margin-bottom: 40px;
        }


        /* ---------- FEATURE CARDS ---------- */

        .feature-card {
            background: #111720;

            border: 1px solid rgba(255,255,255,0.08);

            border-radius: 16px;

            padding: 28px;

            min-height: 190px;

            transition: all 0.2s ease;
        }

        .feature-card:hover {
            border-color: rgba(110,168,254,0.45);

            transform: translateY(-4px);

            box-shadow:
                0 15px 35px rgba(0,0,0,0.25);
        }

        .feature-number {
            color: #6ea8fe;

            font-size: 12px;

            font-weight: 700;

            letter-spacing: 1.5px;
        }

        .feature-title {
            color: #ffffff;

            font-size: 20px;

            font-weight: 650;

            margin-top: 15px;

            margin-bottom: 10px;
        }

        .feature-description {
            color: #8f98a6;

            font-size: 14px;

            line-height: 1.6;
        }


        /* ---------- CTA ---------- */

        .cta {
            margin-top: 80px;

            padding: 65px 40px;

            text-align: center;

            background: #111720;

            border: 1px solid rgba(255,255,255,0.08);

            border-radius: 20px;
        }

        .cta-title {
            color: white;

            font-size: 32px;

            font-weight: 700;

            margin-bottom: 12px;
        }

        .cta-description {
            max-width: 650px;

            margin: auto;

            color: #8f98a6;

            line-height: 1.7;

            font-size: 15px;
        }


        /* ---------- FOOTER ---------- */

        .footer {
            text-align: center;

            color: #626b78;

            font-size: 13px;

            margin-top: 45px;
        }

        </style>
        """),
        unsafe_allow_html=True
    )


    # =========================================================
    # NAVBAR
    # =========================================================

    st.markdown(
        textwrap.dedent("""
        <div class="navbar">

            <div class="logo">
                LUMINA<span>-RECRUIT</span>
            </div>

            <div class="nav-subtitle">
                Intelligent Recruitment Platform
            </div>

        </div>
        """),
        unsafe_allow_html=True
    )


    # =========================================================
    # HERO SECTION
    # =========================================================

    st.markdown(
        textwrap.dedent("""
        <div class="hero">

            <div class="hero-left">

                <div class="hero-label">
                    AI-POWERED RECRUITMENT
                </div>

                <h1 class="hero-title">
                    Hire smarter.<br>
                    Find the <span>right talent.</span>
                </h1>

                <p class="hero-description">
                    LUMINA-RECRUIT brings resume intelligence,
                    job matching, technical assessments and
                    candidate ranking together in one
                    intelligent recruitment platform.
                </p>

            </div>


            <div class="hero-right">

                <img
                    class="hero-image"
                    src="https://images.unsplash.com/photo-1556761175-b413da4baf72?auto=format&fit=crop&w=1200&q=80"
                >

            </div>

        </div>
        """),
        unsafe_allow_html=True
    )


    # =========================================================
    # PLATFORM FEATURES
    # =========================================================

    st.markdown(
        textwrap.dedent("""
        <div class="section">

            <div class="section-title">
                Complete recruitment workflow
            </div>

            <div class="section-description">
                Everything recruiters need to evaluate and manage candidates.
            </div>

        </div>
        """),
        unsafe_allow_html=True
    )


    # ---------- ROW 1 ----------

    col1, col2, col3 = st.columns(3, gap="large")


    with col1:

        st.markdown(
            textwrap.dedent("""
            <div class="feature-card">

                <div class="feature-number">
                    01
                </div>

                <div class="feature-title">
                    Resume Analysis
                </div>

                <div class="feature-description">
                    Extract candidate information, skills,
                    education, experience and projects
                    from uploaded resumes.
                </div>

            </div>
            """),
            unsafe_allow_html=True
        )


    with col2:

        st.markdown(
            textwrap.dedent("""
            <div class="feature-card">

                <div class="feature-number">
                    02
                </div>

                <div class="feature-title">
                    Job Matching
                </div>

                <div class="feature-description">
                    Compare candidate profiles with job
                    requirements and identify the strongest
                    matches.
                </div>

            </div>
            """),
            unsafe_allow_html=True
        )


    with col3:

        st.markdown(
            textwrap.dedent("""
            <div class="feature-card">

                <div class="feature-number">
                    03
                </div>

                <div class="feature-title">
                    Technical Assessment
                </div>

                <div class="feature-description">
                    Evaluate candidates through technical
                    questions, coding assessments and
                    automated scoring.
                </div>

            </div>
            """),
            unsafe_allow_html=True
        )


    # ---------- ROW 2 ----------

    st.write("")


    col1, col2, col3 = st.columns(3, gap="large")


    with col1:

        st.markdown(
            textwrap.dedent("""
            <div class="feature-card">

                <div class="feature-number">
                    04
                </div>

                <div class="feature-title">
                    Candidate Ranking
                </div>

                <div class="feature-description">
                    Combine resume analysis, job matching
                    and assessment results to rank candidates
                    objectively.
                </div>

            </div>
            """),
            unsafe_allow_html=True
        )


    with col2:

        st.markdown(
            textwrap.dedent("""
            <div class="feature-card">

                <div class="feature-number">
                    05
                </div>

                <div class="feature-title">
                    Recruiter Dashboard
                </div>

                <div class="feature-description">
                    Monitor candidates, jobs, assessments
                    and recruitment progress from one place.
                </div>

            </div>
            """),
            unsafe_allow_html=True
        )


    with col3:

        st.markdown(
            textwrap.dedent("""
            <div class="feature-card">

                <div class="feature-number">
                    06
                </div>

                <div class="feature-title">
                    AI Recruitment Agents
                </div>

                <div class="feature-description">
                    Specialized AI agents handle resume
                    analysis, job requirements, matching
                    and candidate evaluation.
                </div>

            </div>
            """),
            unsafe_allow_html=True
        )


    # =========================================================
    # CTA
    # =========================================================

    st.markdown(
        textwrap.dedent("""
        <div class="cta">

            <div class="cta-title">
                Make recruitment data-driven.
            </div>

            <div class="cta-description">
                Reduce manual screening, evaluate candidates
                consistently and focus recruiter attention
                on the people who matter most.
            </div>

        </div>
        """),
        unsafe_allow_html=True
    )


    # =========================================================
    # FOOTER
    # =========================================================

    st.markdown(
        textwrap.dedent("""
        <div class="footer">
            LUMINA-RECRUIT · Intelligent Recruitment Platform
        </div>
        """),
        unsafe_allow_html=True
    )