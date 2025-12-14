"""
TEST NHÓM 5: KHÓA HỌC CÁ NHÂN (2.5)
Tổng: 5 endpoints

Endpoints:
1. POST /api/v1/courses/from-prompt - Tạo khóa học từ AI Prompt
2. POST /api/v1/courses/personal - Tạo khóa học thủ công
3. GET /api/v1/courses/my-personal - Xem danh sách khóa học cá nhân
4. PUT /api/v1/courses/personal/{course_id} - Chỉnh sửa khóa học cá nhân
5. DELETE /api/v1/courses/personal/{course_id} - Xóa khóa học cá nhân

Sử dụng test_variables để lưu trữ personal_course_id và tái sử dụng.
"""
import pytest
from httpx import AsyncClient
from tests.conftest import assert_response_schema
from tests.test_variables import TestVariables


class TestCreateCourseFromPrompt:
    """Test cases cho tạo khóa học từ AI prompt."""
    
    @pytest.mark.asyncio
    async def test_create_course_from_prompt_success(self, client: AsyncClient, test_vars):
        """Test tạo khóa học từ AI prompt thành công."""
        headers = test_vars.get_headers("student1")
        
        payload = {
            "prompt": "Tôi muốn học lập trình Python cơ bản cho người mới bắt đầu, tập trung vào xử lý dữ liệu",
            "level": "Beginner",
            "estimated_duration_weeks": 4,
            "language": "vi"
        }
        
        response = await client.post("/api/v1/courses/from-prompt", headers=headers, json=payload)
        
        assert response.status_code == 201
        data = response.json()
        
        # Kiểm tra response schema
        required_fields = ["id", "title", "description", "category", "level", "status", 
                          "owner_id", "owner_type", "modules", "created_at"]
        assert_response_schema(data, required_fields)
        
        # Kiểm tra AI đã sinh modules và lessons
        assert data["status"] == "draft"  # Mặc định là draft
        assert data["owner_type"] == "student"
        assert len(data["modules"]) > 0  # AI phải sinh ít nhất 1 module
        
        # Kiểm tra module structure
        first_module = data["modules"][0]
        assert "title" in first_module
        assert "lessons" in first_module
        assert len(first_module["lessons"]) > 0
    
    @pytest.mark.asyncio
    async def test_create_course_from_prompt_detailed(self, client: AsyncClient, test_vars):
        """Test tạo khóa học với prompt chi tiết."""
        headers = test_vars.get_headers("student1")
        
        payload = {
            "prompt": """
            Tôi muốn học về Machine Learning cơ bản:
            - Bắt đầu với toán học cho ML (Linear Algebra, Calculus)
            - Tiếp theo là các thuật toán cơ bản (Linear Regression, Logistic Regression)
            - Cuối cùng là Neural Networks cơ bản
            Thời gian học: 8 tuần
            """,
            "level": "Intermediate",
            "estimated_duration_weeks": 8,
            "language": "vi"
        }
        
        response = await client.post("/api/v1/courses/from-prompt", headers=headers, json=payload)
        
        assert response.status_code == 201
        data = response.json()
        
        # AI nên tạo ít nhất 3 modules dựa trên prompt
        assert len(data["modules"]) >= 3
        assert data["level"] == "Intermediate"
    
    @pytest.mark.asyncio
    async def test_create_course_from_prompt_invalid_level(self, client: AsyncClient, test_vars):
        """Test tạo khóa học với level không hợp lệ."""
        headers = test_vars.get_headers("student1")
        
        payload = {
            "prompt": "Learn Python",
            "level": "InvalidLevel",  # Level không hợp lệ
            "estimated_duration_weeks": 4
        }
        
        response = await client.post("/api/v1/courses/from-prompt", headers=headers, json=payload)
        
        assert response.status_code == 400
    
    @pytest.mark.asyncio
    async def test_create_course_from_prompt_empty_prompt(self, client: AsyncClient, test_vars):
        """Test tạo khóa học với prompt rỗng."""
        headers = test_vars.get_headers("student1")
        
        payload = {
            "prompt": "",  # Prompt rỗng
            "level": "Beginner",
            "estimated_duration_weeks": 4
        }
        
        response = await client.post("/api/v1/courses/from-prompt", headers=headers, json=payload)
        
        assert response.status_code == 400
    
    @pytest.mark.asyncio
    async def test_create_course_from_prompt_without_auth(self, client: AsyncClient):
        """Test tạo khóa học không có token."""
        payload = {
            "prompt": "Learn Python",
            "level": "Beginner",
            "estimated_duration_weeks": 4
        }
        
        response = await client.post("/api/v1/courses/from-prompt", json=payload)
        
        assert response.status_code == 401


