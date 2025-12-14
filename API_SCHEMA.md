# API SCHEMA SPECIFICATION - AI LEARNING PLATFORM

> Tài liệu định nghĩa toàn bộ API endpoints và schemas dữ liệu  
> Tuân thủ theo CHUCNANG.md và ENDPOINTS_MAPPING.md  
> Người tạo: NGUYỄN NGỌC TUẤN ANH  
> Ngày cập nhật: 5/11/2025  

---

## MỤC LỤC

1. [XÁC THỰC & QUẢN LÝ TÀI KHOẢN (2.1)](#1-xác-thực--quản-lý-tài-khoản-21)
2. [ĐÁNH GIÁ NĂNG LỰC AI (2.2)](#2-đánh-giá-năng-lực-ai-22)
3. [KHÁM PHÁ & ĐĂNG KÝ KHÓA HỌC (2.3)](#3-khám-phá--đăng-ký-khóa-học-23)
4. [HỌC TẬP & THEO DÕI TIẾN ĐỘ (2.4)](#4-học-tập--theo-dõi-tiến-độ-24)
5. [KHÓA HỌC CÁ NHÂN (2.5)](#5-khóa-học-cá-nhân-25)
6. [CHATBOT HỖ TRỢ AI (2.6)](#6-chatbot-hỗ-trợ-ai-26)
7. [DASHBOARD & PHÂN TÍCH HỌC VIÊN (2.7)](#7-dashboard--phân-tích-học-viên-27)
8. [QUẢN LÝ GIẢNG VIÊN (3.x)](#8-quản-lý-giảng-viên-3x)
9. [QUẢN LÝ HỆ THỐNG ADMIN (4.x)](#9-quản-lý-hệ-thống-admin-4x)
10. [CHỨC NĂNG CHUNG (5.x)](#10-chức-năng-chung-5x)

---

## 1. XÁC THỰC & QUẢN LÝ TÀI KHOẢN (2.1)

### 1.1 Đăng ký tài khoản mới
**Endpoint:** `POST /api/v1/auth/register`  
**Quyền:** Public (không cần token)  
**Router:** `auth_router.py`  
**Controller:** `handle_register`

**Mô tả:** Tạo tài khoản mới với email, mật khẩu, tên đầy đủ. Vai trò mặc định là student. Thông tin bắt buộc: full_name (tối thiểu 2 từ), email (định dạng hợp lệ), password (tối thiểu 8 ký tự).

**Request Schema:**
```json
{
  "full_name": "string (bắt buộc, tối thiểu 2 từ, tối đa 100 ký tự)",
  "email": "string (bắt buộc, định dạng email hợp lệ, unique trong hệ thống)",
  "password": "string (bắt buộc, tối thiểu 8 ký tự, chứa số, chữ hoa, ký tự đặc biệt)"
}
```

**Response Schema (201 Created):**
```json
{
  "id": "string (UUID v4 của user được tạo)",
  "full_name": "string",
  "email": "string",
  "role": "string (mặc định: student)",
  "status": "string (active)",
  "created_at": "datetime (ISO 8601 format)",
  "message": "string (Đăng ký tài khoản thành công)"
}
```

**Error Response (400 Bad Request):**
```json
{
  "detail": "string (Email already exists | Invalid email format | Password too weak | Full name must have at least 2 words)"
}
```

---

### 1.2 Đăng nhập hệ thống
**Endpoint:** `POST /api/v1/auth/login`  
**Quyền:** Public  
**Router:** `auth_router.py`  
**Controller:** `handle_login`

**Mô tả:** Xác thực người dùng với email và password. Trả về JWT access token (thời hạn 15 phút) và refresh token (thời hạn 7 ngày) để duy trì phiên đăng nhập. Hỗ trợ "Ghi nhớ đăng nhập" để gia hạn refresh token.

**Request Schema:**
```json
{
  "email": "string (bắt buộc, email đã đăng ký)",
  "password": "string (bắt buộc, mật khẩu tài khoản)",
  "remember_me": "boolean (tùy chọn, mặc định: false, gia hạn refresh token)"
}
```

**Response Schema (200 OK):**
```json
{
  "access_token": "string (JWT token, thời hạn 15 phút)",
  "refresh_token": "string (JWT token, thời hạn 7 ngày nếu remember_me=true, 1 ngày nếu false)",
  "token_type": "string (Bearer)",
  "user": {
    "id": "string (UUID user)",
    "full_name": "string",
    "email": "string",
    "role": "string (student|instructor|admin)",
    "avatar": "string (URL avatar, có thể null)"
  }
}
```

**Error Response (401 Unauthorized):**
```json
{
  "detail": "string (Invalid email or password | Account is inactive)"
}
```

---

### 1.3 Đăng xuất tài khoản
**Endpoint:** `POST /api/v1/auth/logout`  
**Quyền:** Student, Instructor, Admin (cần access token)  
**Router:** `auth_router.py`  
**Controller:** `handle_logout`

**Mô tả:** Vô hiệu hóa token hiện tại và xóa session trên client. Đồng thời hủy bỏ tất cả refresh token liên quan để đảm bảo bảo mật.

**Request Schema:** (empty body - chỉ cần Authorization header)

**Response Schema (200 OK):**
```json
{
  "message": "string (Đăng xuất thành công)"
}
```

---

### 1.4 Xem hồ sơ cá nhân
**Endpoint:** `GET /api/v1/users/me`  
**Quyền:** Student, Instructor, Admin (cần access token)  
**Router:** `users_router.py`  
**Controller:** `handle_get_profile`

**Mô tả:** Hiển thị thông tin chi tiết người dùng: tên đầy đủ, email, avatar, bio cá nhân, sở thích học tập. Các thông tin như avatar và bio có thể null (không bắt buộc).

**Request Schema:** (không có body - thông tin lấy từ JWT token)

**Response Schema (200 OK):**
```json
{
  "id": "string (UUID user)",
  "full_name": "string",
  "email": "string",
  "role": "string (student|instructor|admin)",
  "avatar_url": "string (URL ảnh đại diện, có thể null)",
  "bio": "string (mô tả bản thân, có thể null)",
  "learning_preferences": [
    "string (danh sách sở thích học tập: Programming, Math, Business, Languages...)"
  ],
  "contact_info": "string (thông tin liên hệ, có thể null)",
  "created_at": "datetime (ngày tạo tài khoản)",
  "updated_at": "datetime (lần cập nhật cuối)"
}
```

---

### 1.5 Cập nhật hồ sơ cá nhân
**Endpoint:** `PATCH /api/v1/users/me`  
**Quyền:** Student, Instructor, Admin (cần access token)  
**Router:** `users_router.py`  
**Controller:** `handle_update_profile`

**Mô tả:** Chỉnh sửa thông tin cá nhân: tên đầy đủ, avatar, bio mô tả bản thân, thông tin liên hệ, sở thích học tập. Tất cả các trường đều tùy chọn (optional) - chỉ cập nhật những trường được gửi lên.

**Request Schema:**
```json
{
  "full_name": "string (tùy chọn, tối thiểu 2 từ)",
  "avatar_url": "string (tùy chọn, URL ảnh hợp lệ)",
  "bio": "string (tùy chọn, tối đa 500 ký tự, mô tả bản thân)",
  "contact_info": "string (tùy chọn, thông tin liên hệ)",
  "learning_preferences": [
    "string (tùy chọn, danh sách sở thích học tập)"
  ]
}
```

**Response Schema (200 OK):**
```json
{
  "id": "string (UUID user)",
  "full_name": "string",
  "email": "string",
  "role": "string",
  "avatar_url": "string (có thể null)",
  "bio": "string (có thể null)",
  "learning_preferences": ["string"],
  "contact_info": "string (có thể null)",
  "updated_at": "datetime",
  "message": "string (Cập nhật hồ sơ thành công)"
}
```

**Error Response (400 Bad Request):**
```json
{
  "detail": "string (Full name must have at least 2 words | Bio too long | Invalid avatar URL)"
}
```

---

## 2. ĐÁNH GIÁ NĂNG LỰC AI (2.2)

### 2.1 Sinh bộ câu hỏi đánh giá năng lực
**Endpoint:** `POST /api/v1/assessments/generate`  
**Quyền:** Student (cần access token)  
**Router:** `assessments_router.py`  
**Controller:** `handle_generate_assessment`

**Mô tả:** Học viên chọn lĩnh vực và chủ đề cụ thể muốn đánh giá năng lực. Lĩnh vực và chủ đề phải tuân theo các khóa học đã được tạo sẵn trong hệ thống để đảm bảo câu hỏi AI sinh ra luôn bám sát nội dung khóa học. AI tự động sinh ra bài quiz với nhiều dạng câu hỏi theo mức độ được chọn.

**Cơ chế sinh câu hỏi:** Sử dụng Google Gemini API để sinh câu hỏi tự động. AI đọc và phân tích nội dung miêu tả ngắn của các khóa học có sẵn trong hệ thống. KHÔNG sử dụng ngân hàng câu hỏi có sẵn - mỗi lần làm bài sẽ có bộ câu hỏi khác nhau.

**Phân bổ số lượng và độ khó:**

| Mức độ | Tổng câu hỏi | Câu Dễ (Easy) 20% | Câu Trung bình (Medium) 50-53% | Câu Khó (Hard) 27-30% | Thời gian |
|---------|-------------|-------------------|-------------------------------|----------------------|-----------|
| Beginner | 15 câu | 3 câu | 8 câu | 4 câu | 15 phút |
| Intermediate | 25 câu | 5 câu | 13 câu | 7 câu | 22 phút |
| Advanced | 35 câu | 7 câu | 18 câu | 10 câu | 30 phút |

**Request Schema:**
```json
{
  "category": "string (bắt buộc, ví dụ: Programming, Math, Business, Languages)",
  "subject": "string (bắt buộc, ví dụ: Python, JavaScript, Algebra, English)",
  "level": "string (bắt buộc: Beginner|Intermediate|Advanced)",
  "focus_areas": [
    "string (tùy chọn, các chủ đề con cụ thể muốn tập trung đánh giá)"
  ]
}
```

**Response Schema (201 Created):**
```json
{
  "session_id": "string (UUID phiên đánh giá, dùng để submit và lấy kết quả)",
  "category": "string",
  "subject": "string", 
  "level": "string",
  "question_count": "number (số lượng câu hỏi được sinh)",
  "time_limit_minutes": "number (thời gian làm bài)",
  "questions": [
    {
      "question_id": "string (UUID câu hỏi)",
      "question_text": "string (đề bài câu hỏi)",
      "question_type": "string (multiple_choice|fill_in_blank|drag_and_drop)",
      "difficulty": "string (easy|medium|hard)",
      "skill_tag": "string (kỹ năng được kiểm tra, ví dụ: python-syntax, algorithm-complexity)",
      "points": "number (điểm số: easy=1, medium=2, hard=3)",
      "options": [
        "string (các lựa chọn cho câu trắc nghiệm, null nếu không phải multiple_choice)"
      ],
      "correct_answer_hint": "string (gợi ý ngắn về đáp án, không spoil kết quả)"
    }
  ],
  "created_at": "datetime",
  "expires_at": "datetime (hết hạn sau 60 phút kể từ khi tạo)",
  "message": "string (Bộ câu hỏi đánh giá đã được tạo thành công)"
}
```

**Error Response (400 Bad Request):**
```json
{
  "detail": "string (Invalid category | Subject not available for this category | Invalid level)"
}

```json
{
  "session_id": "string (UUID phiên đánh giá)",
  "category": "string",
  "subject": "string",
  "level": "string",
  "time_limit": "number (phút)",
  "total_questions": "number",
  "questions": [
    {
      "question_id": "string (UUID câu hỏi)",
      "question_text": "string (đề bài câu hỏi)",
      "question_type": "string (multiple_choice|fill_in_blank|drag_and_drop)",
      "difficulty": "string (easy|medium|hard)",
      "skill_tag": "string (kỹ năng được kiểm tra)",
      "points": "number (điểm số: easy=1, medium=2, hard=3)",
      "options": [
        "string (các lựa chọn cho câu trắc nghiệm, null nếu không phải multiple_choice)"
      ],
      "correct_answer_hint": "string (gợi ý ngắn về đáp án)"
    }
  ],
  "created_at": "datetime",
  "expires_at": "datetime (hết hạn sau 60 phút)",
  "message": "string (Bộ câu hỏi đánh giá đã được tạo thành công)"
}
```

**Error Response (400 Bad Request):**
```json
{
  "detail": "string (Invalid category | Subject not available | Invalid level)"
}
```

---

### 2.2 Nộp bài đánh giá năng lực
**Endpoint:** `POST /api/v1/assessments/{session_id}/submit`  
**Quyền:** Student (cần access token)  
**Router:** `assessments_router.py`  
**Controller:** `handle_submit_assessment`

**Mô tả:** Học viên làm bài theo session_id được tạo và gửi kết quả lên hệ thống khi hoàn thành. AI tự động chấm điểm dựa trên thuật toán có trọng số (câu khó có điểm cao hơn câu dễ).

**Request Schema:**
```json
{
  "answers": [
    {
      "question_id": "string (UUID câu hỏi)",
      "answer_content": "string (đáp án của học viên)",
      "selected_option": "number (chỉ số đáp án cho multiple_choice: 0,1,2,3)",
      "time_taken_seconds": "number (thời gian làm câu này)"
    }
  ],
  "total_time_seconds": "number (tổng thời gian làm bài)",
  "submitted_at": "datetime (thời gian nộp bài)"
}
```

**Response Schema (200 OK):**
```json
{
  "session_id": "string (UUID)",
  "submitted_at": "datetime",
  "total_questions": "number",
  "time_taken_minutes": "number",
  "status": "string (submitted - chờ chấm điểm)",
  "message": "string (Bài làm đã được nộp thành công. Kết quả sẽ có sau vài giây.)"
}
```

**Error Response (400 Bad Request):**
```json
{
  "detail": "string (Session expired | Already submitted | Invalid session_id | Missing answers)"
}
```

---

### 2.3 Xem kết quả và phân tích năng lực chi tiết
**Endpoint:** `GET /api/v1/assessments/{session_id}/results`  
**Quyền:** Student (cần access token, phải là chủ sở hữu session)  
**Router:** `assessments_router.py`  
**Controller:** `handle_get_assessment_results`

**Mô tả:** AI thực hiện phân tích sâu về năng lực học viên theo 4 khía cạnh: (1) Điểm tổng thể, (2) Phân loại trình độ chính xác, (3) Xác định điểm mạnh và điểm yếu cụ thể, (4) Phát hiện lỗ hổng kiến thức.

**Hệ thống tính điểm có trọng số:**
- Câu dễ (Easy): 1 điểm
- Câu trung bình (Medium): 2 điểm  
- Câu khó (Hard): 3 điểm
- **Công thức:** (Điểm đạt được / Tổng điểm tối đa) × 100

**Ngưỡng đánh giá trình độ:**
- **Beginner:** < 60 điểm
- **Intermediate:** 60-80 điểm
- **Advanced:** > 80 điểm

**Response Schema (200 OK):**
```json
{
  "session_id": "string (UUID)",
  "assessment_info": {
    "category": "string",
    "subject": "string", 
    "level": "string",
    "completed_at": "datetime"
  },
  "overall_score": "number (0-100, điểm tổng thể)",
  "proficiency_level": "string (Beginner|Intermediate|Advanced, trình độ thực tế)",
  "total_questions": "number",
  "correct_answers": "number",
  "score_breakdown": {
    "easy_questions": {
      "total": "number",
      "correct": "number", 
      "score_percentage": "number"
    },
    "medium_questions": {
      "total": "number",
      "correct": "number",
      "score_percentage": "number" 
    },
    "hard_questions": {
      "total": "number",
      "correct": "number",
      "score_percentage": "number"
    }
  },
  "skill_analysis": [
    {
      "skill_tag": "string (ví dụ: python-syntax, algorithm-complexity)",
      "questions_count": "number (số câu hỏi về skill này)",
      "correct_count": "number (số câu trả lời đúng)",
      "proficiency_percentage": "number (0-100)",
      "strength_level": "string (Strong|Average|Weak)",
      "detailed_feedback": "string (nhận xét chi tiết về skill này)"
    }
  ],
  "knowledge_gaps": [
    {
      "gap_area": "string (lĩnh vực thiếu kiến thức)",
      "description": "string (mô tả chi tiết lỗ hổng)",
      "importance": "string (High|Medium|Low)",
      "suggested_action": "string (hành động được đề xuất)"
    }
  ],
  "time_analysis": {
    "total_time_seconds": "number",
    "average_time_per_question": "number",
    "fastest_question_time": "number",
    "slowest_question_time": "number"
  },
  "ai_feedback": "string (nhận xét tổng quan và chi tiết từ AI về kết quả làm bài)"
}
```

**Error Response (404 Not Found):**
```json
{
  "detail": "string (Assessment session not found | Results not available yet | Session expired)"
}
```

---

### 2.4 Nhận đề xuất lộ trình học tập cá nhân hóa
**Endpoint:** `GET /api/v1/recommendations/from-assessment`  
**Quyền:** Student (cần access token)  
**Router:** `recommendation_router.py`  
**Controller:** `handle_get_assessment_recommendations`

**Mô tả:** Dựa trên kết quả phân tích chi tiết từ bước 2.3, AI sinh ra lộ trình học tập được cá nhân hóa hoàn toàn cho từng học viên bao gồm: (1) Danh sách khóa học được đề xuất theo thứ tự ưu tiên, (2) Các module cần tập trung học đầu tiên, (3) Thứ tự học tối ưu, (4) Các bài tập ôn luyện.

**Query Parameters:**
```
session_id: string (bắt buộc, UUID của phiên đánh giá đã hoàn thành)
```

**Response Schema (200 OK):**
```json
{
  "assessment_session_id": "string (UUID)",
  "user_proficiency_level": "string (Beginner|Intermediate|Advanced)",
  "recommended_courses": [
    {
      "course_id": "string (UUID khóa học được đề xuất)",
      "title": "string",
      "description": "string",
      "category": "string", 
      "level": "string",
      "thumbnail_url": "string (có thể null)",
      "priority_rank": "number (1=ưu tiên cao nhất)",
      "relevance_score": "number (0-100, độ phù hợp với kết quả đánh giá)",
      "reason": "string (lý do AI đề xuất khóa học này)",
      "addresses_gaps": [
        "string (các lỗ hổng kiến thức mà khóa này sẽ giải quyết)"
      ],
      "estimated_completion_days": "number"
    }
  ],
  "suggested_learning_order": [
    {
      "step": "number (thứ tự học tập từ 1)",
      "course_id": "string (UUID)",
      "focus_modules": [
        "string (tên modules cần tập trung học đầu tiên trong khóa này)"
      ],
      "why_this_order": "string (giải thích tại sao học theo thứ tự này)"
    }
  ],
  "practice_exercises": [
    {
      "skill_tag": "string (kỹ năng cần luyện tập để củng cố)",
      "exercise_type": "string (coding|quiz|project|reading)",
      "description": "string (mô tả bài tập cụ thể)",
      "difficulty": "string (easy|medium|hard)",
      "estimated_time_hours": "number"
    }
  ],
  "total_estimated_hours": "number (tổng thời gian học tập ước tính)",
  "ai_personalized_advice": "string (lời khuyên cá nhân hóa từ AI dựa trên kết quả đánh giá)"
}
```

**Error Response (404 Not Found):**
```json
{
  "detail": "string (Assessment session not found | No recommendations available | Session expired)"
}
```

---

## 3. KHÁM PHÁ & ĐĂNG KÝ KHÓA HỌC (2.3)

### 3.1 Tìm kiếm khóa học nâng cao
**Endpoint:** `GET /api/v1/courses/search`  
**Quyền:** Student (cần access token)  
**Router:** `courses_router.py`  
**Controller:** `handle_search_courses`

**Mô tả:** Tìm kiếm khóa học theo nhiều tiêu chí: (1) Từ khóa (tên khóa học, mô tả), (2) Danh mục (Programming, Math, Business...), (3) Cấp độ (Beginner/Intermediate/Advanced). Hỗ trợ filter nâng cao: lọc theo thời lượng, ngày tạo, số học viên đã đăng ký. Hỗ trợ sắp xếp: mới nhất, cũ nhất. Kết quả tìm kiếm hiển thị real-time khi người dùng nhập.

**Query Parameters:**
```
keyword: string (tìm kiếm theo tên khóa học, mô tả, tùy chọn)
category: string (lọc theo danh mục: Programming|Math|Business|Languages, tùy chọn)
level: string (lọc cấp độ: Beginner|Intermediate|Advanced, tùy chọn)
min_duration: number (thời lượng tối thiểu tính bằng phút, tùy chọn)
max_duration: number (thời lượng tối đa tính bằng phút, tùy chọn)
instructor_id: string (lọc theo giảng viên, UUID, tùy chọn)
sort_by: string (created_at|enrollment_count|avg_rating, mặc định: created_at)
sort_order: string (asc|desc, mặc định: desc)
skip: number (pagination offset, mặc định: 0)
limit: number (số khóa học mỗi trang, mặc định: 10, tối đa: 100)
```

**Response Schema (200 OK):**
```json
{
  "courses": [
    {
      "id": "string (UUID khóa học)",
      "title": "string",
      "description": "string (mô tả ngắn gọn 2-3 câu)",
      "category": "string (danh mục khóa học)",
      "level": "string (Beginner|Intermediate|Advanced)",
      "thumbnail_url": "string (URL ảnh đại diện, có thể null)",
      "total_modules": "number (số lượng modules)",
      "total_lessons": "number (số lượng bài học)",
      "total_duration_minutes": "number (tổng thời lượng học)",
      "enrollment_count": "number (số học viên đã đăng ký)",
      "avg_rating": "number (điểm đánh giá trung bình 0-5, có thể null)",
      "instructor_name": "string (tên giảng viên)",
      "instructor_avatar": "string (avatar giảng viên, có thể null)",
      "instructor_bio": "string (tiểu sử giảng viên, có thể null)",
      "is_enrolled": "boolean (user hiện tại đã đăng ký chưa)",
      "created_at": "datetime"
    }
  ],
  "total": "number (tổng số khóa học tìm được)",
  "skip": "number (offset hiện tại)",
  "limit": "number (giới hạn mỗi trang)",
  "search_metadata": {
    "keyword_used": "string (từ khóa đã tìm, có thể null)",
    "filters_applied": {
      "category": "string (có thể null)",
      "level": "string (có thể null)",
      "duration_range": "string (có thể null)"
    },
    "search_time_ms": "number (thời gian tìm kiếm)"
  }
}
```

**Error Response (400 Bad Request):**
```json
{
  "detail": "string (Invalid sort_by parameter | Invalid level parameter | Limit exceeds maximum)"
}
```

---

### 3.2 Xem danh sách khóa học công khai
**Endpoint:** `GET /api/v1/courses/public`  
**Quyền:** Student (cần access token)  
**Router:** `courses_router.py`  
**Controller:** `handle_list_public_courses`

**Mô tả:** Hiển thị tất cả khóa học đã được Admin publish công khai. Mỗi khóa học hiển thị: (1) Tiêu đề và hình ảnh đại diện, (2) Mô tả ngắn gọn (2-3 câu), (3) Thời lượng học tập ước tính, (4) Số lượng modules và lessons, (5) Cấp độ khóa học. Layout dạng grid card với pagination để dễ duyệt.

**Query Parameters:**
```
skip: number (pagination offset, mặc định: 0)
limit: number (số khóa học mỗi trang, mặc định: 10, tối đa: 50)
category: string (lọc theo danh mục, tùy chọn)
level: string (lọc theo cấp độ, tùy chọn)
```

**Response Schema (200 OK):** (Tương tự như 3.1 nhưng chỉ hiển thị khóa học public)

---

### 3.3 Xem chi tiết khóa học đầy đủ
**Endpoint:** `GET /api/v1/courses/{course_id}`  
**Quyền:** Student (cần access token)  
**Router:** `courses_router.py`  
**Controller:** `handle_get_course_detail`

**Mô tả:** Hiển thị thông tin đầy đủ và toàn diện về khóa học: (1) Thông tin tổng quan: tiêu đề, mô tả chi tiết, hình ảnh/video giới thiệu, (2) Cấu trúc khóa học: danh sách modules và lessons (có thể expand/collapse), (3) Mục tiêu học tập (Learning Outcomes) - những gì học viên sẽ đạt được sau khóa học, (4) Yêu cầu đầu vào (Prerequisites) - kiến thức cần có trước khi học, (5) Thông tin giảng viên: tên, avatar, bio, kinh nghiệm, (6) Video preview để xem trước nội dung. Nếu đã đăng ký: hiển thị thêm tiến độ học tập hiện tại và nút "Tiếp tục học".

**Path Parameters:**
```
course_id: string (bắt buộc, UUID của khóa học cần xem)
```

**Response Schema (200 OK):**
```json
{
  "id": "string (UUID khóa học)",
  "title": "string",
  "description": "string (mô tả chi tiết đầy đủ về khóa học)",
  "category": "string",
  "level": "string (Beginner|Intermediate|Advanced)",
  "thumbnail_url": "string",
  "preview_video_url": "string (URL video preview, có thể null)",
  "language": "string (ngôn ngữ khóa học, ví dụ: vi, en)",
  "status": "string (published|draft|archived)",
  "owner_info": {
    "id": "string (UUID giảng viên)",
    "name": "string (tên giảng viên)",
    "avatar_url": "string (URL avatar, có thể null)",
    "bio": "string (tiểu sử giảng viên, có thể null)",
    "experience_years": "number (số năm kinh nghiệm, có thể null)"
  },
  "learning_outcomes": [
    {
      "description": "string (mục tiêu cụ thể, đo lường được)",
      "skill_tag": "string (kỹ năng liên quan)"
    }
  ],
  "prerequisites": [
    "string (yêu cầu kiến thức đầu vào)"
  ],
  "modules": [
    {
      "id": "string (UUID module)",
      "title": "string",
      "description": "string",
      "difficulty": "string (Basic|Intermediate|Advanced)",
      "estimated_hours": "number (thời gian học ước tính)",
      "lessons": [
        {
          "id": "string (UUID lesson)",
          "title": "string",
          "order": "number (thứ tự lesson trong module)",
          "duration_minutes": "number",
          "content_type": "string (text|video|quiz|mixed)",
          "is_completed": "boolean (nếu user đã đăng ký khóa học)"
        }
      ]
    }
  ],
  "course_statistics": {
    "total_modules": "number",
    "total_lessons": "number", 
    "total_duration_minutes": "number",
    "enrollment_count": "number (số học viên đã đăng ký)",
    "completion_rate": "number (tỷ lệ hoàn thành trung bình, 0-100)",
    "avg_rating": "number (điểm đánh giá trung bình 0-5, có thể null)"
  },
  "enrollment_info": {
    "is_enrolled": "boolean",
    "enrollment_id": "string (UUID nếu đã đăng ký, null nếu chưa)",
    "enrolled_at": "datetime (nếu đã đăng ký, null nếu chưa)",
    "progress_percent": "number (0-100 nếu đã đăng ký, null nếu chưa)",
    "can_access_content": "boolean"
  },
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

**Error Response (404 Not Found):**
```json
{
  "detail": "string (Course not found | Course is not published)"
}
```

---

### 3.4 Đăng ký tham gia khóa học
**Endpoint:** `POST /api/v1/enrollments`  
**Quyền:** Student (cần access token)  
**Router:** `enrollments_router.py`  
**Controller:** `handle_enroll_course`

**Mô tả:** Học viên đăng ký tham gia khóa học bằng course_id. Luồng xử lý: (1) Học viên xem chi tiết khóa học và click nút "Đăng ký", (2) Hệ thống kiểm tra điều kiện: đã đăng ký khóa này chưa, (3) Nếu hợp lệ, tạo bản ghi enrollment mới với trạng thái "active", (4) Trả về thông báo thành công và chuyển hướng đến trang học tập. Ghi nhận thời gian đăng ký để tracking.

**Request Schema:**
```json
{
  "course_id": "string (bắt buộc, UUID của khóa học muốn đăng ký)"
}
```

**Response Schema (201 Created):**
```json
{
  "id": "string (UUID enrollment được tạo)",
  "user_id": "string (UUID học viên)",
  "course_id": "string (UUID khóa học)",
  "course_title": "string (tên khóa học)",
  "status": "string (active)",
  "enrolled_at": "datetime (thời gian đăng ký)",
  "progress_percent": "number (0, khởi tạo với 0%)",
  "completion_rate": "number (0, khởi tạo với 0% - alias của progress_percent)",
  "message": "string (Đăng ký khóa học thành công. Chúc bạn học tập hiệu quả!)"
}
```

**Error Response (400 Bad Request):**
```json
{
  "detail": "string (Already enrolled in this course | Course not found | Course is not available for enrollment)"
}
```

**Error Response (403 Forbidden):**
```json
{
  "detail": "string (Course requires premium subscription | Age restriction not met)"
}
```

---

### 3.5 Xem danh sách khóa học đã đăng ký
**Endpoint:** `GET /api/v1/enrollments/my-courses`  
**Quyền:** Student (cần access token)  
**Router:** `enrollments_router.py`  
**Controller:** `handle_list_my_enrollments`

**Query Parameters:**
```
status: string (in-progress|completed|cancelled, lọc theo trạng thái, tùy chọn)
skip: number (pagination offset, mặc định: 0)
limit: number (số enrollment mỗi trang, mặc định: 10)
sort_by: string (enrolled_at|progress_percent|course_title, mặc định: enrolled_at)
sort_order: string (asc|desc, mặc định: desc)
```

**Response Schema (200 OK):**
```json
{
  "enrollments": [
    {
      "id": "string (UUID enrollment)",
      "course_id": "string (UUID khóa học)",
      "course_title": "string",
      "course_description": "string (mô tả ngắn)",
      "course_thumbnail": "string (URL ảnh đại diện)",
      "course_level": "string (Beginner|Intermediate|Advanced)",
      "instructor_name": "string",
      "instructor_bio": "string (tiểu sử giảng viên, có thể null)",
      "status": "string (in-progress|completed|cancelled)",
      "progress_percent": "number (0-100, tiến độ hoàn thành)",
      "enrolled_at": "datetime (ngày đăng ký)",
      "last_accessed_at": "datetime (lần truy cập cuối, có thể null)",
      "completed_at": "datetime (ngày hoàn thành, null nếu chưa xong)",
      "avg_quiz_score": "number (0-100, điểm trung bình quiz, có thể null)",
      "total_time_spent_minutes": "number (thời gian học đã dành)",
      "next_lesson": {
        "lesson_id": "string (UUID lesson tiếp theo, null nếu đã xong)",
        "lesson_title": "string (null nếu đã xong)",
        "module_title": "string (null nếu đã xong)"
      }
    }
  ],
  "summary": {
    "total_enrollments": "number",
    "in_progress": "number", 
    "completed": "number",
    "cancelled": "number"
  },
  "skip": "number",
  "limit": "number"
}
```

---

### 3.6 Xem chi tiết một enrollment cụ thể
**Endpoint:** `GET /api/v1/enrollments/{enrollment_id}`  
**Quyền:** Student (phải là chủ sở hữu enrollment)  
**Router:** `enrollments_router.py`  
**Controller:** `handle_get_enrollment_detail`

**Mô tả:** Xem thông tin chi tiết về một enrollment cụ thể: thông tin khóa học, ngày đăng ký, tiến độ hiện tại, điểm quiz trung bình, trạng thái. Cần thiết: Khi user click vào một khóa học trong danh sách my-courses để xem thông tin đầy đủ trước khi tiếp tục học.

**Response Schema (200 OK):**
```json
{
  "id": "string (UUID enrollment)",
  "user_id": "string (UUID học viên)",
  "course_id": "string (UUID)",
  "course_title": "string",
  "course_description": "string",
  "course_thumbnail": "string (URL)",
  "instructor_name": "string",
  "instructor_bio": "string (tiểu sử giảng viên, có thể null)",
  "status": "string (active|completed|cancelled)",
  "enrolled_at": "datetime (thời gian đăng ký)",
  "completed_at": "datetime (có thể null)",
  "progress_percent": "number (0-100)",
  "avg_quiz_score": "number (0-100, điểm trung bình tất cả quiz)",
  "total_modules": "number",
  "completed_modules": "number",
  "total_lessons": "number",
  "completed_lessons": "number"
}
```

**Ghi chú:**
- API này cần thiết khi user click vào một khóa học trong danh sách my-courses
- Hiển thị thông tin đầy đủ trước khi tiếp tục học

---

### 3.7 Kiểm tra trạng thái đăng ký khóa học
**Endpoint:** `GET /api/v1/courses/{course_id}/enrollment-status`  
**Quyền:** Student (cần access token)  
**Router:** `courses_router.py` | **Controller:** `handle_check_course_enrollment_status`

**Mô tả:** Kiểm tra trạng thái đăng ký hiện tại của user với một khóa học cụ thể. Cần thiết: Validation trước khi cho phép truy cập nội dung lesson/module, hiển thị button "Đăng ký" hoặc "Tiếp tục học".

**Response Schema (200 OK):**
```json
{
  "enrolled": "boolean (đã đăng ký hay chưa)",
  "status": "string (active|completed|cancelled, null nếu chưa đăng ký)",
  "enrollment_id": "string (UUID, null nếu chưa đăng ký)",
  "can_access_content": "boolean (có thể truy cập nội dung không)",
  "enrollment_date": "datetime (ngày đăng ký, null nếu chưa)",
  "progress_percent": "number (0-100, null nếu chưa đăng ký)"
}
```

---

### 3.8 Hủy đăng ký khóa học
**Endpoint:** `DELETE /api/v1/enrollments/{enrollment_id}`  
**Quyền:** Student (phải là owner của enrollment)  
**Router:** `enrollments_router.py` | **Controller:** `handle_unenroll_course`

**Mô tả:** Cho phép học viên rút khỏi khóa học chưa hoàn thành. Cập nhật trạng thái enrollment từ "active" thành "cancelled", nhưng KHÔNG xóa dữ liệu học tập (progress, quiz results) để học viên có thể tham khảo sau này. Học viên có thể đăng ký lại khóa học này sau nếu muốn.

**Response Schema (200 OK):**
```json
{
  "message": "string (Hủy đăng ký khóa học thành công)",
  "note": "string (Dữ liệu học tập của bạn đã được lưu lại)"
}
```

---

## 4. HỌC TẬP & THEO DÕI TIẾN ĐỘ (2.4)

### 4.1 Xem thông tin module
**Endpoint:** `GET /api/v1/courses/{course_id}/modules/{module_id}`  
**Quyền:** Student (enrolled)  
**Router:** `learning_router.py`  
**Controller:** `handle_get_module_detail`

**Mô tả:** Hiển thị thông tin chi tiết về một module trong khóa học.

**Response Schema (200 OK):**
```json
{
  "id": "string (UUID module)",
  "course_id": "string (UUID)",
  "title": "string (tiêu đề module)",
  "description": "string (mô tả chi tiết về module)",
  "difficulty": "string (Basic|Intermediate|Advanced)",
  "order": "number (thứ tự module trong khóa học)",
  "estimated_hours": "number (thời lượng học tập ước tính)",
  "learning_outcomes": [
    {
      "id": "string (UUID)",
      "outcome": "string (mô tả mục tiêu học tập cụ thể)",
      "skill_tag": "string (tag kỹ năng, vd: 'python-functions')",
      "is_mandatory": "boolean (kiến thức bắt buộc hay tùy chọn)"
    }
  ],
  "lessons": [
    {
      "id": "string (UUID lesson)",
      "title": "string (tiêu đề bài học)",
      "order": "number (thứ tự lesson trong module)",
      "duration_minutes": "number (thời lượng bài học)",
      "content_type": "string (text|video|mixed)",
      "has_quiz": "boolean (có quiz kèm theo không)",
      "is_completed": "boolean (học viên đã hoàn thành chưa)",
      "completion_date": "datetime (ngày hoàn thành, null nếu chưa xong)"
    }
  ],
  "resources": [
    {
      "id": "string (UUID)",
      "title": "string (tên tài liệu)",
      "type": "string (pdf|slide|code|link)",
      "url": "string (link download hoặc xem)",
      "is_mandatory": "boolean"
    }
  ],
  "completion_status": "string (not-started|in-progress|completed)",
  "completed_lessons": "number (số bài đã hoàn thành)",
  "total_lessons": "number (tổng số bài học)",
  "progress_percent": "number (0-100, tiến độ hoàn thành module)",
  "is_accessible": "boolean (có thể truy cập hay cần hoàn thành module trước)",
  "prerequisites": [
    "string (UUID các module tiên quyết)"
  ],
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

**Error Response (403 Forbidden):**
```json
{
  "detail": "string (Not enrolled in this course | Prerequisites not met)"
}
```

**Error Response (404 Not Found):**
```json
{
  "detail": "string (Module not found | Course not found)"
}
```

---

### 4.2 Xem nội dung bài học
**Endpoint:** `GET /api/v1/courses/{course_id}/lessons/{lesson_id}`  
**Quyền:** Student (enrolled)  
**Router:** `learning_router.py`  
**Controller:** `handle_get_lesson_content`

**Mô tả:** Truy cập và học nội dung của một lesson cụ thể. Các loại nội dung: (1) Nội dung text/HTML (bài giảng, giải thích lý thuyết), (2) Video bài giảng với player hỗ trợ tua, tốc độ phát, (3) Tài liệu đính kèm (PDF, Word, code files). Tracking tự động: Hệ thống ghi nhận thời gian học, phần nào đã xem. Tự động đánh dấu phần đã hoàn thành khi học viên xem hết.

**FIXED (Dec 07, 2025):** Response structure đã được cập nhật với navigation nested objects và quiz_info structure đầy đủ hơn.

**Path Parameters:**
```
course_id: string (bắt buộc, UUID của khóa học)
lesson_id: string (bắt buộc, UUID của lesson)
```

**Response Schema (200 OK):**
```json
{
  "id": "string (UUID lesson)",
  "module_id": "string (UUID module chứa lesson này)",
  "course_id": "string (UUID khóa học)",
  "title": "string (tiêu đề bài học)",
  "description": "string (mô tả ngắn gọn về bài học)",
  "order": "number (thứ tự trong module)",
  "duration_minutes": "number (thời lượng ước tính)",
  "content_type": "string (text|video|document|code|mixed)",
  "content": {
    "text_content": "string (HTML content cho phần lý thuyết, có thể null)",
    "video_url": "string (URL video bài giảng, có thể null)",
    "video_duration": "number (thời lượng video tính bằng giây, có thể null)",
    "video_thumbnail": "string (URL ảnh thumbnail video, có thể null)",
    "attachments": [
      {
        "id": "string (UUID tài liệu đính kèm)",
        "name": "string (tên file)",
        "type": "string (pdf|word|pptx|code|external_link)",
        "url": "string (link download hoặc xem)",
        "size": "number (kích thước file bytes, null cho external link)"
      }
    ],
    "code_snippets": [
      {
        "language": "string (python|javascript|java|...)",
        "code": "string (nội dung code)",
        "description": "string (giải thích đoạn code)"
      }
    ]
  },
  "learning_objectives": [
    "string (mục tiêu cụ thể của bài học này)"
  ],
  "resources": [
    {
      "id": "string (UUID)",
      "type": "string (pdf|word|pptx|code|external_link)",
      "title": "string (tên tài liệu)",
      "description": "string (mô tả tài liệu)",
      "url": "string (link download hoặc xem online)",
      "file_size_bytes": "number (kích thước file, null cho external link)",
      "is_downloadable": "boolean"
    }
  ],
  "has_quiz": "boolean (bài học có quiz kèm theo không)",
  "quiz_info": {
    "quiz_id": "string (UUID quiz, null nếu has_quiz=false)",
    "question_count": "number (số câu hỏi trong quiz, null nếu has_quiz=false)",
    "is_mandatory": "boolean (bắt buộc làm quiz để tiếp tục, null nếu has_quiz=false)"
  },
  "completion_status": {
    "is_completed": "boolean (đã hoàn thành bài học chưa)",
    "completion_date": "datetime (ngày hoàn thành, null nếu chưa xong)",
    "time_spent_minutes": "number (thời gian đã dành cho bài học này)",
    "video_progress_percent": "number (0-100, tiến độ xem video, null nếu không có video)"
  },
  "navigation": {
    "previous_lesson": {
      "id": "string (UUID, null nếu là lesson đầu tiên)",
      "title": "string (tiêu đề lesson trước, null nếu là lesson đầu tiên)"
    },
    "next_lesson": {
      "id": "string (UUID, null nếu là lesson cuối hoặc chưa unlock)",
      "title": "string (tiêu đề lesson kế tiếp, null nếu là lesson cuối hoặc chưa unlock)",
      "is_locked": "boolean (có bị khóa không, cần hoàn thành lesson hiện tại)"
    }
  },
  "created_at": "datetime (thời gian tạo lesson)",
  "updated_at": "datetime (thời gian cập nhật gần nhất)"
}
```

**Error Response (403 Forbidden):**
```json
{
  "detail": "string (Not enrolled in this course | Lesson is locked - complete previous lesson first)"
}
```

**Error Response (404 Not Found):**
```json
{
  "detail": "string (Lesson not found | Course not found)"
}
```

---

### 4.3 Lấy danh sách modules trong khóa học
**Endpoint:** `GET /api/v1/courses/{course_id}/modules`  
**Quyền:** Student (enrolled)  
**Router:** `learning_router.py`  
**Controller:** `handle_get_course_modules`

**Mô tả:** Hiển thị toàn bộ modules trong khóa học với thông tin cơ bản và trạng thái hoàn thành. Giúp học viên có cái nhìn tổng quan về cấu trúc khóa học và tiến độ của mình.

**Path Parameters:**
```
course_id: string (bắt buộc, UUID của khóa học)
```

**Response Schema (200 OK):**
```json
{
  "course_id": "string (UUID)",
  "course_title": "string (tên khóa học)",
  "total_modules": "number (tổng số modules)",
  "completed_modules": "number (số modules đã hoàn thành)",
  "overall_progress": "number (0-100, % tiến độ toàn khóa học)",
  "modules": [
    {
      "id": "string (UUID module)",
      "title": "string (tiêu đề module)",
      "description": "string (mô tả ngắn gọn)",
      "order": "number (thứ tự module)",
      "difficulty": "string (Basic|Intermediate|Advanced)",
      "estimated_hours": "number (thời lượng ước tính)",
      "total_lessons": "number (tổng số bài học trong module)",
      "completed_lessons": "number (số bài đã hoàn thành)",
      "progress_percent": "number (0-100, tiến độ module)",
      "is_accessible": "boolean (có thể học hay cần hoàn thành module trước)",
      "unlock_condition": "string (điều kiện để mở khóa module, ví dụ: Complete Module 1)",
      "status": "string (not_started|in_progress|completed)",
      "completion_date": "datetime (ngày hoàn thành, null nếu chưa xong)"
    }
  ]
}
```

**Error Response (403 Forbidden):**
```json
{
  "detail": "string (Not enrolled in this course)"
}
```

---

### 4.4 Lấy kết quả học tập module
**Endpoint:** `GET /api/v1/courses/{course_id}/modules/{module_id}/outcomes`  
**Quyền:** Student (enrolled)  
**Router:** `learning_router.py`  
**Controller:** `handle_get_module_outcomes`

**Mô tả:** Xem chi tiết kết quả học tập và skill đã đạt được sau khi hoàn thành module. Giúp học viên biết mình đã master được những kỹ năng gì và còn thiếu sót ở đâu.

**Path Parameters:**
```
course_id: string (bắt buộc, UUID của khóa học)
module_id: string (bắt buộc, UUID của module)
```

**Response Schema (200 OK):**
```json
{
  "module_id": "string (UUID)",
  "module_title": "string",
  "completion_status": "string (completed|in_progress|not_started)",
  "completion_date": "datetime (ngày hoàn thành module, null nếu chưa xong)",
  "overall_score": "number (0-100, điểm tổng hợp của module)",
  "achieved_outcomes": [
    {
      "outcome_id": "string (UUID)",
      "description": "string (mô tả mục tiêu đã đạt được)",
      "skill_tag": "string (kỹ năng tương ứng)",
      "achievement_level": "string (mastered|proficient|basic|not_achieved)",
      "achievement_date": "datetime (ngày đạt được)",
      "evidence_score": "number (0-100, điểm chứng minh đạt được skill)",
      "quiz_scores": [
        {
          "quiz_id": "string (UUID)",
          "score": "number (0-100)"
        }
      ]
    }
  ],
  "skills_acquired": [
    {
      "skill_tag": "string (tên kỹ năng)",
      "proficiency_level": "string (mastered|proficient|basic)",
      "related_lessons": ["string (UUID các lessons liên quan)"]
    }
  ],
  "areas_for_improvement": [
    {
      "skill_tag": "string (kỹ năng cần cải thiện)",
      "current_level": "string (basic|not_achieved)",
      "target_level": "string (proficient|mastered)",
      "recommended_actions": [
        "string (hành động được đề xuất, ví dụ: Ôn lại Lesson 3)"
      ]
    }
  ],
  "next_recommended_modules": [
    {
      "module_id": "string (UUID)",
      "title": "string",
      "reason": "string (lý do đề xuất học module này tiếp theo)"
    }
  ]
}
```

**Error Response (403 Forbidden):**
```json
{
  "detail": "string (Not enrolled in this course)"
}
```

---

### 4.5 Lấy tài liệu học tập module
**Endpoint:** `GET /api/v1/courses/{course_id}/modules/{module_id}/resources`  
**Quyền:** Student (enrolled)  
**Router:** `learning_router.py`  
**Controller:** `handle_get_module_resources`

**Mô tả:** Tải về hoặc xem các tài liệu bổ sung: slides, PDF, code examples, external links. Tài liệu được phân loại theo loại và mức độ quan trọng (mandatory/optional).

**Path Parameters:**
```
course_id: string (bắt buộc, UUID của khóa học)
module_id: string (bắt buộc, UUID của module)
```

**Response Schema (200 OK):**
```json
{
  "module_id": "string (UUID)",
  "module_title": "string",
  "total_resources": "number (tổng số tài liệu)",
  "mandatory_resources": "number (số tài liệu bắt buộc)",
  "resources": [
    {
      "id": "string (UUID resource)",
      "title": "string (tên tài liệu)",
      "type": "string (pdf|slide|video|code|article|external_link|book)",
      "description": "string (mô tả chi tiết về tài liệu)",
      "url": "string (link download hoặc xem trực tuyến)",
      "file_size_bytes": "number (kích thước file, null cho external link)",
      "file_format": "string (định dạng file: pdf, pptx, zip, null cho link)",
      "duration_minutes": "number (thời lượng cho video/audio, null cho file khác)",
      "is_mandatory": "boolean (tài liệu bắt buộc hay tùy chọn)",
      "is_downloadable": "boolean (có thể tải về không)",
      "language": "string (ngôn ngữ tài liệu: vi, en)",
      "author": "string (tác giả tài liệu, có thể null)",
      "published_date": "datetime (ngày xuất bản, có thể null)",
      "tags": ["string (các tag để phân loại tài liệu)"],
      "preview_available": "boolean (có thể xem trước không)",
      "access_count": "number (số lần tài liệu được truy cập)",
      "rating": "number (0-5, đánh giá của học viên, có thể null)"
    }
  ],
  "resource_categories": [
    {
      "category": "string (theory|practice|reference|supplementary)",
      "count": "number (số tài liệu trong category này)"
    }
  ]
}
```

**Error Response (403 Forbidden):**
```json
{
  "detail": "string (Not enrolled in this course)"
}
```

---

### 4.6 Sinh bài kiểm tra module tự động
**Endpoint:** `POST /api/v1/courses/{course_id}/modules/{module_id}/assessments/generate`  
**Quyền:** Student (enrolled)  
**Router:** `learning_router.py`  
**Controller:** `handle_generate_module_assessment`

**Mô tả:** AI tự động sinh bài kiểm tra ngắn cho module dựa trên nội dung đã học để củng cố kiến thức. Học viên có thể tùy chỉnh số câu hỏi, độ khó và loại bài kiểm tra.

**Path Parameters:**
```
course_id: string (bắt buộc, UUID của khóa học)
module_id: string (bắt buộc, UUID của module)
```

**Request Schema:**
```json
{
  "assessment_type": "string (bắt buộc: review|practice|final_check)",
  "question_count": "number (tùy chọn, 5-15 câu, mặc định: 10)",
  "difficulty_preference": "string (tùy chọn: easy|mixed|hard, mặc định: mixed)",
  "focus_topics": [
    "string (tùy chọn, các skill tags cần tập trung)"
  ],
  "time_limit_minutes": "number (tùy chọn, thời gian làm bài, mặc định: 15)"
}
```

**Response Schema (201 Created):**
```json
{
  "assessment_id": "string (UUID bài kiểm tra được tạo)",
  "module_id": "string (UUID)",
  "module_title": "string",
  "assessment_type": "string (review|practice|final_check)",
  "question_count": "number (số câu hỏi thực tế)",
  "time_limit_minutes": "number (thời gian làm bài)",
  "total_points": "number (tổng điểm tối đa)",
  "pass_threshold": "number (điểm pass tối thiểu, thường 70%)",
  "questions": [
    {
      "question_id": "string (UUID)",
      "order": "number (thứ tự câu hỏi)",
      "question_text": "string (nội dung câu hỏi)",
      "question_type": "string (multiple_choice|fill_in_blank|true_false|short_answer)",
      "difficulty": "string (easy|medium|hard)",
      "skill_tag": "string (kỹ năng được kiểm tra)",
      "points": "number (điểm của câu hỏi này)",
      "is_mandatory": "boolean (câu điểm liệt hay không)",
      "options": [
        {
          "option_id": "string (A|B|C|D)",
          "content": "string (nội dung đáp án)"
        }
      ],
      "hint": "string (gợi ý nhỏ cho học viên, có thể null)"
    }
  ],
  "instructions": "string (hướng dẫn làm bài)",
  "created_at": "datetime",
  "expires_at": "datetime (thời hạn làm bài, thường là 60 phút sau khi tạo)",
  "can_retake": "boolean (có thể làm lại hay không)",
  "message": "string (Bài kiểm tra module đã được tạo thành công)"
}
```

**Error Response (400 Bad Request):**
```json
{
  "detail": "string (Invalid question_count | Module not completed yet | Assessment type not supported)"
}
```

**Error Response (403 Forbidden):**
```json
{
  "detail": "string (Not enrolled in this course | Module not accessible)"
}
```

---

### 4.7 Xem thông tin quiz trước khi làm bài
**Endpoint:** `GET /api/v1/quizzes/{quiz_id}`  
**Quyền:** Student

**Response Schema (200 OK):**
```json
{
  "id": "string (UUID quiz)",
  "title": "string",
  "description": "string",
  "question_count": "number (số lượng câu hỏi)",
  "time_limit": "number (thời gian làm bài - phút)",
  "pass_threshold": "number (điểm pass tối thiểu %)",
  "mandatory_question_count": "number (số câu điểm liệt)",
  "user_attempts": "number (số lần đã làm)",
  "best_score": "number (điểm cao nhất, 0-100, null nếu chưa làm)",
  "last_attempt_at": "datetime (lần làm gần nhất, null nếu chưa làm)"
}
```

**Ghi chú:**
- Hiển thị thông tin trước khi học viên click "Bắt đầu làm bài"
- Giúp học viên biết trước số câu, thời gian, điều kiện pass

---

### 4.8 Làm bài quiz kèm theo bài học
**Endpoint:** `POST /api/v1/quizzes/{quiz_id}/attempt`  
**Quyền:** Student (enrolled)

**Request Schema:**
```json
{
  "answers": [
    {
      "question_id": "string (UUID)",
      "selected_option": "string (A|B|C|D hoặc string fill-in-blank)"
    }
  ]
}
```

**Response Schema (201 Created):**
```json
{
  "attempt_id": "string (UUID)",
  "quiz_id": "string (UUID)",
  "submitted_at": "datetime",
  "message": "string (Bài làm đã được nộp)"
}
```

---

### 4.9 Xem kết quả và giải thích chi tiết quiz
**Endpoint:** `GET /api/v1/quizzes/{quiz_id}/results`  
**Quyền:** Student

**Response Schema (200 OK):**
```json
{
  "attempt_id": "string (UUID)",
  "quiz_id": "string (UUID)",
  "total_score": "number (X/100)",
  "status": "string (Pass|Fail)",
  "pass_threshold": "number (%)",
  "results": [
    {
      "question_id": "string (UUID)",
      "question_content": "string",
      "student_answer": "string (đáp án học viên chọn)",
      "correct_answer": "string (đáp án đúng)",
      "is_correct": "boolean",
      "is_mandatory": "boolean (câu điểm liệt)",
      "score": "number",
      "explanation": "string (giải thích tại sao đúng/sai)",
      "related_lesson_link": "string (link ôn lại bài học)"
    }
  ],
  "mandatory_passed": "boolean (đã trả lời đúng tất cả câu bắt buộc)",
  "can_retake": "boolean"
}
```

**Ghi chú:**
- Điều kiện **Pass:** Đạt ≥70% điểm AND trả lời đúng tất cả câu điểm liệt
- Nếu **Fail:** học viên bắt buộc làm lại

---

### 4.10 Làm lại quiz khi chưa đạt
**Endpoint:** `POST /api/v1/quizzes/{quiz_id}/retake`
**Quyền:** Student

**Ghi chú:** Số lần làm lại không giới hạn. Học viên có thể làm lại cho đến khi pass.**Response Schema (201 Created):**
```json
{
  "new_attempt_id": "string (UUID)",
  "quiz_id": "string (UUID)",
  "message": "string (Bài làm mới được sinh ra)",
  "questions": [
    {
      "id": "string (UUID câu hỏi mới)",
      "content": "string (tương tự nội dung, nhưng khác chi tiết)",
      "options": ["string"]
    }
  ]
}
```

**Ghi chú:**
- AI sinh ra bộ câu **tương tự về nội dung nhưng khác chi tiết** (số liệu, ví dụ)
- Số lần làm lại: **KHÔNG giới hạn**
- Chỉ khi **Pass** mới được học lesson tiếp theo (unlock mechanism)

---

### 4.11 Nhận bài tập luyện tập cá nhân hóa
**Endpoint:** `POST /api/v1/ai/generate-practice`  
**Quyền:** Student  
**Router:** `learning_router.py`  
**Controller:** `learning_controller.generate_practice_exercises`

**Mô tả:** AI phân tích chi tiết các câu trả lời sai của học viên và tự động sinh ra bài tập luyện tập cá nhân hóa phù hợp. Bài tập được tạo dựa trên loại kiến thức bị thiếu, mức độ khó phù hợp, và dạng bài tương tự trong module để củng cố kiến thức. AI kết hợp và chọn lọc từ ngân hàng câu hỏi có sẵn để đảm bảo chất lượng.

**Request Schema:**
```json
{
  "lesson_id": "string (UUID bài học) - optional",
  "course_id": "string (UUID khóa học) - optional",
  "topic_prompt": "string (mô tả chủ đề cần luyện tập) - optional",
  "difficulty": "string (easy|medium|hard) - optional, default: medium",
  "question_count": "integer (số câu hỏi cần sinh) - optional, default: 5, min: 1, max: 20",
  "practice_type": "string (multiple_choice|short_answer|mixed) - optional, default: multiple_choice",
  "focus_skills": ["string (skill tags từ câu sai) - optional"]
}
```

**Ghi chú Request:**
- Phải cung cấp **ít nhất một trong ba:** `lesson_id`, `course_id`, hoặc `topic_prompt`
- `lesson_id`: Tạo bài tập dựa trên nội dung bài học cụ thể
- `course_id`: Tạo bài tập tổng hợp từ toàn bộ khóa học
- `topic_prompt`: Tạo bài tập từ mô tả tự do (VD: "Luyện tập về vòng lặp Python")
- `focus_skills`: Danh sách skill tags cần tập trung (VD: ["python-loops", "error-handling"])

**Response Schema (201 Created):**
```json
{
  "practice_id": "string (UUID)",
  "source": {
    "lesson_id": "string (UUID) - nếu có",
    "course_id": "string (UUID) - nếu có", 
    "topic_prompt": "string - nếu có"
  },
  "difficulty": "string (easy|medium|hard)",
  "exercises": [
    {
      "id": "string (UUID)",
      "type": "string (theory|coding|problem-solving)",
      "question": "string (nội dung câu hỏi)",
      "options": ["string (các lựa chọn)"] // nếu là multiple_choice
      "correct_answer": "string (đáp án đúng)",
      "explanation": "string (giải thích chi tiết)",
      "difficulty": "string (Easy|Medium|Hard)",
      "related_skill": "string (skill tag)",
      "points": "integer (điểm số của câu hỏi)"
    }
  ],
  "total_questions": "integer (tổng số câu)",
  "estimated_time": "integer (thời gian làm bài ước tính - phút)",
  "created_at": "string (ISO 8601 datetime)",
  "message": "string (Bài luyện tập cá nhân hóa được sinh thành công)"
}
```

**Response Schema (400 Bad Request):**
```json
{
  "detail": "string (Phải cung cấp ít nhất một trong: lesson_id, course_id, hoặc topic_prompt)"
}
```

**Response Schema (404 Not Found):**
```json
{
  "detail": "string (Không tìm thấy lesson/course với ID này)"
}
```

**Ghi chú:**
- AI **không tạo hoàn toàn mới** mà kết hợp và chọn lọc từ ngân hàng câu hỏi có sẵn
- Bài tập bao gồm **cả lý thuyết và thực hành** để học viên vừa hiểu vừa biết vận dụng
- Mức độ khó được điều chỉnh phù hợp với trình độ hiện tại của học viên
- `focus_skills` giúp AI tập trung vào những kiến thức cụ thể cần củng cố

---

### 4.12 Hoàn thành bài học tự động
**Cơ chế:** Backend tự động đánh dấu lesson completed khi học viên pass quiz

**Điều kiện hoàn thành (cả 3 cần đạt):**
1. Đã xem hết nội dung bài học (100%)
2. Đạt ≥70% điểm quiz
3. Trả lời đúng tất cả câu điểm liệt

**Luồng hoạt động:**
- Học viên submit quiz qua `POST /api/v1/quizzes/{quiz_id}/attempt`
- Backend chấm điểm và kiểm tra điều kiện
- Nếu pass: tự động cập nhật lesson status = completed
- Response của quiz attempt sẽ bao gồm:

```json
{
  "attempt_id": "string (UUID)",
  "quiz_id": "string (UUID)",
  "score": "number (0-100)",
  "status": "string (Pass|Fail)",
  "lesson_completed": "boolean (true nếu lesson được đánh dấu completed)",
  "next_lesson_unlocked": "boolean",
  "module_progress": "number (%)",
  "course_progress": "number (%)",
  "submitted_at": "datetime",
  "message": "string"
}
```

**Ghi chú:** Không có endpoint riêng để complete lesson. Việc complete lesson được trigger tự động khi pass quiz.

---

### 4.13 Tạo quiz tùy chỉnh cho bài học
**Endpoint:** `POST /api/v1/lessons/{lesson_id}/quizzes`  
**Quyền:** Instructor (class owner)  
**Router:** `quiz_router.py`  
**Controller:** `handle_create_quiz`

**Mô tả:** Giảng viên tự tạo bài quiz riêng cho lesson trong khóa học. Giao diện sử dụng drag-and-drop để thêm câu hỏi. Hỗ trợ các dạng câu hỏi: trắc nghiệm nhiều lựa chọn, điền khuyết, đúng/sai. Có tính năng preview quiz trước khi publish để kiểm tra giao diện và logic câu hỏi.

**Path Parameters:**
- `lesson_id` (UUID): ID của bài học cần tạo quiz

**Request Schema:**
```json
{
  "title": "string (bắt buộc, tiêu đề quiz, tối đa 200 ký tự)",
  "description": "string (tùy chọn, mô tả ngắn gọn về nội dung quiz)",
  "time_limit": "integer (phút làm bài, bắt buộc, min: 1, max: 180)",
  "pass_threshold": "integer (điểm pass tối thiểu %, bắt buộc, min: 0, max: 100, default: 70)",
  "max_attempts": "integer (số lần được làm lại, tùy chọn, null = không giới hạn, min: 1)",
  "deadline": "string (ISO 8601 datetime, thời hạn nộp bài, tùy chọn)",
  "is_draft": "boolean (true = lưu nháp, false = publish ngay, default: false)",
  "questions": [
    {
      "type": "string (multiple_choice|fill_in_blank|true_false)",
      "question_text": "string (nội dung câu hỏi, bắt buộc)",
      "options": ["string array (các lựa chọn - bắt buộc với multiple_choice)"],
      "correct_answer": "string|integer (đáp án đúng, bắt buộc)",
      "explanation": "string (giải thích đáp án, tùy chọn)",
      "points": "integer (điểm số cho câu này, bắt buộc, min: 1)",
      "is_mandatory": "boolean (câu điểm liệt, default: false)",
      "order": "integer (thứ tự hiển thị câu hỏi, bắt buộc)"
    }
  ]
}
```

**Ghi chú Request:**
- `questions`: Tối thiểu 1 câu, tối đa 50 câu
- `type = multiple_choice`: Phải có ít nhất 2 options, tối đa 6 options
- `type = fill_in_blank`: `options` = null, `correct_answer` là văn bản ngắn
- `type = true_false`: `options` = ["Đúng", "Sai"], `correct_answer` là "Đúng" hoặc "Sai"
- `is_mandatory = true`: Câu "điểm liệt" bắt buộc phải trả lời đúng mới pass quiz
- `is_draft = true`: Quiz được lưu nháp, chưa hiển thị cho học viên
- `deadline`: Nếu null, không giới hạn thời hạn nộp

**Response Schema (201 Created):**
```json
{
  "quiz_id": "string (UUID)",
  "lesson_id": "string (UUID)",
  "title": "string (tiêu đề quiz)",
  "description": "string (mô tả quiz)",
  "time_limit": "integer (phút)",
  "pass_threshold": "integer (%)",
  "max_attempts": "integer (số lần làm lại hoặc null)",
  "deadline": "string (ISO 8601 datetime hoặc null)",
  "is_draft": "boolean (trạng thái nháp)",
  "question_count": "integer (tổng số câu hỏi)",
  "total_points": "integer (tổng điểm của quiz)",
  "mandatory_count": "integer (số câu điểm liệt)",
  "created_at": "string (ISO 8601 datetime)",
  "preview_url": "string (URL để preview quiz trước khi publish)",
  "message": "string (Quiz đã được tạo thành công)"
}
```

**Response Schema (400 Bad Request):**
```json
{
  "detail": "string (Lỗi validation: số câu hỏi không hợp lệ, options thiếu, v.v.)"
}
```

**Response Schema (403 Forbidden):**
```json
{
  "detail": "string (Bạn không có quyền tạo quiz cho lesson này)"
}
```

**Response Schema (404 Not Found):**
```json
{
  "detail": "string (Không tìm thấy lesson với ID này)"
}
```

**Ghi chú:**
- Quiz thuộc Lesson cụ thể, endpoint phản ánh đúng quan hệ cha-con
- Giao diện drag-and-drop cho phép sắp xếp câu hỏi theo `order`
- Tính năng preview (`preview_url`) giúp kiểm tra giao diện và logic trước khi publish
- Nếu `is_draft = true`, học viên chưa thể xem/làm quiz này

---

### 4.14 Xem danh sách quiz với bộ lọc
**Endpoint:** `GET /api/v1/quizzes?role=instructor`  
**Quyền:** Instructor  
**Router:** `quiz_router.py`  
**Controller:** `handle_list_quizzes_with_filters`

**Mô tả:** Hiển thị tất cả quiz mà giảng viên có quyền xem với filter mạnh mẽ. Có tính năng search theo tên quiz và sort theo các cột để dễ quản lý.

**Query Parameters:**
- `role` (string): Bắt buộc = "instructor" (quiz tôi đã tạo)
- `course_id` (UUID): Tùy chọn - lọc quiz trong khóa học cụ thể
- `class_id` (UUID): Tùy chọn - lọc quiz trong lớp học cụ thể
- `lesson_id` (UUID): Tùy chọn - lọc quiz của lesson cụ thể
- `status` (string): Tùy chọn - lọc theo trạng thái (active|draft|archived)
- `search` (string): Tùy chọn - tìm kiếm theo tên quiz
- `sort_by` (string): Tùy chọn - sắp xếp (created_at|title|pass_rate|attempts), default: created_at
- `sort_order` (string): Tùy chọn - thứ tự (asc|desc), default: desc
- `skip` (integer): Pagination offset, default: 0
- `limit` (integer): Pagination limit, default: 20, max: 100

**Response Schema (200 OK):**
```json
{
  "data": [
    {
      "quiz_id": "string (UUID)",
      "title": "string (tên quiz)",
      "description": "string (mô tả ngắn)",
      "lesson_id": "string (UUID)",
      "lesson_title": "string (tên bài học)",
      "course_id": "string (UUID)",
      "course_title": "string (tên khóa học)",
      "class_id": "string (UUID hoặc null nếu không thuộc class)",
      "class_name": "string (tên lớp học hoặc null)",
      "status": "string (active|draft|archived)",
      "question_count": "integer (số câu hỏi)",
      "time_limit": "integer (phút)",
      "pass_threshold": "integer (%)",
      "total_students": "integer (tổng số học viên có quyền làm)",
      "completed_count": "integer (số học viên đã làm)",
      "pass_count": "integer (số học viên đã pass)",
      "pass_rate": "float (tỷ lệ pass %, 0-100)",
      "average_score": "float (điểm trung bình, 0-100)",
      "created_at": "string (ISO 8601 datetime)",
      "updated_at": "string (ISO 8601 datetime)"
    }
  ],
  "total": "integer (tổng số quiz)",
  "skip": "integer (offset hiện tại)",
  "limit": "integer (giới hạn mỗi trang)",
  "has_next": "boolean (còn trang tiếp theo không)"
}
```

**Response Schema (400 Bad Request):**
```json
{
  "detail": "string (Thiếu tham số role=instructor hoặc giá trị không hợp lệ)"
}
```

**Ghi chú:**
- Thông tin hiển thị: tên quiz, lesson/course áp dụng, số câu hỏi, thời gian, số học viên đã làm/tổng số, tỷ lệ pass
- Search hỗ trợ tìm theo tên quiz (case-insensitive)
- Sort theo nhiều tiêu chí: thời gian tạo, tên, tỷ lệ pass, số lượt làm

---

### 4.15 Chỉnh sửa quiz
**Endpoint:** `PUT /api/v1/quizzes/{quiz_id}`  
**Quyền:** Instructor (quiz owner)  
**Router:** `quiz_router.py`  
**Controller:** `handle_update_quiz`

**Mô tả:** Sửa đổi mọi thành phần của quiz đã tạo: thêm/xóa/sửa câu hỏi, thay đổi thời gian và điều kiện, cập nhật hướng dẫn. Nếu đã có học viên làm bài, frontend sẽ hiển thị cảnh báo và đề xuất tạo phiên bản mới thay vì sửa trực tiếp quiz cũ để tránh ảnh hưởng đến kết quả đã có.

**Path Parameters:**
- `quiz_id` (UUID): ID của quiz cần chỉnh sửa

**Request Schema:**
```json
{
  "title": "string (tiêu đề quiz, tùy chọn)",
  "description": "string (mô tả, tùy chọn)",
  "time_limit": "integer (phút làm bài, tùy chọn)",
  "pass_threshold": "integer (điểm pass %, tùy chọn)",
  "max_attempts": "integer (số lần làm lại, tùy chọn)",
  "deadline": "string (ISO 8601 datetime, tùy chọn)",
  "is_draft": "boolean (trạng thái nháp, tùy chọn)",
  "questions": [
    {
      "question_id": "string (UUID, null nếu câu mới)",
      "type": "string (multiple_choice|fill_in_blank|true_false)",
      "question_text": "string (nội dung câu hỏi)",
      "options": ["string array (các lựa chọn)"],
      "correct_answer": "string|integer (đáp án đúng)",
      "explanation": "string (giải thích đáp án)",
      "points": "integer (điểm số)",
      "is_mandatory": "boolean (câu điểm liệt)",
      "order": "integer (thứ tự hiển thị)",
      "action": "string (add|update|delete) - hành động với câu hỏi này"
    }
  ]
}
```

**Ghi chú Request:**
- Chỉ cần gửi các field muốn cập nhật (partial update)
- `questions.question_id = null` + `action = add`: Thêm câu hỏi mới
- `questions.question_id != null` + `action = update`: Sửa câu hỏi hiện có
- `questions.question_id != null` + `action = delete`: Xóa câu hỏi
- Nếu quiz đã có học viên làm bài, response sẽ chứa cảnh báo

**Response Schema (200 OK):**
```json
{
  "quiz_id": "string (UUID)",
  "title": "string (tiêu đề mới)",
  "question_count": "integer (số câu sau khi cập nhật)",
  "total_points": "integer (tổng điểm mới)",
  "has_attempts": "boolean (đã có học viên làm bài chưa)",
  "attempts_count": "integer (số lượt làm bài hiện có)",
  "warning": "string (cảnh báo nếu có attempts - đề xuất tạo version mới)",
  "updated_at": "string (ISO 8601 datetime)",
  "message": "string (Quiz đã được cập nhật thành công)"
}
```

**Response Schema (400 Bad Request):**
```json
{
  "detail": "string (Lỗi validation hoặc không thể cập nhật)"
}
```

**Response Schema (403 Forbidden):**
```json
{
  "detail": "string (Bạn không phải là người tạo quiz này)"
}
```

**Response Schema (404 Not Found):**
```json
{
  "detail": "string (Không tìm thấy quiz với ID này)"
}
```

**Ghi chú:**
- Frontend hiển thị cảnh báo nếu `has_attempts = true`
- Đề xuất tạo phiên bản mới thay vì sửa trực tiếp để giữ lịch sử kết quả

---

### 4.16 Xóa quiz
**Endpoint:** `DELETE /api/v1/quizzes/{quiz_id}`  
**Quyền:** Instructor (quiz owner)  
**Router:** `quiz_router.py`  
**Controller:** `handle_delete_quiz`

**Mô tả:** Xóa vĩnh viễn quiz khỏi hệ thống. Chỉ được phép xóa khi chưa có học viên nào làm bài. Frontend hiển thị số lượng học viên đã làm bài và xác nhận có chắc chắn muốn xóa. Dữ liệu không thể khôi phục sau khi xóa.

**Path Parameters:**
- `quiz_id` (UUID): ID của quiz cần xóa

**Response Schema (200 OK):**
```json
{
  "quiz_id": "string (UUID đã xóa)",
  "message": "string (Quiz đã được xóa vĩnh viễn)"
}
```

**Response Schema (400 Bad Request):**
```json
{
  "detail": "string (Không thể xóa quiz đã có học viên làm bài)",
  "attempts_count": "integer (số lượt làm bài hiện có)",
  "students_count": "integer (số học viên đã làm)"
}
```

**Response Schema (403 Forbidden):**
```json
{
  "detail": "string (Bạn không phải là người tạo quiz này)"
}
```

**Response Schema (404 Not Found):**
```json
{
  "detail": "string (Không tìm thấy quiz với ID này)"
}
```

**Ghi chú:**
- Điều kiện xóa: Chưa có học viên nào làm bài (`attempts_count = 0`)
- Frontend phải xác nhận 2 lần trước khi xóa
- Dữ liệu quiz và câu hỏi sẽ bị xóa vĩnh viễn

---

### 4.17 Phân tích kết quả quiz của cả lớp
**Endpoint:** `GET /api/v1/quizzes/{quiz_id}/class-results`  
**Quyền:** Instructor (class owner)  
**Router:** `quiz_router.py`  
**Controller:** `handle_get_class_quiz_results`

**Mô tả:** Dashboard chi tiết phân tích kết quả quiz của toàn lớp học. Hiển thị histogram phân bổ điểm để xem phân bố điểm của học viên, bảng ranking học viên xếp hạng theo điểm. Giúp giảng viên đánh giá độ khó của quiz và hiệu quả học tập của lớp.

**Path Parameters:**
- `quiz_id` (UUID): ID của quiz cần xem kết quả

**Query Parameters:**
- `class_id` (UUID): Tùy chọn - lọc theo lớp cụ thể nếu quiz dùng cho nhiều lớp

**Response Schema (200 OK):**
```json
{
  "quiz_id": "string (UUID)",
  "quiz_title": "string (tên quiz)",
  "class_id": "string (UUID)",
  "class_name": "string (tên lớp)",
  "statistics": {
    "total_students": "integer (tổng số học viên)",
    "completed_count": "integer (số học viên đã làm)",
    "completion_rate": "float (tỷ lệ hoàn thành %, 0-100)",
    "pass_count": "integer (số học viên pass)",
    "fail_count": "integer (số học viên fail)",
    "pass_rate": "float (tỷ lệ pass %, 0-100)",
    "average_score": "float (điểm trung bình, 0-100)",
    "median_score": "float (điểm trung vị, 0-100)",
    "highest_score": "float (điểm cao nhất, 0-100)",
    "lowest_score": "float (điểm thấp nhất, 0-100)",
    "average_time": "integer (thời gian làm trung bình - phút)"
  },
  "score_distribution": [
    {
      "range": "string (khoảng điểm: 0-10, 11-20, ...)",
      "count": "integer (số học viên trong khoảng)",
      "percentage": "float (%, 0-100)"
    }
  ],
  "student_ranking": [
    {
      "rank": "integer (thứ hạng)",
      "user_id": "string (UUID)",
      "full_name": "string (tên học viên)",
      "avatar": "string (URL avatar hoặc null)",
      "score": "float (điểm số, 0-100)",
      "time_spent": "integer (thời gian làm - phút)",
      "attempt_count": "integer (số lần làm)",
      "status": "string (pass|fail)",
      "completed_at": "string (ISO 8601 datetime)"
    }
  ],
  "difficult_questions": [
    {
      "question_id": "string (UUID)",
      "question_text": "string (nội dung câu hỏi)",
      "correct_rate": "float (tỷ lệ trả lời đúng %, 0-100)",
      "total_answers": "integer (tổng số câu trả lời)",
      "is_mandatory": "boolean (câu điểm liệt)"
    }
  ]
}
```

**Response Schema (403 Forbidden):**
```json
{
  "detail": "string (Bạn không phải là giảng viên của lớp này)"
}
```

**Response Schema (404 Not Found):**
```json
{
  "detail": "string (Không tìm thấy quiz hoặc lớp học với ID này)"
}
```

**Ghi chú:**
- **Histogram phân bổ điểm:** `score_distribution` chia thành 10 khoảng (0-10, 11-20, ..., 91-100)
- **Bảng ranking:** Sắp xếp học viên theo điểm từ cao xuống thấp
- **Câu hỏi khó nhất:** Top 5 câu có tỷ lệ sai cao nhất
- Giúp giảng viên đánh giá độ khó quiz và điều chỉnh nội dung giảng dạy

---

### 4.18 Xem tiến độ học tập đa cấp
**Endpoint:** `GET /api/v1/progress/course/{course_id}`  
**Quyền:** Student (enrolled)

**Response Schema (200 OK):**
```json
{
  "course_id": "string (UUID)",
  "course_title": "string",
  "overall_progress": "number (0-100, %)",
  "modules": [
    {
      "id": "string (UUID)",
      "title": "string",
      "progress": "number (%)",
      "lessons": [
        {
          "id": "string (UUID)",
          "title": "string",
          "status": "string (completed|in-progress|not-started)",
          "completion_date": "datetime (có thể null)"
        }
      ]
    }
  ],
  "estimated_hours_remaining": "number",
  "study_streak_days": "number (số ngày học liên tiếp)",
  "avg_quiz_score": "number (0-100)",
  "total_hours_spent": "number"
}
```

---

## 5. KHÓA HỌC CÁ NHÂN (2.5)

### 5.1 Tạo khóa học từ AI Prompt
**Endpoint:** `POST /api/v1/courses/from-prompt`  
**Quyền:** Student  
**Router:** `personal_courses_router.py`  
**Controller:** `handle_create_course_from_prompt`

**Mô tả:** Học viên chỉ cần nhập mô tả bằng ngôn ngữ tự nhiên về chủ đề và mục tiêu học tập, AI sẽ tự động tạo khóa học hoàn chỉnh. Ví dụ prompt: "Tôi muốn học lập trình Python cơ bản cho người mới bắt đầu, tập trung vào xử lý dữ liệu". AI sẽ sinh ra: (1) Danh sách modules được sắp xếp theo thứ tự logic từ cơ bản đến nâng cao, (2) Các lessons trong mỗi module với nội dung cụ thể, (3) Learning outcomes cho từng module, (4) Nội dung cơ bản cho mỗi lesson. Cơ chế: AI tạo ngay một bản draft trong database với status="draft". Học viên có thể chỉnh sửa bản draft này và publish khi hài lòng. Nếu F5 hoặc đóng trình duyệt, bản draft vẫn được lưu.

**Request Schema:**
```json
{
  "prompt": "string (bắt buộc, mô tả bằng ngôn ngữ tự nhiên, tối thiểu 20 ký tự)"
}
```

**Response Schema (201 Created):**
```json
{
  "course_id": "string (UUID khóa học được tạo)",
  "title": "string (tiêu đề do AI sinh ra)",
  "description": "string (mô tả do AI sinh ra)",
  "category": "string (danh mục do AI xác định)",
  "level": "string (Beginner|Intermediate|Advanced, do AI xác định)",
  "status": "string (draft)",
  "modules": [
    {
      "id": "string (UUID module)",
      "title": "string (tiêu đề module do AI sinh)",
      "description": "string (mô tả module)",
      "order": "number (thứ tự module từ 1, 2, 3...)",
      "difficulty": "string (Basic|Intermediate|Advanced)",
      "learning_outcomes": [
        "string (mục tiêu học tập của module)"
      ],
      "lessons": [
        {
          "id": "string (UUID lesson)",
          "title": "string (tiêu đề lesson do AI sinh)",
          "order": "number (thứ tự lesson trong module)",
          "content_outline": "string (outline nội dung chính do AI sinh)"
        }
      ]
    }
  ],
  "created_at": "datetime",
  "message": "string (Khóa học draft đã được tạo, bạn có thể chỉnh sửa trước khi xuất bản)"
}
```

**Error Response (400 Bad Request):**
```json
{
  "detail": "string (Prompt too short - minimum 20 characters | Unable to generate course from prompt | AI service unavailable)"
}
```

**Ghi chú:**
- AI tạo ngay một bản draft trong database (status = "draft")
- Học viên có thể chỉnh sửa bản draft này qua endpoint PUT /api/v1/courses/personal/{course_id}
- Khi hài lòng, học viên có thể publish khóa học bằng cách update status = "published"
- Nếu học viên F5 hoặc đóng trình duyệt, bản draft vẫn được lưu

---

### 5.2 Tạo khóa học thủ công
**Endpoint:** `POST /api/v1/courses/personal`  
**Quyền:** Student  
**Router:** `personal_courses_router.py`  
**Controller:** `handle_create_personal_course`

**Mô tả:** Tạo khóa học từ đầu với thông tin cơ bản do học viên tự nhập và tổ chức nội dung. Bước 1: Nhập thông tin cơ bản: tên khóa học, mô tả ngắn, danh mục (Programming, Math...), cấp độ. Bước 2: Hệ thống tạo khóa học trống với trạng thái "draft". Bước 3: Trả về course_id và chuyển đến trang quản lý để học viên tự thêm modules, lessons, và nội dung. Lợi ích: Kiểm soát hoàn toàn nội dung và cấu trúc khóa học theo ý muốn. Phù hợp cho người có kinh nghiệm hoặc muốn tạo khóa học độc đáo.

**Request Schema:**
```json
{
  "title": "string (bắt buộc, tối thiểu 5 ký tự, tối đa 200 ký tự)",
  "description": "string (bắt buộc, tối thiểu 20 ký tự)",
  "category": "string (bắt buộc: Programming|Math|Business|Languages|Other)",
  "level": "string (bắt buộc: Beginner|Intermediate|Advanced)",
  "thumbnail_url": "string (tùy chọn, URL ảnh đại diện)"
}
```

**Response Schema (201 Created):**
```json
{
  "id": "string (UUID khóa học)",
  "title": "string",
  "description": "string",
  "category": "string",
  "level": "string",
  "status": "string (draft)",
  "owner_id": "string (UUID học viên tạo)",
  "created_at": "datetime",
  "message": "string (Khóa học trống được tạo, hãy thêm modules và lessons)"
}
```

**Error Response (400 Bad Request):**
```json
{
  "detail": "string (Title too short | Description too short | Invalid category | Invalid level)"
}
```

---

### 5.3 Xem danh sách khóa học cá nhân
**Endpoint:** `GET /api/v1/courses/my-personal`  
**Quyền:** Student  
**Router:** `personal_courses_router.py`  
**Controller:** `handle_list_my_personal_courses`

**Mô tả:** Hiển thị tất cả khóa học do chính học viên tạo (từ AI hoặc thủ công). Phạm vi hiển thị: Khóa học cá nhân chỉ hiển thị cho người tạo và Admin. Không công khai, không chia sẻ được. Thông tin hiển thị: (1) Tên khóa học và hình ảnh, (2) Trạng thái: "draft" (nháp), "published" (đã hoàn thành), "archived" (lưu trữ), (3) Thống kê: số modules/lessons đã tạo, (4) Ngày tạo. Tính năng: (a) Filter theo trạng thái (draft/published/archived), (b) Tìm kiếm theo tên, (c) Mỗi item có các action: Xem chi tiết, Chỉnh sửa, Xóa.

**Query Parameters:**
```
status: string (tùy chọn: draft|published|archived)
search: string (tùy chọn, tìm kiếm theo tên khóa học)
skip: number (mặc định: 0)
limit: number (mặc định: 10, tối đa: 50)
sort_by: string (created_at|updated_at|title, mặc định: created_at)
sort_order: string (asc|desc, mặc định: desc)
```

**Response Schema (200 OK):**
```json
{
  "courses": [
    {
      "id": "string (UUID)",
      "title": "string",
      "thumbnail_url": "string (có thể null)",
      "status": "string (draft|published|archived)",
      "category": "string",
      "level": "string",
      "module_count": "number (số modules đã tạo)",
      "lesson_count": "number (số lessons đã tạo)",
      "created_at": "datetime",
      "updated_at": "datetime"
    }
  ],
  "total": "number (tổng số khóa học)",
  "skip": "number",
  "limit": "number",
  "summary": {
    "draft_count": "number",
    "published_count": "number",
    "archived_count": "number"
  }
}
```

---

### 5.4 Chỉnh sửa khóa học cá nhân
**Endpoint:** `PUT /api/v1/courses/personal/{course_id}`  
**Quyền:** Student (owner)  
**Router:** `personal_courses_router.py`  
**Controller:** `handle_update_personal_course`

**Mô tả:** Cho phép sửa đổi mọi thành phần của khóa học cá nhân: (1) Thay đổi tiêu đề, mô tả, hình ảnh khóa học, (2) Thêm/xóa/sắp xếp lại modules, (3) Thêm/xóa/chỉnh sửa nội dung lessons, (4) Cập nhật learning outcomes, (5) Thêm/xóa tài nguyên đính kèm. Giao diện: Cung cấp drag-and-drop để sắp xếp modules/lessons dễ dàng. Auto-save: Mọi thay đổi được tự động lưu sau 2-3 giây hoặc khi người dùng rời khỏi trường đang chỉnh sửa để tránh mất dữ liệu.

**Request Schema:**
```json
{
  "title": "string (tùy chọn)",
  "description": "string (tùy chọn)",
  "thumbnail_url": "string (tùy chọn)",
  "category": "string (tùy chọn)",
  "level": "string (tùy chọn)",
  "status": "string (tùy chọn: draft|published|archived)",
  "modules": [
    {
      "id": "string (UUID module, nếu cập nhật module cũ. Null nếu thêm mới)",
      "title": "string (bắt buộc nếu có module)",
      "description": "string (bắt buộc nếu có module)",
      "order": "number (thứ tự module)",
      "difficulty": "string (Basic|Intermediate|Advanced)",
      "lessons": [
        {
          "id": "string (UUID lesson, nếu cập nhật. Null nếu thêm mới)",
          "title": "string",
          "content": "string (HTML hoặc markdown)",
          "order": "number"
        }
      ]
    }
  ]
}
```

**Response Schema (200 OK):**
```json
{
  "id": "string (UUID)",
  "title": "string",
  "status": "string",
  "updated_at": "datetime",
  "message": "string (Khóa học đã được cập nhật)"
}
```

**Error Response (403 Forbidden):**
```json
{
  "detail": "string (Not the owner of this course | Cannot edit published course)"
}
```

**Error Response (404 Not Found):**
```json
{
  "detail": "string (Course not found)"
}
```

**Ghi chú:**
- Hỗ trợ drag-and-drop sắp xếp modules/lessons
- Auto-save sau 2-3 giây

---

### 5.5 Xóa khóa học cá nhân
**Endpoint:** `DELETE /api/v1/courses/personal/{course_id}`  
**Quyền:** Student (owner)  
**Router:** `personal_courses_router.py`  
**Controller:** `handle_delete_personal_course`

**Mô tả:** Xóa vĩnh viễn khóa học đã tạo. Điều kiện: Chỉ cho phép xóa khóa học do chính học viên đó tạo (owner). Cảnh báo: Hiển thị dialog xác nhận rõ ràng về việc: (1) Xóa không thể khôi phục, (2) Tất cả nội dung, modules, lessons sẽ bị xóa. Kiểm tra: Backend kiểm tra ownership (quyền sở hữu) trước khi cho phép xóa.

**Response Schema (200 OK):**
```json
{
  "message": "string (Khóa học đã được xóa vĩnh viễn)",
  "deleted_course_id": "string (UUID)",
  "deleted_at": "datetime"
}
```

**Error Response (403 Forbidden):**
```json
{
  "detail": "string (Not the owner of this course | Cannot delete published course with enrollments)"
}
```

**Error Response (404 Not Found):**
```json
{
  "detail": "string (Course not found)"
}
```

---

## 6. CHATBOT HỖ TRỢ AI (2.6)

### 6.1 Chat hỏi đáp về khóa học
**Endpoint:** `POST /api/v1/chat/course/{course_id}`  
**Quyền:** Student (enrolled)  
**Router:** `chat_router.py`  
**Controller:** `handle_send_chat_message`

**Mô tả:** Học viên có thể hỏi bất cứ điều gì liên quan đến nội dung khóa học đang học, AI sẽ trả lời dựa trên context (ngữ cảnh) của khóa học đó. AI có context của: (1) Tên và mô tả khóa học, (2) Nội dung tất cả modules và lessons, (3) Learning outcomes, (4) Tài nguyên đính kèm.

**Path Parameters:**
```
course_id: string (bắt buộc, UUID của khóa học)
```

**Request Schema:**
```json
{
  "question": "string (bắt buộc, câu hỏi của học viên)",
  "conversation_id": "string (tùy chọn, UUID conversation hiện tại để duy trì context)",
  "context_type": "string (tùy chọn: lesson|module|general, mặc định: general)"
}
```

**Response Schema (200 OK):**
```json
{
  "conversation_id": "string (UUID, tạo mới nếu chưa có)",
  "message_id": "string (UUID của message này)",
  "question": "string (câu hỏi đã gửi)",
  "answer": "string (câu trả lời từ AI, markdown format)",
  "sources": [
    {
      "type": "string (lesson|module|resource)",
      "id": "string (UUID)",
      "title": "string (tiêu đề nguồn)",
      "excerpt": "string (đoạn trích liên quan)"
    }
  ],
  "related_lessons": [
    {
      "lesson_id": "string (UUID)",
      "title": "string",
      "url": "string (link đến lesson)"
    }
  ],
  "timestamp": "datetime",
  "tokens_used": "number (số tokens AI đã dùng)"
}
```

**Error Response (403 Forbidden):**
```json
{
  "detail": "string (Not enrolled in this course)"
}
```

---

### 6.2 Xem lịch sử hội thoại
**Endpoint:** `GET /api/v1/chat/history`  
**Quyền:** Student  
**Router:** `chat_router.py`  
**Controller:** `handle_get_chat_history`

**Mô tả:** Hiển thị danh sách tất cả các cuộc hội thoại (conversations) đã có với AI. Nhóm theo: (1) Ngày (hôm nay, hôm qua, tuần này...), (2) Chủ đề/khóa học đã chat. Học viên có thể click vào để xem lại toàn bộ nội dung conversation và tiếp tục hỏi đáp từ đó (giữ nguyên context).

**Query Parameters:**
```
course_id: string (tùy chọn, UUID - lọc theo khóa học)
skip: number (pagination, mặc định: 0)
limit: number (pagination, mặc định: 20, tối đa: 50)
```

**Response Schema (200 OK):**
```json
{
  "conversations": [
    {
      "conversation_id": "string (UUID)",
      "course_id": "string (UUID)",
      "course_title": "string",
      "topic_summary": "string (chủ đề chính được AI tóm tắt)",
      "message_count": "number (số messages trong conversation)",
      "last_message_preview": "string (preview message cuối, 100 ký tự)",
      "created_at": "datetime (thời gian bắt đầu)",
      "last_updated": "datetime (message cuối cùng)"
    }
  ],
  "grouped_by_date": {
    "today": ["array of conversation_ids"],
    "yesterday": ["array of conversation_ids"],
    "this_week": ["array of conversation_ids"],
    "older": ["array of conversation_ids"]
  },
  "total": "number",
  "skip": "number",
  "limit": "number"
}
```

---

### 6.3 Xem chi tiết conversation
**Endpoint:** `GET /api/v1/chat/conversations/{conversation_id}`  
**Quyền:** Student (owner)  
**Router:** `chat_router.py`  
**Controller:** `handle_get_conversation_detail`

**Mô tả:** Xem toàn bộ nội dung của một cuộc hội thoại cụ thể với AI. Hiển thị: (1) Tất cả messages trong conversation theo thứ tự thời gian, (2) Thông tin khóa học liên quan (nếu có), (3) Thời gian bắt đầu cuộc hội thoại. Cần thiết: Khi user click vào một conversation trong lịch sử để xem lại hoặc tiếp tục hỏi đáp.

**Path Parameters:**
```
conversation_id: string (bắt buộc, UUID)
```

**Response Schema (200 OK):**
```json
{
  "conversation_id": "string (UUID)",
  "course": {
    "course_id": "string (UUID)",
    "title": "string",
    "thumbnail_url": "string (có thể null)"
  },
  "created_at": "datetime (thời gian bắt đầu conversation)",
  "last_updated": "datetime",
  "message_count": "number",
  "messages": [
    {
      "message_id": "string (UUID)",
      "role": "string (user|assistant)",
      "content": "string (nội dung message, markdown format)",
      "timestamp": "datetime",
      "sources": [
        {
          "type": "string (lesson|module|resource)",
          "title": "string",
          "url": "string"
        }
      ]
    }
  ]
}
```

**Error Response (403 Forbidden):**
```json
{
  "detail": "string (Not the owner of this conversation)"
}
```

**Error Response (404 Not Found):**
```json
{
  "detail": "string (Conversation not found)"
}
```

---

### 6.4 Xóa tất cả lịch sử chat
**Endpoint:** `DELETE /api/v1/chat/conversations`  
**Quyền:** Student  
**Router:** `chat_router.py`  
**Controller:** `handle_delete_all_conversations`

**Mô tả:** Xóa toàn bộ lịch sử hội thoại với AI một lần. Cảnh báo: Dữ liệu đã xóa không thể khôi phục được. Response: Trả về số lượng conversations đã bị xóa.

**Request Schema:** (empty body)

**Response Schema (200 OK):**
```json
{
  "deleted_count": "number (số conversations đã xóa)",
  "message": "string (Đã xóa tất cả lịch sử chat)",
  "deleted_at": "datetime"
}
```

**Ghi chú:**
- Frontend hiển thị modal xác nhận trước khi gọi API
- Dữ liệu đã xóa không thể khôi phục

---

### 6.5 Xóa lịch sử chat từng conversation
**Endpoint:** `DELETE /api/v1/chat/history/{conversation_id}`  
**Quyền:** Student (owner)  
**Router:** `chat_router.py`  
**Controller:** `handle_delete_conversation`

**Mô tả:** Cho phép xóa lịch sử hội thoại để giữ gọn gàng hoặc bảo mật thông tin. Xóa từng conversation: Click icon xóa trên mỗi conversation riêng lẻ. Cảnh báo: Dữ liệu đã xóa không thể khôi phục được.

**Path Parameters:**
```
conversation_id: string (bắt buộc, UUID)
```

**Response Schema (200 OK):**
```json
{
  "conversation_id": "string (UUID đã xóa)",
  "message": "string (Conversation đã được xóa)",
  "deleted_at": "datetime"
}
```

**Error Response (403 Forbidden):**
```json
{
  "detail": "string (Not the owner of this conversation)"
}
```

**Error Response (404 Not Found):**
```json
{
  "detail": "string (Conversation not found)"
}
```

**Ghi chú:**
- Có thể xóa hàng loạt bằng cách gọi API nhiều lần với các conversation_id khác nhau
- Frontend hiển thị checkbox để chọn nhiều conversations và xóa cùng lúc

---

## 7. DASHBOARD & PHÂN TÍCH HỌC VIÊN (2.7)

### 7.1 Dashboard tổng quan học viên
**Endpoint:** `GET /api/v1/dashboard/student`  
**Quyền:** Student  
**Router:** `dashboard_router.py`  
**Controller:** `handle_get_student_dashboard`

**Mô tả:** Trang chủ (home) hiển thị thông tin quan trọng nhất để học viên nắm bắt nhanh tình hình học tập. Các widget hiển thị: (1) Khóa học đang học: danh sách 3-5 khóa đang học gần đây nhất với progress bar (%) cho mỗi khóa, (2) Quiz cần làm: các bài quiz đến hạn hoặc chưa hoàn thành, (3) Số lessons đã hoàn thành và tổng số lessons, (4) Điểm trung bình quiz (trên thang 100). Giao diện: Layout responsive với các widget có thể tùy chỉnh vị trí (drag-and-drop) theo sở thích.

**Response Schema (200 OK):**
```json
{
  "user_id": "string (UUID)",
  "full_name": "string",
  "overview": {
    "total_courses_enrolled": "number",
    "active_courses": "number (đang học)",
    "completed_courses": "number",
    "total_lessons_completed": "number",
    "total_study_hours": "number",
    "current_streak_days": "number (số ngày học liên tiếp)"
  },
  "recent_courses": [
    {
      "course_id": "string (UUID)",
      "title": "string",
      "thumbnail_url": "string (có thể null)",
      "progress_percent": "number (0-100)",
      "last_accessed": "datetime",
      "next_lesson": {
        "lesson_id": "string (UUID)",
        "title": "string"
      }
    }
  ],
  "pending_quizzes": [
    {
      "quiz_id": "string (UUID)",
      "title": "string",
      "course_title": "string",
      "lesson_title": "string",
      "due_date": "datetime (có thể null)",
      "status": "string (not_started|failed - cần làm lại)"
    }
  ],
  "performance_summary": {
    "average_quiz_score": "number (0-100, điểm trung bình tất cả quiz)",
    "quiz_pass_rate": "number (0-100, tỷ lệ pass %)",
    "lessons_this_week": "number (số lessons hoàn thành tuần này)"
  },
  "recommendations": [
    {
      "course_id": "string (UUID)",
      "title": "string",
      "reason": "string (lý do gợi ý ngắn gọn)"
    }
  ]
}
```

### 7.2 Thống kê học tập cá nhân
**Endpoint:** `GET /api/v1/analytics/learning-stats`  
**Quyền:** Student  
**Router:** `analytics_router.py`  
**Controller:** `handle_get_learning_stats`

**Mô tả:** Thống kê tổng quan hoạt động học tập của học viên. Hệ thống chỉ đếm quiz attempts từ các courses đang active (không tính quiz từ courses bị cancelled) để đảm bảo thống kê chính xác.

**Response Schema (200 OK):**
```json
{
  "user_id": "string (UUID)",
  "summary": {
    "total_courses_enrolled": "number",
    "completed_courses": "number",
    "total_study_hours": "number",
    "current_streak_days": "number",
    "longest_streak_days": "number"
  },
  "this_week": {
    "study_hours": "number",
    "lessons_completed": "number",
    "quiz_attempts": "number",
    "average_score": "number (0-100)"
  },
  "skill_progress": [
    {
      "skill_tag": "string",
      "level": "string (Beginner|Intermediate|Advanced)",
      "progress": "number (0-100%)"
    }
  ]
}
```

---

### 7.3 Biểu đồ tiến độ học tập
**Endpoint:** `GET /api/v1/analytics/progress-chart`  
**Quyền:** Student  
**Router:** `analytics_router.py`  
**Controller:** `handle_get_progress_chart`

**Mô tả:** Dữ liệu vẽ biểu đồ tiến độ học tập theo thời gian. Hệ thống parse `lessons_progress` array trong Progress document để đếm lessons completed theo `completion_date` (incremental data, không dùng cumulative count). Đảm bảo chart hiển thị chính xác số lessons hoàn thành trong từng time period.

**FIXED (Dec 07, 2025):** Progress document sử dụng validated LessonProgressItem schema với các fields: lesson_id (UUID), lesson_title (string), status (enum: not-started|in-progress|completed), completion_date (datetime nullable), time_spent_minutes (number), video_progress_seconds (number nullable).

**Query Parameters:**
```
period: string (7days|30days|90days|1year, mặc định: 30days)
type: string (hours|lessons|quizzes, mặc định: hours)
```

**Response Schema (200 OK):**
```json
{
  "period": "string",
  "type": "string", 
  "data_points": [
    {
      "date": "date (YYYY-MM-DD)",
      "value": "number",
      "label": "string (optional description)"
    }
  ],
  "summary": {
    "total_in_period": "number",
    "average_per_day": "number",
    "best_day": {
      "date": "date",
      "value": "number"
    }
  }
}
```

---

### 7.4 Gợi ý khóa học
**Endpoint:** `GET /api/v1/recommendations`  
**Quyền:** Student  
**Router:** `recommendation_router.py`  
**Controller:** `handle_get_recommendations`

**Mô tả:** AI gợi ý khóa học phù hợp dựa trên lịch sử học tập và skill gaps.

**Response Schema (200 OK):**
```json
{
  "user_id": "string (UUID)",
  "recommendations": [
    {
      "course_id": "string (UUID)",
      "title": "string",
      "description": "string",
      "level": "string (Beginner|Intermediate|Advanced)",
      "estimated_hours": "number",
      "match_percentage": "number (0-100%)",
      "reason": "string (lý do gợi ý)",
      "skill_tags": ["string array"],
      "rating": "number (0-5.0)"
    }
  ],
  "based_on": {
    "completed_courses": "number",
    "skill_gaps": ["string array"],
    "learning_preferences": ["string array"]
  }
}
```

---

## 8. QUẢN LÝ GIẢNG VIÊN (3.x)

### 8.1 Tạo lớp học mới
**Endpoint:** `POST /api/v1/classes`  
**Quyền:** Instructor  
**Router:** `classes_router.py`  
**Controller:** `handle_create_class`

**Mô tả:** Giảng viên tạo lớp học mới với thông tin cơ bản và mã mời tự động.

**Request Schema:**
```json
{
  "name": "string (bắt buộc, tên lớp học)",
  "description": "string (tùy chọn, mô tả lớp học)",
  "course_id": "string (UUID khóa học liên kết)",
  "max_students": "number (tối đa học viên, mặc định: 50)",
  "start_date": "datetime (ngày bắt đầu)",
  "end_date": "datetime (ngày kết thúc, tùy chọn)"
}
```

**Response Schema (201 Created):**
```json
{
  "class_id": "string (UUID)",
  "name": "string",
  "invite_code": "string (6-8 ký tự, auto-generated)",
  "course_title": "string",
  "student_count": 0,
  "created_at": "datetime",
  "message": "Lớp học đã được tạo thành công"
}
```

---

### 8.2 Lấy danh sách lớp học của giảng viên
**Endpoint:** `GET /api/v1/classes/my-classes`  
**Quyền:** Instructor  
**Router:** `classes_router.py`  
**Controller:** `handle_list_my_classes`

**Mô tả:** Hiển thị tất cả lớp học do giảng viên tạo và quản lý.

**Query Parameters:**
```
status: string (active|completed|draft, tùy chọn)
skip: number (pagination)
limit: number (pagination)
```

**Response Schema (200 OK):**
```json
{
  "data": [
    {
      "class_id": "string (UUID)",
      "name": "string",
      "course_title": "string", 
      "student_count": "number",
      "invite_code": "string",
      "status": "string (active|completed)",
      "start_date": "datetime",
      "created_at": "datetime"
    }
  ],
  "total": "number",
  "skip": "number",
  "limit": "number"
}
```

---

### 8.3 Xem chi tiết lớp học
**Endpoint:** `GET /api/v1/classes/{class_id}`  
**Quyền:** Instructor (class owner)  
**Router:** `classes_router.py`  
**Controller:** `handle_get_class_detail`

**Mô tả:** Thông tin chi tiết lớp học bao gồm danh sách học viên và tiến độ.

**Response Schema (200 OK):**
```json
{
  "class_id": "string (UUID)",
  "name": "string",
  "description": "string",
  "course": {
    "id": "string (UUID)",
    "title": "string",
    "module_count": "number"
  },
  "invite_code": "string",
  "max_students": "number",
  "student_count": "number",
  "start_date": "datetime",
  "end_date": "datetime",
  "status": "string (active|completed)",
  "recent_students": [
    {
      "student_id": "string (UUID)",
      "student_name": "string",
      "join_date": "datetime",
      "progress": "number (0-100%)"
    }
  ],
  "class_stats": {
    "average_progress": "number (0-100%)",
    "completed_students": "number",
    "active_students": "number"
  }
}
```

---

### 8.4 Cập nhật thông tin lớp học
**Endpoint:** `PUT /api/v1/classes/{class_id}`  
**Quyền:** Instructor (class owner)  
**Router:** `classes_router.py`  
**Controller:** `handle_update_class`

**Mô tả:** Chỉnh sửa tên, mô tả, số lượng học viên tối đa của lớp học.

**Request Schema:**
```json
{
  "name": "string (tùy chọn)",
  "description": "string (tùy chọn)",
  "max_students": "number (tùy chọn)",
  "end_date": "datetime (tùy chọn)"
}
```

**Response Schema (200 OK):**
```json
{
  "class_id": "string (UUID)",
  "message": "Thông tin lớp học đã được cập nhật",
  "updated_at": "datetime"
}
```

---

### 8.5 Xóa lớp học
**Endpoint:** `DELETE /api/v1/classes/{class_id}`  
**Quyền:** Instructor (class owner)  
**Router:** `classes_router.py`  
**Controller:** `handle_delete_class`

**Mô tả:** Xóa lớp học vĩnh viễn (chỉ khi không có học viên hoặc tất cả học viên đã rời khỏi).

**Response Schema (200 OK):**
```json
{
  "message": "Lớp học đã được xóa thành công"
}
```

---

### 8.6 Student tham gia lớp với mã mời
**Endpoint:** `POST /api/v1/classes/join`  
**Quyền:** Student  
**Router:** `classes_router.py`  
**Controller:** `handle_join_class_with_code`

**Mô tả:** Học viên nhập mã mời để tham gia lớp học.

**Request Schema:**
```json
{
  "invite_code": "string (bắt buộc, 6-8 ký tự)"
}
```

**Response Schema (200 OK):**
```json
{
  "class_id": "string (UUID)",
  "class_name": "string",
  "course_title": "string",
  "instructor_name": "string", 
  "join_date": "datetime",
  "message": "Bạn đã tham gia lớp học thành công"
}
```

---

### 8.7 Lấy danh sách học viên trong lớp
**Endpoint:** `GET /api/v1/classes/{class_id}/students`  
**Quyền:** Instructor (class owner)  
**Router:** `classes_router.py`  
**Controller:** `handle_get_class_students`

**Mô tả:** Hiển thị tất cả học viên trong lớp với tiến độ học tập chi tiết.

**Query Parameters:**
```
sort_by: string (name|join_date|progress, mặc định: join_date)
order: string (asc|desc, mặc định: desc)  
skip: number (pagination)
limit: number (pagination)
```

**Response Schema (200 OK):**
```json
{
  "class_id": "string (UUID)",
  "class_name": "string",
  "data": [
    {
      "student_id": "string (UUID)",
      "student_name": "string",
      "email": "string",
      "join_date": "datetime",
      "progress": "number (0-100%)",
      "completed_modules": "number",
      "total_modules": "number",
      "last_activity": "datetime",
      "quiz_average": "number (0-100)"
    }
  ],
  "total": "number",
  "skip": "number", 
  "limit": "number"
}
```

---

### 8.8 Xem chi tiết học viên trong lớp
**Endpoint:** `GET /api/v1/classes/{class_id}/students/{student_id}`  
**Quyền:** Instructor (class owner)  
**Router:** `classes_router.py`  
**Controller:** `handle_get_student_detail`

**Mô tả:** Thông tin chi tiết tiến độ học tập của một học viên cụ thể.

**Response Schema (200 OK):**
```json
{
  "student": {
    "student_id": "string (UUID)",
    "student_name": "string",
    "email": "string",
    "join_date": "datetime"
  },
  "progress": {
    "overall_progress": "number (0-100%)",
    "completed_modules": "number",
    "total_modules": "number",
    "study_streak_days": "number",
    "total_study_time": "number (hours)"
  },
  "module_details": [
    {
      "module_id": "string (UUID)",
      "module_title": "string", 
      "progress": "number (0-100%)",
      "completed_lessons": "number",
      "quiz_scores": [
        {
          "quiz_id": "string (UUID)",
          "quiz_title": "string",
          "score": "number (0-100)",
          "attempt_date": "datetime"
        }
      ]
    }
  ]
}
```

---

### 8.9 Loại học viên khỏi lớp
**Endpoint:** `DELETE /api/v1/classes/{class_id}/students/{student_id}`  
**Quyền:** Instructor (class owner)  
**Router:** `classes_router.py`  
**Controller:** `handle_remove_student`

**Mô tả:** Giảng viên loại học viên khỏi lớp học (học viên mất quyền truy cập).

**Response Schema (200 OK):**
```json
{
  "message": "Học viên đã được loại khỏi lớp học",
  "student_name": "string",
  "removed_at": "datetime"
}
```

---

### 8.10 Xem tiến độ toàn lớp
**Endpoint:** `GET /api/v1/classes/{class_id}/progress`  
**Quyền:** Instructor (class owner)  
**Router:** `classes_router.py`  
**Controller:** `handle_get_class_progress`

**Mô tả:** Tổng quan tiến độ học tập của cả lớp theo module và lesson.

**Response Schema (200 OK):**
```json
{
  "class_id": "string (UUID)",
  "class_name": "string",
  "overall_stats": {
    "total_students": "number",
    "average_progress": "number (0-100%)",
    "completion_rate": "number (0-100%)",
    "average_quiz_score": "number (0-100)"
  },
  "module_progress": [
    {
      "module_id": "string (UUID)",
      "module_title": "string",
      "students_completed": "number",
      "completion_percentage": "number (0-100%)",
      "average_score": "number (0-100)"
    }
  ]
}
```

---

### 8.11 Thống kê lớp học của giảng viên
**Endpoint:** `GET /api/v1/analytics/instructor/classes`  
**Quyền:** Instructor  
**Router:** `analytics_router.py`  
**Controller:** `handle_get_instructor_class_stats`

**Mô tả:** Tổng quan các lớp học và hiệu suất giảng dạy. Hệ thống filter progress chỉ của students trong class cụ thể (dựa trên enrollment user_ids), đảm bảo avg_progress được tính chính xác cho từng lớp.

**Response Schema (200 OK):**
```json
{
  "instructor_id": "string (UUID)",
  "summary": {
    "total_classes": "number",
    "active_classes": "number", 
    "total_students": "number",
    "average_completion_rate": "number (0-100%)"
  },
  "class_performance": [
    {
      "class_id": "string (UUID)",
      "class_name": "string",
      "student_count": "number",
      "average_progress": "number (0-100%)",
      "completion_rate": "number (0-100%)",
      "average_quiz_score": "number (0-100)"
    }
  ]
}
```

---

### 8.12 Biểu đồ tiến độ lớp học
**Endpoint:** `GET /api/v1/analytics/instructor/progress-chart`  
**Quyền:** Instructor  
**Router:** `analytics_router.py`  
**Controller:** `handle_get_instructor_progress_chart`

**Mô tả:** Biểu đồ tiến độ học tập của tất cả lớp học theo thời gian. Hệ thống chỉ đếm progress của students trong classes (filter qua enrollments), parse `lessons_progress` theo `completion_date` (incremental, không cumulative) để hiển thị chính xác số lessons hoàn thành theo từng time period.

**Query Parameters:**
```
class_id: string (UUID, tùy chọn - lọc theo lớp cụ thể)
period: string (7days|30days|90days, mặc định: 30days)
```

**Response Schema (200 OK):**
```json
{
  "period": "string",
  "class_data": [
    {
      "class_id": "string (UUID)",
      "class_name": "string",
      "daily_progress": [
        {
          "date": "date (YYYY-MM-DD)",
          "completed_lessons": "number",
          "quiz_attempts": "number",
          "average_score": "number"
        }
      ]
    }
  ]
}
```

---

### 8.13 Phân tích hiệu suất quiz
**Endpoint:** `GET /api/v1/analytics/instructor/quiz-performance`  
**Quyền:** Instructor  
**Router:** `analytics_router.py`  
**Controller:** `handle_get_instructor_quiz_performance`

**Mô tả:** Phân tích chi tiết hiệu suất các quiz do giảng viên tạo.

**Query Parameters:**
```
class_id: string (UUID, tùy chọn)
quiz_id: string (UUID, tùy chọn)
```

**Response Schema (200 OK):**
```json
{
  "quiz_analytics": [
    {
      "quiz_id": "string (UUID)",
      "quiz_title": "string",
      "class_name": "string",
      "statistics": {
        "total_attempts": "number",
        "pass_rate": "number (0-100%)",
        "average_score": "number (0-100)",
        "average_time": "number (seconds)"
      },
      "question_analysis": [
        {
          "question_id": "string",
          "question_text": "string",
          "correct_rate": "number (0-100%)",
          "common_wrong_answers": ["string array"]
        }
      ]
    }
  ]
}
```

---

## 9. QUẢN LÝ HỆ THỐNG ADMIN (4.x)

### 9.1 Xem danh sách người dùng
**Endpoint:** `GET /api/v1/admin/users`  
**Quyền:** Admin  
**Router:** `admin_router.py`  
**Controller:** `handle_list_users_admin`

**Mô tả:** Admin xem tất cả người dùng trong hệ thống với bộ lọc và tìm kiếm.

**Query Parameters:**
```
role: string (student|instructor|admin, tùy chọn)
status: string (active|inactive|banned, tùy chọn)
search: string (tìm kiếm theo tên, email, tùy chọn)
sort_by: string (created_at|last_login_at|name, mặc định: created_at)
order: string (asc|desc, mặc định: desc)
skip: number (pagination)
limit: number (pagination)
```

**Response Schema (200 OK):**
```json
{
  "data": [
    {
      "user_id": "string (UUID)",
      "full_name": "string",
      "email": "string",
      "role": "string (student|instructor|admin)",
      "status": "string (active|inactive|banned)",
      "created_at": "datetime",
      "last_login_at": "datetime",
      "courses_enrolled": "number (chỉ student)",
      "classes_created": "number (chỉ instructor)"
    }
  ],
  "total": "number",
  "skip": "number",
  "limit": "number",
  "summary": {
    "total_users": "number",
    "active_users": "number",
    "new_users_this_month": "number"
  }
}
```

---

### 9.2 Xem chi tiết người dùng
**Endpoint:** `GET /api/v1/admin/users/{user_id}`  
**Quyền:** Admin  
**Router:** `admin_router.py`  
**Controller:** `handle_get_user_detail_admin`

**Mô tả:** Admin xem thông tin chi tiết của một người dùng cụ thể.

**Response Schema (200 OK):**
```json
{
  "user_id": "string (UUID)",
  "full_name": "string",
  "email": "string",
  "role": "string (student|instructor|admin)",
  "status": "string (active|inactive|banned)",
  "created_at": "datetime",
  "last_login_at": "datetime",
  "profile": {
    "phone": "string (tùy chọn)",
    "bio": "string (tùy chọn)",
    "avatar_url": "string (tùy chọn)"
  },
  "activity_summary": {
    "courses_enrolled": "number",
    "classes_created": "number",
    "total_study_hours": "number",
    "login_streak_days": "number"
  }
}
```

---

### 9.3 Tạo người dùng mới
**Endpoint:** `POST /api/v1/admin/users`  
**Quyền:** Admin  
**Router:** `admin_router.py`  
**Controller:** `handle_create_user_admin`

**Mô tả:** Admin tạo tài khoản mới cho người dùng.

**Request Schema:**
```json
{
  "full_name": "string (bắt buộc)",
  "email": "string (bắt buộc, unique)",
  "password": "string (bắt buộc, tối thiểu 8 ký tự)",
  "role": "string (student|instructor|admin, mặc định: student)",
  "status": "string (active|inactive, mặc định: active)"
}
```

**Response Schema (201 Created):**
```json
{
  "user_id": "string (UUID)",
  "full_name": "string",
  "email": "string",
  "role": "string",
  "status": "string",
  "created_at": "datetime",
  "message": "Tài khoản người dùng đã được tạo thành công"
}
```

---

### 9.4 Cập nhật thông tin người dùng
**Endpoint:** `PUT /api/v1/admin/users/{user_id}`  
**Quyền:** Admin  
**Router:** `admin_router.py`  
**Controller:** `handle_update_user_admin`

**Mô tả:** Admin chỉnh sửa thông tin người dùng.

**Request Schema:**
```json
{
  "full_name": "string (tùy chọn)",
  "email": "string (tùy chọn)",
  "status": "string (active|inactive|banned, tùy chọn)"
}
```

**Response Schema (200 OK):**
```json
{
  "user_id": "string (UUID)",
  "message": "Thông tin người dùng đã được cập nhật",
  "updated_at": "datetime"
}
```

---

### 9.5 Xóa người dùng
**Endpoint:** `DELETE /api/v1/admin/users/{user_id}`  
**Quyền:** Admin  
**Router:** `admin_router.py`  
**Controller:** `handle_delete_user_admin`

**Mô tả:** Admin xóa tài khoản người dùng vĩnh viễn.

**Response Schema (200 OK):**
```json
{
  "message": "Tài khoản người dùng đã được xóa vĩnh viễn"
}
```

---

### 9.6 Thay đổi vai trò người dùng
**Endpoint:** `PUT /api/v1/admin/users/{user_id}/role`  
**Quyền:** Admin  
**Router:** `admin_router.py`  
**Controller:** `handle_change_user_role_admin`

**Mô tả:** Admin thay đổi vai trò của người dùng.

**Request Schema:**
```json
{
  "new_role": "string (student|instructor|admin, bắt buộc)"
}
```

**Response Schema (200 OK):**
```json
{
  "user_id": "string (UUID)",
  "old_role": "string",
  "new_role": "string",
  "message": "Vai trò người dùng đã được thay đổi",
  "updated_at": "datetime"
}
```

---

### 9.7 Đặt lại mật khẩu người dùng
**Endpoint:** `POST /api/v1/admin/users/{user_id}/reset-password`  
**Quyền:** Admin  
**Router:** `admin_router.py`  
**Controller:** `handle_reset_user_password_admin`

**Mô tả:** Admin đặt lại mật khẩu cho người dùng.

**Request Schema:**
```json
{
  "new_password": "string (bắt buộc, tối thiểu 8 ký tự)"
}
```

**Response Schema (200 OK):**
```json
{
  "user_id": "string (UUID)",
  "message": "Mật khẩu đã được đặt lại thành công",
  "updated_at": "datetime"
}
```

---

### 9.8 Xem danh sách khóa học
**Endpoint:** `GET /api/v1/admin/courses`  
**Quyền:** Admin  
**Router:** `admin_router.py`  
**Controller:** `handle_list_courses_admin`

**Mô tả:** Admin xem tất cả khóa học trong hệ thống.

**Query Parameters:**
```
status: string (active|draft|archived, tùy chọn)
creator_id: string (UUID, tùy chọn - lọc theo người tạo)
category: string (danh mục, tùy chọn)
sort_by: string (created_at|enrollment_count|title, mặc định: created_at)
order: string (asc|desc, mặc định: desc)
skip: number (pagination)
limit: number (pagination)
```

**Response Schema (200 OK):**
```json
{
  "data": [
    {
      "course_id": "string (UUID)",
      "title": "string",
      "creator_name": "string",
      "category": "string",
      "level": "string",
      "status": "string (active|draft|archived)",
      "enrollment_count": "number",
      "created_at": "datetime",
      "last_updated": "datetime"
    }
  ],
  "total": "number",
  "skip": "number",
  "limit": "number"
}
```

---

### 9.9 Xem chi tiết khóa học
**Endpoint:** `GET /api/v1/admin/courses/{course_id}`  
**Quyền:** Admin  
**Router:** `admin_router.py`  
**Controller:** `handle_get_course_detail_admin`

**Mô tả:** Admin xem thông tin chi tiết khóa học và thống kê.

**Response Schema (200 OK):**
```json
{
  "course_id": "string (UUID)",
  "title": "string",
  "description": "string",
  "creator": {
    "user_id": "string (UUID)",
    "full_name": "string",
    "email": "string"
  },
  "category": "string",
  "level": "string",
  "status": "string",
  "enrollment_stats": {
    "total_enrollments": "number",
    "active_students": "number",
    "completion_rate": "number (0-100%)"
  },
  "content_stats": {
    "total_modules": "number",
    "total_lessons": "number",
    "total_quizzes": "number"
  },
  "created_at": "datetime",
  "last_updated": "datetime"
}
```

---

### 9.10 Tạo khóa học mới
**Endpoint:** `POST /api/v1/admin/courses`  
**Quyền:** Admin  
**Router:** `admin_router.py`  
**Controller:** `handle_create_course_admin`

**Mô tả:** Admin tạo khóa học mới thay mặt cho giảng viên.

**Request Schema:**
```json
{
  "title": "string (bắt buộc)",
  "description": "string (bắt buộc)",
  "creator_id": "string (UUID giảng viên, bắt buộc)",
  "category": "string (bắt buộc)",
  "level": "string (Beginner|Intermediate|Advanced, bắt buộc)",
  "status": "string (active|draft, mặc định: draft)"
}
```

**Response Schema (201 Created):**
```json
{
  "course_id": "string (UUID)",
  "title": "string",
  "creator_name": "string",
  "status": "string",
  "created_at": "datetime",
  "message": "Khóa học đã được tạo thành công"
}
```

---

### 9.11 Cập nhật khóa học
**Endpoint:** `PUT /api/v1/admin/courses/{course_id}`  
**Quyền:** Admin  
**Router:** `admin_router.py`  
**Controller:** `handle_update_course_admin`

**Mô tả:** Admin chỉnh sửa thông tin khóa học.

**Request Schema:**
```json
{
  "title": "string (tùy chọn)",
  "description": "string (tùy chọn)",
  "category": "string (tùy chọn)",
  "level": "string (tùy chọn)",
  "status": "string (active|draft|archived, tùy chọn)"
}
```

**Response Schema (200 OK):**
```json
{
  "course_id": "string (UUID)",
  "message": "Khóa học đã được cập nhật",
  "updated_at": "datetime"
}
```

---

### 9.12 Xóa khóa học
**Endpoint:** `DELETE /api/v1/admin/courses/{course_id}`  
**Quyền:** Admin  
**Router:** `admin_router.py`  
**Controller:** `handle_delete_course_admin`

**Mô tả:** Admin xóa khóa học vĩnh viễn (chỉ khi không có học viên đang học).

**Response Schema (200 OK):**
```json
{
  "message": "Khóa học đã được xóa vĩnh viễn"
}
```

---

### 9.13 Xem danh sách lớp học
**Endpoint:** `GET /api/v1/admin/classes`  
**Quyền:** Admin  
**Router:** `admin_router.py`  
**Controller:** `handle_list_classes_admin`

**Mô tả:** Admin xem tất cả lớp học trong hệ thống.

**Query Parameters:**
```
status: string (active|completed, tùy chọn)
instructor_id: string (UUID, tùy chọn - lọc theo giảng viên)
course_id: string (UUID, tùy chọn - lọc theo khóa học)
sort_by: string (created_at|student_count|name, mặc định: created_at)
order: string (asc|desc, mặc định: desc)
skip: number (pagination)
limit: number (pagination)
```

**Response Schema (200 OK):**
```json
{
  "data": [
    {
      "class_id": "string (UUID)",
      "class_name": "string",
      "course_title": "string",
      "instructor_name": "string",
      "student_count": "number",
      "status": "string (active|completed)",
      "created_at": "datetime"
    }
  ],
  "total": "number",
  "skip": "number",
  "limit": "number"
}
```

---

### 9.14 Xem chi tiết lớp học
**Endpoint:** `GET /api/v1/admin/classes/{class_id}`  
**Quyền:** Admin  
**Router:** `admin_router.py`  
**Controller:** `handle_get_class_detail_admin`

**Mô tả:** Admin xem thông tin chi tiết lớp học và thống kê.

**Response Schema (200 OK):**
```json
{
  "class_id": "string (UUID)",
  "class_name": "string",
  "course": {
    "course_id": "string (UUID)",
    "title": "string",
    "category": "string"
  },
  "instructor": {
    "user_id": "string (UUID)",
    "full_name": "string",
    "email": "string"
  },
  "student_count": "number",
  "invite_code": "string",
  "status": "string",
  "class_stats": {
    "average_progress": "number (0-100%)",
    "completion_rate": "number (0-100%)",
    "active_students_today": "number"
  },
  "created_at": "datetime",
  "start_date": "datetime",
  "end_date": "datetime"
}
```

---

### 9.16 Xem dashboard admin tổng quan
**Endpoint:** `GET /api/v1/admin/dashboard`  
**Quyền:** Admin  
**Router:** `dashboard_router.py`  
**Controller:** `handle_get_admin_dashboard`

**Mô tả:** Thống kê tổng quan toàn hệ thống cho admin.

**Response Schema (200 OK):**
```json
{
  "system_stats": {
    "total_users": "number",
    "total_courses": "number", 
    "total_classes": "number",
    "total_enrollments": "number"
  },
  "growth_metrics": {
    "new_users_today": "number",
    "new_users_this_week": "number",
    "new_courses_this_month": "number",
    "active_users_today": "number"
  },
  "popular_courses": [
    {
      "course_id": "string (UUID)",
      "title": "string",
      "enrollment_count": "number",
      "completion_rate": "number (0-100%)"
    }
  ],
  "recent_activities": [
    {
      "type": "string (user_registered|course_created|class_created)",
      "description": "string",
      "timestamp": "datetime"
    }
  ]
}
```

---

### 9.17 Xem dashboard giảng viên
**Endpoint:** `GET /api/v1/dashboard/instructor`  
**Quyền:** Instructor  
**Router:** `dashboard_router.py`  
**Controller:** `handle_get_instructor_dashboard`

**Mô tả:** Dashboard tổng quan cho giảng viên về các lớp học và học viên.

**Response Schema (200 OK):**
```json
{
  "instructor_id": "string (UUID)",
  "overview": {
    "total_classes": "number",
    "total_students": "number",
    "active_classes": "number",
    "average_completion_rate": "number (0-100%)"
  },
  "recent_classes": [
    {
      "class_id": "string (UUID)",
      "class_name": "string",
      "student_count": "number",
      "recent_activity": "datetime"
    }
  ],
  "student_activities": [
    {
      "student_name": "string",
      "class_name": "string", 
      "activity": "string (completed_lesson|passed_quiz)",
      "timestamp": "datetime"
    }
  ],
  "upcoming_deadlines": [
    {
      "class_name": "string",
      "task": "string",
      "due_date": "datetime"
    }
  ]
}
```

---

### 9.15 Thống kê tăng trưởng người dùng
**Endpoint:** `GET /api/v1/admin/analytics/users-growth`  
**Quyền:** Admin  
**Router:** `analytics_router.py`  
**Controller:** `handle_get_admin_users_growth`

**Mô tả:** Biểu đồ tăng trưởng người dùng theo thời gian.

**Query Parameters:**
```
period: string (30days|90days|1year, mặc định: 90days)
group_by: string (day|week|month, mặc định: week)
```

**Response Schema (200 OK):**
```json
{
  "period": "string",
  "growth_data": [
    {
      "date": "date (YYYY-MM-DD)",
      "new_users": "number",
      "total_users": "number",
      "new_students": "number",
      "new_instructors": "number"
    }
  ],
  "summary": {
    "total_growth_rate": "number (%)",
    "average_daily_signups": "number",
    "peak_signup_day": {
      "date": "date",
      "count": "number"
    }
  }
}
```

---

### 9.18 Thống kê khóa học hệ thống
**Endpoint:** `GET /api/v1/admin/analytics/courses`  
**Quyền:** Admin  
**Router:** `analytics_router.py`  
**Controller:** `handle_get_admin_courses_analytics`

**Mô tả:** Phân tích hiệu suất các khóa học trong hệ thống. Top courses được tính dựa trên số lượng enrollments trong time_range, sử dụng field `enrolled_at` (không phải `created_at`) để filter chính xác thời điểm học viên đăng ký khóa học.

**Response Schema (200 OK):**
```json
{
  "course_metrics": {
    "total_courses": "number",
    "public_courses": "number", 
    "personal_courses": "number",
    "average_enrollment_per_course": "number"
  },
  "top_courses": [
    {
      "course_id": "string (UUID)",
      "title": "string",
      "creator": "string (instructor name)",
      "enrollment_count": "number",
      "completion_rate": "number (0-100%)",
      "average_rating": "number (0-5.0)"
    }
  ],
  "category_breakdown": [
    {
      "category": "string",
      "course_count": "number",
      "total_enrollments": "number"
    }
  ]
}
```

---

### 9.19 Giám sát sức khỏe hệ thống
**Endpoint:** `GET /api/v1/admin/analytics/system-health`  
**Quyền:** Admin  
**Router:** `analytics_router.py`  
**Controller:** `handle_get_admin_system_health`

**Mô tả:** Thống kê tình trạng hoạt động và hiệu suất hệ thống.

**Response Schema (200 OK):**
```json
{
  "system_status": "string (healthy|warning|critical)",
  "performance_metrics": {
    "average_response_time": "number (ms)",
    "api_success_rate": "number (0-100%)",
    "concurrent_users": "number",
    "server_uptime": "number (hours)"
  },
  "resource_usage": {
    "database_size": "number (MB)",
    "storage_used": "number (GB)",
    "memory_usage": "number (%)",
    "cpu_usage": "number (%)"
  },
  "recent_errors": [
    {
      "error_type": "string",
      "count": "number",
      "last_occurrence": "datetime"
    }
  ]
}
```

---

## 10. CHỨC NĂNG CHUNG (5.x)

### 10.1 Tìm kiếm toàn cầu
**Endpoint:** `GET /api/v1/search`  
**Quyền:** All roles  
**Router:** `search_router.py`  
**Controller:** `handle_global_search`

**Mô tả:** Tìm kiếm thông minh tất cả nội dung: khóa học, lớp học, người dùng, bài học.

**Query Parameters:**
```
q: string (từ khóa tìm kiếm, bắt buộc)
type: string (courses|classes|users|lessons, tùy chọn - lọc loại kết quả)
category: string (danh mục khóa học, tùy chọn)
level: string (Beginner|Intermediate|Advanced, tùy chọn)
skip: number (pagination)
limit: number (pagination, tối đa: 50)
```

**Response Schema (200 OK):**
```json
{
  "query": "string",
  "total_results": "number",
  "results": [
    {
      "type": "string (course|class|user|lesson)",
      "id": "string (UUID)",
      "title": "string",
      "description": "string",
      "thumbnail_url": "string (tùy chọn)",
      "relevance_score": "number (0-100)",
      "highlight": "string (đoạn text có từ khóa được highlight)"
    }
  ],
  "suggestions": ["string array (gợi ý từ khóa liên quan)"],
  "filters": {
    "available_categories": ["string array"],
    "available_levels": ["string array"]
  }
}
```

---

## ERROR RESPONSES

Tất cả API endpoints sử dụng các HTTP status codes tiêu chuẩn:

| Status | Ý nghĩa |
|--------|---------|
| **200** | OK - Request thành công |
| **201** | Created - Resource được tạo thành công |
| **400** | Bad Request - Dữ liệu không hợp lệ |
| **401** | Unauthorized - Cần xác thực |
| **403** | Forbidden - Không có quyền |
| **404** | Not Found - Resource không tìm thấy |
| **409** | Conflict - Dữ liệu trùng lặp (ví dụ: email exist) |
| **422** | Unprocessable Entity - Validation error |
| **500** | Internal Server Error - Lỗi server |

**Error Response Format:**
```json
{
  "detail": "string (mô tả lỗi chi tiết)",
  "status_code": "number",
  "timestamp": "datetime"
}
```

---

## AUTHENTICATION

### JWT Token Format
```
Header: Authorization: Bearer <access_token>
```

### Token Expiration
- **Access Token:** 15 phút
- **Refresh Token:** 7 ngày (nếu remember_me=true)

**Ghi chú:**
- Refresh token được trả về khi login với `remember_me=true`
- Không có API riêng để refresh token trong CHUCNANG.md
- Frontend cần handle việc re-login khi access token hết hạn

---

## PAGINATION

Tất cả endpoints trả về danh sách sử dụng pagination:

**Query Parameters:**
```
skip: number (offset, mặc định: 0)
limit: number (số lượng mỗi trang, mặc định: 10, tối đa: 100)
```

**Response Format:**
```json
{
  "data": ["array của items"],
  "total": "number (tổng số items)",
  "skip": "number",
  "limit": "number"
}
```

---

## NOTES

**Naming Conventions:**
- Tất cả path parameters sử dụng dạng `{resource_id}` để rõ ràng (ví dụ: `{course_id}`, `{class_id}`, `{student_id}`)
- Pagination sử dụng `skip` và `limit` (phù hợp với MongoDB query methods)

**Data Formats:**
- Tất cả datetime sử dụng **ISO 8601 format** với múi giờ UTC (ví dụ: 2025-11-03T10:30:00Z)
- Tất cả UUID sử dụng **UUID v4 format**
- Tất cả requests/responses sử dụng **Content-Type: application/json**

**Response Messages:**
- Luôn có `message` field cho POST, PUT, PATCH, DELETE (201, 200, 204)
- Luôn có `message` field cho tất cả errors (4xx, 5xx)
- GET thành công (200) không bắt buộc có `message`, dữ liệu là đủ
- Các **skill tags** được sử dụng để tracking kiến thức chi tiết (ví dụ: python-syntax, algorithm-complexity)
- Các **learning outcomes** phải **đo lường được** (measurable)
- Câu hỏi trong assessment được **sắp xếp từ dễ đến khó**
- **Điểm liệt** (mandatory questions) phải **trả lời đúng** để pass
- **Quiz** được **AI sinh động** để tránh học thuộc lòng
- **Progress tracking** tự động - không cho phép đánh dấu thủ công
- **Unlock mechanism** - chỉ khi pass lesson mới được học lesson tiếp theo

---

**END OF API SCHEMA SPECIFICATION**

