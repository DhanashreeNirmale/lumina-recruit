import re


def clean_text(text: str) -> str:
    """
    Clean extracted text without destroying useful information.
    """
    if not text:
        return ""

    text = text.replace("\x00", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def normalize_skill(skill: str) -> str:
    """
    Normalize skill names for comparison.
    """
    skill = skill.lower().strip()

    aliases = {
        "react.js": "react",
        "node": "node.js",
        "nodejs": "node.js",
        "postgres": "postgresql",
        "scikit learn": "scikit-learn",
        "ml": "machine learning",
        "dl": "deep learning",
    }

    return aliases.get(skill, skill)


def normalize_skills(skills):
    """
    Normalize and remove duplicate skills.
    """
    result = []

    for skill in skills:
        normalized = normalize_skill(skill)

        if normalized and normalized not in result:
            result.append(normalized)

    return result


def safe_float(value, default=0.0):
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def safe_int(value, default=0):
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return default