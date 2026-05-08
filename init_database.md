
"""
init_data.py — Comprehensive Database Seed Script
=================================================
Tuân thủ CHÍNH XÁC: models.py + tất cả 15 schema files trong schemas/
- 3 admin, 5 instructor, 20 student = 28 users
- 7 public courses × 4 modules × 4 lessons = 112 lessons
- 60-80 enrollments, Progress, Quiz, QuizAttempt
- AssessmentSession, Conversation, Class, Recommendation
- 3-5 personal courses for students
"""

import asyncio
import json
import random
import uuid
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple

from passlib.context import CryptContext
from faker import Faker

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import get_settings
from database import init_db
from models.models import (
    User, Course, Module, Lesson,
    EmbeddedModule, EmbeddedLesson, LessonProgressItem,
    Enrollment, Progress,
    Quiz, QuizAttempt,
    AssessmentSession, Conversation, Class, Recommendation,
    RefreshToken,   # auth.py: RefreshToken collection
)
from beanie.operators import Eq, In, Set

# ─── helpers ───────────────────────────────────────────────────────────────────
fake = Faker("vi_VN")
fake.seed_instance(42)
random.seed(42)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def gid() -> str:
    return str(uuid.uuid4())

def hp(password: str) -> str:
    return pwd_context.hash(password)

def now() -> datetime:
    return datetime.now(timezone.utc)

def past(days=0, hours=0, minutes=0) -> datetime:
    return now() - timedelta(days=days, hours=hours, minutes=minutes)

def future(days=0, hours=0) -> datetime:
    return now() + timedelta(days=days, hours=hours)

def make_resource(rtype: str, title: str, url: str, size_mb: float = 0.0, desc: str = "") -> dict:
    """ResourceItem theo learning.py: {id, title, type, url, size_mb, description}
    type: pdf | slide | code | video | link
    """
    return {"id": gid(), "title": title, "type": rtype, "url": url, "size_mb": size_mb, "description": desc}

def make_module_outcome(outcome: str, skill_tag: str, is_mandatory: bool = True) -> dict:
    """learning.py LearningOutcome: {id, outcome, skill_tag, is_mandatory}"""
    return {"id": gid(), "outcome": outcome, "skill_tag": skill_tag, "is_mandatory": is_mandatory}

def make_course_outcome(description: str, skill_tag: str) -> dict:
    """course.py LearningOutcome: {description, skill_tag}  — NO id"""
    return {"description": description, "skill_tag": skill_tag}

def make_question(qtype: str, text: str, options: List[str], correct: str,
                  explanation: str, points: int, is_mandatory: bool, order: int) -> dict:
    """Quiz question theo quiz.py QuestionCreate + Quiz.questions structure"""
    return {
        "id": gid(),
        "type": qtype,               # multiple_choice | fill_in_blank | true_false
        "question_text": text,
        "options": options,
        "correct_answer": correct,   # string index "0","1","2","3" or text
        "explanation": explanation,
        "points": points,
        "is_mandatory": is_mandatory,
        "order": order,
    }

def make_assessment_question(qtext: str, qtype: str, difficulty: str, skill_tag: str,
                              points: int, options: List[str], hint: str) -> dict:
    """assessment.py AssessmentQuestion schema"""
    return {
        "question_id": gid(),
        "question_text": qtext,
        "question_type": qtype,      # multiple_choice | fill_in_blank | drag_and_drop
        "difficulty": difficulty,    # easy | medium | hard
        "skill_tag": skill_tag,
        "points": points,
        "options": options if options else None,
        "correct_answer_hint": hint,
    }

# ─── USER TEMPLATES ────────────────────────────────────────────────────────────
ADMIN_USERS = [
    {"full_name": "Nguyễn Quản Trị Viên", "email": "admin@ailearning.vn", "avatar_url": "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150", "bio": "Quản trị viên hệ thống AI Learning Platform.", "learning_preferences": ["AI/ML", "Management"]},
    {"full_name": "Trần Thị Admin", "email": "admin2@ailearning.vn", "avatar_url": "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=150", "bio": "Admin phụ trách nội dung và khóa học.", "learning_preferences": ["Programming", "Education"]},
    {"full_name": "Lê Văn System", "email": "system@ailearning.vn", "avatar_url": "https://images.unsplash.com/photo-1519345182560-3f2917c472ef?w=150", "bio": "Admin phụ trách kỹ thuật và hạ tầng.", "learning_preferences": ["DevOps", "Cloud"]},
]

