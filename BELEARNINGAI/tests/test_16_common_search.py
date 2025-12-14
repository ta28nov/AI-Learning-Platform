"""
TEST NHÓM 16: TÌM KIẾM CHUNG (5.1)
Tổng: 1 endpoint

Endpoints (theo CHUCNANG.md):
1. GET /api/v1/search - Tìm kiếm thông minh với filter nâng cao

Sử dụng test_variables để quản lý search operations.
"""
import pytest
from httpx import AsyncClient
from tests.conftest import assert_response_schema
from tests.test_variables import TestVariables


class TestUniversalSearch:
    """Test cases cho tìm kiếm thông minh toàn hệ thống."""
    
    @pytest.mark.asyncio
    async def test_search_basic_success(self, client: AsyncClient, test_vars, test_course):
        """Test tìm kiếm cơ bản."""
        headers = test_vars.get_headers("student1")
        
        response = await client.get("/api/v1/search?q=Python", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Kiểm tra response schema theo CHUCNANG.md
        required_fields = ["results", "total", "query", "categories"]
        assert_response_schema(data, required_fields)
        
        # Kiểm tra results được nhóm theo category
        assert isinstance(data["results"], dict)
        
        # Có thể có courses, users, classes, modules, lessons
        if "courses" in data["results"]:
            courses = data["results"]["courses"]
            assert isinstance(courses, list)
            if len(courses) > 0:
                course = courses[0]
                assert "id" in course
                assert "title" in course
                assert "relevance_score" in course
    
    @pytest.mark.asyncio
    async def test_search_filter_by_category(self, client: AsyncClient, test_vars):
        """Test tìm kiếm với filter category."""
        headers = test_vars.get_headers("student1")
        
        response = await client.get("/api/v1/search?q=Python&category=Programming", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Kết quả phải liên quan đến category Programming
        if "courses" in data["results"]:
            for course in data["results"]["courses"]:
                assert course["category"] == "Programming"
    
    @pytest.mark.asyncio
    async def test_search_filter_by_level(self, client: AsyncClient, test_vars):
        """Test tìm kiếm với filter level."""
        headers = test_vars.get_headers("student1")
        
        response = await client.get("/api/v1/search?q=Python&level=Beginner", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        if "courses" in data["results"]:
            for course in data["results"]["courses"]:
                assert course["level"] == "Beginner"
    
    @pytest.mark.asyncio
    async def test_search_filter_by_rating(self, client: AsyncClient, test_vars):
        """Test tìm kiếm với filter rating."""
        headers = test_vars.get_headers("student1")
        
        response = await client.get("/api/v1/search?q=Python&rating=4.5", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        if "courses" in data["results"]:
            for course in data["results"]["courses"]:
                if "avg_rating" in course:
                    assert course["avg_rating"] >= 4.5
    
    @pytest.mark.asyncio
    async def test_search_filter_by_instructor(self, client: AsyncClient, test_vars: TestVariables):
        """Test tìm kiếm với filter instructor."""
        headers = test_vars.get_headers("student1")
        instructor_id = test_vars.instructor1_user_id
        
        response = await client.get(f"/api/v1/search?q=Python&instructor={instructor_id}", headers=headers)
        
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_search_with_typo_tolerance(self, client: AsyncClient, test_vars):
        """Test tìm kiếm với typo (sai chính tả)."""
        headers = test_vars.get_headers("student1")
        
        # Tìm "Pyton" thay vì "Python"
        response = await client.get("/api/v1/search?q=Pyton", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Vẫn có thể tìm thấy kết quả hoặc có suggestions
        assert "results" in data or "suggestions" in data
    
    @pytest.mark.asyncio
    async def test_search_with_suggestions(self, client: AsyncClient, test_vars):
        """Test tìm kiếm với suggestions."""
        headers = test_vars.get_headers("student1")
        
        response = await client.get("/api/v1/search?q=Py&suggestions=true", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Có thể có suggestions
        if "suggestions" in data:
            assert isinstance(data["suggestions"], list)
    
    @pytest.mark.asyncio
    async def test_search_empty_query(self, client: AsyncClient, test_vars):
        """Test tìm kiếm với query rỗng."""
        headers = test_vars.get_headers("student1")
        
        response = await client.get("/api/v1/search?q=", headers=headers)
        
        # Có thể trả về 400 hoặc 200 với empty results
        assert response.status_code in [200, 400]
    
    @pytest.mark.asyncio
    async def test_search_no_results(self, client: AsyncClient, test_vars):
        """Test tìm kiếm không có kết quả."""
        headers = test_vars.get_headers("student1")
        
        response = await client.get("/api/v1/search?q=NonExistentCourse12345", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["total"] == 0
        # Có thể có suggestions cho từ khóa tương tự
        if "suggestions" in data:
            assert isinstance(data["suggestions"], list)
    
    @pytest.mark.asyncio
    async def test_search_pagination(self, client: AsyncClient, test_vars):
        """Test pagination trong kết quả tìm kiếm."""
        headers = test_vars.get_headers("student1")
        
        response = await client.get("/api/v1/search?q=Python&skip=0&limit=5", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Kiểm tra pagination params
        if "skip" in data and "limit" in data:
            assert data["skip"] == 0
            assert data["limit"] == 5
    
    @pytest.mark.asyncio
    async def test_search_sort_by_relevance(self, client: AsyncClient, test_vars):
        """Test sắp xếp theo độ liên quan."""
        headers = test_vars.get_headers("student1")
        
        response = await client.get("/api/v1/search?q=Python&sort=relevance", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Kết quả phải có relevance_score và được sắp xếp
        if "courses" in data["results"] and len(data["results"]["courses"]) > 1:
            courses = data["results"]["courses"]
            for i in range(len(courses) - 1):
                assert courses[i]["relevance_score"] >= courses[i+1]["relevance_score"]
    
    @pytest.mark.asyncio
    async def test_search_multiple_types(self, client: AsyncClient, test_vars):
        """Test tìm kiếm nhiều loại đối tượng."""
        headers = test_vars.get_headers("student1")
        
        response = await client.get("/api/v1/search?q=Python&types=courses,modules,lessons", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Kết quả có thể có nhiều categories
        results = data["results"]
        assert isinstance(results, dict)
    
    @pytest.mark.asyncio
    async def test_search_without_auth(self, client: AsyncClient):
        """Test tìm kiếm không cần authentication (public search)."""
        # Tìm kiếm public courses không cần đăng nhập
        response = await client.get("/api/v1/search?q=Python")
        
        # Có thể cho phép search public content hoặc yêu cầu auth
        assert response.status_code in [200, 401]
    
    @pytest.mark.asyncio
    async def test_search_admin_can_search_users(self, client: AsyncClient, test_vars):
        """Test admin có thể tìm kiếm users."""
        headers = test_vars.get_headers("admin")
        
        response = await client.get("/api/v1/search?q=student&types=users", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Admin có thể tìm users
        if "users" in data["results"]:
            assert isinstance(data["results"]["users"], list)
    
    @pytest.mark.asyncio
    async def test_search_student_cannot_search_users(self, client: AsyncClient, test_vars):
        """Test student không thể tìm kiếm users."""
        headers = test_vars.get_headers("student1")
        
        response = await client.get("/api/v1/search?q=student&types=users", headers=headers)
        
        # Có thể trả về 403 hoặc 200 nhưng không có users trong results
        if response.status_code == 200:
            data = response.json()
            assert "users" not in data["results"] or len(data["results"]["users"]) == 0
        else:
            assert response.status_code == 403
    
    @pytest.mark.asyncio
    async def test_search_combined_filters(self, client: AsyncClient, test_vars):
        """Test tìm kiếm với nhiều filters kết hợp."""
        headers = test_vars.get_headers("student1")
        
        response = await client.get(
            "/api/v1/search?q=Python&category=Programming&level=Beginner&rating=4.0",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Kết quả phải thỏa mãn tất cả filters
        if "courses" in data["results"]:
            for course in data["results"]["courses"]:
                assert course["category"] == "Programming"
                assert course["level"] == "Beginner"
                if "avg_rating" in course:
                    assert course["avg_rating"] >= 4.0
