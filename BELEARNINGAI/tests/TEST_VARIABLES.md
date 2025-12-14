# Test Variables Guide

## Giới thiệu

`test_variables.py` là module quản lý tập trung tất cả tokens và IDs cho testing.

## Sử dụng cơ bản

### Import
```python
from tests.test_variables import TestVariables
```

### Lấy headers
```python
async def test_example(self, client: AsyncClient, test_vars: TestVariables):
    # Student
    headers = test_vars.get_headers("student1")
    headers = test_vars.get_headers("student2")
    headers = test_vars.get_headers("student3")
    
    # Instructor
    headers = test_vars.get_headers("instructor1")
    headers = test_vars.get_headers("instructor2")
    
    # Admin
    headers = test_vars.get_headers("admin")
```

### Sử dụng User IDs
```python
# Student IDs
student1_id = test_vars.student1_user_id
student2_id = test_vars.student2_user_id
student3_id = test_vars.student3_user_id

# Instructor IDs
instructor1_id = test_vars.instructor1_user_id
instructor2_id = test_vars.instructor2_user_id

# Admin ID
admin_id = test_vars.admin_user_id
```

### Sử dụng Resource IDs
```python
# Course data
course_id = test_vars.course_id
module_id = test_vars.module_id
lesson_id = test_vars.lesson_id

# Enrollment
enrollment_id = test_vars.enrollment_id

# Class
class_id = test_vars.class_id
invite_code = test_vars.invite_code

# Quiz
quiz_id = test_vars.quiz_id

# Personal course
personal_course_id = test_vars.personal_course_id

# Assessment
session_id = test_vars.assessment_session_id

# Chatbot
conversation_id = test_vars.conversation_id
```

### Lưu IDs mới
```python
async def test_create(self, client: AsyncClient, test_vars: TestVariables):
    headers = test_vars.get_headers("student1")
    
    response = await client.post("/api/v1/courses", headers=headers, json=payload)
    
    # Lưu để dùng lại
    test_vars.course_id = response.json()["id"]
```

## Pattern chuẩn

### Thay vì
```python
# KHÔNG NÊN
login_payload = {
    "email": test_users["student1"]["email"],
    "password": test_users["student1"]["password"]
}
response = await client.post("/api/v1/auth/login", json=login_payload)
token = response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}
```

### Sử dụng
```python
# NÊN
headers = test_vars.get_headers("student1")
```

### Thay vì
```python
# KHÔNG NÊN
user_id = test_users["student1"]["id"]
```

### Sử dụng
```python
# NÊN
user_id = test_vars.student1_user_id
```

## Lưu ý

1. `test_vars` tự động inject vào test classes qua fixture
2. Không cần gọi `setup()` thủ công, đã tự động
3. Tokens được cache, không cần login lại
4. IDs được share giữa các tests trong cùng session
5. Mỗi test function nhận `test_vars` mới nhưng data giống nhau

## Ví dụ hoàn chỉnh

```python
import pytest
from httpx import AsyncClient
from tests.conftest import assert_response_schema
from tests.test_variables import TestVariables


class TestExample:
    @pytest.mark.asyncio
    async def test_student_action(self, client: AsyncClient, test_vars: TestVariables):
        # Lấy headers
        headers = test_vars.get_headers("student1")
        
        # Sử dụng IDs
        course_id = test_vars.course_id
        
        # Gọi API
        response = await client.get(f"/api/v1/courses/{course_id}", headers=headers)
        
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_instructor_action(self, client: AsyncClient, test_vars: TestVariables):
        headers = test_vars.get_headers("instructor1")
        instructor_id = test_vars.instructor1_user_id
        
        payload = {"instructor_id": instructor_id}
        response = await client.post("/api/v1/classes", headers=headers, json=payload)
        
        # Lưu class_id
        test_vars.class_id = response.json()["id"]
        
        assert response.status_code == 201
    
    @pytest.mark.asyncio
    async def test_admin_action(self, client: AsyncClient, test_vars: TestVariables):
        headers = test_vars.get_headers("admin")
        
        response = await client.get("/api/v1/admin/users", headers=headers)
        
        assert response.status_code == 200
```
