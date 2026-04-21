# Kế hoạch Kiểm Tra 1-1 Toàn Diện: Backend ↔ Frontend

Rà soát toàn bộ logic, API request/response, schema dữ liệu, auth/RBAC, và business rules theo từng chức năng/nhóm API. Ưu tiên logic thực từ backend và schema Pydantic làm chuẩn sự thật.

> [!IMPORTANT]
> **Nguyên tắc kiểm tra:** Backend (Pydantic schemas + service logic) là nguồn sự thật (source of truth). FE service layer phải mapping chính xác 1-1 với BE.

---

## Phương Pháp Kiểm Tra

Mỗi nhóm chức năng sẽ được kiểm tra theo thứ tự:

1. **BE Schema** → Đọc `BELEARNINGAI/schemas/*.py` → xác định request/response fields thực tế
2. **BE Router → Controller → Service** → Xác định endpoint URL, method, auth guard, business logic
3. **FE Service** → Đọc `FE/src/services/*.js` → kiểm tra URL, payload, headers, response handling
4. **FE Page/Component** → Đọc FE page tương ứng → kiểm tra state management, error handling, UI data mapping
5. **Flag lỗi** → Ghi nhận mismatch, missing fields, wrong auth, wrong URL pattern

---

## Danh Sách Kiểm Tra Theo Nhóm Chức Năng

### 🔐 NHÓM 1: AUTH & NGƯỜI DÙNG (auth_router, users_router)

| # | Endpoint | BE File | FE Service | FE Page | Ưu tiên |
|---|----------|---------|------------|---------|---------|
| 1.1 | `POST /api/v1/auth/register` | `auth_router`, `auth_controller`, `auth_service`, `schemas/auth.py` | `authService.js` | `RegisterPage.jsx` | 🔴 CAO |
| 1.2 | `POST /api/v1/auth/login` | `auth_router`, `auth_controller`, `auth_service`, `schemas/auth.py` | `authService.js` | `LoginPage.jsx` | 🔴 CAO |
| 1.3 | `POST /api/v1/auth/logout` | `auth_router`, `auth_controller` | `authService.js` | `authStore.js` | 🔴 CAO |
| 1.4 | `GET /api/v1/users/me` | `users_router`, `user_controller`, `user_service`, `schemas/user.py` | `userService.js` | `ProfilePage.jsx` | 🔴 CAO |
| 1.5 | `PATCH /api/v1/users/me` | `users_router`, `user_controller`, `user_service` | `userService.js` | `ProfilePage.jsx` | 🟡 TRUNG |
| 1.6 | `POST /api/v1/auth/refresh` *(nếu tồn tại)* | `auth_router`, `auth_controller`, `auth_service` | `api.js` interceptor | `authStore.js` | 🔴 CAO |

**Điểm cần kiểm tra đặc biệt:**
- `remember_me` field trong login request có được FE gửi lên không?
- JWT Bearer token có được đính vào mọi request cần auth không? (`api.js` interceptor)
- `authStore.js` lưu trữ `access_token`, `refresh_token`, `user` có đầy đủ không?
- Logout có clear token khỏi store và redirect về `/login` không?
- Password policy (tối thiểu 8 ký tự, chứa số, chữ hoa, ký tự đặc biệt) có được validate ở FE không?

**🔄 [BỔ SUNG] Refresh Token Flow — Điểm kiểm tra bắt buộc:**
- `api.js` response interceptor có bắt lỗi **401** và tự động gọi `/api/v1/auth/refresh` bằng `refresh_token` trước khi redirect login không?
- Có cơ chế **request queue** (hàng đợi) để giữ lại các request bị 401 trong lúc đang refresh, rồi retry lại toàn bộ sau khi có token mới không? *(Không có queue → nhiều request sẽ cùng lúc gọi refresh → race condition)*
- Nếu `refresh_token` cũng hết hạn hoặc bị từ chối (BE trả 401 lần nữa), FE có:
  - Gọi `authStore.logout()` để clear toàn bộ state không?
  - Redirect về `/login` không?
  - Hiển thị toast/banner **"Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại."** không?
- **Kịch bản nguy hiểm cần test:** User đang làm bài Assessment 60 phút → access token 15 phút hết hạn → request submit bị 401 → interceptor refresh thành công → request submit được retry → kết quả được lưu đúng không?

---

### 📋 NHÓM 2: ĐÁNH GIÁ NĂNG LỰC AI (assessments_router)

| # | Endpoint | BE File | FE Service | FE Page | Ưu tiên |
|---|----------|---------|------------|---------|---------|
| 2.1 | `POST /api/v1/assessments/generate` | `assessments_router`, `assessment_controller`, `assessment_service`, `schemas/assessment.py` | `assessmentService.js` | `AssessmentSetupPage.jsx` | 🔴 CAO |
| 2.2 | `POST /api/v1/assessments/{session_id}/submit` | `assessments_router`, `assessment_controller` | `assessmentService.js` | `AssessmentQuizPage.jsx` | 🔴 CAO |
| 2.3 | `GET /api/v1/assessments/{session_id}/results` | `assessments_router`, `assessment_controller` | `assessmentService.js` | `AssessmentResultsPage.jsx` | 🔴 CAO |
| 2.4 | `GET /api/v1/recommendations/from-assessment` | `recommendation_router`, `recommendation_controller` | `recommendationService.js` | `AssessmentResultsPage.jsx` | 🟡 TRUNG |

**Điểm cần kiểm tra đặc biệt:**
- `session_id` từ response generate có được lưu và truyền sang submit/results không?
- Request schema `generate`: `focus_areas` array có được gửi đúng format không?
- `question_type` enum values: `multiple_choice|fill_in_blank|drag_and_drop` — FE render tương ứng không?
- Submit request: `time_taken_seconds` per question + `total_time_seconds` FE có tracking không?
- Cơ chế timeout 60 phút: FE có đếm ngược và tự submit không?
- `from-assessment` dùng `?session_id=` query param — FE có gửi đúng không?

**⏳ [BỔ SUNG] AI Latency Handling — áp dụng cho `POST /assessments/generate` và `POST .../assessments/generate` (module):**
- Config Axios cho endpoint này có timeout nâng lên ít nhất **60000ms** (60 giây) thay vì mặc định không?
- Trong thời gian chờ AI sinh câu hỏi, FE có:
  - Hiển thị **loading skeleton / spinner** thay vì màn hình trắng không?
  - **Disable** nút "Bắt đầu đánh giá" để ngăn spam click tạo nhiều session AI song song không?
