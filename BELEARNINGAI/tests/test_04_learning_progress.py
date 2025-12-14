"""
TEST NHÓM 4: HỌC TẬP & THEO DÕI TIẾN ĐỘ (2.4)
Tổng: 13 endpoints

Endpoints:
1. GET /api/v1/courses/{course_id}/modules/{module_id} - Xem thông tin module
2. GET /api/v1/courses/{course_id}/lessons/{lesson_id} - Xem nội dung bài học
3. GET /api/v1/courses/{course_id}/modules - Lấy danh sách modules
4. GET /api/v1/courses/{course_id}/modules/{module_id}/outcomes - Kết quả học tập module
5. GET /api/v1/courses/{course_id}/modules/{module_id}/resources - Tài liệu module
6. POST /api/v1/courses/{course_id}/modules/{module_id}/assessments/generate - Sinh bài kiểm tra module
7. GET /api/v1/quizzes/{quiz_id} - Xem thông tin quiz
8. POST /api/v1/quizzes/{quiz_id}/attempt - Làm bài quiz
9. GET /api/v1/quizzes/{quiz_id}/results - Xem kết quả quiz
10. POST /api/v1/quizzes/{quiz_id}/retake - Làm lại quiz
11. POST /api/v1/ai/generate-practice - Nhận bài tập luyện tập
12. POST /api/v1/lessons/{lesson_id}/quizzes - Tạo quiz cho lesson
13. GET /api/v1/progress/course/{course_id} - Xem tiến độ khóa học

Sử dụng test_variables để lưu trữ và tái sử dụng IDs.
"""
import pytest
from httpx import AsyncClient
from tests.conftest import assert_response_schema
from tests.test_variables import TestVariables


