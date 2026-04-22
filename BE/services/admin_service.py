"""
Admin Service - Xử lý business logic cho admin management
Sử dụng: Beanie ODM
Tuân thủ: CHUCNANG.md Section 4.1-4.3, API_SCHEMA.md
"""

from ast import And, Or
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from fastapi import HTTPException, status
from models.models import User, Course, Class, Enrollment, Progress
from utils.security import hash_password, generate_random_password


# ============================================================================
# Section 4.1: ADMIN USER MANAGEMENT  
# ============================================================================

async def get_users_list_admin(
    page: int = 1,
    limit: int = 20,
    search: Optional[str] = None,
    role_filter: Optional[str] = None,
    status_filter: Optional[str] = None,
    sort_by: str = "created_at",
    sort_order: str = "desc"
) -> Dict:
    """
    Lấy danh sách users với pagination và filters cho admin
    
    Business Logic:
    1. Build query với filters
    2. Apply search across name, email
    3. Sort theo field được chỉ định
    4. Return pagination data
    
    Args:
        page: Trang hiện tại (default 1)
        limit: Số items per page (default 20)
        search: Search query (tìm theo name, email)
        role_filter: Lọc theo role
        status_filter: Lọc theo status
        sort_by: Field để sort (default created_at)
        sort_order: asc/desc (default desc)
        
    Returns:
        Dict chứa users list và pagination info
    """
    # Build base query
    query_conditions = []
    
    # Apply role filter
    if role_filter:
        query_conditions.append(User.role == role_filter)
    
    # Apply status filter 
    if status_filter:
        query_conditions.append(User.status == status_filter)
    
    # Apply search
    if search:
        search_conditions = [
            User.full_name.contains(search, case_insensitive=True),
            User.email.contains(search, case_insensitive=True)
        ]
        # Add OR condition for search
        from beanie.operators import Or
        query_conditions.append(Or(*search_conditions))
    
    # Build final query
    if query_conditions:
        from beanie.operators import And
        query = User.find(And(*query_conditions))
    else:
        query = User.find()
    
    # Get total count
    total_count = await query.count()
    
    # Apply sorting
    sort_field = getattr(User, sort_by, User.created_at)
    if sort_order == "desc":
        query = query.sort(-sort_field)
    else:
        query = query.sort(sort_field)
    
    # Apply pagination
    skip = (page - 1) * limit
    users = await query.skip(skip).limit(limit).to_list()
    
    # Format user data
    users_data = []
    for user in users:
        # Get enrollment count if student
        enrollment_count = 0
        if user.role == "student":
            enrollment_count = await Enrollment.find(
                Enrollment.user_id == user.id
            ).count()
        
        # Get course count if instructor
        course_count = 0
        if user.role == "instructor":
            course_count = await Course.find(
                Course.instructor_id == user.id
            ).count()
        
        users_data.append({
            "user_id": str(user.id),
            "full_name": user.full_name,
            "email": user.email,
            "role": user.role,
            "status": user.status,
            "created_at": user.created_at.isoformat(),
            "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None,
            "enrollment_count": enrollment_count if user.role == "student" else None,
            "course_count": course_count if user.role == "instructor" else None
        })
    
    # Calculate pagination - theo API_SCHEMA.md Section 9.1
    # Convert page-based to skip-based for response
    skip = (page - 1) * limit
    total_pages = (total_count + limit - 1) // limit
    
    return {
        "data": users_data,
        "total": total_count,
        "skip": skip,
        "limit": limit,
        "has_next": page < total_pages
    }


