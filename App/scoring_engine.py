from constants import SKILLS


def extract_job_skills(job_description):

    job_text = job_description.lower()

    found_skills = []

    for skill in SKILLS:

        if skill.lower() in job_text:

            found_skills.append(skill)

    return sorted(list(set(found_skills)))


def calculate_score(resume_skills, job_skills):

    if not job_skills:

        return {
            "score": 0,
            "matched_skills": [],
            "missing_skills": [],
            "extra_skills": resume_skills,
            "total_required": 0,
            "total_matched": 0,
            "message": "No Job Requirements Found"
        }

    resume_lower = [skill.lower() for skill in resume_skills]

    job_lower = [skill.lower() for skill in job_skills]

    matched = []

    missing = []

    extra = []

    for skill in job_skills:

        if skill.lower() in resume_lower:

            matched.append(skill)

        else:

            missing.append(skill)

    for skill in resume_skills:

        if skill.lower() not in job_lower:

            extra.append(skill)

    score = round((len(matched) / len(job_skills)) * 100, 2)

    return {

        "score": score,

        "matched_skills": matched,

        "missing_skills": missing,

        "extra_skills": extra,

        "total_required": len(job_skills),

        "total_matched": len(matched)

    }


def get_score_interpretation(score):

    if score >= 80:

        return "Excellent Match", "green"

    elif score >= 60:

        return "Good Match", "orange"

    elif score >= 40:

        return "Average Match", "yellow"

    else:

        return "Poor Match", "red"

        