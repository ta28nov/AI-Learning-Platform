"""
Shared pytest fixtures: test env, HTTP client, DB cleanup, AI mocks, role users.
"""

import os
from typing import AsyncGenerator, Dict

import pytest
from httpx import ASGITransport, AsyncClient

# Set test environment before importing application modules
os.environ.setdefault("TESTING", "true")
os.environ.setdefault("MONGODB_DATABASE", "ai_learning_test")
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-ci-only-min-32-chars")
os.environ.setdefault("GOOGLE_API_KEY", "fake-key-not-used-in-tests")
os.environ.setdefault("ENVIRONMENT", "test")

from config.config import get_settings

get_settings.cache_clear()

from fastapi import FastAPI  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402

from app.database import init_database  # noqa: E402
from routers.routers import api_router  # noqa: E402


def _create_test_app() -> FastAPI:
    """FastAPI app without lifespan (DB init handled in fixtures)."""
    settings = get_settings()
    test_app = FastAPI(title=settings.app_name, version="0.1.0")
    test_app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    test_app.include_router(api_router, prefix="/api/v1")

    @test_app.get("/health", tags=["system"])
    async def health_check() -> dict[str, str]:
        return {"status": "ok"}

    return test_app


app = _create_test_app()  # noqa: E402
from models.models import (  # noqa: E402
    UserDocument,
    RefreshTokenDocument,
    PasswordResetTokenDocument,
    EmailVerificationTokenDocument,
    CourseDocument,
    ModuleDocument,
    LessonDocument,
    EnrollmentDocument,
    AssessmentDocument,
    QuizDocument,
    QuizAttemptDocument,
    ProgressDocument,
    ChatDocument,
    ClassDocument,
    RecommendationDocument,
)
from utils.security import hash_password  # noqa: E402
from tests.mocks import ai_responses  # noqa: E402

ALL_DOCUMENTS = [
    UserDocument,
    RefreshTokenDocument,
    PasswordResetTokenDocument,
    EmailVerificationTokenDocument,
    CourseDocument,
    ModuleDocument,
    LessonDocument,
    EnrollmentDocument,
    AssessmentDocument,
    QuizDocument,
    QuizAttemptDocument,
    ProgressDocument,
    ChatDocument,
    ClassDocument,
    RecommendationDocument,
]

@pytest.fixture(scope="session")
def test_settings():
    settings = get_settings()
    assert settings.testing is True
    assert settings.mongodb_database == "ai_learning_test"
    return settings


async def _clear_all_collections():
    for doc in ALL_DOCUMENTS:
        await doc.delete_all()


@pytest.fixture(autouse=True)
async def setup_database(test_settings):
    """Re-bind Motor/Beanie to the current event loop; clear collections each test."""
    from unittest.mock import AsyncMock, patch

    import app.database as db_module

    with patch.object(db_module, "close_database", new=AsyncMock()):
        if db_module._mongo_client is not None:
            db_module._mongo_client.close()
            db_module._mongo_client = None
        await init_database()
        await _clear_all_collections()
        yield
        await _clear_all_collections()


@pytest.fixture
def mock_ai():
    """Patch Gemini-backed functions for deterministic tests."""
    from unittest.mock import AsyncMock, patch

    patches = [
        patch(
            "services.assessment_service.generate_assessment_questions",
            new=AsyncMock(side_effect=ai_responses.mock_assessment_questions),
        ),
        patch(
            "services.assessment_service.evaluate_assessment_answers",
            new=AsyncMock(side_effect=ai_responses.mock_evaluate_assessment_answers),
        ),
        patch(
            "services.ai_service.generate_assessment_questions",
            new=AsyncMock(side_effect=ai_responses.mock_assessment_questions),
        ),
        patch(
            "services.ai_service.evaluate_assessment_answers",
            new=AsyncMock(side_effect=ai_responses.mock_evaluate_assessment_answers),
        ),
        patch(
            "services.ai_service.chat_with_course_context",
            new=AsyncMock(side_effect=ai_responses.mock_chat_response),
        ),
        patch(
            "services.ai_service.generate_course_recommendations",
            new=AsyncMock(side_effect=ai_responses.mock_course_recommendations),
        ),
        patch(
            "services.ai_service.generate_practice_exercises",
            new=AsyncMock(side_effect=ai_responses.mock_practice_exercises),
        ),
        patch(
            "services.ai_service.generate_course_from_prompt",
            new=AsyncMock(side_effect=ai_responses.mock_generate_course_from_prompt),
        ),
        patch(
            "services.ai_service.generate_module_quiz",
            new=AsyncMock(side_effect=ai_responses.mock_generate_module_quiz),
        ),
        patch(
            "services.recommendation_service._get_ai_recommendation_reasons",
            new=AsyncMock(side_effect=ai_responses.mock_ai_recommendation_reasons),
        ),
        patch(
            "services.personal_courses_service.generate_course_from_prompt",
            new=AsyncMock(side_effect=ai_responses.mock_generate_course_from_prompt),
        ),
    ]
    for p in patches:
        p.start()
    yield
    for p in patches:
        p.stop()


