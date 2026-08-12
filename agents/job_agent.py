import json

from langchain_google_genai import ChatGoogleGenerativeAI

from config.settings import GEMINI_MODEL, GOOGLE_API_KEY


class ResumeAgent:

    def __init__(self):

        if not GOOGLE_API_KEY:
            raise ValueError(
                "GOOGLE_API_KEY is missing. "
                "Add it to your .env file."
            )

        self.llm = ChatGoogleGenerativeAI(
            model=GEMINI_MODEL,
            google_api_key=GOOGLE_API_KEY,
            temperature=0,
        )

    def analyze(self, resume_text):

        prompt = f"""
You are an Indian technology recruitment assistant.

Analyze the following resume.

Return ONLY valid JSON with these fields:

name
email
phone
skills
experience
education
college
location
notice_period
expected_salary
relocation

Rules:
- skills must be a JSON list.
- experience must be a number.
- notice_period must be a number of days or null.
- expected_salary must be a number in LPA or null.
- relocation must be true, false, or null.
- Do not invent information.
- If information is missing, use null or an empty string/list.

RESUME:
{resume_text}
"""

        response = self.llm.invoke(prompt)

        content = response.content

        # Gemini normally returns text. Remove markdown fences if present.
        content = content.strip()

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