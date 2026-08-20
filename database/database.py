import sqlite3

from config.settings import DATABASE_PATH

def get_connection():

    connection = sqlite3.connect(
        str(DATABASE_PATH)
    )

    connection.row_factory = sqlite3.Row

    return connection


def initialize_database():

    connection = get_connection()

    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS jobs (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            title TEXT NOT NULL,

            description TEXT NOT NULL,

            required_skills TEXT DEFAULT '[]',

            preferred_skills TEXT DEFAULT '[]',

            experience TEXT DEFAULT '',

            education TEXT DEFAULT '[]',

            notice_period TEXT DEFAULT '',

            salary_min REAL,

            salary_max REAL,

            location TEXT DEFAULT '',

            regional_preference TEXT DEFAULT '',

            relocation_willingness TEXT DEFAULT '',

            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );


        CREATE TABLE IF NOT EXISTS candidates (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            user_id INTEGER NOT NULL,

            name TEXT NOT NULL,

            email TEXT DEFAULT '',

            phone TEXT DEFAULT '',

            resume_filename TEXT DEFAULT '',

            resume_text TEXT DEFAULT '',

            skills TEXT DEFAULT '[]',

            education TEXT DEFAULT '[]',

            experience TEXT DEFAULT '',

            notice_period TEXT DEFAULT '',

            expected_salary REAL,

            location TEXT DEFAULT '',

            relocation_willingness TEXT DEFAULT '',

            score REAL DEFAULT 0,

            status TEXT DEFAULT 'New',

            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );


        CREATE TABLE IF NOT EXISTS assessments (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            candidate_id INTEGER,

            job_id INTEGER,

            score REAL DEFAULT 0,

            status TEXT DEFAULT 'Pending',

            details TEXT DEFAULT '',

            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );


        CREATE TABLE IF NOT EXISTS interviews (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            candidate_id INTEGER,

            job_id INTEGER,

            interview_date TEXT,

            interview_time TEXT,

            mode TEXT,

            notes TEXT DEFAULT '',

            status TEXT DEFAULT 'Scheduled',

            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        """
    )

    connection.commit()

    connection.close()