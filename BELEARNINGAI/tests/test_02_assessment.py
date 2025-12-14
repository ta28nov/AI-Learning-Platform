"""
TEST NHÓM 2: ĐÁNH GIÁ NĂNG LỰC AI (2.2)
Tổng: 4 endpoints

Endpoints:
1. POST /api/v1/assessments/generate - Sinh bộ câu hỏi đánh giá
2. POST /api/v1/assessments/{session_id}/submit - Nộp bài đánh giá
3. GET /api/v1/assessments/{session_id}/results - Xem kết quả
4. GET /api/v1/recommendations/from-assessment - Nhận đề xuất lộ trình

Sử dụng test_variables để lưu trữ session_id, tokens và tái sử dụng.
"""
import pytest
from httpx import AsyncClient
from tests.conftest import get_auth_headers, assert_response_schema
from tests.test_variables import TestVariables


class TestAssessmentGeneration:
    """Test cases cho sinh bộ câu hỏi đánh giá."""
    
    @pytest.mark.asyncio
    async def test_generate_assessment_beginner(self, client: AsyncClient, test_vars: TestVariables):
        """Test sinh assessment level Beginner."""
        headers = test_vars.get_headers("student1")
        
        payload = {
            "category": "Programming",
            "subject": "Python",
            "level": "Beginner",
            "focus_areas": ["syntax", "variables"]
        }
        
        response = await client.post("/api/v1/assessments/generate", headers=headers, json=payload)
        
        assert response.status_code == 201
        data = response.json()
        
        # Lưu session_id vào test_vars để dùng lại
        test_vars.assessment_session_id = data["session_id"]
        
        # Kiểm tra response schema
        required_fields = ["session_id", "category", "subject", "level", "question_count", 
                          "time_limit_minutes", "questions", "created_at", "expires_at"]
        assert_response_schema(data, required_fields)
        
        # Kiểm tra số lượng câu hỏi theo level Beginner (15 câu)
        assert data["question_count"] == 15
        assert len(data["questions"]) == 15
        assert data["time_limit_minutes"] == 15
        
        # Kiểm tra cấu trúc câu hỏi
        first_question = data["questions"][0]
        question_fields = ["question_id", "question_text", "question_type", "difficulty", 
                          "skill_tag", "points", "options"]
        assert_response_schema(first_question, question_fields)
    
    @pytest.mark.asyncio
    async def test_generate_assessment_intermediate(self, client: AsyncClient, test_vars: TestVariables):
        """Test sinh assessment level Intermediate."""
        headers = test_vars.get_headers("student1")
        
        payload = {
            "category": "Programming",
            "subject": "Python",
            "level": "Intermediate"
        }
        
        response = await client.post("/api/v1/assessments/generate", headers=headers, json=payload)
        
        assert response.status_code == 201
        data = response.json()
        
        # Intermediate: 25 câu, 22 phút
        assert data["question_count"] == 25
        assert data["time_limit_minutes"] == 22
    
    @pytest.mark.asyncio
    async def test_generate_assessment_advanced(self, client: AsyncClient, test_vars: TestVariables):
        """Test sinh assessment level Advanced."""
        headers = test_vars.get_headers("student1")
        
        payload = {
            "category": "Programming",
            "subject": "Python",
            "level": "Advanced"
        }
        
        response = await client.post("/api/v1/assessments/generate", headers=headers, json=payload)
        
        assert response.status_code == 201
        data = response.json()
        
        # Advanced: 35 câu, 30 phút
        assert data["question_count"] == 35
        assert data["time_limit_minutes"] == 30
    
    @pytest.mark.asyncio
    async def test_generate_assessment_invalid_category(self, client: AsyncClient, test_vars: TestVariables):
        """Test sinh assessment với category không chuẩn - Backend vẫn chấp nhận."""
        headers = test_vars.get_headers("student1")
        
        payload = {
            "category": "InvalidCategory",
            "subject": "Python",
            "level": "Beginner"
        }
        
        response = await client.post("/api/v1/assessments/generate", headers=headers, json=payload)
        
        # Backend hiện tại chấp nhận bất kỳ category nào và tạo assessment
        assert response.status_code == 201
        data = response.json()
        
        # Vẫn tạo được assessment với category không chuẩn
        assert data["category"] == "InvalidCategory"
        assert data["question_count"] == 15  # Default cho Beginner
    
    @pytest.mark.asyncio
    async def test_generate_assessment_without_auth(self, client: AsyncClient):
        """Test sinh assessment không có token."""
        payload = {
            "category": "Programming",
            "subject": "Python",
            "level": "Beginner"
        }
        
        response = await client.post("/api/v1/assessments/generate", json=payload)
        
        # Backend trả về 403 khi không có token
        assert response.status_code == 403


