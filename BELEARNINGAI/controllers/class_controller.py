"""
Class Controller - Xử lý requests cho quản lý lớp học
Sử dụng: FastAPI, class_service
Tuân thủ: ENDPOINTS.md Classes Router
"""

from fastapi import HTTPException
from datetime import datetime
from typing import Optional
from schemas.classes import (
    ClassCreateRequest, ClassCreateResponse,
    ClassListResponse,
    ClassDetailResponse,
    ClassUpdateRequest,
    ClassJoinRequest, ClassJoinResponse,
    ClassStudentListResponse,
    ClassStudentDetailResponse,
    ClassProgressResponse
)
from services import class_service


# ============================================================================
# Section 3.1: CLASS MANAGEMENT HANDLERS
# ============================================================================

async def handle_create_class(
    request: ClassCreateRequest,
    current_user: dict
) -> ClassCreateResponse:
    """
    3.1.1: POST /classes - Tạo lớp học mới
    
    Handler Logic:
    1. Extract instructor_id từ JWT
    2. Call service.create_class()
    3. Handle errors (course not found, etc.)
    4. Return ClassCreateResponse
    
    Args:
        request: ClassCreateRequest schema
        current_user: JWT payload
        
    Returns:
        ClassCreateResponse
        
    Raises:
        HTTPException 400: Invalid input
        HTTPException 404: Course not found
        HTTPException 500: Server error
    """
    instructor_id = current_user.get("user_id")
    
    try:
        result = await class_service.create_class(
            instructor_id=instructor_id,
            name=request.name,
            description=request.description,
            course_id=request.course_id,
            start_date=request.start_date,
            end_date=request.end_date,
            max_students=request.max_students
        )
        
        return ClassCreateResponse(**result)
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi tạo lớp học: {str(e)}")


async def handle_list_my_classes(
    status: Optional[str],
    current_user: dict
) -> ClassListResponse:
    """
    3.1.2: GET /classes/my-classes - Danh sách lớp của instructor
    
    Handler Logic:
    1. Extract instructor_id từ JWT
    2. Optional filter theo status
    3. Call service.list_my_classes()
    4. Return ClassListResponse
    
    Args:
        status: Optional filter
        current_user: JWT payload
        
    Returns:
        ClassListResponse
    """
    instructor_id = current_user.get("user_id")
    
    try:
        result = await class_service.list_my_classes(
            instructor_id=instructor_id,
            status_filter=status
        )
        
        return ClassListResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi lấy danh sách lớp: {str(e)}")


async def handle_get_class_detail(
    class_id: str,
    current_user: dict
) -> ClassDetailResponse:
    """
    3.1.3: GET /classes/{class_id} - Chi tiết lớp học
    
    Handler Logic:
    1. Extract instructor_id từ JWT
    2. Call service.get_class_detail() với ownership check
    3. Handle not found / unauthorized
    4. Return ClassDetailResponse
    
    Args:
        class_id: UUID của lớp học
        current_user: JWT payload
        
    Returns:
        ClassDetailResponse
        
    Raises:
        HTTPException 404: Class not found or unauthorized
    """
    instructor_id = current_user.get("user_id")
    
    try:
        result = await class_service.get_class_detail(
            class_id=class_id,
            instructor_id=instructor_id
        )
        
        return ClassDetailResponse(**result)
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi lấy chi tiết lớp: {str(e)}")


async def handle_update_class(
    class_id: str,
    request: ClassUpdateRequest,
    current_user: dict
) -> dict:
    """
    3.1.4: PUT /classes/{class_id} - Cập nhật lớp học
    
    Handler Logic:
    1. Extract instructor_id từ JWT
    2. Convert ClassUpdateRequest to dict (only provided fields)
    3. Call service.update_class() với validation
    4. Handle validation errors
    5. Return success message
    
    Args:
        class_id: UUID của lớp học
        request: ClassUpdateRequest schema
        current_user: JWT payload
        
    Returns:
        Dict với message
        
    Raises:
        HTTPException 400: Validation failed
        HTTPException 404: Class not found
    """
    instructor_id = current_user.get("user_id")
    
    # Convert request to dict (exclude unset fields)
    update_data = request.model_dump(exclude_unset=True)
    
    if not update_data:
        raise HTTPException(status_code=400, detail="Không có dữ liệu để cập nhật")
    
    try:
        result = await class_service.update_class(
            class_id=class_id,
            instructor_id=instructor_id,
            update_data=update_data
        )
        
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi cập nhật lớp: {str(e)}")


async def handle_delete_class(
    class_id: str,
    current_user: dict
) -> dict:
    """
    3.1.5: DELETE /classes/{class_id} - Xóa lớp học
    
    Handler Logic:
    1. Extract instructor_id từ JWT
    2. Call service.delete_class() với ownership + condition checks
    3. Handle errors (has students, not completed, etc.)
    4. Return confirmation
    
    Args:
        class_id: UUID của lớp học
        current_user: JWT payload
        
    Returns:
        Dict với message
        
    Raises:
        HTTPException 400: Cannot delete (has students)
        HTTPException 404: Class not found
    """
    instructor_id = current_user.get("user_id")
    
    try:
        result = await class_service.delete_class(
            class_id=class_id,
            instructor_id=instructor_id
        )
        
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi xóa lớp: {str(e)}")


