import tempfile
from pathlib import Path

import database
from analysis_manager import get_class_ranking, get_course_distribution, get_warning_students
from exporter import export_grade_report


def check_seed_data():
    database.init_db()

    student_count = database.fetch_one("SELECT COUNT(*) AS total FROM students")["total"]
    course_count = database.fetch_one("SELECT COUNT(*) AS total FROM courses")["total"]
    score_count = database.fetch_one("SELECT COUNT(*) AS total FROM scores")["total"]

    assert student_count >= 8, "学生数量不足"
    assert course_count >= 4, "课程数量不足"
    assert score_count >= 28, "成绩数量不足"

    distribution = get_course_distribution("C001")
    expected_distribution = {
        "0-59": 2,
        "60-69": 1,
        "70-79": 1,
        "80-89": 1,
        "90-100": 2,
    }
    assert distribution == expected_distribution, f"C001 分布错误: {distribution}"

    ranking = get_class_ranking("一班")
    assert [item["student_id"] for item in ranking[:3]] == ["S001", "S002", "S003"]

    warnings = get_warning_students()
    warning_ids = {item["student_id"] for item in warnings}
    assert "S005" in warning_ids, "S005 应进入学业预警"
    assert "S008" not in warning_ids, "无成绩学生不应进入预警"

    with tempfile.TemporaryDirectory() as tmpdir:
        report_path = Path(tmpdir) / "seed_report.xlsx"
        export_grade_report(report_path)
        assert report_path.exists(), "Excel 报表未生成"

    print("预设数据测试通过")
    print(f"学生数量: {student_count}")
    print(f"课程数量: {course_count}")
    print(f"成绩数量: {score_count}")
    print(f"C001 成绩分布: {distribution}")
    print("一班排名前三: " + " > ".join(item["name"] for item in ranking[:3]))
    print("预警学生: " + "、".join(item["name"] for item in warnings))


if __name__ == "__main__":
    check_seed_data()