class TestModuleDetail:
    """Test cases cho xem thông tin module."""
    
    @pytest.mark.asyncio
    async def test_get_module_detail_success(self, client: AsyncClient, test_vars, test_course, test_enrollment):
        """Test xem chi tiết module thành công."""
        headers = test_vars.get_headers("student1")
        
        course_id = test_vars.course_id
        module_id = str(test_course["modules"][0].id)
        
        response = await client.get(
            f"/api/v1/courses/{course_id}/modules/{module_id}",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        required_fields = ["id", "title", "description", "difficulty", "order",
                          "estimated_hours", "learning_outcomes", "lessons", "resources",
                          "completion_status", "completed_lessons_count", "total_lessons_count", 
                          "progress_percent", "prerequisites"]
        assert_response_schema(data, required_fields)
        
        # Kiểm tra lessons
        assert len(data["lessons"]) > 0
        lesson = data["lessons"][0]
        assert "id" in lesson
        assert "title" in lesson
        assert "is_completed" in lesson
    
    @pytest.mark.asyncio
    async def test_get_module_detail_not_enrolled(self, client: AsyncClient, test_vars, test_course):
        """Test xem module khi chưa đăng ký khóa học."""
        headers = test_vars.get_headers("student2")  # Chưa đăng ký
        
        course_id = test_vars.course_id
        module_id = str(test_course["modules"][0].id)
        
        response = await client.get(
            f"/api/v1/courses/{course_id}/modules/{module_id}",
            headers=headers
        )
        
        assert response.status_code == 403
    
    @pytest.mark.asyncio
    async def test_get_module_detail_not_found(self, client: AsyncClient, test_vars, test_course, test_enrollment):
        """Test xem module không tồn tại."""
        headers = test_vars.get_headers("student1")
        
        course_id = test_vars.course_id
        fake_module_id = "00000000-0000-0000-0000-000000000000"
        
        response = await client.get(
            f"/api/v1/courses/{course_id}/modules/{fake_module_id}",
            headers=headers
        )
        
        assert response.status_code == 404


class TestLessonContent:
    """Test cases cho xem nội dung bài học."""
    
    @pytest.mark.asyncio
    async def test_get_lesson_content_success(self, client: AsyncClient, test_vars, test_course, test_enrollment):
        """Test xem nội dung lesson thành công."""
        headers = test_vars.get_headers("student1")
        
        course_id = test_vars.course_id
        # Lấy lesson_id từ database
        from models.models import Lesson
        lesson = await Lesson.find_one({"course_id": course_id})
        lesson_id = str(lesson.id)
        
        response = await client.get(
            f"/api/v1/courses/{course_id}/lessons/{lesson_id}",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        required_fields = ["id", "module_id", "course_id", "title", "description", "order",
                          "duration_minutes", "content_type", "content", "resources",
                          "learning_objectives", "has_quiz", "completion_status", "navigation"]
        assert_response_schema(data, required_fields)
        
        # Kiểm tra content structure
        content = data["content"]
        assert "text_content" in content or "video_url" in content
        
        # Kiểm tra navigation
        navigation = data["navigation"]
        assert "previous_lesson" in navigation
        assert "next_lesson" in navigation
    
    @pytest.mark.asyncio
    async def test_get_lesson_content_not_enrolled(self, client: AsyncClient, test_vars, test_course):
        """Test xem lesson khi chưa đăng ký."""
        headers = test_vars.get_headers("student2")
        
        course_id = test_vars.course_id
        from models.models import Lesson
        lesson = await Lesson.find_one({"course_id": course_id})
        lesson_id = str(lesson.id)
        
        response = await client.get(
            f"/api/v1/courses/{course_id}/lessons/{lesson_id}",
            headers=headers
        )
        
        assert response.status_code == 403


class TestCourseModules:
    """Test cases cho lấy danh sách modules."""
    
    @pytest.mark.asyncio
    async def test_get_course_modules_success(self, client: AsyncClient, test_vars, test_course, test_enrollment):
        """Test lấy danh sách modules trong khóa học."""
        headers = test_vars.get_headers("student1")
        
        course_id = test_vars.course_id
        
        response = await client.get(
            f"/api/v1/courses/{course_id}/modules",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        required_fields = ["course_id", "course_title", "total_modules", "completed_modules",
                          "modules"]
        assert_response_schema(data, required_fields)
        
        # Kiểm tra modules
        assert len(data["modules"]) > 0
        module = data["modules"][0]
        module_fields = ["id", "title", "description", "order", "difficulty", "estimated_hours",
                        "total_lessons", "completed_lessons", "progress_percent", "is_accessible", "status"]
        assert_response_schema(module, module_fields)
    
    @pytest.mark.asyncio
    async def test_get_course_modules_not_enrolled(self, client: AsyncClient, test_vars, test_course):
        """Test lấy modules khi chưa đăng ký."""
        headers = test_vars.get_headers("student2")
        
        course_id = test_vars.course_id
        
        response = await client.get(
            f"/api/v1/courses/{course_id}/modules",
            headers=headers
        )
        
        assert response.status_code == 403


class TestModuleOutcomes:
    """Test cases cho kết quả học tập module."""
    
    @pytest.mark.asyncio
    async def test_get_module_outcomes(self, client: AsyncClient, test_vars, test_course, test_enrollment):
        """Test xem kết quả học tập module."""
        headers = test_vars.get_headers("student1")
        
        course_id = test_vars.course_id
        module_id = str(test_course["modules"][0].id)
        
        response = await client.get(
            f"/api/v1/courses/{course_id}/modules/{module_id}/outcomes",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        required_fields = ["module_id", "module_title", "completion_status", "overall_score",
                          "achieved_outcomes", "skills_acquired", "areas_for_improvement"]
        assert_response_schema(data, required_fields)


class TestModuleResources:
    """Test cases cho tài liệu module."""
    
    @pytest.mark.asyncio
    async def test_get_module_resources(self, client: AsyncClient, test_vars, test_course, test_enrollment):
        """Test lấy tài liệu học tập module."""
        headers = test_vars.get_headers("student1")
        
        course_id = test_vars.course_id
        module_id = str(test_course["modules"][0].id)
        
        response = await client.get(
            f"/api/v1/courses/{course_id}/modules/{module_id}/resources",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        required_fields = ["module_id", "module_title", "total_resources", "mandatory_resources",
                          "resources", "resource_categories"]
        assert_response_schema(data, required_fields)
        
        # Kiểm tra resource structure nếu có
        if len(data["resources"]) > 0:
            resource = data["resources"][0]
            resource_fields = ["id", "title", "type", "description", "url", "is_mandatory", "is_downloadable"]
            assert_response_schema(resource, resource_fields)


class TestModuleAssessment:
    """Test cases cho sinh bài kiểm tra module."""
    
    @pytest.mark.asyncio
    async def test_generate_module_assessment(self, client: AsyncClient, test_vars, test_course, test_enrollment):
        """Test sinh bài kiểm tra module."""
        headers = test_vars.get_headers("student1")
        
        course_id = test_vars.course_id
        module_id = str(test_course["modules"][0].id)
        
        payload = {
            "assessment_type": "review",
            "question_count": 10,
            "difficulty_preference": "mixed",
            "time_limit_minutes": 15
        }
        
        response = await client.post(
            f"/api/v1/courses/{course_id}/modules/{module_id}/assessments/generate",
            headers=headers,
            json=payload
        )
        
        assert response.status_code == 201
        data = response.json()
        
        required_fields = ["assessment_id", "module_id", "module_title", "assessment_type",
                          "question_count", "time_limit_minutes", "total_points", "pass_threshold",
                          "questions", "created_at", "expires_at"]
        assert_response_schema(data, required_fields)
        
        assert data["question_count"] == 10
        assert len(data["questions"]) == 10


class TestQuiz:
    """Test cases cho quiz."""
    
    @pytest.mark.asyncio
    async def test_get_quiz_info(self, client: AsyncClient, test_vars):
        """Test xem thông tin quiz trước khi làm."""
        headers = test_vars.get_headers("student1")
        
        # Tạo quiz trước
        from models.models import Quiz
        quiz = Quiz(
            title="Test Quiz",
            description="Quiz for testing",
            lesson_id="test-lesson-id",
            course_id=test_vars.course_id,
            created_by=test_vars.instructor1_user_id,
            time_limit_minutes=15,
            passing_score=70,
            questions=[]
        )
        await quiz.insert()
        
        response = await client.get(f"/api/v1/quizzes/{quiz.id}", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        required_fields = ["id", "title", "description", "question_count", "time_limit",
                          "pass_threshold", "mandatory_question_count", "user_attempts", "best_score"]
        assert_response_schema(data, required_fields)
    
    @pytest.mark.asyncio
    async def test_attempt_quiz(self, client: AsyncClient, test_vars):
        """Test làm bài quiz."""
        headers = test_vars.get_headers("student1")
        
        # Tạo quiz với câu hỏi
        from models.models import Quiz
        quiz = Quiz(
            title="Test Quiz",
            description="Quiz for testing",
            lesson_id="test-lesson-id",
            course_id=test_vars.course_id,
            created_by=test_vars.instructor1_user_id,
            time_limit_minutes=15,
            passing_score=70,
            questions=[
                {
                    "id": "q1",
                    "question_text": "Test question",
                    "type": "multiple_choice",
                    "options": ["A", "B", "C", "D"],
                    "correct_answer": "A",
                    "points": 10
                }
            ]
        )
        await quiz.insert()
        
        payload = {
            "answers": [
                {"question_id": "q1", "selected_option": "A"}
            ]
        }
        
        response = await client.post(
            f"/api/v1/quizzes/{quiz.id}/attempt",
            headers=headers,
            json=payload
        )
        
        assert response.status_code == 201
        data = response.json()
        
        required_fields = ["attempt_id", "quiz_id", "submitted_at", "message"]
        assert_response_schema(data, required_fields)
    
    @pytest.mark.asyncio
    async def test_get_quiz_results(self, client: AsyncClient, test_vars):
        """Test xem kết quả quiz."""
        headers = test_vars.get_headers("student1")
        
        # Tạo quiz và attempt
        from models.models import Quiz, QuizAttempt
        quiz = Quiz(
            title="Test Quiz",
            description="Quiz for testing",
            lesson_id="test-lesson-id",
            course_id=test_vars.course_id,
            created_by=test_vars.instructor1_user_id,
            time_limit_minutes=15,
            passing_score=70,
            questions=[{"id": "q1", "question_text": "Test", "type": "multiple_choice",
                       "options": ["A", "B"], "correct_answer": "A", "points": 10}]
        )
        await quiz.insert()
        
        attempt = QuizAttempt(
            quiz_id=str(quiz.id),
            user_id=test_vars.student1_user_id,  # Sử dụng test_vars
            answers=[{"question_id": "q1", "selected_answer": "A"}],
            score=100.0,
            status="Pass"
        )
        await attempt.insert()
        
        response = await client.get(f"/api/v1/quizzes/{quiz.id}/results", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        required_fields = ["attempt_id", "quiz_id", "total_score", "status", "pass_threshold",
                          "results", "mandatory_passed", "can_retake"]
        assert_response_schema(data, required_fields)
    
    @pytest.mark.asyncio
    async def test_retake_quiz(self, client: AsyncClient, test_vars):
        """Test làm lại quiz."""
        headers = test_vars.get_headers("student1")
        
        from models.models import Quiz
        quiz = Quiz(
            title="Test Quiz",
            description="Quiz for testing",
            lesson_id="test-lesson-id",
            course_id=test_vars.course_id,
            created_by=test_vars.instructor1_user_id,
            time_limit_minutes=15,
            passing_score=70,
            questions=[{"id": "q1", "question_text": "Test", "type": "multiple_choice",
                       "options": ["A", "B"], "correct_answer": "A", "points": 10}]
        )
        await quiz.insert()
        
        response = await client.post(f"/api/v1/quizzes/{quiz.id}/retake", headers=headers)
        
        assert response.status_code == 201
        data = response.json()
        
        required_fields = ["new_attempt_id", "quiz_id", "message", "questions"]
        assert_response_schema(data, required_fields)


class TestPracticeExercises:
    """Test cases cho bài tập luyện tập cá nhân hóa."""
    
    @pytest.mark.skip(reason="Practice exercises endpoint chưa được implement")
    async def test_generate_practice_from_lesson(self, client: AsyncClient, test_vars, test_course):
        """Test sinh bài tập từ lesson."""
        # Chức năng này sẽ được implement sau
        pass
    
    @pytest.mark.skip(reason="Practice exercises endpoint chưa được implement")
    async def test_generate_practice_from_topic(self, client: AsyncClient, test_vars):
        """Test sinh bài tập từ topic prompt."""
        # Chức năng này sẽ được implement sau
        pass
    
    @pytest.mark.skip(reason="Practice exercises endpoint chưa được implement")
    async def test_generate_practice_missing_params(self, client: AsyncClient, test_vars):
        """Test sinh bài tập thiếu parameters."""
        # Chức năng này sẽ được implement sau
        pass


class TestCourseProgress:
    """Test cases cho xem tiến độ khóa học."""
    
    @pytest.mark.asyncio
    async def test_get_course_progress(self, client: AsyncClient, test_vars, test_course, test_enrollment):
        """Test xem tiến độ học tập khóa học."""
        headers = test_vars.get_headers("student1")
        
        course_id = test_vars.course_id
        
        response = await client.get(f"/api/v1/progress/course/{course_id}", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Response schema sẽ phụ thuộc vào implementation cụ thể
        # Thường bao gồm: overall progress, module progress, lesson completion, quiz scores
        assert "progress_percent" in data or "overall_progress" in data
