<<<<<<< HEAD
from services.llm_service import GeminiService


class JobAgent:
    """
    Job Requirement Extraction Agent.

    Responsibility:
    Convert an unstructured job description
    into structured recruitment requirements.
    """

    def __init__(self):

        self.llm = GeminiService()

    # ========================================================
    # ANALYZE JOB
    # ========================================================

    def analyze(
        self,
        job_description: str,
    ) -> dict:

        if not job_description:
            raise ValueError(
                "Job description cannot be empty."
            )

=======
import json

from langchain_google_genai import ChatGoogleGenerativeAI

from config.settings import GEMINI_MODEL, GEMINI_API_KEY


class JobAgent:

    def __init__(self):

        if not GEMINI_API_KEY:
            raise ValueError(
                "GOOGLE_API_KEY is missing."
            )

        self.llm = ChatGoogleGenerativeAI(
            model=GEMINI_MODEL,
            google_api_key=GEMINI_API_KEY,
            temperature=0,
        )

    def analyze(self, job_description):

>>>>>>> f1fae11c75574876b6ccf36da7b7f706c3e1d458
        prompt = f"""
You are an expert Indian technology recruiter.

<<<<<<< HEAD
Analyze the following job description and extract
structured recruitment requirements.

JOB DESCRIPTION
----------------
{job_description}

Return ONLY valid JSON.

Use exactly this structure:

{{
    "job_title": "",
    "required_skills": [],
    "preferred_skills": [],
    "experience": "",
    "education": [],
    "responsibilities": [],
    "notice_period": "",
    "salary_min_lpa": null,
    "salary_max_lpa": null,
    "location": "",
    "regional_preference": "",
    "relocation_willingness": ""
}}

Rules:

1. required_skills:
   Include skills that are explicitly required.

2. preferred_skills:
   Include optional or preferred skills.

3. experience:
   Extract the required experience exactly as
   reasonably stated.

4. education:
   Include degree or educational requirements.

5. responsibilities:
   Extract the major responsibilities.

6. notice_period:
   Extract the acceptable notice period if present.

7. salary_min_lpa:
   Extract minimum annual salary in Indian LPA.
   Use null if unavailable.

8. salary_max_lpa:
   Extract maximum annual salary in Indian LPA.
   Use null if unavailable.

9. location:
   Extract job location.

10. regional_preference:
    Extract any India-specific regional requirement.

11. relocation_willingness:
    Extract whether relocation is required,
    optional, or not mentioned.

12. Do not invent information.

13. If a value is unavailable, use:
    - ""
    - []
    - null

Return JSON only.
=======
Analyze this job description.

Return ONLY valid JSON with:

title
required_skills
experience_required
education_required
location
min_salary
max_salary
max_notice_period
relocation_required

Rules:
- required_skills must be a list.
- experience_required must be a number.
- salaries are LPA numbers.
- max_notice_period is days.
- Do not invent requirements that are not reasonably present.
- Use null when information is missing.

JOB DESCRIPTION:
{job_description}
>>>>>>> f1fae11c75574876b6ccf36da7b7f706c3e1d458
"""

        result = self.llm.generate_json(
            prompt
        )

<<<<<<< HEAD
        # ----------------------------------------------------
        # Ensure expected fields exist
        # ----------------------------------------------------

        defaults = {
=======
        content = response.content.strip()
>>>>>>> f1fae11c75574876b6ccf36da7b7f706c3e1d458

            "job_title": "",

            "required_skills": [],

            "preferred_skills": [],

            "experience": "",

            "education": [],

            "responsibilities": [],

            "notice_period": "",

            "salary_min_lpa": None,

            "salary_max_lpa": None,

            "location": "",

            "regional_preference": "",

            "relocation_willingness": "",
        }

        for key, default in defaults.items():

            if key not in result:

                result[key] = default

        return result