class TestAssessmentSubmission:
    """Test cases cho nộp bài đánh giá."""
    
    @pytest.mark.asyncio
    async def test_submit_assessment_success(self, client: AsyncClient, test_vars: TestVariables):
        """Test nộp bài assessment thành công."""
        headers = test_vars.get_headers("student1")
        
        # Bước 1: Tạo assessment
        gen_payload = {
            "category": "Programming",
            "subject": "Python",
            "level": "Beginner"
        }
        gen_response = await client.post("/api/v1/assessments/generate", headers=headers, json=gen_payload)
        session_id = gen_response.json()["session_id"]
        questions = gen_response.json()["questions"]
        
        # Lưu session_id vào test_vars
        test_vars.assessment_session_id = session_id
        
        # Bước 2: Nộp bài
        answers = [
            {
                "question_id": q["question_id"],
                "answer_content": "Test answer",
                "selected_option": 0,
                "time_taken_seconds": 30
            }
            for q in questions
        ]
        
        submit_payload = {
            "answers": answers,
            "total_time_seconds": 450,
            "submitted_at": "2024-01-01T10:00:00Z"
        }
        
        response = await client.post(
            f"/api/v1/assessments/{session_id}/submit",
            headers=headers,
            json=submit_payload
        )
        
        assert response.status_code == 200
        data = response.json()
        
        required_fields = ["session_id", "submitted_at", "total_questions", 
                          "time_taken_minutes", "status", "message"]
        assert_response_schema(data, required_fields)
        assert data["status"] == "submitted"
    
    @pytest.mark.asyncio
    async def test_submit_assessment_invalid_session(self, client: AsyncClient, test_vars: TestVariables):
        """Test nộp bài với session_id không tồn tại."""
        headers = test_vars.get_headers("student1")
        
        fake_session_id = "00000000-0000-0000-0000-000000000000"
        payload = {
            "answers": [],
            "total_time_seconds": 100,
            "submitted_at": "2024-01-01T10:00:00Z"
        }
        
        response = await client.post(
            f"/api/v1/assessments/{fake_session_id}/submit",
            headers=headers,
            json=payload
        )
        
        # Backend trả về 422 (Unprocessable Entity) cho UUID không tồn tại
        assert response.status_code == 422


class TestAssessmentResults:
    """Test cases cho xem kết quả đánh giá."""
    
    @pytest.mark.asyncio
    async def test_get_results_success(self, client: AsyncClient, test_vars: TestVariables):
        """Test xem kết quả assessment."""
        headers = test_vars.get_headers("student1")
        
        # Tạo và nộp assessment trước
        gen_payload = {
            "category": "Programming",
            "subject": "Python",
            "level": "Beginner"
        }
        gen_response = await client.post("/api/v1/assessments/generate", headers=headers, json=gen_payload)
        session_id = gen_response.json()["session_id"]
        questions = gen_response.json()["questions"]
        
        # Lưu session_id vào test_vars
        test_vars.assessment_session_id = session_id
        
        # Nộp bài
        answers = [
            {"question_id": q["question_id"], "answer_content": "answer", "selected_option": 0, "time_taken_seconds": 30}
            for q in questions
        ]
        await client.post(
            f"/api/v1/assessments/{session_id}/submit",
            headers=headers,
            json={"answers": answers, "total_time_seconds": 450, "submitted_at": "2024-01-01T10:00:00Z"}
        )
        
        # Xem kết quả
        response = await client.get(f"/api/v1/assessments/{session_id}/results", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        required_fields = ["session_id", "assessment_info", "overall_score", "proficiency_level",
                          "total_questions", "correct_answers", "score_breakdown", "skill_analysis",
                          "knowledge_gaps", "time_analysis", "ai_feedback"]
        assert_response_schema(data, required_fields)
        
        # Kiểm tra điểm số
        assert 0 <= data["overall_score"] <= 100
        assert data["proficiency_level"] in ["Beginner", "Intermediate", "Advanced"]
    
    @pytest.mark.asyncio
    async def test_get_results_not_submitted(self, client: AsyncClient, test_vars: TestVariables):
        """Test xem kết quả khi chưa nộp bài."""
        headers = test_vars.get_headers("student1")
        
        # Chỉ tạo assessment, không nộp
        gen_payload = {"category": "Programming", "subject": "Python", "level": "Beginner"}
        gen_response = await client.post("/api/v1/assessments/generate", headers=headers, json=gen_payload)
        session_id = gen_response.json()["session_id"]
        
        response = await client.get(f"/api/v1/assessments/{session_id}/results", headers=headers)
        
        assert response.status_code == 404


class TestRecommendations:
    """Test cases cho đề xuất lộ trình học tập."""
    
    @pytest.mark.asyncio
    async def test_get_recommendations_success(self, client: AsyncClient, test_vars: TestVariables):
        """Test nhận đề xuất lộ trình từ assessment."""
        headers = test_vars.get_headers("student1")
        
        # Tạo, nộp assessment
        gen_payload = {"category": "Programming", "subject": "Python", "level": "Beginner"}
        gen_response = await client.post("/api/v1/assessments/generate", headers=headers, json=gen_payload)
        session_id = gen_response.json()["session_id"]
        questions = gen_response.json()["questions"]
        
        # Lưu session_id vào test_vars
        test_vars.assessment_session_id = session_id
        
        answers = [
            {"question_id": q["question_id"], "answer_content": "answer", "selected_option": 0, "time_taken_seconds": 30}
            for q in questions
        ]
        await client.post(
            f"/api/v1/assessments/{session_id}/submit",
            headers=headers,
            json={"answers": answers, "total_time_seconds": 450, "submitted_at": "2024-01-01T10:00:00Z"}
        )
        
        # Lấy recommendations
        response = await client.get(
            f"/api/v1/recommendations/from-assessment?session_id={session_id}",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        required_fields = ["assessment_session_id", "user_proficiency_level", "recommended_courses",
                          "suggested_learning_order", "practice_exercises", "total_estimated_hours",
                          "ai_personalized_advice"]
        assert_response_schema(data, required_fields)
        
        # Kiểm tra recommended courses
        if len(data["recommended_courses"]) > 0:
            course = data["recommended_courses"][0]
            course_fields = ["course_id", "title", "priority_rank", "relevance_score", "reason"]
            assert_response_schema(course, course_fields)
