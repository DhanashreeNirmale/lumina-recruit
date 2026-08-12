from pathlib import Path


def validate_resume_file(uploaded_file):
    """
    Validate Streamlit uploaded resume.
    """

    if uploaded_file is None:
        return False, "Please upload a resume."

    extension = Path(uploaded_file.name).suffix.lower().replace(".", "")

    if extension not in ["pdf", "docx"]:
        return False, "Only PDF and DOCX resumes are supported."

    if uploaded_file.size == 0:
        return False, "The uploaded file is empty."

    # 10 MB limit
    if uploaded_file.size > 10 * 1024 * 1024:
        return False, "Resume size must be below 10 MB."

    return True, "Valid resume."


def validate_job(job):
    """
    Basic job requirement validation.
    """

    if not job:
        return False, "Job information is missing."

    if not job.get("title"):
        return False, "Job title is required."

    if not job.get("required_skills"):
        return False, "At least one required skill is needed."

    return True, "Valid job."