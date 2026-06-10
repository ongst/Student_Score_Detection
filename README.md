# 学生成绩分析与预警系统

这是一个基于 Python Tkinter 的桌面端学生成绩分析与预警系统，使用 SQLite 存储数据，使用 Matplotlib 绘制成绩分布图，使用 OpenPyXL 导出 Excel 成绩报表。

## 运行环境

- Python 3.8+
- Tkinter
- SQLite3
- Matplotlib
- OpenPyXL

安装依赖：

```bash
pip install -r requirements.txt
```

启动系统：

```bash
python main.py
```

首次运行会在项目目录下自动创建 `student_scores.db` 数据库文件。

运行核心逻辑冒烟测试：

```bash
python test_core_logic.py
```

## 功能模块

### 学生管理

- 添加学生信息：学号、姓名、班级
- 修改学生信息
- 删除学生信息
- 表格展示全部学生
- 删除学生时同步删除该学生相关成绩

### 课程管理

- 添加课程信息：课程编号、课程名、学分
- 修改课程信息
- 删除课程信息
- 表格展示全部课程
- 删除课程时同步删除该课程相关成绩

### 成绩录入

- 选择学生和课程录入成绩
- 成绩范围为 0 到 100
- 同一学生同一课程只能有一条成绩记录
- 再次录入同一学生同一课程成绩时自动更新
- 支持删除成绩记录

### 成绩分析

- 按课程统计成绩分布
- 分数段包括：0-59、60-69、70-79、80-89、90-100
- 使用 Matplotlib 柱状图展示各分数段人数
- 自动计算学生平均分和 GPA
- 支持按班级查看平均分排名
- 支持导出 Excel 成绩报表

### 学业预警

- 自动筛选平均分低于 60 分的学生
- 在预警列表中高亮显示
- 进入或刷新预警页时弹窗提示预警名单
- 无预警学生时提示当前暂无需学业预警学生
- 支持导出 Excel 成绩报表

## 数据库设计

### students 学生表

| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| student_id | TEXT PRIMARY KEY | 学号 |
| name | TEXT NOT NULL | 姓名 |
| class_name | TEXT NOT NULL | 班级 |

### courses 课程表

| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| course_id | TEXT PRIMARY KEY | 课程编号 |
| course_name | TEXT NOT NULL | 课程名 |
| credit | REAL NOT NULL | 学分 |

### scores 成绩表

| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| score_id | INTEGER PRIMARY KEY AUTOINCREMENT | 成绩 ID |
| student_id | TEXT | 学号，外键 |
| course_id | TEXT | 课程编号，外键 |
| score | REAL NOT NULL | 成绩 |

成绩表包含 `UNIQUE(student_id, course_id)` 约束，保证同一学生同一课程只有一条成绩记录。

## GPA 规则

| 成绩范围 | 绩点 |
| --- | --- |
| 90-100 | 4.0 |
| 80-89 | 3.0 |
| 70-79 | 2.0 |
| 60-69 | 1.0 |
| 0-59 | 0 |

计算公式：

```text
GPA = Σ(课程绩点 × 课程学分) / Σ课程学分
```

平均分只统计已经录入成绩的课程，未录入课程不按 0 分计算。

## 文件结构

```text
main.py              程序入口和主窗口
database.py          数据库初始化与数据操作
student_manager.py   学生管理界面
course_manager.py    课程管理界面
score_manager.py     成绩录入界面
analysis_manager.py  成绩分析、GPA、排名和图表
warning_manager.py   学业预警界面
exporter.py          Excel 导出
test_core_logic.py   数据库、统计、预警和导出的冒烟测试
requirements.txt     依赖文件
README.md            项目说明
```

## 测试建议

- 添加重复学号或课程编号，应提示错误。
- 输入空值、非法学分、非法成绩，应提示错误。
- 同一学生同一课程重复录入成绩，应更新原成绩。
- 录入边界成绩 0、59、60、69、70、79、80、89、90、100 后，成绩分布应统计正确。
- 平均分低于 60 的学生应出现在学业预警页。
- Excel 导出文件应包含学号、姓名、班级、各科成绩、平均分、GPA、是否预警。
