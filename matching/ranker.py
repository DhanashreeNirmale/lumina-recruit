from database.repositories import get_assessments_by_application

def calculate_final_score(match_score: float, aptitude_score: float, technical_score: float) -> float:
    """
    Computes final candidate score based on:
      Final Score = (0.60 * Match Score) + (0.40 * Assessment Score)
      Assessment Score = (0.30 * Aptitude Score) + (0.70 * Technical Score)
    """
    # Use 0 if a score is None (not attempted)
    apt = float(aptitude_score if aptitude_score is not None else 0.0)
    tech = float(technical_score if technical_score is not None else 0.0)
    
    assessment_score = (0.30 * apt) + (0.70 * tech)
    final_score = (0.60 * float(match_score)) + (0.40 * assessment_score)
    return round(final_score, 2)

def rank_candidates_for_job(job_id: int, applications: list) -> list:
    """
    Processes a list of applications for a job, loading their assessments
    and ranking them by final score.
    """
    ranked_list = []
    for app in applications:
        # Load assessments for this application
        assessments = get_assessments_by_application(app['id'])
        
        aptitude_score = 0.0
        technical_score = 0.0
        
        for asm in assessments:
            if asm['type'] == 'Aptitude' and asm['score'] is not None:
                aptitude_score = asm['score']
            elif asm['type'] == 'Technical' and asm['score'] is not None:
                technical_score = asm['score']
                
        final_score = calculate_final_score(app['match_score'], aptitude_score, technical_score)
        
        ranked_list.append({
            "application_id": app['id'],
            "candidate_id": app['candidate_id'],
            "candidate_name": app['candidate_name'],
            "match_score": app['match_score'],
            "aptitude_score": aptitude_score,
            "technical_score": technical_score,
            "assessment_score": round((0.30 * aptitude_score) + (0.70 * technical_score), 2),
            "final_score": final_score,
            "status": app['status']
        })
        
    # Sort descending by final score
    ranked_list.sort(key=lambda x: x['final_score'], reverse=True)
    return ranked_list
