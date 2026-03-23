# 🔧 PLAN SỬA FE THEO BE SCHEMA (2026-03-10)

> **Kết quả rà soát: 34/34 pages + 17 services + 3 stores**
> **Tổng: 38 vấn đề** phân loại 7 nhóm ưu tiên
> Tuân thủ: `BE_TO_FE_MAPPING.md`, `FE_CODING_RULES.md`, workflow `/fe-mapping`

---

## PHASE 1: 🔴 CRITICAL — Sai field name / logic sai (7 tasks)
> Ưu tiên CAO NHẤT — gây crash hoặc hiển thị sai

### Task 1.1: MyCoursesPage — Status `'active'` → `'in-progress'`
- **File**: `pages/enrollment/MyCoursesPage.jsx` lines 126, 146, 162
- **Docs ref**: `BE_TO_FE_MAPPING.md` line 244 — `status: Literal["in-progress","completed","cancelled"]`
- **Sửa**: Đổi tất cả `=== 'active'` → `=== 'in-progress'`
- **Hậu quả nếu không sửa**: Tất cả card "Đang học" KHÔNG hiển thị nút "Tiếp tục" và thanh progress

### Task 1.2: MyCoursesPage — `enrollment.enrollment_id` → `enrollment.id`
- **File**: `pages/enrollment/MyCoursesPage.jsx` lines 49, 106, 183
- **Docs ref**: `FE_MAPPING_CHECKLIST.md` line 36 — "enrollment.id (không phải enrollment_id)"
- **Sửa**: `enrollment.enrollment_id` → `enrollment.id` (hoặc fallback `enrollment.id || enrollment.enrollment_id`)
- **Hậu quả nếu không sửa**: key prop = `undefined`, cancel enrollment gửi `undefined`

### Task 1.3: MyCoursesPage — `summary.total` → `summary.total_enrollments`
- **File**: `pages/enrollment/MyCoursesPage.jsx` line 68
- **Docs ref**: `FE_MAPPING_CHECKLIST.md` line 37 — "`total_enrollments` (không phải `total`)"
- **Sửa**: `summary?.total` → `summary?.total_enrollments`

### Task 1.4: LoginPage — Thêm `remember_me` checkbox
- **File**: `pages/auth/LoginPage.jsx`
- **Docs ref**: `BE_TO_FE_MAPPING.md` line 47 — `remember_me: bool, optional, default false`
- **Sửa**: Thêm checkbox, truyền xuống authStore.login()

### Task 1.5: authService.login — Thêm `remember_me` param
- **File**: `services/authService.js` line 17
- **Docs ref**: `BE_TO_FE_MAPPING.md` line 47
- **Sửa**: `api.post('/auth/login', { email, password, remember_me })`

### Task 1.6: authStore.login — Nhận thêm `remember_me`
- **File**: `stores/authStore.js` line 22
- **Sửa**: `login: async (email, password, rememberMe = false)` → pass cho authService

### Task 1.7: ClassDetailPage — student_count format
- **File**: `pages/classes/ClassDetailPage.jsx` line 82
- **Docs ref**: `FE_MAPPING_CHECKLIST.md` line 39 — "student_count: str format '25/30'"
- **Vấn đề**: Code hiện: `{classData.student_count}/{classData.max_students || '∞'}` → nếu BE trả "25/30" thì hiển thị "25/30/∞"
- **Sửa**: Chỉ dùng `{classData.student_count}` (đã là string formatted)

---

## PHASE 2: 🟠 FAKE API → Real service (3 tasks)
> Quan trọng — 3 pages Auth đang giả lập API

### Task 2.1: ForgotPasswordPage — Kết nối real authService
- **File**: `pages/auth/ForgotPasswordPage.jsx` lines 28-32
- **Sửa**: Bỏ `setTimeout`, dùng `await authService.forgotPassword(data.email)`
- **Import**: Thêm `import authService from '@services/authService'`

### Task 2.2: ResetPasswordPage — Kết nối real authService
- **File**: `pages/auth/ResetPasswordPage.jsx` lines 37-44
- **Sửa**: Bỏ `setTimeout`, dùng `await authService.resetPassword(token, data.password)`
- **Import**: Thêm `import authService from '@services/authService'`

### Task 2.3: VerifyEmailPage — Kết nối real authService
- **File**: `pages/auth/VerifyEmailPage.jsx` lines 28-32, 55-59
- **Sửa**: 2 chỗ:
  - Verify: `await authService.verifyEmail(token)`
  - Resend: `await authService.resendVerificationEmail(email)`
- **Import**: Thêm `import authService from '@services/authService'`

---

## PHASE 3: 🟡 THIẾU FIELDS — Bổ sung data vào UI (11 tasks)

### Task 3.1: CoursesPage — Thêm `avg_rating` ⭐
- **File**: `pages/courses/CoursesPage.jsx`
- **Docs ref**: `BE_TO_FE_MAPPING.md` line 69 — "Response có `avg_rating`"
- **Sửa**: Thêm star rating hiển thị trong course card footer