class TestCreateCourseManual:
    """Test cases cho tạo khóa học thủ công."""
    
    @pytest.mark.asyncio
    async def test_create_personal_course_success(self, client: AsyncClient, test_vars):
        """Test tạo khóa học thủ công thành công."""
        headers = test_vars.get_headers("student1")
        
        payload = {
            "title": "My Personal Python Course",
            "description": "Khóa học Python do tôi tự tạo và tổ chức nội dung",
            "category": "Programming",
            "level": "Beginner",
            "language": "vi",
            "thumbnail_url": "https://example.com/image.jpg",
            "prerequisites": ["Kiến thức máy tính cơ bản"]
        }
        
        response = await client.post("/api/v1/courses/personal", headers=headers, json=payload)
        
        assert response.status_code == 201
        data = response.json()
        
        # Kiểm tra response schema
        required_fields = ["id", "title", "description", "category", "level", "status",
                          "owner_id", "owner_type", "created_at"]
        assert_response_schema(data, required_fields)
        
        # Kiểm tra giá trị
        assert data["title"] == payload["title"]
        assert data["description"] == payload["description"]
        assert data["category"] == payload["category"]
        assert data["level"] == payload["level"]
        assert data["status"] == "draft"  # Mặc định là draft
        assert data["owner_type"] == "student"
        assert data["owner_id"] == test_vars.student1_user_id
    
    @pytest.mark.asyncio
    async def test_create_personal_course_minimal_data(self, client: AsyncClient, test_vars):
        """Test tạo khóa học với dữ liệu tối thiểu."""
        headers = test_vars.get_headers("student1")
        
        payload = {
            "title": "Minimal Course",
            "description": "Short description",
            "category": "Programming",
            "level": "Beginner"
        }
        
        response = await client.post("/api/v1/courses/personal", headers=headers, json=payload)
        
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == payload["title"]
    
    @pytest.mark.asyncio
    async def test_create_personal_course_missing_required_fields(self, client: AsyncClient, test_vars):
        """Test tạo khóa học thiếu trường bắt buộc."""
        headers = test_vars.get_headers("student1")
        
        payload = {
            "title": "Test Course"
            # Thiếu description, category, level
        }
        
        response = await client.post("/api/v1/courses/personal", headers=headers, json=payload)
        
        assert response.status_code == 400
    
    @pytest.mark.asyncio
    async def test_create_personal_course_invalid_category(self, client: AsyncClient, test_vars):
        """Test tạo khóa học với category không hợp lệ."""
        headers = test_vars.get_headers("student1")
        
        payload = {
            "title": "Test Course",
            "description": "Description",
            "category": "InvalidCategory",  # Category không hợp lệ
            "level": "Beginner"
        }
        
        response = await client.post("/api/v1/courses/personal", headers=headers, json=payload)
        
        assert response.status_code == 400
    
    @pytest.mark.asyncio
    async def test_create_personal_course_all_fields(self, client: AsyncClient, test_vars):
        """Test tạo khóa học với tất cả các trường."""
        headers = test_vars.get_headers("student1")
        
        payload = {
            "title": "Complete Personal Course",
            "description": "Full description with all fields",
            "category": "Programming",
            "level": "Intermediate",
            "language": "vi",
            "thumbnail_url": "https://example.com/thumb.jpg",
            "preview_video_url": "https://youtube.com/watch?v=example",
            "prerequisites": ["Python basics", "OOP concepts"],
            "learning_outcomes": [
                {
                    "description": "Master advanced Python",
                    "skill_tag": "python-advanced"
                }
            ]
        }
        
        response = await client.post("/api/v1/courses/personal", headers=headers, json=payload)
        
        assert response.status_code == 201
        data = response.json()
        
        assert data["language"] == "vi"
        assert len(data["prerequisites"]) == 2
        assert len(data["learning_outcomes"]) == 1


