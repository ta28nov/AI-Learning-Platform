# Hướng dẫn Testing

## Cài đặt

```bash
# Activate virtual environment
.\venv\Scripts\activate  # Windows PowerShell

# Cài đặt dependencies
pip install -r requirements.txt
```

## Chạy tests

### QUAN TRỌNG: Cách chạy đúng
```bash
# Sử dụng Python từ venv (KHUYẾN NGHỊ)
.\venv\Scripts\python.exe -m pytest tests/ -v

# Hoặc sau khi activate venv
.\venv\Scripts\activate
pytest tests/ -v
```

### Chạy tất cả tests
```bash
.\venv\Scripts\python.exe -m pytest tests/ -v
```

### Chạy một file test cụ thể
```bash
.\venv\Scripts\python.exe -m pytest tests/test_01_auth_user.py -v
```

### Chạy một test cụ thể
```bash
.\venv\Scripts\python.exe -m pytest tests/test_01_auth_user.py::TestAuthRegistration::test_register_success -v
```

### Chạy tests theo nhóm
```bash
# Student tests
.\venv\Scripts\python.exe -m pytest tests/test_01_auth_user.py tests/test_02_assessment.py tests/test_03_course_enrollment.py -v

# Instructor tests
.\venv\Scripts\python.exe -m pytest tests/test_08_instructor_class.py tests/test_09_instructor_students.py tests/test_10_instructor_quiz.py -v

# Admin tests
.\venv\Scripts\python.exe -m pytest tests/test_12_admin_users.py tests/test_13_admin_courses.py tests/test_14_admin_classes.py -v
```

### Chạy với coverage
```bash
.\venv\Scripts\python.exe -m pytest tests/ --cov=. --cov-report=html
```

### Demo test_vars tự động
```bash
# Xem test_vars hoạt động như thế nào
.\venv\Scripts\python.exe -m pytest tests/demo_auto_test_vars.py -v -s
```

## Cấu trúc test files

```
tests/
├── conftest.py              # Pytest fixtures và configurations
├── test_variables.py        # Quản lý test data (tokens, IDs)
│
├── test_01_auth_user.py     # Authentication & User Profile
├── test_02_assessment.py    # AI Assessment
├── test_03_course_enrollment.py  # Course Enrollment
├── test_04_learning_progress.py  # Learning Progress
├── test_05_personal_course.py    # Personal Course
├── test_06_chatbot.py       # AI Chatbot
├── test_07_student_dashboard.py  # Student Dashboard
│
├── test_08_instructor_class.py   # Instructor Class Management
├── test_09_instructor_students.py # Instructor Student Management
├── test_10_instructor_quiz.py    # Instructor Quiz Management
├── test_11_instructor_dashboard.py # Instructor Dashboard
│
├── test_12_admin_users.py   # Admin User Management
├── test_13_admin_courses.py # Admin Course Management
├── test_14_admin_classes.py # Admin Class Management
├── test_15_admin_dashboard.py # Admin Dashboard
│
└── test_16_common_search.py # Universal Search
```

## Sử dụng test_variables

### Lấy authentication headers
```python
async def test_example(self, client: AsyncClient, test_vars: TestVariables):
    # Student
    headers = test_vars.get_headers("student1")
    
    # Instructor
    headers = test_vars.get_headers("instructor1")
    
    # Admin
    headers = test_vars.get_headers("admin")
```

### Sử dụng IDs
```python
async def test_example(self, client: AsyncClient, test_vars: TestVariables):
    # User IDs
    student_id = test_vars.student1_user_id
    instructor_id = test_vars.instructor1_user_id
    admin_id = test_vars.admin_user_id
    
    # Resource IDs
    course_id = test_vars.course_id
    module_id = test_vars.module_id
    lesson_id = test_vars.lesson_id
    enrollment_id = test_vars.enrollment_id
    class_id = test_vars.class_id
    quiz_id = test_vars.quiz_id
```

### Lưu IDs mới
```python
async def test_create_resource(self, client: AsyncClient, test_vars: TestVariables):
    headers = test_vars.get_headers("student1")
    
    response = await client.post("/api/v1/resource", headers=headers, json=payload)
    
    # Lưu ID để dùng lại
    test_vars.resource_id = response.json()["id"]
```

## Viết test mới

### Template cơ bản
```python
import pytest
from httpx import AsyncClient
from tests.conftest import assert_response_schema
from tests.test_variables import TestVariables


class TestFeatureName:
    """Test cases cho feature."""
    
    @pytest.mark.asyncio
    async def test_feature_success(self, client: AsyncClient, test_vars: TestVariables):
        """Test feature thành công."""
        headers = test_vars.get_headers("student1")
        
        response = await client.get("/api/v1/endpoint", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Kiểm tra response schema
        required_fields = ["field1", "field2"]
        assert_response_schema(data, required_fields)
```

## Fixtures có sẵn

### client
AsyncClient để gọi API

### test_vars
TestVariables instance với tokens và IDs đã setup

### test_users
Dict chứa user data (email, password) - chỉ dùng cho auth tests

### test_course
Course data với modules và lessons

### test_enrollment
Enrollment data cho student1

### test_db
Database setup/teardown

## Cấu hình Pytest

File `pytest.ini` đã được cấu hình với:
- `asyncio_mode = auto` - Tự động handle async tests
- Test discovery patterns
- Default markers và options

## Test Variables (Tự động)

Hệ thống test_vars tự động setup:
- ✅ **Tokens**: Admin, Instructor1-2, Student1-5 tự động có sẵn
- ✅ **User IDs**: Tất cả user IDs được lưu sẵn
- ✅ **Resource IDs**: Course, Module, Enrollment IDs có sẵn
- ✅ **Auto Setup**: Không cần login thủ công

```python
# Sử dụng trong test
headers = test_vars.get_headers("student1")  # Tự động có token!
user_id = test_vars.student1_user_id         # Tự động có ID!
```

## Lưu ý

1. ✅ **Luôn sử dụng `test_vars.get_headers()`** thay vì login thủ công
2. ✅ **Sử dụng `test_vars.{role}_user_id`** thay vì `test_users[role]["id"]`
3. ✅ **Lưu IDs mới vào `test_vars`** để tái sử dụng
4. ✅ **Sử dụng `assert_response_schema()`** để validate response
5. ✅ **Mỗi test phải độc lập**, không phụ thuộc vào test khác
6. ✅ **Chạy với đường dẫn đầy đủ** để tránh lỗi virtual environment

## Troubleshooting

### Lỗi pytest không tìm thấy
```
Fatal error in launcher: Unable to create process using '...python.exe'
```
**Giải pháp**: Sử dụng đường dẫn đầy đủ:
```bash
.\venv\Scripts\python.exe -m pytest tests/test_01_auth_user.py -v
```

### Lỗi async fixtures
```
'async_generator' object has no attribute 'post'
```
**Giải pháp**: Đã được khắc phục trong `pytest.ini` với `asyncio_mode = auto`

### Database connection error
Kiểm tra MongoDB đang chạy và connection string trong `.env`

### Test failed do missing data
Chạy `python scripts/init_data.py` để tạo sample data

### Import error
Đảm bảo đã cài đặt dependencies: `pip install -r requirements.txt`

### Kiểm tra môi trường
```bash
# Kiểm tra Python version
.\venv\Scripts\python.exe --version

# Kiểm tra pytest version
.\venv\Scripts\python.exe -m pytest --version

# List installed packages
.\venv\Scripts\python.exe -m pip list
```