### Task 3.2: CourseDetailPage — Thêm `preview_video_url`
- **File**: `pages/courses/CourseDetailPage.jsx`
- **Docs ref**: `BE_TO_FE_MAPPING.md` line 72 — "Có `preview_video_url`"
- **Sửa**: Hiển thị nút "Xem video giới thiệu" nếu field tồn tại

### Task 3.3: MyCoursesPage — Thêm nhiều fields
- **File**: `pages/enrollment/MyCoursesPage.jsx`
- **Thiếu**: `course_description`, `course_level`, `instructor_name`, `completed_at`, `next_lesson.lesson_title`, `next_lesson.module_title`
- **Sửa**: Bổ sung vào card enrollment

### Task 3.4: ChatPage — Thêm `related_lessons[]`
- **File**: `pages/chat/ChatPage.jsx`
- **Docs ref**: `FE_MAPPING_CHECKLIST.md` line 98
- **Sửa**: Render danh sách bài học liên quan dưới sources trong AI message

### Task 3.5: ChatPage — Thêm `grouped_by_date` sidebar
- **File**: `pages/chat/ChatPage.jsx`
- **Docs ref**: `FE_MAPPING_CHECKLIST.md` line 99
- **Sửa**: Nhóm conversations theo "Hôm nay", "Hôm qua", "Tuần này", "Cũ hơn"

### Task 3.6: QuizPage — Thêm fields `description, class_name, pass_count`
- **File**: `pages/quiz/QuizPage.jsx`
- **Docs ref**: `FE_MAPPING_CHECKLIST.md` line 89
- **Sửa**: Hiển thị trên quiz card

### Task 3.7: QuizDetailPage — Thêm `max_attempts, is_retakeable`
- **File**: `pages/quiz/QuizDetailPage.jsx`
- **Sửa**: Hiển thị trong thông tin quiz

### Task 3.8: RecommendationsPage — Thêm `match_score, difficulty`
- **File**: `pages/recommendations/RecommendationsPage.jsx`
- **Sửa**: Hiển thị match score %, difficulty badge

### Task 3.9: ✅ SearchResultsPage — Thêm pagination + metadata (DONE 2026-03-19)
- **File**: `pages/search/SearchResultsPage.jsx`
- **Sửa**: Viết lại hoàn toàn mapping đúng BE SearchResponse schema (results_by_category, total_results, search_time_ms, suggestions, filters_applied). Thêm pagination, filter sidebar, category groups.

### Task 3.10: ProgressPage — Render chart data
- **File**: `pages/progress/ProgressPage.jsx`
- **Vấn đề**: Gọi `getProgressChart()` nhưng không dùng data
- **Sửa**: Thêm Recharts `LineChart` render weekly progress

### Task 3.11: enrollmentService.js — Sửa comment status
- **File**: `services/enrollmentService.js` line 27
- **Sửa**: Comment `active|completed|cancelled` → `in-progress|completed|cancelled`

---

## PHASE 4: 🔵 INLINE STYLES → CSS FILES (10 tasks)
> Theo `FE_CODING_RULES.md`: dùng CSS file + BEM naming, KHÔNG inline styles

### Task 4.1-4.3: Classes pages (3 files)
- Tạo `ClassListPage.css`, `ClassCreatePage.css`, `ClassDetailPage.css`
- Chuyển toàn bộ inline styles sang CSS classes theo BEM

### Task 4.4-4.5: Quiz pages (2 files)
- Tạo `QuizAttemptPage.css`, `QuizResultsPage.css`
- Chuyển inline styles sang CSS

### Task 4.6: ModuleDetailPage
- Tạo `ModuleDetailPage.css`
- Chuyển inline styles sang CSS

### Task 4.7: PersonalCoursesPage
- Tạo `PersonalCoursesPage.css`
- Chuyển inline styles sang CSS

### Task 4.8: RecommendationsPage
- Tạo `RecommendationsPage.css`
- Chuyển inline styles sang CSS

### Task 4.9: ✅ SearchResultsPage (DONE 2026-03-19)
- Tạo `SearchResultsPage.css` — BEM naming, mobile-first, CSS variables
- Chuyển toàn bộ inline styles sang CSS

### Task 4.10: ModuleListPage — Partial fix
- Chuyển loading/empty state inline styles sang CSS

---

## PHASE 5: 🟣 UI TEXT CÓ DẤU (6 tasks)
> Theo `FE_CODING_RULES.md`: Comment không dấu OK, nhưng **text hiển thị cho user phải CÓ DẤU**

### Task 5.1: AssessmentSetupPage.jsx
- "Buoc 1" → "Bước 1", "Chon linh vuc" → "Chọn lĩnh vực", "Bat dau danh gia" → "Bắt đầu đánh giá"...

