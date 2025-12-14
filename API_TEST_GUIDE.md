# 📚 HƯỚNG DẪN TEST API - AI LEARNING PLATFORM

> **URL Swagger UI**: http://localhost:8000/docs  
> **Tổng số API**: **84 endpoints**  
> **Ngày tạo**: 04/12/2025  
> **Cơ sở dữ liệu**: MongoDB với dữ liệu mẫu từ `scripts/init_data.py`

---

## 🚀 BƯỚC CHUẨN BỊ

### 1. Khởi động Server
```bash
cd BELEARNINGAI
uvicorn app.main:app --reload
```

### 2. Khởi tạo Dữ liệu Mẫu
```bash
python -m scripts.init_data
```

### 3. Truy cập Swagger UI
- **URL**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

---

## 👥 TÀI KHOẢN TEST CÓ SẴN

### 🔑 Admin Account
```json
{
  "email": "admin.super@ailab.com.vn",
  "password": "Admin@12345",
  "role": "admin"
}
```

### 👨‍🏫 Instructor Accounts
```json
{
  "email": "tuananh.nguyen@ailab.edu.vn",
  "password": "Giangvien@123",
  "role": "instructor"
}
{
  "email": "tuyet.le@ailab.edu.vn", 
  "password": "Giangvien@123",
  "role": "instructor"
}
{
  "email": "hung.tran@ailab.edu.vn",
  "password": "Giangvien@123", 
  "role": "instructor"
}
```

### 🎓 Student Accounts
```json
{
  "email": "student1@example.com",
  "password": "Hocvien@123",
  "role": "student"
}
```
> **Lưu ý**: Script tạo 10 tài khoản học viên với email ngẫu nhiên và password `Hocvien@123`. 

### 🔍 Cách tìm các ID cần thiết để test:
1. **Course IDs**: GET `/api/v1/courses/public` hoặc search "Python" 
2. **User IDs**: GET `/api/v1/admin/users` (admin only)
3. **Lesson IDs**: GET `/api/v1/courses/{course_id}/detail` 
4. **Class IDs**: GET `/api/v1/classes` (instructor only)
5. **Quiz IDs**: Từ lesson detail có `quiz_id` field

---

## 🔐 CÁCH SỬ DỤNG AUTHENTICATION

### Bước 1: Đăng nhập
1. Mở Swagger UI → Tìm section **Authentication**
2. Click **POST /api/v1/auth/login**
3. Click **Try it out**
4. Nhập dữ liệu:
```json
{
  "email": "admin.super@ailab.com.vn",
  "password": "Admin@12345",
  "remember_me": true
}
```
5. Click **Execute**
6. **Copy `access_token`** từ response

### Bước 2: Authorize
1. Click nút **🔒 Authorize** ở đầu trang Swagger
2. Nhập: `Bearer <your_access_token>`
3. Click **Authorize**
4. Bây giờ có thể test các API protected!

---

## 📖 TEST CASES CHO TỪNG NHÓM API

## 1️⃣ AUTHENTICATION & USER MANAGEMENT (Section 2.1)

### 🆕 POST /api/v1/auth/register - Đăng ký tài khoản mới
```json
{
  "full_name": "Nguyễn Văn Test",
  "email": "testuser@example.com",
  "password": "TestPassword@123"
}
```
**Expected**: 201 Created với thông tin user mới

### 🔑 POST /api/v1/auth/login - Đăng nhập
```json
{
  "email": "admin.super@ailab.com.vn",
  "password": "Admin@12345",
  "remember_me": true
}
```
**Expected**: 200 OK với access_token và refresh_token

### 🚪 POST /api/v1/auth/logout - Đăng xuất
**Headers**: Authorization: Bearer <token>
```json
{}
```
**Expected**: 200 OK với message thành công

### 👤 GET /api/v1/users/me - Xem thông tin cá nhân
**Headers**: Authorization: Bearer <token>
**Expected**: 200 OK với thông tin user đang đăng nhập

### ✏️ PATCH /api/v1/users/me - Cập nhật thông tin
**Headers**: Authorization: Bearer <token>
```json
{
  "full_name": "Nguyễn Văn Test Updated",
  "bio": "Tôi là một lập trình viên đam mê học hỏi",
  "learning_preferences": ["Programming", "Data Science"],
  "contact_info": "Phone: 0987654321"
}
```
**Expected**: 200 OK với thông tin đã cập nhật

---

## 2️⃣ AI ASSESSMENT (Section 2.2)

### 🧠 POST /api/v1/assessments/generate - Tạo bộ câu hỏi đánh giá
**Headers**: Authorization: Bearer <token>
```json
{
  "category": "Programming",
  "subject": "Python",
  "level": "Beginner",
  "focus_areas": ["python-syntax", "python-basics"]
}
```
**Expected**: 201 Created với `session_id` và danh sách câu hỏi
**Lưu ý**: Lưu `session_id` để test bước tiếp theo

### 📝 POST /api/v1/assessments/{session_id}/submit - Nộp bài đánh giá
**Path**: Thay `{session_id}` bằng ID từ bước trước
**Headers**: Authorization: Bearer <token>
```json
{
  "answers": [
    {
      "question_id": "question-uuid-1",
      "answer_content": "list = []",
      "selected_option": 1,
      "time_taken_seconds": 45
    },
    {
      "question_id": "question-uuid-2", 
      "answer_content": "def my_function():",
      "time_taken_seconds": 60
    }
  ],
  "total_time_seconds": 900,
  "submitted_at": "2025-12-04T10:30:00Z"
}
```
**Expected**: 200 OK với status submitted

### 📊 GET /api/v1/assessments/{session_id}/results - Xem kết quả đánh giá
**Path**: Thay `{session_id}` bằng ID từ bước generate
**Headers**: Authorization: Bearer <token>
**Expected**: 200 OK với điểm số, phân tích skill, knowledge gaps

### 💡 GET /api/v1/recommendations/from-assessment - Lộ trình học tập từ đánh giá
**Headers**: Authorization: Bearer <token>
**Expected**: 200 OK với danh sách khóa học được đề xuất

### 🧠 POST /api/v1/courses/{course_id}/modules/{module_id}/assessments/generate - Tạo quiz từ module
**Path**: Thay các ID tương ứng
**Headers**: Authorization: Bearer <token>
```json
{
  "difficulty": "medium",
  "question_count": 15,
  "include_mandatory": true,
  "focus_outcomes": ["python-syntax", "python-functions"]
}
```
**Expected**: 201 Created với quiz được AI tạo từ module content

---

## 🔟 DASHBOARD & RECOMMENDATIONS (Section 2.7) - 4 endpoints

### 📊 GET /api/v1/dashboard/student - Dashboard học viên
**Headers**: Authorization: Bearer <token>
**Expected**: 200 OK với:
- Danh sách khóa học đang học (progress %)
- Quiz pending cần làm
- Achievements gần đây
- Study streak (chuỗi học liên tục)
- Thống kê tổng quan (lessons completed, avg quiz score)

### 👨‍🏫 GET /api/v1/dashboard/instructor - Dashboard giảng viên
**Headers**: Authorization: Bearer <instructor_token>
**Expected**: 200 OK với:
- Số lớp học đang dạy
- Tổng số học viên
- Quiz đã tạo
- Tỷ lệ hoàn thành trung bình
- Quick actions (tạo quiz, xem progress)

### 🛠️ GET /api/v1/dashboard/admin - Dashboard admin
**Headers**: Authorization: Bearer <admin_token>
**Expected**: 200 OK với:
- Tổng users/courses/classes
- Thống kê theo role
- Hoạt động hệ thống (enrollments mới, quiz completed)
- System health metrics

### 💡 GET /api/v1/recommendations - Đề xuất khóa học
**Headers**: Authorization: Bearer <token>
**Query Parameters**:
- `type`: "similar_courses" hoặc "based_on_progress" hoặc "popular"
- `category`: "Programming" (optional)
- `limit`: 5

**Expected**: 200 OK với danh sách khóa học đề xuất dựa trên AI analysis

---

## 3️⃣ COURSE DISCOVERY (Section 2.3)

### 🔍 GET /api/v1/courses/search - Tìm kiếm khóa học
**Query Parameters**:
- `keyword`: "Python" 
- `category`: "Programming"
- `level`: "Beginner"
- `skip`: 0
- `limit`: 10

**Expected**: 200 OK với danh sách khóa học Python

### 📚 GET /api/v1/courses/public - Danh sách khóa học công khai
**Query Parameters**:
- `skip`: 0
- `limit`: 10
- `sort_by`: "created_at"
- `order`: "desc"

**Expected**: 200 OK với danh sách tất cả khóa học

### 📖 GET /api/v1/courses/{course_id}/detail - Chi tiết khóa học
**Path**: Thay `{course_id}` bằng ID khóa học Python từ search
**Headers**: Authorization: Bearer <token>
**Expected**: 200 OK với thông tin đầy đủ khóa học, modules, lessons

### ✅ GET /api/v1/courses/{course_id}/enrollment-status - Trạng thái đăng ký
**Path**: Thay `{course_id}` bằng ID khóa học
**Headers**: Authorization: Bearer <token>
**Expected**: 200 OK với trạng thái enrolled/not_enrolled

---

## 4️⃣ ENROLLMENT (Section 2.3)

### 📝 POST /api/v1/enrollments - Đăng ký khóa học
**Headers**: Authorization: Bearer <token>
```json
{
  "course_id": "course-uuid-from-search"
}
```
**Expected**: 201 Created với enrollment record

### 📋 GET /api/v1/enrollments/my-courses - Danh sách khóa học đã đăng ký
**Headers**: Authorization: Bearer <token>
**Query Parameters**:
- `status`: "active"
- `skip`: 0
- `limit`: 10

**Expected**: 200 OK với danh sách khóa học đã enroll

### 📊 GET /api/v1/enrollments/{enrollment_id}/detail - Chi tiết enrollment
**Path**: Thay `{enrollment_id}` bằng ID từ my-courses
**Headers**: Authorization: Bearer <token>
**Expected**: 200 OK với thông tin chi tiết enrollment

### ❌ DELETE /api/v1/enrollments/{enrollment_id} - Hủy đăng ký
**Path**: Thay `{enrollment_id}` bằng ID enrollment
**Headers**: Authorization: Bearer <token>
**Expected**: 200 OK với message hủy thành công

---

## 5️⃣ LEARNING PROGRESS (Section 2.4)

### 📚 GET /api/v1/learning/courses - Khóa học đang học
**Headers**: Authorization: Bearer <token>
**Expected**: 200 OK với danh sách khóa học + progress

### 📖 GET /api/v1/learning/courses/{course_id} - Chi tiết học tập khóa học
**Path**: Thay `{course_id}` bằng ID khóa học đã enroll
**Headers**: Authorization: Bearer <token>
**Expected**: 200 OK với modules, lessons, progress từng lesson

### ▶️ POST /api/v1/learning/lessons/{lesson_id}/start - Bắt đầu học bài
**Path**: Thay `{lesson_id}` bằng ID lesson từ course detail
**Headers**: Authorization: Bearer <token>
```json
{
  "started_at": "2025-12-04T10:30:00Z"
}
```
**Expected**: 200 OK với session bắt đầu học

### ✅ POST /api/v1/learning/lessons/{lesson_id}/complete - Hoàn thành bài học
**Path**: Thay `{lesson_id}` bằng ID lesson đã start
**Headers**: Authorization: Bearer <token>
```json
{
  "completed_at": "2025-12-04T11:00:00Z",
  "time_spent_minutes": 30,
  "completion_percentage": 100,
  "notes": "Đã hiểu về cú pháp Python cơ bản"
}
```
**Expected**: 200 OK với progress updated

