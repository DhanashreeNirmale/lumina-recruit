import sqlite3
import json
from database.db import get_connection
from database.models import hash_password

# Helper to load JSON
def _load_json(val):
    if not val:
        return []
    try:
        return json.loads(val)
    except:
        return []

# Helper to dump JSON
def _dump_json(val):
    if val is None:
        return "[]"
    if isinstance(val, (list, dict)):
        return json.dumps(val)
    return str(val)

# ============================================================
# USER REPOSITORY
# ============================================================

def create_user(username, password, role):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        hashed = hash_password(password)
        cursor.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            (username.strip().lower(), hashed, role)
        )
        conn.commit()
        user_id = cursor.lastrowid
        return user_id
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()

def verify_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    hashed = hash_password(password)
    cursor.execute(
        "SELECT id, username, role FROM users WHERE username = ? AND password = ?",
        (username.strip().lower(), hashed)
    )
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_user_by_id(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, role FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

# ============================================================
# CANDIDATE REPOSITORY
# ============================================================

def get_candidate_by_user_id(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM candidates WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        c = dict(row)
        c['education'] = _load_json(c['education'])
        c['skills'] = _load_json(c['skills'])
        c['projects'] = _load_json(c['projects'])
        c['experience'] = _load_json(c['experience'])
        c['certifications'] = _load_json(c['certifications'])
        c['preferred_roles'] = _load_json(c['preferred_roles'])
        c['preferred_locations'] = _load_json(c['preferred_locations'])
        return c
    return None

def get_candidate_by_id(candidate_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM candidates WHERE id = ?", (candidate_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        c = dict(row)
        c['education'] = _load_json(c['education'])
        c['skills'] = _load_json(c['skills'])
        c['projects'] = _load_json(c['projects'])
        c['experience'] = _load_json(c['experience'])
        c['certifications'] = _load_json(c['certifications'])
        c['preferred_roles'] = _load_json(c['preferred_roles'])
        c['preferred_locations'] = _load_json(c['preferred_locations'])
        return c
    return None

def get_all_candidates():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM candidates ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    results = []
    for r in rows:
        c = dict(r)
        c['education'] = _load_json(c['education'])
        c['skills'] = _load_json(c['skills'])
        c['projects'] = _load_json(c['projects'])
        c['experience'] = _load_json(c['experience'])
        c['certifications'] = _load_json(c['certifications'])
        c['preferred_roles'] = _load_json(c['preferred_roles'])
        c['preferred_locations'] = _load_json(c['preferred_locations'])
        results.append(c)
    return results

def create_or_update_candidate(user_id, data):
    conn = get_connection()
    cursor = conn.cursor()
    
    # Check if candidate already exists
    cursor.execute("SELECT id FROM candidates WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    
    skills_json = _dump_json(data.get('skills', []))
    education_json = _dump_json(data.get('education', []))
    projects_json = _dump_json(data.get('projects', []))
    experience_json = _dump_json(data.get('experience', []))
    certifications_json = _dump_json(data.get('certifications', []))
    pref_roles_json = _dump_json(data.get('preferred_roles', []))
    pref_locs_json = _dump_json(data.get('preferred_locations', []))
    
    if row:
        candidate_id = row['id']
        cursor.execute("""
            UPDATE candidates SET
                name = ?, email = ?, phone = ?, location = ?, education = ?,
                college = ?, degree = ?, branch = ?, graduation_year = ?,
                skills = ?, projects = ?, experience = ?, experience_years = ?,
                certifications = ?, notice_period = ?, expected_salary = ?,
                preferred_roles = ?, preferred_locations = ?, relocation = ?,
                resume_filename = ?, resume_text = ?
            WHERE id = ?
        """, (
            data.get('name', 'Unknown'), data.get('email', ''), data.get('phone', ''),
            data.get('location', ''), education_json, data.get('college', ''),
            data.get('degree', ''), data.get('branch', ''), data.get('graduation_year', ''),
            skills_json, projects_json, experience_json, float(data.get('experience_years', 0) or 0),
            certifications_json, int(data.get('notice_period', 0) or 0), float(data.get('expected_salary', 0) or 0),
            pref_roles_json, pref_locs_json, int(data.get('relocation', 0) or 0),
            data.get('resume_filename', ''), data.get('resume_text', ''), candidate_id
        ))
    else:
        cursor.execute("""
            INSERT INTO candidates (
                user_id, name, email, phone, location, education, college, degree,
                branch, graduation_year, skills, projects, experience, experience_years,
                certifications, notice_period, expected_salary, preferred_roles,
                preferred_locations, relocation, resume_filename, resume_text
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id, data.get('name', 'Unknown'), data.get('email', ''), data.get('phone', ''),
            data.get('location', ''), education_json, data.get('college', ''),
            data.get('degree', ''), data.get('branch', ''), data.get('graduation_year', ''),
            skills_json, projects_json, experience_json, float(data.get('experience_years', 0) or 0),
            certifications_json, int(data.get('notice_period', 0) or 0), float(data.get('expected_salary', 0) or 0),
            pref_roles_json, pref_locs_json, int(data.get('relocation', 0) or 0),
            data.get('resume_filename', ''), data.get('resume_text', '')
        ))
        candidate_id = cursor.lastrowid
    
    conn.commit()
    conn.close()
    return candidate_id

# ============================================================
# JOB REPOSITORY
# ============================================================

def create_job(data):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO jobs (
            title, description, required_skills, min_experience, location,
            min_salary, max_salary, max_notice_period
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data.get('title', '').strip(), data.get('description', '').strip(),
        _dump_json(data.get('required_skills', [])), float(data.get('min_experience', 0) or 0),
        data.get('location', '').strip(), float(data.get('min_salary', 0) or 0),
        float(data.get('max_salary', 0) or 0), int(data.get('max_notice_period', 0) or 0)
    ))
    conn.commit()
    job_id = cursor.lastrowid
    conn.close()
    return job_id

def get_all_jobs():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM jobs ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    results = []
    for r in rows:
        j = dict(r)
        j['required_skills'] = _load_json(j['required_skills'])
        results.append(j)
    return results

def get_job_by_id(job_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM jobs WHERE id = ?", (job_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        j = dict(row)
        j['required_skills'] = _load_json(j['required_skills'])
        return j
    return None

def delete_job(job_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM jobs WHERE id = ?", (job_id,))
    conn.commit()
    conn.close()

# ============================================================
# APPLICATION REPOSITORY
# ============================================================

def create_application(job_id, candidate_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO applications (job_id, candidate_id, status) VALUES (?, ?, 'Applied')",
            (job_id, candidate_id)
        )
        conn.commit()
        app_id = cursor.lastrowid
        return app_id
    except sqlite3.IntegrityError:
        # Already applied
        return None
    finally:
        conn.close()

def get_application_by_id(application_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT a.*, c.name AS candidate_name, c.email AS candidate_email, j.title AS job_title 
        FROM applications a 
        JOIN candidates c ON a.candidate_id = c.id
        JOIN jobs j ON a.job_id = j.id
        WHERE a.id = ?
    """, (application_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_applications_by_candidate(candidate_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT a.*, j.title AS job_title, j.location AS job_location, j.min_salary, j.max_salary 
        FROM applications a 
        JOIN jobs j ON a.job_id = j.id
        WHERE a.candidate_id = ?
        ORDER BY a.id DESC
    """, (candidate_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_applications_by_job(job_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT a.*, c.name AS candidate_name, c.email AS candidate_email 
        FROM applications a 
        JOIN candidates c ON a.candidate_id = c.id
        WHERE a.job_id = ?
        ORDER BY a.match_score DESC
    """, (job_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_all_applications():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT a.*, c.name AS candidate_name, j.title AS job_title 
        FROM applications a
        JOIN candidates c ON a.candidate_id = c.id
        JOIN jobs j ON a.job_id = j.id
        ORDER BY a.id DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def update_application_status(application_id, status):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE applications SET status = ? WHERE id = ?", (status, application_id))
    conn.commit()
    conn.close()

def update_application_score(application_id, score, explanation):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE applications SET match_score = ?, matching_explanation = ? WHERE id = ?",
        (float(score), explanation, application_id)
    )
    conn.commit()
    conn.close()

# ============================================================
# ASSESSMENT REPOSITORY
# ============================================================

def assign_assessment(application_id, test_type):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO assessments (application_id, type, status) VALUES (?, ?, 'Pending')",
            (application_id, test_type)
        )
        conn.commit()
        asm_id = cursor.lastrowid
        return asm_id
    except sqlite3.IntegrityError:
        # Already assigned
        cursor.execute(
            "SELECT id FROM assessments WHERE application_id = ? AND type = ?",
            (application_id, test_type)
        )
        row = cursor.fetchone()
        return row['id'] if row else None
    finally:
        conn.close()

def get_assessments_by_application(application_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM assessments WHERE application_id = ?", (application_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_assessments_by_candidate(candidate_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT asm.*, j.title AS job_title, a.candidate_id
        FROM assessments asm
        JOIN applications a ON asm.application_id = a.id
        JOIN jobs j ON a.job_id = j.id
        WHERE a.candidate_id = ?
    """, (candidate_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def complete_assessment(assessment_id, score, details_dict):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE assessments SET score = ?, status = 'Completed', details = ? WHERE id = ?",
        (float(score), _dump_json(details_dict), assessment_id)
    )
    conn.commit()
    conn.close()

def get_all_questions_by_type(question_type):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM assessment_questions WHERE type = ?", (question_type,))
    rows = cursor.fetchall()
    conn.close()
    results = []
    for r in rows:
        q = dict(r)
        q['options'] = _load_json(q['options'])
        q['test_cases'] = _load_json(q['test_cases'])
        results.append(q)
    return results

def create_assessment_question(data):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO assessment_questions (
            type, question_text, options, correct_answer, code_template, test_cases, marks, category
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data['type'], data['question_text'], _dump_json(data.get('options', [])),
        data.get('correct_answer', ''), data.get('code_template', ''),
        _dump_json(data.get('test_cases', [])), int(data.get('marks', 1)), data.get('category', '')
    ))
    conn.commit()
    q_id = cursor.lastrowid
    conn.close()
    return q_id

def add_assessment_result(assessment_id, question_id, candidate_answer, is_correct, score):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO assessment_results (
            assessment_id, question_id, candidate_answer, is_correct, score
        ) VALUES (?, ?, ?, ?, ?)
    """, (assessment_id, question_id, candidate_answer, int(is_correct), float(score)))
    conn.commit()
    conn.close()

def get_assessment_results(assessment_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT ar.*, aq.question_text, aq.category, aq.marks 
        FROM assessment_results ar
        JOIN assessment_questions aq ON ar.question_id = aq.id
        WHERE ar.assessment_id = ?
    """, (assessment_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

# ============================================================
# MESSAGING REPOSITORY
# ============================================================

def send_message(application_id, sender_id, sender_role, message):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO messages (application_id, sender_id, sender_role, message)
        VALUES (?, ?, ?, ?)
    """, (application_id, sender_id, sender_role, message.strip()))
    conn.commit()
    msg_id = cursor.lastrowid
    conn.close()
    return msg_id

def get_messages_by_application(application_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT m.*, u.username AS sender_name 
        FROM messages m
        JOIN users u ON m.sender_id = u.id
        WHERE m.application_id = ?
        ORDER BY m.id ASC
    """, (application_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

# ============================================================
# INTERVIEW REPOSITORY
# ============================================================

def schedule_interview(candidate_id, job_id, date, time, mode, venue_link, notes):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO interviews (candidate_id, job_id, interview_date, interview_time, mode, venue_link, notes, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, 'Scheduled')
    """, (candidate_id, job_id, str(date), str(time), mode, venue_link.strip(), notes.strip()))
    conn.commit()
    int_id = cursor.lastrowid
    conn.close()
    return int_id

def get_interviews_by_candidate(candidate_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT i.*, j.title AS job_title 
        FROM interviews i
        JOIN jobs j ON i.job_id = j.id
        WHERE i.candidate_id = ?
        ORDER BY i.interview_date ASC, i.interview_time ASC
    """, (candidate_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_interviews_by_job(job_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT i.*, c.name AS candidate_name 
        FROM interviews i
        JOIN candidates c ON i.candidate_id = c.id
        WHERE i.job_id = ?
        ORDER BY i.interview_date ASC, i.interview_time ASC
    """, (job_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_all_interviews():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT i.*, c.name AS candidate_name, j.title AS job_title 
        FROM interviews i
        JOIN candidates c ON i.candidate_id = c.id
        JOIN jobs j ON i.job_id = j.id
        ORDER BY i.interview_date ASC, i.interview_time ASC
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def update_interview_status(interview_id, status):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE interviews SET status = ? WHERE id = ?", (status, interview_id))
    conn.commit()
    conn.close()
