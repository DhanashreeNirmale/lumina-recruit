import os
import re
import spacy
from pypdf import PdfReader

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# Skills list
SKILLS_LIST = [
    "Python", "Java", "JavaScript", "TypeScript", "C++", "C#", "PHP", "Ruby", "Go", "Rust",
    "React", "Angular", "Vue.js", "Node.js", "Express", "Django", "Flask", "FastAPI",
    "AWS", "Azure", "GCP", "Docker", "Kubernetes", "Jenkins", "GitLab CI", "GitHub Actions",
    "SQL", "MySQL", "PostgreSQL", "MongoDB", "Redis", "Firebase", "DynamoDB",
    "Machine Learning", "Deep Learning", "Data Science", "TensorFlow", "PyTorch", "Pandas", "NumPy",
    "Git", "Linux", "Windows", "MacOS", "Unix",
    "Excel", "Tableau", "Power BI", "Looker",
    "REST API", "GraphQL", "WebSocket", "SOAP",
    "HTML", "CSS", "Bootstrap", "Tailwind",
    "Agile", "Scrum", "Kanban", "JIRA", "Confluence",
    "AWS Lambda", "AWS S3", "AWS EC2", "AWS RDS",
    "Google Cloud Platform", "BigQuery", "Dataflow",
    "Azure VM", "Azure SQL", "Azure DevOps",
    "Elasticsearch", "Kafka", "RabbitMQ",
    "Microservices", "Serverless", "Cloud Computing",
    "OOP", "Functional Programming", "Design Patterns",
    "Unit Testing", "Integration Testing", "Pytest",
    "CI/CD", "DevOps", "Infrastructure as Code",
    "Figma", "Adobe XD", "Sketch",
    "Salesforce", "SAP", "Oracle"
]


def extract_email(text):
    """Extract email from text using regex"""
    match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
    return match.group(0) if match else None


def extract_phone(text):
    """Extract phone number from text using regex"""
    match = re.search(r"(\+?\d{1,3}[-.\s]?)?\d{10}", text)
    return match.group(0) if match else None


def extract_name_and_orgs(text):
    """Extract names and organizations using spaCy NER"""
    doc = nlp(text)
    names = [ent.text for ent in doc.ents if ent.label_ == "PERSON"]
    orgs = [ent.text for ent in doc.ents if ent.label_ == "ORG"]
    return names, orgs


def extract_skills(text):
    """Extract skills from text by matching against SKILLS_LIST"""
    found_skills = []
    text_lower = text.lower()
    for skill in SKILLS_LIST:
        if skill.lower() in text_lower:
            found_skills.append(skill)
    return found_skills


def extract_text_from_pdf(pdf_input):
    """
    Extract text from PDF file.
    Works with both file paths (str) and Streamlit file objects.
    """
    try:
        reader = PdfReader(pdf_input)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text
    except Exception as e:
        return f"Error extracting PDF: {str(e)}"


def extract_keywords(text):
    """Extract all candidate information from resume text"""
    email = extract_email(text)
    phone = extract_phone(text)
    names, orgs = extract_name_and_orgs(text)
    skills = extract_skills(text)

    return {
        "email": email,
        "phone": phone,
        "names_detected": names,
        "organizations_detected": orgs,
        "skills": skills,
    }


def get_resume_path(data="Data"):
    """Find resume PDF in the Data folder"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    full_data_dir = os.path.join(base_dir, data)
    
    for file in os.listdir(full_data_dir):
        if file.lower().endswith(".pdf"):
            return os.path.join(full_data_dir, file)
    return None


if __name__ == "__main__":
    resume_path = get_resume_path()
    if resume_path is None:
        print("No Resume in Data folder. Please add a resume PDF.")
    else: 
        print(f"Found resume: {resume_path}\n")
        
        resume_text = extract_text_from_pdf(resume_path)     
        print("----- RESUME CONTENT -----\n")
        print(resume_text)
        print("\n----- END -----")