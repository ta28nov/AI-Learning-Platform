"""
TEST NHÓM 9: QUẢN LÝ HỌC VIÊN TRONG LỚP (3.2)
Tổng: 5 endpoints

Endpoints:
1. POST /api/v1/classes/join - Học viên tham gia lớp bằng mã mời
2. GET /api/v1/classes/{class_id}/students - Xem danh sách học viên trong lớp
3. GET /api/v1/classes/{class_id}/students/{student_id} - Xem hồ sơ học viên chi tiết
4. DELETE /api/v1/classes/{class_id}/students/{student_id} - Xóa học viên khỏi lớp
5. GET /api/v1/classes/{class_id}/progress - Xem tiến độ tổng thể của lớp

Sử dụng test_variables để quản lý class_id, student_ids và tái sử dụng.
"""
import pytest
from httpx import AsyncClient
from datetime import datetime, timezone, timedelta
from tests.conftest import assert_response_schema
from tests.test_variables import TestVariables


class TestStudentJoinClass:
    """Test cases cho học viên tham gia lớp học."""
    
    @pytest.mark.asyncio
    async def test_join_class_success(self, client: AsyncClient, test_vars: TestVariables, test_course):
        """Test tham gia lớp học thành công với mã mời hợp lệ."""
        # Tạo lớp học với invite code
        from models.models import Class
        cls = Class(
            name="Python Class 2024",
            description="Lớp học Python",
            instructor_id=test_vars.instructor1_user_id,
            course_id=test_vars.course_id,
            max_students=30,
            student_count=0,
            invite_code="PYTHON2024",
            status="active"
        )
        await cls.insert()
        test_vars.class_id = str(cls.id)
        test_vars.invite_code = "PYTHON2024"
        
        # Student tham gia lớp
        headers = test_vars.get_headers("student1")
        
        payload = {
            "invite_code": "PYTHON2024"
        }
        
        response = await client.post("/api/v1/classes/join", headers=headers, json=payload)
        
        assert response.status_code == 200
        data = response.json()
        
        # Kiểm tra response schema
        required_fields = ["class_id", "class_name", "instructor_name", "course_title",
                          "joined_at", "message"]
        assert_response_schema(data, required_fields)
        
        assert data["class_id"] == str(cls.id)
        assert data["class_name"] == "Python Class 2024"
    
    @pytest.mark.asyncio
    async def test_join_class_already_joined(self, client: AsyncClient, test_vars: TestVariables, test_course):
        """Test tham gia lớp đã tham gia rồi."""
        from models.models import Class
        cls = Class(
            name="Test Class",
            instructor_id=test_vars.instructor1_user_id,
            course_id=test_vars.course_id,
            max_students=30,
            student_count=1,
            student_ids=[test_vars.student1_user_id],  # Đã có student1
            invite_code="ALREADY"
        )
        await cls.insert()
        
        headers = test_vars.get_headers("student1")
        
        payload = {"invite_code": "ALREADY"}
        
        response = await client.post("/api/v1/classes/join", headers=headers, json=payload)
        
        assert response.status_code == 400
        assert "already joined" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_join_class_full(self, client: AsyncClient, test_vars: TestVariables, test_course):
        """Test tham gia lớp đã đầy."""
        from models.models import Class
        cls = Class(
            name="Full Class",
            instructor_id=test_vars.instructor1_user_id,
            course_id=test_vars.course_id,
            max_students=2,
            student_count=2,  # Đã đầy
            invite_code="FULL"
        )
        await cls.insert()
        
        headers = test_vars.get_headers("student1")
        
        payload = {"invite_code": "FULL"}
        
        response = await client.post("/api/v1/classes/join", headers=headers, json=payload)
        
        assert response.status_code == 400
        assert "full" in response.json()["detail"].lower()


