# Lumina Recruit — Agentic AI Recruitment Platform

Lumina Recruit is a two-sided recruitment portal enabling candidates to apply for technical job listings and complete online code compilations, while providing recruiters with structured matches, AI justifications, question bank grading, and conversational query consoles.

---

## Getting Started

### 1. Prerequisites
- Python 3.10+
- A Google Gemini API Key

### 2. Installation
Clone the project and initialize dependencies:
```bash
# Activate virtual environment
venv\Scripts\activate

# Install required libraries
pip install -r requirements.txt
```

### 3. Environment Configuration
Create a `.env` file in the root directory:
```env
GEMINI_API_KEY=AIzaSy...
JUDGE0_API_URL=http://localhost:2358
```

### 4. Database Setup
Initialize the database tables and seed default aptitude/technical questions:
```bash
python -c "import sys; sys.path.append('.'); from database.models import initialize_database; initialize_database()"
```

### 5. Running the Application
Launch the Streamlit dev server:
```bash
streamlit run app.py
```

---

## User Flow Guidelines

### Candidate User Guide
1. Select **I'm Looking for a Job** -> Register a new student account.
2. Go to **Resume & Profile** -> Upload a PDF/DOCX resume file. The resume is immediately parsed into a structured candidate record.
3. Validate and save candidate details (e.g. Expected Salary, Notice Period, Location).
4. Go to **Find Jobs** -> Review listings and click **Apply**.
5. Go to **Assessments** -> Complete assigned Aptitude tests or Code editor challenges.

### Recruiter User Guide
1. Select **I'm Hiring** -> Register/Login as a Recruiter.
2. Go to **Post a Job** -> Write a job description. The job requirements (skills, experience, notice period, location, salary constraints) are immediately parsed.
3. Go to **Overview** -> Review received applications and click **View Detail**.
4. In the Detail view, inspect the parsed candidate, read original resume text, assign assessments, write comments/messages, or schedule interviews.
5. Review applicant rankings sorted by final scores (60% match + 40% assessments).
6. Ask conversational queries in the **Agent Playground** (e.g. *"Show candidates with 2 years of experience"*).