async def get_user_detail_admin(user_id: str) -> Dict:
    """
    Lấy chi tiết user cho admin view
    
    Business Logic:
    1. Validate user existence
    2. Lấy additional stats: enrollments, courses created, activity
    3. Lấy recent activity logs
    
    Args:
        user_id: ID của user
        
    Returns:
        Dict chứa detailed user info
        
    Raises:
        404: User không tồn tại
    """
    # Get user
    user = await User.get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User không tồn tại"
        )
    
    # Get enrollments if student
    enrollments_data = []
    if user.role == "student":
        enrollments = await Enrollment.find(
            Enrollment.user_id == user.id
        ).sort(-Enrollment.created_at).to_list()
        
        for enrollment in enrollments:
            course = await Course.get(enrollment.course_id)
            if course:
                enrollments_data.append({
                    "enrollment_id": str(enrollment.id),
                    "course_id": str(course.id),
                    "course_title": course.title,
                    "status": enrollment.status,
                    "progress": enrollment.progress,
                    "enrolled_at": enrollment.created_at.isoformat(),
                    "completed_at": enrollment.completed_at.isoformat() if enrollment.completed_at else None
                })
    
    # Get courses if instructor
    courses_data = []
    if user.role == "instructor":
        courses = await Course.find(
            Course.instructor_id == user.id
        ).sort(-Course.created_at).to_list()
        
        for course in courses:
            enrollment_count = await Enrollment.find(
                Enrollment.course_id == course.id
            ).count()
            
            courses_data.append({
                "course_id": str(course.id),
                "title": course.title,
                "status": course.status,
                "category": course.category,
                "enrollment_count": enrollment_count,
                "created_at": course.created_at.isoformat()
            })
    
    # Activity stats (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    
    # Get recent activity based on role
    recent_activity = []
    if user.role == "student":
        recent_enrollments = await Enrollment.find(
            Enrollment.user_id == user.id,
            Enrollment.created_at >= thirty_days_ago
        ).sort(-Enrollment.created_at).limit(5).to_list()
        
        for enrollment in recent_enrollments:
            course = await Course.get(enrollment.course_id)
            if course:
                recent_activity.append({
                    "type": "enrollment",
                    "description": f"Đăng ký khóa học: {course.title}",
                    "timestamp": enrollment.created_at.isoformat()
                })
    
    elif user.role == "instructor":
        recent_courses = await Course.find(
            Course.instructor_id == user.id,
            Course.created_at >= thirty_days_ago
        ).sort(-Course.created_at).limit(5).to_list()
        
        for course in recent_courses:
            recent_activity.append({
                "type": "course_creation",
                "description": f"Tạo khóa học: {course.title}",
                "timestamp": course.created_at.isoformat()
            })
    
    return {
        "user_id": str(user.id),
        "full_name": user.full_name,
        "email": user.email,
        "role": user.role,
        "status": user.status,
        "created_at": user.created_at.isoformat(),
        "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None,
        "profile": {
            # "phone": user.phone,
            "bio": user.bio,
            #"profile_image": user.profile_image
        },
        "enrollments": enrollments_data if user.role == "student" else None,
        "courses": courses_data if user.role == "instructor" else None,
        "recent_activity": recent_activity,
        "statistics": {
            "total_enrollments": len(enrollments_data) if user.role == "student" else None,
            "total_courses_created": len(courses_data) if user.role == "instructor" else None,
            "activity_last_30d": len(recent_activity)
        }
    }