- Nếu BE dùng **SSE (Server-Sent Events) / Streaming** để trả về từng câu hỏi dần: FE có dùng `EventSource` hoặc `fetch` với ReadableStream thay vì Axios không? *(Axios không hỗ trợ stream native)*

---

### 📚 NHÓM 3: KHÁM PHÁ & ĐĂNG KÝ KHÓA HỌC (courses_router, enrollments_router)

| # | Endpoint | BE File | FE Service | FE Page | Ưu tiên |
|---|----------|---------|------------|---------|---------|
| 3.1 | `GET /api/v1/courses/search` | `courses_router`, `course_controller`, `course_service`, `schemas/course.py` | `courseService.js` | `CoursesPage.jsx` | 🔴 CAO |
| 3.2 | `GET /api/v1/courses/public` | `courses_router`, `course_controller` | `courseService.js` | `CoursesPage.jsx` | 🔴 CAO |
| 3.3 | `GET /api/v1/courses/{course_id}` | `courses_router`, `course_controller` | `courseService.js` | `CourseDetailPage.jsx` | 🔴 CAO |
| 3.4 | `POST /api/v1/enrollments` | `enrollments_router`, `enrollment_controller`, `enrollment_service`, `schemas/enrollment.py` | `enrollmentService.js` | `CourseDetailPage.jsx` | 🔴 CAO |
| 3.5 | `GET /api/v1/enrollments/my-courses` | `enrollments_router`, `enrollment_controller` | `enrollmentService.js` | `MyCoursesPage.jsx` | 🔴 CAO |
| 3.6 | `GET /api/v1/enrollments/{enrollment_id}` | `enrollments_router`, `enrollment_controller` | `enrollmentService.js` | `MyCoursesPage.jsx` | 🟡 TRUNG |
| 3.7 | `GET /api/v1/courses/{course_id}/enrollment-status` | `courses_router` | `enrollmentService.js` | `CourseDetailPage.jsx` | 🟡 TRUNG |
| 3.8 | `DELETE /api/v1/enrollments/{enrollment_id}` | `enrollments_router` | `enrollmentService.js` | `MyCoursesPage.jsx` | 🟡 TRUNG |

**Điểm cần kiểm tra đặc biệt:**
- URL endpoint: `/courses/search` vs `/courses/public` — FE có dùng đúng hai endpoint riêng không, hay gộp?
- Query params cho search: `keyword`, `category`, `level`, `sort_by`, `sort_order`, `skip`, `limit` — FE gửi đúng tên không?
- `is_enrolled` field trong response courses list — FE có dùng để hiển thị button đúng không?
- POST enrollments request body: chỉ cần `{ "course_id": "..." }` — FE có gửi đúng không?
- `enrollment_info` nested object trong course detail — FE có đọc đúng path không?
- `StudentEnrollmentPage.jsx` và `InstructorDashboardPage.jsx` — các trang này dùng service nào?

---

### 🎓 NHÓM 4: HỌC TẬP & TIẾN ĐỘ (learning_router, quiz_router, progress_router)

| # | Endpoint | BE File | FE Service | FE Page | Ưu tiên |
|---|----------|---------|------------|---------|---------|
| 4.1 | `GET /api/v1/courses/{course_id}/modules/{module_id}` | `learning_router`, `learning_controller`, `learning_service`, `schemas/learning.py` | `learningService.js` | `ModuleDetailPage.jsx` | 🔴 CAO |
| 4.2 | `GET /api/v1/courses/{course_id}/lessons/{lesson_id}` | `learning_router`, `learning_controller` | `learningService.js` | `LessonPage.jsx` | 🔴 CAO |
| 4.3 | `GET /api/v1/courses/{course_id}/modules` | `learning_router`, `learning_controller` | `learningService.js` | `ModuleListPage.jsx` | 🔴 CAO |
| 4.4 | `GET /api/v1/courses/{course_id}/modules/{module_id}/outcomes` | `learning_router` | `learningService.js` | `ModuleDetailPage.jsx` | 🟡 TRUNG |
| 4.5 | `GET /api/v1/courses/{course_id}/modules/{module_id}/resources` | `learning_router` | `learningService.js` | `ModuleDetailPage.jsx` | 🟡 TRUNG |
| 4.6 | `POST /api/v1/courses/{course_id}/modules/{module_id}/assessments/generate` | `learning_router` | `learningService.js` | `ModuleDetailPage.jsx` | 🟢 THẤP |
| 4.7 | `GET /api/v1/quizzes/{quiz_id}` | `quiz_router`, `quiz_controller`, `quiz_service`, `schemas/quiz.py` | `quizService.js` | `QuizDetailPage.jsx` | 🔴 CAO |
| 4.8 | `POST /api/v1/quizzes/{quiz_id}/attempt` | `quiz_router`, `quiz_controller` | `quizService.js` | `QuizAttemptPage.jsx` | 🔴 CAO |
| 4.9 | `GET /api/v1/quizzes/{quiz_id}/results` | `quiz_router` | `quizService.js` | `QuizResultsPage.jsx` | 🔴 CAO |
| 4.10 | `POST /api/v1/quizzes/{quiz_id}/retake` | `quiz_router` | `quizService.js` | `QuizAttemptPage.jsx` | 🟡 TRUNG |
| 4.11 | `POST /api/v1/ai/generate-practice` | `learning_router` | `learningService.js` | `LessonPage.jsx` | 🟡 TRUNG |
| 4.12 | *(Quiz attempt auto-complete)* | `quiz_controller/service` | `quizService.js` | `QuizAttemptPage.jsx` | 🔴 CAO |
| 4.13 | `POST /api/v1/lessons/{lesson_id}/quizzes` | `quiz_router` | `quizService.js` | *(Instructor UI)* | 🟢 THẤP |
| 4.14 | `GET /api/v1/quizzes?role=instructor` | `quiz_router` | `quizService.js` | `QuizPage.jsx` | 🟡 TRUNG |
| 4.15 | `PUT /api/v1/quizzes/{quiz_id}` | `quiz_router` | `quizService.js` | *(Editor UI)* | 🟢 THẤP |
| 4.16 | `DELETE /api/v1/quizzes/{quiz_id}` | `quiz_router` | `quizService.js` | `QuizPage.jsx` | 🟢 THẤP |
| 4.17 | `GET /api/v1/quizzes/{quiz_id}/class-results` | `quiz_router` | `quizService.js` | `QuizResultsPage.jsx` | 🟡 TRUNG |
| 4.18 | `GET /api/v1/progress/course/{course_id}` | `progress_router`, `progress_controller` | `progressService.js` | `ProgressPage.jsx` | 🔴 CAO |

