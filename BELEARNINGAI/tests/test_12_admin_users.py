"""
TEST NHÓM 12: QUẢN LÝ NGƯỜI DÙNG CỦA ADMIN (4.1)
Tổng: 7 endpoints

Endpoints (theo CHUCNANG.md):
1. GET /api/v1/admin/users - Xem danh sách người dùng
2. GET /api/v1/admin/users/{user_id} - Xem hồ sơ người dùng chi tiết
3. POST /api/v1/admin/users - Tạo tài khoản người dùng
4. PUT /api/v1/admin/users/{user_id} - Cập nhật thông tin người dùng
5. DELETE /api/v1/admin/users/{user_id} - Xóa người dùng
6. PUT /api/v1/admin/users/{user_id}/role - Thay đổi vai trò người dùng
7. POST /api/v1/admin/users/{user_id}/reset-password - Reset mật khẩu người dùng

Sử dụng test_variables để quản lý admin operations và user IDs.
"""
import pytest
from httpx import AsyncClient
from tests.conftest import assert_response_schema
from tests.test_variables import TestVariables


class TestAdminListUsers:
    """Test cases cho xem danh sách người dùng."""
    
    @pytest.mark.asyncio
    async def test_list_users_success(self, client: AsyncClient, test_vars: TestVariables):
        """Test admin xem danh sách tất cả người dùng."""
        headers = test_vars.get_headers("admin")
        
        response = await client.get("/api/v1/admin/users", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Kiểm tra response schema theo CHUCNANG.md
        required_fields = ["users", "total", "skip", "limit"]
        assert_response_schema(data, required_fields)
        
        # Phải có ít nhất 8 users (1 admin + 2 instructors + 5 students)
        assert data["total"] >= 8
        
        # Kiểm tra user structure
        user = data["users"][0]
        user_fields = ["id", "full_name", "email", "role", "status", "created_at"]
        assert_response_schema(user, user_fields)
    
    @pytest.mark.asyncio
    async def test_list_users_filter_by_role(self, client: AsyncClient, test_vars: TestVariables):
        """Test lọc người dùng theo vai trò."""
        headers = test_vars.get_headers("admin")
        
        response = await client.get("/api/v1/admin/users?role=student", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Tất cả users trả về phải là student
        for user in data["users"]:
            assert user["role"] == "student"
    
    @pytest.mark.asyncio
    async def test_list_users_filter_by_status(self, client: AsyncClient, test_vars: TestVariables):
        """Test lọc người dùng theo trạng thái."""
        headers = test_vars.get_headers("admin")
        
        response = await client.get("/api/v1/admin/users?status=active", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        for user in data["users"]:
            assert user["status"] == "active"
    
    @pytest.mark.asyncio
    async def test_list_users_search_by_email(self, client: AsyncClient, test_vars: TestVariables, test_users):
        """Test tìm kiếm người dùng theo email."""
        headers = test_vars.get_headers("admin")
        
        response = await client.get(f"/api/v1/admin/users?search={test_users['student1']['email']}", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Phải tìm thấy student1
        assert any(user["email"] == test_users["student1"]["email"] for user in data["users"])
    
    @pytest.mark.asyncio
    async def test_list_users_pagination(self, client: AsyncClient, test_vars: TestVariables):
        """Test pagination."""
        headers = test_vars.get_headers("admin")
        
        response = await client.get("/api/v1/admin/users?skip=0&limit=5", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["skip"] == 0
        assert data["limit"] == 5
        assert len(data["users"]) <= 5
    
    @pytest.mark.asyncio
    async def test_list_users_non_admin(self, client: AsyncClient, test_vars: TestVariables):
        """Test non-admin không thể xem danh sách users."""
        headers = test_vars.get_headers("student1")
        
        response = await client.get("/api/v1/admin/users", headers=headers)
        
        assert response.status_code == 403


class TestAdminGetUserDetail:
    """Test cases cho xem hồ sơ người dùng chi tiết."""
    
    @pytest.mark.asyncio
    async def test_get_user_detail_success(self, client: AsyncClient, test_vars: TestVariables):
        """Test xem chi tiết người dùng."""
        headers = test_vars.get_headers("admin")
        user_id = test_vars.student1_user_id
        
        response = await client.get(f"/api/v1/admin/users/{user_id}", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Kiểm tra response schema theo CHUCNANG.md
        required_fields = ["id", "full_name", "email", "role", "status", "bio",
                          "learning_preferences", "statistics", "created_at"]
        assert_response_schema(data, required_fields)
        
        # Kiểm tra statistics
        stats = data["statistics"]
        assert "courses_enrolled" in stats or "classes_teaching" in stats
    
    @pytest.mark.asyncio
    async def test_get_user_detail_not_found(self, client: AsyncClient, test_vars: TestVariables):
        """Test xem user không tồn tại."""
        headers = test_vars.get_headers("admin")
        fake_id = "00000000-0000-0000-0000-000000000000"
        
        response = await client.get(f"/api/v1/admin/users/{fake_id}", headers=headers)
        
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_get_user_detail_non_admin(self, client: AsyncClient, test_vars: TestVariables):
        """Test non-admin không thể xem chi tiết user."""
        headers = test_vars.get_headers("instructor1")
        user_id = test_vars.student1_user_id
        
        response = await client.get(f"/api/v1/admin/users/{user_id}", headers=headers)
        
        assert response.status_code == 403


class TestAdminCreateUser:
    """Test cases cho tạo tài khoản người dùng."""
    
    @pytest.mark.asyncio
    async def test_create_student_success(self, client: AsyncClient, test_vars: TestVariables):
        """Test tạo tài khoản student thành công."""
        headers = test_vars.get_headers("admin")
        
        payload = {
            "full_name": "Học Viên Mới",
            "email": "newstudent@test.com",
            "role": "student"
            # Không cần password - hệ thống sẽ gửi email kích hoạt
        }
        
        response = await client.post("/api/v1/admin/users", headers=headers, json=payload)
        
        assert response.status_code == 201
        data = response.json()
        
        required_fields = ["id", "full_name", "email", "role", "status", "message"]
        assert_response_schema(data, required_fields)
        
        assert data["email"] == payload["email"]
        assert data["role"] == "student"
        assert data["status"] == "active"
    
    @pytest.mark.asyncio
    async def test_create_instructor_with_password(self, client: AsyncClient, test_vars: TestVariables):
        """Test tạo tài khoản instructor với password."""
        headers = test_vars.get_headers("admin")
        
        payload = {
            "full_name": "Giảng Viên Mới",
            "email": "newinstructor@test.com",
            "role": "instructor",
            "password": "Instructor@123"  # Bắt buộc cho instructor/admin
        }
        
        response = await client.post("/api/v1/admin/users", headers=headers, json=payload)
        
        assert response.status_code == 201
        data = response.json()
        
        assert data["role"] == "instructor"
    
    @pytest.mark.asyncio
    async def test_create_admin_success(self, client: AsyncClient, test_vars: TestVariables):
        """Test tạo tài khoản admin."""
        headers = test_vars.get_headers("admin")
        
        payload = {
            "full_name": "Admin Mới",
            "email": "newadmin@test.com",
            "role": "admin",
            "password": "Admin@12345"
        }
        
        response = await client.post("/api/v1/admin/users", headers=headers, json=payload)
        
        assert response.status_code == 201
        data = response.json()
        
        assert data["role"] == "admin"
    
    @pytest.mark.asyncio
    async def test_create_user_duplicate_email(self, client: AsyncClient, test_vars: TestVariables, test_users):
        """Test tạo user với email đã tồn tại."""
        headers = test_vars.get_headers("admin")
        
        payload = {
            "full_name": "Duplicate User",
            "email": test_users["student1"]["email"],  # Email đã tồn tại
            "role": "student"
        }
        
        response = await client.post("/api/v1/admin/users", headers=headers, json=payload)
        
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_create_user_invalid_role(self, client: AsyncClient, test_vars: TestVariables):
        """Test tạo user với role không hợp lệ."""
        headers = test_vars.get_headers("admin")
        
        payload = {
            "full_name": "Test User",
            "email": "test@test.com",
            "role": "invalid_role"
        }
        
        response = await client.post("/api/v1/admin/users", headers=headers, json=payload)
        
        assert response.status_code == 400


class TestAdminUpdateUser:
    """Test cases cho cập nhật thông tin người dùng."""
    
    @pytest.mark.asyncio
    async def test_update_user_success(self, client: AsyncClient, test_vars: TestVariables):
        """Test cập nhật thông tin user thành công."""
        headers = test_vars.get_headers("admin")
        user_id = test_vars.student1_user_id
        
        payload = {
            "full_name": "Tên Đã Cập Nhật",
            "email": "updated@test.com"
        }
        
        response = await client.put(f"/api/v1/admin/users/{user_id}", headers=headers, json=payload)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["full_name"] == payload["full_name"]
        assert data["email"] == payload["email"]
    
    @pytest.mark.asyncio
    async def test_update_user_partial(self, client: AsyncClient, test_vars: TestVariables):
        """Test cập nhật một phần thông tin."""
        headers = test_vars.get_headers("admin")
        user_id = test_vars.student1_user_id
        
        payload = {
            "full_name": "Chỉ Đổi Tên"
        }
        
        response = await client.put(f"/api/v1/admin/users/{user_id}", headers=headers, json=payload)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["full_name"] == payload["full_name"]
    
    @pytest.mark.asyncio
    async def test_update_user_not_found(self, client: AsyncClient, test_vars: TestVariables):
        """Test cập nhật user không tồn tại."""
        headers = test_vars.get_headers("admin")
        fake_id = "00000000-0000-0000-0000-000000000000"
        
        payload = {"full_name": "Test"}
        
        response = await client.put(f"/api/v1/admin/users/{fake_id}", headers=headers, json=payload)
        
        assert response.status_code == 404


class TestAdminDeleteUser:
    """Test cases cho xóa người dùng."""
    
    @pytest.mark.asyncio
    async def test_delete_user_success(self, client: AsyncClient, test_vars: TestVariables):
        """Test xóa user thành công."""
        # Tạo user mới để xóa
        from models.models import User
        from utils.security import hash_password
        
        user = User(
            full_name="User To Delete",
            email="todelete@test.com",
            hashed_password=hash_password("Pass@123"),
            role="student",
            status="active"
        )
        await user.insert()
        
        headers = test_vars.get_headers("admin")
        
        response = await client.delete(f"/api/v1/admin/users/{user.id}", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "message" in data
    
    @pytest.mark.asyncio
    async def test_delete_user_with_dependencies(self, client: AsyncClient, test_vars: TestVariables, test_enrollment):
        """Test xóa user có dependencies (đang học khóa học)."""
        headers = test_vars.get_headers("admin")
        user_id = test_vars.student1_user_id  # Có enrollment
        
        response = await client.delete(f"/api/v1/admin/users/{user_id}", headers=headers)
        
        # Có thể trả về 400 với warning hoặc 200 với impact analysis
        assert response.status_code in [200, 400]
        
        if response.status_code == 200:
            data = response.json()
            assert "warning" in data or "impact" in data
    
    @pytest.mark.asyncio
    async def test_delete_user_not_found(self, client: AsyncClient, test_vars: TestVariables):
        """Test xóa user không tồn tại."""
        headers = test_vars.get_headers("admin")
        fake_id = "00000000-0000-0000-0000-000000000000"
        
        response = await client.delete(f"/api/v1/admin/users/{fake_id}", headers=headers)
        
        assert response.status_code == 404


class TestAdminChangeUserRole:
    """Test cases cho thay đổi vai trò người dùng."""
    
    @pytest.mark.asyncio
    async def test_change_role_student_to_instructor(self, client: AsyncClient, test_vars: TestVariables):
        """Test nâng cấp student lên instructor."""
        headers = test_vars.get_headers("admin")
        user_id = test_vars.student1_user_id
        
        payload = {
            "role": "instructor"
        }
        
        response = await client.put(f"/api/v1/admin/users/{user_id}/role", headers=headers, json=payload)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["role"] == "instructor"
        assert "message" in data
    
    @pytest.mark.asyncio
    async def test_change_role_instructor_to_student(self, client: AsyncClient, test_vars: TestVariables):
        """Test hạ cấp instructor xuống student."""
        headers = test_vars.get_headers("admin")
        user_id = test_vars.instructor1_user_id
        
        payload = {
            "role": "student"
        }
        
        response = await client.put(f"/api/v1/admin/users/{user_id}/role", headers=headers, json=payload)
        
        # Có thể có warning nếu instructor đang dạy lớp
        assert response.status_code in [200, 400]
    
    @pytest.mark.asyncio
    async def test_change_role_to_admin(self, client: AsyncClient, test_vars: TestVariables):
        """Test nâng cấp lên admin."""
        headers = test_vars.get_headers("admin")
        user_id = test_vars.student1_user_id
        
        payload = {
            "role": "admin"
        }
        
        response = await client.put(f"/api/v1/admin/users/{user_id}/role", headers=headers, json=payload)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["role"] == "admin"
    
    @pytest.mark.asyncio
    async def test_change_role_invalid(self, client: AsyncClient, test_vars: TestVariables):
        """Test thay đổi sang role không hợp lệ."""
        headers = test_vars.get_headers("admin")
        user_id = test_vars.student1_user_id
        
        payload = {
            "role": "invalid_role"
        }
        
        response = await client.put(f"/api/v1/admin/users/{user_id}/role", headers=headers, json=payload)
        
        assert response.status_code == 400


class TestAdminResetPassword:
    """Test cases cho reset mật khẩu người dùng."""
    
    @pytest.mark.asyncio
    async def test_reset_password_success(self, client: AsyncClient, test_vars: TestVariables):
        """Test reset mật khẩu thành công."""
        headers = test_vars.get_headers("admin")
        user_id = test_vars.student1_user_id
        
        response = await client.post(f"/api/v1/admin/users/{user_id}/reset-password", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        required_fields = ["message", "user_id"]
        assert_response_schema(data, required_fields)
        
        # Có thể trả về temporary password hoặc reset link
        assert "temporary_password" in data or "reset_link" in data or "email_sent" in data
    
    @pytest.mark.asyncio
    async def test_reset_password_not_found(self, client: AsyncClient, test_vars: TestVariables):
        """Test reset password cho user không tồn tại."""
        headers = test_vars.get_headers("admin")
        fake_id = "00000000-0000-0000-0000-000000000000"
        
        response = await client.post(f"/api/v1/admin/users/{fake_id}/reset-password", headers=headers)
        
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_reset_password_non_admin(self, client: AsyncClient, test_vars: TestVariables):
        """Test non-admin không thể reset password."""
        headers = test_vars.get_headers("instructor1")
        user_id = test_vars.student1_user_id
        
        response = await client.post(f"/api/v1/admin/users/{user_id}/reset-password", headers=headers)
        
        assert response.status_code == 403
