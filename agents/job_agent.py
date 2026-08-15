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

        prompt = f"""
You are an expert Indian technology recruiter.

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
"""

        result = self.llm.generate_json(
            prompt
        )

        # ----------------------------------------------------
        # Ensure expected fields exist
        # ----------------------------------------------------

        defaults = {

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