# ============================================================================
# Section 3.2: STUDENT MANAGEMENT HANDLERS
# ============================================================================

async def handle_join_class_with_code(
    request: ClassJoinRequest,
    current_user: dict
) -> ClassJoinResponse:
    """
    3.2.1: POST /classes/join - Tham gia lớp bằng mã mời
    
    Handler Logic:
    1. Extract user_id từ JWT
    2. Call service.join_class_with_code()
    3. Handle errors (invalid code, full, already joined)
    4. Return ClassJoinResponse
    
    Args:
        request: ClassJoinRequest schema
        current_user: JWT payload
        
    Returns:
        ClassJoinResponse
        
    Raises:
        HTTPException 400: Invalid code or class full
        HTTPException 404: Class not found
    """
    user_id = current_user.get("user_id")
    
    try:
        result = await class_service.join_class_with_code(
            user_id=user_id,
            invite_code=request.invite_code
        )
        
        return ClassJoinResponse(**result)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi tham gia lớp: {str(e)}")


async def handle_get_class_students(
    class_id: str,
    skip: int,
    limit: int,
    current_user: dict
) -> ClassStudentListResponse:
    """
    3.2.2: GET /classes/{class_id}/students - Danh sách học viên
    
    Handler Logic:
    1. Extract instructor_id từ JWT
    2. Validate pagination params
    3. Call service.get_class_students()
    4. Return ClassStudentListResponse
    
    Args:
        class_id: UUID của lớp học
        skip: Pagination skip
        limit: Pagination limit
        current_user: JWT payload
        
    Returns:
        ClassStudentListResponse
    """
    instructor_id = current_user.get("user_id")
    
    try:
        result = await class_service.get_class_students(
            class_id=class_id,
            instructor_id=instructor_id,
            skip=skip,
            limit=limit
        )
        
        return ClassStudentListResponse(**result)
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi lấy danh sách học viên: {str(e)}")


async def handle_get_student_detail(
    class_id: str,
    student_id: str,
    current_user: dict
) -> ClassStudentDetailResponse:
    """
    3.2.3: GET /classes/{class_id}/students/{student_id} - Chi tiết học viên
    
    Handler Logic:
    1. Extract instructor_id từ JWT
    2. Call service.get_student_detail()
    3. Handle errors (not in class, not found)
    4. Return ClassStudentDetailResponse
    
    Args:
        class_id: UUID của lớp học
        student_id: UUID của học viên
        current_user: JWT payload
        
    Returns:
        ClassStudentDetailResponse
        
    Raises:
        HTTPException 404: Student or class not found
    """
    instructor_id = current_user.get("user_id")
    
    try:
        result = await class_service.get_student_detail(
            class_id=class_id,
            student_id=student_id,
            instructor_id=instructor_id
        )
        
        return ClassStudentDetailResponse(**result)
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi lấy thông tin học viên: {str(e)}")


async def handle_remove_student(
    class_id: str,
    student_id: str,
    current_user: dict
) -> dict:
    """
    3.2.4: DELETE /classes/{class_id}/students/{student_id} - Xóa học viên
    
    Handler Logic:
    1. Extract instructor_id từ JWT
    2. Call service.remove_student() (soft delete)
    3. Handle errors (not in class, not found)
    4. Return confirmation
    
    Args:
        class_id: UUID của lớp học
        student_id: UUID của học viên
        current_user: JWT payload
        
    Returns:
        Dict với message
        
    Raises:
        HTTPException 404: Student or class not found
    """
    instructor_id = current_user.get("user_id")
    
    try:
        result = await class_service.remove_student(
            class_id=class_id,
            student_id=student_id,
            instructor_id=instructor_id
        )
        
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi xóa học viên: {str(e)}")


async def handle_get_class_progress(
    class_id: str,
    current_user: dict
) -> ClassProgressResponse:
    """
    3.2.5: GET /classes/{class_id}/progress - Tiến độ tổng thể lớp
    
    Handler Logic:
    1. Extract instructor_id từ JWT
    2. Call service.get_class_progress()
    3. Return ClassProgressResponse với analytics
    
    Args:
        class_id: UUID của lớp học
        current_user: JWT payload
        
    Returns:
        ClassProgressResponse
        
    Raises:
        HTTPException 404: Class not found
    """
    instructor_id = current_user.get("user_id")
    
    try:
        result = await class_service.get_class_progress(
            class_id=class_id,
            instructor_id=instructor_id
        )
        
        return ClassProgressResponse(**result)
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi lấy tiến độ lớp: {str(e)}")
