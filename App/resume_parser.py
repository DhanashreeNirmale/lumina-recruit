import os
import re
import spacy
from pypdf import PdfReader
from spacy.matcher import PhraseMatcher

from constants import SKILLS, EDUCATION

nlp = spacy.load("en_core_web_sm")

skill_matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
patterns = [nlp.make_doc(skill) for skill in SKILLS]
skill_matcher.add("SKILLS", patterns)


def extract_text_from_pdf(pdf_input):
    """
    Extract text from PDF.
    Supports both file path and Streamlit uploaded file.
    """
    reader = PdfReader(pdf_input)

    text = ""

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    return text


def extract_email(text):
    pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"

    match = re.search(pattern, text)

    return match.group() if match else None


def extract_phone(text):
    pattern = r"(\+91[\-\s]?)?[6-9]\d{9}"

    match = re.search(pattern, text)

    return match.group() if match else None


def extract_name(text):
    doc = nlp(text)

    for ent in doc.ents:
        if ent.label_ == "PERSON":
            if len(ent.text.split()) >= 2:
                return ent.text

    return None


def extract_skills(text):
    doc = nlp(text)

    matches = skill_matcher(doc)

    skills = set()

    for _, start, end in matches:
        skills.add(doc[start:end].text)

    return sorted(skills)


def extract_education(text):
    found = []

    text = text.lower()

    for degree in EDUCATION:
        if degree.lower() in text:
            found.append(degree)

    return found


def extract_college(text):
    keywords = [
        "college",
        "university",
        "institute",
        "school"
    ]

    for line in text.split("\n"):
        for key in keywords:
            if key.lower() in line.lower():
                return line.strip()

    return None


def extract_experience(text):
    pattern = r'(\d+)\+?\s*(year|years|yr|yrs)'

    match = re.search(pattern, text, re.IGNORECASE)

    if match:
        return match.group()

    return "Fresher"


def extract_projects(text):
    projects = []

    lines = text.split("\n")

    capture = False

    stop_words = [
        "education",
        "experience",
        "skills",
        "certifications",
        "achievement",
        "languages"
    ]

    for line in lines:

        clean = line.strip()

        if clean.lower() == "projects":
            capture = True
            continue

        if capture:

            if clean.lower() in stop_words:
                break

            if clean != "":
                projects.append(clean)

    return projects


def parse_resume(pdf_input):
    text = extract_text_from_pdf(pdf_input)

    data = {
        "name": extract_name(text),
        "email": extract_email(text),
        "phone": extract_phone(text),
        "skills": extract_skills(text),
        "education": extract_education(text),
        "college": extract_college(text),
        "experience": extract_experience(text),
        "projects": extract_projects(text)
    }

    return data


def get_resume_path(folder="Data"):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    folder_path = os.path.join(base_dir, folder)

    if not os.path.exists(folder_path):
        return None

    for file in os.listdir(folder_path):
        if file.lower().endswith(".pdf"):
            return os.path.join(folder_path, file)

    return None


if __name__ == "__main__":

    resume_path = get_resume_path()

    if resume_path is None:
        print("No Resume Found")

    else:
        candidate = parse_resume(resume_path)

        print("\n========== PARSED RESUME ==========\n")

        for key, value in candidate.items():
            print(f"{key.upper()} : {value}")
            
def extract_text_from_docx(docx_input):
    """Extract text from DOCX (Word) file"""
    try:
        from docx import Document
        doc = Document(docx_input)
        text = ""
        for para in doc.paragraphs:
            text += para.text + "\n"
        return text
    except Exception as e:
        return f"Error extracting DOCX: {str(e)}"


def extract_text_from_txt(txt_input):
    """Extract text from TXT file"""
    try:
        return txt_input.getvalue().decode('utf-8')
    except Exception as e:
        return f"Error extracting TXT: {str(e)}"


def extract_text_from_file(file_input):
    """Extract text from any file format (PDF, DOCX, TXT)"""
    filename = file_input.name.lower()
    
    if filename.endswith('.pdf'):
        return extract_text_from_pdf(file_input)
    elif filename.endswith('.docx'):
        return extract_text_from_docx(file_input)
    elif filename.endswith('.txt'):
        return extract_text_from_txt(file_input)
    else:
        return f"Error: Unsupported file format. Please use PDF, DOCX, or TXT"