async def create_user_admin(user_data: Dict) -> Dict:
    """
    Tạo user mới bởi admin
    
    Business Logic:
    1. Validate email uniqueness
    2. Generate random password if not provided
    3. Hash password
    4. Create user với default values
    5. Return user info + generated password
    
    Args:
        user_data: Dict chứa user creation data
        
    Returns:
        Dict chứa created user info
        
    Raises:
        400: Email đã tồn tại
        500: Lỗi tạo user
    """
    # Check email uniqueness
    existing_user = await User.find_one(User.email == user_data["email"])
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email đã được sử dụng"
        )
    
    # Generate password if not provided
    password = user_data.get("password")
    if not password:
        password = generate_random_password()
    
    # Hash password
    hashed_password = hash_password(password)
    
    # Create user
    user = User(
        email=user_data["email"],
        full_name=user_data["full_name"],
        hashed_password=hashed_password,
        role=user_data.get("role", "student"),
        status="active",
        phone=user_data.get("phone"),
        bio=user_data.get("bio"),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    try:
        await user.save()
        
        return {
            "message": "Tạo tài khoản người dùng thành công", 
            "user_id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "status": user.status,
            "generated_password": password if not user_data.get("password") else None,
            "created_at": user.created_at.isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi tạo user: {str(e)}"
        )


async def update_user_admin(user_id: str, update_data: Dict) -> Dict:
    """
    Cập nhật user bởi admin
    
    Business Logic:
    1. Validate user existence
    2. Check email uniqueness nếu email được update
    3. Hash password mới nếu có
    4. Update allowed fields only
    5. Update timestamp
    
    Args:
        user_id: ID của user cần update
        update_data: Dict chứa fields cần update
        
    Returns:
        Dict chứa updated user info
        
    Raises:
        404: User không tồn tại
        400: Email đã được sử dụng
    """
    # Get user
    user = await User.get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User không tồn tại"
        )
    
    # Check email uniqueness if email is being updated
    if "email" in update_data and update_data["email"] != user.email:
        existing_user = await User.find_one(User.email == update_data["email"])
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email đã được sử dụng"
            )
    
    # Allowed fields for admin update
    allowed_fields = ["full_name", "email", "role", "status", "phone", "bio"]
    
    # Update fields
    for field, value in update_data.items():
        if field in allowed_fields:
            setattr(user, field, value)
    
    # Hash new password if provided
    if "password" in update_data:
        user.password = hash_password(update_data["password"])
    
    user.updated_at = datetime.utcnow()
    
    try:
        await user.save()
        
        return {
            "message": "Cập nhật thông tin người dùng thành công",
            "user_id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "status": user.status,
            "updated_at": user.updated_at.isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi cập nhật user: {str(e)}"
        )


async def delete_user_admin(user_id: str) -> Dict:
    """
    Xóa user bởi admin (soft delete)
    
    Business Logic:
    1. Validate user existence
    2. Check if user has active enrollments/courses
    3. Set status = "deleted" instead of hard delete
    4. Preserve data for audit purposes
    
    Args:
        user_id: ID của user cần xóa
        
    Returns:
        Dict confirmation
        
    Raises:
        404: User không tồn tại
        400: User có dữ liệu liên quan
    """
    # Get user
    user = await User.get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User không tồn tại"
        )
    
    # Check for active enrollments (for students)
    if user.role == "student":
        active_enrollments = await Enrollment.find(
            Enrollment.user_id == user.id,
            {"status": {"$in": ["active", "completed"]}} 
        ).count()
        
        if active_enrollments > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Không thể xóa user có {active_enrollments} enrollment đang hoạt động"
            )
    
    # Check for active courses (for instructors)
    if user.role == "instructor":
        active_courses = await Course.find(
            Course.instructor_id == user.id,
            {"status": {"$in": ["published", "draft"]}} 
        ).count()
        
        if active_courses > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Không thể xóa instructor có {active_courses} khóa học đang hoạt động"
            )
    
    # Soft delete
    user.status = "deleted"
    user.updated_at = datetime.utcnow()
    
    try:
        await user.save()
        
        return {
            "user_id": str(user.id),
            "message": "User đã được xóa thành công",
            "deleted_at": user.updated_at.isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi xóa user: {str(e)}"
        )


# ============================================================================
# Section 4.2: ADMIN COURSE MANAGEMENT
# ============================================================================

