import tempfile
from pathlib import Path

import database
from analysis_manager import get_class_ranking, get_course_distribution, get_warning_students
from exporter import export_grade_report


def run_smoke_test():
    with tempfile.TemporaryDirectory() as tmpdir:
        database.DB_PATH = Path(tmpdir) / "test_student_scores.db"
        database.init_db()

        database.add_student("S001", "张三", "一班")
        database.add_student("S002", "李四", "一班")
        database.add_course("C001", "Python程序设计", 3)
        database.add_course("C002", "数据库基础", 2)

        database.upsert_score("S001", "C001", 95)
        database.upsert_score("S001", "C002", 85)
        database.upsert_score("S002", "C001", 55)
        database.upsert_score("S002", "C002", 58)
        database.upsert_score("S002", "C002", 59)

        distribution = get_course_distribution("C001")
        assert distribution["0-59"] == 1
        assert distribution["90-100"] == 1

        ranking = get_class_ranking("一班")
        assert ranking[0]["student_id"] == "S001"
        assert ranking[1]["student_id"] == "S002"

        warnings = get_warning_students()
        assert len(warnings) == 1
        assert warnings[0]["student_id"] == "S002"

        report_path = Path(tmpdir) / "report.xlsx"
        export_grade_report(report_path)
        assert report_path.exists()


if __name__ == "__main__":
    run_smoke_test()
    print("核心逻辑测试通过")
