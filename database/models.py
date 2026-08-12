import json

from database.database import (
    execute_query,
    fetch_all,
    fetch_one,
)


def save_candidate(candidate):

    query = """
        INSERT INTO candidates (
            name,
            email,
            phone,
            skills,
            experience,
            education,
            college,
            location,
            notice_period,
            expected_salary,
            relocation,
            resume_text
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    return execute_query(
        query,
        (
            candidate.get("name", ""),
            candidate.get("email", ""),
            candidate.get("phone", ""),
            json.dumps(candidate.get("skills", [])),
            candidate.get("experience", 0),
            candidate.get("education", ""),
            candidate.get("college", ""),
            candidate.get("location", ""),
            candidate.get("notice_period"),
            candidate.get("expected_salary"),
            int(bool(candidate.get("relocation")))
            if candidate.get("relocation") is not None
            else None,
            candidate.get("resume_text", ""),
        )
    )


def save_job(job, description=""):

    query = """
        INSERT INTO jobs (
            title,
            required_skills,
            experience_required,
            education_required,
            location,
            min_salary,
            max_salary,
            max_notice_period,
            relocation_required,
            description
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    return execute_query(
        query,
        (
            job.get("title", ""),
            json.dumps(job.get("required_skills", [])),
            job.get("experience_required", 0),
            job.get("education_required", ""),
            job.get("location", ""),
            job.get("min_salary"),
            job.get("max_salary"),
            job.get("max_notice_period"),
            int(bool(job.get("relocation_required")))
            if job.get("relocation_required") is not None
            else None,
            description,
        )
    )


def save_application(candidate_id, job_id, result):

    query = """
        INSERT INTO applications (
            candidate_id,
            job_id,
            overall_score,
            skill_score,
            experience_score,
            education_score,
            notice_score,
            salary_score,
            location_score,
            recommendation,
            matched_skills,
            missing_skills,
            status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    return execute_query(
        query,
        (
            candidate_id,
            job_id,
            result.get("overall_score", 0),
            result.get("skill_score", 0),
            result.get("experience_score", 0),
            result.get("education_score", 0),
            result.get("notice_score", 0),
            result.get("salary_score", 0),
            result.get("location_score", 0),
            result.get("recommendation", ""),
            json.dumps(result.get("matched_skills", [])),
            json.dumps(result.get("missing_skills", [])),
            result.get("recommendation", "Applied"),
        )
    )


def save_interview(
    candidate_id,
    job_id,
    interview_date,
    interview_time,
    interview_type="Technical",
    notes=""
):

    query = """
        INSERT INTO interviews (
            candidate_id,
            job_id,
            interview_date,
            interview_time,
            interview_type,
            notes
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """

    return execute_query(
        query,
        (
            candidate_id,
            job_id,
            interview_date,
            interview_time,
            interview_type,
            notes,
        )
    )


def get_candidates():

    return fetch_all(
        """
        SELECT *
        FROM candidates
        ORDER BY created_at DESC
        """
    )


def get_jobs():

    return fetch_all(
        """
        SELECT *
        FROM jobs
        ORDER BY created_at DESC
        """
    )


def get_applications():

    return fetch_all(
        """
        SELECT
            applications.*,
            candidates.name AS candidate_name,
            candidates.email AS candidate_email,
            jobs.title AS job_title
        FROM applications
        JOIN candidates
            ON candidates.id = applications.candidate_id
        JOIN jobs
            ON jobs.id = applications.job_id
        ORDER BY applications.overall_score DESC
        """
    )


def get_interviews():

    return fetch_all(
        """
        SELECT
            interviews.*,
            candidates.name AS candidate_name,
            jobs.title AS job_title
        FROM interviews
        JOIN candidates
            ON candidates.id = interviews.candidate_id
        JOIN jobs
            ON jobs.id = interviews.job_id
        ORDER BY interview_date, interview_time
        """
    )