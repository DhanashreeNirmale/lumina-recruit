TECH_SKILLS = [
    "python", "django", "flask", "fastapi", "pandas", "numpy", "scikit-learn",
    "tensorflow", "pytorch", "keras", "javascript", "react", "angular", "vue",
    "nodejs", "express", "java", "spring boot", "hibernate", "c", "c++", "cpp",
    "c#", "dotnet", "asp.net", "go", "golang", "rust", "ruby", "rails", "php",
    "laravel", "sql", "mysql", "postgresql", "sqlite", "mongodb", "redis",
    "cassandra", "aws", "azure", "gcp", "docker", "kubernetes", "jenkins",
    "git", "github", "gitlab", "jira", "html", "css", "bootstrap", "tailwind",
    "typescript", "swift", "kotlin", "flutter", "react native", "selenium",
    "pytest", "unittest", "opencv", "nltk", "spacy", "graphql", "rest api"
]

def extract_skills_deterministically(text: str) -> list:
    """Detect skills from raw text by matching against a keyword list."""
    if not text:
        return []
    normalized_text = text.lower()
    found_skills = []
    for skill in TECH_SKILLS:
        # Simple word boundaries matching
        import re
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, normalized_text):
            found_skills.append(skill.title())
    return list(set(found_skills))