async def get_courses_list_admin(
    page: int = 1,
    limit: int = 20,
    search: Optional[str] = None,
    category_filter: Optional[str] = None,
    status_filter: Optional[str] = None,
    instructor_filter: Optional[str] = None,
    sort_by: str = "created_at",
    sort_order: str = "desc"
) -> Dict:
    """
    Lấy danh sách courses với filters cho admin
    
    Business Logic:
    1. Build query với filters
    2. Include instructor info và enrollment stats
    3. Apply pagination
    4. Return formatted course data
    
    Args:
        page: Trang hiện tại
        limit: Số items per page
        search: Search query
        category_filter: Lọc theo category
        status_filter: Lọc theo status
        instructor_filter: Lọc theo instructor
        sort_by: Field để sort
        sort_order: asc/desc
        
    Returns:
        Dict chứa courses list và pagination
    """
    # Build query conditions
    query_conditions = []
    
    # Apply filters
    if category_filter:
        query_conditions.append(Course.category == category_filter)
    
    if status_filter:
        query_conditions.append(Course.status == status_filter)
    
    if instructor_filter:
        query_conditions.append(Course.instructor_id == instructor_filter)
    
    # Apply search
    if search:
        search_conditions = [
            Course.title.contains(search, case_insensitive=True),
            Course.description.contains(search, case_insensitive=True)
        ]
        from beanie.operators import Or
        query_conditions.append(Or(*search_conditions))
    
    # Build final query
    if query_conditions:
        from beanie.operators import And
        query = Course.find(And(*query_conditions))
    else:
        query = Course.find()
    
    # Get total count
    total_count = await query.count()
    
    # Apply sorting
    sort_field = getattr(Course, sort_by, Course.created_at)
    if sort_order == "desc":
        query = query.sort(-sort_field)
    else:
        query = query.sort(sort_field)
    
    # Apply pagination
    skip = (page - 1) * limit
    courses = await query.skip(skip).limit(limit).to_list()
    
    # Format course data
    # Format course data
    courses_data = []
    for course in courses:
        # Get instructor info an toàn (giữ nguyên logic của bạn)
        instructor = None
        if getattr(course, "instructor_id", None):
            instructor = await User.get(course.instructor_id)
            
        # 1. TẠO OBJECT AUTHOR THEO ĐÚNG KHUÔN CourseAuthor
        author_data = {
            "user_id": str(instructor.id) if instructor else str(getattr(course, "instructor_id", "Unknown")),
            "full_name": instructor.full_name if instructor else "Unknown",
            "email": getattr(instructor, "email", "unknown@example.com") if instructor else "unknown@example.com",
            "role": getattr(instructor, "role", "instructor") if instructor else "instructor"
        }
        
        # Get enrollment stats (chỉ giữ lại phần đếm tổng số, bỏ qua completed_count vì schema không cần)
        enrollment_count = await Enrollment.find(
            Enrollment.course_id == str(course.id)
        ).count()
        
        # 2. ĐÓNG GÓI CHUẨN XÁC THEO KHUÔN AdminCourseListItem
        courses_data.append({
            "course_id": str(course.id),
            "title": course.title,
            "thumbnail_url": getattr(course, "thumbnail_url", None),
            
            # Thay instructor_id và instructor_name bằng object author
            "author": author_data, 
            
            # Cung cấp 2 trường bắt buộc bằng getattr để chống sập nếu DB cũ thiếu cột này
            "course_type": getattr(course, "course_type", "public"),
            "level": getattr(course, "level", "Beginner"),
            
            "enrollment_count": enrollment_count,
            "status": course.status,
            "category": course.category,
            
            # Bỏ đuôi .isoformat() để Pydantic xử lý
            "created_at": course.created_at, 
            "updated_at": course.updated_at  
        })
    
    # Calculate pagination
    has_next_page = (skip + limit) < total_count

    return {
        "data": courses_data,
        "total": total_count,
        "skip": skip,
        "limit": limit,
        "has_next": has_next_page
    }
    