---

## 6️⃣ QUIZ SYSTEM (Section 2.4)

### 📝 GET /api/v1/quiz/{quiz_id}/detail - Chi tiết quiz
**Path**: Thay `{quiz_id}` bằng ID quiz từ lesson
**Headers**: Authorization: Bearer <token>
**Expected**: 200 OK với câu hỏi quiz

### ✍️ POST /api/v1/quiz/{quiz_id}/attempt - Làm bài quiz
**Path**: Thay `{quiz_id}` bằng ID quiz
**Headers**: Authorization: Bearer <token>
```json
{
  "answers": [
    {
      "question_id": "quiz-question-1",
      "selected_answer": "A",
      "time_taken_seconds": 30
    },
    {
      "question_id": "quiz-question-2",
      "selected_answer": "C", 
      "time_taken_seconds": 45
    }
  ],
  "total_time_seconds": 300
}
```
**Expected**: 200 OK với attempt_id

### 📊 GET /api/v1/quiz/{quiz_id}/results/{attempt_id} - Kết quả quiz
**Path**: Thay `{quiz_id}` và `{attempt_id}` bằng ID tương ứng
**Headers**: Authorization: Bearer <token>
**Expected**: 200 OK với điểm số và giải thích

### 🔄 POST /api/v1/quiz/{quiz_id}/retake - Làm lại quiz
**Path**: Thay `{quiz_id}` bằng ID quiz
**Headers**: Authorization: Bearer <token>
```json
{
  "reason": "Muốn cải thiện điểm số"
}
```
**Expected**: 200 OK cho phép làm lại

---

## 7️⃣ PROGRESS TRACKING (Section 2.4)

### 📈 GET /api/v1/progress/overall - Tổng quan tiến độ học tập
**Headers**: Authorization: Bearer <token>
**Expected**: 200 OK với tổng quan progress tất cả khóa học

### 📊 GET /api/v1/progress/courses/{course_id} - Tiến độ khóa học cụ thể
**Path**: Thay `{course_id}` bằng ID khóa học
**Headers**: Authorization: Bearer <token>
**Expected**: 200 OK với progress chi tiết từng module/lesson

### 📝 GET /api/v1/progress/courses/{course_id}/analytics - Phân tích học tập
**Path**: Thay `{course_id}` bằng ID khóa học
**Headers**: Authorization: Bearer <token>
**Expected**: 200 OK với thống kê thời gian học, performance

### ⏱️ POST /api/v1/progress/time-tracking - Ghi nhận thời gian học
**Headers**: Authorization: Bearer <token>
```json
{
  "course_id": "course-uuid",
  "lesson_id": "lesson-uuid", 
  "session_start": "2025-12-04T10:00:00Z",
  "session_end": "2025-12-04T10:30:00Z",
  "activity_type": "reading"
}
```
**Expected**: 200 OK với time tracking updated

---

## 8️⃣ PERSONAL COURSES (Section 2.5) - 5 endpoints

### 🤖 POST /api/v1/personal-courses/ai-generate - Tạo khóa học từ AI prompt
**Headers**: Authorization: Bearer <token>
```json
{
  "prompt": "Tôi muốn học lập trình Python từ cơ bản đến nâng cao, bao gồm web development và machine learning",
  "category": "Programming",
  "level": "Intermediate"
}
```
**Expected**: 201 Created với khóa học được AI tạo tự động (modules + lessons)

### 📚 GET /api/v1/personal-courses - Khóa học cá nhân
**Headers**: Authorization: Bearer <token>
**Query Parameters**:
- `status`: "draft" hoặc "published" hoặc "archived"
- `skip`: 0
- `limit`: 10

**Expected**: 200 OK với danh sách khóa học cá nhân + thống kê

### ➕ POST /api/v1/personal-courses - Tạo khóa học thủ công
**Headers**: Authorization: Bearer <token>
```json
{
  "title": "Khóa học Python cá nhân của tôi",
  "description": "Tự học Python theo lộ trình cá nhân, từ syntax cơ bản đến ứng dụng thực tế",
  "category": "Programming",
  "level": "Beginner",
  "thumbnail_url": "https://example.com/python-thumb.jpg",
  "language": "vi"
}
```
**Expected**: 201 Created với khóa học mới (trạng thái draft)

### ✏️ PUT /api/v1/personal-courses/{course_id} - Cập nhật khóa học
**Path**: Thay `{course_id}` bằng ID personal course
**Headers**: Authorization: Bearer <token>
```json
{
  "title": "Khóa học Python nâng cao",
  "description": "Cập nhật mô tả khóa học với nội dung chi tiết hơn",
  "status": "published",
  "modules": [
    {
      "title": "Module 1: Python Cơ bản",
      "description": "Học syntax và concepts cơ bản",
      "order": 1,
      "difficulty": "Basic",
      "estimated_hours": 10,
      "learning_outcomes": ["Hiểu cú pháp Python", "Viết được functions"],
      "lessons": [
        {
          "title": "Biến và Kiểu dữ liệu",
          "order": 1,
          "content": "<h2>Variables trong Python</h2><p>Python hỗ trợ nhiều kiểu dữ liệu...</p>",
          "content_type": "text",
          "duration_minutes": 30
        }
      ]
    }
  ]
}
```
**Expected**: 200 OK với khóa học và modules đã cập nhật

### 🗑️ DELETE /api/v1/personal-courses/{course_id} - Xóa khóa học
**Path**: Thay `{course_id}` bằng ID personal course
**Headers**: Authorization: Bearer <token>
**Expected**: 200 OK với message xóa thành công

### 📊 GET /api/v1/personal-courses/{course_id}/progress - Tiến độ khóa học cá nhân
**Path**: Thay `{course_id}` bằng ID personal course
**Headers**: Authorization: Bearer <token>
**Expected**: 200 OK với thống kê progress

---

## 9️⃣ AI CHATBOT (Section 2.6)

### 💬 GET /api/v1/chat/conversations - Danh sách cuộc trò chuyện
**Headers**: Authorization: Bearer <token>
**Query Parameters**:
- `skip`: 0
- `limit`: 10

**Expected**: 200 OK với danh sách conversations

### 🆕 POST /api/v1/chat/conversations - Tạo cuộc trò chuyện mới
**Headers**: Authorization: Bearer <token>
```json
{
  "title": "Hỏi về Python cơ bản",
  "context": "Tôi đang học Python và cần hỗ trợ"
}
```
**Expected**: 201 Created với conversation mới

### 📤 POST /api/v1/chat/conversations/{conversation_id}/message - Gửi tin nhắn
**Path**: Thay `{conversation_id}` bằng ID conversation
**Headers**: Authorization: Bearer <token>
```json
{
  "message": "Làm thế nào để khai báo list trong Python?",
  "message_type": "question"
}
```
**Expected**: 200 OK với phản hồi từ AI

### 📜 GET /api/v1/chat/conversations/{conversation_id}/history - Lịch sử trò chuyện
**Path**: Thay `{conversation_id}` bằng ID conversation
**Headers**: Authorization: Bearer <token>
**Expected**: 200 OK với toàn bộ lịch sử chat

### 🗑️ DELETE /api/v1/chat/conversations/{conversation_id} - Xóa cuộc trò chuyện
**Path**: Thay `{conversation_id}` bằng ID conversation
**Headers**: Authorization: Bearer <token>
**Expected**: 200 OK với message xóa thành công

---

## 🔟 DASHBOARD & RECOMMENDATIONS (Section 2.7)

### 📊 GET /api/v1/dashboard/student - Dashboard học viên
**Headers**: Authorization: Bearer <token>
**Expected**: 200 OK với tổng quan stats học viên

### 💡 GET /api/v1/recommendations - Đề xuất khóa học
**Headers**: Authorization: Bearer <token>
**Query Parameters**:
- `type`: "similar_courses"
- `limit`: 5

**Expected**: 200 OK với danh sách khóa học đề xuất

### 📈 GET /api/v1/analytics/learning-time - Thống kê thời gian học
**Headers**: Authorization: Bearer <token>
**Query Parameters**:
- `period`: "last_30_days"

**Expected**: 200 OK với biểu đồ thời gian học

### 🏆 GET /api/v1/analytics/achievements - Thành tích học tập
**Headers**: Authorization: Bearer <token>
**Expected**: 200 OK với danh sách achievements

---

## 1️⃣1️⃣ INSTRUCTOR FEATURES (Section 3.x) - 10 endpoints

### 📚 POST /api/v1/classes - Tạo lớp học mới (Instructor)
**Headers**: Authorization: Bearer <instructor_token>
```json
{
  "name": "Lớp Python Cơ bản Tháng 12",
  "description": "Lớp học Python dành cho người mới bắt đầu",
  "course_id": "course-uuid-from-search-python",
  "max_students": 30,
  "start_date": "2025-12-15T09:00:00Z",
  "end_date": "2026-02-15T17:00:00Z"
}
```
**Expected**: 201 Created với class mới và invite_code

### 👥 GET /api/v1/classes - Danh sách lớp học
**Headers**: Authorization: Bearer <instructor_token>
**Query Parameters**:
- `status`: "active" 
- `skip`: 0
- `limit`: 10

**Expected**: 200 OK với danh sách lớp do giảng viên quản lý

### 📖 GET /api/v1/classes/{class_id} - Chi tiết lớp học
**Path**: Thay `{class_id}` bằng ID từ danh sách classes
**Headers**: Authorization: Bearer <instructor_token>
**Expected**: 200 OK với thông tin chi tiết lớp học

### ✏️ PUT /api/v1/classes/{class_id} - Cập nhật lớp học
**Path**: Thay `{class_id}` bằng ID class
**Headers**: Authorization: Bearer <instructor_token>
```json
{
  "name": "Lớp Python Nâng cao",
  "description": "Cập nhật mô tả lớp học",
  "max_students": 25
}
```
**Expected**: 200 OK với thông tin đã cập nhật

### 🗑️ DELETE /api/v1/classes/{class_id} - Xóa lớp học
**Path**: Thay `{class_id}` bằng ID class
**Headers**: Authorization: Bearer <instructor_token>
**Expected**: 200 OK với message xóa thành công

### ➕ POST /api/v1/classes/{class_id}/students - Thêm học viên vào lớp
**Path**: Thay `{class_id}` bằng ID class
**Headers**: Authorization: Bearer <instructor_token>
```json
{
  "user_id": "student-uuid",
  "enrollment_method": "invite_code"
}
```
**Expected**: 201 Created với enrollment thành công

### 👥 GET /api/v1/classes/{class_id}/students - Danh sách học viên trong lớp
**Path**: Thay `{class_id}` bằng ID class
**Headers**: Authorization: Bearer <instructor_token>
**Expected**: 200 OK với danh sách students + progress

### 📊 GET /api/v1/classes/{class_id}/student/{student_id} - Chi tiết học viên
**Path**: Thay các ID tương ứng
**Headers**: Authorization: Bearer <instructor_token>
**Expected**: 200 OK với progress chi tiết của học viên

### 🚫 DELETE /api/v1/classes/{class_id}/students/{student_id} - Xóa học viên khỏi lớp
**Path**: Thay các ID tương ứng  
**Headers**: Authorization: Bearer <instructor_token>
**Expected**: 200 OK với message xóa thành công

