def calculate_match_details(candidate: dict, job: dict) -> dict:
    """
    Calculates detailed matching scores between candidate profile and job requirements.
    Weighting:
      Skills: 40%, Experience: 20%, Education: 10%, Location: 10%, Notice Period: 10%, Salary: 10%
    """
    
    # --------------------------------------------------------
    # 1. Skills (40%)
    # --------------------------------------------------------
    c_skills = [s.strip().lower() for s in candidate.get("skills", [])]
    j_skills = [s.strip().lower() for s in job.get("required_skills", [])]
    
    matched_skills = []
    missing_skills = []
    
    if not j_skills:
        skill_score = 100.0
    else:
        for skill in job.get("required_skills", []):
            normalized = skill.strip().lower()
            # Match substring or exact
            if any(normalized in cs or cs in normalized for cs in c_skills):
                matched_skills.append(skill)
            else:
                missing_skills.append(skill)
        skill_score = (len(matched_skills) / len(j_skills)) * 100.0

    # --------------------------------------------------------
    # 2. Experience (20%)
    # --------------------------------------------------------
    c_exp = float(candidate.get("experience_years", 0.0) or 0.0)
    j_exp = float(job.get("min_experience", 0.0) or 0.0)
    
    if j_exp <= 0:
        experience_score = 100.0
    else:
        experience_score = min(100.0, (c_exp / j_exp) * 100.0)

    # --------------------------------------------------------
    # 3. Education (10%)
    # --------------------------------------------------------
    # Simply check if degree matches standard formats or exists
    c_degree = str(candidate.get("degree", "")).lower()
    c_edu = [str(e).lower() for e in candidate.get("education", [])]
    
    education_score = 0.0
    if c_degree or c_edu:
        # Check if contains engineering / science / tech keywords
        tech_words = ["b.tech", "btech", "m.tech", "mtech", "bca", "mca", "b.sc", "m.sc", "b.e", "be", "computer", "information", "software", "engineering"]
        if any(w in c_degree for w in tech_words) or any(any(w in e for w in tech_words) for e in c_edu):
            education_score = 100.0
        else:
            education_score = 80.0 # general degree
    else:
        education_score = 0.0

    # --------------------------------------------------------
    # 4. Location (10%)
    # --------------------------------------------------------
    j_loc = str(job.get("location", "")).strip().lower()
    c_loc = str(candidate.get("location", "")).strip().lower()
    reloc_willing = bool(candidate.get("relocation", False))
    
    if not j_loc or j_loc in ["remote", "any", "anywhere"]:
        location_score = 100.0
    elif j_loc in c_loc or c_loc in j_loc:
        location_score = 100.0
    elif reloc_willing:
        location_score = 80.0
    else:
        location_score = 20.0

    # --------------------------------------------------------
    # 5. Notice Period (10%)
    # --------------------------------------------------------
    c_np = int(candidate.get("notice_period", 0) or 0)
    j_np = int(job.get("max_notice_period", 0) or 0)
    
    if j_np <= 0 or c_np <= j_np:
        notice_score = 100.0
    else:
        # Deduct 2 points for every day exceeded
        notice_score = max(0.0, 100.0 - float(c_np - j_np) * 2)

    # --------------------------------------------------------
    # 6. Salary (10%)
    # --------------------------------------------------------
    c_sal = float(candidate.get("expected_salary", 0.0) or 0.0)
    j_max_sal = float(job.get("max_salary", 0.0) or 0.0)
    
    if j_max_sal <= 0 or c_sal <= j_max_sal:
        salary_score = 100.0
    else:
        # Deduct percentage exceeded
        diff_pct = ((c_sal - j_max_sal) / j_max_sal) * 100.0
        salary_score = max(0.0, 100.0 - diff_pct)

    # Calculate overall weighted score
    overall_score = (
        (skill_score * 0.40) +
        (experience_score * 0.20) +
        (education_score * 0.10) +
        (location_score * 0.10) +
        (notice_score * 0.10) +
        (salary_score * 0.10)
    )
    
    return {
        "overall_score": round(overall_score, 1),
        "skill_score": round(skill_score, 1),
        "experience_score": round(experience_score, 1),
        "education_score": round(education_score, 1),
        "location_score": round(location_score, 1),
        "notice_score": round(notice_score, 1),
        "salary_score": round(salary_score, 1),
        "matched_skills": matched_skills,
        "missing_skills": missing_skills
    }
