import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from analysis_manager import format_score, get_warning_students
from exporter import export_grade_report


class WarningFrame(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, padding=10)
        self._build_widgets()
        self.refresh(show_popup=False)

    def _build_widgets(self):
        top = ttk.Frame(self)
        top.pack(fill=tk.X)
        self.status_var = tk.StringVar(value="当前暂无需学业预警学生")
        ttk.Label(top, textvariable=self.status_var, foreground="#a33").pack(
            side=tk.LEFT
        )
        ttk.Button(top, text="刷新预警", command=lambda: self.refresh(True)).pack(
            side=tk.RIGHT, padx=4
        )
        ttk.Button(top, text="导出 Excel", command=self.export_excel).pack(
            side=tk.RIGHT, padx=4
        )

        columns = ("student_id", "name", "class_name", "avg_score", "gpa")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=16)
        for column, heading in zip(columns, ("学号", "姓名", "班级", "平均分", "GPA")):
            self.tree.heading(column, text=heading)
            self.tree.column(column, anchor=tk.CENTER, width=140)
        self.tree.tag_configure("warning", background="#f9d6d5")

        ybar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=ybar.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=(10, 0))
        ybar.pack(side=tk.RIGHT, fill=tk.Y, pady=(10, 0))

    def refresh(self, show_popup=True):
        for item in self.tree.get_children():
            self.tree.delete(item)

        warnings = get_warning_students()
        for item in warnings:
            self.tree.insert(
                "",
                tk.END,
                values=(
                    item["student_id"],
                    item["name"],
                    item["class_name"],
                    format_score(item["avg_score"]),
                    format_score(item["gpa"]),
                ),
                tags=("warning",),
            )

        if warnings:
            names = "、".join(item["name"] for item in warnings)
            message = f"以下学生需学业预警: {names}"
        else:
            message = "当前暂无需学业预警学生"
        self.status_var.set(message)

        if show_popup:
            messagebox.showinfo("学业预警", message)

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
