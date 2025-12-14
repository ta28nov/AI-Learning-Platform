"""
TEST NHÓM 10: QUẢN LÝ QUIZ & BÀI TẬP CỦA GIẢNG VIÊN (3.3)
Tổng: 5 endpoints

Endpoints (theo CHUCNANG.md):
1. POST /api/v1/lessons/{lesson_id}/quizzes - Tạo quiz tùy chỉnh cho lesson
2. GET /api/v1/quizzes?role=instructor - Xem danh sách quiz của giảng viên
3. PUT /api/v1/quizzes/{quiz_id} - Chỉnh sửa quiz
4. DELETE /api/v1/quizzes/{quiz_id} - Xóa quiz
5. GET /api/v1/quizzes/{quiz_id}/class-results - Phân tích kết quả quiz của lớp

Sử dụng test_variables để quản lý quiz_id và tái sử dụng.
"""
import pytest
from httpx import AsyncClient
from datetime import datetime, timezone, timedelta
from tests.conftest import assert_response_schema
from tests.test_variables import TestVariables


class TestCreateQuiz:
    """Test cases cho tạo quiz tùy chỉnh."""
    
    @pytest.mark.asyncio
    async def test_create_quiz_success(self, client: AsyncClient, test_vars: TestVariables, test_course):
        """Test tạo quiz thành công cho lesson."""
        # Lấy lesson từ course
        from models.models import Lesson
        lesson = await Lesson.find_one({"course_id": test_vars.course_id})
        
        headers = test_vars.get_headers("instructor1")
        
        payload = {
            "title": "Python Basics Quiz",
            "description": "Quiz kiểm tra kiến thức Python cơ bản",
            "time_limit": 30,
            "pass_threshold": 70,
            "max_attempts": 3,
            "deadline": (datetime.now(timezone.utc) + timedelta(days=7)).isoformat(),
            "questions": [
                {
                    "question_text": "Python là ngôn ngữ lập trình gì?",
                    "type": "multiple_choice",
                    "options": ["Compiled", "Interpreted", "Assembly", "Machine"],
                    "correct_answer": "Interpreted",
                    "points": 10,
                    "is_mandatory": True
                }
            ]
        }
        
        response = await client.post(
            f"/api/v1/lessons/{lesson.id}/quizzes",
            headers=headers,
            json=payload
        )
        
        assert response.status_code == 201
        data = response.json()
        
        # Lưu quiz_id vào test_vars
        test_vars.quiz_id = data["id"]
        
        # Kiểm tra response schema
        required_fields = ["id", "lesson_id", "title", "description", "time_limit",
                          "pass_threshold", "max_attempts", "questions", "total_points",
                          "created_at"]
        assert_response_schema(data, required_fields)