### Task 5.2: AssessmentQuizPage.jsx
- "Cau truoc" → "Câu trước", "Cau tiep" → "Câu tiếp", "Nop bai" → "Nộp bài", "diem" → "điểm"...

### Task 5.3: AssessmentResultsPage.jsx
- "Ket qua danh gia" → "Kết quả đánh giá", "Phan tich ky nang" → "Phân tích kỹ năng"...

### Task 5.4: LessonPage.jsx
- "Khoa hoc" → "Khóa học", "phut" → "phút", "Da hoan thanh" → "Đã hoàn thành"...

### Task 5.5: ModuleListPage.jsx + ModuleDetailPage.jsx
- "Noi dung khoa hoc" → "Nội dung khóa học", "bai hoc" → "bài học"...

### Task 5.6: QuizAttemptPage.jsx + QuizResultsPage.jsx
- "Bat buoc" → "Bắt buộc", "Cau truoc" → "Câu trước", "Dap an dung" → "Đáp án đúng"...

---

## PHASE 6: 🔵 VALIDATION FIX (3 tasks)

### Task 6.1: RegisterPage — `full_name` validation
- **Hiện tại**: `minLength: 2` (ký tự)
- **BE yêu cầu**: ≥2 từ + min 3, max 100 ký tự
- **Sửa**: Thêm custom validate `value.trim().split(/\s+/).length >= 2`

### Task 6.2: RegisterPage — Password strength indicator
- **Hiện tại**: Chỉ check `minLength: 8`
- **BE yêu cầu**: digit + uppercase + special char `!@#$%^&*()_+-=[]{}|;:,.<>?`
- **Sửa**: Thêm 3 rule checks + visual indicator

### Task 6.3: ResetPasswordPage — Password minLength
- **Hiện tại**: `minLength: 6`
- **BE yêu cầu**: `minLength: 8` + digit + uppercase + special char
- **Sửa**: Đổi 6 → 8 + thêm pattern validation giống RegisterPage

---

## PHASE 7: ⬜ COMPONENTS MỚI (3 tasks)

### Task 7.1: JoinClassModal
- **API**: `POST /classes/join` body: `{ invite_code: str }`
- **Response**: `{ message, class_info{id, name, course_title, instructor_name} }`
- **UI**: Modal nhỏ, input mã mời + nút xác nhận

### Task 7.2: GlobalSearchBar
- **API**: `GET /search/suggestions?q=...&limit=5`
- **Response**: `{ suggestions: [{ title, type, id }] }`
- **UI**: Search bar trong DashboardLayout header, autocomplete dropdown

### Task 7.3: CourseEditorPage
- **API**: `PUT /courses/personal/{id}` + `DELETE /courses/personal/{id}`
- **UI**: Form editor cho personal courses, nested modules→lessons

---

## QUY TẮC KHI THỰC HIỆN (theo docs)

### Checklist mỗi task (từ `/fe-mapping` workflow):
- [ ] Đọc endpoint trong `BE_TO_FE_MAPPING.md`
- [ ] Check schema BE thực tế nếu cần
- [ ] Field names **KHỚP** BE schema
- [ ] Nullable fields dùng `?.` optional chaining
- [ ] Status values đúng format (`in-progress` hyphen)
- [ ] Toast dùng `response.message` từ BE
- [ ] CSS: BEM naming, mobile-first, KHÔNG inline styles
- [ ] Comment tiếng Việt không dấu, UI text CÓ DẤU
- [ ] Build pass `npx vite build` → 0 errors

### Không được phép:
- ❌ Cài thêm package
- ❌ Dùng TailwindCSS
- ❌ Dùng icon library
- ❌ Inline styles (trừ dynamic width/color)

---

## THỜI GIAN ƯỚC TÍNH

| Phase | Tasks | Thời gian |
|-------|-------|-----------|
| 1. Critical fixes | 7 | ~40 phút |
| 2. Fake API → Real | 3 | ~20 phút |
| 3. Thiếu fields | 11 | ~1.5 giờ |
| 4. CSS refactor | 10 | ~2 giờ |
| 5. UI text có dấu | 6 | ~30 phút |
| 6. Validation | 3 | ~20 phút |
| 7. New components | 3 | ~2-3 giờ |
| **TỔNG** | **43** | **~7-8 giờ** |

---

## TIẾN ĐỘ THỰC HIỆN

| Phase | Status |
|-------|--------|
| Phase 1 | ✅ Done (2026-03-10 13:20) — 7/7 critical fixes |
| Phase 2 | ✅ Done (2026-03-10 13:22) — 3/3 fake API → real |
| Phase 3 | 🔄 Đang thực hiện |
| Phase 4 | ⬜ Chưa bắt đầu |
| Phase 5 | ⬜ Chưa bắt đầu |
| Phase 6 | ⬜ Chưa bắt đầu |
| Phase 7 | ⬜ Chưa bắt đầu |
