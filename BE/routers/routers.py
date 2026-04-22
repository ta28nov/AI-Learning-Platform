"""
Routers Registry - Đăng ký tất cả routers vào api_router
File này tổng hợp tất cả routers từ các module khác nhau
"""

from fastapi import APIRouter

# Import routers
from routers.auth_router import router as auth_router
from routers.users_router import router as users_router
from routers.assessments_router import router as assessments_router
from routers.courses_router import router as courses_router
from routers.enrollments_router import router as enrollments_router
from routers.learning_router import router as learning_router
from routers.quiz_router import router as quiz_router
from routers.progress_router import router as progress_router
from routers.personal_courses_router import router as personal_courses_router
from routers.chat_router import router as chat_router
from routers.recommendation_router import router as recommendation_router
from routers.dashboard_router import router as dashboard_router
from routers.analytics_router import router as analytics_router
from routers.classes_router import router as classes_router
from routers.search_router import router as search_router
from routers.admin_router import router as admin_router

# Tạo api_router chính
api_router = APIRouter()

# Đăng ký các routers đã hoàn thành
# Group 2.1: Authentication & Users (5 endpoints)
api_router.include_router(auth_router)
api_router.include_router(users_router)

# Group 2.2: AI Assessment (3 endpoints)
api_router.include_router(assessments_router)

# Group 2.3: Course Discovery & Enrollment (8 endpoints)
api_router.include_router(courses_router)
api_router.include_router(enrollments_router)

# Group 2.4: Learning & Progress (17 endpoints)
api_router.include_router(learning_router)
api_router.include_router(quiz_router)
api_router.include_router(progress_router)

# Group 2.5: Personal Courses (5 endpoints)
api_router.include_router(personal_courses_router)

# Group 2.6: AI Chatbot (5 endpoints)
api_router.include_router(chat_router)

# Group 2.7: Dashboard & Analytics (4 endpoints)
api_router.include_router(recommendation_router)
api_router.include_router(dashboard_router)
api_router.include_router(analytics_router)

# Group 3.1-3.2: Class Management (10 endpoints)
api_router.include_router(classes_router)

# Group 5.1: Universal Search (4 endpoints)
api_router.include_router(search_router)

# Group 4.1-4.4: Admin Management (18 endpoints)
api_router.include_router(admin_router)