**Điểm cần kiểm tra đặc biệt:**
- `navigation.previous_lesson` và `navigation.next_lesson` nested objects trong lesson response — FE có parse đúng không?
- `quiz_info.quiz_id` trong lesson response — FE dùng để navigate đến quiz không?
- `completion_status` object trong lesson — `is_completed`, `video_progress_percent` FE có tracking không?
- ChatWidget trong LessonPage sử dụng `useChatLogic.js` — course_id có được pass vào hook không?
- Unlock mechanism: FE có blockUI khi next_lesson `is_locked = true` không?
- Quiz attempt response: `lesson_completed`, `next_lesson_unlocked` — FE xử lý auto-redirect không?
- `POST /api/v1/ai/generate-practice` — At least one of `lesson_id`, `course_id`, `topic_prompt` — FE validate không?

---

### 📝 NHÓM 5: KHÓA HỌC CÁ NHÂN (personal_courses_router)

| # | Endpoint | BE File | FE Service | FE Page | Ưu tiên |
|---|----------|---------|------------|---------|---------|
| 5.1 | `POST /api/v1/courses/from-prompt` | `personal_courses_router`, `personal_courses_controller`, `personal_courses_service`, `schemas/personal_courses.py` | `personalCourseService.js` | `PersonalCoursesPage.jsx` | 🔴 CAO |
| 5.2 | `POST /api/v1/courses/personal` | `personal_courses_router` | `personalCourseService.js` | `PersonalCoursesPage.jsx` | 🔴 CAO |
| 5.3 | `GET /api/v1/courses/my-personal` | `personal_courses_router` | `personalCourseService.js` | `PersonalCoursesPage.jsx` | 🔴 CAO |
| 5.4 | `PUT /api/v1/courses/personal/{course_id}` | `personal_courses_router` | `personalCourseService.js` | `CourseEditorPage.jsx` | 🔴 CAO |
| 5.5 | `DELETE /api/v1/courses/personal/{course_id}` | `personal_courses_router` | `personalCourseService.js` | `PersonalCoursesPage.jsx` | 🟡 TRUNG |

**Điểm cần kiểm tra đặc biệt:**
- `from-prompt` endpoint: `prompt` minimum 20 chars — FE validate trước khi gửi không?
- Response của `from-prompt` có `modules[].lessons[].content_outline` — FE hiển thị trong editor không?
- `PUT .../personal/{course_id}` request: nested `modules[].lessons[]` với `id` null cho item mới — FE xây dựng request body đúng không?
- Auto-save 2-3 giây: FE có debounce save logic trong `CourseEditorPage` không?
- URL conflict: `/courses/from-prompt`, `/courses/personal`, `/courses/my-personal` — router priority với `/courses/{course_id}` cần kiểm tra BE và FE

---

### 💬 NHÓM 6: CHATBOT AI (chat_router)

| # | Endpoint | BE File | FE Service | FE Page/Component | Ưu tiên |
|---|----------|---------|------------|---------|---------|
| 6.1 | `POST /api/v1/chat/course/{course_id}` | `chat_router`, `chat_controller`, `chat_service`, `schemas/chat.py` | `chatService.js` | `ChatPage.jsx`, `ChatWidget.jsx`, `useChatLogic.js` | 🔴 CAO |
| 6.2 | `GET /api/v1/chat/history` | `chat_router` | `chatService.js` | `ChatPage.jsx` | 🔴 CAO |
| 6.3 | `GET /api/v1/chat/conversations/{conversation_id}` | `chat_router` | `chatService.js` | `ChatPage.jsx` | 🔴 CAO |
| 6.4 | `DELETE /api/v1/chat/conversations` | `chat_router` | `chatService.js` | `ChatPage.jsx` | 🟡 TRUNG |
| 6.5 | `DELETE /api/v1/chat/history/{conversation_id}` | `chat_router` | `chatService.js` | `ChatPage.jsx` | 🟡 TRUNG |

**Điểm cần kiểm tra đặc biệt:**
- `useChatLogic.js` hook: có quản lý `conversation_id` state giữa các messages không?
- `ChatWidget.jsx` trong LessonPage: `course_id` được lấy từ router params và pass vào API không?
- `context_type` field trong chat request (`lesson|module|general`) — FE có gửi không?
- Response `sources[]` array — `ChatWidget` có hiển thị nguồn tham khảo không?
- History API: `grouped_by_date` object — FE có render theo nhóm ngày không?
- DELETE all conversations: FE có confirm modal không?

**⏳ [BỔ SUNG] AI Latency Handling — áp dụng cho `POST /api/v1/chat/course/{course_id}`:**
- Timeout Axios cho chat endpoint có được nâng lên **120000ms** (2 phút) không? *(AI có thể cần tới 20-30s để tra cứu context khóa học và tạo câu trả lời)*
- Nếu BE trả về **streaming response từng token** (SSE/chunked): FE có dùng `fetch` + `ReadableStream` để render từng chữ dần (typing effect) không? Hay đang dùng Axios và chờ toàn bộ response?
- Trong khi AI đang xử lý, nút **Gửi** có bị disable (+ hiển thị spinner nhỏ trong input) để ngăn gửi nhiều tin nhắn song song không?

---

### 📊 NHÓM 7: DASHBOARD & ANALYTICS (dashboard_router, analytics_router)

