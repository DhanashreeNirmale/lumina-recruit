from utils.helpers import normalize_skills


def calculate_skill_score(
    candidate_skills,
    required_skills
):
    candidate = set(
        normalize_skills(candidate_skills)
    )

    required = set(
        normalize_skills(required_skills)
    )

    if not required:
        return 0.0

    matched = candidate.intersection(required)

    return (len(matched) / len(required)) * 100


def calculate_experience_score(
    candidate_experience,
    required_experience
):
    if not required_experience:
        return 100.0

    if candidate_experience >= required_experience:
        return 100.0

    return min(
        (candidate_experience / required_experience) * 100,
        100
    )


def calculate_education_score(
    candidate_education,
    required_education
):
    if not required_education:
        return 100.0

    if not candidate_education:
        return 0.0

    candidate = candidate_education.lower()
    required = required_education.lower()

    if required in candidate or candidate in required:
        return 100.0

    # Indian engineering degree fallback.
    if (
        "b.tech" in candidate
        and "engineering" in required
    ):
        return 100.0

    return 50.0


def calculate_notice_score(
    candidate_notice,
    max_notice
):
    if max_notice is None:
        return 100.0

    if candidate_notice is None:
        return 50.0

    if candidate_notice <= max_notice:
        return 100.0

    # Gradually reduce score.
    difference = candidate_notice - max_notice

    return max(
        0.0,
        100 - difference
    )


def calculate_salary_score(
    candidate_salary,
    min_salary,
    max_salary
):
    if candidate_salary is None:
        return 50.0

    if min_salary is None and max_salary is None:
        return 100.0

    if (
        min_salary is not None
        and candidate_salary < min_salary
    ):
        return 70.0

    if (
        max_salary is not None
        and candidate_salary > max_salary
    ):
        difference = candidate_salary - max_salary

        return max(
            0.0,
            100 - difference * 10
        )

    return 100.0


def calculate_location_score(
    candidate_location,
    job_location,
    relocation
):
    if not job_location:
        return 100.0

    if not candidate_location:
        return 50.0

    if candidate_location.lower() == job_location.lower():
        return 100.0

    if relocation is True:
        return 80.0

    if relocation is False:
        return 30.0

    return 50.0


def calculate_overall_score(
    skill_score,
    experience_score,
    education_score,
    notice_score,
    salary_score,
    location_score
):
    """
    Transparent weighted score.

    Skills       40%
    Experience  20%
    Education   10%
    Notice      10%
    Salary      10%
    Location    10%
    """

    score = (
        skill_score * 0.40
        + experience_score * 0.20
        + education_score * 0.10
        + notice_score * 0.10
        + salary_score * 0.10
        + location_score * 0.10
    )

    return round(score, 2)