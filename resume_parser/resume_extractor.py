import re

import spacy

from resume_parser.skills import extract_skills
from utils.helpers import normalize_skills


# Load spaCy once.
try:
    NLP = spacy.load("en_core_web_sm")
except OSError:
    NLP = None


def extract_email(text):
    matches = re.findall(
        r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
        text
    )

    return matches[0] if matches else ""


def extract_phone(text):
    patterns = [
        r"(?:\+91[\s-]?)?[6-9]\d{9}",
        r"(?:\+91[\s-]?)?\d{5}[\s-]\d{5}",
    ]

    for pattern in patterns:
        match = re.search(pattern, text)

        if match:
            return match.group(0)

    return ""


def extract_name(text):
    """
    Use spaCy PERSON entity if available.
    """
    if NLP:
        doc = NLP(text[:5000])

        for entity in doc.ents:
            if entity.label_ == "PERSON":
                return entity.text.strip()

    # Fallback: first non-empty line
    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    return lines[0] if lines else "Unknown Candidate"


def extract_experience(text):
    patterns = [
        r"(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)\s*(?:of)?\s*experience",
        r"experience\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*(?:years?|yrs?)",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            flags=re.IGNORECASE
        )

        if match:
            try:
                return float(match.group(1))
            except ValueError:
                pass

    return 0.0


def extract_notice_period(text):
    text_lower = text.lower()

    if "immediate joiner" in text_lower:
        return 0

    if "immediate joining" in text_lower:
        return 0

    patterns = [
        r"notice period\s*[:\-]?\s*(\d+)\s*days?",
        r"notice\s*[:\-]?\s*(\d+)\s*days?",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text_lower
        )

        if match:
            return int(match.group(1))

    return None


def extract_salary(text):
    """
    Extract rough LPA expectation.
    Example:
    Expected Salary: 8 LPA
    Salary expectation: 10 LPA
    """

    patterns = [
        r"(?:expected salary|salary expectation|ctc|expected ctc)"
        r".{0,30}?(\d+(?:\.\d+)?)\s*lpa",

        r"(\d+(?:\.\d+)?)\s*lpa",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            flags=re.IGNORECASE
        )

        if match:
            try:
                return float(match.group(1))
            except ValueError:
                pass

    return None


def extract_location(text):
    """
    Basic location extraction.
    """
    indian_cities = [
        "mumbai",
        "pune",
        "bangalore",
        "bengaluru",
        "hyderabad",
        "delhi",
        "delhi ncr",
        "noida",
        "gurgaon",
        "gurugram",
        "chennai",
        "kolkata",
        "ahmedabad",
        "nagpur",
        "nashik",
        "indore",
        "jaipur",
        "kochi",
        "thiruvananthapuram",
        "chandigarh",
    ]

    text_lower = text.lower()

    for city in indian_cities:
        if city in text_lower:
            return city.title()

    return ""


def extract_education(text):
    education_keywords = [
        "b.tech",
        "btech",
        "b.e.",
        "be computer",
        "m.tech",
        "mtech",
        "mca",
        "bca",
        "b.sc",
        "bsc",
        "m.sc",
        "msc",
    ]

    text_lower = text.lower()

    for keyword in education_keywords:
        if keyword in text_lower:
            return keyword.upper()

    return ""


def extract_relocation(text):
    text_lower = text.lower()

    positive_terms = [
        "willing to relocate",
        "open to relocation",
        "ready to relocate",
        "relocation preferred",
    ]

    negative_terms = [
        "not willing to relocate",
        "cannot relocate",
        "not open to relocation",
    ]

    if any(term in text_lower for term in negative_terms):
        return False

    if any(term in text_lower for term in positive_terms):
        return True

    return None


def extract_candidate(text: str):
    """
    Main deterministic candidate extractor.
    """

    skills = extract_skills(text)

    candidate = {
        "name": extract_name(text),
        "email": extract_email(text),
        "phone": extract_phone(text),
        "skills": normalize_skills(skills),
        "experience": extract_experience(text),
        "education": extract_education(text),
        "college": "",
        "location": extract_location(text),
        "notice_period": extract_notice_period(text),
        "expected_salary": extract_salary(text),
        "relocation": extract_relocation(text),
        "resume_text": text,
    }

    return candidate