import sqlite3
from pathlib import Path

from config.settings import DATABASE_PATH


def get_connection():
    """
    Create SQLite connection.
    """

    Path(DATABASE_PATH).parent.mkdir(
        parents=True,
        exist_ok=True
    )

    connection = sqlite3.connect(
        DATABASE_PATH,
        check_same_thread=False
    )

    connection.row_factory = sqlite3.Row

    return connection


def initialize_database():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS candidates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            phone TEXT,
            skills TEXT,
            experience REAL,
            education TEXT,
            college TEXT,
            location TEXT,
            notice_period INTEGER,
            expected_salary REAL,
            relocation INTEGER,
            resume_text TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            required_skills TEXT,
            experience_required REAL,
            education_required TEXT,
            location TEXT,
            min_salary REAL,
            max_salary REAL,
            max_notice_period INTEGER,
            relocation_required INTEGER,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            candidate_id INTEGER NOT NULL,
            job_id INTEGER NOT NULL,
            overall_score REAL,
            skill_score REAL,
            experience_score REAL,
            education_score REAL,
            notice_score REAL,
            salary_score REAL,
            location_score REAL,
            recommendation TEXT,
            matched_skills TEXT,
            missing_skills TEXT,
            status TEXT DEFAULT 'Applied',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(candidate_id) REFERENCES candidates(id),
            FOREIGN KEY(job_id) REFERENCES jobs(id)
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS interviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            candidate_id INTEGER NOT NULL,
            job_id INTEGER NOT NULL,
            interview_date TEXT NOT NULL,
            interview_time TEXT NOT NULL,
            interview_type TEXT DEFAULT 'Technical',
            status TEXT DEFAULT 'Scheduled',
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(candidate_id) REFERENCES candidates(id),
            FOREIGN KEY(job_id) REFERENCES jobs(id)
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS assessments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            candidate_id INTEGER NOT NULL,
            job_id INTEGER NOT NULL,
            provider TEXT,
            assessment_name TEXT,
            assessment_url TEXT,
            status TEXT DEFAULT 'Not Sent',
            score REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(candidate_id) REFERENCES candidates(id),
            FOREIGN KEY(job_id) REFERENCES jobs(id)
        )
        """
    )

    connection.commit()
    connection.close()


def execute_query(query, parameters=()):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(query, parameters)

    connection.commit()

    last_id = cursor.lastrowid

    connection.close()

    return last_id


def fetch_all(query, parameters=()):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(query, parameters)

    rows = cursor.fetchall()

    connection.close()

    return [dict(row) for row in rows]


def fetch_one(query, parameters=()):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(query, parameters)

    row = cursor.fetchone()

    connection.close()

    return dict(row) if row else None