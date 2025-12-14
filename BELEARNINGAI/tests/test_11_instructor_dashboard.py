"""
TEST NHÓM 11: DASHBOARD GIẢNG VIÊN (3.4)
Tổng: 4 endpoints

Endpoints (theo CHUCNANG.md):
1. GET /api/v1/dashboard/instructor - Dashboard tổng quan giảng viên
2. GET /api/v1/analytics/instructor/classes - Thống kê lớp học chi tiết
3. GET /api/v1/analytics/instructor/progress-chart - Biểu đồ tiến độ học viên
4. GET /api/v1/analytics/instructor/quiz-performance - Phân tích hiệu quả quiz

Sử dụng test_variables để quản lý instructor data và analytics.
"""
import pytest
from httpx import AsyncClient
from datetime import datetime, timezone, timedelta
from tests.conftest import assert_response_schema
from tests.test_variables import TestVariables


class TestInstructorDashboard:
    """Test cases cho dashboard tổng quan giảng viên."""
    
    @pytest.mark.asyncio
    async def test_get_instructor_dashboard_success(self, client: AsyncClient, test_vars: TestVariables, test_course):
        """Test xem dashboard giảng viên thành công."""
        # Tạo một số lớp học cho instructor
        from models.models import Class
        for i in range(2):
            cls = Class(
                name=f"Class {i+1}",
                instructor_id=test_vars.instructor1_user_id,
                course_id=test_vars.course_id,
                max_students=30,
                student_count=10 + i*5,
                status="active",
                invite_code=f"DASH{i+1}"
            )
            await cls.insert()
        
        headers = test_vars.get_headers("instructor1")
        
        response = await client.get("/api/v1/dashboard/instructor", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Kiểm tra response schema theo CHUCNANG.md
        required_fields = ["active_classes", "total_students", "quizzes_created",
                          "avg_completion_rate", "quick_actions"]
        assert_response_schema(data, required_fields)
        
        # Kiểm tra metrics
        assert data["active_classes"] >= 2
        assert data["total_students"] >= 25  # 10 + 15
        assert data["quizzes_created"] >= 0
        assert 0 <= data["avg_completion_rate"] <= 100
        
        # Kiểm tra quick_actions
        assert "quick_actions" in data
        actions = data["quick_actions"]
        assert "create_class" in actions
        assert "create_quiz" in actions
    
    @pytest.mark.asyncio
    async def test_get_instructor_dashboard_new_instructor(self, client: AsyncClient, test_vars: TestVariables):
        """Test dashboard cho instructor mới chưa có dữ liệu."""
        headers = test_vars.get_headers("instructor2")  # Instructor chưa tạo lớp
        
        response = await client.get("/api/v1/dashboard/instructor", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Metrics phải = 0
        assert data["active_classes"] == 0
        assert data["total_students"] == 0
        assert data["quizzes_created"] == 0
    
    @pytest.mark.asyncio
    async def test_get_instructor_dashboard_wrong_role(self, client: AsyncClient, test_vars: TestVariables):
        """Test student cố gắng xem instructor dashboard."""
        headers = test_vars.get_headers("student1")
        
        response = await client.get("/api/v1/dashboard/instructor", headers=headers)
        
        assert response.status_code == 403


class TestInstructorClassesAnalytics:
    """Test cases cho thống kê lớp học chi tiết."""
    
    @pytest.mark.asyncio
    async def test_get_classes_analytics_success(self, client: AsyncClient, test_vars: TestVariables, test_course):
        """Test xem thống kê lớp học chi tiết."""
        # Tạo lớp học với dữ liệu
        from models.models import Class
        cls = Class(
            name="Analytics Test Class",
            instructor_id=test_vars.instructor1_user_id,
            course_id=test_vars.course_id,
            max_students=30,
            student_count=20,
            status="active",
            invite_code="ANALYTICS"
        )
        await cls.insert()
        
        headers = test_vars.get_headers("instructor1")
        
        response = await client.get("/api/v1/analytics/instructor/classes", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Kiểm tra response schema theo CHUCNANG.md
        required_fields = ["classes_stats", "total_classes", "total_students",
                          "avg_attendance_rate", "avg_progress"]
        assert_response_schema(data, required_fields)
        
        # Kiểm tra classes_stats
        assert len(data["classes_stats"]) > 0
        class_stat = data["classes_stats"][0]
        stat_fields = ["class_id", "class_name", "student_count", "attendance_rate",
                      "avg_progress", "quizzes_created", "completion_rate"]
        assert_response_schema(class_stat, stat_fields)
    
    @pytest.mark.asyncio
    async def test_get_classes_analytics_filter_by_class(self, client: AsyncClient, test_vars: TestVariables, test_course):
        """Test lọc analytics theo lớp cụ thể."""
        from models.models import Class
        cls = Class(
            name="Specific Class",
            instructor_id=test_vars.instructor1_user_id,
            course_id=test_vars.course_id,
            max_students=30,
            invite_code="SPECIFIC"
        )
        await cls.insert()
        
        headers = test_vars.get_headers("instructor1")
        
        response = await client.get(
            f"/api/v1/analytics/instructor/classes?class_id={cls.id}",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Chỉ có 1 class trong kết quả
        assert len(data["classes_stats"]) == 1
        assert data["classes_stats"][0]["class_id"] == str(cls.id)
    
    @pytest.mark.asyncio
    async def test_get_classes_analytics_filter_by_time_range(self, client: AsyncClient, test_vars: TestVariables):
        """Test lọc analytics theo khoảng thời gian."""
        headers = test_vars.get_headers("instructor1")
        
        start_date = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
        end_date = datetime.now(timezone.utc).isoformat()
        
        response = await client.get(
            f"/api/v1/analytics/instructor/classes?start_date={start_date}&end_date={end_date}",
            headers=headers
        )
        
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_get_classes_analytics_filter_by_course(self, client: AsyncClient, test_vars: TestVariables, test_course):
        """Test lọc analytics theo khóa học."""
        headers = test_vars.get_headers("instructor1")
        
        response = await client.get(
            f"/api/v1/analytics/instructor/classes?course_id={test_course['course_id']}",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Tất cả classes phải thuộc course này
        for class_stat in data["classes_stats"]:
            assert class_stat["course_id"] == test_vars.course_id


class TestInstructorProgressChart:
    """Test cases cho biểu đồ tiến độ học viên."""
    
    @pytest.mark.asyncio
    async def test_get_progress_chart_success(self, client: AsyncClient, test_vars: TestVariables, test_course):
        """Test xem biểu đồ tiến độ học viên."""
        # Tạo lớp học
        from models.models import Class
        cls = Class(
            name="Progress Chart Class",
            instructor_id=test_vars.instructor1_user_id,
            course_id=test_vars.course_id,
            max_students=30,
            invite_code="PROGRESS"
        )
        await cls.insert()
        
        headers = test_vars.get_headers("instructor1")
        
        response = await client.get("/api/v1/analytics/instructor/progress-chart", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Kiểm tra response schema theo CHUCNANG.md
        required_fields = ["chart_type", "time_period", "data_points"]
        assert_response_schema(data, required_fields)
        
        # Kiểm tra data_points structure
        assert isinstance(data["data_points"], list)
        if len(data["data_points"]) > 0:
            point = data["data_points"][0]
            point_fields = ["date", "value", "metric"]
            assert_response_schema(point, point_fields)
    
    @pytest.mark.asyncio
    async def test_get_progress_chart_by_class(self, client: AsyncClient, test_vars: TestVariables, test_course):
        """Test biểu đồ tiến độ theo lớp cụ thể."""
        from models.models import Class
        cls = Class(
            name="Specific Class",
            instructor_id=test_vars.instructor1_user_id,
            course_id=test_vars.course_id,
            max_students=30,
            invite_code="CHARTCLASS"
        )
        await cls.insert()
        
        headers = test_vars.get_headers("instructor1")
        
        response = await client.get(
            f"/api/v1/analytics/instructor/progress-chart?class_id={cls.id}",
            headers=headers
        )
        
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_get_progress_chart_daily(self, client: AsyncClient, test_vars: TestVariables):
        """Test biểu đồ theo ngày."""
        headers = test_vars.get_headers("instructor1")
        
        response = await client.get(
            "/api/v1/analytics/instructor/progress-chart?period=daily&days=7",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["time_period"] == "daily"
        assert len(data["data_points"]) <= 7
    
    @pytest.mark.asyncio
    async def test_get_progress_chart_weekly(self, client: AsyncClient, test_vars: TestVariables):
        """Test biểu đồ theo tuần."""
        headers = test_vars.get_headers("instructor1")
        
        response = await client.get(
            "/api/v1/analytics/instructor/progress-chart?period=weekly&weeks=4",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["time_period"] == "weekly"
        assert len(data["data_points"]) <= 4
    
    @pytest.mark.asyncio
    async def test_get_progress_chart_monthly(self, client: AsyncClient, test_vars: TestVariables):
        """Test biểu đồ theo tháng."""
        headers = test_vars.get_headers("instructor1")
        
        response = await client.get(
            "/api/v1/analytics/instructor/progress-chart?period=monthly&months=6",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["time_period"] == "monthly"
        assert len(data["data_points"]) <= 6


class TestInstructorQuizPerformance:
    """Test cases cho phân tích hiệu quả quiz."""
    
    @pytest.mark.asyncio
    async def test_get_quiz_performance_success(self, client: AsyncClient, test_vars: TestVariables, test_course):
        """Test xem phân tích hiệu quả quiz."""
        # Tạo quiz với attempts
        from models.models import Quiz, QuizAttempt, Lesson
        lesson = await Lesson.find_one({"course_id": test_vars.course_id})
        
        quiz = Quiz(
            lesson_id=str(lesson.id),
            title="Performance Test Quiz",
            time_limit=30,
            pass_threshold=70,
            questions=[
                {
                    "id": "q1",
                    "question_text": "Question 1",
                    "type": "multiple_choice",
                    "correct_answer": "A",
                    "points": 10
                },
                {
                    "id": "q2",
                    "question_text": "Question 2",
                    "type": "multiple_choice",
                    "correct_answer": "B",
                    "points": 10
                }
            ],
            total_points=20,
            created_by=test_vars.instructor1_user_id
        )
        await quiz.insert()
        
        # Tạo attempts với các student IDs từ test_vars
        student_ids = [test_vars.student1_user_id, test_vars.student2_user_id]
        for i, student_id in enumerate(student_ids, 1):
            attempt = QuizAttempt(
                quiz_id=str(quiz.id),
                user_id=student_id,
                answers=[
                    {"question_id": "q1", "selected_answer": "A", "is_correct": True},
                    {"question_id": "q2", "selected_answer": "B", "is_correct": i > 1}
                ],
                score=50.0 + (i * 10),
                time_taken_minutes=15 + i,
                status="Pass" if (50 + i*10) >= 70 else "Fail"
            )
            await attempt.insert()
        
        headers = test_vars.get_headers("instructor1")
        
        response = await client.get("/api/v1/analytics/instructor/quiz-performance", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Kiểm tra response schema theo CHUCNANG.md
        required_fields = ["quizzes", "total_quizzes", "overall_stats"]
        assert_response_schema(data, required_fields)
        
        # Kiểm tra quiz structure
        if len(data["quizzes"]) > 0:
            quiz_perf = data["quizzes"][0]
            quiz_fields = ["quiz_id", "quiz_title", "total_attempts", "pass_rate",
                          "avg_score", "avg_time_minutes", "hardest_questions", "score_distribution"]
            assert_response_schema(quiz_perf, quiz_fields)
            
            # Kiểm tra hardest_questions
            if len(quiz_perf["hardest_questions"]) > 0:
                hard_q = quiz_perf["hardest_questions"][0]
                assert "question_id" in hard_q
                assert "question_text" in hard_q
                assert "error_rate" in hard_q
        
        # Kiểm tra overall_stats
        overall = data["overall_stats"]
        assert "total_attempts" in overall
        assert "avg_pass_rate" in overall
        assert "avg_completion_time" in overall
    
    @pytest.mark.asyncio
    async def test_get_quiz_performance_filter_by_quiz(self, client: AsyncClient, test_vars: TestVariables, test_course):
        """Test phân tích hiệu quả cho quiz cụ thể."""
        from models.models import Quiz, Lesson
        lesson = await Lesson.find_one({"course_id": test_vars.course_id})
        
        quiz = Quiz(
            lesson_id=str(lesson.id),
            title="Specific Quiz",
            time_limit=30,
            pass_threshold=70,
            questions=[],
            created_by=test_vars.instructor1_user_id
        )
        await quiz.insert()
        
        headers = test_vars.get_headers("instructor1")
        
        response = await client.get(
            f"/api/v1/analytics/instructor/quiz-performance?quiz_id={quiz.id}",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Chỉ có 1 quiz trong kết quả
        assert len(data["quizzes"]) == 1
        assert data["quizzes"][0]["quiz_id"] == str(quiz.id)
    
    @pytest.mark.asyncio
    async def test_get_quiz_performance_filter_by_class(self, client: AsyncClient, test_vars: TestVariables, test_course):
        """Test phân tích hiệu quả quiz theo lớp."""
        from models.models import Class
        cls = Class(
            name="Quiz Performance Class",
            instructor_id=test_vars.instructor1_user_id,
            course_id=test_vars.course_id,
            max_students=30,
            invite_code="QUIZPERF"
        )
        await cls.insert()
        
        headers = test_vars.get_headers("instructor1")
        
        response = await client.get(
            f"/api/v1/analytics/instructor/quiz-performance?class_id={cls.id}",
            headers=headers
        )
        
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_get_quiz_performance_no_quizzes(self, client: AsyncClient, test_vars: TestVariables):
        """Test phân tích khi chưa có quiz nào."""
        headers = test_vars.get_headers("instructor2")  # Instructor chưa tạo quiz
        
        response = await client.get("/api/v1/analytics/instructor/quiz-performance", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["total_quizzes"] == 0
        assert len(data["quizzes"]) == 0
    
    @pytest.mark.asyncio
    async def test_get_quiz_performance_detailed_analysis(self, client: AsyncClient, test_vars: TestVariables, test_course):
        """Test phân tích chi tiết với score distribution."""
        from models.models import Quiz, QuizAttempt, Lesson
        lesson = await Lesson.find_one({"course_id": test_vars.course_id})
        
        quiz = Quiz(
            lesson_id=str(lesson.id),
            title="Detailed Analysis Quiz",
            time_limit=30,
            pass_threshold=70,
            questions=[],
            total_points=100,
            created_by=test_vars.instructor1_user_id
        )
        await quiz.insert()
        
        # Tạo nhiều attempts với điểm số khác nhau
        scores = [50, 60, 70, 80, 90, 95]
        student_ids = [test_vars.student1_user_id, test_vars.student2_user_id]
        
        for i, score in enumerate(scores):
            # Rotate through available student IDs
            student_id = student_ids[i % len(student_ids)]
            attempt = QuizAttempt(
                quiz_id=str(quiz.id),
                user_id=student_id,
                answers=[],
                score=float(score),
                status="Pass" if score >= 70 else "Fail"
            )
            await attempt.insert()
        
        headers = test_vars.get_headers("instructor1")
        
        response = await client.get(
            f"/api/v1/analytics/instructor/quiz-performance?quiz_id={quiz.id}&detailed=true",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        quiz_perf = data["quizzes"][0]
        
        # Kiểm tra score_distribution
        assert "score_distribution" in quiz_perf
        distribution = quiz_perf["score_distribution"]
        
        # Distribution có thể là histogram hoặc ranges
        assert isinstance(distribution, (list, dict))
        
        # Kiểm tra pass_rate
        expected_pass_rate = (4 / 6) * 100  # 4 pass / 6 total
        assert abs(quiz_perf["pass_rate"] - expected_pass_rate) < 1