### 📈 GET /api/v1/classes/{class_id}/analytics - Analytics lớp học
**Path**: Thay `{class_id}` bằng ID class
**Headers**: Authorization: Bearer <instructor_token>
**Expected**: 200 OK với thống kê chi tiết về lớp học

---

## 1️⃣2️⃣ ADMIN FEATURES (Section 4.x) - 18 endpoints

### 📊 GET /api/v1/admin/dashboard - Dashboard admin tổng quan
**Headers**: Authorization: Bearer <admin_token>
**Expected**: 200 OK với thống kê chi tiết:
```json
{
  "total_users": 15,
  "users_by_role": {
    "student": 10,
    "instructor": 4,
    "admin": 1
  },
  "total_courses": 5,
  "courses_stats": {
    "published": 3,
    "draft": 2
  },
  "total_classes": 8,
  "active_classes": 5,
  "total_enrollments": 25
}
```

### 👥 GET /api/v1/admin/users - Quản lý người dùng (Admin)
**Headers**: Authorization: Bearer <admin_token>
**Query Parameters**:
- `role`: "student" hoặc "instructor" hoặc "admin"
- `status`: "active" hoặc "inactive"
- `search`: "tên user hoặc email" (tìm kiếm)
- `skip`: 0, `limit`: 10

**Expected**: 200 OK với danh sách users:
```json
{
  "data": [
    {
      "user_id": "uuid",
      "full_name": "Nguyễn Văn A",
      "email": "student1@example.com",
      "avatar": "https://...",
      "role": "student",
      "status": "active",
      "created_at": "2025-01-01T00:00:00Z",
      "last_login": "2025-01-03T15:30:00Z",
      "enrollment_count": 3
    }
  ],
  "total": 15,
  "skip": 0,
  "limit": 10,
  "has_next": true
}
```

### 🔍 GET /api/v1/admin/users/{user_id} - Chi tiết người dùng
**Path**: Thay `{user_id}` bằng UUID user
**Headers**: Authorization: Bearer <admin_token>
**Expected**: 200 OK với thông tin chi tiết:
```json
{
  "user_id": "uuid",
  "full_name": "Nguyễn Văn A",
  "email": "student1@example.com",
  "role": "student",
  "status": "active",
  "statistics": {
    "enrolled_courses": 3,
    "completed_courses": 1,
    "average_score": 85.5
  },
  "current_enrollments": [
    {
      "course_id": "course-uuid",
      "course_title": "Python Cơ Bản",
      "progress": 75.0,
      "status": "in-progress"
    }
  ]
}
```

### ➕ POST /api/v1/admin/users - Tạo người dùng mới
**Headers**: Authorization: Bearer <admin_token>
```json
{
  "full_name": "Giảng Viên Mới",
  "email": "newteacher@ailab.edu.vn", 
  "password": "TempPassword@123",
  "role": "instructor",
  "bio": "Giảng viên chuyên về AI"
}
```
**Expected**: 201 Created với user mới

### ✏️ PUT /api/v1/admin/users/{user_id} - Cập nhật thông tin user
**Path**: Thay `{user_id}` bằng UUID user
**Headers**: Authorization: Bearer <admin_token>
```json
{
  "full_name": "Tên mới", 
  "bio": "Bio mới",
  "status": "inactive"
}
```
**Expected**: 200 OK với user đã cập nhật

### 🔄 PUT /api/v1/admin/users/{user_id}/role - Thay đổi role user
**Path**: Thay `{user_id}` bằng UUID user
**Headers**: Authorization: Bearer <admin_token>
```json
{
  "new_role": "instructor"
}
```
**Expected**: 200 OK với thông tin impact (ảnh hưởng đến classes, enrollments)

### 🔑 POST /api/v1/admin/users/{user_id}/reset-password - Reset mật khẩu
**Path**: Thay `{user_id}` bằng UUID user
**Headers**: Authorization: Bearer <admin_token>
```json
{
  "new_password": "NewTempPassword@123"
}
```
**Expected**: 200 OK với message confirm

### 🗑️ DELETE /api/v1/admin/users/{user_id} - Xóa người dùng
**Path**: Thay `{user_id}` bằng UUID user (test với user không có enrollment)
**Headers**: Authorization: Bearer <admin_token>
**Expected**: 200 OK với message confirm deletion

### 📚 GET /api/v1/admin/courses - Quản lý khóa học
**Headers**: Authorization: Bearer <admin_token>
**Query Parameters**:
- `status`: "published" hoặc "draft"
- `course_type`: "public" hoặc "personal"
- `author_id`: UUID của tác giả
- `skip`: 0, `limit`: 10

**Expected**: 200 OK với tất cả khóa học trong hệ thống

### 🔍 GET /api/v1/admin/courses/{course_id} - Chi tiết khóa học (Admin)
**Path**: Thay `{course_id}` bằng UUID course
**Headers**: Authorization: Bearer <admin_token>
**Expected**: 200 OK với chi tiết đầy đủ course + analytics

### ➕ POST /api/v1/admin/courses - Tạo khóa học mới (Admin)
**Headers**: Authorization: Bearer <admin_token>
```json
{
  "title": "Khóa học AI cơ bản",
  "description": "Khóa học về AI dành cho người mới bắt đầu...",
  "category": "Technology",
  "level": "Beginner",
  "language": "vi",
  "thumbnail_url": "https://example.com/thumb.jpg",
  "prerequisites": ["Kiến thức máy tính cơ bản"],
  "learning_outcomes": [
    {"description": "Hiểu được AI là gì"}
  ],
  "status": "published"
}
```
**Expected**: 201 Created với course mới

### ✏️ PUT /api/v1/admin/courses/{course_id} - Cập nhật khóa học
**Path**: Thay `{course_id}` bằng UUID course
**Headers**: Authorization: Bearer <admin_token>
```json
{
  "title": "Tiêu đề mới",
  "description": "Mô tả mới...",
  "status": "archived"
}
```
**Expected**: 200 OK với thông tin đã update

### 🗑️ DELETE /api/v1/admin/courses/{course_id} - Xóa khóa học
**Path**: Thay `{course_id}` bằng UUID course (test với course ít ảnh hưởng)
**Headers**: Authorization: Bearer <admin_token>
**Expected**: 200 OK với thông tin impact và confirm deletion

### 🏫 GET /api/v1/admin/classes - Quản lý lớp học admin
**Headers**: Authorization: Bearer <admin_token>
**Query Parameters**:
- `status`: "preparing", "active", "completed"
- `instructor_id`: UUID giảng viên
- `skip`: 0, `limit`: 10

**Expected**: 200 OK với danh sách classes:
```json
{
  "data": [
    {
      "class_id": "uuid",
      "class_name": "Lớp Python Cơ Bản - Batch 1",
      "instructor_name": "Nguyễn Văn Giảng",
      "instructor_email": "instructor@example.com",
      "course_title": "Python Cơ Bản",
      "student_count": 15,
      "max_students": 20,
      "status": "active",
      "start_date": "2025-01-01T00:00:00Z",
      "end_date": "2025-03-01T00:00:00Z",
      "created_at": "2024-12-15T00:00:00Z"
    }
  ],
  "total": 8,
  "has_next": false
}
```

### 🏫 GET /api/v1/admin/classes/{class_id} - Chi tiết lớp học admin
**Path**: Thay `{class_id}` bằng UUID lớp học
**Headers**: Authorization: Bearer <admin_token>
**Expected**: 200 OK với thông tin chi tiết:
```json
{
  "class_id": "uuid",
  "class_name": "Lớp Python Cơ Bản - Batch 1",
  "description": "Lớp học dành cho người mới bắt đầu",
  "course_id": "course-uuid",
  "course_title": "Python Cơ Bản",
  "invite_code": "PYTHON2025",
  "status": "active",
  "start_date": "2025-01-01T00:00:00Z",
  "end_date": "2025-03-01T00:00:00Z",
  "max_students": 20,
  "instructor_info": {
    "instructor_id": "instructor-uuid",
    "instructor_name": "Nguyễn Văn Giảng",
    "instructor_email": "instructor@example.com",
    "total_classes": 3,
    "total_students_taught": 45
  },
  "students": [
    {
      "student_id": "student-uuid",
      "student_name": "Nguyễn Văn A",
      "student_email": "student1@example.com",
      "progress": 75.0,
      "lessons_completed": 15,
      "avg_quiz_score": 85.5,
      "last_activity": "2025-01-03T15:30:00Z",
      "joined_at": "2025-01-01T00:00:00Z",
      "enrollment_status": "enrolled"
    }
  ],
  "stats": {
    "total_students": 15,
    "active_students": 14,
    "avg_progress": 68.5,
    "avg_quiz_score": 82.3,
    "completion_rate": 75.0,
    "total_lessons": 20,
    "total_quizzes": 10
  }
}
```

### 📈 GET /api/v1/admin/system/users-growth - Thống kê tăng trưởng users
**Headers**: Authorization: Bearer <admin_token>
**Query Parameters**:
- `period`: "last_30_days" hoặc "last_90_days" hoặc "last_year"

**Expected**: 200 OK với biểu đồ tăng trưởng users

### 📊 GET /api/v1/admin/system/course-analytics - Phân tích khóa học
**Headers**: Authorization: Bearer <admin_token>
**Expected**: 200 OK với thống kê về các khóa học

### ⚡ GET /api/v1/admin/system/health - Tình trạng hệ thống
**Headers**: Authorization: Bearer <admin_token>
**Expected**: 200 OK với health metrics hệ thống

---

## 1️⃣3️⃣ ANALYTICS FEATURES (Section 2.7, 3.4, 4.4) - 8 endpoints

### 📊 GET /api/v1/analytics/learning-stats - Thống kê học tập chi tiết (Student)
**Headers**: Authorization: Bearer <token>
**Expected**: 200 OK với metrics học tập của student

### 📈 GET /api/v1/analytics/progress-chart - Biểu đồ tiến độ (Student)
**Headers**: Authorization: Bearer <token>
**Query Parameters**:
- `period`: "last_30_days"
- `course_id`: "course-uuid" (optional)

**Expected**: 200 OK với dữ liệu biểu đồ tiến độ

### 👨‍🏫 GET /api/v1/analytics/instructor/class-stats - Thống kê lớp học (Instructor)
**Headers**: Authorization: Bearer <instructor_token>
**Query Parameters**:
- `class_id`: "class-uuid" (optional)

**Expected**: 200 OK với thống kê các lớp dạy

### 📊 GET /api/v1/analytics/instructor/progress-chart - Biểu đồ tiến độ lớp (Instructor)
**Headers**: Authorization: Bearer <instructor_token>
**Query Parameters**:
- `class_id`: "class-uuid"
- `period`: "last_30_days"

**Expected**: 200 OK với dữ liệu tiến độ học viên

### 📝 GET /api/v1/analytics/instructor/quiz-performance - Hiệu suất quiz (Instructor)
**Headers**: Authorization: Bearer <instructor_token>
**Query Parameters**:
- `class_id`: "class-uuid"

**Expected**: 200 OK với phân tích hiệu suất quiz

### 🏢 GET /api/v1/analytics/admin/users-growth - Tăng trưởng users (Admin)
**Headers**: Authorization: Bearer <admin_token>
**Query Parameters**:
- `period`: "last_90_days"

**Expected**: 200 OK với dữ liệu tăng trưởng

### 📚 GET /api/v1/analytics/admin/course-analytics - Phân tích khóa học (Admin)
**Headers**: Authorization: Bearer <admin_token>
**Expected**: 200 OK với thống kê toàn bộ khóa học

