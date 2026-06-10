import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk

import database


class ScoreFrame(ttk.Frame):
    def __init__(self, master, on_data_changed=None):
        super().__init__(master, padding=10)
        self.on_data_changed = on_data_changed
        self.student_map = {}
        self.course_map = {}
        self.selected_score_id = None
        self._build_widgets()
        self.refresh()

    def _build_widgets(self):
        form = ttk.LabelFrame(self, text="成绩录入", padding=10)
        form.pack(fill=tk.X)

        ttk.Label(form, text="学生:").grid(row=0, column=0, padx=5, pady=5)
        self.student_combo = ttk.Combobox(form, state="readonly", width=28)
        self.student_combo.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(form, text="课程:").grid(row=0, column=2, padx=5, pady=5)
        self.course_combo = ttk.Combobox(form, state="readonly", width=28)
        self.course_combo.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(form, text="成绩:").grid(row=0, column=4, padx=5, pady=5)
        self.score_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.score_var, width=12).grid(
            row=0, column=5, padx=5, pady=5
        )

        buttons = ttk.Frame(form)
        buttons.grid(row=1, column=0, columnspan=6, pady=8)
        ttk.Button(buttons, text="保存成绩", command=self.save_score).pack(
            side=tk.LEFT, padx=4
        )
        ttk.Button(buttons, text="删除成绩", command=self.delete_score).pack(
            side=tk.LEFT, padx=4
        )
        ttk.Button(buttons, text="清空", command=self.clear_form).pack(
            side=tk.LEFT, padx=4
        )
        ttk.Button(buttons, text="刷新", command=self.refresh).pack(side=tk.LEFT, padx=4)

        columns = ("score_id", "student_id", "name", "course_id", "course_name", "score")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=14)
        headings = ("成绩ID", "学号", "姓名", "课程编号", "课程名", "成绩")
        widths = (70, 120, 120, 120, 160, 90)
        for column, heading, width in zip(columns, headings, widths):
            self.tree.heading(column, text=heading)
            self.tree.column(column, anchor=tk.CENTER, width=width)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        ybar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=ybar.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=(10, 0))
        ybar.pack(side=tk.RIGHT, fill=tk.Y, pady=(10, 0))

    def refresh_options(self):
        students = database.get_students()
        courses = database.get_courses()
        self.student_map = {
            f"{row['student_id']} - {row['name']}": row["student_id"] for row in students
        }
        self.course_map = {
            f"{row['course_id']} - {row['course_name']}": row["course_id"]
            for row in courses
        }
        self.student_combo["values"] = list(self.student_map.keys())
        self.course_combo["values"] = list(self.course_map.keys())
        if self.student_combo.get() not in self.student_map:
            self.student_combo.set("")
        if self.course_combo.get() not in self.course_map:
            self.course_combo.set("")
        if self.student_map and not self.student_combo.get():
            self.student_combo.current(0)
        if self.course_map and not self.course_combo.get():
            self.course_combo.current(0)

    def validate_form(self):
        student_label = self.student_combo.get()
        course_label = self.course_combo.get()
        score_text = self.score_var.get().strip()
        if not student_label or not course_label:
            messagebox.showwarning("输入错误", "请先选择学生和课程")
            return None
        if not score_text:
            messagebox.showwarning("输入错误", "成绩不能为空")
            return None
        try:
            score = float(score_text)
        except ValueError:
            messagebox.showwarning("输入错误", "成绩必须为数字")
            return None
        if score < 0 or score > 100:
            messagebox.showwarning("输入错误", "成绩必须在 0 到 100 之间")
            return None
        return self.student_map[student_label], self.course_map[course_label], score

    def save_score(self):
        data = self.validate_form()
        if not data:
            return
        try:
            database.upsert_score(*data)
        except sqlite3.IntegrityError as exc:
            messagebox.showerror("保存失败", f"成绩数据不合法: {exc}")
            return
        self.clear_form(keep_options=True)
        self._changed()

    def delete_score(self):
        if not self.selected_score_id:
            messagebox.showwarning("提示", "请先选择要删除的成绩")
            return
        if not messagebox.askyesno("确认删除", "是否删除该成绩记录？"):
            return
        database.delete_score(self.selected_score_id)
        self.clear_form(keep_options=True)
        self._changed()

    def on_select(self, _event):
        selected = self.tree.selection()
        if not selected:
            return
        values = self.tree.item(selected[0], "values")
        self.selected_score_id = values[0]
        student_label = f"{values[1]} - {values[2]}"
        course_label = f"{values[3]} - {values[4]}"
        self.student_combo.set(student_label)
        self.course_combo.set(course_label)
        self.score_var.set(values[5])

    def clear_form(self, keep_options=False):
        self.selected_score_id = None
        if not keep_options:
            self.student_combo.set("")
            self.course_combo.set("")
        self.score_var.set("")
        self.tree.selection_remove(self.tree.selection())

    def refresh(self):
        self.refresh_options()
        for item in self.tree.get_children():
            self.tree.delete(item)
        for row in database.get_scores():
            self.tree.insert(
                "",
                tk.END,
                values=(
                    row["score_id"],
                    row["student_id"],
                    row["name"],
                    row["course_id"],
                    row["course_name"],
                    row["score"],
                ),
            )

    def _changed(self):
        self.refresh()
        if self.on_data_changed:
            self.on_data_changed()