async def update_course_status_admin(course_id: str, new_status: str, admin_id: str) -> Dict:
    """
    Cập nhật status của course bởi admin
    
    Business Logic:
    1. Validate course existence
    2. Validate status transition rules
    3. Log admin action
    4. Update course status
    
    Args:
        course_id: ID của course
        new_status: Status mới (draft, published, archived)
        admin_id: ID của admin thực hiện action
        
    Returns:
        Dict confirmation
        
    Raises:
        404: Course không tồn tại
        400: Invalid status transition
    """
    # Get course
    course = await Course.get(course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course không tồn tại"
        )
    
    # Validate status values
    valid_statuses = ["draft", "published", "archived"]
    if new_status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Status phải là một trong: {', '.join(valid_statuses)}"
        )
    
    # Check if status is actually changing
    if course.status == new_status:
        return {
            "course_id": str(course.id),
            "message": f"Course đã ở status {new_status}",
            "current_status": course.status
        }
    
    # Update course
    old_status = course.status
    course.status = new_status
    course.updated_at = datetime.utcnow()
    
    try:
        await course.save()
        
        return {
            "course_id": str(course.id),
            "title": course.title,
            "old_status": old_status,
            "new_status": new_status,
            "updated_by": admin_id,
            "updated_at": course.updated_at.isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi cập nhật course status: {str(e)}"
        )


# ============================================================================
# Section 4.3: ADMIN CLASS MONITORING
# ============================================================================

async def get_classes_list_admin(
    page: int = 1,
    limit: int = 20,
    search: Optional[str] = None,
    instructor_filter: Optional[str] = None,
    status_filter: Optional[str] = None,
    sort_by: str = "created_at",
    sort_order: str = "desc"
) -> Dict:
    """
    Lấy danh sách classes cho admin monitoring
    
    Business Logic:
    1. Aggregate classes với instructor info
    2. Calculate student counts và progress stats
    3. Apply filters và pagination
    4. Return formatted class data
    """
    # Build query conditions
    query_conditions = []
    
    # Apply filters
    if instructor_filter:
        query_conditions.append(Class.instructor_id == instructor_filter)
    
    if status_filter:
        query_conditions.append(Class.status == status_filter)
    
    # Apply search
    if search:
        search_conditions = [
            Class.class_name.contains(search, case_insensitive=True),
            Class.description.contains(search, case_insensitive=True)
        ]
        query_conditions.append(Or(*search_conditions))
    
    # Build final query
    if query_conditions:
        query = Class.find(And(*query_conditions))
    else:
        query = Class.find()
    
    # Get total count
    total_count = await query.count()
    
    # Apply sorting
    sort_field = getattr(Class, sort_by, Class.created_at)
    if sort_order == "desc":
        query = query.sort(-sort_field)
    else:
        query = query.sort(sort_field)
    
    # Apply pagination
    skip = (page - 1) * limit
    classes = await query.skip(skip).limit(limit).to_list()
    
    # Format class data - match API_SCHEMA Section 9.13
    classes_data = []
    for class_obj in classes:
        # 1. Get instructor info (Đã thêm kiểm tra an toàn chống lỗi Null)
        instructor_id = getattr(class_obj, "instructor_id", None)
        instructor = await User.get(instructor_id) if instructor_id else None
        instructor_name = instructor.full_name if instructor else "Unknown"
        
        # 2. Get course info (Đã thêm kiểm tra an toàn chống lỗi Null)
        course_id = getattr(class_obj, "course_id", None)
        course = await Course.get(course_id) if course_id else None
        course_title = course.title if course else "Unknown Course"
        
        # 3. Calculate student count (FIX LỖI 500 Ở ĐÂY)
        # Sửa chữ 'students' thành 'student_ids' và dùng getattr để chống sập API
        students_list = getattr(class_obj, "student_ids", [])
        student_count = len(students_list) if students_list else 0
        
        classes_data.append({
            "class_id": str(class_obj.id),
            "class_name": getattr(class_obj, "class_name", "Unknown Class"),
            "course_title": course_title,
            "instructor_name": instructor_name,
            "student_count": student_count,
            "status": getattr(class_obj, "status", "active"),
            "created_at": getattr(class_obj, "created_at", None) # Đã bỏ .isoformat() theo đúng Schema
        })
    
    return {
        "data": classes_data,
        "total": total_count,
        "skip": skip,
        "limit": limit
    }


