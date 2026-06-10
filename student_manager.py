import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk

import database


class StudentFrame(ttk.Frame):
    def __init__(self, master, on_data_changed=None):
        super().__init__(master, padding=10)
        self.on_data_changed = on_data_changed
        self.selected_student_id = None
        self._build_widgets()
        self.refresh()

    def _build_widgets(self):
        form = ttk.LabelFrame(self, text="学生信息", padding=10)
        form.pack(fill=tk.X)

        ttk.Label(form, text="学号:").grid(row=0, column=0, padx=5, pady=5)
        self.student_id_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.student_id_var, width=20).grid(
            row=0, column=1, padx=5, pady=5
        )

        ttk.Label(form, text="姓名:").grid(row=0, column=2, padx=5, pady=5)
        self.name_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.name_var, width=20).grid(
            row=0, column=3, padx=5, pady=5
        )

        ttk.Label(form, text="班级:").grid(row=0, column=4, padx=5, pady=5)
        self.class_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.class_var, width=20).grid(
            row=0, column=5, padx=5, pady=5
        )

        buttons = ttk.Frame(form)
        buttons.grid(row=1, column=0, columnspan=6, pady=8)
        ttk.Button(buttons, text="添加", command=self.add_student).pack(
            side=tk.LEFT, padx=4
        )
        ttk.Button(buttons, text="修改", command=self.update_student).pack(
            side=tk.LEFT, padx=4
        )
        ttk.Button(buttons, text="删除", command=self.delete_student).pack(
            side=tk.LEFT, padx=4
        )
        ttk.Button(buttons, text="清空", command=self.clear_form).pack(
            side=tk.LEFT, padx=4
        )
        ttk.Button(buttons, text="刷新", command=self.refresh).pack(side=tk.LEFT, padx=4)

        columns = ("student_id", "name", "class_name")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=14)
        for column, heading in zip(columns, ("学号", "姓名", "班级")):
            self.tree.heading(column, text=heading)
            self.tree.column(column, anchor=tk.CENTER, width=160)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        ybar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=ybar.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=(10, 0))
        ybar.pack(side=tk.RIGHT, fill=tk.Y, pady=(10, 0))

    def validate_form(self):
        student_id = self.student_id_var.get().strip()
        name = self.name_var.get().strip()
        class_name = self.class_var.get().strip()
        if not student_id or not name or not class_name:
            messagebox.showwarning("输入错误", "学号、姓名和班级不能为空")
            return None
        return student_id, name, class_name

    def add_student(self):
        data = self.validate_form()
        if not data:
            return
        try:
            database.add_student(*data)
        except sqlite3.IntegrityError:
            messagebox.showerror("添加失败", "学号已存在")
            return
        self.clear_form()
        self._changed()

    def update_student(self):
        if not self.selected_student_id:
            messagebox.showwarning("提示", "请先选择要修改的学生")
            return
        data = self.validate_form()
        if not data:
            return
        try:
            database.update_student(self.selected_student_id, *data)
        except sqlite3.IntegrityError:
            messagebox.showerror("修改失败", "学号已存在或数据不合法")
            return
        self.clear_form()
        self._changed()

    def delete_student(self):
        if not self.selected_student_id:
            messagebox.showwarning("提示", "请先选择要删除的学生")
            return
        if not messagebox.askyesno("确认删除", "删除学生会同步删除相关成绩，是否继续？"):
            return
        database.delete_student(self.selected_student_id)
        self.clear_form()
        self._changed()

    def on_select(self, _event):
        selected = self.tree.selection()
        if not selected:
            return
        values = self.tree.item(selected[0], "values")
        self.selected_student_id = values[0]
        self.student_id_var.set(values[0])
        self.name_var.set(values[1])
        self.class_var.set(values[2])

    def clear_form(self):
        self.selected_student_id = None
        self.student_id_var.set("")
        self.name_var.set("")
        self.class_var.set("")
        self.tree.selection_remove(self.tree.selection())

    def refresh(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for row in database.get_students():
            self.tree.insert(
                "",
                tk.END,
                values=(row["student_id"], row["name"], row["class_name"]),
            )

    def _changed(self):
        self.refresh()
        if self.on_data_changed:
            self.on_data_changed()
