from database.models import save_interview


def schedule_interview(
    candidate_id,
    job_id,
    interview_date,
    interview_time,
    interview_type="Technical",
    notes=""
):

    if not interview_date:
        raise ValueError("Interview date is required.")

    if not interview_time:
        raise ValueError("Interview time is required.")

    return save_interview(
        candidate_id=candidate_id,
        job_id=job_id,
        interview_date=str(interview_date),
        interview_time=str(interview_time),
        interview_type=interview_type,
        notes=notes,
    )