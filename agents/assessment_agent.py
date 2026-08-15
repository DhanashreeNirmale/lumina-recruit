from services.llm_service import GeminiService


class AssessmentAgent:

    def __init__(self):

        self.llm = GeminiService()


    def generate_questions(
        self,
        job,
        count=3
    ):

        prompt = f"""
Create {count} programming questions
for this Indian technology job.

Return ONLY JSON.

Format:

{{
    "questions": [
        {{
            "id": 1,
            "title": "",
            "description": "",
            "language": "Python",
            "sample_input": "",
            "sample_output": "",
            "test_cases": [
                {{
                    "input": "",
                    "output": ""
                }}
            ]
        }}
    ]
}}

Rules:

- Programming questions only.
- Deterministic test cases.
- Suitable for Python, Java or C++.
- No external libraries.
- Do not provide solutions.

JOB:

{job}
"""

        return self.llm.generate_json(
            prompt
        )