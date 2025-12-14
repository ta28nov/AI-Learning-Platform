"""
Pytest configuration và fixtures dùng chung cho tất cả test files.
Cung cấp test client, test database, và test data chuẩn.
Sử dụng pattern từ init_data.py để tạo dữ liệu test realistic.
"""
import pytest
import asyncio
from typing import Dict, Any, List
from httpx import AsyncClient, ASGITransport
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from faker import Faker
from datetime import datetime, timezone, timedelta
import random
import sys
import os

# Thêm đường dẫn gốc vào sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.main import app
from config.config import get_settings
from models.models import (
    User, Course, Module, Lesson, Enrollment, Progress,
    AssessmentSession, Quiz, QuizAttempt, Class, Conversation,
    Recommendation, RefreshToken, PasswordResetTokenDocument,
    EmbeddedModule, EmbeddedLesson
)
from utils.security import hash_password, create_access_token

# Khởi tạo Faker với locale tiếng Việt
fake = Faker('vi_VN')

# Test database settings
TEST_MONGODB_URL = "mongodb://localhost:27017"
TEST_DATABASE_NAME = "ai_learning_test_db"


@pytest.fixture
async def test_db():
    """
    Khởi tạo test database và cleanup sau mỗi test.
    Scope: function - mỗi test có database riêng sạch sẽ.
    """
    # Kết nối MongoDB test
    client = AsyncIOMotorClient(TEST_MONGODB_URL)
    database = client[TEST_DATABASE_NAME]
    
    # Khởi tạo Beanie với test database
    await init_beanie(
        database=database,
        document_models=[
            User, RefreshToken, PasswordResetTokenDocument,
            Course, Module, Lesson, Enrollment, Progress,
            AssessmentSession, Quiz, QuizAttempt, Class,
            Conversation, Recommendation
        ]
    )
    
    yield database
    
    # Cleanup: Xóa tất cả collections sau mỗi test
    for collection_name in await database.list_collection_names():
        await database[collection_name].delete_many({})
    
    client.close()


