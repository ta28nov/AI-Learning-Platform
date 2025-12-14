"""
TEST NHÓM 8: QUẢN LÝ LỚP HỌC CỦA GIẢNG VIÊN (3.1)
Tổng: 5 endpoints

Endpoints:
1. POST /api/v1/classes - Tạo lớp học mới
2. GET /api/v1/classes/my-classes - Xem danh sách lớp học
3. GET /api/v1/classes/{id} - Xem chi tiết lớp học
4. PUT /api/v1/classes/{id} - Chỉnh sửa thông tin lớp
5. DELETE /api/v1/classes/{id} - Xóa lớp học

Sử dụng test_variables để lưu trữ class_id, invite_code và tái sử dụng.
"""
import pytest
from httpx import AsyncClient
from datetime import datetime, timezone, timedelta
from tests.conftest import assert_response_schema
from tests.test_variables import TestVariables


class TestCreateClass:
    """Test cases cho tạo lớp học mới."""
    
    @pytest.mark.asyncio
    async def test_create_class_success(self, client: AsyncClient, test_vars: TestVariables, test_course):
        """Test tạo lớp học thành công."""
        headers = test_vars.get_headers("instructor1")
        
        start_date = (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()
        end_date = (datetime.now(timezone.utc) + timedelta(days=90)).isoformat()
        
        payload = {
            "name": "Python Programming Class 2024",
            "description": "Lớp học lập trình Python cho người mới bắt đầu",
            "course_id": test_vars.course_id,
            "start_date": start_date,
            "end_date": end_date,
            "max_students": 30
        }
        
        response = await client.post("/api/v1/classes", headers=headers, json=payload)
        
        assert response.status_code == 201
        data = response.json()
        
        # Lưu class_id và invite_code vào test_vars
        test_vars.class_id = data["id"]
        test_vars.invite_code = data["invite_code"]
        
        # Kiểm tra response schema
        required_fields = ["id", "name", "description", "course_id", "instructor_id",
                          "start_date", "end_date", "max_students", "invite_code",
                          "status", "student_count", "created_at"]
        assert_response_schema(data, required_fields)
        
        # Kiểm tra giá trị
        assert data["name"] == payload["name"]
        assert data["course_id"] == test_vars.course_id
        assert data["instructor_id"] == test_vars.instructor1_user_id
        assert data["max_students"] == 30
        assert data["student_count"] == 0
        assert data["status"] == "preparing"
        
        # Invite code phải được tạo tự động
        assert len(data["invite_code"]) >= 6
    
    @pytest.mark.asyncio
    async def test_create_class_student_role(self, client: AsyncClient, test_vars: TestVariables, test_course):
        """Test student không thể tạo lớp học."""
        headers = test_vars.get_headers("student1")
        
        payload = {
            "name": "Test Class",
            "description": "Description",
            "course_id": test_vars.course_id,
            "start_date": (datetime.now(timezone.utc) + timedelta(days=7)).isoformat(),
            "end_date": (datetime.now(timezone.utc) + timedelta(days=90)).isoformat(),
            "max_students": 30
        }
        
        response = await client.post("/api/v1/classes", headers=headers, json=payload)
        
        assert response.status_code == 403


class TestListMyClasses:
    """Test cases cho xem danh sách lớp học."""
    
    @pytest.mark.asyncio
    async def test_list_my_classes_success(self, client: AsyncClient, test_vars: TestVariables, test_course):
        """Test xem danh sách lớp học của instructor."""
        headers = test_vars.get_headers("instructor1")
        
        # Tạo 2 lớp học trước
        for i in range(2):
            from models.models import Class
            cls = Class(
                name=f"Class {i+1}",
                description=f"Description {i+1}",
                instructor_id=test_vars.instructor1_user_id,
                course_id=test_vars.course_id,
                max_students=30,
                invite_code=f"CODE{i+1}"
            )
            await cls.insert()
        
        # Lấy danh sách
        response = await client.get("/api/v1/classes/my-classes", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Kiểm tra response schema
        required_fields = ["classes", "total", "skip", "limit"]
        assert_response_schema(data, required_fields)
        
        # Phải có ít nhất 2 lớp
        assert data["total"] >= 2
        assert len(data["classes"]) >= 2
    
    @pytest.mark.asyncio
    async def test_list_my_classes_empty(self, client: AsyncClient, test_vars: TestVariables):
        """Test xem danh sách khi chưa có lớp nào."""
        headers = test_vars.get_headers("instructor2")  # Instructor chưa tạo lớp
        
        response = await client.get("/api/v1/classes/my-classes", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["total"] == 0
        assert len(data["classes"]) == 0


class TestGetClassDetail:
    """Test cases cho xem chi tiết lớp học."""
    
    @pytest.mark.asyncio
    async def test_get_class_detail_success(self, client: AsyncClient, test_vars: TestVariables, test_course):
        """Test xem chi tiết lớp học thành công."""
        headers = test_vars.get_headers("instructor1")
        
        # Tạo lớp học
        from models.models import Class
        cls = Class(
            name="Test Class",
            description="Detailed class",
            instructor_id=test_vars.instructor1_user_id,
            course_id=test_vars.course_id,
            max_students=30,
            invite_code="DETAIL1"
        )
        await cls.insert()
        test_vars.class_id = str(cls.id)
        
        # Xem chi tiết
        response = await client.get(f"/api/v1/classes/{cls.id}", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Kiểm tra response schema
        required_fields = ["id", "name", "description", "course_id", "course_title",
                          "instructor_id", "instructor_name", "max_students", "student_count",
                          "invite_code", "status", "students", "statistics", "created_at"]
        assert_response_schema(data, required_fields)
    
    @pytest.mark.asyncio
    async def test_get_class_detail_not_owner(self, client: AsyncClient, test_vars: TestVariables, test_course):
        """Test xem chi tiết lớp của instructor khác."""
        # Instructor1 tạo lớp
        from models.models import Class
        cls = Class(
            name="Instructor1 Class",
            instructor_id=test_vars.instructor1_user_id,
            course_id=test_vars.course_id,
            max_students=30,
            invite_code="NOTOWNER"
        )
        await cls.insert()
        
        # Instructor2 cố gắng xem
        headers2 = test_vars.get_headers("instructor2")
        
        response = await client.get(f"/api/v1/classes/{cls.id}", headers=headers2)
        
        assert response.status_code == 403


class TestUpdateClass:
    """Test cases cho cập nhật lớp học."""
    
    @pytest.mark.asyncio
    async def test_update_class_success(self, client: AsyncClient, test_vars: TestVariables, test_course):
        """Test cập nhật lớp học thành công."""
        headers = test_vars.get_headers("instructor1")
        
        # Tạo lớp
        from models.models import Class
        cls = Class(
            name="Original Name",
            description="Original description",
            instructor_id=test_vars.instructor1_user_id,
            course_id=test_vars.course_id,
            max_students=30,
            status="preparing",
            invite_code="UPDATE1"
        )
        await cls.insert()
        
        # Cập nhật
        update_payload = {
            "name": "Updated Name",
            "description": "Updated description",
            "max_students": 40,
            "status": "active"
        }
        
        response = await client.put(f"/api/v1/classes/{cls.id}", headers=headers, json=update_payload)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["name"] == "Updated Name"
        assert data["description"] == "Updated description"
        assert data["max_students"] == 40
        assert data["status"] == "active"
    
    @pytest.mark.asyncio
    async def test_update_class_not_owner(self, client: AsyncClient, test_vars: TestVariables, test_course):
        """Test cập nhật lớp của instructor khác."""
        from models.models import Class
        cls = Class(
            name="Instructor1 Class",
            instructor_id=test_vars.instructor1_user_id,
            course_id=test_vars.course_id,
            max_students=30,
            invite_code="NOTOWNER2"
        )
        await cls.insert()
        
        headers2 = test_vars.get_headers("instructor2")
        
        update_payload = {"name": "Hacked Name"}
        
        response = await client.put(f"/api/v1/classes/{cls.id}", headers=headers2, json=update_payload)
        
        assert response.status_code == 403


class TestDeleteClass:
    """Test cases cho xóa lớp học."""
    
    @pytest.mark.asyncio
    async def test_delete_class_success(self, client: AsyncClient, test_vars: TestVariables, test_course):
        """Test xóa lớp học thành công."""
        headers = test_vars.get_headers("instructor1")
        
        # Tạo lớp không có học viên
        from models.models import Class
        cls = Class(
            name="To Delete",
            instructor_id=test_vars.instructor1_user_id,
            course_id=test_vars.course_id,
            max_students=30,
            student_count=0,
            invite_code="DELETE1"
        )
        await cls.insert()
        
        # Xóa
        response = await client.delete(f"/api/v1/classes/{cls.id}", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "message" in data
    
    @pytest.mark.asyncio
    async def test_delete_class_not_owner(self, client: AsyncClient, test_vars: TestVariables, test_course):
        """Test xóa lớp của instructor khác."""
        from models.models import Class
        cls = Class(
            name="Instructor1 Class",
            instructor_id=test_vars.instructor1_user_id,
            course_id=test_vars.course_id,
            max_students=30,
            invite_code="NOTOWNER3"
        )
        await cls.insert()
        
        headers2 = test_vars.get_headers("instructor2")
        
        response = await client.delete(f"/api/v1/classes/{cls.id}", headers=headers2)
        
        assert response.status_code == 403