| # | Endpoint | BE File | FE Service | FE Page | Ưu tiên |
|---|----------|---------|------------|---------|---------|
| 7.1 | `GET /api/v1/dashboard/student` | `dashboard_router`, `dashboard_controller`, `dashboard_service`, `schemas/dashboard.py` | `dashboardService.js` | `DashboardPage.jsx` | 🔴 CAO |
| 7.2 | `GET /api/v1/analytics/learning-stats` | `analytics_router` | `analyticsService.js` | `ProgressPage.jsx` | 🟡 TRUNG |
| 7.3 | `GET /api/v1/analytics/progress-chart` | `analytics_router` | `analyticsService.js` | `ProgressPage.jsx` | 🟡 TRUNG |
| 7.4 | `GET /api/v1/recommendations` | `recommendation_router`, `recommendation_controller`, `recommendation_service`, `schemas/recommendation.py` | `recommendationService.js` | `RecommendationsPage.jsx` | 🟡 TRUNG |
| 7.5 | `GET /api/v1/dashboard/instructor` | `dashboard_router` | `dashboardService.js` | `InstructorDashboardPage.jsx` | 🔴 CAO |
| 7.6 | `GET /api/v1/analytics/instructor/classes` | `analytics_router` | `analyticsService.js` | `InstructorDashboardPage.jsx` | 🟡 TRUNG |
| 7.7 | `GET /api/v1/analytics/instructor/progress-chart` | `analytics_router` | `analyticsService.js` | `InstructorDashboardPage.jsx` | 🟡 TRUNG |
| 7.8 | `GET /api/v1/analytics/instructor/quiz-performance` | `analytics_router` | `analyticsService.js` | `InstructorDashboardPage.jsx` | 🟡 TRUNG |

**Điểm cần kiểm tra đặc biệt:**
- `overview` nested object trong student dashboard — FE map đúng tên field không?
- `recent_courses[].next_lesson` nested object — FE hiển thị "Tiếp tục học" button đúng không?
- `pending_quizzes[]` — FE hiển thị và navigate tới đúng quiz không?
- `performance_summary` — FE render stats đúng không?
- Analytics chart: `period` query param (`7days|30days|90days|1year`) — FE có control period selector không?
- Instructor dashboard: RBAC — chỉ render nếu `user.role === 'instructor'` không?

---

### 🏫 NHÓM 8: QUẢN LÝ LỚP HỌC (classes_router)

| # | Endpoint | BE File | FE Service | FE Page/Component | Ưu tiên |
|---|----------|---------|------------|---------|---------|
| 8.1 | `POST /api/v1/classes` | `classes_router`, `class_controller`, `class_service`, `schemas/classes.py` | `classService.js` | `ClassCreatePage.jsx` | 🔴 CAO |
| 8.2 | `GET /api/v1/classes/my-classes` | `classes_router` | `classService.js` | `ClassListPage.jsx` | 🔴 CAO |
| 8.3 | `GET /api/v1/classes/{class_id}` | `classes_router` | `classService.js` | `ClassDetailPage.jsx` | 🔴 CAO |
| 8.4 | `PUT /api/v1/classes/{class_id}` | `classes_router` | `classService.js` | `ClassDetailPage.jsx` | 🟡 TRUNG |
| 8.5 | `DELETE /api/v1/classes/{class_id}` | `classes_router` | `classService.js` | `ClassDetailPage.jsx` | 🟡 TRUNG |
| 8.6 | `POST /api/v1/classes/join` | `classes_router` | `classService.js` | `JoinClassModal.jsx` | 🔴 CAO |
| 8.7 | `GET /api/v1/classes/{class_id}/students` | `classes_router` | `classService.js` | `ClassDetailPage.jsx` | 🔴 CAO |
| 8.8 | `GET /api/v1/classes/{class_id}/students/{student_id}` | `classes_router` | `classService.js` | `ClassDetailPage.jsx` | 🟡 TRUNG |
| 8.9 | `DELETE /api/v1/classes/{class_id}/students/{student_id}` | `classes_router` | `classService.js` | `ClassDetailPage.jsx` | 🟡 TRUNG |
| 8.10 | `GET /api/v1/classes/{class_id}/progress` | `classes_router` | `classService.js` | `ClassDetailPage.jsx` | 🟡 TRUNG |

**Điểm cần kiểm tra đặc biệt:**
- `JoinClassModal.jsx` gửi `{ invite_code: "..." }` — component có pass đúng data không?
- Response `class_id` vs `id` — BE trả về field nào, FE đọc field nào?
- `invite_code` hiển thị ở ClassDetailPage — copy function có làm việc không?
- RBAC tại FE: Class create/manage chỉ cho Instructor role — `ProtectedRoute.jsx` check đúng không?
- `ClassCreatePage`: `course_id` select — FE có gọi API lấy danh sách courses để chọn không?

---

### 🔍 NHÓM 9: TÌM KIẾM TOÀN CỤC (search_router)

| # | Endpoint | BE File | FE Service | FE Page/Component | Ưu tiên |
|---|----------|---------|------------|---------|---------|
| 9.1 | `GET /api/v1/search` | `search_router`, `search_controller`, `search_service`, `schemas/search.py` | `searchService.js` | `SearchResultsPage.jsx`, `GlobalSearchBar.jsx` | 🔴 CAO |

**Điểm cần kiểm tra đặc biệt:**
- Query param: `q` (từ khóa) — `GlobalSearchBar` có gửi đúng param name không?
- `type` filter: `courses|classes|users|lessons` — FE có tabs/filter không?
- `GlobalSearchBar` trong `DashboardLayout` — debounce search có hoạt động không?
- Response `results[].type` — FE render card khác nhau cho mỗi type không?
- `suggestions[]` array — FE hiển thị dropdown gợi ý không?

---

### 🛡️ NHÓM 10: ADMIN MANAGEMENT (admin_router)