class TestListInstructorQuizzes:
    """Test cases cho xem danh sách quiz của giảng viên."""
    
    @pytest.mark.asyncio
    async def test_list_instructor_quizzes_success(self, client: AsyncClient, test_vars: TestVariables, test_course):
        """Test xem danh sách quiz của instructor."""
        # Tạo một số quiz trước
        from models.models import Quiz, Lesson
        lesson = await Lesson.find_one({"course_id": test_vars.course_id})
        
        for i in range(3):
            quiz = Quiz(
                lesson_id=str(lesson.id),
                title=f"Quiz {i+1}",
                description=f"Description {i+1}",
                time_limit=30,
                pass_threshold=70,
                questions=[],
                created_by=test_vars.instructor1_user_id
            )
            await quiz.insert()
        
        headers = test_vars.get_headers("instructor1")
        
        response = await client.get("/api/v1/quizzes?role=instructor", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Kiểm tra response schema
        required_fields = ["quizzes", "total", "skip", "limit"]
        assert_response_schema(data, required_fields)
        
        # Phải có ít nhất 3 quizzes
        assert data["total"] >= 3


class TestUpdateQuiz:
    """Test cases cho chỉnh sửa quiz."""
    
    @pytest.mark.asyncio
    async def test_update_quiz_success(self, client: AsyncClient, test_vars: TestVariables, test_course):
        """Test cập nhật quiz thành công."""
        # Tạo quiz trước
        from models.models import Quiz, Lesson
        lesson = await Lesson.find_one({"course_id": test_vars.course_id})
        
        quiz = Quiz(
            lesson_id=str(lesson.id),
            title="Original Title",
            description="Original description",
            time_limit=30,
            pass_threshold=70,
            questions=[],
            created_by=test_vars.instructor1_user_id
        )
        await quiz.insert()
        
        headers = test_vars.get_headers("instructor1")
        
        # Cập nhật quiz
        update_payload = {
            "title": "Updated Quiz Title",
            "description": "Updated description",
            "time_limit": 45,
            "pass_threshold": 80
        }
        
        response = await client.put(
            f"/api/v1/quizzes/{quiz.id}",
            headers=headers,
            json=update_payload
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["title"] == "Updated Quiz Title"
        assert data["time_limit"] == 45
        assert data["pass_threshold"] == 80
    
    @pytest.mark.asyncio
    async def test_update_quiz_with_attempts_warning(self, client: AsyncClient, test_vars: TestVariables, test_course):
        """Test cập nhật quiz đã có học viên làm bài (cảnh báo)."""
        from models.models import Quiz, QuizAttempt, Lesson
        lesson = await Lesson.find_one({"course_id": test_vars.course_id})
        
        quiz = Quiz(
            lesson_id=str(lesson.id),
            title="Quiz with Attempts",
            time_limit=30,
            pass_threshold=70,
            questions=[],
            created_by=test_vars.instructor1_user_id
        )
        await quiz.insert()
        
        # Tạo attempt
        attempt = QuizAttempt(
            quiz_id=str(quiz.id),
            user_id=test_vars.student1_user_id,
            answers=[],
            score=80.0,
            status="Pass"
        )
        await attempt.insert()
        
        headers = test_vars.get_headers("instructor1")
        
        update_payload = {"title": "Updated Title"}
        
        response = await client.put(
            f"/api/v1/quizzes/{quiz.id}",
            headers=headers,
            json=update_payload
        )
        
        # Có thể trả về 200 với warning hoặc 400 tùy implementation
        assert response.status_code in [200, 400]
    
    @pytest.mark.asyncio
    async def test_update_quiz_not_owner(self, client: AsyncClient, test_vars: TestVariables, test_course):
        """Test cập nhật quiz của instructor khác."""
        from models.models import Quiz, Lesson
        lesson = await Lesson.find_one({"course_id": test_vars.course_id})
        
        quiz = Quiz(
            lesson_id=str(lesson.id),
            title="Instructor1 Quiz",
            time_limit=30,
            pass_threshold=70,
            questions=[],
            created_by=test_vars.instructor1_user_id
        )
        await quiz.insert()
        
        # Instructor2 cố gắng update
        headers = test_vars.get_headers("instructor2")
        
        update_payload = {"title": "Hacked Title"}
        
        response = await client.put(
            f"/api/v1/quizzes/{quiz.id}",
            headers=headers,
            json=update_payload
        )
        
        assert response.status_code == 403


class TestDeleteQuiz:
    """Test cases cho xóa quiz."""
    
    @pytest.mark.asyncio
    async def test_delete_quiz_success(self, client: AsyncClient, test_vars: TestVariables, test_course):
        """Test xóa quiz thành công khi chưa có attempts."""
        from models.models import Quiz, Lesson
        lesson = await Lesson.find_one({"course_id": test_vars.course_id})
        
        quiz = Quiz(
            lesson_id=str(lesson.id),
            title="Quiz to Delete",
            time_limit=30,
            pass_threshold=70,
            questions=[],
            created_by=test_vars.instructor1_user_id
        )
        await quiz.insert()
        
        headers = test_vars.get_headers("instructor1")
        
        response = await client.delete(f"/api/v1/quizzes/{quiz.id}", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
    
    @pytest.mark.asyncio
    async def test_delete_quiz_with_attempts(self, client: AsyncClient, test_vars: TestVariables, test_course):
        """Test xóa quiz đã có học viên làm bài (không được phép)."""
        from models.models import Quiz, QuizAttempt, Lesson
        lesson = await Lesson.find_one({"course_id": test_vars.course_id})
        
        quiz = Quiz(
            lesson_id=str(lesson.id),
            title="Quiz with Attempts",
            time_limit=30,
            pass_threshold=70,
            questions=[],
            created_by=test_vars.instructor1_user_id
        )
        await quiz.insert()
        
        # Tạo attempt
        attempt = QuizAttempt(
            quiz_id=str(quiz.id),
            user_id=test_vars.student1_user_id,
            answers=[],
            score=80.0,
            status="Pass"
        )
        await attempt.insert()
        
        headers = test_vars.get_headers("instructor1")
        
        response = await client.delete(f"/api/v1/quizzes/{quiz.id}", headers=headers)
        
        assert response.status_code == 400
        assert "attempts" in response.json()["detail"].lower()


class TestQuizClassResults:
    """Test cases cho phân tích kết quả quiz của lớp."""
    
    @pytest.mark.asyncio
    async def test_get_class_results_success(self, client: AsyncClient, test_vars: TestVariables, test_course):
        """Test xem kết quả quiz của lớp thành công."""
        from models.models import Quiz, QuizAttempt, Lesson
        lesson = await Lesson.find_one({"course_id": test_vars.course_id})
        
        # Tạo quiz
        quiz = Quiz(
            lesson_id=str(lesson.id),
            title="Class Quiz",
            time_limit=30,
            pass_threshold=70,
            questions=[],
            total_points=100,
            created_by=test_vars.instructor1_user_id
        )
        await quiz.insert()
        
        # Tạo một số attempts
        student_ids = [test_vars.student1_user_id, test_vars.student2_user_id]
        for i, student_id in enumerate(student_ids, 1):
            attempt = QuizAttempt(
                quiz_id=str(quiz.id),
                user_id=student_id,
                answers=[],
                score=60.0 + (i * 10),  # 70, 80
                status="Pass" if (60 + i*10) >= 70 else "Fail"
            )
            await attempt.insert()
        
        headers = test_vars.get_headers("instructor1")
        
        response = await client.get(
            f"/api/v1/quizzes/{quiz.id}/class-results",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Kiểm tra response schema
        required_fields = ["quiz_id", "quiz_title", "total_attempts", "avg_score",
                          "pass_rate", "score_distribution", "student_rankings"]
        assert_response_schema(data, required_fields)
        
        # Kiểm tra metrics
        assert data["total_attempts"] >= 2
        assert 0 <= data["pass_rate"] <= 100
    
    @pytest.mark.asyncio
    async def test_get_class_results_not_owner(self, client: AsyncClient, test_vars: TestVariables, test_course):
        """Test xem kết quả quiz của instructor khác."""
        from models.models import Quiz, Lesson
        lesson = await Lesson.find_one({"course_id": test_vars.course_id})
        
        quiz = Quiz(
            lesson_id=str(lesson.id),
            title="Instructor1 Quiz",
            time_limit=30,
            pass_threshold=70,
            questions=[],
            created_by=test_vars.instructor1_user_id
        )
        await quiz.insert()
        
        headers = test_vars.get_headers("instructor2")
        
        response = await client.get(
            f"/api/v1/quizzes/{quiz.id}/class-results",
            headers=headers
        )
        
        assert response.status_code == 403