### ⚡ GET /api/v1/analytics/admin/system-health - Sức khỏe hệ thống (Admin)
**Headers**: Authorization: Bearer <admin_token>
**Expected**: 200 OK với metrics hệ thống

---

## 1️⃣4️⃣ CHAT AI FEATURES (Section 2.6) - 5 endpoints

### 💬 POST /api/v1/chat/course/{course_id} - Gửi câu hỏi cho AI
**Path**: Thay `{course_id}` bằng UUID course đã enroll
**Headers**: Authorization: Bearer <token>
```json
{
  "question": "Làm thế nào để khai báo list trong Python?",
  "conversation_id": null
}
```
**Expected**: 201 Created với câu trả lời từ AI + sources từ lessons

### 📜 GET /api/v1/chat/history - Lịch sử conversations
**Headers**: Authorization: Bearer <token>
**Query Parameters**:
- `course_id`: "course-uuid" (optional filter)
- `skip`: 0
- `limit`: 10

**Expected**: 200 OK với danh sách conversations

### 🔍 GET /api/v1/chat/conversations/{conversation_id} - Chi tiết conversation
**Path**: Thay `{conversation_id}` bằng ID từ history
**Headers**: Authorization: Bearer <token>
**Expected**: 200 OK với toàn bộ messages trong conversation

### 🗑️ DELETE /api/v1/chat/conversations - Xóa toàn bộ lịch sử
**Headers**: Authorization: Bearer <token>
**Expected**: 200 OK với số lượng conversations đã xóa

### 🗑️ DELETE /api/v1/chat/history/{conversation_id} - Xóa một conversation
**Path**: Thay `{conversation_id}` bằng ID conversation
**Headers**: Authorization: Bearer <token>
**Expected**: 200 OK với message xóa thành công

---

## 1️⃣5️⃣ SEARCH FEATURES (Section 5.1) - 4 endpoints

### 🔍 GET /api/v1/search/global - Tìm kiếm toàn hệ thống
**Query Parameters**:
- `q`: "Python"
- `type`: "all"
- `skip`: 0
- `limit`: 10

**Expected**: 200 OK với kết quả mixed (courses, lessons, users)

### 🔍 GET /api/v1/search/courses - Tìm kiếm khóa học
**Query Parameters**:
- `q`: "machine learning"
- `category`: "Programming"

**Expected**: 200 OK với danh sách khóa học liên quan

### 📝 GET /api/v1/search/suggestions - Gợi ý tìm kiếm
**Query Parameters**:
- `partial`: "pytho"

**Expected**: 200 OK với danh sách gợi ý từ khóa

### 📜 GET /api/v1/search/history - Lịch sử tìm kiếm
**Headers**: Authorization: Bearer <token>
**Expected**: 200 OK với lịch sử searches của user

---

## 1️⃣6️⃣ PROGRESS TRACKING EXTENDED (Section 2.4) - 4 endpoints

### 📊 GET /api/v1/progress/courses/{course_id}/analytics - Phân tích học tập chi tiết
**Path**: Thay `{course_id}` bằng ID khóa học đã enroll
**Headers**: Authorization: Bearer <token>
**Query Parameters**:
- `period`: "last_30_days" hoặc "all_time"

**Expected**: 200 OK với:
- Biểu đồ thời gian học theo ngày/tuần
- Performance trends (quiz scores theo thời gian)
- Thống kê study habits (thời gian học mỗi ngày)
- So sánh với học viên khác (anonymous)

### ⏱️ POST /api/v1/progress/time-tracking - Ghi nhận thời gian học
**Headers**: Authorization: Bearer <token>
```json
{
  "course_id": "course-uuid", 
  "lesson_id": "lesson-uuid",
  "session_start": "2025-12-04T10:00:00Z",
  "session_end": "2025-12-04T10:30:00Z",
  "activity_type": "reading"
}
```
**Expected**: 200 OK với time tracking updated

### 📈 GET /api/v1/progress/overall/analytics - Analytics tổng quan tất cả khóa học
**Headers**: Authorization: Bearer <token>
**Query Parameters**:
- `time_range`: "last_7_days" hoặc "last_30_days" hoặc "last_90_days"

**Expected**: 200 OK với analytics tổng hợp tất cả khóa học

### 🏆 GET /api/v1/progress/achievements - Thành tích và badges
**Headers**: Authorization: Bearer <token>
**Expected**: 200 OK với danh sách achievements đã đạt được

---

## 1️⃣7️⃣ LEARNING EXTENDED FEATURES (Section 2.4) - 6 endpoints

### 📚 GET /api/v1/courses/{course_id}/modules - Danh sách modules
**Path**: Thay `{course_id}` bằng ID khóa học đã enroll
**Headers**: Authorization: Bearer <token>
**Expected**: 200 OK với danh sách modules + progress cho mỗi module

### 🎯 GET /api/v1/courses/{course_id}/modules/{module_id} - Chi tiết module
**Path**: Thay các ID tương ứng
**Headers**: Authorization: Bearer <token>
**Expected**: 200 OK với:
- Thông tin module (title, description, difficulty, estimated_hours)
- Danh sách lessons với trạng thái hoàn thành
- Learning outcomes và progress
- Resources và attachments
- Prerequisites modules

### 📖 GET /api/v1/courses/{course_id}/lessons/{lesson_id} - Chi tiết bài học
**Path**: Thay các ID tương ứng
**Headers**: Authorization: Bearer <token>
**Expected**: 200 OK với:
- Nội dung lesson (text_content, video_info, attachments)
- Navigation (previous/next lesson IDs)
- Progress tracking (thời gian học, video progress)
- Quiz liên kết (quiz_id, quiz_passed status)
- Trạng thái khóa lesson tiếp theo

### 📎 GET /api/v1/courses/{course_id}/modules/{module_id}/resources - Tài nguyên module
**Path**: Thay các ID tương ứng
**Headers**: Authorization: Bearer <token>
**Expected**: 200 OK với:
- Danh sách files, PDFs, links
- Phân loại theo type (pdf, video, code, slide)
- Kích thước files và links download

### 🎯 GET /api/v1/courses/{course_id}/modules/{module_id}/outcomes - Learning outcomes
**Path**: Thay các ID tương ứng 
**Headers**: Authorization: Bearer <token>
**Expected**: 200 OK với:
- Chi tiết từng learning outcome
- Skill tags để tracking
- Trạng thái đạt được của từng outcome
- Mandatory vs optional outcomes

### 📖 GET /api/v1/learning/lessons/{lesson_id}/resources - Tài nguyên bài học
**Path**: Thay `{lesson_id}` bằng ID lesson
**Headers**: Authorization: Bearer <token>
**Expected**: 200 OK với danh sách files, links, materials

### ▶️ POST /api/v1/learning/lessons/{lesson_id}/start - Bắt đầu học bài
**Path**: Thay `{lesson_id}` bằng ID lesson
**Headers**: Authorization: Bearer <token>
```json
{
  "started_at": "2025-12-04T10:30:00Z"
}
```
**Expected**: 200 OK với session bắt đầu học

### ✅ POST /api/v1/learning/lessons/{lesson_id}/complete - Hoàn thành bài học
**Path**: Thay `{lesson_id}` bằng ID lesson đã start
**Headers**: Authorization: Bearer <token>
```json
{
  "completed_at": "2025-12-04T11:00:00Z",
  "time_spent_minutes": 30,
  "completion_percentage": 100,
  "notes": "Đã hiểu về cú pháp Python cơ bản"
}
```
**Expected**: 200 OK với progress updated

### ▶️ POST /api/v1/learning/lessons/{lesson_id}/start - Bắt đầu học bài
**Path**: Thay `{lesson_id}` bằng ID lesson
**Headers**: Authorization: Bearer <token>
```json
{
  "started_at": "2025-12-04T10:30:00Z"
}
```
**Expected**: 200 OK với session bắt đầu học

### ✅ POST /api/v1/learning/lessons/{lesson_id}/complete - Hoàn thành bài học
**Path**: Thay `{lesson_id}` bằng ID lesson đã start
**Headers**: Authorization: Bearer <token>
```json
{
  "completed_at": "2025-12-04T11:00:00Z",
  "time_spent_minutes": 30,
  "completion_percentage": 100,
  "notes": "Đã hiểu về cú pháp Python cơ bản",
  "video_progress_seconds": 1200
}
```
**Expected**: 200 OK với progress updated và lesson unlocked tiếp theo

### ⏰ POST /api/v1/learning/time-tracking - Tracking thời gian học
**Headers**: Authorization: Bearer <token>
```json
{
  "course_id": "course-uuid",
  "lesson_id": "lesson-uuid",
  "session_duration_seconds": 1800,
  "activity_type": "video_watching",
  "timestamp": "2025-12-04T10:30:00Z"
}
```
**Expected**: 200 OK với time tracking recorded

---

## ⚠️ DANH SÁCH ĐẦY ĐỦ 84 API ENDPOINTS

### 🔐 Authentication (3 endpoints)
1. POST /api/v1/auth/register
2. POST /api/v1/auth/login  
3. POST /api/v1/auth/logout

### 👤 User Management (2 endpoints)
4. GET /api/v1/users/me
5. PATCH /api/v1/users/me

### 🧠 AI Assessment (3 endpoints)  
6. POST /api/v1/assessments/generate
7. POST /api/v1/assessments/{session_id}/submit
8. GET /api/v1/assessments/{session_id}/results

### 📚 Courses (4 endpoints)
9. GET /api/v1/courses/search
10. GET /api/v1/courses/public
11. GET /api/v1/courses/{course_id}/detail
12. GET /api/v1/courses/{course_id}/enrollment-status

### 📝 Enrollments (4 endpoints)
13. POST /api/v1/enrollments
14. GET /api/v1/enrollments/my-courses
15. GET /api/v1/enrollments/{enrollment_id}/detail  
16. DELETE /api/v1/enrollments/{enrollment_id}

### 📖 Learning (6 endpoints)
17. GET /api/v1/learning/courses
18. GET /api/v1/learning/courses/{course_id}
19. GET /api/v1/learning/lessons/{lesson_id}
20. GET /api/v1/learning/modules/{module_id}
21. GET /api/v1/learning/lessons/{lesson_id}/resources
22. POST /api/v1/learning/time-tracking

### 📝 Quizzes (10 endpoints)  
23. GET /api/v1/quiz/{quiz_id}/detail
24. POST /api/v1/quiz/{quiz_id}/attempt
25. GET /api/v1/quiz/{quiz_id}/results/{attempt_id}
26. POST /api/v1/quiz/{quiz_id}/retake
27. POST /api/v1/quiz/create  
28. GET /api/v1/quiz/instructor
29. PUT /api/v1/quiz/{quiz_id}
30. DELETE /api/v1/quiz/{quiz_id}
31. GET /api/v1/quiz/{quiz_id}/attempts
32. GET /api/v1/quiz/{quiz_id}/analytics

### 📊 Progress (4 endpoints)
33. GET /api/v1/progress/overall
34. GET /api/v1/progress/courses/{course_id}
35. GET /api/v1/progress/courses/{course_id}/analytics
36. GET /api/v1/progress/achievements

### 🎓 Personal Courses (5 endpoints)
37. GET /api/v1/personal-courses
38. POST /api/v1/personal-courses
39. GET /api/v1/personal-courses/{course_id}/progress
40. PUT /api/v1/personal-courses/{course_id}
41. DELETE /api/v1/personal-courses/{course_id}

