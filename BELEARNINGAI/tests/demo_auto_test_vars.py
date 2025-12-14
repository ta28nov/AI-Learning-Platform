"""
DEMO: Test_vars TỰ ĐỘNG - Không cần khai báo!
Chạy file này để xem test_vars hoạt động như thế nào.

Command: pytest tests/demo_auto_test_vars.py -v -s
"""

import pytest
from httpx import AsyncClient


class TestAutoTestVars:
    """Demo test_vars tự động."""
    
    @pytest.mark.asyncio
    async def test_auto_student_token(self, client: AsyncClient, test_vars):
        """Test 1: Lấy token student tự động."""
        print("\n" + "="*60)
        print("TEST 1: Student Token")
        print("="*60)
        
        # Lấy headers - TỰ ĐỘNG có token!
        headers = test_vars.get_headers("student1")
        print(f"✅ Headers: {headers}")
        
        # Call API
        response = await client.get("/api/v1/users/me", headers=headers)
        print(f"✅ Status: {response.status_code}")
        print(f"✅ Response: {response.json()}")
        
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_auto_instructor_token(self, client: AsyncClient, test_vars):
        """Test 2: Lấy token instructor tự động."""
        print("\n" + "="*60)
        print("TEST 2: Instructor Token")
        print("="*60)
        
        headers = test_vars.get_headers("instructor1")
        print(f"✅ Headers: {headers}")
        
        response = await client.get("/api/v1/classes/my-classes", headers=headers)
        print(f"✅ Status: {response.status_code}")
        
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_auto_admin_token(self, client: AsyncClient, test_vars):
        """Test 3: Lấy token admin tự động."""
        print("\n" + "="*60)
        print("TEST 3: Admin Token")
        print("="*60)
        
        headers = test_vars.get_headers("admin")
        print(f"✅ Headers: {headers}")
        
        response = await client.get("/api/v1/admin/users", headers=headers)
        print(f"✅ Status: {response.status_code}")
        
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_auto_course_id(self, client: AsyncClient, test_vars):
        """Test 4: Sử dụng course_id có sẵn."""
        print("\n" + "="*60)
        print("TEST 4: Course ID có sẵn")
        print("="*60)
        
        print(f"✅ Course ID: {test_vars.course_id}")
        print(f"✅ Module ID: {test_vars.module_id}")
        print(f"✅ Enrollment ID: {test_vars.enrollment_id}")
        
        headers = test_vars.get_headers("student1")
        response = await client.get(f"/api/v1/courses/{test_vars.course_id}", headers=headers)
        
        print(f"✅ Status: {response.status_code}")
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_save_and_reuse_id(self, client: AsyncClient, test_vars):
        """Test 5: Lưu và sử dụng lại ID."""
        print("\n" + "="*60)
        print("TEST 5: Lưu và reuse ID")
        print("="*60)
        
        headers = test_vars.get_headers("student1")
        
        # Tạo personal course
        payload = {
            "title": "Demo Course",
            "description": "Test course for demo",
            "category": "Programming",
            "level": "Beginner"
        }
        response = await client.post("/api/v1/courses/personal", headers=headers, json=payload)
        
        if response.status_code == 201:
            # Lưu ID
            test_vars.personal_course_id = response.json()["id"]
            print(f"✅ Created personal course: {test_vars.personal_course_id}")
            
            # Sử dụng lại
            response2 = await client.get(
                f"/api/v1/courses/personal/{test_vars.personal_course_id}",
                headers=headers
            )
            print(f"✅ Retrieved course: {response2.status_code}")
            assert response2.status_code == 200
        else:
            print(f"⚠️  Could not create course: {response.status_code}")
    
    @pytest.mark.asyncio
    async def test_all_variables(self, test_vars):
        """Test 6: Xem tất cả variables."""
        print("\n" + "="*60)
        print("TEST 6: Tất cả Variables")
        print("="*60)
        
        import json
        all_vars = test_vars.to_dict()
        print(json.dumps(all_vars, indent=2, default=str))
        
        # Verify có đủ tokens
        assert test_vars.admin_token is not None
        assert test_vars.student1_token is not None
        assert test_vars.instructor1_token is not None
        
        print("\n✅ All tokens are available!")


# Test function (không phải class)
@pytest.mark.asyncio
async def test_function_style(client: AsyncClient, test_vars):
    """Demo: Test function cũng dùng được test_vars."""
    print("\n" + "="*60)
    print("FUNCTION TEST: test_vars cũng hoạt động!")
    print("="*60)
    
    headers = test_vars.get_headers("student1")
    response = await client.get("/api/v1/users/me", headers=headers)
    
    print(f"✅ Status: {response.status_code}")
    assert response.status_code == 200
