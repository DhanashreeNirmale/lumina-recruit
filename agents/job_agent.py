import re
import logging
from services.llm_service import GeminiService
from config.settings import is_gemini_configured
from resume_parser.skills import extract_skills_deterministically

logger = logging.getLogger(__name__)

class JobAgent:
    """
    Job Analysis Agent.
    Parses job descriptions into structured requirements JSON.
    """

    def __init__(self):
        self.gemini_configured = is_gemini_configured()
        if self.gemini_configured:
            try:
                self.llm = GeminiService()
            except Exception as e:
                logger.error(f"Failed to initialize Gemini Service: {e}")
                self.gemini_configured = False

    def analyze(self, job_description: str) -> dict:
        """
        Extracts structured job requirements.
        If Gemini is unavailable, falls back to deterministic extraction.
        """
        if not job_description or not job_description.strip():
            raise ValueError("Job description cannot be empty.")

        if self.gemini_configured:
            try:
                return self._analyze_with_gemini(job_description)
            except Exception as exc:
                logger.warning(f"Gemini job analysis failed: {exc}")
                return self._fallback_analyze(job_description, warning=str(exc))
        else:
            return self._fallback_analyze(job_description, warning="Gemini API is not configured.")

    def _analyze_with_gemini(self, jd_text: str) -> dict:
        prompt = f"""
You are an expert recruitment assistant.
Analyze the following job description and extract the key job requirements.

JOB DESCRIPTION:
====================
{jd_text}
====================

Your response must be ONLY valid JSON matching this schema exactly:
{{
    "title": "",
    "required_skills": [],
    "min_experience": 0.0,
    "location": "",
    "min_salary": 0.0,
    "max_salary": 0.0,
    "max_notice_period": 0
}}

Rules:
1. title: Extract the job title.
2. required_skills: List of critical technical/functional skills required.
3. min_experience: Minimum years of experience as a float (e.g. 2.0). If not specified, use 0.0.
4. location: Job location city. If remote/any, specify "Remote".
5. min_salary: Minimum salary in LPA (Lakhs Per Annum) as a float. If not specified, use 0.0.
6. max_salary: Maximum salary in LPA as a float. If not specified, use 0.0.
7. max_notice_period: Maximum acceptable notice period in days as an integer. If not specified, use 0.

Return JSON only.
"""
        result = self.llm.generate_json(prompt)
        
        if not isinstance(result, dict):
            raise ValueError("LLM returned non-dictionary result for job analysis.")

        return self._normalize_schema(result)

    def _fallback_analyze(self, text: str, warning: str = "") -> dict:
        """Deterministic fallback job parser."""
        logger.info(f"Executing deterministic job parsing fallback. Reason: {warning}")

        lines = [line.strip() for line in text.split("\n") if line.strip()]
        title = "Job Position"
        if lines:
            title = lines[0][:100]

        # Skills
        skills = extract_skills_deterministically(text)

        # Experience
        min_exp = 0.0
        exp_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:\+|to|-)?\s*(?:\d+)?\s*(?:years?|yrs?)\s*experience', text, re.IGNORECASE)
        if exp_match:
            try:
                min_exp = float(exp_match.group(1))
            except:
                pass

        # Location
        location = "Remote"
        loc_words = ["pune", "mumbai", "bangalore", "bengaluru", "hyderabad", "delhi", "noida", "gurgaon", "chennai", "kolkata"]
        for word in loc_words:
            if re.search(r'\b' + word + r'\b', text.lower()):
                location = word.title()
                break

        # Salary
        min_sal = 0.0
        max_sal = 0.0
        sal_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:-|to)\s*(\d+(?:\.\d+)?)\s*(?:lpa|lakhs)', text, re.IGNORECASE)
        if sal_match:
            try:
                min_sal = float(sal_match.group(1))
                max_sal = float(sal_match.group(2))
            except:
                pass
        else:
            single_sal = re.search(r'(\d+(?:\.\d+)?)\s*(?:lpa|lakhs)', text, re.IGNORECASE)
            if single_sal:
                try:
                    min_sal = float(single_sal.group(1))
                    max_sal = min_sal
                except:
                    pass

        # Notice period
        max_np = 30
        np_match = re.search(r'(?:notice|np)[^\d]*(\d+)\s*(?:days?)', text, re.IGNORECASE)
        if np_match:
            try:
                max_np = int(np_match.group(1))
            except:
                pass

        return {
            "title": title,
            "required_skills": skills,
            "min_experience": min_exp,
            "location": location,
            "min_salary": min_sal,
            "max_salary": max_sal,
            "max_notice_period": max_np,
            "warning": warning or "Fallback parser activated."
        }

    def _normalize_schema(self, data: dict) -> dict:
        normalized = {}
        normalized["title"] = str(data.get("title", "Untitled Job")).strip() or "Untitled Job"
        
        skills = data.get("required_skills", [])
        normalized["required_skills"] = skills if isinstance(skills, list) else [str(skills)]
        
        try:
            normalized["min_experience"] = float(data.get("min_experience", 0.0) or 0.0)
        except:
            normalized["min_experience"] = 0.0
            
        normalized["location"] = str(data.get("location", "")).strip() or "Remote"
        
        try:
            normalized["min_salary"] = float(data.get("min_salary", 0.0) or 0.0)
        except:
            normalized["min_salary"] = 0.0
            
        try:
            normalized["max_salary"] = float(data.get("max_salary", 0.0) or 0.0)
        except:
            normalized["max_salary"] = 0.0
            
        try:
            normalized["max_notice_period"] = int(data.get("max_notice_period", 0) or 0)
        except:
            normalized["max_notice_period"] = 0
            
        return normalized