INSTRUCTOR_USERS = [
    {"full_name": "Phạm Minh Tuấn", "email": "tuan.pham@ailearning.vn", "avatar_url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150", "bio": "Chuyên gia Python và Machine Learning với 10 năm kinh nghiệm tại các công ty công nghệ hàng đầu. Đã đào tạo hơn 5000 học viên.", "learning_preferences": ["Python", "ML", "Data Science"]},
    {"full_name": "Nguyễn Thị Lan Anh", "email": "lananh@ailearning.vn", "avatar_url": "https://images.unsplash.com/photo-1580489944761-15a19d654956?w=150", "bio": "Senior Frontend Developer với 8 năm kinh nghiệm, chuyên gia React và JavaScript. Đã tham gia nhiều dự án quốc tế.", "learning_preferences": ["JavaScript", "React", "Frontend"]},
    {"full_name": "Hoàng Đức Mạnh", "email": "manh.hoang@ailearning.vn", "avatar_url": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=150", "bio": "Data Scientist tại tập đoàn lớn, chuyên về phân tích dữ liệu và xây dựng mô hình dự đoán. Tác giả nhiều bài báo khoa học.", "learning_preferences": ["Data Science", "Statistics", "Python"]},
    {"full_name": "Vũ Thanh Hương", "email": "huong.vu@ailearning.vn", "avatar_url": "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=150", "bio": "Chuyên gia tiếng Anh IELTS 8.5, 12 năm giảng dạy tại các trung tâm uy tín. Phương pháp giảng dạy hiệu quả và thực tế.", "learning_preferences": ["English", "IELTS", "Communication"]},
    {"full_name": "Bùi Quốc Hùng", "email": "hung.bui@ailearning.vn", "avatar_url": "https://images.unsplash.com/photo-1463453091185-61582044d556?w=150", "bio": "Marketing Director với 15 năm kinh nghiệm, chuyên về Digital Marketing và Growth Hacking. Đã giúp hàng chục startup tăng trưởng.", "learning_preferences": ["Marketing", "Business", "Growth"]},
]

STUDENT_USERS = [
    {"full_name": "Nguyễn Văn An", "email": "an.nguyen@gmail.com", "avatar_url": "https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=150", "bio": "Sinh viên CNTT năm 3, đam mê lập trình và AI.", "learning_preferences": ["Programming", "AI/ML", "Python"]},
    {"full_name": "Trần Thị Bình", "email": "binh.tran@gmail.com", "avatar_url": "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=150", "bio": "Kỹ sư cơ khí muốn chuyển ngành sang lập trình.", "learning_preferences": ["Python", "Data Science"]},
    {"full_name": "Lê Minh Cường", "email": "cuong.le@gmail.com", "avatar_url": "https://images.unsplash.com/photo-1599566150163-29194dcaad36?w=150", "bio": "Fresher backend developer đang học nâng cao.", "learning_preferences": ["Programming", "Backend", "API"]},
    {"full_name": "Phạm Thị Dung", "email": "dung.pham@gmail.com", "avatar_url": "https://images.unsplash.com/photo-1507101105822-7472b28e22ac?w=150", "bio": "Nhân viên văn phòng quan tâm đến Data Analysis.", "learning_preferences": ["Data Science", "Excel", "Business"]},
    {"full_name": "Hoàng Văn Em", "email": "em.hoang@gmail.com", "avatar_url": "https://images.unsplash.com/photo-1531746020798-e6953c6e8e04?w=150", "bio": "Sinh viên kinh tế muốn học lập trình để tăng giá trị bản thân.", "learning_preferences": ["Python", "Business", "Finance"]},
    {"full_name": "Vũ Thị Phương", "email": "phuong.vu@gmail.com", "avatar_url": "https://images.unsplash.com/photo-1551836022-deb4988cc6c0?w=150", "bio": "Marketer muốn học Data để phân tích hiệu quả campaign.", "learning_preferences": ["Marketing", "Data Science", "Analytics"]},
    {"full_name": "Đặng Quốc Giang", "email": "giang.dang@gmail.com", "avatar_url": "https://images.unsplash.com/photo-1492562080023-ab3db95bfbce?w=150", "bio": "JavaScript developer 2 năm kinh nghiệm muốn học React.", "learning_preferences": ["JavaScript", "React", "Frontend"]},
    {"full_name": "Bùi Thị Hoa", "email": "hoa.bui@gmail.com", "avatar_url": "https://images.unsplash.com/photo-1502685104226-ee32379fefbe?w=150", "bio": "Nhà quản lý cần học kỹ năng phân tích dữ liệu.", "learning_preferences": ["Business", "Excel", "Leadership"]},
    {"full_name": "Ngô Văn Hùng", "email": "hung.ngo@gmail.com", "avatar_url": "https://images.unsplash.com/photo-1566492031773-4f4e44671857?w=150", "bio": "Kỹ sư CNTT quan tâm đến Machine Learning.", "learning_preferences": ["ML", "Python", "Mathematics"]},
    {"full_name": "Đinh Thị Lan", "email": "lan.dinh@gmail.com", "avatar_url": "https://images.unsplash.com/photo-1487412720507-e7ab37603c6f?w=150", "bio": "Giáo viên Anh văn muốn nâng cao nghiệp vụ kỹ thuật số.", "learning_preferences": ["English", "Digital", "Education"]},
    {"full_name": "Phan Văn Mạnh", "email": "manh.phan@gmail.com", "avatar_url": "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=150", "bio": "Sinh viên năm cuối ngành Khoa học dữ liệu.", "learning_preferences": ["Data Science", "Python", "Statistics"]},
    {"full_name": "Lý Thị Ngọc", "email": "ngoc.ly@gmail.com", "avatar_url": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150", "bio": "Chuyên viên nhân sự tìm hiểu về HR Analytics.", "learning_preferences": ["Business", "Analytics", "Excel"]},
    {"full_name": "Hồ Văn Oanh", "email": "oanh.ho@gmail.com", "avatar_url": "https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?w=150", "bio": "Tự học lập trình sau giờ làm để chuyển nghề.", "learning_preferences": ["Programming", "Python", "Career"]},
    {"full_name": "Đỗ Thị Phúc", "email": "phuc.do@gmail.com", "avatar_url": "https://images.unsplash.com/photo-1508214751196-bcfd4ca60f91?w=150", "bio": "Product manager muốn hiểu kỹ thuật để làm việc với dev.", "learning_preferences": ["Programming", "Product", "Agile"]},
    {"full_name": "Trương Văn Quân", "email": "quan.truong@gmail.com", "avatar_url": "https://images.unsplash.com/photo-1480455624313-e29b44bbfde1?w=150", "bio": "Fresher muốn tìm việc làm frontend developer.", "learning_preferences": ["JavaScript", "HTML", "CSS", "React"]},
    {"full_name": "Nguyễn Thị Hằng", "email": "hang.nguyen@gmail.com", "avatar_url": "https://images.unsplash.com/photo-1524504388940-b1c1722653e1?w=150", "bio": "Nhân viên ngân hàng muốn ứng dụng Data vào tài chính.", "learning_preferences": ["Finance", "Python", "Data Science"]},
    {"full_name": "Mai Văn Sơn", "email": "son.mai@gmail.com", "avatar_url": "https://images.unsplash.com/photo-1561406636-b80293969660?w=150", "bio": "Doanh nhân trẻ muốn học digital marketing.", "learning_preferences": ["Marketing", "Business", "Growth"]},
    {"full_name": "Lê Thị Thu", "email": "thu.le@gmail.com", "avatar_url": "https://images.unsplash.com/photo-1517841905240-472988babdf9?w=150", "bio": "Giáo viên THPT muốn ứng dụng công nghệ trong dạy học.", "learning_preferences": ["Education", "Digital", "Programming"]},
    {"full_name": "Phùng Văn Thắng", "email": "thang.phung@gmail.com", "avatar_url": "https://images.unsplash.com/photo-1570295999919-56ceb5ecca61?w=150", "bio": "Backend developer muốn chuyển sang ML/AI.", "learning_preferences": ["ML", "Python", "API"]},
    {"full_name": "Đoàn Thị Uyên", "email": "uyen.doan@gmail.com", "avatar_url": "https://images.unsplash.com/photo-1558203728-00f45181dd84?w=150", "bio": "Sinh viên Marketing muốn học Growth Hacking.", "learning_preferences": ["Marketing", "Analytics", "Social Media"]},
]

# ─── COURSE CATALOG ─────────────────────────────────────────────────────────────
# 7 public courses × 4 modules × 4 lessons
COURSE_CATALOG = [
    {
        "title": "Lập trình Python từ Cơ bản đến Nâng cao",
        "description": "Khóa học toàn diện về lập trình Python, từ cú pháp cơ bản đến nâng cao. Học viên sẽ được học OOP, xử lý dữ liệu với Pandas, phát triển web với FastAPI, và Machine Learning cơ bản. Bao gồm 4 modules với 16 bài học chi tiết, bài tập thực hành và project cuối khóa.",
        "category": "Programming",
        "level": "Beginner",
        "thumbnail_url": "https://images.unsplash.com/photo-1526379095098-d400fd0bf935?w=800&h=450",
        "preview_video_url": "https://www.youtube.com/watch?v=rfscVS0vtbw",
        "avg_rating": 4.8,
        "learning_outcomes": [
            make_course_outcome("Nắm vững cú pháp Python: biến, vòng lặp, hàm, exception handling", "python-basics"),
            make_course_outcome("Lập trình hướng đối tượng: class, inheritance, polymorphism", "python-oop"),
            make_course_outcome("Xử lý dữ liệu với Pandas: DataFrame, cleaning, visualization", "python-pandas"),
            make_course_outcome("Phát triển REST API với FastAPI: endpoints, validation, database", "python-fastapi"),
            make_course_outcome("Machine Learning cơ bản: regression, classification, scikit-learn", "python-ml"),
        ],
        "prerequisites": ["Kiến thức máy tính cơ bản", "Không cần kinh nghiệm lập trình"],
        "instr_idx": 0,
        "modules": [
            {
                "title": "Module 1: Python Cơ bản và Môi trường",
                "description": "Cài đặt Python, làm quen với cú pháp cơ bản, biến, kiểu dữ liệu và câu lệnh điều khiển.",
                "difficulty": "Basic",
                "learning_outcomes": [
                    make_module_outcome("Cài đặt Python 3.11+ và VS Code thành thạo", "python-setup", True),
                    make_module_outcome("Khai báo biến với đầy đủ kiểu dữ liệu", "python-variables", True),
                    make_module_outcome("Viết cấu trúc điều khiển if/else, for, while", "python-control-flow", True),
                    make_module_outcome("Sử dụng Python REPL và debug cơ bản", "python-debugging", False),
                ],
                "lessons": [
                    {"title": "Cài đặt Python và VS Code", "desc": "Hướng dẫn cài đặt Python 3.11, pip, venv và cấu hình VS Code với extensions", "type": "mixed", "mins": 35, "video": "https://www.youtube.com/watch?v=YYXdXT2l-Gg", "objectives": ["Cài Python từ python.org", "Cài VS Code + Python extension", "Tạo virtual environment đầu tiên"], "has_quiz": True},
                    {"title": "Biến và Kiểu dữ liệu", "desc": "String, int, float, bool, list, dict, tuple, set — khai báo và thao tác cơ bản", "type": "code", "mins": 45, "video": "https://www.youtube.com/watch?v=cQT33yu9pY8", "objectives": ["Khai báo biến đúng naming convention", "Sử dụng string methods", "Type conversion"], "has_quiz": True},
                    {"title": "Câu lệnh điều kiện và vòng lặp", "desc": "if/elif/else, for loop, while loop, break, continue, list comprehension", "type": "code", "mins": 50, "video": "https://www.youtube.com/watch?v=PqFKRqpHrjw", "objectives": ["Viết if/elif/else đúng logic", "Duyệt list với for loop", "List comprehension cơ bản"], "has_quiz": True},
                    {"title": "Hàm và Modules", "desc": "Định nghĩa hàm, tham số, return value, *args, **kwargs, import modules", "type": "code", "mins": 55, "video": "https://www.youtube.com/watch?v=9Os0o3wzS_I", "objectives": ["Viết hàm với parameter đúng cách", "Hiểu scope và closure", "Import thư viện chuẩn"], "has_quiz": False},
                ],
            },
            {
                "title": "Module 2: Lập trình Hướng đối tượng (OOP)",
                "description": "Class, object, kế thừa, đa hình, encapsulation và các design pattern cơ bản trong Python.",
                "difficulty": "Intermediate",
                "learning_outcomes": [
                    make_module_outcome("Định nghĩa class với __init__, properties và methods", "python-class", True),
                    make_module_outcome("Implement kế thừa và method overriding", "python-inheritance", True),
                    make_module_outcome("Áp dụng encapsulation với private/protected attributes", "python-encapsulation", False),
                    make_module_outcome("Sử dụng magic methods (__str__, __len__, __eq__)", "python-magic-methods", False),
                ],
                "lessons": [
                    {"title": "Class và Object trong Python", "desc": "Cách định nghĩa class, tạo object, __init__ method và instance variables", "type": "code", "mins": 50, "video": "https://www.youtube.com/watch?v=apACNr7DC_s", "objectives": ["Tạo class đơn giản", "Phân biệt class và instance variables", "Sử dụng self"], "has_quiz": True},
                    {"title": "Kế thừa và Đa hình", "desc": "Single inheritance, multiple inheritance, method overriding, super()", "type": "code", "mins": 55, "video": "https://www.youtube.com/watch?v=Ej_02ICOIgs", "objectives": ["Tạo class con kế thừa class cha", "Override method cơ bản", "Dùng super() đúng cách"], "has_quiz": True},
                    {"title": "Encapsulation và Properties", "desc": "Private/protected, @property decorator, getter/setter, @staticmethod, @classmethod", "type": "mixed", "mins": 45, "video": "https://www.youtube.com/watch?v=jCzT9XFZ5bw", "objectives": ["Dùng _ và __ convention", "Viết property decorator", "Phân biệt static vs class method"], "has_quiz": False},
                    {"title": "Magic Methods và Operators", "desc": "__str__, __repr__, __len__, __eq__, __lt__, operator overloading", "type": "code", "mins": 40, "video": "https://www.youtube.com/watch?v=z1mlmR0ZzYo", "objectives": ["Implement __str__ và __repr__", "Overload toán tử cơ bản"], "has_quiz": False},
                ],
            },
            {
                "title": "Module 3: Xử lý Dữ liệu với Pandas",
                "description": "Đọc dữ liệu từ CSV/Excel, làm sạch dữ liệu, phân tích và visualization với Matplotlib.",
                "difficulty": "Intermediate",
                "learning_outcomes": [
                    make_module_outcome("Đọc và ghi dữ liệu CSV, Excel, JSON với Pandas", "pandas-io", True),
                    make_module_outcome("Làm sạch dữ liệu: xử lý null, duplicate, outlier", "pandas-cleaning", True),
                    make_module_outcome("Phân tích dữ liệu: groupby, pivot_table, merge", "pandas-analysis", True),
                    make_module_outcome("Vẽ biểu đồ với Matplotlib và Seaborn", "data-visualization", False),
                ],
                "lessons": [
                    {"title": "Introduction to Pandas", "desc": "Series, DataFrame, đọc file CSV/Excel, index và column operations", "type": "code", "mins": 60, "video": "https://www.youtube.com/watch?v=vmEHCJofslg", "objectives": ["Tạo DataFrame từ dict và list", "Đọc file CSV với read_csv()", "Truy cập dữ liệu với loc/iloc"], "has_quiz": True},
                    {"title": "Data Cleaning với Pandas", "desc": "Xử lý missing values, drop duplicates, fillna, dtype conversion, string cleaning", "type": "code", "mins": 65, "video": "https://www.youtube.com/watch?v=ZOX18HfLHGQ", "objectives": ["Tìm và xử lý NaN values", "Remove duplicates", "Chuẩn hóa kiểu dữ liệu"], "has_quiz": True},
                    {"title": "Data Analysis: GroupBy và Aggregation", "desc": "groupby, agg, pivot_table, merge, concat, apply lambda functions", "type": "code", "mins": 70, "video": "https://www.youtube.com/watch?v=txMdrV1Ut64", "objectives": ["Tổng hợp dữ liệu với groupby", "Tạo pivot table", "Merge nhiều DataFrame"], "has_quiz": True},
                    {"title": "Data Visualization", "desc": "Matplotlib: bar, line, scatter, histogram. Seaborn: heatmap, boxplot", "type": "mixed", "mins": 55, "video": "https://www.youtube.com/watch?v=yZTBMMdPOww", "objectives": ["Vẽ biểu đồ cơ bản", "Customize màu sắc và labels"], "has_quiz": False},
                ],
            },
            {
                "title": "Module 4: REST API với FastAPI",
                "description": "Phát triển REST API chuyên nghiệp với FastAPI, Pydantic validation, SQLAlchemy và deployment.",
                "difficulty": "Advanced",
                "learning_outcomes": [
                    make_module_outcome("Xây dựng CRUD API với FastAPI và Pydantic", "fastapi-crud", True),
                    make_module_outcome("Implement JWT authentication và authorization", "fastapi-auth", True),
                    make_module_outcome("Kết nối database với SQLAlchemy async", "fastapi-database", True),
                    make_module_outcome("Deploy API với Docker và Render/Railway", "fastapi-deployment", False),
                ],
                "lessons": [
                    {"title": "FastAPI Basics và Pydantic", "desc": "Setup FastAPI project, route decorators, Pydantic models, request/response validation", "type": "code", "mins": 65, "video": "https://www.youtube.com/watch?v=0RS9W8MtZe4", "objectives": ["Tạo FastAPI app cơ bản", "Định nghĩa Pydantic models", "Viết GET/POST endpoints"], "has_quiz": True},
                    {"title": "CRUD Operations và Routing", "desc": "Path params, query params, request body, response models, dependency injection", "type": "code", "mins": 70, "video": "https://www.youtube.com/watch?v=QH-1EknMEP8", "objectives": ["Implement đầy đủ CRUD endpoints", "Sử dụng Depends()", "HTTPException handling"], "has_quiz": True},
                    {"title": "Authentication với JWT", "desc": "JWT tokens, OAuth2, bcrypt password hashing, middleware, CORS", "type": "code", "mins": 75, "video": "https://www.youtube.com/watch?v=6hTRw_HK3Ts", "objectives": ["Implement login/register", "JWT access và refresh token", "Protect routes với dependency"], "has_quiz": True},
                    {"title": "Database Integration và Deployment", "desc": "SQLAlchemy async, alembic migrations, Docker Compose, deployment", "type": "mixed", "mins": 85, "video": "https://www.youtube.com/watch?v=2g1ZjA6zHRo", "objectives": ["Kết nối PostgreSQL với SQLAlchemy", "Tạo migration với Alembic", "Containerize với Docker"], "has_quiz": False},
                ],
            },
        ],
    },
    {
        "title": "JavaScript Modern - ES6+ và React",
        "description": "Học JavaScript hiện đại từ ES6+ đến React framework. Master async/await, Promises, React Hooks, Context API và Redux Toolkit để xây dựng ứng dụng web production-ready.",
        "category": "Programming",
        "level": "Intermediate",
        "thumbnail_url": "https://images.unsplash.com/photo-1579468118864-1b9ea3c0db4a?w=800&h=450",
        "preview_video_url": "https://www.youtube.com/watch?v=W6NZfCO5SIk",
        "avg_rating": 4.7,
        "learning_outcomes": [
            make_course_outcome("Sử dụng thành thạo ES6+: arrow functions, destructuring, spread/rest, modules", "javascript-es6"),
            make_course_outcome("Xử lý bất đồng bộ với Promises, async/await và Fetch API", "javascript-async"),
            make_course_outcome("Xây dựng React components với Hooks (useState, useEffect, useContext)", "react-hooks"),
            make_course_outcome("Quản lý state với Redux Toolkit và RTK Query", "react-redux"),
        ],
        "prerequisites": ["Biết HTML/CSS cơ bản", "Hiểu JavaScript căn bản (var, function, DOM)"],
        "instr_idx": 1,
        "modules": [
            {
                "title": "Module 1: JavaScript ES6+ Hiện đại",
                "description": "let/const, arrow functions, template literals, destructuring, spread/rest, modules và Symbol.",
                "difficulty": "Basic",
                "learning_outcomes": [
                    make_module_outcome("Sử dụng let/const và hiểu block scoping", "js-scoping", True),
                    make_module_outcome("Viết arrow functions và template literals thành thạo", "js-syntax", True),
                    make_module_outcome("Destructuring arrays và objects phức tạp", "js-destructuring", True),
                    make_module_outcome("Chia nhỏ code với ES6 modules (import/export)", "js-modules", False),
                ],
                "lessons": [
                    {"title": "let, const và Arrow Functions", "desc": "Block scoping, TDZ, arrow functions, implicit return, this binding", "type": "code", "mins": 45, "video": "https://www.youtube.com/watch?v=hdI2bqOjy3c", "objectives": ["Phân biệt var/let/const", "Viết arrow function đúng cú pháp", "Hiểu this trong arrow function"], "has_quiz": True},
                    {"title": "Destructuring và Spread/Rest", "desc": "Array/object destructuring, default values, nested destructuring, spread operator, rest params", "type": "code", "mins": 50, "video": "https://www.youtube.com/watch?v=NIq3qLaHCIs", "objectives": ["Destructuring lồng nhau", "Clone array/object với spread", "Dùng rest params trong hàm"], "has_quiz": True},
                    {"title": "Template Literals và String Methods", "desc": "Tagged templates, multi-line strings, includes, startsWith, padStart", "type": "code", "mins": 35, "video": "https://www.youtube.com/watch?v=DG4obitDvUA", "objectives": ["Viết template literals đúng", "Dùng tagged templates cơ bản"], "has_quiz": False},
                    {"title": "ES6 Modules và Iterators", "desc": "import/export default/named, dynamic import, Symbol, for...of, generators", "type": "code", "mins": 55, "video": "https://www.youtube.com/watch?v=cRHQNNkYi58", "objectives": ["Import/export module", "Viết iterator đơn giản"], "has_quiz": False},
                ],
            },
            {
                "title": "Module 2: Bất đồng bộ và API",
                "description": "Callbacks, Promises, async/await, Fetch API, Axios và error handling",
                "difficulty": "Intermediate",
                "learning_outcomes": [
                    make_module_outcome("Hiểu event loop, call stack và callback queue", "js-event-loop", True),
                    make_module_outcome("Làm việc với Promises: then/catch/finally, Promise.all", "js-promises", True),
                    make_module_outcome("Viết async/await endpoint với xử lý lỗi đúng cách", "js-async-await", True),
                    make_module_outcome("Gọi REST API với Fetch và Axios, xử lý response", "js-fetch", False),
                ],
                "lessons": [
                    {"title": "Event Loop và Callbacks", "desc": "Call stack, Web APIs, event loop, callback hell và các vấn đề", "type": "mixed", "mins": 50, "video": "https://www.youtube.com/watch?v=8aGhZQkoFbQ", "objectives": ["Giải thích event loop", "Nhận biết callback hell"], "has_quiz": True},
                    {"title": "Promises", "desc": "Tạo Promise, then/catch/finally, chaining, Promise.all/race/allSettled", "type": "code", "mins": 55, "video": "https://www.youtube.com/watch?v=DHvZLI7Db8E", "objectives": ["Tạo và consume Promise", "Chain multiple promises", "Error handling với catch"], "has_quiz": True},
                    {"title": "Async/Await", "desc": "async function, await, try/catch, parallel async với Promise.all, top-level await", "type": "code", "mins": 50, "video": "https://www.youtube.com/watch?v=V_Kr9OSfDeU", "objectives": ["Convert Promise sang async/await", "Parallel requests với Promise.all"], "has_quiz": True},
                    {"title": "Fetch API và Axios", "desc": "fetch(), JSON, headers, Axios interceptors, error handling, timeout", "type": "code", "mins": 60, "video": "https://www.youtube.com/watch?v=cuEtnrL9-H0", "objectives": ["Gọi GET/POST API", "Xử lý lỗi network"], "has_quiz": False},
                ],
            },
            {
                "title": "Module 3: React Fundamentals",
                "description": "JSX, components, props, state với useState, side effects với useEffect",
                "difficulty": "Intermediate",
                "learning_outcomes": [
                    make_module_outcome("Viết React components với JSX cú pháp đúng", "react-jsx", True),
                    make_module_outcome("Quản lý state với useState và truyền props", "react-state", True),
                    make_module_outcome("Handle side effects với useEffect và cleanup", "react-effects", True),
                    make_module_outcome("Render lists với key và xử lý conditional rendering", "react-rendering", False),
                ],
                "lessons": [
                    {"title": "React Components và JSX", "desc": "Vite setup, function components, JSX syntax, render list, fragments", "type": "code", "mins": 60, "video": "https://www.youtube.com/watch?v=bMknfKXIFA8", "objectives": ["Tạo React app với Vite", "Viết function component", "JSX rules và expressions"], "has_quiz": True},
                    {"title": "Props và State với useState", "desc": "Props passing, PropTypes, useState hook, controlled components, form handling", "type": "code", "mins": 65, "video": "https://www.youtube.com/watch?v=O6P86uwfdR0", "objectives": ["Truyền props giữa components", "Quản lý form state", "Lifting state up"], "has_quiz": True},
                    {"title": "useEffect và Data Fetching", "desc": "useEffect dependencies, cleanup, fetching API, loading states, error handling", "type": "code", "mins": 70, "video": "https://www.youtube.com/watch?v=0ZJgIjIuY7U", "objectives": ["Fetch data với useEffect", "Handle loading và error states", "Cleanup subscriptions"], "has_quiz": True},
                    {"title": "useContext và Custom Hooks", "desc": "Context API, createContext, useProvider, viết custom hooks để reuse logic", "type": "code", "mins": 65, "video": "https://www.youtube.com/watch?v=5LrDIWkK_Bc", "objectives": ["Tạo và consume Context", "Viết custom hook useLocalStorage"], "has_quiz": False},
                ],
            },
            {
                "title": "Module 4: Redux Toolkit và Advanced React",
                "description": "Redux Toolkit, RTK Query, React Router v6, performance optimization",
                "difficulty": "Advanced",
                "learning_outcomes": [
                    make_module_outcome("Cấu hình Redux store với createSlice và configureStore", "redux-toolkit", True),
                    make_module_outcome("Fetch và cache API data với RTK Query", "rtk-query", True),
                    make_module_outcome("Cài đặt routing với React Router v6", "react-router", True),
                    make_module_outcome("Optimize performance với memo, useMemo, useCallback", "react-performance", False),
                ],
                "lessons": [
                    {"title": "Redux Toolkit Basics", "desc": "createSlice, reducers, actions, configureStore, React-Redux Provider, useSelector/useDispatch", "type": "code", "mins": 75, "video": "https://www.youtube.com/watch?v=bbkBuqC1rU4", "objectives": ["Setup Redux store", "Viết slice với actions", "Connect component với Redux"], "has_quiz": True},
                    {"title": "RTK Query Data Fetching", "desc": "createApi, endpoints, useQuery, useMutation, cache invalidation, polling", "type": "code", "mins": 80, "video": "https://www.youtube.com/watch?v=HyZzCHgG3AY", "objectives": ["Tạo API slice", "Fetch data với useQuery", "Mutate data với useMutation"], "has_quiz": True},
                    {"title": "React Router v6", "desc": "BrowserRouter, Routes, Route, Link, NavLink, useParams, useNavigate, protected routes", "type": "code", "mins": 65, "video": "https://www.youtube.com/watch?v=Ul3y1LXxzdU", "objectives": ["Cài đặt navigation cơ bản", "Dynamic routes với params", "Protected routes pattern"], "has_quiz": False},
                    {"title": "Performance Optimization", "desc": "React.memo, useMemo, useCallback, lazy loading, Suspense, code splitting", "type": "mixed", "mins": 70, "video": "https://www.youtube.com/watch?v=uojLJFt9SzY", "objectives": ["Tránh re-render không cần thiết", "Lazy load components"], "has_quiz": False},
                ],
            },
        ],
    },
    {
        "title": "Data Science với Python và Pandas",
        "description": "Phân tích dữ liệu chuyên sâu: EDA, feature engineering, machine learning pipeline và data storytelling. Học với datasets thực tế từ Kaggle.",
        "category": "Data Science",
        "level": "Intermediate",
        "thumbnail_url": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=800&h=450",
        "preview_video_url": "https://www.youtube.com/watch?v=LHBE6Q9XlzI",
        "avg_rating": 4.6,
        "learning_outcomes": [
            make_course_outcome("Thực hiện EDA toàn diện: describe, correlation, distribution", "eda-analysis"),
            make_course_outcome("Feature engineering: encoding, scaling, imputation", "feature-engineering"),
            make_course_outcome("Xây dựng ML pipeline với scikit-learn", "ml-pipeline"),
            make_course_outcome("Kể chuyện bằng dữ liệu với Matplotlib và Plotly", "data-storytelling"),
        ],
        "prerequisites": ["Python cơ bản", "Kiến thức Pandas cơ bản"],
        "instr_idx": 2,
        "modules": [
            {
                "title": "Module 1: Exploratory Data Analysis (EDA)",
                "description": "Khám phá và hiểu dữ liệu với thống kê mô tả, missing value analysis và correlation matrix.",
                "difficulty": "Basic",
                "learning_outcomes": [
                    make_module_outcome("Thực hiện statistical summary với describe()", "stats-summary", True),
                    make_module_outcome("Phân tích phân phối dữ liệu với histogram và boxplot", "distribution-analysis", True),
                    make_module_outcome("Tìm correlation giữa các features", "correlation-analysis", True),
                    make_module_outcome("Detect và xử lý outliers", "outlier-detection", False),
                ],
                "lessons": [
                    {"title": "Loading và Overview Dataset", "desc": "Đọc CSV/Excel từ URL, info(), describe(), dtypes, value_counts()", "type": "code", "mins": 50, "video": "https://www.youtube.com/watch?v=e60ItwlZTKM", "objectives": ["Load Titanic dataset", "Kiểm tra shape, dtypes", "Tính basic statistics"], "has_quiz": True},
                    {"title": "Phân tích Missing Values", "desc": "isnull, heatmap missing, strategies: drop, fillna mean/median/mode, KNNImputer", "type": "code", "mins": 55, "video": "https://www.youtube.com/watch?v=P_iMSYIBFGo", "objectives": ["Visualize missing pattern", "Chọn strategy phù hợp"], "has_quiz": True},
                    {"title": "Distribution và Outlier Analysis", "desc": "Histogram, KDE, boxplot, IQR method, Z-score, log transformation", "type": "mixed", "mins": 60, "video": "https://www.youtube.com/watch?v=8QaS2dBT_E4", "objectives": ["Đánh giá phân phối features", "Detect outliers với IQR"], "has_quiz": True},
                    {"title": "Correlation và Heatmap", "desc": "corr(), heatmap, pairplot, scatter matrix, variance inflation factor", "type": "code", "mins": 50, "video": "https://www.youtube.com/watch?v=ioN1jcWxbv8", "objectives": ["Tạo correlation matrix", "Đọc heatmap đúng cách"], "has_quiz": False},
                ],
            },
            {
                "title": "Module 2: Feature Engineering",
                "description": "Biến đổi dữ liệu: encoding categorical, scaling numerical, tạo new features",
                "difficulty": "Intermediate",
                "learning_outcomes": [
                    make_module_outcome("Label encoding và One-Hot encoding categorical features", "categorical-encoding", True),
                    make_module_outcome("StandardScaler, MinMaxScaler cho numerical features", "feature-scaling", True),
                    make_module_outcome("Tạo polynomial features và interaction features", "feature-creation", False),
                    make_module_outcome("Feature selection với correlation và importance scores", "feature-selection", True),
                ],
                "lessons": [
                    {"title": "Categorical Encoding", "desc": "LabelEncoder, OrdinalEncoder, OneHotEncoder, pd.get_dummies, target encoding", "type": "code", "mins": 55, "video": "https://www.youtube.com/watch?v=AznKsPh8PkE", "objectives": ["Transform categorical columns", "Tránh dummy variable trap"], "has_quiz": True},
                    {"title": "Feature Scaling", "desc": "StandardScaler, MinMaxScaler, RobustScaler, khi nào dùng cái nào", "type": "code", "mins": 45, "video": "https://www.youtube.com/watch?v=0gwJ82vNAtE", "objectives": ["Scale features đúng phương pháp", "Fit trên train, transform test"], "has_quiz": True},
                    {"title": "Feature Creation và Interaction", "desc": "Binning, polynomial features, date features, ratio features, text length", "type": "code", "mins": 60, "video": "https://www.youtube.com/watch?v=Nj5dNIJz9d4", "objectives": ["Tạo features mới từ existing", "Binning continuous variables"], "has_quiz": False},
                    {"title": "Feature Selection", "desc": "SelectKBest, RFE, feature_importances_, VIF, Mutual Information", "type": "code", "mins": 55, "video": "https://www.youtube.com/watch?v=kA4mD3y4aqA", "objectives": ["Chọn top features", "Remove redundant features"], "has_quiz": False},
                ],
            },
            {
                "title": "Module 3: Machine Learning với scikit-learn",
                "description": "Train/test split, classification, regression, cross-validation và hyperparameter tuning",
                "difficulty": "Advanced",
                "learning_outcomes": [
                    make_module_outcome("Implement classification với Logistic Regression và Random Forest", "ml-classification", True),
                    make_module_outcome("Implement regression với Linear Regression và XGBoost", "ml-regression", True),
                    make_module_outcome("Đánh giá model với accuracy, F1, AUC-ROC, RMSE", "ml-evaluation", True),
                    make_module_outcome("Optimize hyperparameters với GridSearchCV", "hyperparameter-tuning", False),
                ],
                "lessons": [
                    {"title": "ML Pipeline và Train/Test Split", "desc": "Pipeline, ColumnTransformer, train_test_split, stratified split, cross_val_score", "type": "code", "mins": 65, "video": "https://www.youtube.com/watch?v=pqNCD_5r0IU", "objectives": ["Xây dựng Pipeline hoàn chỉnh", "Stratified split đúng cách"], "has_quiz": True},
                    {"title": "Classification Models", "desc": "Logistic Regression, Decision Tree, Random Forest, SVM — fit, predict, evaluate", "type": "code", "mins": 70, "video": "https://www.youtube.com/watch?v=GqCSaC137b8", "objectives": ["Train classification model", "So sánh nhiều algorithms"], "has_quiz": True},
                    {"title": "Regression Models", "desc": "Linear, Ridge, Lasso, RandomForest, XGBoost regression — MSE, RMSE, R²", "type": "code", "mins": 65, "video": "https://www.youtube.com/watch?v=3CC4N4z3GJc", "objectives": ["Implement regression pipeline", "Interpret RMSE và R²"], "has_quiz": True},
                    {"title": "Hyperparameter Tuning", "desc": "GridSearchCV, RandomizedSearchCV, Optuna basics, learning curves", "type": "code", "mins": 60, "video": "https://www.youtube.com/watch?v=jUxhUgkKAjE", "objectives": ["GridSearch với CV", "Plot learning curves"], "has_quiz": False},
                ],
            },
            {
                "title": "Module 4: Data Storytelling và Reporting",
                "description": "Trình bày phân tích dữ liệu chuyên nghiệp với Plotly, Seaborn và Jupyter Notebook",
                "difficulty": "Intermediate",
                "learning_outcomes": [
                    make_module_outcome("Tạo interactive charts với Plotly Express", "plotly-charts", True),
                    make_module_outcome("Viết Jupyter Notebook báo cáo chuyên nghiệp", "jupyter-reporting", True),
                    make_module_outcome("Dashboard đơn giản với Streamlit", "streamlit-basics", False),
                    make_module_outcome("Xuất báo cáo PDF và HTML", "report-export", False),
                ],
                "lessons": [
                    {"title": "Advanced Seaborn Visualization", "desc": "FacetGrid, PairGrid, violin plot, stripplot, swarmplot, custom themes", "type": "mixed", "mins": 55, "video": "https://www.youtube.com/watch?v=6GUZXDef2U0", "objectives": ["Multi-plot với FacetGrid", "Custom Seaborn themes"], "has_quiz": False},
                    {"title": "Interactive với Plotly", "desc": "plotly.express, go.Figure, subplots, animations, Dash basics", "type": "code", "mins": 60, "video": "https://www.youtube.com/watch?v=GGL6U0k8WYA", "objectives": ["Interactive scatter và line plots", "Hover tooltips"], "has_quiz": True},
                    {"title": "Jupyter Notebook Best Practices", "desc": "Markdown, LaTeX equations, nbconvert, widgets, Voilà", "type": "mixed", "mins": 45, "video": "https://www.youtube.com/watch?v=HW29067qVWk", "objectives": ["Viết notebook dễ đọc", "Export sang HTML"], "has_quiz": False},
                    {"title": "Streamlit Dashboard", "desc": "st.write, charts, widgets, sidebar, caching, deploy trên Streamlit Cloud", "type": "code", "mins": 65, "video": "https://www.youtube.com/watch?v=VtrFjkSGgKM", "objectives": ["Tạo dashboard 1 trang", "Deploy lên Streamlit Cloud"], "has_quiz": False},
                ],
            },
        ],
    },
    {
        "title": "Machine Learning và AI cơ bản",
        "description": "Nền tảng vững chắc về Machine Learning: supervised/unsupervised learning, neural networks cơ bản, NLP và Computer Vision với thực hành trên projects thực tế.",
        "category": "Data Science",
        "level": "Advanced",
        "thumbnail_url": "https://images.unsplash.com/photo-1677442135703-1787eea5ce01?w=800&h=450",
        "preview_video_url": "https://www.youtube.com/watch?v=GwIo3gDZCVQ",
        "avg_rating": 4.9,
        "learning_outcomes": [
            make_course_outcome("Hiểu và implement các ML algorithms: SVM, Ensemble, Gradient Boosting", "ml-algorithms"),
            make_course_outcome("Xây dựng Neural Network với TensorFlow/Keras", "deep-learning-basics"),
            make_course_outcome("Áp dụng NLP: text preprocessing, sentiment analysis", "nlp-basics"),
            make_course_outcome("Làm việc với hình ảnh: CNN và transfer learning", "computer-vision-basics"),
        ],
        "prerequisites": ["Python thành thạo", "Pandas và scikit-learn cơ bản", "Đại số tuyến tính cơ bản"],
        "instr_idx": 2,
        "modules": [
            {
                "title": "Module 1: Advanced ML Algorithms",
                "description": "Ensemble methods, Gradient Boosting, SVM, Clustering — lý thuyết và thực hành",
                "difficulty": "Advanced",
                "learning_outcomes": [
                    make_module_outcome("Hiểu và dùng XGBoost, LightGBM cho classification", "gradient-boosting", True),
                    make_module_outcome("Implement SVM với kernel trick", "svm", True),
                    make_module_outcome("K-Means và DBSCAN clustering", "clustering", False),
                    make_module_outcome("Interpret model với SHAP values", "model-interpretability", False),
                ],
                "lessons": [
                    {"title": "Ensemble Methods: Bagging và Boosting", "desc": "Random Forest, Extra Trees, AdaBoost, Gradient Boosting — compare và tune", "type": "code", "mins": 75, "video": "https://www.youtube.com/watch?v=J4Wdy0Wc_xQ", "objectives": ["Train Random Forest và GBM", "Tune n_estimators và depth"], "has_quiz": True},
                    {"title": "XGBoost và LightGBM", "desc": "XGBoost theory, DMatrix, early stopping, monotone constraints, LightGBM", "type": "code", "mins": 80, "video": "https://www.youtube.com/watch?v=OtD8wVaFm6E", "objectives": ["XGBoost pipeline", "Feature importance plots"], "has_quiz": True},
                    {"title": "Support Vector Machines", "desc": "Linear SVM, kernel trick (RBF, polynomial), C parameter, SVR, multiclass", "type": "mixed", "mins": 65, "video": "https://www.youtube.com/watch?v=efR1C6CvhmE", "objectives": ["SVM cho classification", "Tune C và gamma"], "has_quiz": True},
                    {"title": "Unsupervised Learning và Clustering", "desc": "K-Means, Elbow method, DBSCAN, PCA dimensionality reduction, t-SNE", "type": "code", "mins": 70, "video": "https://www.youtube.com/watch?v=5w7cv89hsl0", "objectives": ["K-Means với optimal K", "Visualize với t-SNE"], "has_quiz": False},
                ],
            },
            {
                "title": "Module 2: Deep Learning với TensorFlow/Keras",
                "description": "Neural networks, backpropagation, CNN cơ bản với Keras Sequential API",
                "difficulty": "Advanced",
                "learning_outcomes": [
                    make_module_outcome("Xây dựng MLP với Keras Sequential API", "keras-mlp", True),
                    make_module_outcome("Regularization: Dropout, Batch Normalization, L2", "regularization", True),
                    make_module_outcome("Build CNN cho image classification", "cnn-basics", True),
                    make_module_outcome("Transfer learning với VGG16/ResNet50", "transfer-learning", False),
                ],
                "lessons": [
                    {"title": "Neural Networks và Backpropagation", "desc": "Perceptron, activation functions, forward/backward pass, gradient descent", "type": "mixed", "mins": 80, "video": "https://www.youtube.com/watch?v=aircAruvnKk", "objectives": ["Hiểu forward và backprop", "Implement MLP từ scratch cơ bản"], "has_quiz": True},
                    {"title": "Keras Sequential API", "desc": "Dense layers, activations, optimizer, loss, callbacks, model.fit, TensorBoard", "type": "code", "mins": 85, "video": "https://www.youtube.com/watch?v=wQ8BIBpya2k", "objectives": ["Train MLP với Keras", "Visualize training với TensorBoard"], "has_quiz": True},
                    {"title": "Convolutional Neural Network", "desc": "Conv2D, MaxPooling, Flatten, BatchNorm, Dropout — MNIST và CIFAR-10", "type": "code", "mins": 90, "video": "https://www.youtube.com/watch?v=QzY57FaENXg", "objectives": ["Build CNN cho image classification", "Improve với BatchNorm"], "has_quiz": True},
                    {"title": "Transfer Learning", "desc": "Pretrained models: VGG16, ResNet50, MobileNet — fine-tuning và feature extraction", "type": "code", "mins": 85, "video": "https://www.youtube.com/watch?v=hnGHiAPh0AT", "objectives": ["Feature extraction với VGG16", "Fine-tune cho custom dataset"], "has_quiz": False},
                ],
            },
            {
                "title": "Module 3: Natural Language Processing",
                "description": "Text preprocessing, word embeddings, sentiment analysis và named entity recognition",
                "difficulty": "Advanced",
                "learning_outcomes": [
                    make_module_outcome("Tiền xử lý text: tokenization, stopwords, stemming, lemmatization", "nlp-preprocessing", True),
                    make_module_outcome("Word2Vec và GloVe word embeddings", "word-embeddings", True),
                    make_module_outcome("Sentiment analysis với LSTM và BERT fine-tuning", "sentiment-analysis", True),
                    make_module_outcome("Named entity recognition với spaCy", "ner", False),
                ],
                "lessons": [
                    {"title": "NLP Preprocessing và Feature Extraction", "desc": "NLTK, spaCy, tokenization, TF-IDF, Bag of Words", "type": "code", "mins": 70, "video": "https://www.youtube.com/watch?v=05ONoGfmKvA", "objectives": ["Preprocess raw text", "TF-IDF vectorization"], "has_quiz": True},
                    {"title": "Word Embeddings", "desc": "Word2Vec (CBOW, Skip-gram), GloVe, fastText, gensim", "type": "mixed", "mins": 75, "video": "https://www.youtube.com/watch?v=viZrOnJclY0", "objectives": ["Train Word2Vec trên corpus", "Visualize word vectors"], "has_quiz": True},
                    {"title": "Sentiment Analysis", "desc": "LSTM với Keras, BERT fine-tuning với HuggingFace Transformers", "type": "code", "mins": 85, "video": "https://www.youtube.com/watch?v=8HL-Ap5_Axo", "objectives": ["Fine-tune BERT cho sentiment", "Evaluate với F1-score"], "has_quiz": True},
                    {"title": "NER và Text Classification", "desc": "spaCy NER, custom entities, text classification với zero-shot (OpenAI)", "type": "code", "mins": 75, "video": "https://www.youtube.com/watch?v=05ONoGfmKvA&t=1000", "objectives": ["Extract entities với spaCy"], "has_quiz": False},
                ],
            },
            {
                "title": "Module 4: ML Projects và Deployment",
                "description": "End-to-end ML project: từ problem definition đến deployment với FastAPI và Docker",
                "difficulty": "Advanced",
                "learning_outcomes": [
                    make_module_outcome("Define ML problem và collect/label data correctly", "ml-problem-definition", True),
                    make_module_outcome("Build end-to-end ML pipeline với MLflow tracking", "mlflow", True),
                    make_module_outcome("Serve ML model qua REST API với FastAPI", "ml-serving", True),
                    make_module_outcome("Monitor model drift và retrain strategy", "model-monitoring", False),
                ],
                "lessons": [
                    {"title": "End-to-End ML Project", "desc": "CRISP-DM methodology, problem framing, data collection, baseline model", "type": "mixed", "mins": 80, "video": "https://www.youtube.com/watch?v=pqNCD_5r0IU", "objectives": ["Định nghĩa ML problem rõ ràng", "Build và evaluate baseline"], "has_quiz": False},
                    {"title": "MLflow Experiment Tracking", "desc": "mlflow.log_param, log_metric, log_model, Model Registry, UI", "type": "code", "mins": 70, "video": "https://www.youtube.com/watch?v=859OxXrt_TI", "objectives": ["Track experiments với MLflow", "Compare model runs"], "has_quiz": True},
                    {"title": "Serve Model với FastAPI", "desc": "Load model, prediction endpoint, input validation, batch prediction, caching", "type": "code", "mins": 75, "video": "https://www.youtube.com/watch?v=1zMQBe0l1bM", "objectives": ["Wrap model trong FastAPI", "Handle prediction requests"], "has_quiz": True},
                    {"title": "Docker và Cloud Deployment", "desc": "Dockerfile cho ML app, docker-compose, push to ECR/GCR, deploy on AWS/GCP", "type": "code", "mins": 80, "video": "https://www.youtube.com/watch?v=0H2miBK_gAk", "objectives": ["Containerize ML app", "Deploy trên cloud"], "has_quiz": False},
                ],
            },
        ],
    },
    {
        "title": "Tiếng Anh Giao tiếp B1-B2",
        "description": "Nâng cao kỹ năng tiếng Anh giao tiếp từ B1 lên B2. Luyện speaking, listening, vocabulary và pronunciation để tự tin giao tiếp trong môi trường quốc tế.",
        "category": "Languages",
        "level": "Intermediate",
        "thumbnail_url": "https://images.unsplash.com/photo-1546410531-bb4caa6b424d?w=800&h=450",
        "preview_video_url": "https://www.youtube.com/watch?v=UF8uR6Z6KLc",
        "avg_rating": 4.5,
        "learning_outcomes": [
            make_course_outcome("Giao tiếp tự tin trong các tình huống hàng ngày và công việc", "english-speaking"),
            make_course_outcome("Hiểu native speakers ở tốc độ bình thường (podcasts, meetings)", "english-listening"),
            make_course_outcome("Sử dụng 2000+ từ vựng học thuật và chuyên ngành", "english-vocabulary"),
            make_course_outcome("Viết email và báo cáo chuyên nghiệp bằng tiếng Anh", "english-writing"),
        ],
        "prerequisites": ["Tiếng Anh A2-B1", "Biết ngữ pháp cơ bản"],
        "instr_idx": 3,
        "modules": [
            {
                "title": "Module 1: Speaking và Pronunciation",
                "description": "Nâng cao phát âm, intonation và fluency để giao tiếp tự tin hơn",
                "difficulty": "Basic",
                "learning_outcomes": [
                    make_module_outcome("Phát âm đúng 44 phonemes tiếng Anh", "pronunciation-phonemes", True),
                    make_module_outcome("Dùng intonation để express emotion và meaning", "intonation", True),
                    make_module_outcome("Nói fluently với 120+ words per minute", "speaking-fluency", False),
                    make_module_outcome("Strategies khi không hiểu hoặc quên từ", "communication-strategies", False),
                ],
                "lessons": [
                    {"title": "Pronunciation: Vowels và Consonants", "desc": "IPA chart, khó phát âm nhất, tongue twisters, minimal pairs", "type": "mixed", "mins": 55, "video": "https://www.youtube.com/watch?v=dAfhMtRHLAg", "objectives": ["Nhận biết IPA symbols", "Luyện 10 âm khó nhất"], "has_quiz": True},
                    {"title": "Stress và Intonation", "desc": "Word stress, sentence stress, rising/falling intonation, connected speech", "type": "mixed", "mins": 50, "video": "https://www.youtube.com/watch?v=UF8uR6Z6KLc", "objectives": ["Stress đúng word và sentence", "Rising/falling intonation"], "has_quiz": False},
                    {"title": "Fluency Techniques", "desc": "Filler words, pausing strategies, topic expansion, avoiding silence", "type": "mixed", "mins": 45, "video": "https://www.youtube.com/watch?v=IFNhvHBFMhQ", "objectives": ["Dùng fillers đúng cách", "Expand topic fluently"], "has_quiz": True},
                    {"title": "Conversation Practice: Daily Life", "desc": "Small talk, giving opinions, agreeing/disagreeing, telling stories", "type": "mixed", "mins": 60, "video": "https://www.youtube.com/watch?v=U8gT3n1S9MA", "objectives": ["Small talk 5 phút", "Express opinions với hedging"], "has_quiz": False},
                ],
            },
            {
                "title": "Module 2: Listening và Comprehension",
                "description": "Strategies để hiểu native speakers, podcasts và academic lectures",
                "difficulty": "Intermediate",
                "learning_outcomes": [
                    make_module_outcome("Note-taking khi nghe lecture hoặc meeting", "listening-note-taking", True),
                    make_module_outcome("Hiểu accent khác nhau (British, American, Australian)", "accents", True),
                    make_module_outcome("Inference meaning từ context khi không hiểu từ", "listening-inference", False),
                    make_module_outcome("Nghe và summarize podcast 5-10 phút", "podcast-listening", False),
                ],
                "lessons": [
                    {"title": "Listening Strategies", "desc": "Top-down vs bottom-up, predicting, note-taking symbols, IELTS listening tips", "type": "mixed", "mins": 50, "video": "https://www.youtube.com/watch?v=6K5vkJuP2iE", "objectives": ["Top-down listening approach", "Create note-taking system"], "has_quiz": True},
                    {"title": "British và American English", "desc": "Pronunciation differences, vocab differences, rhotic vs non-rhotic, reductions", "type": "mixed", "mins": 45, "video": "https://www.youtube.com/watch?v=owvp4G1dzXU", "objectives": ["Nhận biết British vs American", "Catch reductions và linking"], "has_quiz": True},
                    {"title": "Podcast Listening Practice", "desc": "BBC Learning English, TED Talks, shadowing technique, transcript practice", "type": "mixed", "mins": 55, "video": "https://www.youtube.com/watch?v=HuFYqnbVbzY", "objectives": ["Shadow TED talk 5 phút", "Summarize main points"], "has_quiz": False},
                    {"title": "Academic and Business Listening", "desc": "Meeting jargon, academic lectures, webinars, Q&A sessions", "type": "mixed", "mins": 60, "video": "https://www.youtube.com/watch?v=bpHf1XcoiFs", "objectives": ["Note-taking trong meeting", "Identify action items"], "has_quiz": False},
                ],
            },
            {
                "title": "Module 3: Vocabulary và Grammar in Context",
                "description": "Academic Word List, collocations, phrasal verbs và grammar cho communication",
                "difficulty": "Intermediate",
                "learning_outcomes": [
                    make_module_outcome("Sử dụng 500 từ trong Academic Word List", "academic-vocabulary", True),
                    make_module_outcome("Collocations và phrasal verbs phổ biến nhất", "collocations", True),
                    make_module_outcome("Perfect tenses và conditionals trong giao tiếp", "grammar-communication", True),
                    make_module_outcome("Idioms và expressions cho native-like speech", "idioms", False),
                ],
                "lessons": [
                    {"title": "Academic Word List (AWL)", "desc": "Top 200 AWL words, word families, collocations, Quizlet sets", "type": "text", "mins": 55, "video": "https://www.youtube.com/watch?v=g_YsboLxKRg", "objectives": ["Learn 50 AWL words/module", "Use in context"], "has_quiz": True},
                    {"title": "Phrasal Verbs và Collocations", "desc": "Business phrasal verbs, common collocations, word partnerships", "type": "mixed", "mins": 50, "video": "https://www.youtube.com/watch?v=fEjyRRpn3og", "objectives": ["20 business phrasal verbs", "Collocations với make/do/have"], "has_quiz": True},
                    {"title": "Perfect Tenses trong Context", "desc": "Present Perfect, Past Perfect, Future Perfect — khi nào dùng trong giao tiếp thực tế", "type": "mixed", "mins": 55, "video": "https://www.youtube.com/watch?v=Zek1tJ_aDr8", "objectives": ["Perfect tenses đúng context", "Common mistakes correction"], "has_quiz": True},
                    {"title": "Idioms và Expressions", "desc": "Body idioms, weather idioms, business sayings, informal vs formal register", "type": "mixed", "mins": 45, "video": "https://www.youtube.com/watch?v=1X0YoMXtDdA", "objectives": ["20 common idioms", "Formal vs informal register"], "has_quiz": False},
                ],
            },
            {
                "title": "Module 4: Professional Communication",
                "description": "Email writing, presentations, meetings và negotiation trong môi trường quốc tế",
                "difficulty": "Advanced",
                "learning_outcomes": [
                    make_module_outcome("Viết professional email với tone và format đúng", "email-writing", True),
                    make_module_outcome("Trình bày presentation tự tin với structure rõ ràng", "presentation-skills", True),
                    make_module_outcome("Participate hiệu quả trong business meetings", "meeting-english", True),
                    make_module_outcome("Negotiate và handle conflict professionally", "negotiation-english", False),
                ],
                "lessons": [
                    {"title": "Professional Email Writing", "desc": "Subject, salutation, body structure, tone, CC/BCC etiquette, formal phrases", "type": "text", "mins": 55, "video": "https://www.youtube.com/watch?v=o96Kbv61fKs", "objectives": ["Viết request và complaint email", "Subject line best practices"], "has_quiz": True},
                    {"title": "Presentations in English", "desc": "Opening hook, structure (PREP), signposting phrases, handling Q&A", "type": "mixed", "mins": 65, "video": "https://www.youtube.com/watch?v=gcLP8LoFBG4", "objectives": ["3-minute presentation với structure", "Signposting language"], "has_quiz": True},
                    {"title": "Business Meetings", "desc": "Chairing, agenda, turn-taking, interrupting politely, action items, follow-up", "type": "mixed", "mins": 60, "video": "https://www.youtube.com/watch?v=7DONLnYlLSo", "objectives": ["Chair a meeting in English", "Polite interruption phrases"], "has_quiz": False},
                    {"title": "Negotiation và Problem-solving", "desc": "Bargaining phrases, compromising, express disagreement diplomatically", "type": "mixed", "mins": 70, "video": "https://www.youtube.com/watch?v=QhhfErjBRZw", "objectives": ["Win-win negotiation phrases", "Handle objections diplomatically"], "has_quiz": False},
                ],
            },
        ],
    },
    {
        "title": "Marketing Digital và Growth Hacking",
        "description": "Từ SEO và Content Marketing đến Paid Ads, Email Marketing và Analytics. Học cách xây dựng và execute chiến lược digital marketing hiệu quả cho doanh nghiệp.",
        "category": "Business",
        "level": "Beginner",
        "thumbnail_url": "https://images.unsplash.com/photo-1432888622747-4eb9a8efeb07?w=800&h=450",
        "preview_video_url": "https://www.youtube.com/watch?v=bixR-KIJKYM",
        "avg_rating": 4.6,
        "learning_outcomes": [
            make_course_outcome("Xây dựng SEO strategy toàn diện: on-page, off-page, technical", "seo-strategy"),
            make_course_outcome("Chạy Google Ads và Meta Ads hiệu quả với ROAS dương", "paid-advertising"),
            make_course_outcome("Content marketing: editorial calendar, copywriting, distribution", "content-marketing"),
            make_course_outcome("Phân tích data với Google Analytics 4 và make decisions", "marketing-analytics"),
        ],
        "prerequisites": ["Kiến thức cơ bản về internet", "Có tài khoản Google và Facebook"],
        "instr_idx": 4,
        "modules": [
            {
                "title": "Module 1: SEO và Content Marketing",
                "description": "Keyword research, on-page SEO, content strategy và link building",
                "difficulty": "Basic",
                "learning_outcomes": [
                    make_module_outcome("Keyword research với Ahrefs, SEMrush, Google Keyword Planner", "keyword-research", True),
                    make_module_outcome("On-page SEO: title, meta, H-tags, internal linking", "on-page-seo", True),
                    make_module_outcome("Viết content chuẩn SEO và readable", "seo-content-writing", True),
                    make_module_outcome("Link building strategies: guest post, HARO, resource pages", "link-building", False),
                ],
                "lessons": [
                    {"title": "SEO Fundamentals", "desc": "How search engines work, ranking factors, crawling vs indexing, Google Search Console", "type": "mixed", "mins": 50, "video": "https://www.youtube.com/watch?v=DvwS7cV9GmQ", "objectives": ["Hiểu ranking factors", "Setup Google Search Console"], "has_quiz": True},
                    {"title": "Keyword Research", "desc": "Seed keywords, long-tail, search intent (informational/commercial), competitor gaps", "type": "mixed", "mins": 60, "video": "https://www.youtube.com/watch?v=eMpblyM-BKY", "objectives": ["Research 50 target keywords", "Prioritize bằng volume vs difficulty"], "has_quiz": True},
                    {"title": "On-Page SEO Optimization", "desc": "Title tags, meta descriptions, header structure, image alt, URL, internal links, page speed", "type": "mixed", "mins": 55, "video": "https://www.youtube.com/watch?v=Yqbn2M9ngRE", "objectives": ["Audit một trang web cơ bản", "Fix common on-page issues"], "has_quiz": True},
                    {"title": "Content Strategy và Copywriting", "desc": "Editorial calendar, content pillars, AIDA/PAS frameworks, headline formulas", "type": "text", "mins": 65, "video": "https://www.youtube.com/watch?v=MJ2cBbBCeQk", "objectives": ["Tạo editorial calendar 3 tháng", "Viết headline với hooks"], "has_quiz": False},
                ],
            },
            {
                "title": "Module 2: Paid Advertising",
                "description": "Google Ads Search và Meta Ads — setup, targeting, optimization và reporting",
                "difficulty": "Intermediate",
                "learning_outcomes": [
                    make_module_outcome("Setup Google Ads Search campaign từ đầu", "google-ads", True),
                    make_module_outcome("Meta Ads: audience targeting, creative testing, lookalike", "meta-ads", True),
                    make_module_outcome("Optimize campaign: CTR, CPC, ROAS, Quality Score", "campaign-optimization", True),
                    make_module_outcome("Attribution và multi-touch tracking", "attribution", False),
                ],
                "lessons": [
                    {"title": "Google Ads Search Campaign", "desc": "Campaign structure, match types, Quality Score, bidding strategies, ad extensions", "type": "mixed", "mins": 70, "video": "https://www.youtube.com/watch?v=kHctM7-DVcc", "objectives": ["Tạo search campaign", "Write effective ad copy"], "has_quiz": True},
                    {"title": "Meta Ads (Facebook/Instagram)", "desc": "Campaign objective, audience targeting, creative formats, A/B testing, pixel setup", "type": "mixed", "mins": 75, "video": "https://www.youtube.com/watch?v=f_fNLwdZbXw", "objectives": ["Setup Meta Pixel", "Tạo first ad campaign"], "has_quiz": True},
                    {"title": "Campaign Optimization", "desc": "CTR, CPC, CVR, ROAS, budget allocation, frequency capping, negative keywords", "type": "mixed", "mins": 65, "video": "https://www.youtube.com/watch?v=XBDaHMQsMvM", "objectives": ["Identify và fix low-performing ads", "Optimize bidding strategy"], "has_quiz": True},
                    {"title": "Retargeting và Lookalike Audiences", "desc": "Custom audiences, retargeting sequence, lookalike audiences, CRM integration", "type": "mixed", "mins": 60, "video": "https://www.youtube.com/watch?v=Gv5QdYy_mR8", "objectives": ["Setup retargeting campaign", "Tạo lookalike audience"], "has_quiz": False},
                ],
            },
            {
                "title": "Module 3: Email Marketing và Automation",
                "description": "Xây dựng email list, viết campaigns, automation flows và deliverability",
                "difficulty": "Intermediate",
                "learning_outcomes": [
                    make_module_outcome("Xây dựng email list với lead magnets", "list-building", True),
                    make_module_outcome("Viết email subject lines có open rate cao", "email-copywriting", True),
                    make_module_outcome("Setup automation flows: welcome, nurture, cart abandon", "email-automation", True),
                    make_module_outcome("Optimize deliverability và avoid spam filters", "email-deliverability", False),
                ],
                "lessons": [
                    {"title": "Email Marketing Strategy", "desc": "Platform comparison (Mailchimp, Klaviyo, ActiveCampaign), list hygiene, segmentation", "type": "text", "mins": 50, "video": "https://www.youtube.com/watch?v=nE2IaDiEPso", "objectives": ["Chọn email platform phù hợp", "Segmentation strategy"], "has_quiz": True},
                    {"title": "Email Copywriting và Design", "desc": "Subject lines, preheader, body structure, CTA, mobile-responsive design, personalization", "type": "mixed", "mins": 60, "video": "https://www.youtube.com/watch?v=QhhfEi5d9SY", "objectives": ["Viết 5 subject line variations", "A/B test subject lines"], "has_quiz": True},
                    {"title": "Automation Flows", "desc": "Welcome series, lead nurture, cart abandon, win-back, post-purchase sequences", "type": "mixed", "mins": 65, "video": "https://www.youtube.com/watch?v=4WkVbN5bhN4", "objectives": ["Map out welcome flow", "Setup trigger-based emails"], "has_quiz": False},
                    {"title": "Analytics và Reporting", "desc": "Open rate, CTR, unsubscribe, revenue per email, list growth rate dashboards", "type": "mixed", "mins": 50, "video": "https://www.youtube.com/watch?v=yNSmVElFpME", "objectives": ["Build email dashboard", "Interpret key metrics"], "has_quiz": False},
                ],
            },
            {
                "title": "Module 4: Analytics và Growth Strategy",
                "description": "Google Analytics 4, data-driven decisions, A/B testing và growth framework",
                "difficulty": "Advanced",
                "learning_outcomes": [
                    make_module_outcome("Setup và phân tích GA4 events, funnels, reports", "google-analytics-4", True),
                    make_module_outcome("Design và analyze A/B tests đúng statistical significance", "ab-testing", True),
                    make_module_outcome("AARRR Growth framework: Acquisition, Activation, Retention", "growth-framework", True),
                    make_module_outcome("Xây dựng marketing dashboard với Looker Studio", "looker-studio", False),
                ],
                "lessons": [
                    {"title": "Google Analytics 4 Fundamentals", "desc": "Events model, custom events, conversions, audiences, exploration reports, API", "type": "mixed", "mins": 70, "video": "https://www.youtube.com/watch?v=XSSEjEFvh6M", "objectives": ["Setup GA4 với custom events", "Build funnel exploration"], "has_quiz": True},
                    {"title": "A/B Testing Framework", "desc": "Hypothesis, sample size, statistical significance, p-value, Google Optimize", "type": "mixed", "mins": 65, "video": "https://www.youtube.com/watch?v=VYpCYkTBZQ4", "objectives": ["Design valid A/B test", "Calculate sample size"], "has_quiz": True},
                    {"title": "Growth Hacking Techniques", "desc": "AARRR metrics, viral loops, referral programs, product-led growth, North Star metric", "type": "mixed", "mins": 70, "video": "https://www.youtube.com/watch?v=bixR-KIJKYM", "objectives": ["Define North Star metric", "Design referral program"], "has_quiz": True},
                    {"title": "Marketing Dashboard với Looker Studio", "desc": "Connect GA4, Ads, Search Console — build CMO-level dashboard", "type": "mixed", "mins": 60, "video": "https://www.youtube.com/watch?v=6FTUpceqWnc", "objectives": ["Build 1-page dashboard", "Visualize key KPIs"], "has_quiz": False},
                ],
            },
        ],
    },
    {
        "title": "Quản lý Dự án với Excel và Jira",
        "description": "Kỹ năng quản lý dự án thực chiến: lập kế hoạch với Excel/Google Sheets, theo dõi với Jira và Confluence, Agile/Scrum methodology và risk management.",
        "category": "Business",
        "level": "Beginner",
        "thumbnail_url": "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=800&h=450",
        "preview_video_url": "https://www.youtube.com/watch?v=6y4GCJ3mL4U",
        "avg_rating": 4.4,
        "learning_outcomes": [
            make_course_outcome("Lập kế hoạch dự án với WBS, Gantt chart và resource planning", "project-planning"),
            make_course_outcome("Quản lý backlog, sprint và team với Jira Scrum board", "jira-scrum"),
            make_course_outcome("Risk management: identify, assess và mitigate risks", "risk-management"),
            make_course_outcome("Báo cáo tiến độ và communicate với stakeholders hiệu quả", "stakeholder-communication"),
        ],
        "prerequisites": ["Biết Excel cơ bản", "Không cần kinh nghiệm PM"],
        "instr_idx": 4,
        "modules": [
            {
                "title": "Module 1: Project Planning với Excel",
                "description": "WBS, Gantt chart, resource plan và budget tracking trong Excel/Google Sheets",
                "difficulty": "Basic",
                "learning_outcomes": [
                    make_module_outcome("Tạo WBS (Work Breakdown Structure) cho dự án", "wbs", True),
                    make_module_outcome("Build Gantt chart trong Excel với conditional formatting", "gantt-chart", True),
                    make_module_outcome("Resource planning và budget tracking spreadsheet", "resource-planning", True),
                    make_module_outcome("Critical Path Method cơ bản", "critical-path", False),
                ],
                "lessons": [
                    {"title": "Project Initiation và WBS", "desc": "Project charter, stakeholder analysis, scope statement, WBS decomposition", "type": "text", "mins": 55, "video": "https://www.youtube.com/watch?v=X5haGwNvCfc", "objectives": ["Write project charter", "Create 2-level WBS"], "has_quiz": True},
                    {"title": "Gantt Chart trong Excel", "desc": "Excel Gantt với conditional formatting, dependencies, milestone markers, progress tracking", "type": "mixed", "mins": 65, "video": "https://www.youtube.com/watch?v=jfVFnKR8bFQ", "objectives": ["Build 20-task Gantt chart", "Link task dependencies"], "has_quiz": True},
                    {"title": "Resource Planning và Budget", "desc": "Resource matrix, capacity planning, RACI chart, budget baseline, earned value basics", "type": "mixed", "mins": 60, "video": "https://www.youtube.com/watch?v=1T4y-UxA4Ko", "objectives": ["Create RACI chart", "Build budget tracker"], "has_quiz": True},
                    {"title": "Risk Management", "desc": "Risk register, probability-impact matrix, risk response strategies, contingency", "type": "text", "mins": 55, "video": "https://www.youtube.com/watch?v=FPDjjkVQfbo", "objectives": ["Identify 10 project risks", "Fill risk register"], "has_quiz": False},
                ],
            },
            {
                "title": "Module 2: Agile và Scrum",
                "description": "Agile manifesto, Scrum framework, sprints, ceremonies và team collaboration",
                "difficulty": "Basic",
                "learning_outcomes": [
                    make_module_outcome("Hiểu Agile values và 12 principles", "agile-principles", True),
                    make_module_outcome("Run Scrum ceremonies: planning, daily standup, review, retro", "scrum-ceremonies", True),
                    make_module_outcome("Viết user stories và acceptance criteria đúng chuẩn", "user-stories", True),
                    make_module_outcome("Velocity tracking và sprint forecasting", "velocity", False),
                ],
                "lessons": [
                    {"title": "Agile Mindset và Values", "desc": "Agile manifesto, Waterfall vs Agile, Scrum vs Kanban vs SAFe, roles", "type": "text", "mins": 50, "video": "https://www.youtube.com/watch?v=GE6lbPLEAzc", "objectives": ["Explain Agile values", "Compare Scrum và Kanban"], "has_quiz": True},
                    {"title": "Scrum Roles và Ceremonies", "desc": "PO, SM, Dev Team, Sprint Planning, Daily Scrum, Review, Retrospective — cheat sheets", "type": "mixed", "mins": 60, "video": "https://www.youtube.com/watch?v=9TycLR0TqFA", "objectives": ["Run mock sprint planning", "Facilitate retrospective"], "has_quiz": True},
                    {"title": "User Stories và Backlog Refinement", "desc": "As a... I want... So that..., acceptance criteria, story points, INVEST criteria", "type": "text", "mins": 55, "video": "https://www.youtube.com/watch?v=apOvF9NVguA", "objectives": ["Write 10 user stories", "Estimate với planning poker"], "has_quiz": True},
                    {"title": "Velocity và Sprint Metrics", "desc": "Velocity chart, burndown chart, WIP limits, cycle time, lead time", "type": "mixed", "mins": 50, "video": "https://www.youtube.com/watch?v=1T4y-UxA4Ko&t=500", "objectives": ["Create burndown chart", "Calculate team velocity"], "has_quiz": False},
                ],
            },
            {
                "title": "Module 3: Jira và Confluence",
                "description": "Setup Jira project, manage Scrum board, create Confluence documentation",
                "difficulty": "Intermediate",
                "learning_outcomes": [
                    make_module_outcome("Setup Jira Scrum project với custom workflows", "jira-setup", True),
                    make_module_outcome("Manage backlog, sprints và board trong Jira", "jira-scrum-board", True),
                    make_module_outcome("Create và organize Confluence documentation", "confluence", False),
                    make_module_outcome("Jira Automation và JQL queries", "jira-automation", False),
                ],
                "lessons": [
                    {"title": "Jira Project Setup", "desc": "Project types, issue types, workflow, permissions, components, versions", "type": "mixed", "mins": 60, "video": "https://www.youtube.com/watch?v=GWxMTvRGIpc", "objectives": ["Create Jira Scrum project", "Customize workflow"], "has_quiz": True},
                    {"title": "Scrum Board và Backlog", "desc": "Backlog grooming, epic/story/task hierarchy, sprint planning in Jira, board customization", "type": "mixed", "mins": 65, "video": "https://www.youtube.com/watch?v=SqukW289yls", "objectives": ["Create và start sprint", "Manage board columns"], "has_quiz": True},
                    {"title": "Confluence Documentation", "desc": "Page hierarchy, templates, macros, version history, Jira integration", "type": "mixed", "mins": 55, "video": "https://www.youtube.com/watch?v=OlR7UZxWsoo", "objectives": ["Create team space", "Write sprint wiki page"], "has_quiz": False},
                    {"title": "Jira Automation và JQL", "desc": "Auto-assign, status transitions, JQL queries, dashboards, reports", "type": "mixed", "mins": 60, "video": "https://www.youtube.com/watch?v=t5YmdEYaU-8", "objectives": ["Write basic JQL", "Create automation rule"], "has_quiz": False},
                ],
            },
            {
                "title": "Module 4: Stakeholder Management và Reporting",
                "description": "Communication plan, status reports, presentations và difficult conversations",
                "difficulty": "Intermediate",
                "learning_outcomes": [
                    make_module_outcome("Tạo communication plan và RACI matrix", "communication-plan", True),
                    make_module_outcome("Viết weekly status report theo chuẩn PMO", "status-reporting", True),
                    make_module_outcome("Handle scope creep và change request đúng process", "change-management", True),
                    make_module_outcome("Difficult conversations: escalation và conflict resolution", "conflict-management", False),
                ],
                "lessons": [
                    {"title": "Stakeholder Analysis và Communication", "desc": "Stakeholder mapping, power/interest grid, communication plan, meeting cadences", "type": "text", "mins": 55, "video": "https://www.youtube.com/watch?v=3cGdaXjhIog", "objectives": ["Create stakeholder map", "Write communication plan"], "has_quiz": True},
                    {"title": "Status Reports và Dashboards", "desc": "Red/Amber/Green status, executive summary format, project dashboard in Excel", "type": "mixed", "mins": 60, "video": "https://www.youtube.com/watch?v=u21W_tfPVrY", "objectives": ["Write RAG status report", "Build project dashboard"], "has_quiz": True},
                    {"title": "Scope và Change Management", "desc": "Change request process, impact analysis, change log, scope creep prevention", "type": "text", "mins": 55, "video": "https://www.youtube.com/watch?v=r2JlJZG8dS4", "objectives": ["Write change request template", "Handle scope creep scenario"], "has_quiz": True},
                    {"title": "Project Closure và Lessons Learned", "desc": "Closure checklist, handover, lessons learned workshop, post-mortem", "type": "text", "mins": 50, "video": "https://www.youtube.com/watch?v=gVfKr69j1og", "objectives": ["Complete closure checklist"], "has_quiz": False},
                ],
            },
        ],
    },
]


# ─── SEED FUNCTIONS ─────────────────────────────────────────────────────────────

async def drop_all_collections():
    """Xóa toàn bộ data cũ trước khi seed"""
    collections = [
        User, Course, Module, Lesson, Enrollment, Progress,
        Quiz, QuizAttempt, AssessmentSession, Conversation, Class, Recommendation,
        RefreshToken,   # auth.py: cần clear refresh_tokens collection
    ]
    for col in collections:
        await col.find_all().delete()
    print("Cleared all collections.")


async def seed_users() -> Dict[str, List[str]]:
    """Tạo 28 users: 3 admin, 5 instructor, 20 student"""
    print("\n--- Seeding Users ---")
    user_ids: Dict[str, List[str]] = {"admin": [], "instructor": [], "student": []}
    users_to_insert: List[User] = []

    for i, tmpl in enumerate(ADMIN_USERS):
        uid = gid()
        users_to_insert.append(User(
            id=uid,
            full_name=tmpl["full_name"],
            email=tmpl["email"],
            hashed_password=hp("Admin@123456"),
            role="admin",
            status="active",
            avatar_url=tmpl["avatar_url"],
            bio=tmpl["bio"],
            contact_info=f"+84 90{i} 000 00{i+1}",   # Unique per admin
            learning_preferences=tmpl["learning_preferences"],
            last_login_at=past(days=random.randint(0, 2)),
            email_verified=True,
            phone_verified=True,
            created_at=past(days=365),
            updated_at=past(days=random.randint(0, 30)),
        ))
        user_ids["admin"].append(uid)

    admin_id = user_ids["admin"][0]  # Admin chính để dùng cho created_by

    for tmpl in INSTRUCTOR_USERS:
        uid = gid()
        users_to_insert.append(User(
            id=uid,
            full_name=tmpl["full_name"],
            email=tmpl["email"],
            hashed_password=hp("Instructor@123"),
            role="instructor",
            status="active",
            avatar_url=tmpl["avatar_url"],
            bio=tmpl["bio"],
            contact_info=f"+84 9{random.randint(10,99)} {random.randint(100,999)} {random.randint(100,999)}",
            learning_preferences=tmpl["learning_preferences"],
            last_login_at=past(days=random.randint(0, 3)),
            email_verified=True,
            phone_verified=True,
            # admin.py AdminCreateUserResponse: created_by = admin UUID
            created_by=admin_id,
            created_at=past(days=random.randint(300, 400)),
            updated_at=past(days=random.randint(0, 14)),
        ))
        user_ids["instructor"].append(uid)

    for tmpl in STUDENT_USERS:
        uid = gid()
        # admin.py AdminUserListItem: status = "active|inactive|banned"
        # Đảm bảo có đủ cả 3 status để test admin UI
        statuses = ["active"] * 15 + ["inactive"] * 3 + ["banned"] * 2
        users_to_insert.append(User(
            id=uid,
            full_name=tmpl["full_name"],
            email=tmpl["email"],
            hashed_password=hp("Student@123"),
            role="student",
            status=random.choice(statuses),
            avatar_url=tmpl["avatar_url"],
            bio=tmpl["bio"],
            contact_info=f"+84 9{random.randint(10,99)} {random.randint(100,999)} {random.randint(100,999)}",
            learning_preferences=tmpl["learning_preferences"],
            last_login_at=past(days=random.randint(0, 7), hours=random.randint(0, 23)),
            email_verified=random.choice([True, True, True, False]),
            phone_verified=False,
            # admin.py AdminCreateUserResponse: created_by = admin UUID
            created_by=admin_id,
            created_at=past(days=random.randint(30, 300)),
            updated_at=past(days=random.randint(0, 30)),
        ))
        user_ids["student"].append(uid)

    await User.insert_many(users_to_insert)
    print(f"  Created {len(users_to_insert)} users: {len(user_ids['admin'])} admin, {len(user_ids['instructor'])} instructor, {len(user_ids['student'])} student")
    return user_ids


async def seed_courses(user_ids: Dict[str, List[str]]) -> Dict[str, str]:
    """Tạo 7 public courses — return {title: course_id}"""
    print("\n--- Seeding Courses ---")
    admin_id = user_ids["admin"][0]
    instructor_ids = user_ids["instructor"]

    # Fetch instructor user objects to denormalize
    instr_users = []
    for iid in instructor_ids:
        u = await User.get(iid)
        if u:
            instr_users.append(u)

    course_ids_map: Dict[str, str] = {}

    for catalog in COURSE_CATALOG:
        cid = gid()
        instr_user = instr_users[catalog["instr_idx"] % len(instr_users)]
        course_created_at = past(days=random.randint(60, 200))

        # Compute derived course_type
        course_type = "public"  # admin-created courses are public

        c = Course(
            id=cid,
            title=catalog["title"],
            description=catalog["description"],
            category=catalog["category"],
            level=catalog["level"],
            thumbnail_url=catalog["thumbnail_url"],
            preview_video_url=catalog["preview_video_url"],
            language="vi",
            status="published",
            owner_id=admin_id,
            owner_type="admin",
            course_type=course_type,
            instructor_id=instr_user.id,
            instructor_name=instr_user.full_name,
            instructor_avatar=instr_user.avatar_url,
            instructor_bio=instr_user.bio or "Giảng viên chuyên nghiệp với nhiều năm kinh nghiệm.",
            learning_outcomes=catalog["learning_outcomes"],
            prerequisites=catalog["prerequisites"],
            modules=[],           # will be populated by seed_modules_and_lessons
            total_duration_minutes=0,
            total_modules=0,
            total_lessons=0,
            enrollment_count=0,
            avg_rating=catalog["avg_rating"],
            created_at=course_created_at,
            updated_at=past(days=random.randint(5, 30)),
        )
        await c.insert()
        course_ids_map[catalog["title"]] = cid
        print(f"  Course: {catalog['title']} [{catalog['level']}] → instructor: {instr_user.full_name}")

    return course_ids_map


async def seed_modules_and_lessons(course_ids: Dict[str, str]) -> Dict[str, List[str]]:
    """
    Hybrid architecture: mỗi course có EmbeddedModule trong Course.modules[]
    và separate Module/Lesson documents. Trả về {course_id: [lesson_ids]}
    """
    print("\n--- Seeding Modules & Lessons (Hybrid Architecture) ---")
    all_lesson_ids: Dict[str, List[str]] = {}

    for catalog in COURSE_CATALOG:
        course_id = course_ids[catalog["title"]]
        all_lesson_ids[course_id] = []

        embedded_modules: List[EmbeddedModule] = []
        separate_modules: List[Module] = []
        separate_lessons: List[Lesson] = []

        total_course_duration = 0
        total_course_lessons = 0

        for mod_order, mod_data in enumerate(catalog["modules"], start=1):
            module_id = gid()
            module_created_at = past(days=random.randint(30, 180))

            embedded_lessons: List[EmbeddedLesson] = []
            module_lesson_docs: List[Lesson] = []
            total_mod_duration = 0

            for les_order, les_data in enumerate(mod_data["lessons"], start=1):
                lesson_id = gid()
                lesson_created_at = past(days=random.randint(20, 150))

                # Content JSON cho lesson
                lesson_content = {
                    "video_url": les_data["video"],
                    "video_duration_seconds": les_data["mins"] * 60,
                    "text_content": f"<h2>{les_data['title']}</h2><p>{les_data['desc']}</p>",
                    "code_example": f"# Code example cho bài {les_data['title']}\nprint('Hello from {catalog['category']}!')" if les_data["type"] in ("code", "mixed") else None,
                }

                # Resources — theo learning.py ResourceItem schema: {id, title, type, url, size_mb, description}
                lesson_resources = [
                    make_resource("pdf", f"Slide - {les_data['title']}", f"https://docs.ailearning.vn/{catalog['category'].lower()}/module{mod_order}/lesson{les_order}.pdf", round(random.uniform(1.0, 6.0), 1), f"Slide bài giảng PDF cho {les_data['title']}"),
                    make_resource("code", f"Code examples - {les_data['title']}", f"https://github.com/ailearning/{catalog['category'].lower()}/blob/main/module{mod_order}/lesson{les_order}.py", round(random.uniform(0.01, 0.1), 3), "File code mẫu và exercises"),
                    make_resource("video", f"Video bài giảng - {les_data['title']}", les_data["video"], 0.0, f"Video bài giảng {les_data['mins']} phút"),
                    make_resource("link", "Official Documentation", f"https://docs.python.org/3/" if catalog["category"] == "Programming" else "https://pandas.pydata.org/docs/", 0.0, "Tài liệu chính thức"),
                ]

                quiz_id_for_lesson = gid() if les_data["has_quiz"] else None

                # 1. EmbeddedLesson
                emb_lesson = EmbeddedLesson(
                    id=lesson_id,
                    title=les_data["title"],
                    description=les_data["desc"],
                    order=les_order,
                    content=json.dumps(lesson_content),
                    content_type=les_data["type"],
                    duration_minutes=les_data["mins"],
                    video_url=les_data["video"],
                    audio_url=None,
                    resources=lesson_resources,
                    learning_objectives=les_data["objectives"],
                    quiz_id=quiz_id_for_lesson,
                    is_published=True,
                    created_at=lesson_created_at,
                    updated_at=past(days=random.randint(5, 20)),
                )
                embedded_lessons.append(emb_lesson)

                # 2. Separate Lesson document
                sep_lesson = Lesson(
                    id=lesson_id,
                    module_id=module_id,
                    course_id=course_id,
                    title=les_data["title"],
                    description=les_data["desc"],
                    order=les_order,
                    content=json.dumps(lesson_content),
                    content_type=les_data["type"],
                    duration_minutes=les_data["mins"],
                    video_url=les_data["video"],
                    audio_url=None,
                    learning_objectives=les_data["objectives"],
                    resources=lesson_resources,
                    quiz_id=quiz_id_for_lesson,
                    is_published=True,
                    created_at=lesson_created_at,
                    updated_at=past(days=random.randint(5, 20)),
                )
                module_lesson_docs.append(sep_lesson)
                all_lesson_ids[course_id].append(lesson_id)
                total_mod_duration += les_data["mins"]

            # Module-level resources
            mod_resources = [
                make_resource("pdf", f"Tài liệu tổng hợp - {mod_data['title']}", f"https://docs.ailearning.vn/{catalog['category'].lower()}/module{mod_order}/summary.pdf", round(random.uniform(2.0, 10.0), 1), "Tài liệu tổng hợp toàn bộ module"),
                make_resource("link", "Thư viện tham khảo", f"https://resources.ailearning.vn/module/{mod_order}", 0.0, "Link tài liệu tham khảo bổ sung"),
            ]

            # Module prerequisites (chỉ có từ module 2 trở đi)
            mod_prerequisites: List[str] = []
            if mod_order > 1 and embedded_modules:
                mod_prerequisites = [embedded_modules[mod_order - 2].id]

            # 3. EmbeddedModule
            emb_module = EmbeddedModule(
                id=module_id,
                title=mod_data["title"],
                description=mod_data["description"],
                order=mod_order,
                difficulty=mod_data["difficulty"],
                estimated_hours=round(total_mod_duration / 60, 1),
                learning_outcomes=mod_data["learning_outcomes"],
                prerequisites=mod_prerequisites,
                resources=mod_resources,
                lessons=embedded_lessons,
                total_lessons=len(embedded_lessons),
                total_duration_minutes=total_mod_duration,
                created_at=module_created_at,
                updated_at=past(days=random.randint(5, 25)),
            )
            embedded_modules.append(emb_module)

            # 4. Separate Module document
            sep_module = Module(
                id=module_id,
                course_id=course_id,
                title=mod_data["title"],
                description=mod_data["description"],
                order=mod_order,
                difficulty=mod_data["difficulty"],
                estimated_hours=round(total_mod_duration / 60, 1),
                learning_outcomes=mod_data["learning_outcomes"],
                resources=mod_resources,
                prerequisites=mod_prerequisites,
                total_lessons=len(embedded_lessons),
                total_duration_minutes=total_mod_duration,
                created_at=module_created_at,
                updated_at=past(days=random.randint(5, 25)),
            )
            separate_modules.append(sep_module)
            separate_lessons.extend(module_lesson_docs)

            total_course_duration += total_mod_duration
            total_course_lessons += len(embedded_lessons)

        # Update Course với embedded modules và stats
        await Course.find_one(Eq(Course.id, course_id)).update(Set({
            "modules": [m.model_dump() for m in embedded_modules],
            "total_modules": len(embedded_modules),
            "total_lessons": total_course_lessons,
            "total_duration_minutes": total_course_duration,
        }))

        if separate_modules:
            await Module.insert_many(separate_modules)
        if separate_lessons:
            await Lesson.insert_many(separate_lessons)

        print(f"  {catalog['title']}: {len(embedded_modules)} modules, {total_course_lessons} lessons, {total_course_duration} mins")

    return all_lesson_ids


async def seed_classes(user_ids: Dict[str, List[str]], course_ids: Dict[str, str]) -> List[str]:
    """Tạo 5 classes do instructor tạo"""
    print("\n--- Seeding Classes ---")
    instructor_ids = user_ids["instructor"]
    student_ids = user_ids["student"]
    all_course_ids = list(course_ids.values())
    class_ids = []

    class_templates = [
        {"name": "Python Bootcamp 2025 - Batch 1", "desc": "Lớp học Python cường độ cao, 3 tháng Master Python từ cơ bản đến senior level.", "max_students": 30, "status": "active"},
        {"name": "React & Frontend Masterclass", "desc": "Lớp học chuyên sâu về React ecosystem: Hooks, Redux, TypeScript và deployment.", "max_students": 25, "status": "active"},
        {"name": "Data Science Foundation", "desc": "Nền tảng Data Science: Pandas, visualization, statistics và ML cơ bản.", "max_students": 20, "status": "active"},
        {"name": "English for Tech - B2 Level", "desc": "Tiếng Anh chuyên ngành công nghệ: technical writing, presentations, interviews.", "max_students": 15, "status": "preparing"},
        {"name": "Digital Marketing Intensive", "desc": "Khóa học Marketing thực chiến: từ strategy đến execution và analytics.", "max_students": 20, "status": "completed"},
    ]

    course_list = list(course_ids.values())

    for i, tmpl in enumerate(class_templates):
        cid = gid()
        instr_id = instructor_ids[i % len(instructor_ids)]
        course_id = course_list[i % len(course_list)]
        start = past(days=random.randint(30, 120))
        end = start + timedelta(days=90)
        # Assign some students
        num_students = random.randint(8, min(tmpl["max_students"], len(student_ids)))
        assigned_students = random.sample(student_ids, num_students)

        cls = Class(
            id=cid,
            name=tmpl["name"],
            description=tmpl["desc"],
            course_id=course_id,
            instructor_id=instr_id,
            invite_code=gid()[:8].upper(),
            max_students=tmpl["max_students"],
            start_date=start,
            end_date=end,
            status=tmpl["status"],
            student_ids=assigned_students,
            created_at=past(days=random.randint(120, 200)),
            updated_at=past(days=random.randint(1, 10)),
        )
        await cls.insert()
        class_ids.append(cid)
        print(f"  Class: {tmpl['name']} ({num_students} students, status: {tmpl['status']})")

    return class_ids


async def seed_enrollments(user_ids: Dict[str, List[str]], course_ids: Dict[str, str]) -> List[str]:
    """Mỗi student enroll vào 3-5 courses ngẫu nhiên"""
    print("\n--- Seeding Enrollments ---")
    student_ids = user_ids["student"]
    all_course_ids = list(course_ids.values())
    enrollments: List[Enrollment] = []
    enrollment_ids: List[str] = []

    for student_id in student_ids:
        # Mỗi student enroll 3-5 courses
        num_courses = random.randint(3, min(5, len(all_course_ids)))
        chosen_courses = random.sample(all_course_ids, num_courses)

        for course_id in chosen_courses:
            statuses_weighted = ["active", "active", "active", "completed", "cancelled"]
            status = random.choice(statuses_weighted)

            progress = 0.0
            completed_at = None
            if status == "completed":
                progress = 100.0
                completed_at = past(days=random.randint(5, 60))
            elif status == "active":
                progress = round(random.uniform(5.0, 95.0), 2)

            # completed_lessons và completed_modules là List[str] UUIDs trong model
            completed_lessons_list: List[str] = []
            completed_modules_list: List[str] = []

            enroll_date = past(days=random.randint(30, 250))
            last_accessed = past(days=random.randint(0, 7)) if status != "cancelled" else None
            avg_score = round(random.uniform(60.0, 98.0), 2) if status != "cancelled" else None
            time_spent = random.randint(60, 2400) if status != "cancelled" else 0

            enroll = Enrollment(
                id=gid(),
                user_id=student_id,
                course_id=course_id,
                status=status,
                progress_percent=progress,
                completion_rate=progress,           # alias, same value
                completed_lessons=completed_lessons_list,
                completed_modules=completed_modules_list,
                avg_quiz_score=avg_score,
                total_time_spent_minutes=time_spent,
                enrolled_at=enroll_date,
                last_accessed_at=last_accessed,
                completed_at=completed_at,
            )
            enrollments.append(enroll)
            enrollment_ids.append(enroll.id)

    await Enrollment.insert_many(enrollments)

    # Update enrollment_count trên Course
    for course_id in all_course_ids:
        count = sum(1 for e in enrollments if e.course_id == course_id and e.status != "cancelled")
        await Course.find_one(Eq(Course.id, course_id)).update(Set({"enrollment_count": count}))

    print(f"  Created {len(enrollments)} enrollments for {len(student_ids)} students")
    return enrollment_ids


async def seed_progress(user_ids: Dict[str, List[str]], lesson_ids: Dict[str, List[str]]):
    """Tạo Progress document cho mỗi active/completed enrollment"""
    print("\n--- Seeding Progress ---")
    student_ids = user_ids["student"]

    active_enrollments = await Enrollment.find(
        In(Enrollment.user_id, student_ids),
        In(Enrollment.status, ["active", "completed"])
    ).to_list()

    progress_docs: List[Progress] = []

    for enroll in active_enrollments:
        course_lesson_ids = lesson_ids.get(enroll.course_id, [])
        if not course_lesson_ids:
            continue

        total_lessons = len(course_lesson_ids)
        overall_pct = enroll.progress_percent

        # Generate lesson-level progress
        lessons_progress: List[LessonProgressItem] = []
        completed_count = 0

        # Fetch lesson documents để lấy module_id
        lesson_docs = await Lesson.find(
            Eq(Lesson.course_id, enroll.course_id)
        ).to_list()
        lesson_module_map: Dict[str, str] = {l.id: l.module_id for l in lesson_docs}

        for i, les_id in enumerate(course_lesson_ids):
            module_id = lesson_module_map.get(les_id) or None  # None nếu không tìm thấy
            lesson_doc = next((l for l in lesson_docs if l.id == les_id), None)
            lesson_title = lesson_doc.title if lesson_doc else f"Lesson {i+1}"

            # Xác định status dựa trên overall progress
            if enroll.status == "completed":
                les_status = "completed"
                completion_date: Optional[datetime] = past(days=random.randint(5, 90))
                time_spent = random.randint(10, lesson_doc.duration_minutes if lesson_doc else 30)
                video_progress = lesson_doc.duration_minutes * 60 if lesson_doc else 1800
                completed_count += 1
            else:
                # Proportion-based: how many lessons completed given overall %
                lesson_idx_normalized = (i + 1) / total_lessons * 100
                if lesson_idx_normalized <= overall_pct - 10:
                    les_status = "completed"
                    completion_date = past(days=random.randint(1, 60))
                    time_spent = random.randint(10, 60)
                    video_progress = (lesson_doc.duration_minutes if lesson_doc else 30) * 60
                    completed_count += 1
                elif lesson_idx_normalized <= overall_pct + 5:
                    les_status = "in-progress"
                    completion_date = None
                    time_spent = random.randint(1, 20)
                    video_progress = random.randint(60, 900)
                else:
                    les_status = "not-started"
                    completion_date = None
                    time_spent = 0
                    video_progress = 0

            # LessonProgressItem — theo models.py (với module_id field mới thêm)
            lessons_progress.append(LessonProgressItem(
                lesson_id=les_id,
                module_id=module_id,
                lesson_title=lesson_title,
                status=les_status,
                completion_date=completion_date if les_status == "completed" else None,
                time_spent_minutes=time_spent,
                video_progress_seconds=video_progress,
            ))

        overall_pct_actual = round((completed_count / total_lessons) * 100, 2)
        total_time = enroll.total_time_spent_minutes
        total_course_mins = sum(l.duration_minutes for l in lesson_docs) if lesson_docs else total_lessons * 30
        remaining_mins = max(0, total_course_mins - total_time)

        progress_doc = Progress(
            id=gid(),
            user_id=enroll.user_id,
            course_id=enroll.course_id,
            enrollment_id=enroll.id,
            overall_progress_percent=overall_pct_actual,
            completed_lessons_count=completed_count,
            total_lessons_count=total_lessons,
            lessons_progress=lessons_progress,
            total_time_spent_minutes=total_time,
            estimated_hours_remaining=round(remaining_mins / 60, 2),
            study_streak_days=random.randint(0, 30),
            avg_quiz_score=enroll.avg_quiz_score or 0.0,
            last_accessed_at=enroll.last_accessed_at,
            created_at=enroll.enrolled_at,
            updated_at=past(days=random.randint(0, 3)),
        )
        progress_docs.append(progress_doc)

    if progress_docs:
        await Progress.insert_many(progress_docs)
    print(f"  Created {len(progress_docs)} progress records")


async def seed_quizzes_and_attempts(user_ids: Dict[str, List[str]], lesson_ids: Dict[str, List[str]]):
    """Tạo 2-3 quizzes mỗi course (lessons có has_quiz=True) và quiz attempts cho students"""
    print("\n--- Seeding Quizzes & Attempts ---")
    student_ids = user_ids["student"]
    instructor_ids = user_ids["instructor"]

    quizzes: List[Quiz] = []
    attempts: List[QuizAttempt] = []

    for course_id, course_lesson_ids in lesson_ids.items():
        if not course_lesson_ids:
            continue

        # Lấy lessons có has_quiz từ catalog (via lesson documents với quiz_id not None)
        quiz_lessons = await Lesson.find(
            Eq(Lesson.course_id, course_id),
        ).to_list()
        quiz_lesson_ids = [l.id for l in quiz_lessons if l.quiz_id is not None]

        for lesson_id in quiz_lesson_ids:
            lesson_doc = next((l for l in quiz_lessons if l.id == lesson_id), None)
            if not lesson_doc:
                continue

            # Tìm pre-generated quiz_id trong lesson
            quiz_id = lesson_doc.quiz_id

            # Sinh questions (6 câu)
            question_count = 6
            questions = []
            total_points = 0

            for qi in range(question_count):
                q_type = random.choice(["multiple_choice", "multiple_choice", "multiple_choice", "true_false"])
                if q_type == "multiple_choice":
                    opts = [f"Đáp án {chr(65+j)}: Lựa chọn số {qi*4+j+1}" for j in range(4)]
                    correct_idx = random.randint(0, 3)
                else:
                    opts = ["Đúng", "Sai"]
                    correct_idx = random.randint(0, 1)

                pts = random.choice([1, 1, 2])
                is_mandatory = qi < 3  # 3 câu đầu là bắt buộc

                q = make_question(
                    qtype=q_type,
                    text=f"[{lesson_doc.title}] Câu {qi+1}: {fake.sentence(nb_words=12)}?",
                    options=opts,
                    correct=str(correct_idx),
                    explanation=f"Giải thích đáp án {chr(65+correct_idx)}: {fake.sentence(nb_words=10)}",
                    points=pts,
                    is_mandatory=is_mandatory,
                    order=qi + 1,
                )
                questions.append(q)
                total_points += pts

            mandatory_count = sum(1 for q in questions if q["is_mandatory"])

            quiz = Quiz(
                id=quiz_id,
                lesson_id=lesson_id,
                course_id=course_id,
                module_id=lesson_doc.module_id,
                title=f"Kiểm tra: {lesson_doc.title}",
                description=f"Quiz kiểm tra kiến thức bài học: {lesson_doc.title}. Cần đạt 70% để vượt qua.",
                quiz_type="review",
                time_limit_minutes=random.randint(10, 20),
                passing_score=70.0,
                max_attempts=3,
                deadline=None,
                is_draft=False,
                questions=questions,
                question_count=question_count,
                total_points=total_points,
                mandatory_question_count=mandatory_count,
                created_by=random.choice(instructor_ids),
                created_at=past(days=random.randint(20, 100)),
                updated_at=past(days=random.randint(1, 10)),
            )
            quizzes.append(quiz)

            # Tạo QuizAttempts cho 5-12 students
            num_attempers = random.randint(5, min(12, len(student_ids)))
            for student_id in random.sample(student_ids, num_attempers):
                # Simulate student answering
                attempt_answers = []
                correct_count = 0
                mandatory_correct_count = 0
                mandatory_total_count = 0

                for q in questions:
                    is_correct_q = random.random() < 0.68
                    opts_count = len(q["options"])
                    if is_correct_q:
                        chosen = int(q["correct_answer"])
                    else:
                        available = [j for j in range(opts_count) if j != int(q["correct_answer"])]
                        chosen = random.choice(available)

                    if is_correct_q:
                        correct_count += 1
                    if q["is_mandatory"]:
                        mandatory_total_count += 1
                        if is_correct_q:
                            mandatory_correct_count += 1

                    # QuestionResult structure theo quiz.py
                    attempt_answers.append({
                        "question_id": q["id"],
                        "question_content": q["question_text"],
                        "student_answer": str(chosen),
                        "correct_answer": q["correct_answer"],
                        "is_correct": is_correct_q,
                        "is_mandatory": q["is_mandatory"],
                        "score": float(q["points"]) if is_correct_q else 0.0,
                        "explanation": q["explanation"],
                        "related_lesson_link": f"https://ailearning.vn/lessons/{lesson_id}",
                    })

                score = round((correct_count / question_count) * 100, 2)
                passed = score >= 70.0
                mandatory_passed = (mandatory_correct_count >= mandatory_total_count) if mandatory_total_count > 0 else True
                started = past(days=random.randint(1, 50), hours=random.randint(0, 23))
                submitted = started + timedelta(seconds=random.randint(200, 1200))

                attempt = QuizAttempt(
                    id=gid(),
                    quiz_id=quiz_id,
                    user_id=student_id,
                    answers=attempt_answers,
                    score=score,
                    status="Pass" if passed else "Fail",
                    passed=passed,
                    attempt_number=random.randint(1, 3),
                    correct_answers=correct_count,
                    total_questions=question_count,
                    mandatory_correct=mandatory_correct_count,
                    mandatory_total=mandatory_total_count,
                    mandatory_passed=mandatory_passed,
                    can_retake=not passed,
                    started_at=started,
                    submitted_at=submitted,
                    time_spent_seconds=(submitted - started).seconds,
                )
                attempts.append(attempt)

    if quizzes:
        await Quiz.insert_many(quizzes)
    if attempts:
        await QuizAttempt.insert_many(attempts)

    print(f"  Created {len(quizzes)} quizzes and {len(attempts)} quiz attempts")


async def seed_assessment_sessions(user_ids: Dict[str, List[str]]) -> Dict[str, str]:
    """Tạo 2 AssessmentSession cho mỗi student"""
    print("\n--- Seeding Assessment Sessions ---")
    student_ids = user_ids["student"]

    ASSESSMENT_SUBJECTS = {
        "Programming": {
            "subjects": ["Python", "JavaScript", "SQL"],
            "focus_areas": [["python-syntax", "python-oop"], ["javascript-es6", "react"], ["sql-queries", "database-design"]],
            "skill_tags": ["python-syntax", "python-oop", "python-functions", "python-debugging"],
        },
        "Data Science": {
            "subjects": ["Pandas", "Machine Learning"],
            "focus_areas": [["data-cleaning", "eda"], ["regression", "classification"]],
            "skill_tags": ["pandas-dataframe", "data-visualization", "ml-algorithms", "feature-engineering"],
        },
        "Business": {
            "subjects": ["Marketing", "Project Management"],
            "focus_areas": [["seo", "content-marketing"], ["agile", "scrum"]],
            "skill_tags": ["digital-marketing", "google-analytics", "project-planning", "stakeholder-management"],
        },
        "Languages": {
            "subjects": ["English B1-B2"],
            "focus_areas": [["grammar", "vocabulary", "speaking"]],
            "skill_tags": ["english-grammar", "english-vocabulary", "english-speaking", "ielts-writing"],
        },
    }

    sessions: List[AssessmentSession] = []
    user_session_map: Dict[str, str] = {}  # user_id -> latest evaluated session_id

    for student_id in student_ids:
        num_sessions = random.choice([1, 2, 2, 2, 3])
        for s_idx in range(num_sessions):
            category = random.choice(list(ASSESSMENT_SUBJECTS.keys()))
            cat_data = ASSESSMENT_SUBJECTS[category]
            subject_idx = random.randint(0, len(cat_data["subjects"]) - 1)
            subject = cat_data["subjects"][subject_idx]
            focus_areas = cat_data["focus_areas"][subject_idx]
            skill_tags = cat_data["skill_tags"]
            level = random.choice(["Beginner", "Beginner", "Intermediate", "Advanced"])

            # Sinh 10 câu hỏi — assessment.py AssessmentQuestion schema
            q_count = 10
            qestions_data = []
            difficulties = ["easy"] * 4 + ["medium"] * 4 + ["hard"] * 2
            random.shuffle(difficulties)

            for qidx in range(q_count):
                diff = difficulties[qidx]
                pts = 1 if diff == "easy" else (2 if diff == "medium" else 3)
                s_tag = skill_tags[qidx % len(skill_tags)]
                opts = [f"{chr(65+j)}. {fake.sentence(nb_words=6)}" for j in range(4)]
                qestions_data.append(make_assessment_question(
                    qtext=f"[{subject}] {fake.sentence(nb_words=14)}?",
                    qtype="multiple_choice",
                    difficulty=diff,
                    skill_tag=s_tag,
                    points=pts,
                    options=opts,
                    hint=f"Gợi ý: Đáp án liên quan đến {s_tag.replace('-', ' ')}",
                ))

            statuses = ["evaluated", "evaluated", "evaluated", "submitted", "in_progress"]
            status = statuses[s_idx] if s_idx < len(statuses) else "evaluated"
            created = past(days=random.randint(10, 180))
            expires = created + timedelta(hours=1)

            session = AssessmentSession(
                id=gid(),
                user_id=student_id,
                category=category,
                subject=subject,
                level=level,
                focus_areas=focus_areas,
                total_questions=q_count,
                time_limit_minutes=30,
                questions=qestions_data,
                status=status,
                answers=[],
                overall_score=None,
                proficiency_level=None,
                correct_answers=None,
                skill_analysis=None,
                knowledge_gaps=[],
                ai_feedback=None,
                time_analysis=None,
                created_at=created,
                expires_at=expires,
                submitted_at=None,
                evaluated_at=None,
            )

            if status in ("submitted", "evaluated"):
                submitted_at = created + timedelta(minutes=random.randint(10, 28))
                session.submitted_at = submitted_at

                # Generate answers — assessment.py AssessmentAnswer schema
                answer_times: List[int] = []
                answers = []
                for q in qestions_data:
                    t = random.randint(15, 120)
                    answer_times.append(t)
                    chosen = random.randint(0, 3)
                    answers.append({
                        "question_id": q["question_id"],
                        "answer_content": str(chosen),
                        "selected_option": chosen,
                        "time_taken_seconds": t,
                    })
                session.answers = answers

            if status == "evaluated":
                score = round(random.uniform(35.0, 97.0), 2)
                session.evaluated_at = session.submitted_at + timedelta(seconds=random.randint(30, 90))
                session.overall_score = score
                proficiency = "Beginner" if score < 50 else ("Intermediate" if score < 78 else "Advanced")
                session.proficiency_level = proficiency
                session.correct_answers = max(1, int(q_count * score / 100))

                # skill_analysis — List[SkillAnalysis] (assessment.py)
                unique_skill_tags = list(set(q["skill_tag"] for q in qestions_data))
                skill_analysis_list = []
                for tag in unique_skill_tags:
                    tag_qs = [q for q in qestions_data if q["skill_tag"] == tag]
                    tag_count = len(tag_qs)
                    tag_correct = max(0, int(tag_count * score / 100))
                    prof_pct = round((tag_correct / tag_count) * 100, 1) if tag_count else 0.0
                    strength = "Strong" if prof_pct >= 75 else ("Average" if prof_pct >= 50 else "Weak")
                    skill_analysis_list.append({
                        "skill_tag": tag,
                        "questions_count": tag_count,
                        "correct_count": tag_correct,
                        "proficiency_percentage": prof_pct,
                        "strength_level": strength,
                        "detailed_feedback": f"Bạn {'nắm vững' if strength == 'Strong' else ('cần cải thiện' if strength == 'Average' else 'cần tập trung nhiều hơn vào')} kỹ năng {tag.replace('-', ' ')}.",
                    })
                session.skill_analysis = skill_analysis_list  # List[dict]

                # knowledge_gaps — List[KnowledgeGap] (assessment.py)
                weak_skills = [s for s in skill_analysis_list if s["strength_level"] in ("Weak", "Average")][:3]
                session.knowledge_gaps = [
                    {
                        "gap_area": s["skill_tag"].replace("-", " ").title(),
                        "description": f"Cần củng cố kiến thức về {s['skill_tag'].replace('-', ' ')} — chỉ đạt {s['proficiency_percentage']}%.",
                        "importance": "High" if s["strength_level"] == "Weak" else "Medium",
                        "suggested_action": f"Xem lại bài học về {s['skill_tag'].replace('-', ' ')} và làm thêm practice exercises.",
                    }
                    for s in weak_skills
                ]
                if not session.knowledge_gaps:
                    session.knowledge_gaps = [{
                        "gap_area": "Advanced Concepts",
                        "description": f"Cần nâng cao các kỹ năng nâng cao trong {subject}.",
                        "importance": "Low",
                        "suggested_action": f"Học khóa {subject} level cao hơn.",
                    }]

                # time_analysis — TimeAnalysis (assessment.py)
                total_time = sum(answer_times)
                session.time_analysis = {
                    "total_time_seconds": total_time,
                    "average_time_per_question": round(total_time / q_count, 1),
                    "fastest_question_time": min(answer_times),
                    "slowest_question_time": max(answer_times),
                }

                # ai_feedback (models.py field mới thêm)
                session.ai_feedback = (
                    f"Dựa trên kết quả đánh giá {subject}, bạn đang ở trình độ **{proficiency}** với điểm số {score:.1f}/100. "
                    f"Bạn trả lời đúng {session.correct_answers}/{q_count} câu hỏi. "
                    f"{'Bạn có nền tảng tốt, hãy thử thách bản thân với những câu hỏi khó hơn.' if score >= 70 else 'Bạn cần tập trung vào các kỹ năng cơ bản trước.'} "
                    f"Các lĩnh vực cần cải thiện: {', '.join(s['skill_tag'] for s in weak_skills[:2]) if weak_skills else 'Tiếp tục duy trì phong độ'}."
                )

                if student_id not in user_session_map:
                    user_session_map[student_id] = session.id

            sessions.append(session)

    if sessions:
        await AssessmentSession.insert_many(sessions)
    print(f"  Created {len(sessions)} assessment sessions")
    return user_session_map


async def seed_recommendations(user_ids: Dict[str, List[str]], course_ids: Dict[str, str], session_map: Dict[str, str]):
    """Tạo Recommendation cho mỗi student có assessment session"""
    print("\n--- Seeding Recommendations ---")
    all_courses = list(course_ids.items())  # [(title, id)]
    recommendations: List[Recommendation] = []

    for student_id, session_id in session_map.items():
        # Chọn 3 courses để recommend
        rec_courses_sample = random.sample(all_courses, min(3, len(all_courses)))
        recommended_courses = []
        for rank, (c_title, c_id) in enumerate(rec_courses_sample, start=1):
            # RecommendedCourseItem (recommendation.py)
            c_doc = await Course.get(c_id)
            recommended_courses.append({
                "course_id": c_id,
                "title": c_title,
                "description": c_doc.description[:200] + "..." if c_doc else c_title,
                "category": c_doc.category if c_doc else "Programming",
                "level": c_doc.level if c_doc else "Beginner",
                "thumbnail_url": c_doc.thumbnail_url if c_doc else None,
                "priority_rank": rank,
                "relevance_score": round(random.uniform(65.0, 98.0), 1),
                "reason": f"Dựa trên kết quả đánh giá và sở thích học tập của bạn, khóa học này sẽ giúp bạn cải thiện kỹ năng.",
                "addresses_gaps": [f"gap-skill-{rank}", f"gap-concept-{rank}"],
                "estimated_completion_days": random.randint(21, 90),
            })

        # suggested_learning_order — LearningStep (recommendation.py)
        suggested_order = [
            {
                "step": i + 1,
                "course_id": rc["course_id"],
                "focus_modules": [f"Module {j+1}" for j in range(2)],
                "why_this_order": f"Bước {i+1}: Học {'nền tảng' if i == 0 else 'nâng cao'} trước để có cơ sở vững chắc.",
            }
            for i, rc in enumerate(recommended_courses)
        ]

        # practice_exercises — PracticeExerciseItem (recommendation.py)
        # Sử dụng category/subject tử session để tạo skill_tag thực tế
        session_doc = await AssessmentSession.get(session_id)
        base_skills = (
            [s["skill_tag"] for s in (session_doc.skill_analysis or [])[:3]]
            if session_doc and session_doc.skill_analysis
            else ["python-basics", "data-structures", "algorithms"]
        )
        practice_exercises = [
            {
                "skill_tag": base_skills[i % len(base_skills)],
                "exercise_type": random.choice(["coding", "quiz", "project", "reading"]),
                "description": f"Bài tập {i+1}: Ôn luyện kỹ năng {base_skills[i % len(base_skills)].replace('-', ' ')}",
                "difficulty": random.choice(["easy", "medium", "hard"]),
                "estimated_time_hours": round(random.uniform(0.5, 3.0), 1),
            }
            for i in range(3)
        ]

        rec = Recommendation(
            id=gid(),
            user_id=student_id,
            source="assessment",
            assessment_session_id=session_id,
            user_proficiency_level=random.choice(["Beginner", "Intermediate", "Advanced"]),
            recommended_courses=recommended_courses,
            suggested_learning_order=suggested_order,
            practice_exercises=practice_exercises,
            ai_personalized_advice=(
                f"Dựa trên lịch sử học tập và kết quả đánh giá của bạn, chúng tôi đề xuất lộ trình học tập "
                f"gồm {len(recommended_courses)} khóa học được sắp xếp theo thứ tự phù hợp nhất. "
                f"Hãy bắt đầu với khóa học ưu tiên số 1 và dành 30 phút mỗi ngày để đạt kết quả tốt nhất."
            ),
            total_estimated_hours=round(sum(r["estimated_completion_days"] * 0.5 for r in recommended_courses), 1),
            created_at=past(days=random.randint(1, 30)),
            expires_at=future(days=90),
        )
        recommendations.append(rec)

    if recommendations:
        await Recommendation.insert_many(recommendations)
    print(f"  Created {len(recommendations)} recommendations")


async def seed_conversations(user_ids: Dict[str, List[str]], course_ids: Dict[str, str]):
    """Tạo 2-3 conversations mỗi student với enrolled courses"""
    print("\n--- Seeding Conversations ---")
    student_ids = user_ids["student"]
    all_course_ids = list(course_ids.values())
    conversations: List[Conversation] = []

    msg_pairs = [
        ("Hàm trong Python hoạt động như thế nào?", "Hàm trong Python được định nghĩa bằng từ khóa `def`. Mỗi hàm có thể nhận tham số và trả về giá trị..."),
        ("Sự khác biệt giữa list và tuple là gì?", "List có thể thay đổi (mutable) còn tuple thì không thể thay đổi (immutable). List dùng `[]` còn tuple dùng `()`..."),
        ("Làm sao để đọc file CSV với Pandas?", "Bạn dùng `pd.read_csv('file.csv')`. Có thể thêm các params như `sep=','`, `encoding='utf-8'`, `index_col=0`..."),
        ("useEffect trong React dùng để làm gì?", "useEffect là hook để handle side effects: fetching data, subscriptions, DOM manipulation. Chạy sau mỗi render..."),
        ("Giải thích về correlation trong thống kê?", "Correlation đo lường mức độ tương quan giữa 2 biến. Pearson correlation r: từ -1 đến 1. r=1 tương quan hoàn hảo dương..."),
        ("Cách viết subject line email hiệu quả?", "Subject line tốt cần: ngắn gọn (< 50 ký tự), cụ thể, tạo urgency, personalization. Ví dụ: 'Báo cáo Q1 - cần review trước 5h'..."),
    ]

    for student_id in student_ids:
        num_convos = random.randint(1, 3)
        chosen_courses = random.sample(all_course_ids, min(num_convos, len(all_course_ids)))

        for course_id in chosen_courses:
            c_doc = await Course.get(course_id)
            if not c_doc:
                continue

            num_messages = random.randint(3, 8)
            messages = []
            convo_start = past(days=random.randint(1, 60))

            for i in range(num_messages):
                pair = msg_pairs[i % len(msg_pairs)]
                ts = convo_start + timedelta(minutes=i * random.randint(2, 15))
                # chat.py Message schema: {message_id, role, content, timestamp, sources}
                # KEY: 'message_id' (NOT 'id'), 'timestamp' (NOT 'created_at')
                messages.append({
                    "message_id": gid(),
                    "role": "user",
                    "content": pair[0],
                    "timestamp": ts.isoformat(),
                    "sources": None,
                })
                messages.append({
                    "message_id": gid(),
                    "role": "assistant",
                    "content": pair[1],
                    "timestamp": (ts + timedelta(seconds=random.randint(3, 15))).isoformat(),
                    "sources": None,
                })

            last_msg_at = convo_start + timedelta(minutes=num_messages * 10)

            conv = Conversation(
                id=gid(),
                user_id=student_id,
                course_id=course_id,
                title=f"Hỏi đáp về {c_doc.title[:40]}",
                summary=f"Cuộc trò chuyện về các khái niệm trong {c_doc.category}",
                course_title=c_doc.title,
                messages=messages,
                total_messages=len(messages),
                last_message_at=last_msg_at,
                created_at=convo_start,
                updated_at=last_msg_at,
            )
            conversations.append(conv)

    if conversations:
        await Conversation.insert_many(conversations)
    print(f"  Created {len(conversations)} conversations")


async def seed_personal_courses(user_ids: Dict[str, List[str]]):
    """Tạo personal courses cho 5 students đầu"""
    print("\n--- Seeding Personal Courses ---")
    selected_students = user_ids["student"][:5]

    personal_templates = [
        {"title": "Chinh phục IELTS 7.0+ — Lộ trình Cá nhân", "desc": "Khóa học tự tổng hợp từ nhiều nguồn để ôn IELTS đạt 7.0+. Tập trung vào 4 kỹ năng và chiến lược làm bài.", "category": "Languages", "level": "Advanced"},
        {"title": "Toán học cho Data Science", "desc": "Tự học các phần toán cần thiết: Linear Algebra (Ma trận, vector), Calculus (đạo hàm), Probability & Statistics.", "category": "Math", "level": "Intermediate"},
        {"title": "Xây dựng Portfolio Full-Stack", "desc": "Dự án cá nhân: xây dựng app quản lý công việc với React + FastAPI + PostgreSQL để showcase trên GitHub.", "category": "Programming", "level": "Advanced"},
        {"title": "Khởi nghiệp từ Zero", "desc": "Tổng hợp kiến thức về khởi nghiệp: idea validation, MVP, business model canvas, funding stages.", "category": "Business", "level": "Beginner"},
        {"title": "Thiền định và Productivity", "desc": "Kết hợp thiền Mindfulness với kỹ thuật Pomodoro và GTD để tăng năng suất học tập và công việc.", "category": "Personal Development", "level": "Beginner"},
    ]

    personal_courses: List[Course] = []
    personal_modules: List[Module] = []
    personal_lessons_list: List[Lesson] = []

    for i, student_id in enumerate(selected_students):
        tmpl = personal_templates[i % len(personal_templates)]
        course_id = gid()
        student = await User.get(student_id)
        if not student:
            continue

        # 3 modules, mỗi module 3 lessons
        embedded_mods: List[EmbeddedModule] = []
        sep_mods: List[Module] = []
        sep_less: List[Lesson] = []
        total_dur = 0
        total_less = 0

        for mod_i in range(3):
            module_id = gid()
            emb_lessions: List[EmbeddedLesson] = []
            sep_lessions_internal: List[Lesson] = []
            mod_dur = 0

            mod_outcomes = [
                make_module_outcome(f"Mục tiêu {mod_i+1}.{j+1}: {fake.sentence(nb_words=8)}", f"{tmpl['category'].lower()}-skill-{mod_i*3+j+1}", j < 2)
                for j in range(3)
            ]
            mod_resources = [
                make_resource("link", f"Reference {mod_i+1}", f"https://example.com/personal/{course_id}/module{mod_i+1}", 0.0, "Tài liệu tham khảo"),
                make_resource("pdf", f"Notes Module {mod_i+1}", f"https://docs.example.com/personal/{course_id}/module{mod_i+1}.pdf", round(random.uniform(0.5, 3.0), 1), "Ghi chú cá nhân"),
            ]

            for les_i in range(3):
                lesson_id = gid()
                lesson_content = {
                    "video_url": f"https://www.youtube.com/watch?v=personal_{course_id[:8]}_{les_i}",
                    "video_duration_seconds": random.randint(900, 3600),
                    "text_content": f"<h2>Bài {les_i+1}</h2><p>{fake.paragraph(nb_sentences=4)}</p>",
                    "code_example": None,
                }
                les_resources = [
                    make_resource("link", f"Resource {les_i+1}", f"https://example.com/lesson/{les_i+1}", 0.0, "Tài liệu tham khảo"),
                ]
                dur = random.randint(20, 50)
                mod_dur += dur

                emb_lesson = EmbeddedLesson(
                    id=lesson_id,
                    title=f"Bài {les_i+1}: {fake.catch_phrase()}",
                    description=fake.sentence(nb_words=12),
                    order=les_i + 1,
                    content=json.dumps(lesson_content),
                    content_type=random.choice(["text", "video", "mixed"]),
                    duration_minutes=dur,
                    video_url=lesson_content["video_url"],
                    audio_url=None,
                    resources=les_resources,
                    learning_objectives=[fake.sentence(nb_words=8) for _ in range(2)],
                    quiz_id=None,
                    is_published=True,
                    created_at=past(days=random.randint(5, 30)),
                    updated_at=past(days=random.randint(1, 5)),
                )
                emb_lessions.append(emb_lesson)

                sep_lesson = Lesson(
                    id=lesson_id,
                    module_id=module_id,
                    course_id=course_id,
                    title=emb_lesson.title,
                    description=emb_lesson.description,
                    order=les_i + 1,
                    content=emb_lesson.content,
                    content_type=emb_lesson.content_type,
                    duration_minutes=dur,
                    video_url=emb_lesson.video_url,
                    audio_url=None,
                    learning_objectives=emb_lesson.learning_objectives,
                    resources=les_resources,
                    quiz_id=None,
                    is_published=True,
                    created_at=emb_lesson.created_at,
                    updated_at=emb_lesson.updated_at,
                )
                sep_lessions_internal.append(sep_lesson)

            emb_module = EmbeddedModule(
                id=module_id,
                title=f"Module {mod_i+1}: {fake.bs().title()}",
                description=fake.sentence(nb_words=15),
                order=mod_i + 1,
                difficulty=random.choice(["Basic", "Intermediate", "Advanced"]),
                estimated_hours=round(mod_dur / 60, 1),
                learning_outcomes=mod_outcomes,
                prerequisites=[embedded_mods[mod_i-1].id] if mod_i > 0 else [],
                resources=mod_resources,
                lessons=emb_lessions,
                total_lessons=len(emb_lessions),
                total_duration_minutes=mod_dur,
                created_at=past(days=random.randint(10, 40)),
                updated_at=past(days=random.randint(1, 5)),
            )
            embedded_mods.append(emb_module)

            sep_mod = Module(
                id=module_id,
                course_id=course_id,
                title=emb_module.title,
                description=emb_module.description,
                order=mod_i + 1,
                difficulty=emb_module.difficulty,
                estimated_hours=emb_module.estimated_hours,
                learning_outcomes=mod_outcomes,
                resources=mod_resources,
                prerequisites=[embedded_mods[mod_i-1].id] if mod_i > 0 else [],
                total_lessons=len(emb_lessions),
                total_duration_minutes=mod_dur,
                created_at=emb_module.created_at,
                updated_at=emb_module.updated_at,
            )
            sep_mods.append(sep_mod)
            sep_less.extend(sep_lessions_internal)
            total_dur += mod_dur
            total_less += len(emb_lessions)

        personal_course = Course(
            id=course_id,
            title=tmpl["title"],
            description=tmpl["desc"],
            category=tmpl["category"],
            level=tmpl["level"],
            thumbnail_url=None,
            preview_video_url=None,
            language="vi",
            status=random.choice(["draft", "published", "draft"]),
            owner_id=student_id,
            owner_type="student",
            course_type="personal",
            instructor_id=None,
            instructor_name=student.full_name,
            instructor_avatar=student.avatar_url,
            instructor_bio=student.bio,
            # course.py LearningOutcome: {description, skill_tag} — NO id
            learning_outcomes=[
                make_course_outcome(fake.sentence(nb_words=10), f"{tmpl['category'].lower()}-skill-{j+1}")
                for j in range(3)
            ],
            prerequisites=[],
            modules=embedded_mods,
            total_duration_minutes=total_dur,
            total_modules=len(embedded_mods),
            total_lessons=total_less,
            enrollment_count=0,
            avg_rating=None,
            created_at=past(days=random.randint(10, 60)),
            updated_at=past(days=random.randint(1, 7)),
        )
        personal_courses.append(personal_course)
        personal_modules.extend(sep_mods)
        personal_lessons_list.extend(sep_less)

    if personal_courses:
        await Course.insert_many(personal_courses)
    if personal_modules:
        await Module.insert_many(personal_modules)
    if personal_lessons_list:
        await Lesson.insert_many(personal_lessons_list)

    print(f"  Created {len(personal_courses)} personal courses with {len(personal_modules)} modules and {len(personal_lessons_list)} lessons")


async def seed_refresh_tokens(user_ids: Dict[str, List[str]]):
    """
    Tạo RefreshToken mẫu cho tất cả users đang active.
    auth.py: LoginResponse trả về refresh_token — model RefreshToken cần có data.
    Mỗi user active được tạo 1 token hợp lệ (remember_me=True, 7 ngày)
    RefreshToken fields: id, user_id, token (unique str), expires_at, created_at
    """
    import secrets
    print("\n--- Seeding Refresh Tokens ---")
    tokens: List[RefreshToken] = []

    all_user_ids = user_ids["admin"] + user_ids["instructor"] + user_ids["student"]

    # Lấy chỉ active users để seed token
    active_users = await User.find(
        In(User.id, all_user_ids),
        Eq(User.status, "active")
    ).to_list()

    for u in active_users:
        # Mỗi user có 1 refresh token hiện tại (mẫng login gần nhất)
        token_str = secrets.token_urlsafe(64)  # Token ngẫu nhiên an toàn
        created = past(days=random.randint(0, 7))
        tokens.append(RefreshToken(
            id=gid(),
            user_id=u.id,
            token=token_str,
            expires_at=created + timedelta(days=7),   # remember_me=True → 7 ngày
            created_at=created,
        ))

    if tokens:
        await RefreshToken.insert_many(tokens)
    print(f"  Created {len(tokens)} refresh tokens for active users")


# ─── MAIN ────────────────────────────────────────────────────────────────────────

async def main():
    print("=" * 60)
    print("AI Learning Platform — Comprehensive Database Seed")
    print("=" * 60)

    settings = get_settings()
    await init_db()
    print(f"Connected to MongoDB: {settings.mongodb_url[:40]}...")

    # 1. Clear
    await drop_all_collections()

    # 2. Users
    user_ids = await seed_users()

    # 3. Courses (title->id map)
    course_ids = await seed_courses(user_ids)

    # 4. Modules & Lessons — hybrid architecture
    lesson_ids = await seed_modules_and_lessons(course_ids)

    # 5. Classes
    await seed_classes(user_ids, course_ids)

    # 6. Enrollments
    await seed_enrollments(user_ids, course_ids)

    # 7. Progress (needs lesson_ids for mapping)
    await seed_progress(user_ids, lesson_ids)

    # 8. Quizzes & Attempts
    await seed_quizzes_and_attempts(user_ids, lesson_ids)

    # 9. Assessment Sessions
    session_map = await seed_assessment_sessions(user_ids)

    # 10. Recommendations (needs session_map)
    await seed_recommendations(user_ids, course_ids, session_map)

    # 11. Conversations
    await seed_conversations(user_ids, course_ids)

    # 12. Personal Courses
    await seed_personal_courses(user_ids)

    # 13. Refresh Tokens (auth.py: để test login/refresh flow)
    await seed_refresh_tokens(user_ids)

    print("\n" + "=" * 60)
    print("Seed completed successfully!")
    print(f"  Users: {len(user_ids['admin'])} admin + {len(user_ids['instructor'])} instructor + {len(user_ids['student'])} student (incl. banned/inactive)")
    print(f"  Courses: {len(course_ids)} public courses (7 × 4 modules × 4 lessons = 112 lessons)")
    print("  + 5 personal courses")
    print("  Classes, Enrollments, Progress, Quizzes, Assessments, Conversations, Recommendations, RefreshTokens: done")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
