import sqlite3
import json
import hashlib
from database.db import get_connection

def hash_password(password: str) -> str:
    """Hash password using SHA-256."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def initialize_database():
    """Initializes the database schema for Lumina Recruit."""
    connection = get_connection()
    cursor = connection.cursor()

    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON;")

    # 1. USERS TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('student', 'recruiter')),
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 2. CANDIDATES TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS candidates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER UNIQUE,
        name TEXT NOT NULL,
        email TEXT,
        phone TEXT,
        location TEXT,
        education TEXT DEFAULT '[]', -- JSON list
        college TEXT,
        degree TEXT,
        branch TEXT,
        graduation_year TEXT,
        skills TEXT DEFAULT '[]', -- JSON list
        projects TEXT DEFAULT '[]', -- JSON list
        experience TEXT DEFAULT '[]', -- JSON list
        experience_years REAL DEFAULT 0,
        certifications TEXT DEFAULT '[]', -- JSON list
        notice_period INTEGER DEFAULT 0, -- in days
        expected_salary REAL DEFAULT 0, -- in LPA
        preferred_roles TEXT DEFAULT '[]', -- JSON list
        preferred_locations TEXT DEFAULT '[]', -- JSON list
        relocation INTEGER DEFAULT 0, -- 1 = True, 0 = False
        resume_filename TEXT DEFAULT '',
        resume_text TEXT DEFAULT '',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    """)

    # 3. JOBS TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        required_skills TEXT DEFAULT '[]', -- JSON list
        min_experience REAL DEFAULT 0,
        location TEXT DEFAULT '',
        min_salary REAL DEFAULT 0,
        max_salary REAL DEFAULT 0,
        max_notice_period INTEGER DEFAULT 0,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 4. APPLICATIONS TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS applications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_id INTEGER NOT NULL,
        candidate_id INTEGER NOT NULL,
        match_score REAL DEFAULT 0,
        matching_explanation TEXT DEFAULT '',
        status TEXT DEFAULT 'Applied', -- Applied, Screening, Shortlisted, Assessment, Assessment Completed, Interview, Selected, Rejected
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(job_id, candidate_id),
        FOREIGN KEY(job_id) REFERENCES jobs(id) ON DELETE CASCADE,
        FOREIGN KEY(candidate_id) REFERENCES candidates(id) ON DELETE CASCADE
    );
    """)

    # 5. ASSESSMENTS TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS assessments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        application_id INTEGER NOT NULL,
        type TEXT NOT NULL, -- 'Aptitude' or 'Technical'
        score REAL DEFAULT NULL, -- NULL until completed
        status TEXT DEFAULT 'Pending', -- 'Pending', 'Completed'
        details TEXT DEFAULT '{}', -- JSON results breakdown
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(application_id, type),
        FOREIGN KEY(application_id) REFERENCES applications(id) ON DELETE CASCADE
    );
    """)

    # 6. ASSESSMENT QUESTIONS TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS assessment_questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type TEXT NOT NULL, -- 'Aptitude' or 'Technical'
        question_text TEXT NOT NULL,
        options TEXT DEFAULT '[]', -- JSON list of options for Aptitude
        correct_answer TEXT, -- correct option (e.g. 'A') or exact output string
        code_template TEXT DEFAULT '', -- for coding tasks
        test_cases TEXT DEFAULT '[]', -- JSON list of {"input": "", "output": ""}
        marks INTEGER DEFAULT 1,
        category TEXT DEFAULT '', -- category of question
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 7. ASSESSMENT RESULTS TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS assessment_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        assessment_id INTEGER NOT NULL,
        question_id INTEGER NOT NULL,
        candidate_answer TEXT DEFAULT '',
        is_correct INTEGER DEFAULT 0,
        score REAL DEFAULT 0,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(assessment_id) REFERENCES assessments(id) ON DELETE CASCADE,
        FOREIGN KEY(question_id) REFERENCES assessment_questions(id) ON DELETE CASCADE
    );
    """)

    # 8. MESSAGES TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        application_id INTEGER NOT NULL,
        sender_id INTEGER NOT NULL,
        sender_role TEXT NOT NULL, -- 'student' or 'recruiter'
        message TEXT NOT NULL,
        timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(application_id) REFERENCES applications(id) ON DELETE CASCADE,
        FOREIGN KEY(sender_id) REFERENCES users(id) ON DELETE CASCADE
    );
    """)

    # 9. INTERVIEWS TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS interviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        candidate_id INTEGER NOT NULL,
        job_id INTEGER NOT NULL,
        interview_date TEXT NOT NULL,
        interview_time TEXT NOT NULL,
        mode TEXT NOT NULL, -- 'Online', 'In-person', 'Phone'
        venue_link TEXT DEFAULT '', -- virtual URL or location address
        notes TEXT DEFAULT '',
        status TEXT DEFAULT 'Scheduled', -- 'Scheduled', 'Completed', 'Cancelled'
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(candidate_id) REFERENCES candidates(id) ON DELETE CASCADE,
        FOREIGN KEY(job_id) REFERENCES jobs(id) ON DELETE CASCADE
    );
    """)

    # Seeding question bank
    seed_questions(connection)

    connection.commit()
    connection.close()

def seed_questions(connection):
    """Seed questions into assessment_questions if table is empty."""
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) as count FROM assessment_questions")
    row = cursor.fetchone()
    if row and row[0] > 0:
        # Already seeded
        return

    import os
    from config.settings import BASE_DIR
    
    # 1. Seed Aptitude Questions
    apt_file = BASE_DIR / "data" / "aptitude_questions.json"
    if os.path.exists(apt_file):
        try:
            with open(apt_file, "r") as f:
                questions = json.load(f)
                for q in questions:
                    cursor.execute("""
                        INSERT INTO assessment_questions (type, question_text, options, correct_answer, marks, category)
                        VALUES ('Aptitude', ?, ?, ?, ?, ?)
                    """, (
                        q["question_text"],
                        json.dumps(q.get("options", [])),
                        q.get("correct_answer", ""),
                        int(q.get("marks", 5)),
                        q.get("category", "")
                    ))
            print("Aptitude question bank seeded successfully.")
        except Exception as e:
            print(f"Error seeding aptitude questions: {e}")

    # 2. Seed Technical Questions
    tech_file = BASE_DIR / "data" / "technical_questions.json"
    if os.path.exists(tech_file):
        try:
            with open(tech_file, "r") as f:
                questions = json.load(f)
                for q in questions:
                    cursor.execute("""
                        INSERT INTO assessment_questions (type, question_text, code_template, test_cases, correct_answer, marks, category)
                        VALUES ('Technical', ?, ?, ?, ?, ?, ?)
                    """, (
                        q["question_text"],
                        q.get("code_template", ""),
                        json.dumps(q.get("test_cases", [])),
                        q.get("correct_answer", ""),
                        int(q.get("marks", 10)),
                        q.get("category", "")
                    ))
            print("Technical question bank seeded successfully.")
        except Exception as e:
            print(f"Error seeding technical questions: {e}")

if __name__ == "__main__":
    initialize_database()
    print("Database schema initialized and seeded successfully.")