@pytest.fixture
async def client(test_db):
    """
    HTTP client để gọi API endpoints.
    Sử dụng test database đã được setup.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture(scope="function")
async def test_users(test_db) -> Dict[str, Any]:
    """
    Tạo test users chuẩn: 1 admin, 2 instructors, 5 students.
    Sử dụng Faker để tạo dữ liệu realistic.
    Return dict với user IDs, emails, passwords và tokens.
    """
    users_data = {}
    
    # 1. Tạo Admin
    admin = User(
        full_name="Quản Trị Viên Test",
        email="admin.test@ailab.com.vn",
        hashed_password=hash_password("Admin@12345"),
        role="admin",
        status="active",
        email_verified=True,
        bio="Admin test account cho hệ thống",
        learning_preferences=["Programming", "Data Science", "AI"],
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    await admin.insert()
    
    admin_token = create_access_token({"sub": admin.email, "role": admin.role})
    users_data["admin"] = {
        "id": str(admin.id),
        "email": admin.email,
        "password": "Admin@12345",
        "role": admin.role,
        "token": admin_token,
        "user_obj": admin
    }
    
    # 2. Tạo Instructors
    instructor_names = ["Nguyễn Văn An", "Trần Thị Bình"]
    for i, name in enumerate(instructor_names, 1):
        instructor = User(
            full_name=name,
            email=f"instructor{i}@test.com",
            hashed_password=hash_password("Instructor@123"),
            role="instructor",
            status="active",
            email_verified=True,
            bio=f"Giảng viên {name} - Chuyên gia về {random.choice(['Python', 'Java', 'Web Development'])}",
            learning_preferences=["Programming", "Teaching"],
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        await instructor.insert()
        
        instructor_token = create_access_token({"sub": instructor.email, "role": instructor.role})
        users_data[f"instructor{i}"] = {
            "id": str(instructor.id),
            "email": instructor.email,
            "password": "Instructor@123",
            "role": instructor.role,
            "token": instructor_token,
            "user_obj": instructor
        }
    
    # 3. Tạo Students
    for i in range(1, 6):
        student_name = fake.name()
        student = User(
            full_name=student_name,
            email=f"student{i}@test.com",
            hashed_password=hash_password("Student@123"),
            role="student",
            status="active",
            email_verified=True,
            bio=f"Học viên {student_name}",
            learning_preferences=random.sample(
                ["Programming", "Data Science", "Web Development", "Mobile Development", "AI"],
                k=random.randint(1, 3)
            ),
            created_at=datetime.now(timezone.utc) - timedelta(days=random.randint(1, 90)),
            updated_at=datetime.now(timezone.utc)
        )
        await student.insert()
        
        student_token = create_access_token({"sub": student.email, "role": student.role})
        users_data[f"student{i}"] = {
            "id": str(student.id),
            "email": student.email,
            "password": "Student@123",
            "role": student.role,
            "token": student_token,
            "user_obj": student
        }
    
    return users_data


@pytest.fixture(scope="function")
async def test_course(test_db, test_users) -> Dict[str, Any]:
    """
    Tạo 1 khóa học test đầy đủ với modules và lessons.
    """
    admin_id = test_users["admin"]["id"]
    
    course = Course(
        title="Python Programming Test Course",
        description="Khóa học Python test đầy đủ",
        category="Programming",
        level="Beginner",
        status="published",
        owner_id=admin_id,
        owner_type="admin",
        language="vi",
        total_modules=2,
        total_lessons=4,
        total_duration_minutes=200,
        learning_outcomes=[
            {"id": "1", "description": "Learn Python basics", "skill_tag": "python-basics"}
        ],
        prerequisites=["Basic computer knowledge"]
    )
    await course.insert()
    
    # Tạo 2 modules với embedded lessons
    embedded_modules = []
    modules_data = []
    
    for i in range(1, 3):
        # Tạo embedded lessons cho module này
        embedded_lessons = []
        for j in range(1, 3):
            embedded_lesson = EmbeddedLesson(
                title=f"Lesson {j} - Module {i}",
                description=f"Lesson {j} description",
                order=j,
                content='{"html_content": "Test content"}',
                content_type="text",
                duration_minutes=50
            )
            embedded_lessons.append(embedded_lesson)
            
        # Tạo embedded module
        embedded_module = EmbeddedModule(
            title=f"Module {i}: Python Basics",
            description=f"Module {i} description",
            order=i,
            difficulty="Basic",
            estimated_hours=2.0,
            total_lessons=2,
            total_duration_minutes=100,
            learning_outcomes=[
                {"description": f"Outcome {i}", "skill_tag": f"skill-{i}"}
            ],
            lessons=embedded_lessons
        )
        embedded_modules.append(embedded_module)
        
        # Tạo Module document riêng (nếu cần cho các test khác)
        module = Module(
            course_id=str(course.id),
            title=f"Module {i}: Python Basics",
            description=f"Module {i} description",
            order=i,
            difficulty="Basic",
            estimated_hours=2.0,
            total_lessons=2,
            total_duration_minutes=100,
            learning_outcomes=[
                {"description": f"Outcome {i}", "skill_tag": f"skill-{i}"}
            ]
        )
        await module.insert()
        modules_data.append(module)
        
        # Tạo 2 lessons cho mỗi module document
        for j in range(1, 3):
            lesson = Lesson(
                module_id=str(module.id),
                course_id=str(course.id),
                title=f"Lesson {j} - Module {i}",
                description=f"Lesson {j} description",
                order=j,
                content='{"html_content": "Test content"}',
                content_type="text",
                duration_minutes=50,
                is_published=True
            )
            await lesson.insert()
    
    # Cập nhật course với embedded modules
    course.modules = embedded_modules
    await course.replace()
    
    return {
        "course_id": str(course.id),
        "course": course,
        "modules": embedded_modules  # Return embedded modules for direct access
    }


@pytest.fixture(scope="function")
async def test_enrollment(test_db, test_users, test_course) -> Dict[str, Any]:
    """
    Tạo enrollment cho student1 vào test course.
    """
    student_id = test_users["student1"]["id"]
    course_id = test_course["course_id"]
    
    enrollment = Enrollment(
        user_id=student_id,
        course_id=course_id,
        status="active",
        progress_percent=0.0
    )
    await enrollment.insert()
    
    return {
        "enrollment_id": str(enrollment.id),
        "enrollment": enrollment
    }


# Global cache cho test_vars theo session
_test_vars_cache = {}


@pytest.fixture(scope="session")
def event_loop_policy():
    """Provide event loop policy for session-scoped async fixtures."""
    return asyncio.get_event_loop_policy()


@pytest.fixture(scope="function")
async def test_vars(client, test_users, test_course, test_enrollment):
    """
    Fixture cung cấp TestVariables đã setup sẵn.
    TỰ ĐỘNG SETUP mỗi khi chạy test - không cần khai báo!
    
    Usage - CÁCH 1 (với parameter):
        async def test_example(test_vars):
            headers = test_vars.get_headers("student1")
    
    Usage - CÁCH 2 (tự động inject vào self):
        class TestExample:
            async def test_something(self):
                headers = self.test_vars.get_headers("student1")
    """
    from tests.test_variables import TestVariables
    
    # Tạo instance mới cho mỗi test
    vars = TestVariables()
    await vars.setup(client, test_users)
    
    # Set các IDs từ fixtures
    vars.course_id = test_course["course_id"]
    if test_course.get("modules"):
        vars.module_id = str(test_course["modules"][0].id)
    vars.enrollment_id = test_enrollment["enrollment_id"]
    
    return vars


@pytest.fixture(autouse=True)
def inject_test_vars(request, test_db):
    """
    TỰ ĐỘNG inject test_vars vào self cho test classes.
    Không cần khai báo gì cả!
    
    Sau khi có fixture này, mọi test class đều có self.test_vars
    """
    # Chỉ inject cho test classes (không phải functions)
    if request.instance is not None:
        # Đánh dấu rằng instance này cần test_vars
        request.instance._needs_test_vars = True


# Helper functions cho tests
def get_auth_headers(token: str) -> Dict[str, str]:
    """Tạo authorization headers với token."""
    return {"Authorization": f"Bearer {token}"}


def assert_response_schema(response_data: dict, required_fields: list):
    """Kiểm tra response có đủ các trường bắt buộc."""
    for field in required_fields:
        assert field in response_data, f"Missing required field: {field}"


async def get_real_token(client, test_users, user_key: str = "student1") -> str:
    """
    Login và lấy token thật từ backend.
    
    Args:
        client: AsyncClient fixture
        test_users: test_users fixture
        user_key: Key của user trong test_users dict (student1, instructor1, admin, etc.)
    
    Returns:
        str: Access token từ login response
    """
    from httpx import AsyncClient
    
    login_payload = {
        "email": test_users[user_key]["email"],
        "password": test_users[user_key]["password"],
        "remember_me": False
    }
    login_response = await client.post("/api/v1/auth/login", json=login_payload)
    assert login_response.status_code == 200, f"Login failed: {login_response.json()}"
    return login_response.json()["access_token"]