async def get_class_detail_admin(class_id: str) -> Dict:
    """
    Lấy thông tin chi tiết của một lớp học cho Admin
    """
    # 1. Truy vấn Lớp học
    class_obj = await Class.get(class_id)
    if not class_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy thông tin lớp học"
        )

    # 2. Xử lý An toàn: Thông tin Khóa học
    course_id = getattr(class_obj, "course_id", None)
    course = await Course.get(course_id) if course_id else None
    
    # 3. Xử lý An toàn: Thông tin Giảng viên
    instructor_id = getattr(class_obj, "instructor_id", None)
    instructor = await User.get(instructor_id) if instructor_id else None

    # 4. SỬA LỖI 500: Đếm học viên dựa trên student_ids
    students_list = getattr(class_obj, "student_ids", [])
    student_count = len(students_list) if students_list else 0

    # 5. Tính toán Thống kê lớp học (Bạn có thể cập nhật logic tính toán thực tế sau)
    # Hiện tại cung cấp dữ liệu mặc định để Pydantic Schema không báo lỗi
    class_stats = {
        "average_progress": getattr(class_obj, "average_progress", 0),
        "completion_rate": getattr(class_obj, "completion_rate", 0),
        "active_students_today": getattr(class_obj, "active_students_today", 0)
    }

    # 6. Đóng gói dữ liệu KHỚP TUYỆT ĐỐI VỚI SCHEMA
    return {
        "class_id": str(class_obj.id),
        "class_name": getattr(class_obj, "class_name", "Lớp học chưa đặt tên"),
        
        # Object Course lồng nhau
        "course": {
            "course_id": str(course.id) if course else str(course_id or "Unknown"),
            "title": getattr(course, "title", "Khóa học không xác định") if course else "Khóa học không xác định",
            "category": getattr(course, "category", "Chưa phân loại") if course else "Chưa phân loại"
        },
        
        # Object Instructor lồng nhau
        "instructor": {
            "user_id": str(instructor.id) if instructor else str(instructor_id or "Unknown"),
            "full_name": getattr(instructor, "full_name", "Giảng viên ẩn danh") if instructor else "Giảng viên ẩn danh",
            "email": getattr(instructor, "email", "no-reply@example.com") if instructor else "no-reply@example.com"
        },
        
        "student_count": student_count,
        "invite_code": getattr(class_obj, "invite_code", "N/A"),
        "status": getattr(class_obj, "status", "active"),
        
        # Object Stats lồng nhau
        "class_stats": class_stats,
        
        # Giữ nguyên kiểu dữ liệu Datetime
        "created_at": getattr(class_obj, "created_at", None),
        "start_date": getattr(class_obj, "start_date", None),
        "end_date": getattr(class_obj, "end_date", None)
    }


# ============================================================================
# MISSING FUNCTIONS - IMPLEMENTATION THEO TÀI LIỆU
# ============================================================================

async def change_user_role_admin(user_id: str, new_role: str) -> Dict:
    """
    Thay đổi vai trò người dùng (Section 4.1.6)
    
    Args:
        user_id: ID của user cần thay đổi role
        new_role: Vai trò mới (student|instructor|admin)
        
    Returns:
        Dict chứa thông tin role change
        
    Raises:
        404: User không tồn tại
        400: Invalid role hoặc không thể thay đổi
    """
    # Get user
    user = await User.get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User không tồn tại"
        )
    
    # Validate new role
    valid_roles = ["student", "instructor", "admin"]
    if new_role not in valid_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Role phải là một trong: {', '.join(valid_roles)}"
        )
    
    # Check if role is actually changing
    old_role = user.role
    if old_role == new_role:
        return {
            "user_id": str(user.id),
            "old_role": old_role,
            "new_role": new_role,
            "message": f"User đã có role {new_role}",
            "updated_at": datetime.utcnow().isoformat()
        }
    
    # Update user role
    user.role = new_role
    user.updated_at = datetime.utcnow()
    
    try:
        await user.save()
        
        return {
            "user_id": str(user.id),
            "old_role": old_role,
            "new_role": new_role,
            "impact": f"Vai trò đã được thay đổi thành công sang {user.role}. Các quyền hạn mới đã được áp dụng.",
            "message": f"Vai trò đã được thay đổi từ {old_role} thành {new_role}",
            "updated_at": user.updated_at.isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi thay đổi role: {str(e)}"
        )


