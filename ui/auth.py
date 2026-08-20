import streamlit as st
from database.repositories import verify_user, create_user, get_candidate_by_user_id, create_or_update_candidate

def show_auth_page():
    role = st.session_state.get("role", "student")
    role_label = "Student / Candidate" if role == "student" else "Recruiter / Hiring Authority"

    st.markdown(
        """
        <style>
        .auth-container {
            max-width: 480px;
            margin: 60px auto;
            background: rgba(30, 41, 59, 0.5);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 16px;
            padding: 40px;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        }
        .auth-title {
            font-family: 'Outfit', sans-serif;
            font-size: 28px;
            font-weight: 700;
            text-align: center;
            margin-bottom: 20px;
            color: #ffffff;
        }
        .auth-subtitle {
            text-align: center;
            color: #94a3b8;
            font-size: 14px;
            margin-bottom: 30px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown(f"""
    <div class="auth-container">
        <div class="auth-title">Lumina Recruit Authentication</div>
        <div class="auth-subtitle">Accessing portal as <b>{role_label}</b></div>
    </div>
    """, unsafe_allow_html=True)

    # Let's use clean Streamlit columns to center our form
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        tab1, tab2 = st.tabs([" Login", " Register"])

        with tab1:
            login_username = st.text_input("Username / Email", key="login_user").strip()
            login_password = st.text_input("Password", type="password", key="login_pass").strip()

            if st.button("Sign In", type="primary", use_container_width=True):
                if not login_username or not login_password:
                    st.error("Please fill in all fields.")
                else:
                    user = verify_user(login_username, login_password)
                    
                    print("LOGIN USER:", user)
                    
                    if user:
                        if user['role'] != role:
                            st.error(f"Account exists but is registered as a {user['role']}. Please authenticate as {user['role']}.")
                        else:
                            st.session_state.user = user
                            st.session_state.page = "student_dashboard" if role == "student" else "recruiter_dashboard"
                            
                            # If student, ensure candidate row exists
                            if role == "student":
                                candidate = get_candidate_by_user_id(user['id'])
                                if not candidate:
                                    # Create default candidate profile
                                    create_or_update_candidate(user['id'], {
                                        "name": user['username'],
                                        "email": user['username'] if "@" in user['username'] else ""
                                    })
                            st.success("Successfully logged in!")
                            st.rerun()
                    else:
                        st.error("Invalid username or password.")

        with tab2:
            reg_username = st.text_input("Choose Username / Email", key="reg_user").strip()
            reg_password = st.text_input("Choose Password", type="password", key="reg_pass").strip()
            confirm_password = st.text_input("Confirm Password", type="password", key="reg_pass_conf").strip()

            if st.button("Sign Up", type="primary", use_container_width=True):
                if not reg_username or not reg_password:
                    st.error("Please fill in all fields.")
                elif reg_password != confirm_password:
                    st.error("Passwords do not match.")
                elif len(reg_password) < 6:
                    st.error("Password must be at least 6 characters.")
                else:
                    # Create user
                    user_id = create_user(reg_username, reg_password, role)
                    if user_id:
                        st.success("Registration successful! Please login above.")
                        # Auto login or switch to login tab
                    else:
                        st.error("Username is already taken.")

        # Navigation back
        st.write("")
        if st.button("Back to Landing Page", use_container_width=True):
            st.session_state.page = "landing"
            st.session_state.pop("role", None)
            st.rerun()
