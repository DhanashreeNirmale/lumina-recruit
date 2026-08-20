import json
from database.repositories import (
    get_all_questions_by_type,
    complete_assessment,
    add_assessment_result
)

def evaluate_aptitude_test(assessment_id: int, candidate_answers: dict) -> float:
    """
    Evaluates candidate MCQ answers against database/JSON questions.
    candidate_answers: dict of {question_id: selected_option}
    Returns calculated percentage score (0-100).
    """
    # Load all aptitude questions
    questions = get_all_questions_by_type("Aptitude")
    if not questions:
        return 0.0
        
    total_marks = 0
    earned_marks = 0
    details = {}
    
    for q in questions:
        q_id = q["id"]
        correct = q["correct_answer"]
        marks = q["marks"]
        total_marks += marks
        
        selected = candidate_answers.get(str(q_id), "").strip().upper()
        # Clean answer to check letter only (e.g. if option is "A) 60 km/hr", match "A")
        correct_letter = correct.strip().upper()[0] if correct else ""
        selected_letter = selected[0] if selected else ""
        
        is_correct = (selected_letter == correct_letter)
        score = marks if is_correct else 0
        earned_marks += score
        
        details[q_id] = {
            "question": q["question_text"],
            "selected": selected,
            "correct": correct,
            "is_correct": is_correct,
            "score": score
        }
        
        # Save individual result in DB
        add_assessment_result(
            assessment_id=assessment_id,
            question_id=q_id,
            candidate_answer=selected,
            is_correct=is_correct,
            score=score
        )
        
    final_percentage = (earned_marks / total_marks) * 100.0 if total_marks > 0 else 0.0
    final_percentage = round(final_percentage, 1)
    
    # Update main assessment record
    complete_assessment(
        assessment_id=assessment_id,
        score=final_percentage,
        details_dict=details
    )
    
    return final_percentage
