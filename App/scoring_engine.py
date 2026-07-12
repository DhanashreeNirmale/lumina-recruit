"""Scoring Engine to calculate candidate match against job requirements"""

from resume_parser import SKILLS_LIST

def extract_job_skills(job_description):
    job_text_lower = job_description.lower()
    found_skills = []
    
    for skill in SKILLS_LIST:
        if skill.lower() in job_text_lower:
            found_skills.append(skill)
            
    return found_skills

def calculate_score(resume_skills, job_skills):
    if not job_skills:
        return{
            'score' : 0,
            'matched_skills' : [],
            'missing_skills' : [],
            'extra_skills' : resume_skills,
            'message' : 'No job requirements provided'
        }
        
    resume_skills_lower = [s.lower() for s in resume_skills]
    job_skills_lower = [s.lower() for s in job_skills]
    
    matched = [skill for skill in job_skills 
               if skill.lower() in resume_skills_lower]
    
    missing = [skill for skill in job_skills
               if skill.lower() not in resume_skills_lower]
    
    extra = [skill for skill in resume_skills
             if skill.lower() not in job_skills_lower]
    
    if len(job_skills)>0:
        score = (len(matched) / len(job_skills)) *100
    else :
        score = 0
        
    score = round(score,2)
    
    return {
        'score': score,
        'matched_skills': matched,
        'missing_skills': missing,
        'extra_skills': extra,
        'total_required': len(job_skills),
        'total_matched': len(matched)
    }
    
def get_score_interpretation(score):
    """Return interpretation and color for score"""
    if score >= 80:
        return "Excellent Match", "green"
    elif score >= 60:
        return "Good Match", "orange"
    elif score >= 40:
        return "Moderate Match", "yellow"
    else:
        return "Poor Match", "red"
    

        