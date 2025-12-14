"""
Search Controller
Xử lý requests cho universal search endpoints  
Section 5.1: TÌM KIẾM & LỌC
"""

from typing import Dict, Optional
from fastapi import HTTPException, status

from schemas.search import SearchResponse, SearchHistoryResponse, SearchAnalytics
from services import search_service


# ============================================================================
# Section 5.1: UNIVERSAL SEARCH & ADVANCED FILTERING
# ============================================================================

async def handle_universal_search(
    query: str,
    category_filter: Optional[str] = None,
    level_filter: Optional[str] = None,
    instructor_filter: Optional[str] = None,
    rating_filter: Optional[float] = None,
    page: int = 1,
    limit: int = 20,
    current_user: Dict = None
) -> SearchResponse:
    """
    5.1.1: Universal search box với advanced filtering
    
    Flow:
    1. Validate search parameters
    2. Gọi search_service để thực hiện tìm kiếm
    3. Return kết quả grouped by category với suggestions
    
    Args:
        query: Từ khóa tìm kiếm (required)
        category_filter: Programming/Math/Business... (optional)
        level_filter: Beginner/Intermediate/Advanced (optional) 
        instructor_filter: UUID giảng viên (optional)
        rating_filter: Đánh giá tối thiểu 0-5 (optional)
        page: Trang hiện tại (default 1)
        limit: Số kết quả per page (default 20)
        current_user: User context từ JWT
        
    Returns:
        SearchResponse với results grouped by category
        
    Raises:
        HTTPException 400: Invalid parameters
        HTTPException 500: Search service error
    """
    # Validate required parameters
    if not query or len(query.strip()) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Từ khóa tìm kiếm phải có ít nhất 2 ký tự"
        )
    
    # Validate pagination
    if page < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Trang phải lớn hơn 0"
        )
    
    if limit < 1 or limit > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Limit phải từ 1-100"
        )
    
    # Validate rating filter
    if rating_filter is not None and (rating_filter < 0 or rating_filter > 5):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rating filter phải từ 0-5"
        )
    
    # Validate category filter
    valid_categories = [
        "Programming", "Math", "Business", "Design", "Marketing", 
        "Science", "Language", "Music", "Health", "Engineering"
    ]
    if category_filter and category_filter not in valid_categories:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Category không hợp lệ. Các category: {', '.join(valid_categories)}"
        )
    
    # Validate level filter
    valid_levels = ["Beginner", "Intermediate", "Advanced"]
    if level_filter and level_filter not in valid_levels:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Level không hợp lệ. Các level: {', '.join(valid_levels)}"
        )
    
    try:
        # Thực hiện universal search
        search_results = await search_service.universal_search(
            query=query.strip(),
            current_user=current_user or {},
            category_filter=category_filter,
            level_filter=level_filter,
            instructor_filter=instructor_filter,
            rating_filter=rating_filter,
            page=page,
            limit=limit
        )
        
        return SearchResponse(**search_results)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi thực hiện tìm kiếm: {str(e)}"
        )


async def handle_get_search_history(current_user: Dict) -> SearchHistoryResponse:
    """
    Lấy lịch sử tìm kiếm của user hiện tại
    
    Flow:
    1. Validate user login
    2. Gọi search_service để lấy history
    3. Return search history với popular searches
    
    Args:
        current_user: User context từ JWT
        
    Returns:
        SearchHistoryResponse với lịch sử và popular searches
        
    Raises:
        HTTPException 401: User chưa đăng nhập
        HTTPException 500: Service error
    """
    # Validate user login
    if not current_user or not current_user.get("user_id"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Cần đăng nhập để xem lịch sử tìm kiếm"
        )
    
    try:
        # Lấy search history
        history_data = await search_service.get_search_history(
            current_user["user_id"]
        )
        
        return SearchHistoryResponse(**history_data)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi lấy lịch sử tìm kiếm: {str(e)}"
        )


async def handle_get_search_analytics(current_user: Dict) -> SearchAnalytics:
    """
    Lấy search analytics cho admin
    
    Flow:
    1. Validate admin permission
    2. Gọi search_service để lấy analytics
    3. Return search performance metrics
    
    Args:
        current_user: User context từ JWT
        
    Returns:
        SearchAnalytics với search performance data
        
    Raises:
        HTTPException 403: Không phải admin
        HTTPException 500: Service error
    """
    # Validate admin permission
    if not current_user or current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ admin mới có quyền xem search analytics"
        )
    
    try:
        # Lấy search analytics
        analytics_data = await search_service.get_search_analytics()
        
        return SearchAnalytics(**analytics_data)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi lấy search analytics: {str(e)}"
        )


async def handle_search_suggestions(
    query: str,
    current_user: Dict = None
) -> Dict:
    """
    Lấy search suggestions real-time cho autocomplete
    
    Flow:
    1. Validate query length
    2. Generate suggestions từ existing data
    3. Return autocomplete suggestions
    
    Args:
        query: Partial query string
        current_user: User context (optional)
        
    Returns:
        Dict với suggestions list
        
    Raises:
        HTTPException 400: Query quá ngắn
    """
    # Validate query
    if not query or len(query.strip()) < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query phải có ít nhất 1 ký tự"
        )
    
    try:
        # Generate suggestions (simplified version of full search)
        from services.search_service import _generate_suggestions
        suggestions = await _generate_suggestions(query.strip(), query.strip())
        
        return {
            "query": query,
            "suggestions": suggestions
        }
        
    except Exception as e:
        # Return empty suggestions nếu có lỗi
        return {
            "query": query,
            "suggestions": []
        }