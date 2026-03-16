# CHECKLIST MAPPING BE → FE (Cập nhật: 2026-03-10)

> File này dùng để track tiến độ mapping chính xác từ BE → FE.
> Mỗi phiên làm việc, đọc file này trước để biết task nào đang dở.
> Luôn đối chiếu với `BE_TO_FE_MAPPING.md` và code BE thực tế trong `BELEARNINGAI/schemas/`.

---

## QUY TẮC MAPPING

### Trước khi code page/component:
1. ✅ Đọc endpoint tương ứng trong `BE_TO_FE_MAPPING.md`
2. ✅ Đọc Pydantic schema thực tế trong `BELEARNINGAI/schemas/<module>.py`
3. ✅ So sánh field names — **ưu tiên BE thực tế** nếu có khác biệt
4. ✅ Kiểm tra nullable fields → dùng `?.` optional chaining
5. ✅ Kiểm tra status values → dùng đúng format (`in-progress` hyphen)

### Khi code xong:
1. ✅ Build pass (`npx vite build` → 0 errors)
2. ✅ Đánh dấu page trong checklist bên dưới
3. ✅ Ghi chú nếu có khác biệt BE/FE

---

## ⚠️ FIELD NAME CẢNH BÁO (đã phát hiện qua audit)

| BE Schema | BE Field | FE thường nhầm thành | Đúng |
|-----------|----------|---------------------|------|
| `auth.LoginResponse` | `user.avatar` | `user.avatar_url` | `user.avatar` → map sang `avatar_url` khi lưu store |
| `auth.RegisterRequest` | ❌ không có `role` | gửi `role` | KHÔNG gửi role, BE mặc định `student` |
| `auth.RegisterResponse` | `id` | `user_id` | `id` |
| `admin.AdminUserListItem` | `user_id` | `id` | `user_id` |
| `admin.AdminUserListItem` | `avatar` | `avatar_url` | `avatar` (không có `_url`) |
| `dashboard.UsersByRole` | `student, instructor, admin` | `students, instructors, admins` | SỐ ÍT (không có "s") |
| `enrollment.EnrollmentListItem` | status `in-progress` | `in_progress` | Hyphen `-` không phải underscore |
| `enrollment.EnrollmentListItem` | `id` | `enrollment_id` | `id` |
| `enrollment.EnrollmentSummary` | `total_enrollments` | `total` | `total_enrollments` |
| `enrollment.NextLessonInfo` | `lesson_title` | `title` | `lesson_title` |
| `classes.ClassListItem` | `student_count: str` | `student_count: int` | String format `"25/30"` |

---

## CHECKLIST PAGES (33 pages)

### Auth Pages
- [x] LoginPage — `POST /auth/login` → `LoginResponse`
  - ⚠️ `user.avatar` → map sang `avatar_url` khi lưu authStore
  - ⚠️ Gửi `remember_me` checkbox (ảnh hưởng refresh token TTL)
- [x] RegisterPage — `POST /auth/register` → `RegisterResponse`
  - ⚠️ KHÔNG gửi `role`. Response có `id` (không phải `user_id`), `status`, `created_at`
- [x] ForgotPasswordPage — `POST /auth/forgot-password`
- [x] ResetPasswordPage — `POST /auth/reset-password`
- [x] VerifyEmailPage — `GET /auth/verify-email`

### Profile
- [x] ProfilePage — `GET /users/me` + `PATCH /users/me`
  - ✅ `contact_info` = `str` (không phải object)
  - ✅ `learning_preferences` = `List[str]`
  - ✅ `bio` max 500, `full_name` ≥ 2 từ

### Assessment
- [x] AssessmentSetupPage — `POST /assessments/generate`
- [x] AssessmentQuizPage — `POST /assessments/{id}/submit`
  - ⚠️ Phải gửi `total_time_seconds` và `submitted_at`
- [x] AssessmentResultsPage — `GET /assessments/{id}/results`

### Courses
- [x] CoursesPage — `GET /courses/search`
  - ⚠️ Response có `avg_rating`, `created_at` (thêm vào card)
- [x] CourseDetailPage — `GET /courses/{id}`
  - ⚠️ `owner_info` có `id`, `role`, `experience_years`
  - ⚠️ Có `preview_video_url`, `status`, `updated_at`

### Enrollment
- [x] MyCoursesPage — `GET /enrollments/my-courses`
  - ⚠️ Status = `in-progress` (hyphen!)
  - ⚠️ `enrollments[].id` (không phải `enrollment_id`)
  - ⚠️ `next_lesson.lesson_title` (không phải `title`)
  - ⚠️ `summary.total_enrollments` (không phải `total`)

