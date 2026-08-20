import re
import json
import logging
from services.llm_service import GeminiService
from config.settings import is_gemini_configured
from resume_parser.skills import extract_skills_deterministically

logger = logging.getLogger(__name__)

class ResumeAgent:
    """
    Resume screening agent for Lumina Recruit.
    Parses resume text into a structured JSON schema.
    """

    def __init__(self):
        self.gemini_configured = is_gemini_configured()
        if self.gemini_configured:
            try:
                self.llm = GeminiService()
            except Exception as e:
                logger.error(f"Failed to initialize Gemini Service: {e}")
                self.gemini_configured = False

    def analyze(self, resume_text: str) -> dict:
        """
        Extracts structured information from resume text.
        If Gemini fails or is not configured, falls back to deterministic extraction.
        """
        if not resume_text or not resume_text.strip():
            raise ValueError("Resume text is empty.")

        if self.gemini_configured:
            try:
                return self._analyze_with_gemini(resume_text)
            except Exception as exc:
                logger.warning(f"Gemini resume analysis failed, using fallback: {exc}")
                return self._fallback_analyze(resume_text, warning=str(exc))
        else:
            return self._fallback_analyze(resume_text, warning="Gemini API is not configured.")

    def _analyze_with_gemini(self, resume_text: str) -> dict:
        prompt = f"""
You are an expert AI resume screening assistant.
Analyze the following resume text and extract candidates' profile details into a valid structured JSON format.

RESUME TEXT:
====================
{resume_text}
====================

Your response must be ONLY valid JSON matching this schema exactly. Do not add markdown notes or explanations outside the JSON object.

{{
    "name": "",
    "email": "",
    "phone": "",
    "location": "",
    "education": [],
    "college": "",
    "degree": "",
    "branch": "",
    "graduation_year": "",
    "skills": [],
    "projects": [],
    "experience": [],
    "experience_years": 0.0,
    "certifications": [],
    "notice_period": 0,
    "expected_salary": 0.0,
    "preferred_roles": [],
    "preferred_locations": [],
    "relocation": false
}}

Rules:
1. name: Extract the candidate's full name.
2. email: Extract the candidate's email address.
3. phone: Extract phone number(s).
4. location: Current city/country.
5. education: A list of degrees or schools.
6. college: Primary/latest college/university name.
7. degree: Primary degree (e.g. "B.Tech", "MCA", "MBA").
8. branch: Branch of study (e.g. "Computer Science").
9. graduation_year: Year of graduation (e.g. "2024").
10. skills: A list of technical skills (e.g. ["Python", "SQL"]).
11. projects: List of software project names or descriptions.
12. experience: List of past job roles or descriptions.
13. experience_years: Total years of professional experience as a float.
14. certifications: List of certifications (e.g. "AWS Certified").
15. notice_period: Expected notice period in days as an integer.
16. expected_salary: Expected salary in LPA (Lakhs Per Annum) as a float.
17. preferred_roles: List of roles they are seeking.
18. preferred_locations: List of locations they prefer.
19. relocation: Boolean (true/false) indicating if they are willing to relocate.

Return JSON only.
"""
        result = self.llm.generate_json(prompt)
        
        # Ensure returned object matches expected types/keys
        if not isinstance(result, dict):
            raise ValueError("LLM returned non-dictionary result.")

        return self._normalize_schema(result)

    def _fallback_analyze(self, text: str, warning: str = "") -> dict:
        """Fallback deterministic extractor using regex and word lists."""
        logger.info(f"Executing deterministic resume parsing fallback. Reason: {warning}")

        # Name extraction (first line with text)
        name = "Unknown Candidate"
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        if lines:
            # Clean first line a bit
            first_line = lines[0]
            if len(first_line) < 50 and not any(kwd in first_line.lower() for kwd in ["resume", "curriculum", "cv", "page"]):
                name = first_line

        # Email
        email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
        email = email_match.group(0) if email_match else ""

        # Phone
        phone_match = re.search(r'\+?\d[\d -]{8,12}\d', text)
        phone = phone_match.group(0) if phone_match else ""

        # Skills
        skills = extract_skills_deterministically(text)

        # Experience years
        exp_years = 0.0
        exp_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:years?|yrs?)\s*(?:of\s*)?experience', text, re.IGNORECASE)
        if exp_match:
            try:
                exp_years = float(exp_match.group(1))
            except:
                pass

        # Degree & College
        degree = ""
        college = ""
        for line in lines:
            line_lower = line.lower()
            if any(d in line_lower for d in ["b.tech", "btech", "b.e.", "b.e", "m.tech", "mtech", "bca", "mca", "b.sc", "m.sc", "bba", "mba", "bachelor", "master"]):
                degree_match = re.search(r'(b\.?tech|m\.?tech|b\.?c\.?a|m\.?c\.?a|b\.?sc|m\.?sc|b\.?e\.?|m\.?b\.?a)', line, re.IGNORECASE)
                if degree_match:
                    degree = degree_match.group(1).upper()
            if "college" in line_lower or "university" in line_lower or "institute" in line_lower:
                college = line

        # Notice period
        notice_period = 0
        np_match = re.search(r'(\d+)\s*(?:days?|months?)\s*notice', text, re.IGNORECASE)
        if np_match:
            try:
                val = int(np_match.group(1))
                # Convert months to days
                if "month" in np_match.group(0).lower():
                    notice_period = val * 30
                else:
                    notice_period = val
            except:
                pass

        # Expected Salary
        expected_salary = 0.0
        sal_match = re.search(r'(?:expected|salary|package|ctc)\s*(?:of\s*)?(\d+(?:\.\d+)?)\s*(?:lpa|lakhs)', text, re.IGNORECASE)
        if sal_match:
            try:
                expected_salary = float(sal_match.group(1))
            except:
                pass

        # Location
        location = ""
        loc_words = ["pune", "mumbai", "bangalore", "bengaluru", "hyderabad", "delhi", "noida", "gurgaon", "chennai", "kolkata"]
        for word in loc_words:
            if re.search(r'\b' + word + r'\b', text.lower()):
                location = word.title()
                break

        fallback_result = {
            "name": name,
            "email": email,
            "phone": phone,
            "location": location,
            "education": [degree] if degree else [],
            "college": college,
            "degree": degree,
            "branch": "",
            "graduation_year": "",
            "skills": skills,
            "projects": [],
            "experience": [],
            "experience_years": exp_years,
            "certifications": [],
            "notice_period": notice_period,
            "expected_salary": expected_salary,
            "preferred_roles": [],
            "preferred_locations": [],
            "relocation": False,
            "warning": warning or "Fallback parser activated."
        }

        return fallback_result

    def _normalize_schema(self, data: dict) -> dict:
        """Normalizes schema types to match expected database types."""
        normalized = {}
        normalized["name"] = str(data.get("name", "Unknown Candidate")).strip() or "Unknown Candidate"
        normalized["email"] = str(data.get("email", "")).strip()
        normalized["phone"] = str(data.get("phone", "")).strip()
        normalized["location"] = str(data.get("location", "")).strip()
        
        edu = data.get("education", [])
        normalized["education"] = edu if isinstance(edu, list) else [str(edu)]
        
        normalized["college"] = str(data.get("college", "")).strip()
        normalized["degree"] = str(data.get("degree", "")).strip()
        normalized["branch"] = str(data.get("branch", "")).strip()
        normalized["graduation_year"] = str(data.get("graduation_year", "")).strip()
        
        skills = data.get("skills", [])
        normalized["skills"] = skills if isinstance(skills, list) else [str(skills)]
        
        projects = data.get("projects", [])
        normalized["projects"] = projects if isinstance(projects, list) else [str(projects)]
        
        exp = data.get("experience", [])
        normalized["experience"] = exp if isinstance(exp, list) else [str(exp)]
        
        try:
            normalized["experience_years"] = float(data.get("experience_years", 0.0) or 0.0)
        except:
            normalized["experience_years"] = 0.0
            
        certs = data.get("certifications", [])
        normalized["certifications"] = certs if isinstance(certs, list) else [str(certs)]
        
        try:
            normalized["notice_period"] = int(data.get("notice_period", 0) or 0)
        except:
            normalized["notice_period"] = 0
            
        try:
            normalized["expected_salary"] = float(data.get("expected_salary", 0.0) or 0.0)
        except:
            normalized["expected_salary"] = 0.0
            
        roles = data.get("preferred_roles", [])
        normalized["preferred_roles"] = roles if isinstance(roles, list) else [str(roles)]
        
        locs = data.get("preferred_locations", [])
        normalized["preferred_locations"] = locs if isinstance(locs, list) else [str(locs)]
        
        reloc = data.get("relocation", False)
        if isinstance(reloc, str):
            normalized["relocation"] = reloc.lower() in ["true", "yes", "1"]
        else:
            normalized["relocation"] = bool(reloc)
            
        return normalized