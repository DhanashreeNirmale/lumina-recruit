<<<<<<< HEAD
import json
import re


def _list(value):

    if isinstance(
        value,
        list
    ):

        return [
            str(x).lower().strip()
            for x in value
            if str(x).strip()
        ]

    try:

        parsed = json.loads(
            value or "[]"
        )

        return [
            str(x).lower().strip()
            for x in parsed
            if str(x).strip()
        ]

    except (
        TypeError,
        json.JSONDecodeError
    ):

        return []


def _contains(
    skill,
    candidate_skill
):

    return (
        skill == candidate_skill
        or skill in candidate_skill
        or candidate_skill in skill
    )


def _extract_days(text):

    match = re.search(
        r"(\d+)",
        str(text or "")
    )

    return (
        int(match.group(1))
        if match
        else None
    )


def score_candidate(
    candidate,
    job
):

    required = _list(
        job.get(
            "required_skills"
        )
    )

    preferred = _list(
        job.get(
            "preferred_skills"
        )
    )

    candidate_skills = _list(
        candidate.get(
            "skills"
        )
    )


    required_hits = sum(

        any(
            _contains(
                skill,
                cs
            )

            for cs in candidate_skills
        )

        for skill in required
    )


    preferred_hits = sum(

        any(
            _contains(
                skill,
                cs
            )

            for cs in candidate_skills
        )

        for skill in preferred
    )


    required_score = (

        55
        * required_hits
        / max(
            1,
            len(required)
        )
    )


    preferred_score = (

        10
        * preferred_hits
        / max(
            1,
            len(preferred)
        )
    )


    education = " ".join(
        _list(
            candidate.get(
                "education"
            )
        )
    )

    education_score = (
        10
        if education
        else 0
    )


    # --------------------------------------------------------
    # NOTICE PERIOD
    # --------------------------------------------------------

    notice_score = 0

    job_notice = _extract_days(
        job.get(
            "notice_period"
        )
    )

    candidate_notice = _extract_days(
        candidate.get(
            "notice_period"
        )
    )

    if (
        job_notice is None
        or candidate_notice is None
        or candidate_notice <= job_notice
    ):

        notice_score = 10


    # --------------------------------------------------------
    # SALARY
    # --------------------------------------------------------

    salary_score = 0

    try:

        expected = float(
            candidate.get(
                "expected_salary"
            ) or 0
        )

        maximum = float(
            job.get(
                "salary_max"
            ) or 0
        )

        if (
            expected == 0
            or maximum == 0
            or expected <= maximum
        ):

            salary_score = 10

    except (
        TypeError,
        ValueError
    ):

        salary_score = 0


    # --------------------------------------------------------
    # LOCATION / RELOCATION
    # --------------------------------------------------------

    location_score = 0

    job_location = str(
        job.get(
            "location",
            ""
        )
    ).lower()

    candidate_location = str(
        candidate.get(
            "location",
            ""
        )
    ).lower()

    relocation = str(
        candidate.get(
            "relocation_willingness",
            ""
        )
    ).lower()


    if (
        not job_location
        or not candidate_location
    ):

        location_score = 0

    elif (
        job_location in candidate_location
        or candidate_location in job_location
    ):

        location_score = 5

    elif (
        "yes" in relocation
        or "willing" in relocation
    ):

        location_score = 5


    total = (

        required_score
        + preferred_score
        + education_score
        + notice_score
        + salary_score
        + location_score
    )


    return round(
        min(
            100.0,
            total
        ),
        2
    )
=======
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
>>>>>>> f1fae11c75574876b6ccf36da7b7f706c3e1d458
