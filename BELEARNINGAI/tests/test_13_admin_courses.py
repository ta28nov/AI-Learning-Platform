"""
TEST NHÓM 13: QUẢN LÝ KHÓA HỌC CỦA ADMIN (4.2)
Tổng: 5 endpoints

Endpoints (theo CHUCNANG.md):
1. GET /api/v1/admin/courses - Xem tất cả khóa học
2. GET /api/v1/admin/courses/{course_id} - Xem chi tiết khóa học
3. POST /api/v1/admin/courses - Tạo khóa học chính thức
4. PUT /api/v1/admin/courses/{course_id} - Chỉnh sửa bất kỳ khóa học nào
5. DELETE /api/v1/admin/courses/{course_id} - Xóa khóa học

Sử dụng test_variables để quản lý admin operations và course IDs.
"""
import pytest
from httpx import AsyncClient
from tests.conftest import assert_response_schema
from tests.test_variables import TestVariables


class TestAdminListCourses:
    """Test cases cho xem tất cả khóa học."""
    
    @pytest.mark.asyncio
    async def test_list_all_courses_success(self, client: AsyncClient, test_vars, test_course):
        """Test admin xem tất cả khóa học (public và personal)."""
        headers = test_vars.get_headers("admin")
        
        response = await client.get("/api/v1/admin/courses", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Kiểm tra response schema theo CHUCNANG.md
        required_fields = ["courses", "total", "skip", "limit"]
        assert_response_schema(data, required_fields)
        
        # Phải có ít nhất 1 course
        assert data["total"] >= 1
        
        # Kiểm tra course structure
        course = data["courses"][0]
        course_fields = ["id", "title", "owner_type", "owner_name", "category",
                        "enrollment_count", "status", "created_at"]
        assert_response_schema(course, course_fields)
    
    @pytest.mark.asyncio
    async def test_list_courses_filter_by_type(self, client: AsyncClient, test_vars):
        """Test lọc khóa học theo loại (public/personal)."""
        headers = test_vars.get_headers("admin")
        
        response = await client.get("/api/v1/admin/courses?type=public", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Tất cả courses phải là public (owner_type = admin)
        for course in data["courses"]:
            assert course["owner_type"] in ["admin", "public"]
    
    @pytest.mark.asyncio
    async def test_list_courses_filter_by_status(self, client: AsyncClient, test_vars):
        """Test lọc khóa học theo trạng thái."""
        headers = test_vars.get_headers("admin")
        
        response = await client.get("/api/v1/admin/courses?status=published", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        for course in data["courses"]:
            assert course["status"] == "published"
    
    @pytest.mark.asyncio
    async def test_list_courses_filter_by_owner(self, client: AsyncClient, test_vars: TestVariables):
        """Test lọc khóa học theo tác giả."""
        headers = test_vars.get_headers("admin")
        owner_id = test_vars.admin_user_id
        
        response = await client.get(f"/api/v1/admin/courses?owner_id={owner_id}", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        for course in data["courses"]:
            assert course["owner_id"] == owner_id
    
    @pytest.mark.asyncio
    async def test_list_courses_search(self, client: AsyncClient, test_vars):
        """Test tìm kiếm khóa học theo tên."""
        headers = test_vars.get_headers("admin")
        
        response = await client.get("/api/v1/admin/courses?search=Python", headers=headers)
        
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_list_courses_non_admin(self, client: AsyncClient, test_vars):
        """Test non-admin không thể xem tất cả courses."""
        headers = test_vars.get_headers("student1")
        
        response = await client.get("/api/v1/admin/courses", headers=headers)
        
        assert response.status_code == 403


class TestAdminGetCourseDetail:
    """Test cases cho xem chi tiết khóa học."""
    
    @pytest.mark.asyncio
    async def test_get_course_detail_success(self, client: AsyncClient, test_vars, test_course):
        """Test xem chi tiết khóa học."""
        headers = test_vars.get_headers("admin")
        course_id = test_vars.course_id
        
        response = await client.get(f"/api/v1/admin/courses/{course_id}", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Kiểm tra response schema theo CHUCNANG.md
        required_fields = ["id", "title", "description", "category", "level", "modules",
                          "analytics", "created_at", "updated_at"]
        assert_response_schema(data, required_fields)
        
        # Kiểm tra analytics
        analytics = data["analytics"]
        assert "enrollment_count" in analytics
        assert "completion_rate" in analytics
    
    @pytest.mark.asyncio
    async def test_get_course_detail_with_preview(self, client: AsyncClient, test_vars, test_course):
        """Test xem chi tiết với preview mode."""
        headers = test_vars.get_headers("admin")
        course_id = test_vars.course_id
        
        response = await client.get(
            f"/api/v1/admin/courses/{course_id}?preview=true",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Preview mode có thể có thêm thông tin về giao diện học tập
        assert "preview_url" in data or "content_preview" in data or "modules" in data
    
    @pytest.mark.asyncio
    async def test_get_course_detail_not_found(self, client: AsyncClient, test_vars):
        """Test xem course không tồn tại."""
        headers = test_vars.get_headers("admin")
        fake_id = "00000000-0000-0000-0000-000000000000"
        
        response = await client.get(f"/api/v1/admin/courses/{fake_id}", headers=headers)
        
        assert response.status_code == 404


class TestAdminCreateCourse:
    """Test cases cho tạo khóa học chính thức."""
    
    @pytest.mark.asyncio
    async def test_create_official_course_success(self, client: AsyncClient, test_vars):
        """Test tạo khóa học chính thức thành công."""
        headers = test_vars.get_headers("admin")
        
        payload = {
            "title": "Official Python Course",
            "description": "Khóa học Python chính thức của hệ thống",
            "category": "Programming",
            "level": "Beginner",
            "language": "vi",
            "learning_outcomes": [
                {
                    "description": "Master Python basics",
                    "skill_tag": "python-basics"
                }
            ],
            "prerequisites": ["Basic computer knowledge"],
            "modules": [
                {
                    "title": "Module 1: Introduction",
                    "description": "Introduction to Python",
                    "order": 1,
                    "difficulty": "Basic",
                    "lessons": [
                        {
                            "title": "Lesson 1: Getting Started",
                            "description": "First lesson",
                            "order": 1,
                            "content_type": "text",
                            "duration_minutes": 30
                        }
                    ]
                }
            ]
        }
        
        response = await client.post("/api/v1/admin/courses", headers=headers, json=payload)
        
        assert response.status_code == 201
        data = response.json()
        
        required_fields = ["id", "title", "description", "category", "level", "status",
                          "owner_type", "created_at"]
        assert_response_schema(data, required_fields)
        
        assert data["title"] == payload["title"]
        assert data["owner_type"] == "admin"
        assert data["status"] == "draft"  # Mặc định là draft
    
    @pytest.mark.asyncio
    async def test_create_course_minimal_data(self, client: AsyncClient, test_vars):
        """Test tạo khóa học với dữ liệu tối thiểu."""
        headers = test_vars.get_headers("admin")
        
        payload = {
            "title": "Minimal Course",
            "description": "Short description",
            "category": "Programming",
            "level": "Beginner"
        }
        
        response = await client.post("/api/v1/admin/courses", headers=headers, json=payload)
        
        assert response.status_code == 201
    
    @pytest.mark.asyncio
    async def test_create_course_invalid_category(self, client: AsyncClient, test_vars):
        """Test tạo khóa học với category không hợp lệ."""
        headers = test_vars.get_headers("admin")
        
        payload = {
            "title": "Test Course",
            "description": "Description",
            "category": "InvalidCategory",
            "level": "Beginner"
        }
        
        response = await client.post("/api/v1/admin/courses", headers=headers, json=payload)
        
        assert response.status_code == 400


class TestAdminUpdateCourse:
    """Test cases cho chỉnh sửa bất kỳ khóa học nào."""
    
    @pytest.mark.asyncio
    async def test_update_any_course_success(self, client: AsyncClient, test_vars, test_course):
        """Test admin cập nhật bất kỳ khóa học nào."""
        headers = test_vars.get_headers("admin")
        course_id = test_vars.course_id
        
        payload = {
            "title": "Updated by Admin",
            "description": "Admin đã cập nhật khóa học này"
        }
        
        response = await client.put(
            f"/api/v1/admin/courses/{course_id}",
            headers=headers,
            json=payload
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["title"] == payload["title"]
        assert data["description"] == payload["description"]
    
    @pytest.mark.asyncio
    async def test_update_personal_course(self, client: AsyncClient, test_vars: TestVariables):
        """Test admin cập nhật personal course của user."""
        # Tạo personal course của student
        from models.models import Course
        personal_course = Course(
            title="Student Personal Course",
            description="Personal course",
            category="Programming",
            level="Beginner",
            owner_id=test_vars.student1_user_id,
            owner_type="student",
            status="draft"
        )
        await personal_course.insert()
        
        headers = test_vars.get_headers("admin")
        
        payload = {
            "title": "Admin Updated Personal Course",
            "status": "published"  # Admin có thể publish personal course
        }
        
        response = await client.put(
            f"/api/v1/admin/courses/{personal_course.id}",
            headers=headers,
            json=payload
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["title"] == payload["title"]
        assert data["status"] == "published"
    
    @pytest.mark.asyncio
    async def test_update_course_add_modules(self, client: AsyncClient, test_vars, test_course):
        """Test thêm modules vào khóa học."""
        headers = test_vars.get_headers("admin")
        course_id = test_vars.course_id
        
        payload = {
            "modules": [
                {
                    "title": "New Module",
                    "description": "New module description",
                    "order": 10,
                    "difficulty": "Intermediate"
                }
            ]
        }
        
        response = await client.put(
            f"/api/v1/admin/courses/{course_id}",
            headers=headers,
            json=payload
        )
        
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_update_course_not_found(self, client: AsyncClient, test_vars):
        """Test cập nhật course không tồn tại."""
        headers = test_vars.get_headers("admin")
        fake_id = "00000000-0000-0000-0000-000000000000"
        
        payload = {"title": "Test"}
        
        response = await client.put(f"/api/v1/admin/courses/{fake_id}", headers=headers, json=payload)
        
        assert response.status_code == 404


class TestAdminDeleteCourse:
    """Test cases cho xóa khóa học."""
    
    @pytest.mark.asyncio
    async def test_delete_course_success(self, client: AsyncClient, test_vars: TestVariables):
        """Test xóa khóa học thành công."""
        # Tạo course để xóa
        from models.models import Course
        course = Course(
            title="Course To Delete",
            description="Will be deleted",
            category="Programming",
            level="Beginner",
            owner_id=test_vars.admin_user_id,
            owner_type="admin",
            status="draft"
        )
        await course.insert()
        
        headers = test_vars.get_headers("admin")
        
        response = await client.delete(f"/api/v1/admin/courses/{course.id}", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "message" in data
        
        # Verify đã xóa
        from models.models import Course as CourseModel
        deleted_course = await CourseModel.get(course.id)
        assert deleted_course is None
    
    @pytest.mark.asyncio
    async def test_delete_course_with_enrollments(self, client: AsyncClient, test_vars, test_enrollment):
        """Test xóa khóa học có enrollments."""
        headers = test_vars.get_headers("admin")
        
        # Lấy course_id từ enrollment
        enrollment = test_enrollment["enrollment"]
        course_id = enrollment.course_id
        
        response = await client.delete(f"/api/v1/admin/courses/{course_id}", headers=headers)
        
        # Có thể trả về 200 với warning hoặc 400
        assert response.status_code in [200, 400]
        
        if response.status_code == 200:
            data = response.json()
            assert "warning" in data or "impact" in data
    
    @pytest.mark.asyncio
    async def test_delete_course_used_in_classes(self, client: AsyncClient, test_vars: TestVariables, test_course):
        """Test xóa khóa học đang được sử dụng trong lớp."""
        # Tạo class sử dụng course
        from models.models import Class
        cls = Class(
            name="Test Class",
            instructor_id=test_vars.instructor1_user_id,
            course_id=test_vars.course_id,
            max_students=30,
            invite_code="DELETETEST"
        )
        await cls.insert()
        
        headers = test_vars.get_headers("admin")
        
        response = await client.delete(f"/api/v1/admin/courses/{test_course['course_id']}", headers=headers)
        
        # Phải có impact analysis
        assert response.status_code in [200, 400]
        
        if response.status_code == 200:
            data = response.json()
            assert "impact" in data or "classes_affected" in data
    
    @pytest.mark.asyncio
    async def test_delete_course_not_found(self, client: AsyncClient, test_vars):
        """Test xóa course không tồn tại."""
        headers = test_vars.get_headers("admin")
        fake_id = "00000000-0000-0000-0000-000000000000"
        
        response = await client.delete(f"/api/v1/admin/courses/{fake_id}", headers=headers)
        
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_delete_course_non_admin(self, client: AsyncClient, test_vars, test_course):
        """Test non-admin không thể xóa course."""
        headers = test_vars.get_headers("instructor1")
        
        response = await client.delete(f"/api/v1/admin/courses/{test_course['course_id']}", headers=headers)
        
        assert response.status_code == 403