| # | Endpoint | BE File | FE Service | FE Page | Ưu tiên |
|---|----------|---------|------------|---------|---------|
| 10.1 | `GET /api/v1/admin/users` | `admin_router`, `admin_controller`, `admin_service`, `schemas/admin.py` | `adminService.js` | `AdminPage.jsx` | 🔴 CAO |
| 10.2 | `GET /api/v1/admin/users/{user_id}` | `admin_router` | `adminService.js` | `AdminPage.jsx` | 🟡 TRUNG |
| 10.3 | `POST /api/v1/admin/users` | `admin_router` | `adminService.js` | `AdminPage.jsx` | 🟡 TRUNG |
| 10.4 | `PUT /api/v1/admin/users/{user_id}` | `admin_router` | `adminService.js` | `AdminPage.jsx` | 🟡 TRUNG |
| 10.5 | `DELETE /api/v1/admin/users/{user_id}` | `admin_router` | `adminService.js` | `AdminPage.jsx` | 🟡 TRUNG |
| 10.6 | `PUT /api/v1/admin/users/{user_id}/role` | `admin_router` | `adminService.js` | `AdminPage.jsx` | 🟡 TRUNG |
| 10.7 | `POST /api/v1/admin/users/{user_id}/reset-password` | `admin_router` | `adminService.js` | `AdminPage.jsx` | 🟡 TRUNG |
| 10.8 | `GET /api/v1/admin/courses` | `admin_router` | `adminService.js` | `AdminPage.jsx` | 🔴 CAO |
| 10.9 | `GET /api/v1/admin/courses/{course_id}` | `admin_router` | `adminService.js` | `AdminPage.jsx` | 🟡 TRUNG |
| 10.10 | `POST /api/v1/admin/courses` | `admin_router` | `adminService.js` | `AdminPage.jsx` | 🟡 TRUNG |
| 10.11 | `PUT /api/v1/admin/courses/{course_id}` | `admin_router` | `adminService.js` | `AdminPage.jsx` | 🟡 TRUNG |
| 10.12 | `DELETE /api/v1/admin/courses/{course_id}` | `admin_router` | `adminService.js` | `AdminPage.jsx` | 🟡 TRUNG |
| 10.13 | `GET /api/v1/admin/classes` | `admin_router` | `adminService.js` | `AdminPage.jsx` | 🟡 TRUNG |
| 10.14 | `GET /api/v1/admin/classes/{class_id}` | `admin_router` | `adminService.js` | `AdminPage.jsx` | 🟡 TRUNG |
| 10.15 | `GET /api/v1/admin/dashboard` | `dashboard_router` | `dashboardService.js` | `AdminPage.jsx` | 🔴 CAO |
| 10.16 | `GET /api/v1/admin/analytics/users-growth` | `analytics_router` | `analyticsService.js` | `AdminPage.jsx` | 🟡 TRUNG |
| 10.17 | `GET /api/v1/admin/analytics/courses` | `analytics_router` | `analyticsService.js` | `AdminPage.jsx` | 🟡 TRUNG |
| 10.18 | `GET /api/v1/admin/analytics/system-health` | `analytics_router` | `analyticsService.js` | `AdminPage.jsx` | 🟢 THẤP |

**Điểm cần kiểm tra đặc biệt:**
- `AdminPage.jsx` có phải single-page với nhiều tabs/sections không? Cần xem cấu trúc component
- `ProtectedRoute.jsx` check `role === 'admin'` trước khi render admin routes không?
- Admin user list: field `user_id` vs `id` consistency — thống nhất giữa list và detail response không?
- `GET /api/v1/admin/dashboard` route đăng ký trong `dashboard_router` hay `admin_router`? Cần verify

---

## Cross-Cutting Concerns

### 🔑 Auth & RBAC Checklist

| Kiểm tra | Vị trí |
|----------|--------|
| Axios instance có `Authorization: Bearer <token>` interceptor | `api.js` |
| Token expiry (401) → interceptor thử refresh trước, rồi mới redirect login | `api.js` |
| **[MỚI]** Request queue tránh race condition khi nhiều request cùng bị 401 | `api.js` |
| **[MỚI]** Refresh Token hết hạn → force logout + toast "Phiên đăng nhập hết hạn" | `api.js`, `authStore.js` |
| `ProtectedRoute` check: `isAuthenticated` | `ProtectedRoute.jsx` |
| Role-based route guard: `admin`, `instructor`, `student` | `ProtectedRoute.jsx`, `AppRouter.jsx` |
| BE middleware: `get_current_user` dependency injection | `middleware/auth.py` |
| BE middleware: RBAC `require_role(['admin'])` | `middleware/rbac.py` |

### 📡 API Layer Checklist

| Kiểm tra | Vị trí |
|----------|--------|
| Base URL từ env var `VITE_API_BASE_URL` | `api.js`, `.env.example` |
| Content-Type: application/json trên POST/PUT/PATCH | `api.js` |
| **[MỚI]** Timeout mặc định Axios — AI endpoints cần riêng timeout ≥60s | `api.js` hoặc từng service call |
| Error response handling: `error.response.data.detail` | Mỗi service file |
| **[MỚI]** Toast thành công (200/201) và toast lỗi (4xx) đúng message từ BE | Mỗi page/component |
| Pagination params: `skip`/`limit` (không phải `page`/`per_page`) | Mọi list API |
| UUID format validation trước khi gọi API | FE forms |

### 📦 Data Model Checklist

| Kiểm tra | Vị trí |
|----------|--------|
| BE model `id` field vs `user_id`/`course_id`/`class_id` naming inconsistency | Mỗi response schema |
| Datetime: ISO 8601 UTC (`2025-11-03T10:30:00Z`) — FE parse/display đúng timezone | Mọi datetime field |
| Nullable fields: FE handle `null` gracefully (không crash) | Mọi optional fields |
| Enum values: case-sensitive matching giữa BE và FE | `role`, `status`, `level`, `category` |

---

### 🔄 [MỚI — BỔ SUNG 1] Refresh Token Flow

> [!CAUTION]
> Access Token sống 15 phút. User làm Assessment 60 phút hoặc chat kéo dài sẽ gặp 401 ở giữa chừng nếu không có refresh flow.

**Checklist Axios Interceptor (`api.js`):**

```
☐ Response interceptor bắt status 401
☐ Kiểm tra: lỗi này có phải từ chính request refresh không? (tránh vòng lặp vô tận)
☐ Gọi POST /api/v1/auth/refresh với { refresh_token } từ authStore
☐ Nếu refresh thành công → cập nhật token mới vào authStore → retry request gốc
☐ Queue: các request khác bị 401 trong lúc đang refresh phải được giữ lại và retry sau
☐ Nếu refresh thất bại (401 lần 2) → authStore.logout() → redirect /login → toast "Phiên đăng nhập đã hết hạn"
```

**Kịch bản kiểm tra thực tế:**
- Giả lập token hết hạn trong DevTools → submit assessment → kết quả có được lưu không?
- Mở 2 tab cùng lúc, cả 2 gặp 401 → chỉ 1 request refresh được gửi không?

---

### ⏳ [MỚI — BỔ SUNG 2] AI Latency Handling

> [!WARNING]
> Axios mặc định timeout thường là 0 (không timeout) hoặc rất thấp ở một số config. AI Gemini API có thể mất 5–20 giây. Nếu không disable nút, user spam click tạo nhiều session AI song song.

**Endpoints cần kiểm tra timeout và UX loading:**

| Endpoint | Timeout tối thiểu | Chặn spam click | Loading indicator |
|----------|------------------|-----------------|-------------------|
| `POST /assessments/generate` | 60s | ✅ Bắt buộc | Spinner full-page |
| `POST .../modules/.../assessments/generate` | 60s | ✅ Bắt buộc | Spinner inline |
| `POST /courses/from-prompt` | 120s | ✅ Bắt buộc | Progress bar / skeleton |
| `POST /chat/course/{course_id}` | 120s | ✅ Bắt buộc | Typing indicator (3 chấm) |

