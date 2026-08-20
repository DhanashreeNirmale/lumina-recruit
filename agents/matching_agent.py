import logging
from matching.scorer import calculate_match_details
from services.llm_service import GeminiService
from config.settings import is_gemini_configured

logger = logging.getLogger(__name__)

class MatchingAgent:
    """
    Matching Agent.
    Compares candidate profile details against job requirements to calculate compatibility.
    """

    def __init__(self):
        self.gemini_configured = is_gemini_configured()
        if self.gemini_configured:
            try:
                self.llm = GeminiService()
            except Exception as e:
                logger.error(f"Failed to initialize Gemini Service: {e}")
                self.gemini_configured = False

    def evaluate(self, candidate: dict, job: dict) -> dict:
        """
        Calculates compatibility score and generates an explanation report.
        """
        # Calculate scores deterministically
        match_report = calculate_match_details(candidate, job)
        
        # Generate explanation narrative
        if self.gemini_configured:
            try:
                match_report["explanation"] = self._generate_explanation(candidate, job, match_report)
            except Exception as exc:
                logger.warning(f"Gemini match explanation failed: {exc}")
                match_report["explanation"] = self._fallback_explanation(match_report)
        else:
            match_report["explanation"] = self._fallback_explanation(match_report)
            
        return match_report

    def _generate_explanation(self, candidate: dict, job: dict, scores: dict) -> str:
        prompt = f"""
You are an expert AI talent recruiter.
Provide a professional, concise explanation of the compatibility score between this candidate and job.

CANDIDATE DETAILS:
- Name: {candidate.get('name')}
- Skills: {candidate.get('skills')}
- Experience: {candidate.get('experience_years')} years
- Education: {candidate.get('degree') or candidate.get('education')}
- Location: {candidate.get('location')} (Relocation: {candidate.get('relocation')})
- Notice Period: {candidate.get('notice_period')} days
- Expected Salary: {candidate.get('expected_salary')} LPA

JOB REQUIREMENTS:
- Title: {job.get('title')}
- Required Skills: {job.get('required_skills')}
- Experience Needed: {job.get('min_experience')} years
- Location: {job.get('location')}
- Max Notice Period: {job.get('max_notice_period')} days
- Max Salary: {job.get('max_salary')} LPA

CALCULATED SCORES:
- Overall Compatibility: {scores['overall_score']}%
- Skill Score: {scores['skill_score']}%
- Experience Score: {scores['experience_score']}%
- Location Score: {scores['location_score']}%
- Notice Period Score: {scores['notice_score']}%
- Salary Score: {scores['salary_score']}%

Provide a bulleted summary of:
1. Key Strengths (aligned skills, experience surplus, proximity).
2. Major Gaps (missing required skills, excessive notice period, salary mismatch).
3. Final Hiring Recommendation.

Write in a professional tone, keeping it under 250 words.
"""
        return self.llm.generate(prompt)

    def _fallback_explanation(self, scores: dict) -> str:
        matched = ", ".join(scores.get("matched_skills", [])) or "None"
        missing = ", ".join(scores.get("missing_skills", [])) or "None"
        
        explanation = f"""### Match Analysis (Deterministic Fallback)

- **Overall Match Score:** {scores['overall_score']}%
- **Matched Skills:** {matched}
- **Missing Skills:** {missing}
- **Experience Score:** {scores['experience_score']}%
- **Location Score:** {scores['location_score']}%
- **Notice Period Score:** {scores['notice_score']}%
- **Salary Score:** {scores['salary_score']}%

*Recommendation:* Candidate matches {scores['skill_score']}% of required skills and has an experience rating of {scores['experience_score']}%. Review details to decide on proceeding to assessments.
"""
        return explanation