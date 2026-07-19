import os
import sqlite3
import json
from datetime import datetime

DATABASE_PATH = "resume_screening.db"

def init_database():
    """Initialise the database with required tables"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS screenings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            candidate_name TEXT,
            email TEXT,
            phone TEXT,
            resume_text TEXT,
            job_description TEXT,
            score REAL,
            matched_skills TEXT,
            missing_skills TEXT,
            extra_skills TEXT,
            total_required INTEGER,
            total_matched INTEGER,
            screening_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create interviews table (NEW!)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS interviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            screening_id INTEGER,
            candidate_name TEXT,
            candidate_email TEXT,
            interview_date TEXT,
            interview_time TEXT,
            interviewer_email TEXT,
            status TEXT DEFAULT 'Scheduled',
            notes TEXT,
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (screening_id) REFERENCES screenings(id)
        )
    """)
    
    conn.commit()
    conn.close()
    
def save_screening_result(
    candidate_name, 
    email, 
    phone, 
    resume_text, 
    job_description, 
    score_data
):
    """
    Save screening result to database
    
    Args:
        candidate_name (str): Candidate name
        email (str): Candidate email
        phone (str): Candidate phone
        resume_text (str): Full resume text
        job_description (str): Job description
        score_data (dict): Score data from scoring_engine
    """
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    missing_skills = json.dumps(score_data.get('missing_skills', []))
    matched_skills = json.dumps(score_data.get('matched_skills', []))
    extra_skills = json.dumps(score_data.get('extra_skills', []))
    
    cursor.execute("""
        INSERT INTO screenings (
            candidate_name, email, phone, resume_text, job_description,
            score, matched_skills, missing_skills, extra_skills,
            total_required, total_matched
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        candidate_name,
        email,
        phone,
        resume_text,
        job_description,
        score_data['score'],
        matched_skills,
        missing_skills,
        extra_skills,
        score_data.get('total_required', 0),
        score_data.get('total_matched', 0)
    )) 
    
    conn.commit()
    conn.close()
    
    return True

def get_all_screenings():
    """Retrieve all screening results from database"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM screenings 
        ORDER BY screening_date DESC
    """)
    
    results = cursor.fetchall()
    conn.close()
    
    # Convert to list of dicts
    screenings = []
    for row in results:
        screening = dict(row)
        # Convert JSON strings back to lists
        screening['matched_skills'] = json.loads(screening['matched_skills'])
        screening['missing_skills'] = json.loads(screening['missing_skills'])
        screening['extra_skills'] = json.loads(screening['extra_skills'])
        screenings.append(screening)
    
    return screenings
 
def get_screening_by_id(screening_id):
    """Get specific screening result by ID"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM screenings WHERE id = ?", (screening_id,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        screening = dict(result)
        screening['matched_skills'] = json.loads(screening['matched_skills'])
        screening['missing_skills'] = json.loads(screening['missing_skills'])
        screening['extra_skills'] = json.loads(screening['extra_skills'])
        return screening
    
    return None
 
def delete_screening(screening_id):
    """Delete a screening result"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM screenings WHERE id = ?", (screening_id,))
    conn.commit()
    conn.close()
    
    return True
 
def get_statistics():
    """Get overall statistics from all screenings"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Total screenings
    cursor.execute("SELECT COUNT(*) FROM screenings")
    total = cursor.fetchone()[0]
    
    # Average score
    cursor.execute("SELECT AVG(score) FROM screenings")
    avg_score = cursor.fetchone()[0] or 0
    
    # High performers (score >= 70)
    cursor.execute("SELECT COUNT(*) FROM screenings WHERE score >= 70")
    high_performers = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        'total_screenings': total,
        'average_score': round(avg_score, 2),
        'high_performers': high_performers
    }


# ============================================
# NEW INTERVIEW SCHEDULING FUNCTIONS
# ============================================

def schedule_interview(screening_id, candidate_name, candidate_email, interview_date, interview_time, interviewer_email, notes=""):
    """Schedule an interview for a candidate"""
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO interviews (
            screening_id, candidate_name, candidate_email, 
            interview_date, interview_time, interviewer_email, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (screening_id, candidate_name, candidate_email, interview_date, interview_time, interviewer_email, notes))
    
    conn.commit()
    conn.close()
    
    return True


def get_all_interviews():
    """Retrieve all scheduled interviews"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM interviews 
        ORDER BY interview_date DESC, interview_time DESC
    """)
    
    results = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in results]


def get_interviews_by_status(status):
    """Get interviews by status (Scheduled, Completed, Cancelled)"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM interviews 
        WHERE status = ?
        ORDER BY interview_date DESC
    """, (status,))
    
    results = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in results]


def update_interview_status(interview_id, status):
    """Update interview status (Scheduled, Completed, Cancelled)"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE interviews 
        SET status = ?
        WHERE id = ?
    """, (status, interview_id))
    
    conn.commit()
    conn.close()
    
    return True


def delete_interview(interview_id):
    """Delete an interview"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM interviews WHERE id = ?", (interview_id,))
    conn.commit()
    conn.close()
    
    return True


if __name__ == "__main__":
    # Initialize database when script is run directly
    init_database()
    print("Database initialized successfully!")
    print("Screenings table created")
    print("Interviews table created")