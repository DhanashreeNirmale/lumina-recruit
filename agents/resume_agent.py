from services.llm_service import GeminiService


class ResumeAgent:

    def __init__(self):

        self.llm = GeminiService()

    # ========================================================
    # ANALYZE RESUME
    # ========================================================

    def analyze(self, resume_text):

        if not resume_text or not resume_text.strip():

            raise ValueError(
                "Resume text is empty."
            )

        prompt = f"""
You are an AI resume screening assistant
for Indian technology recruitment.

Analyze the resume carefully.

Return ONLY valid JSON.

Do not return:
- Markdown
- ```json
- explanations
- comments
- extra text

Use exactly this JSON structure:

{{
    "name": "",
    "email": "",
    "phone": "",
    "skills": [],
    "education": [],
    "college": "",
    "university": "",
    "graduation_year": null,
    "cgpa_percentage": "",
    "experience": "",
    "experience_years": 0,
    "notice_period": "",
    "current_ctc": null,
    "expected_salary": null,
    "location": "",
    "preferred_city": "",
    "preferred_state": "",
    "preferred_mode": "",
    "relocation_willingness": "",
    "projects": []
}}

Extraction rules:

1. NAME
Extract the candidate's full name.

2. CONTACT
Extract email and Indian phone number.

3. SKILLS
Extract technical skills such as:
Python, Java, C++, SQL, React, Django,
FastAPI, Node.js, MongoDB, PostgreSQL,
AWS, Docker, Git, Machine Learning, etc.

Do not invent skills.

4. EDUCATION
Extract Indian degrees such as:
B.Tech, BE, M.Tech, MCA, BCA,
B.Sc, M.Sc, Diploma, MBA, etc.

5. COLLEGE
Extract college/institute name if available.

6. UNIVERSITY
Extract university name if available.

7. GRADUATION YEAR
Extract graduation/completion year.

8. CGPA/PERCENTAGE
Extract CGPA or percentage exactly as written.

9. EXPERIENCE
Extract total professional experience.

For a fresher:
"experience": "Fresher"
"experience_years": 0

10. NOTICE PERIOD
Extract notice period.

Examples:

"Immediate" -> "Immediate Joiner"
"15 days" -> "15 Days"
"1 month" -> "30 Days"
"2 months" -> "60 Days"
"3 months" -> "90 Days"

If not mentioned:
""

Do NOT assume a notice period.

11. CURRENT CTC
Extract current CTC.

If written as:

8 LPA -> 800000
8.5 LPA -> 850000
12 LPA -> 1200000

Return annual INR amount.

If unavailable:
null

12. EXPECTED SALARY
Extract expected salary/CTC.

Convert LPA to annual INR.

Example:

10 LPA -> 1000000

If unavailable:
null

13. LOCATION
Extract candidate's current location.

14. PREFERRED LOCATION
Extract preferred city/state if mentioned.

15. WORK MODE
Extract:

Remote
Hybrid
Work From Office

If not mentioned:
""

16. RELOCATION
Extract whether the candidate is willing to relocate.

Use:

"Yes"
"No"
""

If not mentioned, use "".

17. PROJECTS
Extract important projects mentioned in the resume.

Return project names or short descriptions.

IMPORTANT:

- Do not invent information.
- If information is missing, use empty string, empty array, or null as appropriate.
- Preserve factual information from the resume.
- Return valid JSON only.

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