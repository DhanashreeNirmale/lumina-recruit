import re

from utils.constants import TECH_SKILLS
from utils.helpers import normalize_skills


def extract_job_title(text):
    """
    Extract job title from the job description.
    """

    patterns = [
        r"job title\s*[:\-]\s*(.+)",
        r"position\s*[:\-]\s*(.+)",
        r"role\s*[:\-]\s*(.+)",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            flags=re.IGNORECASE
        )

        if match:
            return match.group(1).strip()

    return "Technology Role"


def extract_required_skills(text):
    """
    Extract technical skills from the job description
    using the controlled skill dictionary.
    """

    if not text:
        return []

    text_lower = text.lower()

    found_skills = []

    for skill in TECH_SKILLS:

        if skill.lower() in text_lower:
            found_skills.append(skill)

    return normalize_skills(found_skills)


def extract_experience_required(text):
    """
    Extract required years of experience.

    Examples:
    2+ years experience
    3 years of experience
    minimum 4 years experience
    """

    patterns = [
        r"(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)\s*(?:of)?\s*experience",

        r"minimum\s*(?:of)?\s*(\d+(?:\.\d+)?)\s*(?:years?|yrs?)",

        r"at least\s*(\d+(?:\.\d+)?)\s*(?:years?|yrs?)",
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


def extract_education_required(text):
    """
    Detect Indian education requirements.
    """

    education_keywords = [
        "b.tech",
        "btech",
        "b.e.",
        "be",
        "m.tech",
        "mtech",
        "mca",
        "bca",
        "b.sc",
        "bsc",
        "m.sc",
        "msc",
        "computer science",
        "information technology",
    ]

    text_lower = text.lower()

    found = []

    for keyword in education_keywords:

        if keyword in text_lower:
            found.append(keyword.upper())

    if not found:
        return ""

    return ", ".join(dict.fromkeys(found))


def extract_location(text):
    """
    Detect common Indian technology hiring locations.
    """

    indian_cities = [
        "Mumbai",
        "Pune",
        "Bangalore",
        "Bengaluru",
        "Hyderabad",
        "Delhi",
        "Delhi NCR",
        "Noida",
        "Gurgaon",
        "Gurugram",
        "Chennai",
        "Kolkata",
        "Ahmedabad",
        "Nagpur",
        "Nashik",
        "Indore",
        "Jaipur",
        "Kochi",
        "Thiruvananthapuram",
        "Chandigarh",
        "Mysore",
        "Mysuru",
    ]

    text_lower = text.lower()

    for city in indian_cities:

        if city.lower() in text_lower:
            return city

    return ""


def extract_salary_range(text):
    """
    Extract salary range in LPA.

    Examples:
    5-10 LPA
    6 to 12 LPA
    salary 8 LPA
    """

    range_patterns = [
        r"(\d+(?:\.\d+)?)\s*(?:-|to)\s*(\d+(?:\.\d+)?)\s*lpa",

        r"(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)\s*lakhs?",
    ]

    for pattern in range_patterns:

        match = re.search(
            pattern,
            text,
            flags=re.IGNORECASE
        )

        if match:

            try:

                return (
                    float(match.group(1)),
                    float(match.group(2))
                )

            except ValueError:
                pass

    # Single salary
    single_pattern = (
        r"(?:salary|ctc|package)"
        r".{0,30}?"
        r"(\d+(?:\.\d+)?)\s*lpa"
    )

    match = re.search(
        single_pattern,
        text,
        flags=re.IGNORECASE
    )

    if match:

        try:

            salary = float(match.group(1))

            return salary, salary

        except ValueError:
            pass

    return None, None


def extract_notice_period(text):
    """
    Extract maximum acceptable notice period.

    Examples:
    notice period up to 30 days
    maximum notice period 60 days
    join within 30 days
    """

    patterns = [
        r"notice\s*period\s*(?:of|up to|max(?:imum)?)?"
        r"\s*[:\-]?\s*(\d+)\s*days?",

        r"join(?:ing)?\s*(?:within|in)"
        r"\s*(\d+)\s*days?",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            flags=re.IGNORECASE
        )

        if match:

            try:
                return int(match.group(1))

            except ValueError:
                pass

    return None


def extract_relocation_requirement(text):
    """
    Detect whether relocation is required.
    """

    text_lower = text.lower()

    required_terms = [
        "willing to relocate",
        "must relocate",
        "relocation required",
        "open to relocation",
    ]

    not_required_terms = [
        "relocation not required",
        "no relocation required",
        "remote",
        "work from home",
    ]

    for term in not_required_terms:

        if term in text_lower:
            return False

    for term in required_terms:

        if term in text_lower:
            return True

    return None


def extract_job(text):
    """
    Main job description extraction function.

    Converts raw job description into structured data
    required by the matching engine.
    """

    min_salary, max_salary = extract_salary_range(text)

    job = {
        "title": extract_job_title(text),

        "required_skills": extract_required_skills(
            text
        ),

        "experience_required":
            extract_experience_required(text),

        "education_required":
            extract_education_required(text),

        "location":
            extract_location(text),

        "min_salary":
            min_salary,

        "max_salary":
            max_salary,

        "max_notice_period":
            extract_notice_period(text),

        "relocation_required":
            extract_relocation_requirement(text),

        "description": text,
    }

    return job