### 💬 AI Chat (5 endpoints)
42. POST /api/v1/chat/course/{course_id}
43. GET /api/v1/chat/history
44. GET /api/v1/chat/conversations/{conversation_id}
45. DELETE /api/v1/chat/conversations
46. DELETE /api/v1/chat/history/{conversation_id}

### 💡 Recommendations (2 endpoints)
47. GET /api/v1/recommendations
48. GET /api/v1/recommendations/from-assessment

### 📊 Dashboard (3 endpoints)
49. GET /api/v1/dashboard/student
50. GET /api/v1/dashboard/instructor  
51. GET /api/v1/dashboard/admin

### 🔍 Search (4 endpoints)
52. GET /api/v1/search/global
53. GET /api/v1/search/courses
54. GET /api/v1/search/suggestions
55. GET /api/v1/search/history

### 🏫 Classes - Instructor (10 endpoints)
56. POST /api/v1/classes
57. GET /api/v1/classes
58. GET /api/v1/classes/{class_id}
59. PUT /api/v1/classes/{class_id}
60. DELETE /api/v1/classes/{class_id}
61. POST /api/v1/classes/{class_id}/students
62. GET /api/v1/classes/{class_id}/students
63. GET /api/v1/classes/{class_id}/student/{student_id}
64. DELETE /api/v1/classes/{class_id}/students/{student_id}
65. GET /api/v1/classes/{class_id}/analytics

### 📊 Analytics (8 endpoints)
66. GET /api/v1/analytics/learning-stats
67. GET /api/v1/analytics/progress-chart
68. GET /api/v1/analytics/instructor/class-stats
69. GET /api/v1/analytics/instructor/progress-chart
70. GET /api/v1/analytics/instructor/quiz-performance
71. GET /api/v1/analytics/admin/users-growth
72. GET /api/v1/analytics/admin/course-analytics
73. GET /api/v1/analytics/admin/system-health

### 🛠️ Admin Management (18 endpoints)
74. GET /api/v1/admin/users
75. GET /api/v1/admin/users/{user_id}
76. POST /api/v1/admin/users
77. PUT /api/v1/admin/users/{user_id}
78. DELETE /api/v1/admin/users/{user_id}
79. PUT /api/v1/admin/users/{user_id}/role
80. POST /api/v1/admin/users/{user_id}/reset-password
81. GET /api/v1/admin/courses
82. GET /api/v1/admin/courses/{course_id}
83. POST /api/v1/admin/courses
84. PUT /api/v1/admin/courses/{course_id}
85. DELETE /api/v1/admin/courses/{course_id}
86. GET /api/v1/admin/classes
87. GET /api/v1/admin/classes/{class_id}

> **Lưu ý**: Có thể có sự chênh lệch nhỏ do cách đếm, nhưng đây là danh sách đầy đủ các endpoints có trong hệ thống.

## ⚠️ LƯU Ý QUAN TRỌNG

### 🔑 Authentication Token
- Access token có thời hạn **15 phút**
- Nếu token hết hạn → Error 401 → Đăng nhập lại
- Refresh token có thời hạn **7 ngày** (remember_me=true)

### 🚫 Common Error Codes
- **400**: Bad Request (validation error, missing fields)
- **401**: Unauthorized (token không hợp lệ/hết hạn)  
- **403**: Forbidden (không có quyền)
- **404**: Not Found (resource không tồn tại)
- **500**: Internal Server Error

### 📊 Dữ Liệu Test Có Sẵn
- **1 Admin**: admin.super@ailab.com.vn / Admin@12345
- **3 Instructors**: tuananh.nguyen@, tuyet.le@, hung.tran@ / Giangvien@123  
- **~10 Students**: random emails / Hocvien@123
- **Khóa học Python**: "Lập trình Python từ Cơ bản đến Nâng cao"
- **2 Modules**: Python Cơ bản + Cấu trúc dữ liệu
- **6+ Lessons**: Từng module có 3+ lessons với content chi tiết
- **Quiz data**: Mỗi lesson có quiz với câu hỏi mẫu
- **AI Assessment**: Tự động sinh câu hỏi với Google Gemini

### 🔍 Cách Lấy Dữ Liệu Cần Thiết
1. **Course IDs**: Sau khi init data, search "Python" hoặc GET /courses/public
2. **User IDs**: Admin có thể GET /admin/users để lấy user IDs
3. **Lesson IDs**: GET course detail sẽ có embedded lessons với IDs
4. **Quiz IDs**: Từ lesson detail, trường `quiz_id` nếu lesson có quiz  
5. **Module IDs**: Từ course detail, embedded modules có IDs
6. **Class IDs**: Instructor có thể GET /classes sau khi tạo class
7. **Enrollment IDs**: GET /enrollments/my-courses sau khi enroll
8. **Assessment Session IDs**: Tạo mới bằng POST /assessments/generate

### 🔄 Reset Dữ Liệu
```bash
# Chạy lại script này để reset toàn bộ database
python -m scripts.init_data
```

### 🎯 Tips Test Hiệu Quả
1. **Test theo workflow**: Auth → Enroll → Learn → Quiz → Progress
2. **Sử dụng nhiều role**: Test với admin, instructor, student
3. **Kiểm tra permissions**: API chỉ accessible với đúng role
4. **Copy IDs từ response**: Lưu các UUIDs để test endpoints khác
5. **Test error cases**: Thử với token hết hạn, invalid IDs
6. **Verify data flow**: Đảm bảo progress update, enrollment tracking hoạt động

---

## 📝 QUY TRÌNH TEST HOÀN CHỈNH

1. **Khởi động**: Server + Init data
2. **Đăng nhập**: Admin/Instructor/Student  
3. **Test Authentication**: Register → Login → Profile
4. **Test Assessment**: Generate → Submit → Results → Recommendations
5. **Test Learning**: Search Course → Enroll → Learn → Progress → Quiz
6. **Test Personal**: Create Personal Course → Update → Track Progress
7. **Test AI Chat**: Create Conversation → Send Messages → History
8. **Test Admin**: Manage Users → Courses → Analytics (admin only)

**🎯 Kết quả mong đợi**: Tất cả API trả về đúng status code và data structure theo schema định nghĩa!

---

## 🔄 LUỒNG CHỨC NĂNG END-TO-END CẦN TEST

> **Tổng số luồng E2E**: 25 luồng  
> **Mục đích**: Đảm bảo các chức năng hoạt động trọn vẹn từ đầu đến cuối, logic ăn khớp giữa các module

---

### **NHÓM 1: AUTHENTICATION & USER MANAGEMENT** 🔐

#### **E2E-01: Đăng ký và kích hoạt tài khoản Student**
**Mục đích**: Test luồng đăng ký tài khoản mới và xác thực thông tin

**Các bước**:
```
1. POST /api/v1/auth/register
   Body: {
     "email": "newstudent@test.com",
     "password": "Student@123",
     "full_name": "New Student Test",
     "role": "student"
   }
   ✓ Verify: 201 Created, user_id trả về

2. Kiểm tra MongoDB
   ✓ Verify: User tồn tại với email đã đăng ký
   ✓ Verify: Password đã được hash

3. POST /api/v1/auth/login
   Body: {
     "email": "newstudent@test.com",
     "password": "Student@123"
   }
   ✓ Verify: 200 OK, access_token + refresh_token

4. GET /api/v1/users/me
   Headers: Authorization: Bearer {access_token}
   ✓ Verify: full_name, email, role đúng
   ✓ Verify: user_id khớp với response đăng ký
```

**Expected Results**:
- ✅ Tài khoản được tạo thành công
- ✅ Login thành công với credentials vừa tạo
- ✅ JWT tokens hoạt động bình thường
- ✅ Profile đầy đủ thông tin

---

#### **E2E-02: Luồng đăng nhập và refresh token**
**Mục đích**: Test JWT authentication flow và token refresh mechanism

**Các bước**:
```
1. POST /api/v1/auth/login
   Body: {
     "email": "admin.super@ailab.com.vn",
     "password": "Admin@12345"
   }
   ✓ Save: access_token, refresh_token

2. GET /api/v1/users/me
   Headers: Authorization: Bearer {access_token}
   ✓ Verify: 200 OK, user data

3. [Giả lập token hết hạn - Mock hoặc đợi]
   GET /api/v1/users/me (với access_token cũ)
   ✓ Verify: 401 Unauthorized

4. POST /api/v1/auth/refresh
   Body: { "refresh_token": "{refresh_token}" }
   ✓ Verify: 200 OK, access_token mới

5. GET /api/v1/users/me
   Headers: Authorization: Bearer {new_access_token}
   ✓ Verify: 200 OK, user data

6. POST /api/v1/auth/logout
   Headers: Authorization: Bearer {access_token}
   ✓ Verify: 200 OK

7. GET /api/v1/users/me (với token đã logout)
   ✓ Verify: 401 Unauthorized, token đã bị revoke
```

**Expected Results**:
- ✅ Refresh token hoạt động khi access_token hết hạn
- ✅ Logout vô hiệu hóa tokens
- ✅ Không thể dùng token đã logout

---

#### **E2E-03: Cập nhật profile và avatar**
**Mục đích**: Test chức năng update thông tin cá nhân

**Các bước**:
```
1. POST /api/v1/auth/login (student)
   ✓ Save: access_token

2. GET /api/v1/users/me
   ✓ Save: current full_name, bio

3. PATCH /api/v1/users/me
   Body: {
     "full_name": "Updated Name",
     "bio": "New bio description",
     "phone": "+84912345678"
   }
   ✓ Verify: 200 OK

4. GET /api/v1/users/me
   ✓ Verify: full_name = "Updated Name"
   ✓ Verify: bio = "New bio description"
   ✓ Verify: phone = "+84912345678"
   ✓ Verify: updated_at đã thay đổi
```

**Expected Results**:
- ✅ Profile được cập nhật thành công
- ✅ Thông tin mới reflect ngay lập tức
- ✅ Timestamp updated_at được cập nhật

---

### **NHÓM 2: ASSESSMENT & PERSONALIZED LEARNING** 🎯

#### **E2E-04: Luồng đánh giá năng lực AI hoàn chỉnh**
**Mục đích**: Test toàn bộ quy trình assessment từ generate → submit → results → recommendations

**Các bước**:
```
1. POST /api/v1/auth/login (student)
   ✓ Save: access_token

2. POST /api/v1/assessments/generate
   Body: {
     "category": "Programming",
     "topic": "Python Basics",
     "level": "Beginner"
   }
   ✓ Verify: 201 Created
   ✓ Save: session_id
   ✓ Verify: questions[] có 15 câu (Beginner)
   ✓ Verify: Tỷ lệ độ khó: ~20% Easy, ~50% Medium, ~30% Hard
   ✓ Verify: Mỗi câu có: question_id, question_text, options[], difficulty, skill_tag

3. POST /api/v1/assessments/{session_id}/submit
   Body: {
     "answers": [
       { "question_id": "q1", "selected_answer": "A" },
       { "question_id": "q2", "selected_answer": "B" },
       ...
     ]
   }
   ✓ Verify: 200 OK

4. GET /api/v1/assessments/{session_id}/results
   ✓ Verify: score (0-100)
   ✓ Verify: proficiency_level (Beginner/Intermediate/Advanced)
   ✓ Verify: skill_analysis[] với mỗi skill:
     - skill_tag
     - questions_count
     - correct_count
     - proficiency_percentage
     - strength_level (Strong/Average/Weak)
   ✓ Verify: knowledge_gaps[] (các lỗ hổng kiến thức)
   ✓ Verify: time_analysis (thời gian làm bài)
   ✓ Verify: ai_feedback (nhận xét chi tiết)

5. GET /api/v1/recommendations/from-assessment?session_id={session_id}
   ✓ Verify: user_proficiency_level
   ✓ Verify: recommended_courses[] được sắp xếp theo priority_rank
   ✓ Verify: Mỗi course có:
     - course_id, title, category, level
     - relevance_score (0-100)
     - reason (lý do AI đề xuất)
     - addresses_gaps[] (gaps được giải quyết)
   ✓ Verify: suggested_learning_order[] (thứ tự học tối ưu)
   ✓ Verify: practice_exercises[] (bài tập đề xuất)
   ✓ Verify: ai_personalized_advice
```