**Streaming (SSE) — kiểm tra nếu BE implement:**
```
☐ Chatbot có dùng SSE/chunked response không? (xem BE chat_service.py)
☐ Nếu có: FE có dùng fetch() + ReadableStream thay vì Axios không?
☐ from-prompt AI sinh course có streaming từng module/lesson không?
☐ Nếu có stream: FE render từng phần tử dần (progressive rendering) không?
```

---

### 🧹 [MỚI — BỔ SUNG 3] State Leakage Prevention

> [!CAUTION]
> Nếu chỉ xóa token khi logout mà không reset các store khác, User B đăng nhập trên cùng trình duyệt sẽ thấy dữ liệu của User A còn sót lại trong RAM.

**Checklist `authStore.js` — hàm `logout()`:**

```
☐ Xóa access_token, refresh_token, user khỏi authStore
☐ Gọi courseStore.reset() (xóa danh sách courses, enrollment đã load)
☐ Gọi uiStore.reset() (xóa UI state, notifications, search query)
☐ Nếu có learningStore, chatStore, progressStore → gọi reset() cho tất cả
☐ Clear localStorage / sessionStorage nếu có lưu state
☐ Sau khi clear xong mới navigate('/login')
```

**Kiểm tra tình huống:**
- Login user A → xem dashboard có data → logout → login user B → dashboard phải hiển thị data của B, không phải A

---

### 📎 [MỚI — BỔ SUNG 4] Multipart/Form-Data Upload

> [!WARNING]
> Gửi ảnh nhị phân qua `application/json` sẽ lỗi hoặc chỉ gửi được URL string. Cần xác định rõ endpoint nào thực sự upload file.

**Checklist — Xác định các endpoint upload:**

| Endpoint | Upload field | Cần FormData? | Ghi chú |
|----------|-------------|---------------|---------|
| `PATCH /api/v1/users/me` | `avatar_url` | Chỉ nếu là file upload trực tiếp | Schema BE hiện nhận URL string — verify xem BE có hỗ trợ file binary không |
| `POST /api/v1/courses/personal` | `thumbnail_url` | Chỉ nếu upload file | Tương tự — có thể chỉ nhận URL |
| `PUT /api/v1/courses/personal/{course_id}` | `thumbnail_url` | Chỉ nếu upload file | Verify BE schema |

**Nếu xác nhận BE có nhận file upload:**
```
☐ FE tạo FormData object: const form = new FormData(); form.append('avatar', file)
☐ Gọi axios với headers { 'Content-Type': 'multipart/form-data' } (hoặc để browser tự set boundary)
☐ KHÔNG dùng instance Axios mặc định (đang set Content-Type: application/json)
☐ Validate file size và type ở FE trước khi upload
☐ Hiển thị preview ảnh sau khi chọn file (trước khi upload)
```

---

### 🔔 [MỚI — BỔ SUNG 5] UI Toast / Feedback Verification

> [!IMPORTANT]
> Hệ thống chỉ hoàn thiện khi người dùng biết rõ điều gì đang xảy ra. "Có lỗi xảy ra" là không chấp nhận được.

**Quy tắc bắt buộc cho mọi action:**

| HTTP Status | Loại action | FE phải làm |
|-------------|-------------|-------------|
| 200 / 201 | POST/PUT/PATCH/DELETE | 🟢 Toast thành công với message từ `response.data.message` |
| 400 Bad Request | Bất kỳ | 🔴 Toast lỗi với string `error.response.data.detail` chính xác |
| 401 Unauthorized | Auto-refresh flow | 🟡 Nếu sau refresh vẫn lỗi: toast "Phiên hết hạn" |
| 403 Forbidden | Bất kỳ | 🔴 Toast "Bạn không có quyền thực hiện hành động này" |
| 404 Not Found | GET | 🔴 Redirect đến `/404` hoặc hiển thị empty state |
| 422 Validation Error | POST/PUT | 🔴 Toast chuỗi `detail` từ BE (thường là mảng lỗi Pydantic) |
| 500 Server Error | Bất kỳ | 🔴 Toast lỗi chung + log console.error |

**Checklist:**
```
☐ Dự án có cài thư viện toast chưa? (react-hot-toast, react-toastify, sonner...)
☐ Mỗi service call trong FE có try/catch và gọi toast trong catch block không?
☐ 422 Pydantic error: detail thường là array — FE có join và hiển thị đúng không?
☐ Loading state (isLoading) được set true khi bắt đầu call và false sau khi xong (thành công hoặc lỗi)?
```

---

## Thứ Tự Thực Hiện Kiểm Tra

> [!IMPORTANT]
> Theo thứ tự từ tầng nền tảng đến tính năng cao cấp:

```
Phase 1 (Nền tảng)   → Nhóm 1: Auth + API Layer + RBAC
Phase 2 (Core Flow)   → Nhóm 3: Course Discovery & Enrollment
Phase 3 (Learning)    → Nhóm 4: Learning + Quiz + Progress  
Phase 4 (AI Features) → Nhóm 2: Assessment + Nhóm 6: Chat
Phase 5 (Mgmt)        → Nhóm 5: Personal Courses + Nhóm 8: Classes  
Phase 6 (Analytics)   → Nhóm 7: Dashboard + Nhóm 9: Search
Phase 7 (Admin)       → Nhóm 10: Admin Management
```

---

## Output Mong Đợi Sau Mỗi Kiểm Tra

### Format PASS
```
✅ PASS | [Method] [Endpoint]
Ghi chú: (Tình trạng mapping chính xác, hoặc điểm đặc biệt cần lưu ý)
```

### Format WARN
```
⚠️ WARN | [Method] [Endpoint]
Vấn đề tiềm ẩn: (Mô tả vấn đề có thể gây bug trong tương lai)
Đề xuất: (Hành động nên làm dù chưa bắt buộc)
```

### Format FAIL — Chuẩn AI-Executable

