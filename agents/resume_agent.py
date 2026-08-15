from services.llm_service import GeminiService


class ResumeAgent:

    def __init__(self):

        self.llm = GeminiService()


    def analyze(self, resume_text):

        if not resume_text or not resume_text.strip():

            raise ValueError(
                "Resume text is empty."
            )

        prompt = f"""
You are an AI resume screening assistant
for Indian technology recruitment.

Return ONLY valid JSON.

Use exactly:

{{
    "name": "",
    "email": "",
    "phone": "",
    "skills": [],
    "education": [],
    "experience": "",
    "notice_period": "",
    "expected_salary": null,
    "location": "",
    "relocation_willingness": ""
}}

Extract:

- technical skills
- Indian degrees
- Indian colleges if available
- experience
- notice period
- expected salary in LPA
- location
- relocation willingness

Do not invent information.

RESUME:

{resume_text}
"""

        result = self.llm.generate_json(
            prompt
        )

        if not isinstance(
            result,
            dict
        ):

            raise ValueError(
                "Invalid resume analysis response."
            )

        return result