@pytest.fixture
async def client(mock_ai) -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test/api/v1") as ac:
        yield ac


@pytest.fixture
async def health_client() -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


async def _create_user(role: str, email: str, password: str = "TestPass1!") -> UserDocument:
    user = UserDocument(
        full_name="Test User Role",
        email=email,
        hashed_password=hash_password(password),
        role=role,
        status="active",
    )
    await user.insert()
    return user


@pytest.fixture
async def student_user() -> UserDocument:
    return await _create_user("student", "student-test@example.com")


@pytest.fixture
async def instructor_user() -> UserDocument:
    return await _create_user("instructor", "instructor-test@example.com")


@pytest.fixture
async def admin_user() -> UserDocument:
    return await _create_user("admin", "admin-test@example.com")


@pytest.fixture
async def student_auth(client: AsyncClient, student_user: UserDocument) -> Dict:
    from tests.helpers.auth import login_user, bearer

    res = await login_user(client, student_user.email)
    assert res.status_code == 200, res.text
    data = res.json()
    return {
        "user": data["user"],
        "access_token": data["access_token"],
        "refresh_token": data["refresh_token"],
        "headers": bearer(data["access_token"]),
    }


@pytest.fixture
async def instructor_auth(client: AsyncClient, instructor_user: UserDocument) -> Dict:
    from tests.helpers.auth import login_user, bearer

    res = await login_user(client, instructor_user.email)
    assert res.status_code == 200, res.text
    data = res.json()
    return {
        "user": data["user"],
        "access_token": data["access_token"],
        "headers": bearer(data["access_token"]),
    }


@pytest.fixture
async def admin_auth(client: AsyncClient, admin_user: UserDocument) -> Dict:
    from tests.helpers.auth import login_user, bearer

    res = await login_user(client, admin_user.email)
    assert res.status_code == 200, res.text
    data = res.json()
    return {
        "user": data["user"],
        "access_token": data["access_token"],
        "headers": bearer(data["access_token"]),
    }


@pytest.fixture
async def sample_quiz(student_user: UserDocument) -> QuizDocument:
    """Published quiz with one multiple-choice question."""
    import uuid

    course_id = str(uuid.uuid4())
    lesson_id = str(uuid.uuid4())
    qid = str(uuid.uuid4())
    quiz = QuizDocument(
        lesson_id=lesson_id,
        course_id=course_id,
        title="Integration Test Quiz",
        description="Quiz for pytest",
        time_limit_minutes=30,
        passing_score=70.0,
        max_attempts=3,
        is_draft=False,
        questions=[
            {
                "id": qid,
                "type": "multiple_choice",
                "question_text": "What is 2+2?",
                "options": ["3", "4", "5", "6"],
                "correct_answer": "4",
                "explanation": "Basic math",
                "points": 10,
                "is_mandatory": True,
                "order": 1,
            }
        ],
        question_count=1,
        total_points=10,
        mandatory_question_count=1,
        created_by=student_user.id,
    )
    await quiz.insert()

    enrollment = EnrollmentDocument(
        user_id=student_user.id,
        course_id=course_id,
        status="active",
    )
    await enrollment.insert()

    return quiz


