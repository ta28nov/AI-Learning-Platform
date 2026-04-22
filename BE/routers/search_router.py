"""
Search Router
Định nghĩa routes cho universal search endpoints
Section 5.1: TÌM KIẾM & LỌC
"""

from fastapi import APIRouter, Depends, status, Query
from typing import Optional
from middleware.auth import get_current_user, get_optional_user
from controllers.search_controller import (
    handle_universal_search,
    handle_get_search_history,
    handle_get_search_analytics,
    handle_search_suggestions
)
from schemas.search import (
    SearchResponse,
    SearchHistoryResponse,
    SearchAnalytics
)


router = APIRouter(prefix="/search", tags=["Search"])


# ============================================================================
# Section 5.1: UNIVERSAL SEARCH & ADVANCED FILTERING
# ============================================================================

@router.get(
    "",
    response_model=SearchResponse,
    status_code=status.HTTP_200_OK,
    summary="Tìm kiếm thông minh universal",
    description="Universal search box cho tất cả đối tượng: courses, users, classes, modules, lessons"
)
async def universal_search(
    q: str = Query(..., min_length=2, description="Từ khóa tìm kiếm (ít nhất 2 ký tự)"),
    category: Optional[str] = Query(None, description="Filter category: Programming|Math|Business|Design|Marketing|Science|Language|Music|Health|Engineering"),
    level: Optional[str] = Query(None, description="Filter level: Beginner|Intermediate|Advanced"),
    instructor: Optional[str] = Query(None, description="Filter theo instructor ID"),
    rating: Optional[float] = Query(None, ge=0, le=5, description="Đánh giá tối thiểu (0-5)"),
    page: int = Query(1, ge=1, description="Số trang"),
    limit: int = Query(20, ge=1, le=100, description="Số kết quả per page"),
    current_user: dict = Depends(get_optional_user)
):
    """
    Section 5.1.1 - Tìm kiếm thông minh với filter nâng cao
    
    **Tính năng nâng cao:**
    - Full-text search across multiple types
    - Search suggestions với autocomplete
    - Typo tolerance
    - Results grouped by category
    - Relevance scoring
    - Search history cho logged-in users
    
    **Có thể tìm:**
    - Khóa học (courses)
    - Người dùng (users - nếu có quyền)
    - Lớp học (classes)
    - Modules
    - Lessons
    
    **Ví dụ:**
    - Tìm cơ bản: `GET /api/v1/search?q=python`
    - Tìm có filter: `GET /api/v1/search?q=python&category=Programming&level=Beginner&rating=4.5`
    """
    return await handle_universal_search(
        query=q,
        category_filter=category,
        level_filter=level,
        instructor_filter=instructor,
        rating_filter=rating,
        page=page,
        limit=limit,
        current_user=current_user
    )


@router.get(
    "/suggestions",
    status_code=status.HTTP_200_OK,
    summary="Gợi ý tìm kiếm real-time",
    description="Autocomplete suggestions cho search box khi user đang typing"
)
async def get_search_suggestions(
    q: str = Query(..., min_length=1, description="Partial query cho autocomplete"),
    current_user: dict = Depends(get_optional_user)
):
    """
    Real-time search suggestions cho autocomplete
    
    **Tính năng:**
    - Autocomplete từ course titles
    - Typo correction suggestions
    - Popular search terms
    - Fast response cho typing experience
    """
    return await handle_search_suggestions(q, current_user)


@router.get(
    "/history",
    response_model=SearchHistoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Lịch sử tìm kiếm của user",
    description="Xem lịch sử tìm kiếm cá nhân và popular searches"
)
async def get_search_history(
    current_user: dict = Depends(get_current_user)
):
    """
    Lấy lịch sử tìm kiếm của user hiện tại
    
    **Hiển thị:**
    - 20 searches gần đây nhất
    - Popular search terms trong hệ thống
    - Click analytics cho optimization
    """
    return await handle_get_search_history(current_user)


@router.get(
    "/analytics",
    response_model=SearchAnalytics,
    status_code=status.HTTP_200_OK,
    summary="Search analytics cho admin",
    description="Thống kê hiệu suất search và user behavior"
)
async def get_search_analytics(
    current_user: dict = Depends(get_current_user)
):
    """
    Search analytics cho admin
    
    **Metrics:**
    - Tổng số searches
    - Trung bình kết quả per search
    - Popular categories
    - No-results queries cần optimize
    - Average search response time
    """
    return await handle_get_search_analytics(current_user)
