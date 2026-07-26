SHORTLIST_PROMPT = """
You are an HR assistant.

Generate a professional email for a candidate.

Candidate Name: {name}
Role: {role}
Skills: {skills}

The candidate has been shortlisted.

The email should:
- Congratulate the candidate.
- Mention the role.
- Appreciate their application.
- Tell them that interview details will be shared soon.
- Keep the tone warm and professional.
- Sign as HR Team.

Return only the email.
"""


REJECTION_PROMPT = """
You are an HR assistant.

Generate a polite rejection email.

Candidate Name: {name}
Role: {role}

Requirements:
- Thank them for applying.
- Appreciate their effort.
- Politely inform them they were not selected.
- Encourage future applications.
- Keep the tone respectful and encouraging.

Return only the email.
"""


INTERVIEW_PROMPT = """
Generate an interview invitation email.

Candidate Name: {name}
Role: {role}
Interview Date: {date}
Interview Time: {time}
Meeting Link: {link}

Return only the email.
"""