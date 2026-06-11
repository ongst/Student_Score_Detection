import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

import database
from exporter import export_grade_report


SCORE_BANDS = [
    ("0-59", 0, 59),
    ("60-69", 60, 69),
    ("70-79", 70, 79),
    ("80-89", 80, 89),
    ("90-100", 90, 100),
]


def configure_matplotlib_chinese_font():
    from matplotlib import font_manager, rcParams

    windows_fonts = Path("C:/Windows/Fonts")
    font_candidates = [
        ("Microsoft YaHei", windows_fonts / "msyh.ttc"),
        ("SimHei", windows_fonts / "simhei.ttf"),
        ("SimSun", windows_fonts / "simsun.ttc"),
        ("KaiTi", windows_fonts / "simkai.ttf"),
    ]

    selected_font = None
    installed_names = {font.name for font in font_manager.fontManager.ttflist}
    for font_name, font_path in font_candidates:
        if font_path.exists():
            font_manager.fontManager.addfont(str(font_path))
            selected_font = font_name
            break
        if font_name in installed_names:
            selected_font = font_name
            break

    fallback_fonts = [
        "Microsoft YaHei",
        "SimHei",
        "SimSun",
        "KaiTi",
        "Noto Sans CJK SC",
        "Arial Unicode MS",
        "DejaVu Sans",
    ]
    if selected_font:
        fallback_fonts.insert(0, selected_font)

    rcParams["font.sans-serif"] = fallback_fonts
    rcParams["font.family"] = "sans-serif"
    rcParams["axes.unicode_minus"] = False


def score_to_point(score):
    score = float(score)
    if score >= 90:
        return 4.0
    if score >= 80:
        return 3.0
    if score >= 70:
        return 2.0
    if score >= 60:
        return 1.0
    return 0.0


def get_student_summaries():
    students = database.get_students()
    courses = database.get_courses()
    scores = database.fetch_all(
        """
        SELECT sc.student_id, sc.course_id, sc.score, c.credit
        FROM scores sc
        JOIN courses c ON c.course_id = sc.course_id
        """
    )

    grouped = {}
    for row in scores:
        grouped.setdefault(row["student_id"], []).append(row)

    summaries = []
    for student in students:
        student_scores = grouped.get(student["student_id"], [])
        scores_by_course = {row["course_id"]: row["score"] for row in student_scores}

        if student_scores:
            total_score = sum(row["score"] for row in student_scores)
            avg_score = total_score / len(student_scores)
            total_credit = sum(row["credit"] for row in student_scores)
            gpa = (
                sum(score_to_point(row["score"]) * row["credit"] for row in student_scores)
                / total_credit
                if total_credit
                else None
            )
        else:
            avg_score = None
            gpa = None

        summaries.append(
            {
                "student_id": student["student_id"],
                "name": student["name"],
                "class_name": student["class_name"],
                "avg_score": avg_score,
                "gpa": gpa,
                "scores_by_course": scores_by_course,
                "course_count": len(student_scores),
            }
        )
    return summaries, courses


def get_warning_students():
    summaries, _ = get_student_summaries()
    return [
        item
        for item in summaries
        if item["avg_score"] is not None and item["avg_score"] < 60
    ]


def get_course_distribution(course_id):
    result = {label: 0 for label, _, _ in SCORE_BANDS}
    rows = database.fetch_all(
        "SELECT score FROM scores WHERE course_id = ?",
        (course_id,),
    )
    for row in rows:
        score = row["score"]
        for label, low, high in SCORE_BANDS:
            if low <= score <= high:
                result[label] += 1
                break
    return result


def get_class_ranking(class_name):
    summaries, _ = get_student_summaries()
    ranking = [
        item
        for item in summaries
        if item["class_name"] == class_name and item["avg_score"] is not None
    ]
    ranking.sort(key=lambda item: (-item["avg_score"], item["student_id"]))
    return ranking


def format_score(value):
    return "暂无" if value is None else f"{value:.2f}"


