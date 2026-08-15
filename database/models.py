import json

from database.database import get_connection


def _json(value):

    if isinstance(value, list):
        return json.dumps(value)

    return json.dumps([])


def _decode(value):

    if isinstance(value, list):
        return value

    try:

        parsed = json.loads(
            value or "[]"
        )

        if isinstance(parsed, list):
            return parsed

    except (
        TypeError,
        json.JSONDecodeError
    ):
        pass

    return []


# ============================================================
# JOBS
# ============================================================

def create_job(data):

    connection = get_connection()

    cursor = connection.execute(
        """
        INSERT INTO jobs
        (
            title,
            description,
            required_skills,
            preferred_skills,
            experience,
            education,
            notice_period,
            salary_min,
            salary_max,
            location,
            regional_preference,
            relocation_willingness
        )

        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            data["title"].strip(),

            data["description"].strip(),

            _json(
                data.get(
                    "required_skills"
                )
            ),

            _json(
                data.get(
                    "preferred_skills"
                )
            ),

            data.get(
                "experience",
                ""
            ),

            _json(
                data.get(
                    "education"
                )
            ),

            data.get(
                "notice_period",
                ""
            ),

            data.get(
                "salary_min_lpa"
            ),

            data.get(
                "salary_max_lpa"
            ),

            data.get(
                "location",
                ""
            ),

            data.get(
                "regional_preference",
                ""
            ),

            data.get(
                "relocation_willingness",
                ""
            ),
        )
    )

    connection.commit()

    job_id = cursor.lastrowid

    connection.close()

    return job_id


def get_jobs():

    connection = get_connection()

    rows = connection.execute(
        """
        SELECT *
        FROM jobs
        ORDER BY id DESC
        """
    ).fetchall()

    connection.close()

    return [
        dict(row)
        for row in rows
    ]


def get_job(job_id):

    connection = get_connection()

    row = connection.execute(
        """
        SELECT *
        FROM jobs
        WHERE id = ?
        """,
        (job_id,)
    ).fetchone()

    connection.close()

    return dict(row) if row else None


# ============================================================
# CANDIDATES
# ============================================================

def create_candidate(data):

    connection = get_connection()

    cursor = connection.execute(
        """
        INSERT INTO candidates
        (
            name,
            email,
            phone,
            resume_filename,
            resume_text,
            skills,
            education,
            experience,
            notice_period,
            expected_salary,
            location,
            relocation_willingness,
            score,
            status
        )

        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            data.get(
                "name"
            ) or "Unknown",

            data.get(
                "email",
                ""
            ),

            data.get(
                "phone",
                ""
            ),

            data.get(
                "resume_filename",
                ""
            ),

            data.get(
                "resume_text",
                ""
            ),

            _json(
                data.get(
                    "skills"
                )
            ),

            _json(
                data.get(
                    "education"
                )
            ),

            data.get(
                "experience",
                ""
            ),

            data.get(
                "notice_period",
                ""
            ),

            data.get(
                "expected_salary"
            ),

            data.get(
                "location",
                ""
            ),

            data.get(
                "relocation_willingness",
                ""
            ),

            float(
                data.get(
                    "score",
                    0
                ) or 0
            ),

            data.get(
                "status",
                "New"
            ),
        )
    )

    connection.commit()

    candidate_id = cursor.lastrowid

    connection.close()

    return candidate_id


def get_candidates():

    connection = get_connection()

    rows = connection.execute(
        """
        SELECT *
        FROM candidates
        ORDER BY score DESC, id DESC
        """
    ).fetchall()

    connection.close()

    return [
        dict(row)
        for row in rows
    ]


def get_candidate(candidate_id):

    connection = get_connection()

    row = connection.execute(
        """
        SELECT *
        FROM candidates
        WHERE id = ?
        """,
        (candidate_id,)
    ).fetchone()

    connection.close()

    return dict(row) if row else None


def update_candidate_score(
    candidate_id,
    score,
    status=None
):

    connection = get_connection()

    if status is None:

        connection.execute(
            """
            UPDATE candidates
            SET score = ?
            WHERE id = ?
            """,
            (
                float(score),
                candidate_id
            )
        )

    else:

        connection.execute(
            """
            UPDATE candidates
            SET score = ?,
                status = ?
            WHERE id = ?
            """,
            (
                float(score),
                status,
                candidate_id
            )
        )

    connection.commit()

    connection.close()


def update_candidate_status(
    candidate_id,
    status
):

    connection = get_connection()

    connection.execute(
        """
        UPDATE candidates
        SET status = ?
        WHERE id = ?
        """,
        (
            status,
            candidate_id
        )
    )

    connection.commit()

    connection.close()


# ============================================================
# ASSESSMENTS
# ============================================================

def save_assessment_result(
    candidate_id,
    job_id,
    score,
    details=""
):

    connection = get_connection()

    connection.execute(
        """
        INSERT INTO assessments
        (
            candidate_id,
            job_id,
            score,
            status,
            details
        )

        VALUES (?, ?, ?, 'Completed', ?)
        """,
        (
            candidate_id,
            job_id,
            float(score),
            details
        )
    )

    connection.commit()

    connection.close()


# ============================================================
# INTERVIEWS
# ============================================================

def schedule_interview(
    candidate_id,
    job_id,
    date,
    time,
    mode,
    notes
):

    connection = get_connection()

    connection.execute(
        """
        INSERT INTO interviews
        (
            candidate_id,
            job_id,
            interview_date,
            interview_time,
            mode,
            notes
        )

        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            candidate_id,
            job_id,
            date,
            time,
            mode,
            notes
        )
    )

    connection.commit()

    connection.close()


def get_interviews():

    connection = get_connection()

    rows = connection.execute(
        """
        SELECT
            i.*,
            c.name AS candidate_name,
            j.title AS job_title

        FROM interviews i

        LEFT JOIN candidates c
            ON c.id = i.candidate_id

        LEFT JOIN jobs j
            ON j.id = i.job_id

        ORDER BY
            i.interview_date,
            i.interview_time
        """
    ).fetchall()

    connection.close()

    return [
        dict(row)
        for row in rows
    ]


# ============================================================
# JSON HELPERS
# ============================================================

def decode_json_fields(row):

    item = dict(row)

    for key in (
        "required_skills",
        "preferred_skills",
        "education",
        "skills"
    ):

        if key in item:

            item[key] = _decode(
                item[key]
            )

    return item