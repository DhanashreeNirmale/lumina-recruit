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

        prompt = f"""
You are an Indian technology recruitment assistant.

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
"""

        response = self.llm.invoke(prompt)

        content = response.content.strip()

        if content.startswith("```"):
            content = content.replace("```json", "")
            content = content.replace("```", "")
            content = content.strip()

        try:
            return json.loads(content)

        except json.JSONDecodeError:
            return {
                "raw_analysis": content
            }