**Expected Results**:
- ✅ AI sinh đúng số lượng câu hỏi theo level
- ✅ Chấm điểm và phân tích skill chính xác
- ✅ Recommendations phù hợp với kết quả assessment
- ✅ Learning path được cá nhân hóa

---

#### **E2E-05: Retake assessment với câu hỏi khác**
**Mục đích**: Verify AI sinh câu hỏi mới cho mỗi lần assessment

**Các bước**:
```
1. Hoàn thành E2E-04
   ✓ Save: questions[] lần 1, session_id_1

2. POST /api/v1/assessments/generate
   Body: { (cùng category, topic, level như lần 1) }
   ✓ Save: questions[] lần 2, session_id_2

3. So sánh questions[]
   ✓ Verify: session_id_1 ≠ session_id_2
   ✓ Verify: Nội dung câu hỏi khác nhau (ít nhất 70%)
   ✓ Verify: Skill tags coverage tương tự
   ✓ Verify: Tỷ lệ độ khó tương đương

4. Submit và compare results
   ✓ Verify: Kết quả phản ánh đúng answers
```

**Expected Results**:
- ✅ Mỗi lần generate có bộ câu hỏi khác nhau
- ✅ Chất lượng và coverage đồng đều
- ✅ Tránh học thuộc lòng

---

### **NHÓM 3: COURSE ENROLLMENT & LEARNING** 📚

#### **E2E-06: Tìm và enroll khóa học**
**Mục đích**: Test luồng tìm kiếm, xem chi tiết và enroll course

**Các bước**:
```
1. POST /api/v1/auth/login (student)
   ✓ Save: access_token

2. GET /api/v1/courses?search=Python&category=Programming
   ✓ Verify: Courses liên quan đến Python
   ✓ Save: course_id của course muốn enroll

3. GET /api/v1/courses/{course_id}
   ✓ Verify: Course detail đầy đủ:
     - title, description, instructor_info
     - modules[] với lessons[]
     - difficulty_level, estimated_duration
   ✓ Verify: is_enrolled = false (chưa enroll)

4. POST /api/v1/enrollments
   Body: { "course_id": "{course_id}" }
   ✓ Verify: 201 Created
   ✓ Save: enrollment_id

5. GET /api/v1/enrollments/my-courses
   ✓ Verify: Course vừa enroll xuất hiện
   ✓ Verify: enrollment_status = "active"
   ✓ Verify: progress_percentage = 0

6. GET /api/v1/courses/{course_id}
   ✓ Verify: is_enrolled = true
   ✓ Verify: Student có quyền xem modules/lessons

7. GET /api/v1/courses/{course_id}/modules
   ✓ Verify: Modules list với lessons
   ✓ Verify: Mỗi lesson có: lesson_id, title, content_type
```

**Expected Results**:
- ✅ Search hoạt động chính xác
- ✅ Enrollment thành công
- ✅ Student có quyền truy cập nội dung sau enroll

---

#### **E2E-07: Học bài và hoàn thành lesson**
**Mục đích**: Test progress tracking khi học lesson

**Các bước**:
```
1. Student đã enroll course (từ E2E-06)
   ✓ Have: course_id, enrollment_id

2. GET /api/v1/courses/{course_id}/modules
   ✓ Save: lesson_id đầu tiên

3. GET /api/v1/lessons/{lesson_id}
   ✓ Verify: Lesson content (markdown format)
   ✓ Verify: has_quiz (true/false)
   ✓ Save: quiz_id nếu có

4. POST /api/v1/progress/lessons/{lesson_id}/complete
   Headers: Authorization: Bearer {token}
   ✓ Verify: 200 OK

5. GET /api/v1/progress/courses/{course_id}
   ✓ Verify: completed_lessons[] chứa lesson_id vừa complete
   ✓ Verify: completion_percentage tăng
   ✓ Verify: lessons_completed tăng 1
   ✓ Verify: last_accessed updated

6. Lặp lại bước 3-5 với các lessons khác
   ✓ Verify: Progress tăng tuyến tính
   ✓ Verify: completion_percentage đến 100% khi hoàn thành tất cả
```

**Expected Results**:
- ✅ Lesson content hiển thị đầy đủ
- ✅ Progress tracking chính xác
- ✅ Completion percentage tính đúng

---

#### **E2E-08: Làm quiz và pass/fail**
**Mục đích**: Test quiz flow với retry mechanism

**Các bước**:
```
1. Student đang học lesson có quiz
   ✓ Have: lesson_id, quiz_id

2. GET /api/v1/quizzes/lessons/{lesson_id}/quiz
   ✓ Verify: Quiz detail:
     - title, description, time_limit
     - questions[], passing_score
     - total_points

3. POST /api/v1/quizzes/{quiz_id}/attempts
   Body: {
     "answers": [
       { "question_id": "q1", "answer": "A" },
       { "question_id": "q2", "answer": "B" },
       ...
     ],
     "time_taken": 120
   }
   ✓ Save: attempt_id

4. GET /api/v1/quizzes/{quiz_id}/results?attempt_id={attempt_id}
   ✓ Verify: score (0-100)
   ✓ Verify: passed (true/false)
   ✓ Verify: correct_answers_count
   ✓ Verify: detailed_feedback[] cho từng câu
   ✓ Verify: skill_performance[]

5. CASE: Nếu FAILED (passed = false)
   POST /api/v1/quizzes/{quiz_id}/retake
   ✓ Verify: 200 OK
   ✓ Verify: new_quiz_id (AI sinh quiz tương tự)
   ✓ Save: new_quiz_id

6. Làm lại quiz mới và PASS
   POST /api/v1/quizzes/{new_quiz_id}/attempts
   (Với answers đúng hơn)
   ✓ Verify: passed = true

7. Kiểm tra progress
   GET /api/v1/progress/courses/{course_id}
   ✓ Verify: Quiz được mark completed
   ✓ Verify: Progress updated
```

**Expected Results**:
- ✅ Quiz attempts được track
- ✅ Scoring chính xác
- ✅ Retake mechanism hoạt động (AI sinh quiz mới)
- ✅ Progress chỉ update khi pass

---

### **NHÓM 4: AI CHATBOT & LEARNING SUPPORT** 🤖

#### **E2E-09: Chat với AI trong context khóa học**
**Mục đích**: Test AI chatbot với course context và conversation history

**Các bước**:
```
1. Student đã enroll course
   ✓ Have: course_id

2. POST /api/v1/chat/conversations
   Body: { "course_id": "{course_id}" }
   ✓ Verify: 201 Created
   ✓ Save: conversation_id

3. POST /api/v1/chat/conversations/{conversation_id}/messages
   Body: {
     "question": "Giải thích về Python list comprehension"
   }
   ✓ Verify: 200 OK
   ✓ Verify: Response có:
     - message_id
     - question (echo back)
     - answer (markdown format, detailed)
     - sources[] (optional - RAG references)
     - related_lessons[]
     - tokens_used (optional)
     - timestamp
   ✓ Save: message_id, answer

4. POST /api/v1/chat/conversations/{conversation_id}/messages
   Body: {
     "question": "Cho ví dụ cụ thể về list comprehension"
   }
   (Follow-up question)
   ✓ Verify: AI hiểu context từ câu trước
   ✓ Verify: Response có ví dụ code cụ thể

5. GET /api/v1/chat/conversations/{conversation_id}
   ✓ Verify: Conversation detail:
     - conversation_id
     - course: { course_id, title }
     - messages[] có đầy đủ 2 messages
     - Mỗi message có: message_id, role (user/assistant), content, timestamp
     - created_at, updated_at

6. Verify conversation history
   ✓ messages[0].role = "user"
   ✓ messages[0].content = câu hỏi đầu
   ✓ messages[1].role = "assistant"
   ✓ messages[1].content = câu trả lời đầu
   ✓ messages[2].role = "user"
   ✓ messages[3].role = "assistant"
```

**Expected Results**:
- ✅ AI response có context về course
- ✅ Follow-up questions maintain conversation flow
- ✅ History được lưu đầy đủ
- ✅ Response quality tốt (markdown format, detailed)

---

#### **E2E-10: Chat history và search**
**Mục đích**: Test quản lý conversations

**Các bước**:
```
1. POST /api/v1/auth/login (student)
   ✓ Tạo nhiều conversations (ít nhất 3)

2. GET /api/v1/chat/conversations
   ✓ Verify: List all conversations
   ✓ Verify: Mỗi item có:
     - conversation_id
     - course_title
     - last_message_preview
     - message_count
     - updated_at

3. GET /api/v1/chat/conversations?course_id={course_id}
   ✓ Verify: Chỉ conversations của course đó
   ✓ Verify: Filter hoạt động đúng

4. GET /api/v1/chat/conversations/{conversation_id}
   ✓ Verify: Chi tiết conversation
   ✓ Verify: Full messages history

5. DELETE /api/v1/chat/conversations/{conversation_id}
   ✓ Verify: 200 OK

6. GET /api/v1/chat/conversations/{conversation_id}
   ✓ Verify: 404 Not Found (conversation đã xóa)

7. GET /api/v1/chat/conversations
   ✓ Verify: Conversation đã bị remove khỏi list
```

**Expected Results**:
- ✅ List conversations hoạt động
- ✅ Filter by course_id chính xác
- ✅ Delete conversation success
- ✅ Soft/hard delete được handle đúng

---

### **NHÓM 5: PRACTICE EXERCISES (AI GENERATED)** 💪

#### **E2E-11: AI sinh bài tập luyện tập cá nhân hóa**
**Mục đích**: Test AI practice generation với multiple input sources

**Các bước**:
```
1. POST /api/v1/auth/login (student)

2. CASE 1: Generate từ lesson_id
   POST /api/v1/ai/generate-practice
   Body: {
     "lesson_id": "{lesson_id}",
     "difficulty": "medium",
     "question_count": 10,
     "practice_type": "multiple_choice"
   }
   ✓ Verify: 201 Created
   ✓ Save: practice_id_1

3. CASE 2: Generate từ course_id
   POST /api/v1/ai/generate-practice
   Body: {
     "course_id": "{course_id}",
     "difficulty": "hard",
     "question_count": 15,
     "practice_type": "mixed"
   }
   ✓ Save: practice_id_2

4. CASE 3: Generate từ topic_prompt
   POST /api/v1/ai/generate-practice
   Body: {
     "topic_prompt": "Python loops and iterations",
     "difficulty": "easy",
     "question_count": 5,
     "focus_skills": ["python-loops", "control-flow"]
   }
   ✓ Save: practice_id_3

5. Verify response structure cho tất cả cases
   ✓ practice_id (UUID)
   ✓ source: { lesson_id OR course_id OR topic_prompt }
   ✓ difficulty
   ✓ exercises[] với đúng số lượng
   ✓ Mỗi exercise có:
     - id, type (theory/coding/problem-solving)
     - question, options[], correct_answer
     - explanation, difficulty, related_skill, points
   ✓ total_questions
   ✓ estimated_time (minutes)
   ✓ created_at

6. Làm bài tập (submit logic tương tự quiz)
   [Mock submit - API chưa implement]

7. Verify quality
   ✓ Câu hỏi bám sát topic
   ✓ Độ khó phù hợp với request
   ✓ Explanation chi tiết
```

