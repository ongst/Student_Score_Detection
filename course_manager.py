import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk

import database


class CourseFrame(ttk.Frame):
    def __init__(self, master, on_data_changed=None):
        super().__init__(master, padding=10)
        self.on_data_changed = on_data_changed
        self.selected_course_id = None
        self._build_widgets()
        self.refresh()

    def _build_widgets(self):
        form = ttk.LabelFrame(self, text="课程信息", padding=10)
        form.pack(fill=tk.X)

        ttk.Label(form, text="课程编号:").grid(row=0, column=0, padx=5, pady=5)
        self.course_id_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.course_id_var, width=20).grid(
            row=0, column=1, padx=5, pady=5
        )

        ttk.Label(form, text="课程名:").grid(row=0, column=2, padx=5, pady=5)
        self.course_name_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.course_name_var, width=20).grid(
            row=0, column=3, padx=5, pady=5
        )

        ttk.Label(form, text="学分:").grid(row=0, column=4, padx=5, pady=5)
        self.credit_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.credit_var, width=12).grid(
            row=0, column=5, padx=5, pady=5
        )

        buttons = ttk.Frame(form)
        buttons.grid(row=1, column=0, columnspan=6, pady=8)
        ttk.Button(buttons, text="添加", command=self.add_course).pack(
            side=tk.LEFT, padx=4
        )
        ttk.Button(buttons, text="修改", command=self.update_course).pack(
            side=tk.LEFT, padx=4
        )
        ttk.Button(buttons, text="删除", command=self.delete_course).pack(
            side=tk.LEFT, padx=4
        )
        ttk.Button(buttons, text="清空", command=self.clear_form).pack(
            side=tk.LEFT, padx=4
        )
        ttk.Button(buttons, text="刷新", command=self.refresh).pack(side=tk.LEFT, padx=4)

        columns = ("course_id", "course_name", "credit")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=14)
        for column, heading in zip(columns, ("课程编号", "课程名", "学分")):
            self.tree.heading(column, text=heading)
            self.tree.column(column, anchor=tk.CENTER, width=160)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        ybar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=ybar.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=(10, 0))
        ybar.pack(side=tk.RIGHT, fill=tk.Y, pady=(10, 0))

    def validate_form(self):
        course_id = self.course_id_var.get().strip()
        course_name = self.course_name_var.get().strip()
        credit_text = self.credit_var.get().strip()
        if not course_id or not course_name or not credit_text:
            messagebox.showwarning("输入错误", "课程编号、课程名和学分不能为空")
            return None
        try:
            credit = float(credit_text)
        except ValueError:
            messagebox.showwarning("输入错误", "学分必须为数字")
            return None
        if credit <= 0:
            messagebox.showwarning("输入错误", "学分必须大于 0")
            return None
        return course_id, course_name, credit

    def add_course(self):
        data = self.validate_form()
        if not data:
            return
        try:
            database.add_course(*data)
        except sqlite3.IntegrityError:
            messagebox.showerror("添加失败", "课程编号已存在或数据不合法")
            return
        self.clear_form()
        self._changed()

    def update_course(self):
        if not self.selected_course_id:
            messagebox.showwarning("提示", "请先选择要修改的课程")
            return
        data = self.validate_form()
        if not data:
            return
        try:
            database.update_course(self.selected_course_id, *data)
        except sqlite3.IntegrityError:
            messagebox.showerror("修改失败", "课程编号已存在或数据不合法")
            return
        self.clear_form()
        self._changed()

    def delete_course(self):
        if not self.selected_course_id:
            messagebox.showwarning("提示", "请先选择要删除的课程")
            return
        if not messagebox.askyesno("确认删除", "删除课程会同步删除相关成绩，是否继续？"):
            return
        database.delete_course(self.selected_course_id)
        self.clear_form()
        self._changed()

    def on_select(self, _event):
        selected = self.tree.selection()
        if not selected:
            return
        values = self.tree.item(selected[0], "values")
        self.selected_course_id = values[0]
        self.course_id_var.set(values[0])
        self.course_name_var.set(values[1])
        self.credit_var.set(values[2])

    def clear_form(self):
        self.selected_course_id = None
        self.course_id_var.set("")
        self.course_name_var.set("")
        self.credit_var.set("")
        self.tree.selection_remove(self.tree.selection())

    def refresh(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for row in database.get_courses():
            self.tree.insert(
                "",
                tk.END,
                values=(row["course_id"], row["course_name"], row["credit"]),
            )

    def _changed(self):
        self.refresh()
        if self.on_data_changed:
            self.on_data_changed()
