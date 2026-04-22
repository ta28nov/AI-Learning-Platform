"""Hàm tiện ích chung cho dự án."""
import re
import unicodedata
from datetime import datetime
from typing import List


def utc_now_str() -> str:
    """Trả về thời gian hiện tại dạng ISO 8601."""
    return datetime.utcnow().isoformat()


def normalize_search_query(query: str) -> str:
    """
    Chuẩn hóa search query để improve search quality
    
    Args:
        query: Raw search query
        
    Returns:
        Normalized query string
    """
    if not query:
        return ""
    
    # Convert to lowercase
    normalized = query.lower().strip()
    
    # Remove Vietnamese accents for better search
    normalized = remove_vietnamese_accents(normalized)
    
    # Remove extra spaces
    normalized = re.sub(r'\s+', ' ', normalized)
    
    # Remove special characters (keep letters, numbers, spaces)
    normalized = re.sub(r'[^\w\s]', ' ', normalized)
    
    # Remove extra spaces again after special char removal
    normalized = re.sub(r'\s+', ' ', normalized).strip()
    
    return normalized


def remove_vietnamese_accents(text: str) -> str:
    """
    Remove Vietnamese accents for search normalization
    
    Args:
        text: Text với accents
        
    Returns:
        Text không accents
    """
    if not text:
        return ""
    
    # Vietnamese accent mapping
    vietnamese_accents = {
        'à': 'a', 'á': 'a', 'ả': 'a', 'ã': 'a', 'ạ': 'a',
        'ă': 'a', 'ằ': 'a', 'ắ': 'a', 'ẳ': 'a', 'ẵ': 'a', 'ặ': 'a',
        'â': 'a', 'ầ': 'a', 'ấ': 'a', 'ẩ': 'a', 'ẫ': 'a', 'ậ': 'a',
        'è': 'e', 'é': 'e', 'ẻ': 'e', 'ẽ': 'e', 'ẹ': 'e',
        'ê': 'e', 'ề': 'e', 'ế': 'e', 'ể': 'e', 'ễ': 'e', 'ệ': 'e',
        'ì': 'i', 'í': 'i', 'ỉ': 'i', 'ĩ': 'i', 'ị': 'i',
        'ò': 'o', 'ó': 'o', 'ỏ': 'o', 'õ': 'o', 'ọ': 'o',
        'ô': 'o', 'ồ': 'o', 'ố': 'o', 'ổ': 'o', 'ỗ': 'o', 'ộ': 'o',
        'ơ': 'o', 'ờ': 'o', 'ớ': 'o', 'ở': 'o', 'ỡ': 'o', 'ợ': 'o',
        'ù': 'u', 'ú': 'u', 'ủ': 'u', 'ũ': 'u', 'ụ': 'u',
        'ư': 'u', 'ừ': 'u', 'ứ': 'u', 'ử': 'u', 'ữ': 'u', 'ự': 'u',
        'ỳ': 'y', 'ý': 'y', 'ỷ': 'y', 'ỹ': 'y', 'ỵ': 'y',
        'đ': 'd'
    }
    
    # Replace Vietnamese accents
    result = text
    for accented, unaccented in vietnamese_accents.items():
        result = result.replace(accented, unaccented)
        result = result.replace(accented.upper(), unaccented.upper())
    
    return result


def calculate_relevance_score(query: str, texts: List[str]) -> float:
    """
    Tính relevance score cho search results
    
    Args:
        query: Search query đã normalized
        texts: List of texts để tính score (title, description, etc.)
        
    Returns:
        Relevance score from 0-100
    """
    if not query or not texts:
        return 0.0
    
    total_score = 0.0
    query_words = query.lower().split()
    
    for text in texts:
        if not text:
            continue
            
        text_normalized = normalize_search_query(text)
        text_words = text_normalized.split()
        
        # Score calculations
        exact_match_score = 0
        partial_match_score = 0
        position_bonus = 0
        
        # Check for exact phrase match
        if query.lower() in text_normalized:
            exact_match_score = 50
            # Bonus nếu match ở đầu text
            if text_normalized.startswith(query.lower()):
                position_bonus = 20
        
        # Check word matches
        matched_words = 0
        for query_word in query_words:
            if query_word in text_words:
                matched_words += 1
                # Bonus cho exact word matches
                partial_match_score += 10
        
        # Calculate percentage of query words matched
        if len(query_words) > 0:
            match_percentage = matched_words / len(query_words)
            partial_match_score *= match_percentage
        
        # Text score for this field
        text_score = exact_match_score + partial_match_score + position_bonus
        
        # Weight different fields differently (title có weight cao hơn description)
        if texts.index(text) == 0:  # Assume first text is title
            text_score *= 1.5
        
        total_score += text_score
    
    # Normalize to 0-100 range
    max_possible_score = len(texts) * 100
    if max_possible_score > 0:
        normalized_score = min(100.0, (total_score / max_possible_score) * 100)
    else:
        normalized_score = 0.0
    
    return round(normalized_score, 2)


def truncate_text(text: str, max_length: int = 200, suffix: str = "...") -> str:
    """
    Truncate text với suffix
    
    Args:
        text: Text cần truncate
        max_length: Độ dài tối đa
        suffix: Suffix khi truncate
        
    Returns:
        Truncated text
    """
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def format_search_url(object_type: str, object_id: str, **kwargs) -> str:
    """
    Format URL cho search results
    
    Args:
        object_type: course|user|class|module|lesson
        object_id: UUID của object
        **kwargs: Additional parameters (course_id, module_id, etc.)
        
    Returns:
        Formatted URL string
    """
    if object_type == "course":
        return f"/courses/{object_id}"
    elif object_type == "user":
        return f"/users/{object_id}"
    elif object_type == "class":
        return f"/classes/{object_id}"
    elif object_type == "module":
        course_id = kwargs.get("course_id", "")
        return f"/courses/{course_id}/modules/{object_id}"
    elif object_type == "lesson":
        course_id = kwargs.get("course_id", "")
        module_id = kwargs.get("module_id", "")
        return f"/courses/{course_id}/modules/{module_id}/lessons/{object_id}"
    else:
        return f"/{object_type}s/{object_id}"