### Learning
- [x] ModuleListPage — `GET /courses/{id}/modules`
- [x] ModuleDetailPage — `GET /courses/{id}/modules/{id}`
- [x] LessonPage — `GET /courses/{id}/lessons/{id}`
  - ⚠️ `navigation`, `quiz_info`, `completion_status` là nested Dict

### Quiz
- [x] QuizPage (List) — `GET /quizzes`
  - ⚠️ Có thêm `description`, `class_id`, `class_name`, `pass_count`, `updated_at`
- [x] QuizDetailPage — `GET /quizzes/{id}`
- [x] QuizAttemptPage — `POST /quizzes/{id}/attempt`
  - ⚠️ Response có `attempt_number`, `submitted_at`
- [x] QuizResultsPage — `GET /quizzes/{id}/results`
  - ⚠️ Có `mandatory_passed`, `can_retake`, `is_mandatory` per question

### Chat
- [x] ChatPage — chatService (5 methods)
  - ⚠️ `related_lessons[]` trong message response
  - ⚠️ `grouped_by_date{today[], yesterday[], this_week[], older[]}` trong history
  - ⚠️ `last_updated`, `created_at` trong conversation list

### Personal Courses
- [x] PersonalCoursesPage — personalCourseService

### Classes
- [x] ClassListPage — `GET /classes/my-classes`
  - ⚠️ `student_count` là `str` "25/30" (không phải int)
- [x] ClassCreatePage — `POST /classes`
- [x] ClassDetailPage — `GET /classes/{id}`
  - ⚠️ `course.module_count`, `max_students`, `student_count` (int)

### Dashboard
- [x] DashboardPage (Student) — `GET /dashboard/student`
  - ✅ `overview.total_lessons_completed`, `performance_summary.average_quiz_score`
- [x] DashboardPage (Instructor) — `GET /dashboard/instructor`
  - ✅ `quick_actions[]{action_type, label, link, icon}`
- [x] DashboardPage (Admin) — `GET /dashboard/admin`
  - ⚠️ `users_by_role.student` (SỐ ÍT!) — ĐÃ FIX
  - ⚠️ Có `last_updated` field

### Search & Other
- [x] SearchResultsPage — `GET /search`
- [x] RecommendationsPage — `GET /recommendations`
- [x] ProgressPage — `GET /progress/course/{id}`

### Admin
- [x] AdminPage — adminService + analyticsService
  - ⚠️ Users: `user_id` (không phải `id`), `avatar` (không phải `avatar_url`) — ĐÃ FIX
  - ⚠️ Có thêm `last_login_at`, `courses_enrolled`, `classes_created`

### Static Pages
- [x] LandingPage — không cần API
- [x] NotFoundPage — không cần API
- [x] UnauthorizedPage — không cần API

---

## COMPONENTS CHƯA HOÀN THÀNH

| # | Component | Endpoint | Ưu tiên | Status |
|---|-----------|----------|---------|--------|
| 1 | JoinClassModal | `POST /classes/join` | TRUNG BÌNH | ⬜ Chưa làm |
| 2 | GlobalSearchBar | `GET /search/suggestions` | TRUNG BÌNH | ⬜ Chưa làm |
| 3 | CourseEditorPage | `PUT /courses/personal/{id}` | THẤP | ⬜ Chưa làm |

---

## TỔNG KẾT (CẬP NHẬT SAU AUDIT CODE THỰC TẾ — 2026-03-10)

> ⚠️ **Checklist trên đánh dấu ✅ ở mức docs, nhưng audit code thực tế phát hiện 38 vấn đề**
> Xem chi tiết: `FE_FIX_PLAN.md`

| Hạng mục | Status |
|----------|--------|
| Services | 17/17 tạo xong, 3 chưa kết nối (Auth fake API) |
| Stores | 3/3, authStore.login thiếu param `remember_me` |
| Routes | 14/14 ✅ |
| Pages mapping đúng BE | **11/34 OK** — 23 pages cần sửa |
| Vấn đề Critical (crash) | 7 (MyCoursesPage 3, Login/Auth 3, ClassDetail 1) |
| Vấn đề Fake API | 3 (ForgotPassword, ResetPassword, VerifyEmail) |
| Vấn đề thiếu fields | 11 pages |
| Vi phạm coding rules (inline CSS) | 9 pages thiếu CSS file |
| UI text không dấu tiếng Việt | 6 pages |
| Validation sai | 3 pages |
| Components chưa có | 3 (JoinClassModal, GlobalSearchBar, CourseEditorPage) |
| Build | ✅ 458 modules, 0 errors |
| **Tổng vấn đề cần fix** | **38 + 3 new components** |
