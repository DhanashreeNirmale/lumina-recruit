import streamlit as st

from utils.pdf_reader import read_pdf
from ai.chatbot import ask_resume

st.set_page_config(page_title="Recruiter AI Agent")

st.title("🤖 Recruiter AI Agent")

uploaded_file = st.file_uploader(
    "Upload Resume",
    type=["pdf"]
)

if uploaded_file:

    resume = read_pdf(uploaded_file)

    st.success("Resume Uploaded!")

    question = st.text_input(
        "Ask a question about the candidate"
    )

    if st.button("Ask"):

        answer = ask_resume(
            question,
            resume
        )

        st.subheader("Answer")

        st.write(answer)