async def reset_user_password_admin(user_id: str, new_password: str) -> Dict:
    """
    Reset mật khẩu người dùng (Section 4.1.7)
    
    Args:
        user_id: ID của user cần reset password
        new_password: Mật khẩu mới
        
    Returns:
        Dict confirmation
        
    Raises:
        404: User không tồn tại
        400: Password không hợp lệ
    """
    # Get user
    user = await User.get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User không tồn tại"
        )
    
    # Validate password strength (basic validation)
    if len(new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mật khẩu phải có ít nhất 8 ký tự"
        )
    
    # Hash new password
    user.hashed_password = hash_password(new_password)
    user.updated_at = datetime.utcnow()
    
    try:
        await user.save()
        
        return {
            "user_id": str(user.id),
            "note": f"Mật khẩu đã được reset bởi admin. Mật khẩu mới là: {new_password}",
            "message": "Mật khẩu đã được reset thành công",
            "updated_at": user.updated_at.isoformat(),
            "new_password": new_password  
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi reset password: {str(e)}"
        )


async def create_course_admin(course_data: Dict) -> Dict:
    """
    Tạo khóa học chính thức (Section 4.2.3)
    
    Args:
        course_data: Dict chứa thông tin khóa học
        
    Returns:
        Dict chứa thông tin khóa học mới
    """
    # Create course
    course = Course(
        title=course_data["title"],
        description=course_data["description"],
        instructor_id=course_data.get("creator_id", course_data.get("instructor_id")),
        category=course_data["category"],
        level=course_data["level"],
        status=course_data.get("status", "draft"),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    try:
        await course.save()
        
        # Get instructor info
        instructor = await User.get(course.instructor_id)
        instructor_name = instructor.full_name if instructor else "Unknown"
        
        return {
            "course_id": str(course.id),
            "title": course.title,
            "creator_name": instructor_name,
            "status": course.status,
            "created_at": course.created_at.isoformat(),
            "message": "Khóa học đã được tạo thành công"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi tạo khóa học: {str(e)}"
        )


async def update_course_admin(course_id: str, update_data: Dict) -> Dict:
    """
    Cập nhật khóa học (Section 4.2.4)
    
    Args:
        course_id: ID khóa học
        update_data: Dữ liệu cần cập nhật
        
    Returns:
        Dict confirmation
    """
    # Get course
    course = await Course.get(course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Khóa học không tồn tại"
        )
    
    # Update allowed fields
    allowed_fields = ["title", "description", "category", "level", "status"]
    
    for field, value in update_data.items():
        if field in allowed_fields:
            setattr(course, field, value)
    
    course.updated_at = datetime.utcnow()
    
    try:
        await course.save()
        
        return {
            "course_id": str(course.id),
            "message": "Khóa học đã được cập nhật",
            "updated_at": course.updated_at.isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi cập nhật khóa học: {str(e)}"
        )


async def delete_course_admin(course_id: str) -> Dict:
    """
    Xóa khóa học (Section 4.2.5)
    
    Args:
        course_id: ID khóa học cần xóa
        
    Returns:
        Dict confirmation
    """
    # Get course
    course = await Course.get(course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Khóa học không tồn tại"
        )
    
    # Check for active enrollments
    active_enrollments = await Enrollment.find(
        Enrollment.course_id == course_id,
        Enrollment.status.in_(["active", "completed"])
    ).count()
    
    if active_enrollments > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Không thể xóa khóa học có {active_enrollments} học viên đang học"
        )
    
    # Check for classes using this course
    classes_using_course = await Class.find(
        Class.course_id == course_id
    ).count()
    
    if classes_using_course > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Không thể xóa khóa học được sử dụng bởi {classes_using_course} lớp học"
        )
    
    try:
        await course.delete()
        
        return {
            "message": "Khóa học đã được xóa vĩnh viễn"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi xóa khóa học: {str(e)}"
        )