```
❌ FAIL | [Method] [Endpoint]

Tình trạng FE hiện tại:
  (Mô tả chi tiết FE đang làm gì sai — ví dụ: đang gửi field `password_confirm`
   nhưng BE không yêu cầu field này)

Sự thật từ BE Schema:
  (Dẫn chứng trực tiếp từ Pydantic schema — ví dụ: Class RegisterRequest chỉ có
   fields: full_name, email, password. Không có password_confirm.)

Tác động:
  (Hậu quả thực tế — ví dụ: BE trả về HTTP 422 Unprocessable Entity, user
   không đăng ký được dù nhập đúng thông tin)

Vị trí cần sửa:
  - File: src/services/authService.js (dòng XX)
  - File: src/pages/auth/RegisterPage.jsx (dòng YY — loại bỏ field thừa)

Mã nguồn đề xuất:
```js
// TRƯỚC (sai)
const payload = { full_name, email, password, password_confirm };

// SAU (đúng theo BE schema)
const payload = { full_name, email, password };
```
```

---

> [!NOTE]
> Kết quả tổng hợp sau mỗi phase sẽ được ghi vào `task.md`. Các sửa đổi phát hiện ra sẽ được thực thi trực tiếp lên file FE source code, không đặt câu hỏi lại trừ khi có ambiguity nghiêm trọng về business logic.



Kế Hoạch Kiểm Tra Backend Toàn Diện: API Logic, Validation, Error Handling, Business Rules
Audit chuyên sâu Backend — tập trung kiểm tra logic nghiệp vụ, error handling, validation, RBAC enforcement, DB queries, và đảm bảo mọi luồng hoạt động chính xác khi FE gọi vào.

IMPORTANT

Nguyên tắc: Đọc Router → Controller → Service → Model theo chuỗi. Phát hiện lỗi → sửa ngay. Không sửa FE trừ khi BE thay đổi schema.

Phương Pháp Kiểm Tra
Mỗi nhóm chức năng sẽ được kiểm tra theo các trục:

Validation — Pydantic schemas validate đúng không? Edge cases (empty strings, negative numbers, invalid UUIDs)?
RBAC — Mỗi endpoint có check role đúng không? Admin-only endpoints có guard không?
Error Handling — Try/catch trong controller/service đầy đủ không? HTTPException đúng status code?
Business Logic — Luồng logic đúng không? Race conditions? Side effects?
DB Operations — Queries tối ưu? Index được dùng? Data integrity?
Edge Cases — Null handling, empty arrays, duplicate operations?
Format báo cáo
❌ BUG | [Severity: Critical/High/Medium/Low] | [File] [Line]
Mô tả: ...
Tác động: ...
Fix đề xuất: ...
⚠️ WARN | [File] [Line]
Vấn đề: ...
Đề xuất: ...
✅ PASS | [Component]
Ghi chú: ...
User Review Required
IMPORTANT

Kế hoạch này rất lớn (15 services, 15 controllers, 16 routers, 15 schemas). Đề xuất thực hiện theo phases, sau mỗi phase báo cáo + sửa lỗi trước khi đi tiếp.

WARNING

Phạm vi sửa: Chỉ sửa BE code. Nếu fix BE thay đổi response schema → cập nhật FE service tương ứng để đồng bộ.

Danh Sách Kiểm Tra Theo Phase
🔐 PHASE 1: Nền Tảng — Auth, Security, Middleware, Config
Mục tiêu: Đảm bảo xương sống hệ thống vững chắc.

#	File	Kiểm tra	Ưu tiên
1.1	config/config.py	Env vars load đúng, defaults hợp lý, sensitive values required	🔴
1.2	app/main.py + app/database.py	CORS config, lifespan, Beanie init đúng models	🔴
1.3	utils/security.py	hash_password, verify_password, create_access_token, create_refresh_token, decode_token — edge cases	🔴
1.4	middleware/auth.py	get_current_user — token validation flow, error messages chuẩn	🔴
1.5	middleware/rbac.py	Role hierarchy, permission sets đầy đủ, require_role async function bug check	🔴
1.6	services/auth_service.py	Duplicate hash_password/verify_password vs utils, authenticate_user status check, refresh token flow	🔴
1.7	controllers/auth_controller.py	Register validation, login response format, refresh flow, logout	🔴
1.8	routers/auth_router.py	Endpoint definitions, status codes	🟡
1.9	schemas/auth.py	Field validation rules (email, password min length, remember_me)	🔴
Điểm kiểm tra đặc biệt Phase 1:

rbac.py line 87-111 và line 244-284 — CÓ HAI require_role functions (1 trong auth.py, 1 trong rbac.py) → conflict?
check_enrollment_access (rbac.py line 390-409) trả return True — STUB chưa implement
auth_service.py duplicate hash_password/verify_password với utils/security.py — dùng cái nào?
authenticate_user trả None khi status != "active" nhưng KHÔNG phân biệt "inactive" vs "suspended" cho FE
Refresh token lưu raw JWT vào DB thay vì hash — security concern?
📚 PHASE 2: Course & Enrollment — Core Business Logic
Mục tiêu: Luồng khám phá → đăng ký → học tập phải hoạt động chính xác.

#	File	Kiểm tra	Ưu tiên
2.1	schemas/course.py	Course create/update validation, enum values	🔴
2.2	services/course_service.py (28KB)	Search logic, public listing, detail with enrollment info, pagination	🔴
2.3	controllers/course_controller.py (23KB)	Error handling, response mapping	🔴
2.4	routers/courses_router.py	URL conflicts (/courses/search vs /courses/{course_id})	🔴
2.5	schemas/enrollment.py	Enrollment create/cancel validation	🟡
2.6	services/enrollment_service.py (14KB)	Duplicate enrollment prevention, cancel logic, progress cleanup	🔴
2.7	controllers/enrollment_controller.py (14KB)	Ownership check (student can only see own enrollments)	🔴
2.8	routers/enrollments_router.py	RBAC guards on all endpoints	🟡
Điểm kiểm tra đặc biệt Phase 2:

Course search vs public listing — logic khác nhau thế nào?
Enrollment count on Course document — có được increment/decrement atomically không?
Cancel enrollment → có cleanup Progress document không?
URL conflict: /courses/search, /courses/public, /courses/from-prompt, /courses/personal, /courses/my-personal vs /courses/{course_id} — router priority đúng không?
🎓 PHASE 3: Learning, Quiz & Progress — Complex Business Logic
Mục tiêu: Luồng lesson → quiz → progress → unlock phải đúng.