**Expected Results**:
- ✅ AI generate từ 3 sources: lesson, course, topic_prompt
- ✅ Số lượng và độ khó đúng yêu cầu
- ✅ Practice exercises chất lượng cao
- ✅ Schema match API_SCHEMA.md Section 4.11

---

### **NHÓM 6: CLASS MANAGEMENT (INSTRUCTOR)** 👨‍🏫

#### **E2E-12: Instructor tạo và quản lý lớp học**
**Mục đích**: Test full class lifecycle từ create → update → manage

**Các bước**:
```
1. POST /api/v1/auth/login (instructor)
   ✓ Save: instructor_token

2. GET /api/v1/courses (courses của instructor)
   ✓ Save: course_id để tạo class

3. POST /api/v1/classes
   Body: {
     "course_id": "{course_id}",
     "class_name": "Python K01 2025",
     "description": "Lớp Python cơ bản khóa 01",
     "max_students": 30,
     "schedule": "Mon, Wed, Fri 19:00-21:00",
     "start_date": "2025-01-15",
     "end_date": "2025-03-15"
   }
   ✓ Verify: 201 Created
   ✓ Save: class_id, invite_code
   ✓ Verify: invite_code được generate (6-8 ký tự)
   ✓ Verify: status = "preparing"

4. GET /api/v1/classes/my-classes
   ✓ Verify: Class vừa tạo xuất hiện
   ✓ Verify: student_count = 0

5. GET /api/v1/classes/{class_id}
   ✓ Verify: Class detail đầy đủ:
     - class_name, description, course_title
     - instructor_name (chính instructor đã login)
     - max_students, student_count
     - invite_code, status, schedule
     - created_at, start_date, end_date

6. PATCH /api/v1/classes/{class_id}
   Body: {
     "class_name": "Python Advanced K01 2025",
     "max_students": 40,
     "status": "active"
   }
   ✓ Verify: 200 OK

7. GET /api/v1/classes/{class_id}
   ✓ Verify: Thông tin đã update
   ✓ Verify: status = "active"
```

**Expected Results**:
- ✅ Class được tạo với invite_code
- ✅ Update class thành công
- ✅ Instructor có full control

---

#### **E2E-13: Student join class bằng invite code**
**Mục đích**: Test enrollment flow via invite code

**Các bước**:
```
1. Instructor tạo class (từ E2E-12)
   ✓ Have: class_id, invite_code

2. POST /api/v1/auth/login (student1)
   ✓ Save: student1_token

3. POST /api/v1/classes/join
   Body: { "invite_code": "{invite_code}" }
   Headers: Authorization: Bearer {student1_token}
   ✓ Verify: 200 OK
   ✓ Verify: Message: "Joined class successfully"

4. GET /api/v1/classes/my-classes
   Headers: Authorization: Bearer {student1_token}
   ✓ Verify: Class xuất hiện trong list
   ✓ Verify: role = "student"

5. Instructor check
   GET /api/v1/classes/{class_id}
   Headers: Authorization: Bearer {instructor_token}
   ✓ Verify: student_count = 1
   ✓ Verify: students[] chứa student1_id

6. Student2 join
   POST /api/v1/auth/login (student2)
   POST /api/v1/classes/join với cùng invite_code
   ✓ Verify: Success

7. Instructor check lại
   GET /api/v1/classes/{class_id}
   ✓ Verify: student_count = 2
   ✓ Verify: students[] chứa cả student1 và student2

8. Test max_students limit
   [Join thêm students đến khi đủ max_students]
   POST /api/v1/classes/join (student thứ 31)
   ✓ Verify: 400 Bad Request
   ✓ Verify: Message: "Class is full"
```

**Expected Results**:
- ✅ Join bằng invite_code thành công
- ✅ Student count tăng chính xác
- ✅ Max students limit được enforce

---

#### **E2E-14: Instructor xem progress học viên**
**Mục đích**: Test analytics và tracking cho instructor

**Các bước**:
```
1. Class có students đã join và học (từ E2E-13)
   ✓ Students đã complete lessons, làm quizzes

2. Instructor login
   GET /api/v1/classes/{class_id}/students
   ✓ Verify: List all students trong class
   ✓ Verify: Mỗi student có:
     - student_id, student_name, email
     - progress_percentage
     - completed_lessons, total_lessons
     - average_quiz_score
     - last_accessed

3. GET /api/v1/classes/{class_id}/students/{student_id}
   ✓ Verify: Chi tiết progress của student:
     - Student info
     - Course progress: completion_percentage, completed_lessons[]
     - Quiz results: attempts[], scores[], average_score
     - Learning streak: study_streak_days
     - Time spent: total_time_spent_minutes

4. GET /api/v1/classes/{class_id}/analytics
   ✓ Verify: Class-level analytics:
     - average_progress (%)
     - completion_rate (%)
     - active_students_count
     - quiz_performance: { average_score, pass_rate }
     - engagement_metrics
```

**Expected Results**:
- ✅ Instructor xem được progress từng student
- ✅ Class analytics tổng hợp chính xác
- ✅ Data real-time và accurate

---

### **NHÓM 7: QUIZ MANAGEMENT (INSTRUCTOR)** 📝

#### **E2E-15: Instructor tạo quiz cho lesson**
**Mục đích**: Test quiz creation và management

**Các bước**:
```
1. POST /api/v1/auth/login (instructor)

2. GET /api/v1/courses (own courses)
   GET /api/v1/courses/{course_id}/modules
   ✓ Save: lesson_id

3. POST /api/v1/quizzes/lessons/{lesson_id}/quizzes
   Body: {
     "title": "Python Basics Quiz 01",
     "description": "Test kiến thức về Python cơ bản",
     "questions": [
       {
         "question_text": "Python là gì?",
         "question_type": "multiple_choice",
         "options": ["A", "B", "C", "D"],
         "correct_answer": "A",
         "points": 10,
         "difficulty": "easy",
         "skill_tag": "python-basics"
       },
       { ... } // 9 câu nữa
     ],
     "time_limit": 30,
     "passing_score": 70,
     "allow_retake": true
   }
   ✓ Verify: 201 Created
   ✓ Save: quiz_id

4. GET /api/v1/quizzes/{quiz_id}
   ✓ Verify: Quiz detail đầy đủ
   ✓ Verify: total_points = sum(questions[].points)
   ✓ Verify: question_count = 10

5. PATCH /api/v1/quizzes/{quiz_id}
   Body: {
     "title": "Python Basics Quiz 01 - Updated",
     "passing_score": 75
   }
   ✓ Verify: 200 OK

6. Students làm quiz (xem E2E-08)

7. GET /api/v1/quizzes/{quiz_id}/analytics
   ✓ Verify: Quiz analytics:
     - total_attempts
     - average_score
     - pass_rate
     - question_difficulty_stats[]
     - common_mistakes[]
```

**Expected Results**:
- ✅ Quiz được tạo và gắn vào lesson
- ✅ Update quiz thành công
- ✅ Analytics reflect student performance

---

#### **E2E-16: Instructor xem quiz attempts**
**Mục đích**: Test review mechanism cho instructor

**Các bước**:
```
1. Quiz đã có students attempts (từ E2E-15)

2. GET /api/v1/quizzes/{quiz_id}/attempts
   ✓ Verify: List all attempts
   ✓ Verify: Mỗi attempt có:
     - attempt_id, student_name, student_email
     - score, passed, time_taken
     - submitted_at

3. GET /api/v1/quizzes/{quiz_id}/attempts/{attempt_id}
   ✓ Verify: Detailed attempt:
     - Student info
     - Quiz info
     - answers[] với từng câu:
       - question_text
       - selected_answer
       - correct_answer
       - is_correct
       - points_earned
     - total_score, passed
```

**Expected Results**:
- ✅ Instructor xem được tất cả attempts
- ✅ Chi tiết từng attempt đầy đủ
- ✅ Có thể review answers của students

---

### **NHÓM 8: PERSONAL COURSES (AI GENERATED)** 🌟

#### **E2E-17: Tạo khóa học cá nhân từ AI**
**Mục đích**: Test AI course generation feature

**Các bước**:
```
1. POST /api/v1/auth/login (student)

2. POST /api/v1/personal-courses
   Body: {
     "topic_prompt": "Học Python từ cơ bản đến nâng cao với focus vào web development",
     "difficulty": "intermediate",
     "duration_weeks": 8,
     "learning_goals": [
       "Master Python syntax",
       "Build web apps with Flask",
       "Work with databases"
     ]
   }
   ✓ Verify: 201 Created (có thể mất 10-30s - AI generating)
   ✓ Save: personal_course_id

3. GET /api/v1/personal-courses/{personal_course_id}
   ✓ Verify: AI-generated course structure:
     - title (AI sinh)
     - description (AI sinh)
     - modules[] với lessons[]
     - Mỗi lesson có content (markdown)
     - estimated_duration
     - difficulty_level
   ✓ Verify: created_by = student_id

4. GET /api/v1/personal-courses
   ✓ Verify: List personal courses
   ✓ Verify: Course vừa tạo xuất hiện

5. Student học personal course (tương tự E2E-07)
   POST /api/v1/progress/lessons/{lesson_id}/complete
   ✓ Verify: Progress tracking hoạt động

6. GET /api/v1/progress/courses/{personal_course_id}
   ✓ Verify: Progress updated

7. PATCH /api/v1/personal-courses/{personal_course_id}
   Body: {
     "title": "My Custom Python Course",
     "is_public": true
   }
   ✓ Verify: Update success
```

**Expected Results**:
- ✅ AI sinh course structure hợp lý
- ✅ Lessons có nội dung chất lượng
- ✅ Progress tracking tương tự official courses
- ✅ Student có thể customize

---

### **NHÓM 9: ADMIN MANAGEMENT** 👑

#### **E2E-18: Admin quản lý users**
**Mục đích**: Test full user management flow

**Các bước**:
```
1. POST /api/v1/auth/login (admin)
   ✓ Save: admin_token

2. GET /api/v1/admin/users
   ✓ Verify: List all users
   ✓ Verify: Có pagination (skip, limit)
   ✓ Verify: Filter by role, status

3. GET /api/v1/admin/users?role=student&status=active&skip=0&limit=20
   ✓ Verify: Filtered results
   ✓ Save: student_id

4. GET /api/v1/admin/users/{student_id}
   ✓ Verify: User detail đầy đủ:
     - Personal info
     - Enrollment statistics
     - Activity logs
     - Created/updated timestamps

5. POST /api/v1/admin/users/{student_id}/change-role
   Body: { "new_role": "instructor" }
   ✓ Verify: 200 OK
   ✓ Verify: Role changed từ student → instructor

6. GET /api/v1/admin/users/{student_id}
   ✓ Verify: role = "instructor"

7. POST /api/v1/admin/users/{student_id}/reset-password
   Body: { "new_password": "NewPassword@123" }
   ✓ Verify: 200 OK

8. Test login với password mới
   POST /api/v1/auth/login
   Body: { email: student_email, password: "NewPassword@123" }
   ✓ Verify: Login success

9. DELETE /api/v1/admin/users/{user_id}
   (Test với user không có dependencies)
   ✓ Verify: 200 OK hoặc 400 nếu có dependencies

10. GET /api/v1/admin/users/{user_id}
    ✓ Verify: 404 Not Found
```

