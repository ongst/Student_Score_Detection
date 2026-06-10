import sqlite3
from pathlib import Path


DB_PATH = Path(__file__).resolve().parent / "student_scores.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS students (
                student_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                class_name TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS courses (
                course_id TEXT PRIMARY KEY,
                course_name TEXT NOT NULL,
                credit REAL NOT NULL CHECK (credit > 0)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS scores (
                score_id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT NOT NULL,
                course_id TEXT NOT NULL,
                score REAL NOT NULL CHECK (score >= 0 AND score <= 100),
                UNIQUE(student_id, course_id),
                FOREIGN KEY(student_id) REFERENCES students(student_id)
                    ON UPDATE CASCADE
                    ON DELETE CASCADE,
                FOREIGN KEY(course_id) REFERENCES courses(course_id)
                    ON UPDATE CASCADE
                    ON DELETE CASCADE
            )
            """
        )


def fetch_all(sql, params=()):
    with get_connection() as conn:
        return conn.execute(sql, params).fetchall()


def fetch_one(sql, params=()):
    with get_connection() as conn:
        return conn.execute(sql, params).fetchone()


def execute(sql, params=()):
    with get_connection() as conn:
        cur = conn.execute(sql, params)
        return cur.lastrowid


def add_student(student_id, name, class_name):
    execute(
        "INSERT INTO students(student_id, name, class_name) VALUES (?, ?, ?)",
        (student_id, name, class_name),
    )


def update_student(old_student_id, student_id, name, class_name):
    execute(
        """
        UPDATE students
        SET student_id = ?, name = ?, class_name = ?
        WHERE student_id = ?
        """,
        (student_id, name, class_name, old_student_id),
    )


def delete_student(student_id):
    execute("DELETE FROM students WHERE student_id = ?", (student_id,))


def get_students():
    return fetch_all(
        "SELECT student_id, name, class_name FROM students ORDER BY class_name, student_id"
    )


def add_course(course_id, course_name, credit):
    execute(
        "INSERT INTO courses(course_id, course_name, credit) VALUES (?, ?, ?)",
        (course_id, course_name, credit),
    )


def update_course(old_course_id, course_id, course_name, credit):
    execute(
        """
        UPDATE courses
        SET course_id = ?, course_name = ?, credit = ?
        WHERE course_id = ?
        """,
        (course_id, course_name, credit, old_course_id),
    )


def delete_course(course_id):
    execute("DELETE FROM courses WHERE course_id = ?", (course_id,))


def get_courses():
    return fetch_all(
        "SELECT course_id, course_name, credit FROM courses ORDER BY course_id"
    )


def upsert_score(student_id, course_id, score):
    execute(
        """
        INSERT INTO scores(student_id, course_id, score)
        VALUES (?, ?, ?)
        ON CONFLICT(student_id, course_id)
        DO UPDATE SET score = excluded.score
        """,
        (student_id, course_id, score),
    )


def delete_score(score_id):
    execute("DELETE FROM scores WHERE score_id = ?", (score_id,))


def get_scores():
    return fetch_all(
        """
        SELECT
            sc.score_id,
            s.student_id,
            s.name,
            c.course_id,
            c.course_name,
            sc.score
        FROM scores sc
        JOIN students s ON s.student_id = sc.student_id
        JOIN courses c ON c.course_id = sc.course_id
        ORDER BY s.class_name, s.student_id, c.course_id
        """
    )


def get_classes():
    rows = fetch_all("SELECT DISTINCT class_name FROM students ORDER BY class_name")
    return [row["class_name"] for row in rows]
