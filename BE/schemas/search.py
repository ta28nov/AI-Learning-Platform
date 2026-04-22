"""
Search Schemas
Định nghĩa request/response schemas cho search endpoints
Section 5.1: Universal Search & Filter
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional


class SearchResultItem(BaseModel):
    """Schema cho mỗi kết quả tìm kiếm"""
    id: str = Field(..., description="UUID của đối tượng")
    type: str = Field(..., description="course|user|class|module|lesson")
    title: str = Field(..., description="Tiêu đề/tên đối tượng")
    description: str = Field(..., description="Mô tả ngắn 2-3 lines")
    relevance_score: float = Field(..., description="Điểm độ liên quan 0-100")
    url: str = Field(..., description="URL để truy cập đối tượng")
    metadata: Optional[dict] = Field(None, description="Thông tin bổ sung theo type")


class SearchCategoryGroup(BaseModel):
    """Nhóm kết quả theo category"""
    category: str = Field(..., description="courses|users|classes|modules|lessons")
    count: int = Field(..., description="Số lượng kết quả trong category")
    items: List[SearchResultItem] = Field(..., description="Danh sách kết quả")


class SearchSuggestion(BaseModel):
    """Gợi ý tìm kiếm"""
    query: str = Field(..., description="Từ khóa gợi ý")
    type: str = Field(..., description="Loại gợi ý: autocomplete|typo_correction|popular")
    score: float = Field(..., description="Điểm ưu tiên gợi ý")


class SearchResponse(BaseModel):
    """Response cho universal search"""
    query: str = Field(..., description="Từ khóa tìm kiếm")
    total_results: int = Field(..., description="Tổng số kết quả")
    results_by_category: List[SearchCategoryGroup] = Field(..., description="Kết quả group theo category")
    suggestions: List[SearchSuggestion] = Field([], description="Gợi ý tìm kiếm")
    search_time_ms: int = Field(..., description="Thời gian tìm kiếm (milliseconds)")
    filters_applied: dict = Field(..., description="Các filter đã áp dụng")


class SearchHistoryItem(BaseModel):
    """Lịch sử tìm kiếm của user"""
    query: str = Field(..., description="Từ khóa đã tìm")
    timestamp: datetime = Field(..., description="Thời gian tìm kiếm")
    results_count: int = Field(..., description="Số kết quả tìm được")
    clicked_result_id: Optional[str] = Field(None, description="ID kết quả user đã click")


class SearchHistoryResponse(BaseModel):
    """Response cho lịch sử tìm kiếm"""
    user_id: str = Field(..., description="UUID user")
    search_history: List[SearchHistoryItem] = Field(..., description="Lịch sử tìm kiếm")
    popular_searches: List[str] = Field(..., description="Từ khóa tìm kiếm phổ biến")


class SearchAnalytics(BaseModel):
    """Analytics cho search performance"""
    total_searches: int = Field(..., description="Tổng số lần tìm kiếm")
    avg_results_per_search: float = Field(..., description="Trung bình kết quả mỗi lần tìm")
    popular_categories: List[dict] = Field(..., description="Danh mục được tìm nhiều nhất")
    no_results_queries: List[str] = Field(..., description="Từ khóa không có kết quả")
    avg_search_time_ms: float = Field(..., description="Thời gian tìm kiếm trung bình")