**Expected Results**:
- ✅ Admin có full control users
- ✅ Change role hoạt động
- ✅ Reset password thành công
- ✅ Delete check dependencies

---

#### **E2E-19: Admin quản lý courses**
**Mục đích**: Test course management cho admin

**Các bước**:
```
1. POST /api/v1/auth/login (admin)

2. GET /api/v1/admin/courses
   ✓ Verify: List all courses (official + personal)
   ✓ Verify: Filter by category, status, instructor_id

3. POST /api/v1/admin/courses
   Body: {
     "title": "Advanced Machine Learning",
     "description": "...",
     "category": "AI/ML",
     "level": "advanced",
     "instructor_id": "{instructor_id}"
   }
   ✓ Verify: 201 Created
   ✓ Save: course_id

4. GET /api/v1/admin/courses/{course_id}
   ✓ Verify: Course detail

5. PATCH /api/v1/admin/courses/{course_id}
   Body: { "status": "published" }
   ✓ Verify: Status updated

6. GET /api/v1/admin/courses/{course_id}/impact
   (Check impact trước khi xóa)
   ✓ Verify: Impact analysis:
     - enrollments_count
     - active_classes_count
     - students_affected[]

7. DELETE /api/v1/admin/courses/{course_id}
   (Nếu không có dependencies)
   ✓ Verify: 200 OK hoặc 400 nếu có impact

8. Nếu có dependencies:
   ✓ Verify: Error message chi tiết về impact
```

**Expected Results**:
- ✅ Admin create/update/delete courses
- ✅ Impact check trước khi delete
- ✅ Prevent delete khi có students enrolled

---

#### **E2E-20: Admin giám sát classes**
**Mục đích**: Test monitoring capabilities

**Các bước**:
```
1. POST /api/v1/auth/login (admin)

2. GET /api/v1/admin/classes
   ✓ Verify: Tất cả classes từ mọi instructors
   ✓ Verify: Filter by instructor_id, course_id, status

3. GET /api/v1/admin/classes?status=active&sort_by=student_count&order=desc
   ✓ Verify: Sorted by student_count descending

4. GET /api/v1/admin/classes/{class_id}
   ✓ Verify: Chi tiết class với:
     - Class info
     - Instructor info
     - Course info
     - Students count, stats
     - Average progress, completion rate

5. GET /api/v1/admin/analytics/users-growth?period=90days&group_by=week
   ✓ Verify: Growth data:
     - growth_data[] by week
     - Mỗi point: date, new_users, total_users
     - summary: growth_rate, average_signups
```

**Expected Results**:
- ✅ Admin xem được tất cả classes
- ✅ Filter và sort hoạt động
- ✅ Analytics cung cấp insights

---

### **NHÓM 10: DASHBOARD & ANALYTICS** 📊

#### **E2E-21: Student dashboard**
**Mục đích**: Test dashboard data aggregation

**Các bước**:
```
1. POST /api/v1/auth/login (student)
   Student đã có enrolled courses, progress

2. GET /api/v1/dashboard/student
   ✓ Verify: Dashboard data:
     - enrolled_courses[] với progress
     - progress_summary:
       - total_courses_enrolled
       - courses_in_progress
       - courses_completed
       - average_progress
     - recent_activities[] (học lesson, làm quiz)
     - learning_streak: study_streak_days
     - recommendations[] (optional)

3. Verify data accuracy
   ✓ enrolled_courses.length khớp với GET /enrollments/my-courses
   ✓ Progress data khớp với actual progress
   ✓ Recent activities theo thời gian giảm dần

4. GET /api/v1/dashboard/student/recommendations
   ✓ Verify: Recommended courses dựa trên:
     - Completed courses
     - Assessment results (nếu có)
     - Learning preferences
```

**Expected Results**:
- ✅ Dashboard aggregate data chính xác
- ✅ Recommendations personalized
- ✅ Real-time data

---

#### **E2E-22: Instructor dashboard**
**Mục đích**: Test instructor analytics

**Các bước**:
```
1. POST /api/v1/auth/login (instructor)
   Instructor có classes với students

2. GET /api/v1/dashboard/instructor
   ✓ Verify: Instructor dashboard:
     - overview:
       - total_classes
       - total_students
       - active_classes
       - average_completion_rate
     - recent_classes[] với student_count, activity
     - student_activities[] (recent completions, quiz attempts)
     - upcoming_deadlines[] (nếu có)

3. GET /api/v1/analytics/instructor/classes?class_id={class_id}
   ✓ Verify: Class-specific analytics:
     - Student progress distribution
     - Quiz performance trends
     - Engagement metrics
     - At-risk students[]

4. GET /api/v1/analytics/instructor/progress-chart?time_range=week&class_id={id}
   ✓ Verify: Time-series data:
     - Daily/weekly progress data
     - Chart-ready format
```

**Expected Results**:
- ✅ Instructor overview accurate
- ✅ Class analytics detailed
- ✅ Identify at-risk students

---

#### **E2E-23: Admin dashboard**
**Mục đích**: Test system-wide analytics

**Các bước**:
```
1. POST /api/v1/auth/login (admin)

2. GET /api/v1/admin/dashboard
   ✓ Verify: System stats:
     - system_stats:
       - total_users (by role)
       - total_courses
       - total_classes
       - total_enrollments
     - growth_metrics:
       - new_users_today, this_week, this_month
       - active_users_today
     - popular_courses[] (by enrollment_count)
     - recent_activities[] (system-wide)

3. GET /api/v1/admin/analytics/users-growth?period=90days&group_by=week
   ✓ Verify: Growth chart data
   ✓ Verify: Trend analysis

4. Verify data consistency
   ✓ total_users = sum(users by role)
   ✓ Popular courses match enrollment data
```

**Expected Results**:
- ✅ System-wide stats accurate
- ✅ Growth trends visualizable
- ✅ Real-time insights

---

### **NHÓM 11: SEARCH & RECOMMENDATION** 🔍

#### **E2E-24: Search courses, users, classes**
**Mục đích**: Test unified search functionality

**Các bước**:
```
1. POST /api/v1/auth/login (student)

2. GET /api/v1/search/courses?keyword=Python&category=Programming&level=beginner
   ✓ Verify: Courses matching criteria
   ✓ Verify: Relevance sorting
   ✓ Verify: Pagination

3. GET /api/v1/search/users?keyword=John&role=instructor
   ✓ Verify: Instructors tên "John"
   ✓ Verify: Role filter applied

4. POST /api/v1/auth/login (instructor)
   GET /api/v1/search/classes?keyword=Web&status=active
   ✓ Verify: Classes matching keyword
   ✓ Verify: Status filter

5. Test advanced search
   GET /api/v1/search/courses?keyword=Python&category=Programming&min_rating=4.5&sort_by=popularity
   ✓ Verify: Multiple filters combined
   ✓ Verify: Sorting applied

6. Test fuzzy search
   GET /api/v1/search/courses?keyword=Pythn (typo)
   ✓ Verify: Still return Python courses (fuzzy match)
```

**Expected Results**:
- ✅ Search cross multiple entities
- ✅ Filters và sorting work
- ✅ Fuzzy matching for typos
- ✅ Fast response time

---

#### **E2E-25: Recommendation engine**
**Mục đích**: Test personalized recommendations

**Các bước**:
```
1. POST /api/v1/auth/login (student)
   Student có history: completed courses, assessment

2. GET /api/v1/recommendations/courses
   ✓ Verify: Recommended courses:
     - Based on completed_courses
     - Based on assessment results (proficiency_level)
     - Based on learning_preferences
   ✓ Verify: Mỗi recommendation có:
     - course_id, title, description
     - relevance_score (0-100)
     - reason (tại sao recommend)

3. Test different scenarios:
   CASE A: Student chưa học gì
   ✓ Verify: Recommend beginner courses

   CASE B: Student đã complete Python Basics
   ✓ Verify: Recommend Python Intermediate

   CASE C: Student assessment results: Advanced Python
   ✓ Verify: Recommend advanced topics

4. GET /api/v1/recommendations/from-assessment?session_id={id}
   (Từ E2E-04)
   ✓ Verify: Recommendations dựa trên assessment
   ✓ Verify: Address knowledge_gaps

5. Verify recommendation quality
   ✓ Courses follow learning progression
   ✓ Relevance scores reasonable
   ✓ Reasons explain logic
```

**Expected Results**:
- ✅ Recommendations personalized
- ✅ Multiple factors considered
- ✅ Learning path logical
- ✅ Quality explanations

---

## 📈 **TỔNG KẾT LUỒNG E2E**

### **Phân Loại Theo Độ Ưu Tiên**

| **Độ Ưu Tiên** | **Luồng E2E** | **Lý Do** |
|----------------|---------------|-----------|
| 🔴 **Critical** | E2E-01, E2E-02, E2E-03 | Authentication - Nền tảng của hệ thống |
| 🔴 **Critical** | E2E-04, E2E-05 | Assessment - Core feature AI |
| 🔴 **Critical** | E2E-06, E2E-07, E2E-08 | Learning flow - Main user journey |
| 🟡 **High** | E2E-09, E2E-10 | AI Chatbot - Key differentiator |
| 🟡 **High** | E2E-11 | Practice - Learning enhancement |
| 🟡 **High** | E2E-12, E2E-13, E2E-14 | Class management - B2B feature |
| 🟡 **High** | E2E-15, E2E-16 | Quiz management - Assessment |
| 🟢 **Medium** | E2E-17 | Personal courses - Advanced feature |
| 🟢 **Medium** | E2E-18, E2E-19, E2E-20 | Admin - Management layer |
| 🟢 **Medium** | E2E-21, E2E-22, E2E-23 | Dashboards - Analytics |
| 🟢 **Medium** | E2E-24, E2E-25 | Search & Recommendations |

### **Test Execution Strategy**

**Phase 1: Foundation (Tuần 1)**
- E2E-01 → E2E-03: Authentication flow
- E2E-06 → E2E-08: Basic learning flow

**Phase 2: Core Features (Tuần 2)**
- E2E-04 → E2E-05: Assessment & AI
- E2E-09 → E2E-11: AI features

**Phase 3: Advanced Features (Tuần 3)**
- E2E-12 → E2E-16: Class & Quiz management
- E2E-17: Personal courses

**Phase 4: Management & Analytics (Tuần 4)**
- E2E-18 → E2E-23: Admin & Dashboards
- E2E-24 → E2E-25: Search & Recommendations

### **Success Metrics**

- ✅ **Pass Rate**: ≥ 95% của test cases pass
- ✅ **Response Time**: < 2s cho non-AI endpoints, < 10s cho AI endpoints
- ✅ **Data Integrity**: 100% data consistency checks pass
- ✅ **Error Handling**: All error cases return proper status codes và messages

### **Tools & Automation**

- **Manual Testing**: Swagger UI, Postman
- **Automated Testing**: pytest với asyncio
- **CI/CD**: GitHub Actions run tests on every PR
- **Monitoring**: Track test execution times và failure rates

---