class AnalysisFrame(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, padding=10)
        self.course_map = {}
        self.class_values = []
        self.canvas = None
        self.figure = None
        self._build_widgets()
        self.refresh()

    def _build_widgets(self):
        top = ttk.LabelFrame(self, text="课程成绩分布", padding=10)
        top.pack(fill=tk.BOTH, expand=True)

        controls = ttk.Frame(top)
        controls.pack(fill=tk.X)
        ttk.Label(controls, text="选择课程:").pack(side=tk.LEFT)
        self.course_combo = ttk.Combobox(controls, state="readonly", width=28)
        self.course_combo.pack(side=tk.LEFT, padx=8)
        ttk.Button(controls, text="生成直方图", command=self.draw_distribution).pack(
            side=tk.LEFT
        )
        ttk.Button(controls, text="导出 Excel", command=self.export_excel).pack(
            side=tk.RIGHT
        )

        self.chart_area = ttk.Frame(top)
        self.chart_area.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        bottom = ttk.Frame(self)
        bottom.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        summary_box = ttk.LabelFrame(bottom, text="学生平均分与 GPA", padding=8)
        summary_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        self.summary_tree = self._make_tree(
            summary_box,
            ("student_id", "name", "class_name", "avg_score", "gpa"),
            ("学号", "姓名", "班级", "平均分", "GPA"),
        )

        ranking_box = ttk.LabelFrame(bottom, text="班级成绩排名", padding=8)
        ranking_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))
        rank_controls = ttk.Frame(ranking_box)
        rank_controls.pack(fill=tk.X)
        ttk.Label(rank_controls, text="选择班级:").pack(side=tk.LEFT)
        self.class_combo = ttk.Combobox(rank_controls, state="readonly", width=18)
        self.class_combo.pack(side=tk.LEFT, padx=8)
        ttk.Button(rank_controls, text="查看排名", command=self.refresh_ranking).pack(
            side=tk.LEFT
        )
        self.ranking_tree = self._make_tree(
            ranking_box,
            ("rank", "student_id", "name", "avg_score", "gpa"),
            ("排名", "学号", "姓名", "平均分", "GPA"),
        )

    def _make_tree(self, master, columns, headings):
        tree = ttk.Treeview(master, columns=columns, show="headings", height=8)
        for column, heading in zip(columns, headings):
            tree.heading(column, text=heading)
            tree.column(column, anchor=tk.CENTER, width=90)
        ybar = ttk.Scrollbar(master, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=ybar.set)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        ybar.pack(side=tk.RIGHT, fill=tk.Y)
        return tree

    def refresh(self):
        courses = database.get_courses()
        self.course_map = {
            f"{row['course_id']} - {row['course_name']}": row["course_id"]
            for row in courses
        }
        self.course_combo["values"] = list(self.course_map.keys())
        if self.course_combo.get() not in self.course_map:
            self.course_combo.set("")
        if self.course_map and not self.course_combo.get():
            self.course_combo.current(0)

        self.class_values = database.get_classes()
        self.class_combo["values"] = self.class_values
        if self.class_combo.get() not in self.class_values:
            self.class_combo.set("")
        if self.class_values and not self.class_combo.get():
            self.class_combo.current(0)

        self.refresh_summary()
        self.refresh_ranking()

    def refresh_summary(self):
        for item in self.summary_tree.get_children():
            self.summary_tree.delete(item)
        summaries, _ = get_student_summaries()
        for item in summaries:
            self.summary_tree.insert(
                "",
                tk.END,
                values=(
                    item["student_id"],
                    item["name"],
                    item["class_name"],
                    format_score(item["avg_score"]),
                    format_score(item["gpa"]),
                ),
            )

    def refresh_ranking(self):
        for item in self.ranking_tree.get_children():
            self.ranking_tree.delete(item)
        class_name = self.class_combo.get()
        if not class_name:
            return
        for index, item in enumerate(get_class_ranking(class_name), start=1):
            self.ranking_tree.insert(
                "",
                tk.END,
                values=(
                    index,
                    item["student_id"],
                    item["name"],
                    format_score(item["avg_score"]),
                    format_score(item["gpa"]),
                ),
            )

    def draw_distribution(self):
        selected = self.course_combo.get()
        if not selected:
            messagebox.showwarning("提示", "请先选择课程")
            return

        course_id = self.course_map[selected]
        distribution = get_course_distribution(course_id)
        labels = list(distribution.keys())
        counts = list(distribution.values())
        if sum(counts) == 0:
            messagebox.showinfo("提示", "该课程暂无成绩数据")

        for child in self.chart_area.winfo_children():
            child.destroy()

        configure_matplotlib_chinese_font()

        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        from matplotlib.figure import Figure

        self.figure = Figure(figsize=(6, 3.2), dpi=100)
        axis = self.figure.add_subplot(111)
        axis.bar(labels, counts, color="#4f81bd")
        axis.set_xlabel("分数段")
        axis.set_ylabel("学生人数")
        axis.set_title("课程成绩分布")
        axis.set_ylim(bottom=0)
        for index, count in enumerate(counts):
            axis.text(index, count, str(count), ha="center", va="bottom")
        self.figure.tight_layout()

        self.canvas = FigureCanvasTkAgg(self.figure, master=self.chart_area)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def export_excel(self):
        path = filedialog.asksaveasfilename(
            title="导出成绩报表",
            defaultextension=".xlsx",
            filetypes=[("Excel 文件", "*.xlsx")],
        )
        if not path:
            return
        try:
            export_grade_report(path)
        except Exception as exc:
            messagebox.showerror("导出失败", str(exc))
        else:
            messagebox.showinfo("导出成功", f"成绩报表已导出到:\n{path}")
