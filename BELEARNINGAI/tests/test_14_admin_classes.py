"""
TEST NHÓM 14: GIÁM SÁT LỚP HỌC CỦA ADMIN (4.3)
Tổng: 2 endpoints

Endpoints (theo CHUCNANG.md):
1. GET /api/v1/admin/classes - Xem tất cả lớp học
2. GET /api/v1/admin/classes/{class_id} - Xem chi tiết lớp học

Sử dụng test_variables để quản lý admin operations và class IDs.
"""
import pytest
from httpx import AsyncClient
from tests.conftest import assert_response_schema
from tests.test_variables import TestVariables


class TestAdminListClasses:
    """Test cases cho xem tất cả lớp học."""
    
    @pytest.mark.asyncio
    async def test_list_all_classes_success(self, client: AsyncClient, test_vars: TestVariables, test_course):
        """Test admin xem tất cả lớp học từ mọi giảng viên."""
        # Tạo lớp học từ nhiều instructors
        from models.models import Class
        instructor_ids = [test_vars.instructor1_user_id, test_vars.instructor2_user_id]
        for i, instructor_id in enumerate(instructor_ids, 1):
            cls = Class(
                name=f"Class from instructor{i}",
                instructor_id=instructor_id,
                course_id=test_vars.course_id,
                max_students=30,
                student_count=10 + i,
                status="active",
                invite_code=f"ADMIN{i}"
            )
            await cls.insert()
        
        headers = test_vars.get_headers("admin")
        
        response = await client.get("/api/v1/admin/classes", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Kiểm tra response schema theo API_SCHEMA Section 9.13
        required_fields = ["data", "total", "skip", "limit"]
        assert_response_schema(data, required_fields)
        
        # Phải có ít nhất 2 classes
        assert data["total"] >= 2
        
        # Kiểm tra class structure
        cls = data["data"][0]
        class_fields = ["class_id", "class_name", "course_title", "instructor_name", 
                       "student_count", "status", "created_at"]
        assert_response_schema(cls, class_fields)
    
    @pytest.mark.asyncio
    async def test_list_classes_filter_by_instructor(self, client: AsyncClient, test_vars: TestVariables, test_course):
        """Test lọc lớp học theo giảng viên."""
        from models.models import Class
        cls = Class(
            name="Instructor1 Class",
            instructor_id=test_vars.instructor1_user_id,
            course_id=test_vars.course_id,
            max_students=30,
            invite_code="FILTERINST"
        )
        await cls.insert()
        
        headers = test_vars.get_headers("admin")
        
        response = await client.get(
            f"/api/v1/admin/classes?instructor_id={test_vars.instructor1_user_id}",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Data should only contain classes from instructor1
        # Note: instructor_id is not in response, but we filtered by it
        assert data["total"] >= 1
    
    @pytest.mark.asyncio
    async def test_list_classes_filter_by_status(self, client: AsyncClient, test_vars):
        """Test lọc lớp học theo trạng thái."""
        headers = test_vars.get_headers("admin")
        
        response = await client.get("/api/v1/admin/classes?status=active", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        for cls in data["data"]:
            assert cls["status"] == "active"
    
    @pytest.mark.asyncio
    async def test_list_classes_pagination(self, client: AsyncClient, test_vars):
        """Test pagination."""
        headers = test_vars.get_headers("admin")
        
        response = await client.get("/api/v1/admin/classes?skip=0&limit=5", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["skip"] == 0
        assert data["limit"] == 5
    
    @pytest.mark.asyncio
    async def test_list_classes_non_admin(self, client: AsyncClient, test_vars):
        """Test non-admin không thể xem tất cả classes."""
        headers = test_vars.get_headers("student1")
        
        response = await client.get("/api/v1/admin/classes", headers=headers)
        
        assert response.status_code == 403


class TestAdminGetClassDetail:
    """Test cases cho xem chi tiết lớp học."""
    
    @pytest.mark.asyncio
    async def test_get_class_detail_success(self, client: AsyncClient, test_vars: TestVariables, test_course):
        """Test admin xem chi tiết bất kỳ lớp học nào."""
        from models.models import Class
        cls = Class(
            name="Test Class",
            instructor_id=test_vars.instructor1_user_id,
            course_id=test_vars.course_id,
            max_students=30,
            student_count=15,
            student_ids=[test_vars.student1_user_id, test_vars.student2_user_id],
            invite_code="ADMINDETAIL"
        )
        await cls.insert()
        
        headers = test_vars.get_headers("admin")
        
        response = await client.get(f"/api/v1/admin/classes/{cls.id}", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Kiểm tra response schema theo API_SCHEMA Section 9.14
        required_fields = ["class_id", "class_name", "course", "instructor", 
                          "student_count", "invite_code", "status", "class_stats",
                          "created_at", "start_date", "end_date"]
        assert_response_schema(data, required_fields)
        
        # Kiểm tra course nested object
        course = data["course"]
        assert "course_id" in course
        assert "title" in course
        assert "category" in course
        
        # Kiểm tra instructor nested object
        instructor = data["instructor"]
        assert "user_id" in instructor
        assert "full_name" in instructor
        assert "email" in instructor
        
        # Kiểm tra class_stats
        stats = data["class_stats"]
        assert "average_progress" in stats
        assert "completion_rate" in stats
        assert "active_students_today" in stats
    
    @pytest.mark.asyncio
    async def test_get_class_detail_not_found(self, client: AsyncClient, test_vars):
        """Test xem class không tồn tại."""
        headers = test_vars.get_headers("admin")
        fake_id = "00000000-0000-0000-0000-000000000000"
        
        response = await client.get(f"/api/v1/admin/classes/{fake_id}", headers=headers)
        
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_get_class_detail_non_admin(self, client: AsyncClient, test_vars: TestVariables, test_course):
        """Test non-admin không thể xem chi tiết class của instructor khác."""
        from models.models import Class
        cls = Class(
            name="Instructor1 Class",
            instructor_id=test_vars.instructor1_user_id,
            course_id=test_vars.course_id,
            max_students=30,
            invite_code="NOADMIN"
        )
        await cls.insert()
        
        # Instructor2 cố gắng xem
        headers = test_vars.get_headers("instructor2")
        
        response = await client.get(f"/api/v1/admin/classes/{cls.id}", headers=headers)
        
        assert response.status_code == 403