#	File	Kiểm tra	Ưu tiên
3.1	schemas/learning.py (14KB)	Module/Lesson response schemas	🟡
3.2	services/learning_service.py (26KB)	Module detail, lesson content, navigation, unlock logic	🔴
3.3	controllers/learning_controller.py (19KB)	Enrollment check before lesson access	🔴
3.4	schemas/quiz.py (9KB)	Quiz create/attempt/results validation	🔴
3.5	services/quiz_service.py (39KB)	Attempt logic, scoring, max_attempts, passing_score, retake, mandatory questions	🔴
3.6	controllers/quiz_controller.py (35KB)	Instructor ownership check, student enrollment check	🔴
3.7	schemas/progress.py	Progress response schema	🟡
3.8	services/learning_service.py	Lesson completion → progress update → unlock next lesson logic	🔴
Điểm kiểm tra đặc biệt Phase 3:

Quiz attempt: kiểm tra max_attempts enforcement
Quiz scoring: mandatory_questions phải đúng 100% mới pass — logic đúng?
Lesson completion → auto-update Progress document → auto-unlock next lesson chain
Quiz retake: reset attempt_number hay increment?
Instructor create quiz: validate course_id ownership?
Class-results: chỉ instructor thấy kết quả class mình dạy?
🤖 PHASE 4: AI Features — Assessment, Chat, Personal Courses, Recommendations
Mục tiêu: AI integration hoạt động đúng, error handling cho Gemini API.

#	File	Kiểm tra	Ưu tiên
4.1	schemas/assessment.py	Generate request, submit answer, results schemas	🔴
4.2	services/assessment_service.py (8KB)	Generate flow, submit + AI evaluate, session expiry	🔴
4.3	services/ai_service.py (63KB!)	Gemini API calls, prompt engineering, error handling, timeout	🔴
4.4	controllers/assessment_controller.py (14KB)	Session ownership check, expiry validation	🔴
4.5	schemas/chat.py (7KB)	Chat message, conversation schemas	🟡
4.6	services/chat_service.py (7KB)	Conversation management, message context, AI response	🔴
4.7	controllers/chat_controller.py (13KB)	Enrollment check for course chat	🔴
4.8	schemas/personal_courses.py (10KB)	From-prompt, create, update schemas	🟡
4.9	services/personal_courses_service.py (15KB)	AI course generation, ownership CRUD	🔴
4.10	services/recommendation_service.py (22KB)	Assessment-based + learning history recommendations	🟡
Điểm kiểm tra đặc biệt Phase 4:

ai_service.py là 63KB! — Cần kiểm tra error handling cho Gemini API failures
Assessment session expiry: BE check expires_at trước khi cho submit?
Chat context: gửi đúng course context cho AI không?
from-prompt AI generation: validate prompt min 20 chars?
Recommendation: session_id required? Timeline logic?
🏫 PHASE 5: Classes, Search, Dashboard, Analytics
Mục tiêu: Feature quản lý và analytics hoạt động đúng.

#	File	Kiểm tra	Ưu tiên
5.1	schemas/classes.py	Create/join/update validation	🟡
5.2	services/class_service.py (28KB)	Join with code, student management, max_students enforcement	🔴
5.3	controllers/class_controller.py (13KB)	Instructor ownership, student enrollment on join	🔴
5.4	schemas/search.py	Search query params, response types	🟡
5.5	services/search_service.py (27KB)	Multi-type search, relevance scoring, guest vs auth access	🔴
5.6	schemas/dashboard.py (14KB)	Student/Instructor/Admin dashboard response structures	🟡
5.7	services/dashboard_service.py (55KB!)	Dashboard data aggregation, chart data, system health	🔴
5.8	controllers/dashboard_controller.py (18KB)	Role-based dashboard routing	🟡
Điểm kiểm tra đặc biệt Phase 5:

Class join: auto-enroll student vào course?
Class max_students: enforce khi join?
Search: guest access (get_optional_user) hoạt động đúng?
Dashboard service 55KB — cần check DB query efficiency
System health metrics: real values hay hardcoded?
🛡️ PHASE 6: Admin & User Management
Mục tiêu: Admin CRUD operations + role change impact analysis.

#	File	Kiểm tra	Ưu tiên
6.1	schemas/admin.py (12KB)	User/Course/Class CRUD schemas	🟡
6.2	services/admin_service.py (37KB)	User CRUD, role change impact, course admin CRUD, class monitoring	🔴
6.3	controllers/admin_controller.py (23KB)	Admin role enforcement on all handlers	🔴
6.4	schemas/user.py (6KB)	Profile update validation	🟡
6.5	services/user_service.py (29KB)	Profile CRUD, email uniqueness, avatar handling	🔴
Điểm kiểm tra đặc biệt Phase 6:

Admin delete user: cascade delete enrollments, progress, conversations?
Admin change role: impact analysis accuracy?
Admin delete course: cascade delete modules, lessons, enrollments, progress?
Email uniqueness enforcement khi admin/user update email?
Admin reset password: response trả new_password về client — bảo mật?
Cross-Cutting Concerns (Kiểm tra xuyên suốt)
Concern	Kiểm tra	Files
Duplicate Code	hash_password/verify_password duplicate giữa auth_service.py và utils/security.py	auth_service, security
Error Response Format	Tất cả HTTPException dùng detail field chuẩn	All controllers
DateTime Consistency	datetime.utcnow() vs datetime.now(timezone.utc) — mixing?	All services
UUID Validation	Path params {user_id}, {course_id} etc có validate UUID format?	All routers
Null Safety	.get() trên optional fields có handle None?	All services
Pagination	skip/limit consistent? total count accurate?	All list endpoints
RBAC Stub	check_enrollment_access trả True hardcoded	rbac.py
Index Coverage	DB queries match declared indexes?	models.py vs services
Thứ Tự Thực Hiện
IMPORTANT

Từ nền tảng lên feature phức tạp:

Phase 1 (Nền tảng)     → Auth, Security, Middleware, Config
Phase 2 (Core)          → Course & Enrollment logic
Phase 3 (Complex)       → Learning, Quiz, Progress chains
Phase 4 (AI)            → Assessment, Chat, Personal Courses
Phase 5 (Features)      → Classes, Search, Dashboard
Phase 6 (Admin)         → Admin CRUD, User management
Verification Plan
Automated Tests
Sau mỗi phase, chạy uvicorn để verify server khởi động không lỗi
Test API endpoints bằng browser subagent nếu cần
Manual Verification
Review console log cho ImportError, DeprecationWarning
Kiểm tra response format bằng Swagger UI (/docs)