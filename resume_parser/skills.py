from utils.constants import TECH_SKILLS
from utils.helpers import normalize_skills


def extract_skills(text: str):
    """
    Extract technical skills using a controlled skill dictionary.

    This provides deterministic matching. The LLM can later
    supplement the extracted information.
    """

    if not text:
        return []

    text_lower = text.lower()

    found = []

    for skill in TECH_SKILLS:

        # Simple phrase matching.
        if skill.lower() in text_lower:
            found.append(skill)

    return normalize_skills(found)