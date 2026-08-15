from services.llm_service import GeminiService


class JobAgent:
    """
    Job Analysis Agent for Lumina Recruit.

    Responsibilities:
    1. Accept a raw job description.
    2. Send it to Gemini through GeminiService.
    3. Extract structured recruitment requirements.
    4. Return the result as a Python dictionary.
    """

    def __init__(self):
        self.llm = GeminiService()

    # ========================================================
    # ANALYZE JOB DESCRIPTION
    # ========================================================

    def analyze(self, job_description: str) -> dict:

        # ----------------------------------------------------
        # Validate input
        # ----------------------------------------------------

        if not job_description:
            raise ValueError(
                "Job description cannot be empty."
            )

        job_description = job_description.strip()

        if len(job_description) < 20:
            raise ValueError(
                "Please provide a more detailed job description."
            )

        # ----------------------------------------------------
        # Gemini prompt
        # ----------------------------------------------------

        prompt = f"""
You are an expert AI recruitment assistant.

Your task is to analyze the following job description
and extract the recruitment requirements.

JOB DESCRIPTION
================

{job_description}

================

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
    "employment_type": "",
    "regional_preference": "",
    "relocation_willingness": ""
}}

Rules:

1. job_title:
   Extract the job title.

2. required_skills:
   Include only skills explicitly required
   or clearly essential for the role.

3. preferred_skills:
   Include optional, preferred or good-to-have skills.

4. experience:
   Extract required years of experience.

5. education:
   Extract required degrees, qualifications
   or educational requirements.

6. responsibilities:
   Extract the major responsibilities
   mentioned in the job description.

7. notice_period:
   Extract the required or preferred notice period.

8. salary_min_lpa:
   Extract the minimum salary in LPA if mentioned.
   Otherwise use null.

9. salary_max_lpa:
   Extract the maximum salary in LPA if mentioned.
   Otherwise use null.

10. location:
    Extract the job location.

11. employment_type:
    Extract whether the role is Full-time,
    Part-time, Internship, Contract, etc.

12. regional_preference:
    Extract any regional/candidate-location
    preference if explicitly mentioned.

13. relocation_willingness:
    Extract whether relocation is required,
    preferred, optional or not mentioned.

14. Never invent information.

15. If information is unavailable:
    - use "" for text
    - use [] for lists
    - use null for numeric values.

Return JSON only.
"""

        # ----------------------------------------------------
        # Call Gemini
        # ----------------------------------------------------

        result = self.llm.generate_json(prompt)

        # ----------------------------------------------------
        # Make sure result is a dictionary
        # ----------------------------------------------------

        if not isinstance(result, dict):
            raise ValueError(
                "Gemini returned an invalid job analysis."
            )

        # ----------------------------------------------------
        # Default structure
        # ----------------------------------------------------

        default_result = {
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
            "employment_type": "",
            "regional_preference": "",
            "relocation_willingness": ""
        }

        # ----------------------------------------------------
        # Fill missing fields
        # ----------------------------------------------------

        for key, default_value in default_result.items():

            if key not in result:
                result[key] = default_value

        # ----------------------------------------------------
        # Ensure list fields are lists
        # ----------------------------------------------------

        list_fields = [
            "required_skills",
            "preferred_skills",
            "education",
            "responsibilities"
        ]

        for field in list_fields:

            if not isinstance(result[field], list):

                if result[field]:
                    result[field] = [str(result[field])]
                else:
                    result[field] = []

        # ----------------------------------------------------
        # Return final structured result
        # ----------------------------------------------------

        return result


# ============================================================
# OPTIONAL HELPER FUNCTION
# ============================================================

def analyze_job(job_description: str) -> dict:
    """
    Convenience function for other parts of the application.
    """

    agent = JobAgent()

    return agent.analyze(job_description)