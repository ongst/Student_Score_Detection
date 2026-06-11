import database


STUDENTS = [
    ("S001", "张优秀", "一班"),
    ("S002", "李良好", "一班"),
    ("S003", "王中等", "一班"),
    ("S004", "赵及格", "二班"),
    ("S005", "钱预警", "二班"),
    ("S006", "孙偏科", "二班"),
    ("S007", "周边界", "三班"),
    ("S008", "吴暂无", "三班"),
]


COURSES = [
    ("C001", "Python程序设计", 3),
    ("C002", "数据库基础", 2),
    ("C003", "高等数学", 4),
    ("C004", "大学英语", 2),
]


SCORES = [
    ("S001", "C001", 95),
    ("S001", "C002", 92),
    ("S001", "C003", 98),
    ("S001", "C004", 90),
    ("S002", "C001", 88),
    ("S002", "C002", 84),
    ("S002", "C003", 82),
    ("S002", "C004", 80),
    ("S003", "C001", 76),
    ("S003", "C002", 72),
    ("S003", "C003", 75),
    ("S003", "C004", 70),
    ("S004", "C001", 65),
    ("S004", "C002", 61),
    ("S004", "C003", 68),
    ("S004", "C004", 60),
    ("S005", "C001", 55),
    ("S005", "C002", 58),
    ("S005", "C003", 52),
    ("S005", "C004", 59),
    ("S006", "C001", 100),
    ("S006", "C002", 45),
    ("S006", "C003", 82),
    ("S006", "C004", 60),
    ("S007", "C001", 59),
    ("S007", "C002", 60),
    ("S007", "C003", 69),
    ("S007", "C004", 90),
]


def upsert_student(student_id, name, class_name):
    database.execute(
        """
        INSERT INTO students(student_id, name, class_name)
        VALUES (?, ?, ?)
        ON CONFLICT(student_id)
        DO UPDATE SET name = excluded.name, class_name = excluded.class_name
        """,
        (student_id, name, class_name),
    )


def upsert_course(course_id, course_name, credit):
    database.execute(
        """
        INSERT INTO courses(course_id, course_name, credit)
        VALUES (?, ?, ?)
        ON CONFLICT(course_id)
        DO UPDATE SET course_name = excluded.course_name, credit = excluded.credit
        """,
        (course_id, course_name, credit),
    )


def seed():
    database.init_db()
    for student in STUDENTS:
        upsert_student(*student)
    for course in COURSES:
        upsert_course(*course)
    for score in SCORES:
        database.upsert_score(*score)


if __name__ == "__main__":
    seed()
    print("预设数据写入完成")
    print(f"学生: {len(STUDENTS)} 人")
    print(f"课程: {len(COURSES)} 门")
    print(f"成绩: {len(SCORES)} 条")
