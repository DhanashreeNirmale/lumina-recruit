import json
from assessments.judge0 import run_candidate_code
from database.repositories import (
    get_all_questions_by_type,
    complete_assessment,
    add_assessment_result
)

def evaluate_technical_test(assessment_id: int, candidate_codes: dict) -> float:
    """
    Evaluates coding submissions against predefined test cases.
    candidate_codes: dict of {question_id: source_code}
    Returns calculated percentage score (0-100).
    """
    questions = get_all_questions_by_type("Technical")
    if not questions:
        return 0.0
        
    total_marks = 0
    earned_marks = 0
    details = {}
    
    for q in questions:
        q_id = q["id"]
        marks = q["marks"]
        total_marks += marks
        
        source_code = candidate_codes.get(str(q_id), "").strip()
        if not source_code:
            # Not attempted
            add_assessment_result(assessment_id, q_id, "", 0, 0.0)
            details[q_id] = {
                "question": q["question_text"],
                "score": 0.0,
                "passed_cases": 0,
                "total_cases": len(q["test_cases"]),
                "error": "Not attempted"
            }
            continue
            
        test_cases = q["test_cases"]
        passed = 0
        test_results = []
        err_msg = ""
        
        for tc in test_cases:
            tc_input = tc["input"]
            tc_expected = tc["output"]
            
            # Execute code on sandbox compiler
            exec_res = run_candidate_code(
                source_code=source_code,
                language="Python", # Python is standard for candidate portal coding
                stdin=tc_input,
                expected_output=tc_expected
            )
            
            stdout = exec_res.get("stdout", "").strip()
            stderr = exec_res.get("stderr", "").strip()
            compile_output = exec_res.get("compile_output", "").strip()
            status_id = exec_res.get("status_id", 4) # 3 is Accepted
            
            # Match
            is_match = (status_id == 3) or (stdout == tc_expected.strip())
            
            if is_match:
                passed += 1
                
            test_results.append({
                "input": tc_input,
                "expected": tc_expected,
                "stdout": stdout,
                "stderr": stderr,
                "compile_output": compile_output,
                "passed": is_match
            })
            
            if stderr:
                err_msg = stderr
            elif compile_output:
                err_msg = compile_output
                
        # Calculate marks for this question
        question_score = 0.0
        if len(test_cases) > 0:
            question_score = (passed / len(test_cases)) * marks
            
        earned_marks += question_score
        
        details[q_id] = {
            "question": q["question_text"],
            "score": round(question_score, 1),
            "passed_cases": passed,
            "total_cases": len(test_cases),
            "results": test_results,
            "error": err_msg
        }
        
        # Save individual result in DB
        add_assessment_result(
            assessment_id=assessment_id,
            question_id=q_id,
            candidate_answer=source_code,
            is_correct=int(passed == len(test_cases)),
            score=question_score
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
