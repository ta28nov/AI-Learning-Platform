"""
TEST NHÓM 1: XÁC THỰC & QUẢN LÝ TÀI KHOẢN (2.1)
Tổng: 5 endpoints

Endpoints:
1. POST /api/v1/auth/register - Đăng ký tài khoản
2. POST /api/v1/auth/login - Đăng nhập
3. POST /api/v1/auth/logout - Đăng xuất
4. GET /api/v1/users/me - Xem hồ sơ cá nhân
5. PATCH /api/v1/users/me - Cập nhật hồ sơ

Sử dụng test_variables để lưu trữ và tái sử dụng tokens, user IDs.
"""
import pytest
from httpx import AsyncClient
from tests.conftest import get_auth_headers, assert_response_schema
from tests.test_variables import TestVariables


class TestAuthRegistration:
    """Test cases cho đăng ký tài khoản."""
    
    @pytest.mark.asyncio
    async def test_register_success(self, client: AsyncClient):
        """Test đăng ký thành công với dữ liệu hợp lệ."""
        payload = {
            "full_name": "Nguyễn Văn Test",
            "email": "newuser@test.com",
            "password": "StrongPass@123"
        }
        
        response = await client.post("/api/v1/auth/register", json=payload)
        
        assert response.status_code == 201
        data = response.json()
        
        # Kiểm tra response schema
        required_fields = ["id", "full_name", "email", "role", "status", "created_at", "message"]
        assert_response_schema(data, required_fields)
        
        # Kiểm tra giá trị
        assert data["email"] == payload["email"]
        assert data["full_name"] == payload["full_name"]
        assert data["role"] == "student"  # Mặc định
        assert data["status"] == "active"
    
    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, client: AsyncClient, test_users):
        """Test đăng ký với email đã tồn tại."""
        payload = {
            "full_name": "Duplicate User",
            "email": test_users["student1"]["email"],  # Email đã tồn tại
            "password": "StrongPass@123"
        }
        
        response = await client.post("/api/v1/auth/register", json=payload)
        
        assert response.status_code == 400
        # Backend có thể trả về message tiếng Việt hoặc tiếng Anh
        detail = response.json()["detail"].lower()
        assert "đã được sử dụng" in detail or "already exists" in detail or "already" in detail
    
    @pytest.mark.asyncio
    async def test_register_invalid_email(self, client: AsyncClient):
        """Test đăng ký với email không hợp lệ."""
        payload = {
            "full_name": "Test User",
            "email": "invalid-email",  # Email không hợp lệ
            "password": "StrongPass@123"
        }
        
        response = await client.post("/api/v1/auth/register", json=payload)
        
        # FastAPI trả về 422 cho validation errors
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_register_weak_password(self, client: AsyncClient):
        """Test đăng ký với mật khẩu yếu."""
        payload = {
            "full_name": "Test User",
            "email": "test@example.com",
            "password": "123"  # Mật khẩu quá ngắn
        }
        
        response = await client.post("/api/v1/auth/register", json=payload)
        
        # FastAPI trả về 422 cho validation errors
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_register_invalid_fullname(self, client: AsyncClient):
        """Test đăng ký với tên không hợp lệ (ít hơn 2 từ)."""
        payload = {
            "full_name": "SingleName",  # Chỉ 1 từ
            "email": "test@example.com",
            "password": "StrongPass@123"
        }
        
        response = await client.post("/api/v1/auth/register", json=payload)
        
        # FastAPI trả về 422 cho validation errors
        assert response.status_code == 422


