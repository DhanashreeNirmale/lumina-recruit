"""
Candidate matching and scoring utilities.

This module compares a candidate's resume information
with the requirements extracted from a job description.
"""


# ============================================================
# TEXT NORMALIZATION
# ============================================================

def _normalize(value):
    """Convert a value into normalized lowercase text."""

    if value is None:
        return ""

    return str(value).strip().lower()


# ============================================================
# LIST NORMALIZATION
# ============================================================

def _to_list(value):
    """Convert a value into a clean list of strings."""

    if value is None:
        return []

    if isinstance(value, list):
        return [
            str(item).strip()
            for item in value
            if str(item).strip()
        ]

    if isinstance(value, str):
        return [
            item.strip()
            for item in value.split(",")
            if item.strip()
        ]

    return [str(value).strip()]


# ============================================================
# SKILL MATCHING
# ============================================================

def match_skills(
    candidate_skills,
    required_skills,
    preferred_skills=None
):
    """
    Compare candidate skills with job requirements.

    Returns:
        dict containing matched and missing skills.
    """

    candidate = {
        _normalize(skill)
        for skill in _to_list(candidate_skills)
    }

    required = _to_list(required_skills)

    preferred = _to_list(preferred_skills)

    matched_required = []
    missing_required = []

    for skill in required:

        normalized = _normalize(skill)

        if normalized in candidate:
            matched_required.append(skill)
        else:
            missing_required.append(skill)

    matched_preferred = []

    for skill in preferred:

        normalized = _normalize(skill)

        if normalized in candidate:
            matched_preferred.append(skill)

    return {
        "matched_required": matched_required,
        "missing_required": missing_required,
        "matched_preferred": matched_preferred
    }


# ============================================================
# SKILL SCORE
# ============================================================

def calculate_skill_score(
    candidate_skills,
    required_skills,
    preferred_skills=None
):
    """
    Calculate skill compatibility score.

    Required skills have higher importance than
    preferred skills.
    """

    required = _to_list(required_skills)

    preferred = _to_list(preferred_skills)

    candidate = {
        _normalize(skill)
        for skill in _to_list(candidate_skills)
    }

    # --------------------------------------------------------
    # Required skills
    # --------------------------------------------------------

    if required:

        required_matches = sum(
            1
            for skill in required
            if _normalize(skill) in candidate
        )

        required_score = (
            required_matches / len(required)
        ) * 80

    else:

        required_score = 80

    # --------------------------------------------------------
    # Preferred skills
    # --------------------------------------------------------

    if preferred:

        preferred_matches = sum(
            1
            for skill in preferred
            if _normalize(skill) in candidate
        )

        preferred_score = (
            preferred_matches / len(preferred)
        ) * 20

    else:

        preferred_score = 20

    return round(
        required_score + preferred_score,
        2
    )


# ============================================================
# EXPERIENCE SCORE
# ============================================================

def calculate_experience_score(
    candidate_experience,
    required_experience
):
    """
    Calculate experience compatibility.

    This function handles simple numeric experience
    values such as:
        2
        2.5
        "2 years"
        "3-5 years"
    """

    try:

        candidate_years = float(
            str(candidate_experience)
            .replace("years", "")
            .replace("year", "")
            .strip()
        )

    except (ValueError, TypeError):

        return 50.0

    try:

        required_text = _normalize(
            required_experience
        )

        # Extract the first number.
        import re

        match = re.search(
            r"\d+(?:\.\d+)?",
            required_text
        )

        if not match:
            return 50.0

        required_years = float(
            match.group()
        )

    except (ValueError, TypeError):

        return 50.0

    if required_years <= 0:
        return 100.0

    if candidate_years >= required_years:
        return 100.0

    score = (
        candidate_years / required_years
    ) * 100

    return round(
        max(0.0, min(100.0, score)),
        2
    )


# ============================================================
# OVERALL CANDIDATE SCORE
# ============================================================

def score_candidate(
    candidate,
    job
):
    """
    Calculate an overall candidate-job compatibility score.

    Parameters
    ----------
    candidate : dict
        Candidate information.

    job : dict
        Job requirement information.

    Returns
    -------
    dict
        Detailed matching result.
    """

    if not isinstance(candidate, dict):
        candidate = {}

    if not isinstance(job, dict):
        job = {}

    # --------------------------------------------------------
    # Candidate skills
    # --------------------------------------------------------

    candidate_skills = candidate.get(
        "skills",
        candidate.get(
            "technical_skills",
            []
        )
    )

    # --------------------------------------------------------
    # Job skills
    # --------------------------------------------------------

    required_skills = job.get(
        "required_skills",
        []
    )

    preferred_skills = job.get(
        "preferred_skills",
        []
    )

    # --------------------------------------------------------
    # Skill matching
    # --------------------------------------------------------

    skill_match = match_skills(
        candidate_skills,
        required_skills,
        preferred_skills
    )

    skill_score = calculate_skill_score(
        candidate_skills,
        required_skills,
        preferred_skills
    )

    # --------------------------------------------------------
    # Experience
    # --------------------------------------------------------

    candidate_experience = candidate.get(
        "experience",
        candidate.get(
            "years_of_experience",
            0
        )
    )

    required_experience = job.get(
        "experience",
        ""
    )

    experience_score = calculate_experience_score(
        candidate_experience,
        required_experience
    )

    # --------------------------------------------------------
    # Overall score
    #
    # Skills = 80%
    # Experience = 20%
    # --------------------------------------------------------

    overall_score = (
        skill_score * 0.80
        +
        experience_score * 0.20
    )

    overall_score = round(
        overall_score,
        2
    )

    # --------------------------------------------------------
    # Recommendation
    # --------------------------------------------------------

    if overall_score >= 80:

        recommendation = "Highly Recommended"

    elif overall_score >= 65:

        recommendation = "Recommended"

    elif overall_score >= 50:

        recommendation = "Consider"

    else:

        recommendation = "Not Recommended"

    # --------------------------------------------------------
    # Final result
    # --------------------------------------------------------

    return {
        "score": overall_score,

        "skill_score": round(
            skill_score,
            2
        ),

        "experience_score": round(
            experience_score,
            2
        ),

        "matched_required_skills":
            skill_match[
                "matched_required"
            ],

        "missing_required_skills":
            skill_match[
                "missing_required"
            ],

        "matched_preferred_skills":
            skill_match[
                "matched_preferred"
            ],

        "recommendation":
            recommendation
    }