@pytest.fixture
async def sample_course_with_enrollment(
    student_user: UserDocument,
) -> Dict:
    """Minimal course + enrollment for learning endpoint tests."""
    import uuid
    from datetime import datetime

    from models.models import EmbeddedLesson, EmbeddedModule

    course_id = str(uuid.uuid4())
    module_id = str(uuid.uuid4())
    lesson_id = str(uuid.uuid4())

    lesson = EmbeddedLesson(
        id=lesson_id,
        title="Intro Lesson",
        order=1,
        content="Hello world",
        duration_minutes=10,
        is_published=True,
    )
    module = EmbeddedModule(
        id=module_id,
        title="Module 1",
        description="First module",
        order=1,
        learning_outcomes=[
            {
                "id": str(uuid.uuid4()),
                "description": "Understand basics",
                "skill_tag": "python-basics",
                "is_mandatory": True,
            }
        ],
        lessons=[lesson],
        total_lessons=1,
        total_duration_minutes=10,
    )
    course = CourseDocument(
        id=course_id,
        title="Test Course",
        description="For integration tests",
        category="Programming",
        level="Beginner",
        status="published",
        owner_id=student_user.id,
        owner_type="admin",
        modules=[module],
        total_modules=1,
        total_lessons=1,
        total_duration_minutes=10,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    await course.insert()

    enrollment = EnrollmentDocument(
        user_id=student_user.id,
        course_id=course_id,
        status="active",
    )
    await enrollment.insert()

    lesson_doc = LessonDocument(
        id=lesson_id,
        module_id=module_id,
        course_id=course_id,
        title="Intro Lesson",
        order=1,
        content="Hello world",
        duration_minutes=10,
    )
    await lesson_doc.insert()

    return {
        "course_id": course_id,
        "module_id": module_id,
        "lesson_id": lesson_id,
        "course": course,
        "enrollment": enrollment,
        "lesson_doc": lesson_doc,
    }


@pytest.fixture
async def published_catalog_course(student_user: UserDocument) -> CourseDocument:
    """Published course without enrollment — for catalog/search/recommendations."""
    import uuid
    from datetime import datetime

    from models.models import EmbeddedLesson, EmbeddedModule

    course_id = str(uuid.uuid4())
    lesson = EmbeddedLesson(
        id=str(uuid.uuid4()),
        title="Catalog Lesson",
        order=1,
        content="Catalog content",
        duration_minutes=20,
        is_published=True,
    )
    module = EmbeddedModule(
        id=str(uuid.uuid4()),
        title="Catalog Module",
        description="Public module",
        order=1,
        lessons=[lesson],
        total_lessons=1,
        total_duration_minutes=20,
    )
    course = CourseDocument(
        id=course_id,
        title="Public Python Course",
        description="Published catalog course for discovery tests",
        category="Programming",
        level="Beginner",
        status="published",
        owner_id=student_user.id,
        owner_type="admin",
        course_type="public",
        modules=[module],
        total_modules=1,
        total_lessons=1,
        total_duration_minutes=20,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    await course.insert()
    return course


async def _submit_assessment_session(client: AsyncClient, headers: dict, session_id: str, questions: list):
    from datetime import datetime, timezone

    answers = [
        {
            "question_id": q["question_id"],
            "answer_content": "A",
            "selected_option": 0,
            "time_taken_seconds": 30,
        }
        for q in questions
    ]
    return await client.post(
        f"/assessments/{session_id}/submit",
        json={
            "answers": answers,
            "total_time_seconds": 300,
            "submitted_at": datetime.now(timezone.utc).isoformat(),
        },
        headers=headers,
    )


@pytest.fixture
async def evaluated_assessment_session(client: AsyncClient, student_auth: dict, mock_ai) -> dict:
    """Assessment session after generate + submit (evaluated)."""
    from tests.helpers.factories import assessment_generate_payload

    gen = await client.post(
        "/assessments/generate",
        json=assessment_generate_payload(),
        headers=student_auth["headers"],
    )
    assert gen.status_code == 201, gen.text
    data = gen.json()
    session_id = data["session_id"]
    submit = await _submit_assessment_session(
        client, student_auth["headers"], session_id, data["questions"]
    )
    assert submit.status_code == 200, submit.text
    return {"session_id": session_id, "generate": data, "submit": submit.json()}


@pytest.fixture
async def instructor_with_class(
    instructor_user: UserDocument,
    published_catalog_course: CourseDocument,
) -> dict:
    """Instructor + published course + one class."""
    from datetime import datetime, timedelta

    from models.models import Class

    now = datetime.utcnow()
    cls = Class(
        name="Test Class",
        description="Pytest class",
        course_id=published_catalog_course.id,
        instructor_id=instructor_user.id,
        invite_code="TESTCODE",
        max_students=30,
        start_date=now,
        end_date=now + timedelta(days=90),
        status="active",
        student_ids=[],
    )
    await cls.insert()
    return {
        "class": cls,
        "class_id": cls.id,
        "course_id": published_catalog_course.id,
        "invite_code": cls.invite_code,
    }
