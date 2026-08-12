from matching.scorer import (
    calculate_skill_score,
    calculate_experience_score,
    calculate_education_score,
    calculate_notice_score,
    calculate_salary_score,
    calculate_location_score,
    calculate_overall_score,
)


def match_candidate(candidate, job):

    skill_score = calculate_skill_score(
        candidate.get("skills", []),
        job.get("required_skills", [])
    )

    experience_score = calculate_experience_score(
        candidate.get("experience", 0),
        job.get("experience_required", 0)
    )

    education_score = calculate_education_score(
        candidate.get("education", ""),
        job.get("education_required", "")
    )

    notice_score = calculate_notice_score(
        candidate.get("notice_period"),
        job.get("max_notice_period")
    )

    salary_score = calculate_salary_score(
        candidate.get("expected_salary"),
        job.get("min_salary"),
        job.get("max_salary")
    )

    location_score = calculate_location_score(
        candidate.get("location", ""),
        job.get("location", ""),
        candidate.get("relocation")
    )

    overall = calculate_overall_score(
        skill_score,
        experience_score,
        education_score,
        notice_score,
        salary_score,
        location_score
    )

    required_skills = set(
        skill.lower()
        for skill in job.get("required_skills", [])
    )

    candidate_skills = set(
        skill.lower()
        for skill in candidate.get("skills", [])
    )

    missing_skills = sorted(
        required_skills - candidate_skills
    )

    matched_skills = sorted(
        required_skills.intersection(candidate_skills)
    )

    if overall >= 80:
        recommendation = "Shortlisted"
    elif overall >= 65:
        recommendation = "Review"
    else:
        recommendation = "Not Shortlisted"

    return {
        "skill_score": round(skill_score, 2),
        "experience_score": round(experience_score, 2),
        "education_score": round(education_score, 2),
        "notice_score": round(notice_score, 2),
        "salary_score": round(salary_score, 2),
        "location_score": round(location_score, 2),
        "overall_score": overall,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "recommendation": recommendation,
    }