class TestListPersonalCourses:
    """Test cases cho xem danh sách khóa học cá nhân."""
    
    @pytest.mark.asyncio
    async def test_list_personal_courses_success(self, client: AsyncClient, test_vars):
        """Test xem danh sách khóa học cá nhân."""
        headers = test_vars.get_headers("student1")
        
        # Tạo 2 khóa học cá nhân trước
        for i in range(2):
            payload = {
                "title": f"Personal Course {i+1}",
                "description": f"Description {i+1}",
                "category": "Programming",
                "level": "Beginner"
            }
            await client.post("/api/v1/courses/personal", headers=headers, json=payload)
        
        # Lấy danh sách
        response = await client.get("/api/v1/courses/my-personal", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Kiểm tra response schema
        required_fields = ["courses", "total", "skip", "limit"]
        assert_response_schema(data, required_fields)
        
        # Phải có ít nhất 2 khóa học
        assert data["total"] >= 2
        assert len(data["courses"]) >= 2
        
        # Kiểm tra course structure
        course = data["courses"][0]
        course_fields = ["id", "title", "description", "category", "level", "status",
                        "total_modules", "total_lessons", "created_at"]
        assert_response_schema(course, course_fields)
    
    @pytest.mark.asyncio
    async def test_list_personal_courses_filter_by_status(self, client: AsyncClient, test_vars):
        """Test lọc khóa học theo status."""
        headers = test_vars.get_headers("student1")
        
        # Tạo khóa học draft
        payload = {
            "title": "Draft Course",
            "description": "Test",
            "category": "Programming",
            "level": "Beginner"
        }
        await client.post("/api/v1/courses/personal", headers=headers, json=payload)
        
        # Lọc theo status=draft
        response = await client.get("/api/v1/courses/my-personal?status=draft", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Tất cả courses trả về phải có status=draft
        for course in data["courses"]:
            assert course["status"] == "draft"
    
    @pytest.mark.asyncio
    async def test_list_personal_courses_pagination(self, client: AsyncClient, test_vars):
        """Test pagination."""
        headers = test_vars.get_headers("student1")
        
        response = await client.get("/api/v1/courses/my-personal?skip=0&limit=5", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["skip"] == 0
        assert data["limit"] == 5
        assert len(data["courses"]) <= 5
    
    @pytest.mark.asyncio
    async def test_list_personal_courses_empty(self, client: AsyncClient, test_vars):
        """Test xem danh sách khi chưa có khóa học nào."""
        headers = test_vars.get_headers("student3")  # Student chưa tạo course
        
        response = await client.get("/api/v1/courses/my-personal", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["total"] == 0
        assert len(data["courses"]) == 0
    
    @pytest.mark.asyncio
    async def test_list_personal_courses_without_auth(self, client: AsyncClient):
        """Test xem danh sách không có token."""
        response = await client.get("/api/v1/courses/my-personal")
        
        assert response.status_code == 401


class TestUpdatePersonalCourse:
    """Test cases cho chỉnh sửa khóa học cá nhân."""
    
    @pytest.mark.asyncio
    async def test_update_personal_course_success(self, client: AsyncClient, test_vars):
        """Test cập nhật khóa học cá nhân thành công."""
        headers = test_vars.get_headers("student1")
        
        # Tạo course trước
        create_payload = {
            "title": "Original Title",
            "description": "Original description",
            "category": "Programming",
            "level": "Beginner"
        }
        create_response = await client.post("/api/v1/courses/personal", headers=headers, json=create_payload)
        course_id = create_response.json()["id"]
        
        # Update course
        update_payload = {
            "title": "Updated Title",
            "description": "Updated description",
            "level": "Intermediate"
        }
        
        response = await client.put(
            f"/api/v1/courses/personal/{course_id}",
            headers=headers,
            json=update_payload
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Kiểm tra đã update
        assert data["title"] == "Updated Title"
        assert data["description"] == "Updated description"
        assert data["level"] == "Intermediate"
        assert "updated_at" in data
    
    @pytest.mark.asyncio
    async def test_update_personal_course_partial(self, client: AsyncClient, test_vars):
        """Test cập nhật một phần khóa học."""
        headers = test_vars.get_headers("student1")
        
        # Tạo course
        create_payload = {
            "title": "Test Course",
            "description": "Description",
            "category": "Programming",
            "level": "Beginner"
        }
        create_response = await client.post("/api/v1/courses/personal", headers=headers, json=create_payload)
        course_id = create_response.json()["id"]
        
        # Chỉ update title
        update_payload = {
            "title": "New Title Only"
        }
        
        response = await client.put(
            f"/api/v1/courses/personal/{course_id}",
            headers=headers,
            json=update_payload
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["title"] == "New Title Only"
        assert data["description"] == "Description"  # Không thay đổi
    
    @pytest.mark.asyncio
    async def test_update_personal_course_not_owner(self, client: AsyncClient, test_vars):
        """Test cập nhật khóa học của người khác."""
        # Student1 tạo course
        headers1 = test_vars.get_headers("student1")
        
        create_payload = {
            "title": "Student1 Course",
            "description": "Description",
            "category": "Programming",
            "level": "Beginner"
        }
        create_response = await client.post("/api/v1/courses/personal", headers=headers1, json=create_payload)
        course_id = create_response.json()["id"]
        
        # Student2 cố gắng update
        headers2 = test_vars.get_headers("student2")
        
        update_payload = {"title": "Hacked Title"}
        
        response = await client.put(
            f"/api/v1/courses/personal/{course_id}",
            headers=headers2,
            json=update_payload
        )
        
        assert response.status_code == 403
    
    @pytest.mark.asyncio
    async def test_update_personal_course_not_found(self, client: AsyncClient, test_vars):
        """Test cập nhật khóa học không tồn tại."""
        headers = test_vars.get_headers("student1")
        
        fake_id = "00000000-0000-0000-0000-000000000000"
        update_payload = {"title": "New Title"}
        
        response = await client.put(
            f"/api/v1/courses/personal/{fake_id}",
            headers=headers,
            json=update_payload
        )
        
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_update_personal_course_add_modules(self, client: AsyncClient, test_vars):
        """Test thêm modules vào khóa học."""
        headers = test_vars.get_headers("student1")
        
        # Tạo course
        create_payload = {
            "title": "Course with Modules",
            "description": "Description",
            "category": "Programming",
            "level": "Beginner"
        }
        create_response = await client.post("/api/v1/courses/personal", headers=headers, json=create_payload)
        course_id = create_response.json()["id"]
        
        # Thêm modules
        update_payload = {
            "modules": [
                {
                    "title": "Module 1",
                    "description": "First module",
                    "order": 1,
                    "difficulty": "Basic"
                },
                {
                    "title": "Module 2",
                    "description": "Second module",
                    "order": 2,
                    "difficulty": "Intermediate"
                }
            ]
        }
        
        response = await client.put(
            f"/api/v1/courses/personal/{course_id}",
            headers=headers,
            json=update_payload
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["total_modules"] == 2


class TestDeletePersonalCourse:
    """Test cases cho xóa khóa học cá nhân."""
    
    @pytest.mark.asyncio
    async def test_delete_personal_course_success(self, client: AsyncClient, test_vars):
        """Test xóa khóa học cá nhân thành công."""
        headers = test_vars.get_headers("student1")
        
        # Tạo course để xóa
        create_payload = {
            "title": "Course To Delete",
            "description": "Will be deleted",
            "category": "Programming",
            "level": "Beginner"
        }
        create_response = await client.post("/api/v1/courses/personal", headers=headers, json=create_payload)
        course_id = create_response.json()["id"]
        
        # Xóa course
        response = await client.delete(
            f"/api/v1/courses/personal/{course_id}",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "message" in data
        
        # Verify đã xóa - không thể get lại
        get_response = await client.get(f"/api/v1/courses/{course_id}", headers=headers)
        assert get_response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_delete_personal_course_not_owner(self, client: AsyncClient, test_vars):
        """Test xóa khóa học của người khác."""
        # Student1 tạo course
        headers1 = test_vars.get_headers("student1")
        
        create_payload = {
            "title": "Student1 Course",
            "description": "Description",
            "category": "Programming",
            "level": "Beginner"
        }
        create_response = await client.post("/api/v1/courses/personal", headers=headers1, json=create_payload)
        course_id = create_response.json()["id"]
        
        # Student2 cố gắng xóa
        headers2 = test_vars.get_headers("student2")
        
        response = await client.delete(
            f"/api/v1/courses/personal/{course_id}",
            headers=headers2
        )
        
        assert response.status_code == 403
    
    @pytest.mark.asyncio
    async def test_delete_personal_course_not_found(self, client: AsyncClient, test_vars):
        """Test xóa khóa học không tồn tại."""
        headers = test_vars.get_headers("student1")
        
        fake_id = "00000000-0000-0000-0000-000000000000"
        
        response = await client.delete(
            f"/api/v1/courses/personal/{fake_id}",
            headers=headers
        )
        
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_delete_personal_course_without_auth(self, client: AsyncClient, test_vars):
        """Test xóa khóa học không có token."""
        # Tạo course trước
        headers = test_vars.get_headers("student1")
        
        create_payload = {
            "title": "Test Course",
            "description": "Description",
            "category": "Programming",
            "level": "Beginner"
        }
        create_response = await client.post("/api/v1/courses/personal", headers=headers, json=create_payload)
        course_id = create_response.json()["id"]
        
        # Xóa không có token
        response = await client.delete(f"/api/v1/courses/personal/{course_id}")
        
        assert response.status_code == 401
