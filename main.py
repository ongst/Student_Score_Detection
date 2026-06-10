import tkinter as tk
from tkinter import ttk

import database
from analysis_manager import AnalysisFrame
from course_manager import CourseFrame
from score_manager import ScoreFrame
from student_manager import StudentFrame
from warning_manager import WarningFrame


class StudentScoreApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("学生成绩分析与预警系统")
        self.geometry("1050x720")
        self.minsize(960, 640)

        self._configure_style()
        database.init_db()
        self._build_widgets()

    def _configure_style(self):
        style = ttk.Style(self)
        if "vista" in style.theme_names():
            style.theme_use("vista")
        style.configure("Treeview", rowheight=26)
        style.configure("TButton", padding=(10, 4))

    def _build_widgets(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.student_frame = StudentFrame(self.notebook, self.refresh_all)
        self.course_frame = CourseFrame(self.notebook, self.refresh_all)
        self.score_frame = ScoreFrame(self.notebook, self.refresh_all)
        self.analysis_frame = AnalysisFrame(self.notebook)
        self.warning_frame = WarningFrame(self.notebook)

        self.notebook.add(self.student_frame, text="学生管理")
        self.notebook.add(self.course_frame, text="课程管理")
        self.notebook.add(self.score_frame, text="成绩录入")
        self.notebook.add(self.analysis_frame, text="成绩分析")
        self.notebook.add(self.warning_frame, text="学业预警")
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

    def refresh_all(self):
        self.student_frame.refresh()
        self.course_frame.refresh()
        self.score_frame.refresh()
        self.analysis_frame.refresh()
        self.warning_frame.refresh(show_popup=False)

    def on_tab_changed(self, _event):
        selected = self.notebook.select()
        if selected == str(self.warning_frame):
            self.warning_frame.refresh(show_popup=True)
        elif selected == str(self.analysis_frame):
            self.analysis_frame.refresh()
        elif selected == str(self.score_frame):
            self.score_frame.refresh()


if __name__ == "__main__":
    app = StudentScoreApp()
    app.mainloop()
