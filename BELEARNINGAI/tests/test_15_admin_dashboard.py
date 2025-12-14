"""
TEST NHÓM 15: DASHBOARD QUẢN TRỊ (4.4)
Tổng: 4 endpoints

Endpoints (theo CHUCNANG.md):
1. GET /api/v1/admin/dashboard - Dashboard tổng quan hệ thống
2. GET /api/v1/admin/analytics/users-growth - Thống kê tăng trưởng người dùng
3. GET /api/v1/admin/analytics/courses - Phân tích khóa học
4. GET /api/v1/admin/analytics/system-health - Giám sát sức khỏe hệ thống
"""
import pytest
from httpx import AsyncClient
from tests.conftest import get_auth_headers, assert_response_schema


class TestAdminDashboard:
    """Test cases cho dashboard tổng quan hệ thống."""
    
    @pytest.mark.asyncio
    async def test_get_admin_dashboard_success(self, client: AsyncClient, test_vars):
        """Test xem dashboard tổng quan."""
        headers = test_vars.get_headers("admin")
        
        response = await client.get("/api/v1/admin/dashboard", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Kiểm tra response schema theo CHUCNANG.md
        required_fields = ["total_users", "user_breakdown", "total_courses",
                          "course_breakdown", "total_classes", "class_breakdown",
                          "activity_stats"]
        assert_response_schema(data, required_fields)
        
        # Kiểm tra user_breakdown
        user_breakdown = data["user_breakdown"]
        assert "students" in user_breakdown
        assert "instructors" in user_breakdown
        assert "admins" in user_breakdown
        
        # Kiểm tra course_breakdown
        course_breakdown = data["course_breakdown"]
        assert "public" in course_breakdown
        assert "personal" in course_breakdown
        assert "published" in course_breakdown
        assert "draft" in course_breakdown
        
        # Kiểm tra class_breakdown
        class_breakdown = data["class_breakdown"]
        assert "active" in class_breakdown
        assert "completed" in class_breakdown
        
        # Kiểm tra activity_stats
        activity = data["activity_stats"]
        assert "new_enrollments_this_week" in activity
        assert "quizzes_completed_today" in activity
    
    @pytest.mark.asyncio
    async def test_get_admin_dashboard_non_admin(self, client: AsyncClient, test_vars):
        """Test non-admin không thể xem admin dashboard."""
        headers = test_vars.get_headers("instructor1")
        
        response = await client.get("/api/v1/admin/dashboard", headers=headers)
        
        assert response.status_code == 403


class TestAdminUsersGrowth:
    """Test cases cho thống kê tăng trưởng người dùng."""
    
    @pytest.mark.asyncio
    async def test_get_users_growth_success(self, client: AsyncClient, test_vars):
        """Test xem thống kê tăng trưởng người dùng."""
        headers = test_vars.get_headers("admin")
        
        response = await client.get("/api/v1/admin/analytics/users-growth", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Kiểm tra response schema theo CHUCNANG.md
        required_fields = ["chart_data", "role_breakdown", "retention_rate", "active_users"]
        assert_response_schema(data, required_fields)
        
        # Kiểm tra chart_data
        assert isinstance(data["chart_data"], list)
        if len(data["chart_data"]) > 0:
            point = data["chart_data"][0]
            assert "date" in point
            assert "new_users" in point
        
        # Kiểm tra role_breakdown
        role_breakdown = data["role_breakdown"]
        assert "student_growth" in role_breakdown
        assert "instructor_growth" in role_breakdown
        
        # Kiểm tra active_users
        active_users = data["active_users"]
        assert "last_7_days" in active_users
        assert "last_30_days" in active_users
    
    @pytest.mark.asyncio
    async def test_get_users_growth_filter_by_time(self, client: AsyncClient, test_vars):
        """Test lọc theo khoảng thời gian."""
        headers = test_vars.get_headers("admin")
        
        response = await client.get(
            "/api/v1/admin/analytics/users-growth?period=monthly&months=6",
            headers=headers
        )
        
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_get_users_growth_filter_by_role(self, client: AsyncClient, test_vars):
        """Test lọc theo vai trò."""
        headers = test_vars.get_headers("admin")
        
        response = await client.get(
            "/api/v1/admin/analytics/users-growth?role=student",
            headers=headers
        )
        
        assert response.status_code == 200


class TestAdminCoursesAnalytics:
    """Test cases cho phân tích khóa học."""
    
    @pytest.mark.asyncio
    async def test_get_courses_analytics_success(self, client: AsyncClient, test_vars):
        """Test xem phân tích khóa học."""
        headers = test_vars.get_headers("admin")
        
        response = await client.get("/api/v1/admin/analytics/courses", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Kiểm tra response schema theo CHUCNANG.md
        required_fields = ["top_courses", "completion_rates", "avg_quiz_scores",
                          "course_creation_trend"]
        assert_response_schema(data, required_fields)
        
        # Kiểm tra top_courses
        assert isinstance(data["top_courses"], list)
        if len(data["top_courses"]) > 0:
            course = data["top_courses"][0]
            assert "course_id" in course
            assert "title" in course
            assert "enrollment_count" in course
        
        # Kiểm tra completion_rates
        assert isinstance(data["completion_rates"], list)
        
        # Kiểm tra avg_quiz_scores
        assert isinstance(data["avg_quiz_scores"], (int, float, dict))
        
        # Kiểm tra course_creation_trend
        assert isinstance(data["course_creation_trend"], list)
    
    @pytest.mark.asyncio
    async def test_get_courses_analytics_filter_by_category(self, client: AsyncClient, test_vars):
        """Test lọc theo category."""
        headers = test_vars.get_headers("admin")
        
        response = await client.get(
            "/api/v1/admin/analytics/courses?category=Programming",
            headers=headers
        )
        
        assert response.status_code == 200


class TestAdminSystemHealth:
    """Test cases cho giám sát sức khỏe hệ thống."""
    
    @pytest.mark.asyncio
    async def test_get_system_health_success(self, client: AsyncClient, test_vars):
        """Test xem sức khỏe hệ thống."""
        headers = test_vars.get_headers("admin")
        
        response = await client.get("/api/v1/admin/analytics/system-health", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Kiểm tra response schema theo CHUCNANG.md
        required_fields = ["api_performance", "error_rate", "database_performance",
                          "storage_usage", "active_sessions"]
        assert_response_schema(data, required_fields)
        
        # Kiểm tra api_performance
        api_perf = data["api_performance"]
        assert "avg_response_time_ms" in api_perf
        assert "requests_per_minute" in api_perf
        
        # Kiểm tra error_rate
        error_rate = data["error_rate"]
        assert "total_errors" in error_rate
        assert "error_percentage" in error_rate
        
        # Kiểm tra database_performance
        db_perf = data["database_performance"]
        assert "avg_query_time_ms" in db_perf
        assert "connection_pool_usage" in db_perf
        
        # Kiểm tra storage_usage
        storage = data["storage_usage"]
        assert "used_gb" in storage
        assert "total_gb" in storage
        assert "usage_percentage" in storage
        
        # Kiểm tra active_sessions
        assert isinstance(data["active_sessions"], int)
        assert data["active_sessions"] >= 0
    
    @pytest.mark.asyncio
    async def test_get_system_health_with_alerts(self, client: AsyncClient, test_vars):
        """Test kiểm tra alerts khi có vấn đề."""
        headers = test_vars.get_headers("admin")
        
        response = await client.get("/api/v1/admin/analytics/system-health", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Có thể có alerts
        if "alerts" in data:
            assert isinstance(data["alerts"], list)
            if len(data["alerts"]) > 0:
                alert = data["alerts"][0]
                assert "type" in alert
                assert "message" in alert
                assert "severity" in alert
    
    @pytest.mark.asyncio
    async def test_get_system_health_non_admin(self, client: AsyncClient, test_vars):
        """Test non-admin không thể xem system health."""
        headers = test_vars.get_headers("student1")
        
        response = await client.get("/api/v1/admin/analytics/system-health", headers=headers)
        
        assert response.status_code == 403
