"""
TEST NHÓM 3: KHÁM PHÁ & ĐĂNG KÝ KHÓA HỌC (2.3)
Tổng: 8 endpoints

Endpoints:
1. GET /api/v1/courses/search - Tìm kiếm khóa học
2. GET /api/v1/courses/public - Xem danh sách khóa học công khai
3. GET /api/v1/courses/{course_id} - Xem chi tiết khóa học
4. POST /api/v1/enrollments - Đăng ký khóa học
5. GET /api/v1/enrollments/my-courses - Xem khóa học đã đăng ký
6. GET /api/v1/enrollments/{enrollment_id} - Xem chi tiết enrollment
7. GET /api/v1/courses/{course_id}/enrollment-status - Kiểm tra trạng thái đăng ký
8. DELETE /api/v1/enrollments/{enrollment_id} - Hủy đăng ký
"""
import pytest
from httpx import AsyncClient
from tests.conftest import get_auth_headers, assert_response_schema


class TestCourseSearch:
    """Test cases cho tìm kiếm khóa học."""
    
    @pytest.mark.asyncio
    async def test_search_courses_by_keyword(self, client: AsyncClient, test_vars, test_course):
        """Test tìm kiếm khóa học theo từ khóa."""
        headers = test_vars.get_headers("student1")
        
        response = await client.get(
            "/api/v1/courses/search?keyword=Python",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        required_fields = ["courses", "total", "skip", "limit", "search_metadata"]
        assert_response_schema(data, required_fields)
        
        # Kiểm tra có tìm thấy khóa học
        assert data["total"] >= 0
        if len(data["courses"]) > 0:
            course = data["courses"][0]
            course_fields = ["id", "title", "description", "category", "level", "total_modules", 
                            "total_lessons", "enrollment_count", "is_enrolled"]
            assert_response_schema(course, course_fields)
    
    @pytest.mark.asyncio
    async def test_search_courses_with_filters(self, client: AsyncClient, test_vars):
        """Test tìm kiếm với filters nâng cao."""
        headers = test_vars.get_headers("student1")
        
        response = await client.get(
            "/api/v1/courses/search?category=Programming&level=Beginner&sort_by=created_at&sort_order=desc",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "courses" in data
    
    @pytest.mark.asyncio
    async def test_search_courses_pagination(self, client: AsyncClient, test_vars):
        """Test pagination trong tìm kiếm."""
        headers = test_vars.get_headers("student1")
        
        response = await client.get(
            "/api/v1/courses/search?skip=0&limit=5",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["skip"] == 0
        assert data["limit"] == 5
        assert len(data["courses"]) <= 5


class TestPublicCourses:
    """Test cases cho danh sách khóa học công khai."""
    
    @pytest.mark.asyncio
    async def test_list_public_courses(self, client: AsyncClient, test_vars, test_course):
        """Test xem danh sách khóa học công khai."""
        headers = test_vars.get_headers("student1")
        
        response = await client.get("/api/v1/courses/public", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        required_fields = ["courses", "total", "skip", "limit"]
        assert_response_schema(data, required_fields)
    
    @pytest.mark.asyncio
    async def test_list_public_courses_with_category_filter(self, client: AsyncClient, test_vars):
        """Test lọc khóa học theo category."""
        headers = test_vars.get_headers("student1")
        
        response = await client.get(
            "/api/v1/courses/public?category=Programming",
            headers=headers
        )
        
        assert response.status_code == 200


class TestCourseDetail:
    """Test cases cho xem chi tiết khóa học."""
    
    @pytest.mark.asyncio
    async def test_get_course_detail_success(self, client: AsyncClient, test_vars, test_course):
        """Test xem chi tiết khóa học."""
        headers = test_vars.get_headers("student1")
        course_id = test_vars.course_id
        
        response = await client.get(f"/api/v1/courses/{course_id}", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        required_fields = ["id", "title", "description", "category", "level", "owner_info",
                          "learning_outcomes", "prerequisites", "modules", "course_statistics",
                          "enrollment_info", "created_at", "updated_at"]
        assert_response_schema(data, required_fields)
        
        # Kiểm tra modules
        assert len(data["modules"]) > 0
        module = data["modules"][0]
        assert "id" in module
        assert "title" in module
        assert "lessons" in module
    
    @pytest.mark.asyncio
    async def test_get_course_detail_not_found(self, client: AsyncClient, test_vars):
        """Test xem khóa học không tồn tại."""
        headers = test_vars.get_headers("student1")
        fake_id = "00000000-0000-0000-0000-000000000000"
        
        response = await client.get(f"/api/v1/courses/{fake_id}", headers=headers)
        
        assert response.status_code == 404


class TestEnrollment:
    """Test cases cho đăng ký khóa học."""
    
    @pytest.mark.asyncio
    async def test_enroll_course_success(self, client: AsyncClient, test_vars, test_course):
        """Test đăng ký khóa học thành công."""
        headers = test_vars.get_headers("student2")  # Student chưa đăng ký
        course_id = test_vars.course_id
        
        payload = {"course_id": course_id}
        response = await client.post("/api/v1/enrollments", headers=headers, json=payload)
        
        assert response.status_code == 201
        data = response.json()
        
        required_fields = ["id", "user_id", "course_id", "course_title", "status", 
                          "enrolled_at", "progress_percent", "message"]
        assert_response_schema(data, required_fields)
        
        assert data["status"] == "active"
        assert data["progress_percent"] == 0
    
    @pytest.mark.asyncio
    async def test_enroll_course_already_enrolled(self, client: AsyncClient, test_vars, test_enrollment):
        """Test đăng ký khóa học đã đăng ký."""
        headers = test_vars.get_headers("student1")  # Đã đăng ký
        
        # Lấy course_id từ enrollment hiện tại
        enrollment = test_enrollment["enrollment"]
        course_id = enrollment.course_id
        
        payload = {"course_id": course_id}
        response = await client.post("/api/v1/enrollments", headers=headers, json=payload)
        
        assert response.status_code == 400
        # Backend trả về message tiếng Việt
        assert "đã đăng ký" in response.json()["detail"].lower() or "already enrolled" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_enroll_course_not_found(self, client: AsyncClient, test_vars):
        """Test đăng ký khóa học không tồn tại."""
        headers = test_vars.get_headers("student1")
        fake_id = "00000000-0000-0000-0000-000000000000"
        
        payload = {"course_id": fake_id}
        response = await client.post("/api/v1/enrollments", headers=headers, json=payload)
        
        # Backend trả về 404 (Not Found) cho UUID không tồn tại
        assert response.status_code == 404


class TestMyEnrollments:
    """Test cases cho xem khóa học đã đăng ký."""
    
    @pytest.mark.asyncio
    async def test_list_my_enrollments(self, client: AsyncClient, test_vars, test_enrollment):
        """Test xem danh sách khóa học đã đăng ký."""
        headers = test_vars.get_headers("student1")
        
        response = await client.get("/api/v1/enrollments/my-courses", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        required_fields = ["enrollments", "summary", "skip", "limit"]
        assert_response_schema(data, required_fields)
        
        # Kiểm tra summary
        summary = data["summary"]
        assert "total_enrollments" in summary
        assert "in_progress" in summary
        assert "completed" in summary
        assert "cancelled" in summary
    
    @pytest.mark.asyncio
    async def test_list_my_enrollments_filter_by_status(self, client: AsyncClient, test_vars, test_enrollment):
        """Test lọc enrollment theo status."""
        headers = test_vars.get_headers("student1")
        
        response = await client.get(
            "/api/v1/enrollments/my-courses?status=active",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Tất cả enrollment trả về phải có status = active
        for enrollment in data["enrollments"]:
            assert enrollment["status"] == "active"
    
    @pytest.mark.asyncio
    async def test_get_enrollment_detail(self, client: AsyncClient, test_vars, test_enrollment):
        """Test xem chi tiết một enrollment."""
        headers = test_vars.get_headers("student1")
        enrollment_id = test_vars.enrollment_id
        
        response = await client.get(f"/api/v1/enrollments/{enrollment_id}", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        required_fields = ["id", "user_id", "course_id", "course_title", "status", 
                          "enrolled_at", "progress_percent"]
        assert_response_schema(data, required_fields)


class TestEnrollmentStatus:
    """Test cases cho kiểm tra trạng thái đăng ký."""
    
    @pytest.mark.asyncio
    async def test_check_enrollment_status_enrolled(self, client: AsyncClient, test_vars, test_enrollment):
        """Test kiểm tra status khi đã đăng ký."""
        headers = test_vars.get_headers("student1")
        
        enrollment = test_enrollment["enrollment"]
        course_id = enrollment.course_id
        
        response = await client.get(
            f"/api/v1/courses/{course_id}/enrollment-status",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        required_fields = ["is_enrolled", "enrollment_id", "can_access_content", 
                          "enrolled_at", "progress_percent"]
        assert_response_schema(data, required_fields)
        
        assert data["is_enrolled"] is True
        assert data["can_access_content"] is True
    
    @pytest.mark.asyncio
    async def test_check_enrollment_status_not_enrolled(self, client: AsyncClient, test_vars, test_course):
        """Test kiểm tra status khi chưa đăng ký."""
        headers = test_vars.get_headers("student2")  # Chưa đăng ký
        course_id = test_vars.course_id
        
        response = await client.get(
            f"/api/v1/courses/{course_id}/enrollment-status",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["is_enrolled"] is False
        assert data["can_access_content"] is False
        assert data["enrollment_id"] is None


class TestUnenrollment:
    """Test cases cho hủy đăng ký khóa học."""
    
    @pytest.mark.asyncio
    async def test_unenroll_course_success(self, client: AsyncClient, test_vars, test_enrollment):
        """Test hủy đăng ký khóa học thành công."""
        headers = test_vars.get_headers("student1")
        enrollment_id = test_vars.enrollment_id
        
        response = await client.delete(f"/api/v1/enrollments/{enrollment_id}", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "message" in data
        assert "note" in data
    
    @pytest.mark.asyncio
    async def test_unenroll_course_not_owner(self, client: AsyncClient, test_vars, test_enrollment):
        """Test hủy đăng ký enrollment của người khác."""
        headers = test_vars.get_headers("student2")  # Không phải owner
        enrollment_id = test_vars.enrollment_id
        
        response = await client.delete(f"/api/v1/enrollments/{enrollment_id}", headers=headers)
        
        assert response.status_code == 403