class TestListClassStudents:
    """Test cases cho xem danh sách học viên trong lớp."""
    
    @pytest.mark.asyncio
    async def test_list_students_success(self, client: AsyncClient, test_vars: TestVariables, test_course):
        """Test xem danh sách học viên thành công."""
        # Tạo lớp với học viên
        from models.models import Class
        cls = Class(
            name="Test Class",
            instructor_id=test_vars.instructor1_user_id,
            course_id=test_vars.course_id,
            max_students=30,
            student_count=2,
            student_ids=[test_vars.student1_user_id, test_vars.student2_user_id],
            invite_code="LISTSTUDENTS"
        )
        await cls.insert()
        
        headers = test_vars.get_headers("instructor1")
        
        response = await client.get(f"/api/v1/classes/{cls.id}/students", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Kiểm tra response schema
        required_fields = ["students", "total", "skip", "limit", "class_info"]
        assert_response_schema(data, required_fields)
        
        # Phải có 2 học viên
        assert data["total"] == 2
        assert len(data["students"]) == 2
    
    @pytest.mark.asyncio
    async def test_list_students_not_instructor(self, client: AsyncClient, test_vars: TestVariables, test_course):
        """Test xem danh sách học viên khi không phải instructor của lớp."""
        from models.models import Class
        cls = Class(
            name="Instructor1 Class",
            instructor_id=test_vars.instructor1_user_id,
            course_id=test_vars.course_id,
            max_students=30,
            invite_code="NOTINSTRUCTOR"
        )
        await cls.insert()
        
        # Instructor2 cố gắng xem
        headers = test_vars.get_headers("instructor2")
        
        response = await client.get(f"/api/v1/classes/{cls.id}/students", headers=headers)
        
        assert response.status_code == 403


class TestGetStudentProfile:
    """Test cases cho xem hồ sơ học viên chi tiết."""
    
    @pytest.mark.asyncio
    async def test_get_student_profile_success(self, client: AsyncClient, test_vars: TestVariables, test_course):
        """Test xem hồ sơ học viên thành công."""
        from models.models import Class
        cls = Class(
            name="Test Class",
            instructor_id=test_vars.instructor1_user_id,
            course_id=test_vars.course_id,
            max_students=30,
            student_ids=[test_vars.student1_user_id],
            invite_code="PROFILE"
        )
        await cls.insert()
        
        headers = test_vars.get_headers("instructor1")
        student_id = test_vars.student1_user_id
        
        response = await client.get(
            f"/api/v1/classes/{cls.id}/students/{student_id}",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Kiểm tra response schema
        required_fields = ["id", "full_name", "email", "enrolled_at", "progress_percent",
                          "completed_lessons", "total_lessons", "quiz_attempts",
                          "avg_quiz_score", "study_time_minutes", "learning_path"]
        assert_response_schema(data, required_fields)
    
    @pytest.mark.asyncio
    async def test_get_student_profile_not_in_class(self, client: AsyncClient, test_vars: TestVariables, test_course):
        """Test xem hồ sơ học viên không có trong lớp."""
        from models.models import Class
        cls = Class(
            name="Test Class",
            instructor_id=test_vars.instructor1_user_id,
            course_id=test_vars.course_id,
            max_students=30,
            invite_code="NOTINCLASS"
        )
        await cls.insert()
        
        headers = test_vars.get_headers("instructor1")
        student_id = test_vars.student1_user_id  # Không có trong lớp
        
        response = await client.get(
            f"/api/v1/classes/{cls.id}/students/{student_id}",
            headers=headers
        )
        
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_get_student_profile_not_instructor(self, client: AsyncClient, test_vars: TestVariables, test_course):
        """Test xem hồ sơ khi không phải instructor."""
        from models.models import Class
        cls = Class(
            name="Instructor1 Class",
            instructor_id=test_vars.instructor1_user_id,
            course_id=test_vars.course_id,
            max_students=30,
            student_ids=[test_vars.student1_user_id],
            invite_code="NOTINST2"
        )
        await cls.insert()
        
        headers = test_vars.get_headers("instructor2")
        student_id = test_vars.student1_user_id
        
        response = await client.get(
            f"/api/v1/classes/{cls.id}/students/{student_id}",
            headers=headers
        )
        
        assert response.status_code == 403


class TestRemoveStudent:
    """Test cases cho xóa học viên khỏi lớp."""
    
    @pytest.mark.asyncio
    async def test_remove_student_success(self, client: AsyncClient, test_vars: TestVariables, test_course):
        """Test xóa học viên khỏi lớp thành công."""
        from models.models import Class
        cls = Class(
            name="Test Class",
            instructor_id=test_vars.instructor1_user_id,
            course_id=test_vars.course_id,
            max_students=30,
            student_count=1,
            student_ids=[test_vars.student1_user_id],
            invite_code="REMOVE"
        )
        await cls.insert()
        
        headers = test_vars.get_headers("instructor1")
        student_id = test_vars.student1_user_id
        
        response = await client.delete(
            f"/api/v1/classes/{cls.id}/students/{student_id}",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "message" in data
    
    @pytest.mark.asyncio
    async def test_remove_student_not_instructor(self, client: AsyncClient, test_vars: TestVariables, test_course):
        """Test xóa học viên khi không phải instructor."""
        from models.models import Class
        cls = Class(
            name="Instructor1 Class",
            instructor_id=test_vars.instructor1_user_id,
            course_id=test_vars.course_id,
            max_students=30,
            student_ids=[test_vars.student1_user_id],
            invite_code="REMOVENOINST"
        )
        await cls.insert()
        
        headers = test_vars.get_headers("instructor2")
        student_id = test_vars.student1_user_id
        
        response = await client.delete(
            f"/api/v1/classes/{cls.id}/students/{student_id}",
            headers=headers
        )
        
        assert response.status_code == 403


class TestGetClassProgress:
    """Test cases cho xem tiến độ tổng thể của lớp."""
    
    @pytest.mark.asyncio
    async def test_get_class_progress_success(self, client: AsyncClient, test_vars: TestVariables, test_course):
        """Test xem tiến độ lớp học thành công."""
        from models.models import Class
        cls = Class(
            name="Test Class",
            instructor_id=test_vars.instructor1_user_id,
            course_id=test_vars.course_id,
            max_students=30,
            student_count=2,
            student_ids=[test_vars.student1_user_id, test_vars.student2_user_id],
            invite_code="PROGRESS"
        )
        await cls.insert()
        
        headers = test_vars.get_headers("instructor1")
        
        response = await client.get(f"/api/v1/classes/{cls.id}/progress", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Kiểm tra response schema
        required_fields = ["class_id", "class_name", "total_students", "avg_progress",
                          "avg_quiz_score", "completion_rate", "module_progress",
                          "student_distribution"]
        assert_response_schema(data, required_fields)
        
        # Kiểm tra metrics
        assert 0 <= data["avg_progress"] <= 100
        assert 0 <= data["avg_quiz_score"] <= 100
        assert 0 <= data["completion_rate"] <= 100
    
    @pytest.mark.asyncio
    async def test_get_class_progress_not_instructor(self, client: AsyncClient, test_vars: TestVariables, test_course):
        """Test xem tiến độ khi không phải instructor."""
        from models.models import Class
        cls = Class(
            name="Instructor1 Class",
            instructor_id=test_vars.instructor1_user_id,
            course_id=test_vars.course_id,
            max_students=30,
            invite_code="PROGRESSNOINST"
        )
        await cls.insert()
        
        headers = test_vars.get_headers("instructor2")
        
        response = await client.get(f"/api/v1/classes/{cls.id}/progress", headers=headers)
        
        assert response.status_code == 403