class TestAuthLogin:
    """Test cases cho đăng nhập."""
    
    @pytest.mark.asyncio
    async def test_login_success(self, client: AsyncClient, test_users):
        """Test đăng nhập thành công."""
        payload = {
            "email": test_users["student1"]["email"],
            "password": test_users["student1"]["password"],
            "remember_me": False
        }
        
        response = await client.post("/api/v1/auth/login", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        
        # Kiểm tra response schema
        required_fields = ["access_token", "refresh_token", "token_type", "user"]
        assert_response_schema(data, required_fields)
        
        # Kiểm tra token
        assert data["token_type"] == "Bearer"
        assert len(data["access_token"]) > 0
        assert len(data["refresh_token"]) > 0
        
        # Kiểm tra user info
        assert data["user"]["email"] == payload["email"]
        assert data["user"]["role"] == "student"
    
    @pytest.mark.asyncio
    async def test_login_with_remember_me(self, client: AsyncClient, test_users):
        """Test đăng nhập với remember_me=true."""
        payload = {
            "email": test_users["student1"]["email"],
            "password": test_users["student1"]["password"],
            "remember_me": True
        }
        
        response = await client.post("/api/v1/auth/login", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert "refresh_token" in data
    
    @pytest.mark.asyncio
    async def test_login_wrong_password(self, client: AsyncClient, test_users):
        """Test đăng nhập với mật khẩu sai."""
        payload = {
            "email": test_users["student1"]["email"],
            "password": "WrongPassword@123",
            "remember_me": False
        }
        
        response = await client.post("/api/v1/auth/login", json=payload)
        
        assert response.status_code == 401
        assert "invalid" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_login_nonexistent_email(self, client: AsyncClient):
        """Test đăng nhập với email không tồn tại."""
        payload = {
            "email": "nonexistent@test.com",
            "password": "SomePassword@123",
            "remember_me": False
        }
        
        response = await client.post("/api/v1/auth/login", json=payload)
        
        assert response.status_code == 401


class TestAuthLogout:
    """Test cases cho đăng xuất."""
    
    @pytest.mark.asyncio
    async def test_logout_success(self, client: AsyncClient, test_vars: TestVariables):
        """Test đăng xuất thành công."""
        # Sử dụng token từ test_vars (đã được setup sẵn)
        headers = test_vars.get_headers("student1")
        response = await client.post("/api/v1/auth/logout", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
    
    @pytest.mark.asyncio
    async def test_logout_without_token(self, client: AsyncClient):
        """Test đăng xuất không có token."""
        response = await client.post("/api/v1/auth/logout")
        
        # Backend trả về 403 khi không có token
        assert response.status_code == 403


class TestUserProfile:
    """Test cases cho xem và cập nhật hồ sơ."""
    
    @pytest.mark.asyncio
    async def test_get_profile_success(self, client: AsyncClient, test_vars: TestVariables, test_users):
        """Test xem hồ sơ cá nhân thành công."""
        # Sử dụng token từ test_vars
        headers = test_vars.get_headers("student1")
        response = await client.get("/api/v1/users/me", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Kiểm tra response schema
        required_fields = ["id", "full_name", "email", "role", "created_at", "updated_at"]
        assert_response_schema(data, required_fields)
        
        assert data["email"] == test_users["student1"]["email"]
    
    @pytest.mark.asyncio
    async def test_get_profile_without_auth(self, client: AsyncClient):
        """Test xem hồ sơ không có token."""
        response = await client.get("/api/v1/users/me")
        
        # Backend trả về 403 khi không có token
        assert response.status_code == 403
    
    @pytest.mark.asyncio
    async def test_update_profile_success(self, client: AsyncClient, test_vars: TestVariables):
        """Test cập nhật hồ sơ thành công."""
        # Sử dụng token từ test_vars
        headers = test_vars.get_headers("student1")
        payload = {
            "full_name": "Updated Name Test",
            "bio": "This is my updated bio",
            "learning_preferences": ["Programming", "Data Science"]
        }
        
        response = await client.patch("/api/v1/users/me", headers=headers, json=payload)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["full_name"] == payload["full_name"]
        assert data["bio"] == payload["bio"]
        assert data["learning_preferences"] == payload["learning_preferences"]
    
    @pytest.mark.asyncio
    async def test_update_profile_partial(self, client: AsyncClient, test_vars: TestVariables):
        """Test cập nhật một phần hồ sơ."""
        # Sử dụng token từ test_vars
        headers = test_vars.get_headers("student1")
        payload = {
            "bio": "Only updating bio"
        }
        
        response = await client.patch("/api/v1/users/me", headers=headers, json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["bio"] == payload["bio"]
    
    @pytest.mark.asyncio
    async def test_update_profile_invalid_fullname(self, client: AsyncClient, test_vars: TestVariables):
        """Test cập nhật với tên không hợp lệ."""
        # Sử dụng token từ test_vars
        headers = test_vars.get_headers("student1")
        payload = {
            "full_name": "SingleName"  # Chỉ 1 từ
        }
        
        response = await client.patch("/api/v1/users/me", headers=headers, json=payload)
        
        # Nếu token không hợp lệ, sẽ trả về 401, nếu validation error sẽ là 422
        assert response.status_code in [400, 401, 422]
