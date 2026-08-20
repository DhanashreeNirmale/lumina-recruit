import streamlit as st
import textwrap

def show_landing_page():
    # Set page configuration parameters
    st.markdown(
        textwrap.dedent("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=Inter:wght@300;400;600&display=swap');
        
        .stApp {
            background: radial-gradient(circle at 10% 20%, rgb(15, 23, 42) 0%, rgb(9, 13, 26) 90%);
            color: #f8fafc;
            font-family: 'Inter', sans-serif;
        }

        .hero-title {
            font-family: 'Outfit', sans-serif;
            font-size: 64px;
            font-weight: 800;
            line-height: 1.1;
            text-align: center;
            margin-top: 40px;
            background: linear-gradient(135deg, #ffffff 40%, #86b1f9 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .hero-subtitle {
            font-family: 'Outfit', sans-serif;
            font-size: 20px;
            text-align: center;
            color: #94a3b8;
            margin-bottom: 40px;
        }

        .features-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 24px;
            margin: 50px 0;
        }

        .glass-card {
            background: rgba(30, 41, 59, 0.4);
            border: 1px solid rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(12px);
            border-radius: 16px;
            padding: 30px;
            transition: all 0.3s ease;
            box-shadow: 0 4px 30px rgba(0, 0, 0, 0.2);
        }

        .glass-card:hover {
            transform: translateY(-5px);
            border-color: rgba(99, 102, 241, 0.4);
            box-shadow: 0 10px 30px rgba(99, 102, 241, 0.1);
        }

        .card-number {
            font-family: 'Outfit', sans-serif;
            color: #6366f1;
            font-size: 14px;
            font-weight: 700;
            letter-spacing: 2px;
            margin-bottom: 10px;
        }

        .card-title {
            font-family: 'Outfit', sans-serif;
            font-size: 20px;
            font-weight: 600;
            color: #ffffff;
            margin-bottom: 10px;
        }

        .card-desc {
            font-size: 14px;
            color: #94a3b8;
            line-height: 1.6;
        }

        /* Center columns wrapper */
        .cta-container {
            display: flex;
            justify-content: center;
            gap: 20px;
            margin: 40px 0;
        }

        </style>
        """),
        unsafe_allow_html=True
    )

    # Navbar/Header
    st.markdown(
        """
        <div style="display: flex; justify-content: space-between; align-items: center; padding: 20px 0; border-bottom: 1px solid rgba(255, 255, 255, 0.05); margin-bottom: 30px;">
            <div style="font-family: 'Outfit', sans-serif; font-size: 26px; font-weight: 800; color: white;">
                LUMINA<span style="color:#6366f1;"> RECRUIT</span>
            </div>
            <div style="color: #64748b; font-size: 14px; font-weight: 600;">
                Two-Sided Agentic AI Recruitment Platform
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Hero Title
    st.markdown('<div class="hero-title">Lumina Recruit</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">AI-Powered Recruitment Platform for Modern Tech Talent</div>', unsafe_allow_html=True)

    # CTA Buttons Side-by-Side
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<div style='text-align: right;'>", unsafe_allow_html=True)
        if st.button("🙋‍♂️ I'm Looking for a Job", use_container_width=True, type="primary"):
            st.session_state.page = "auth"
            st.session_state.role = "student"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div style='text-align: left;'>", unsafe_allow_html=True)
        if st.button("💼 I'm Hiring / Managing", use_container_width=True):
            st.session_state.page = "auth"
            st.session_state.role = "recruiter"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)

    # Feature Cards
    st.markdown('<div style="text-align: center; font-family: Outfit; font-size: 32px; font-weight:700; margin-bottom: 10px;">Platform capabilities</div>', unsafe_allow_html=True)
    st.markdown('<div style="text-align: center; color: #94a3b8; margin-bottom: 40px;">Specialized AI agents handling each segment of the hiring pipeline</div>', unsafe_allow_html=True)

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.markdown("""
        <div class="glass-card">
            <div class="card-number">01 / CANDIDATE</div>
            <div class="card-title">Resume Parsing</div>
            <div class="card-desc">Immediate parsing of PDF and DOCX files into structural JSON, saving profile parameters instantly to SQLite database.</div>
        </div>
        """, unsafe_allow_html=True)
    with col_b:
        st.markdown("""
        <div class="glass-card">
            <div class="card-number">02 / RECRUITER</div>
            <div class="card-title">Explainable Matching</div>
            <div class="card-desc">Deterministic score calculations combined with AI agent justifications, highlighting candidates matching precise skill requirements.</div>
        </div>
        """, unsafe_allow_html=True)
    with col_c:
        st.markdown("""
        <div class="glass-card">
            <div class="card-number">03 / ASSESSMENT</div>
            <div class="card-title">Automated Testing</div>
            <div class="card-desc">Aptitude and coding assessments executed inside remote compiler sandbox, compiling results back into candidate ranks automatically.</div>
        </div>
        """, unsafe_allow_html=True)

    # Footer
    st.markdown(
        """
        <div style="text-align: center; color: #475569; font-size: 13px; margin-top: 80px; padding-top: 20px; border-top: 1px solid rgba(255, 255, 255, 0.05);">
            Lumina Recruit © 2026 · Powered by Google Gemini & Agentic Workflow Orchestration
        </div>
        """,
        unsafe_allow_html=True
    )
