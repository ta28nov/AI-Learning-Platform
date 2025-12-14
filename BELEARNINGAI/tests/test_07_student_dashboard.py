"""
TEST NHÓM 7: DASHBOARD & PHÂN TÍCH HỌC VIÊN (2.7)
Tổng: 4 endpoints

Endpoints:
1. GET /api/v1/dashboard/student - Dashboard tổng quan học viên
2. GET /api/v1/analytics/learning-stats - Thống kê học tập chi tiết
3. GET /api/v1/analytics/progress-chart - Biểu đồ tiến độ theo thời gian
4. GET /api/v1/recommendations - Đề xuất khóa học thông minh bằng AI

Sử dụng test_variables để lưu trữ và tái sử dụng IDs.
"""
import pytest
from httpx import AsyncClient
from tests.conftest import assert_response_schema
from tests.test_variables import TestVariables


class TestStudentDashboard:
    """Test cases cho dashboard tổng quan học viên."""
    
    @pytest.mark.asyncio
    async def test_get_student_dashboard_success(self, client: AsyncClient, test_vars, test_enrollment):
        """Test xem dashboard học viên thành công."""
        headers = test_vars.get_headers("student1")
        
        response = await client.get("/api/v1/dashboard/student", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Kiểm tra response schema
        required_fields = ["ongoing_courses", "quizzes_pending", "lessons_completed",
                          "total_lessons", "avg_quiz_score", "recent_activity"]
        assert_response_schema(data, required_fields)
        
        # Kiểm tra ongoing_courses structure
        if len(data["ongoing_courses"]) > 0:
            course = data["ongoing_courses"][0]
            course_fields = ["course_id", "title", "progress_percent", "last_accessed_at"]
            assert_response_schema(course, course_fields)
        
        # Kiểm tra quizzes_pending structure
        if len(data["quizzes_pending"]) > 0:
            quiz = data["quizzes_pending"][0]
            quiz_fields = ["quiz_id", "title", "lesson_title", "deadline"]
            assert_response_schema(quiz, quiz_fields)
    
    @pytest.mark.asyncio
    async def test_get_student_dashboard_with_multiple_enrollments(self, client: AsyncClient, test_vars: TestVariables, test_course):
        """Test dashboard với nhiều khóa học đang học."""
        headers = test_vars.get_headers("student1")
        
        # Đăng ký thêm khóa học
        from models.models import Enrollment
        enrollment = Enrollment(
            user_id=test_vars.student1_user_id,
            course_id=test_vars.course_id,
            status="active",
            progress_percent=50.0
        )
        await enrollment.insert()
        
        response = await client.get("/api/v1/dashboard/student", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Phải hiển thị khóa học đang học
        assert len(data["ongoing_courses"]) > 0
    
    @pytest.mark.asyncio
    async def test_get_student_dashboard_new_user(self, client: AsyncClient, test_vars: TestVariables):
        """Test dashboard cho user mới chưa có dữ liệu."""
        headers = test_vars.get_headers("student3")  # User mới
        
        response = await client.get("/api/v1/dashboard/student", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Dashboard rỗng nhưng vẫn trả về structure
        assert data["lessons_completed"] == 0
        assert data["total_lessons"] == 0
        assert len(data["ongoing_courses"]) == 0
    
    @pytest.mark.asyncio
    async def test_get_student_dashboard_without_auth(self, client: AsyncClient):
        """Test xem dashboard không có token."""
        response = await client.get("/api/v1/dashboard/student")
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_get_student_dashboard_wrong_role(self, client: AsyncClient, test_vars):
        """Test instructor cố gắng xem student dashboard."""
        headers = test_vars.get_headers("instructor1")
        
        response = await client.get("/api/v1/dashboard/student", headers=headers)
        
        # Có thể trả về 403 hoặc empty data tùy implementation
        assert response.status_code in [200, 403]


class TestLearningStats:
    """Test cases cho thống kê học tập chi tiết."""
    
    @pytest.mark.asyncio
    async def test_get_learning_stats_success(self, client: AsyncClient, test_vars, test_enrollment):
        """Test xem thống kê học tập thành công."""
        headers = test_vars.get_headers("student1")
        
        response = await client.get("/api/v1/analytics/learning-stats", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Kiểm tra response schema
        required_fields = ["total_courses_enrolled", "courses_completed", "courses_in_progress",
                          "total_lessons_completed", "total_quizzes_passed", "avg_quiz_score",
                          "total_study_time_minutes", "streak_days"]
        assert_response_schema(data, required_fields)
        
        # Kiểm tra giá trị hợp lệ
        assert data["total_courses_enrolled"] >= 0
        assert data["courses_completed"] >= 0
        assert data["courses_in_progress"] >= 0
        assert 0 <= data["avg_quiz_score"] <= 100
        assert data["total_study_time_minutes"] >= 0
        assert data["streak_days"] >= 0
    
    @pytest.mark.asyncio
    async def test_get_learning_stats_with_breakdown(self, client: AsyncClient, test_vars, test_enrollment):
        """Test thống kê với breakdown chi tiết."""
        headers = test_vars.get_headers("student1")
        
        response = await client.get("/api/v1/analytics/learning-stats?include_breakdown=true", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Phải có breakdown theo category
        if "category_breakdown" in data:
            assert isinstance(data["category_breakdown"], list)
            if len(data["category_breakdown"]) > 0:
                category = data["category_breakdown"][0]
                assert "category" in category
                assert "courses_count" in category
    
    @pytest.mark.asyncio
    async def test_get_learning_stats_filter_by_timerange(self, client: AsyncClient, test_vars):
        """Test thống kê theo khoảng thời gian."""
        headers = test_vars.get_headers("student1")
        
        response = await client.get(
            "/api/v1/analytics/learning-stats?start_date=2024-01-01&end_date=2024-12-31",
            headers=headers
        )
        
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_get_learning_stats_new_user(self, client: AsyncClient, test_vars):
        """Test thống kê cho user mới."""
        headers = test_vars.get_headers("student3")
        
        response = await client.get("/api/v1/analytics/learning-stats", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Tất cả metrics phải = 0
        assert data["total_courses_enrolled"] == 0
        assert data["courses_completed"] == 0
        assert data["total_lessons_completed"] == 0


class TestProgressChart:
    """Test cases cho biểu đồ tiến độ theo thời gian."""
    
    @pytest.mark.asyncio
    async def test_get_progress_chart_success(self, client: AsyncClient, test_vars, test_enrollment):
        """Test xem biểu đồ tiến độ thành công."""
        headers = test_vars.get_headers("student1")
        
        response = await client.get("/api/v1/analytics/progress-chart", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Kiểm tra response schema
        required_fields = ["chart_type", "time_period", "data_points"]
        assert_response_schema(data, required_fields)
        
        # Kiểm tra data_points structure
        assert isinstance(data["data_points"], list)
        if len(data["data_points"]) > 0:
            point = data["data_points"][0]
            point_fields = ["date", "value", "metric"]
            assert_response_schema(point, point_fields)
    
    @pytest.mark.asyncio
    async def test_get_progress_chart_by_day(self, client: AsyncClient, test_vars):
        """Test biểu đồ theo ngày."""
        headers = test_vars.get_headers("student1")
        
        response = await client.get(
            "/api/v1/analytics/progress-chart?period=daily&days=7",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["time_period"] == "daily"
        # Phải có tối đa 7 data points
        assert len(data["data_points"]) <= 7
    
    @pytest.mark.asyncio
    async def test_get_progress_chart_by_week(self, client: AsyncClient, test_vars):
        """Test biểu đồ theo tuần."""
        headers = test_vars.get_headers("student1")
        
        response = await client.get(
            "/api/v1/analytics/progress-chart?period=weekly&weeks=4",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["time_period"] == "weekly"
        assert len(data["data_points"]) <= 4
    
    @pytest.mark.asyncio
    async def test_get_progress_chart_by_month(self, client: AsyncClient, test_vars):
        """Test biểu đồ theo tháng."""
        headers = test_vars.get_headers("student1")
        
        response = await client.get(
            "/api/v1/analytics/progress-chart?period=monthly&months=6",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["time_period"] == "monthly"
        assert len(data["data_points"]) <= 6
    
    @pytest.mark.asyncio
    async def test_get_progress_chart_filter_by_course(self, client: AsyncClient, test_vars, test_course):
        """Test biểu đồ cho khóa học cụ thể."""
        headers = test_vars.get_headers("student1")
        course_id = test_vars.course_id
        
        response = await client.get(
            f"/api/v1/analytics/progress-chart?course_id={course_id}",
            headers=headers
        )
        
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_get_progress_chart_invalid_period(self, client: AsyncClient, test_vars):
        """Test biểu đồ với period không hợp lệ."""
        headers = test_vars.get_headers("student1")
        
        response = await client.get(
            "/api/v1/analytics/progress-chart?period=invalid",
            headers=headers
        )
        
        assert response.status_code == 400


class TestRecommendations:
    """Test cases cho đề xuất khóa học thông minh."""
    
    @pytest.mark.asyncio
    async def test_get_recommendations_success(self, client: AsyncClient, test_vars, test_enrollment):
        """Test nhận đề xuất khóa học thành công."""
        headers = test_vars.get_headers("student1")
        
        response = await client.get("/api/v1/recommendations", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Kiểm tra response schema
        required_fields = ["recommended_courses", "recommendation_basis", "total_recommendations"]
        assert_response_schema(data, required_fields)
        
        # Kiểm tra recommended_courses structure
        assert isinstance(data["recommended_courses"], list)
        if len(data["recommended_courses"]) > 0:
            course = data["recommended_courses"][0]
            course_fields = ["course_id", "title", "description", "category", "level",
                            "relevance_score", "reason", "priority_rank"]
            assert_response_schema(course, course_fields)
            
            # Kiểm tra relevance_score
            assert 0 <= course["relevance_score"] <= 100
    
    @pytest.mark.asyncio
    async def test_get_recommendations_based_on_history(self, client: AsyncClient, test_vars, test_enrollment):
        """Test đề xuất dựa trên lịch sử học tập."""
        headers = test_vars.get_headers("student1")
        
        response = await client.get("/api/v1/recommendations?basis=learning_history", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["recommendation_basis"] == "learning_history"
    
    @pytest.mark.asyncio
    async def test_get_recommendations_based_on_preferences(self, client: AsyncClient, test_vars):
        """Test đề xuất dựa trên sở thích."""
        headers = test_vars.get_headers("student1")
        
        response = await client.get("/api/v1/recommendations?basis=preferences", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["recommendation_basis"] == "preferences"
    
    @pytest.mark.asyncio
    async def test_get_recommendations_based_on_skill_gaps(self, client: AsyncClient, test_vars):
        """Test đề xuất dựa trên lỗ hổng kiến thức."""
        headers = test_vars.get_headers("student1")
        
        response = await client.get("/api/v1/recommendations?basis=skill_gaps", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["recommendation_basis"] == "skill_gaps"
    
    @pytest.mark.asyncio
    async def test_get_recommendations_limit(self, client: AsyncClient, test_vars):
        """Test giới hạn số lượng đề xuất."""
        headers = test_vars.get_headers("student1")
        
        response = await client.get("/api/v1/recommendations?limit=5", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Số lượng đề xuất không vượt quá limit
        assert len(data["recommended_courses"]) <= 5
    
    @pytest.mark.asyncio
    async def test_get_recommendations_filter_by_category(self, client: AsyncClient, test_vars):
        """Test đề xuất lọc theo category."""
        headers = test_vars.get_headers("student1")
        
        response = await client.get("/api/v1/recommendations?category=Programming", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Tất cả courses đề xuất phải thuộc category Programming
        for course in data["recommended_courses"]:
            assert course["category"] == "Programming"
    
    @pytest.mark.asyncio
    async def test_get_recommendations_filter_by_level(self, client: AsyncClient, test_vars):
        """Test đề xuất lọc theo level."""
        headers = test_vars.get_headers("student1")
        
        response = await client.get("/api/v1/recommendations?level=Beginner", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Tất cả courses đề xuất phải là Beginner level
        for course in data["recommended_courses"]:
            assert course["level"] == "Beginner"
    
    @pytest.mark.asyncio
    async def test_get_recommendations_new_user(self, client: AsyncClient, test_vars):
        """Test đề xuất cho user mới chưa có dữ liệu."""
        headers = test_vars.get_headers("student3")
        
        response = await client.get("/api/v1/recommendations", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Vẫn có đề xuất (based on popular courses hoặc default)
        assert len(data["recommended_courses"]) > 0
    
    @pytest.mark.asyncio
    async def test_get_recommendations_without_auth(self, client: AsyncClient):
        """Test nhận đề xuất không có token."""
        response = await client.get("/api/v1/recommendations")
        
        assert response.status_code == 401
