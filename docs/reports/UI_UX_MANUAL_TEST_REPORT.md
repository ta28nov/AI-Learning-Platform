# UI/UX Manual Test Report

**Ngày:** 2026-05-19  
**Plan:** [`ui_ux_full_qa_73509397.plan.md`](../../.cursor/plans/ui_ux_full_qa_73509397.plan.md)  
**DB:** `ai_learning_app` | **FE:** http://localhost:3000 | **BE:** http://127.0.0.1:8000

---

## Phase 0 — Pre-flight

| Kiểm tra | Kết quả |
|----------|---------|
| Health | PASS |
| DB counts | users 411, courses 150, enrollments 6095, classes 98, lessons 4120, quizzes 2929, modules 740 |

---

## Phase 1 — Authentication

**Trạng thái:** Hoàn thành (trừ verify-email / reset-password cần token DB).

| Case | Kết quả |
|------|---------|
| Login 3 role, logout, guards, OAuth toast, register/forgot/terms UI | PASS |

---

## Phase 2 — Data & UI validation (đầy đủ)

**Phương pháp:** So khớp MongoDB → API (curl/script `BE/scripts/phase2_data_audit.py`) → UI field usage (grep FE) → smoke browser `localhost:3000`.

**Mẫu chính:** Course `Bootcamp Business 3` (`6cec7c81-6ff4-425e-84c8-de3238e0b5a2`), student `student1@gmail.com`, instructor `instructor1@ailearning.vn`, admin `admin1@ailearning.vn`.

---

### 2.1 Course / catalog / detail (Student)

| Field / feature | DB | API | UI | Kết quả | Ghi chú |
|-----------------|----|-----|-----|---------|---------|
| `title`, `description` | ✓ | ✓ `GET /courses/{id}` | CourseDetailPage | **PASS** | |
| `level`, `category` | ✓ | ✓ | Metadata hero | **PASS** | |
| `thumbnail_url` | ✓ | ✓ | Card + hero | **PASS** | |
| `preview_video_url` | ✓ | ✓ | Nút "Xem video giới thiệu" | **PASS** | |
| `language`, `status` | ✓ | ✓ | — | **PASS** | Không highlight riêng |
| `learning_outcomes` | ✓ | ✓ | "Bạn sẽ học được gì" | **PASS** | |
| `prerequisites` | ✓ | ✓ | Section Yêu cầu | **PASS** | |
| `modules` + lessons (embedded) | ✓ | ✓ (6 modules) | Accordion + tiến độ lesson | **PASS** | Progress từ `enrollment_info` + lesson flags |
| `enrollment_info.progress_percent` | ✓ (55.1%) | ✓ | Hero + dashboard card | **PASS** | Khớp dashboard |
| `owner_info` (instructor) | `instructor_id` | ✓ `name`, `avatar_url`; `bio`/`experience_years` null | Section Giảng viên | **PARTIAL** | UI ẩn bio/exp khi null — OK |
| **`avg_rating`** | **4.6** | ✓ search + ✓ `course_statistics.avg_rating` detail | Catalog + CourseDetailPage hero (★) | **PASS** | **UIUX-002 FIXED** 2026-05-19 |
| `enrollment_count`, `instructor_name`, stats | ✓ | ✓ search only | Catalog card footer | **PASS** catalog / **N/A** detail |
| `is_enrolled` (catalog) | ✓ | ✓ search | Badge trên card (nếu có) | **PASS** | |
| Unenrolled `enrollment_info.is_enrolled` | — | `false` (Complete Math 1) | Nút đăng ký | **PASS** | |
| Comments / reviews CRUD | — | — | — | **N/A** | By design |

**API paths thực tế:** Catalog dùng `GET /api/v1/courses/search` (không phải `GET /courses?page=`).

---

### 2.2 Module / lesson (Student)

| Field / feature | DB | API | UI | Kết quả | Ghi chú |
|-----------------|----|-----|-----|---------|---------|
| Module list trong course detail | ✓ | ✓ embedded | CourseDetailPage | **PASS** | |
| Lesson list + completion trong course | ✓ | ✓ embedded | "Tiến độ học tập" | **PASS** | Hoàn thành / Chưa bắt đầu |
| `GET /courses/{cid}/lessons/{lid}` | ✓ | ✓ **200** | LessonPage | **PASS** | **UIUX-007 FIXED** — `LessonProgressItem` dùng attribute, không `.get()` |
| `text_content`, `video_info`, `attachments` | ✓ | ✓ | LessonPage | **PASS** | Browser: title, nội dung, đính kèm, nav, AI chat |
| `quiz_info` trên lesson | ✓ | ✓ embedded | LessonPage «Làm quiz» | **PASS** | 2b.3 browser: Quiz 6 câu, badge Bắt buộc |

**Mẫu lesson:** `93d2684b-d82a-4a62-aa2d-2af068fe0e99` (Module 1, Bootcamp Business 3).

---

### 2.3 Quiz (Student)

| Field / feature | DB | API `GET /quizzes/{id}` | UI | Kết quả | Ghi chú |
|-----------------|----|-------------------------|-----|---------|---------|
| `title`, `description` | ✓ | ✓ | QuizPage / QuizDetailPage | **PASS** | |
| `question_count` | ✓ (9 câu) | ✓ | QuizPage stat | **PASS** | |
| `time_limit`, `pass_threshold` | ✓ | ✓ (mapped từ `passing_score`) | QuizDetailPage | **PASS** | |
| **`questions[]`** | ✓ embedded | ✓ (sanitized, no answers) | QuizAttemptPage | **PASS** | **UIUX-008 FIXED** |
| Attempt / results | ✓ | `POST /quizzes/{id}/attempt` | QuizAttemptPage | **PASS** (UI) | Câu hỏi + đáp án A/B/C/D hiển thị; chưa nộp bài E2E |

---

### 2.4 Classes (Student + Instructor)

| Field / feature | DB | API | UI | Kết quả | Ghi chú |
|-----------------|----|-----|-----|---------|---------|
| Student `GET /classes/my-classes` | ✓ | **200** (15 lớp) | ClassListPage | **PASS** | `name`, `course_title`, `student_count`, `status`, dates, `progress` |
| Student `GET /classes/{id}` | ✓ | 200 (mẫu E2E class) | ClassDetailPage | **PASS** | `invite_code` ẩn với student; `my_progress` khi có |
| Instructor `GET /classes/my-classes` | ✓ | ✓ **200** | Instructor ClassList | **PASS** | **UIUX-003 FIXED** |
| Instructor `GET /classes/{id}` | ✓ | ✓ **200** | ClassDetailPage | **PASS** | **UIUX-003** (thêm fix `In()` thay `.in_()`) |
| `invite_code`, `max_students`, dates | ✓ | ✓ | Tab Thông tin | **PASS** | FE: Sao chép mã mời, Chỉnh sửa |
| `GET /classes/{id}/students` | ✓ | ✓ (lớp có HV) | Tab Học viên | **PASS** | Lớp E2E 0 HV — tab vẫn mở |
| `GET /classes/{id}/progress` | ✓ | ✓ | Tab Tiến độ lớp | **PASS** | Chưa drill sâu chart | |

---

### 2.5 Instructor — Quiz CRUD & Analytics

| Entity | API | UI | Kết quả |
|--------|-----|-----|---------|
| Dashboard instructor | `GET /dashboard/instructor` 200 | `/dashboard/instructor` | **PASS** |
| Analytics classes | `GET /analytics/instructor/classes` 200 | InstructorAnalyticsPage | **PASS** (API) |
| Analytics progress-chart | 200 | Chart | **PASS** (API) |
| Analytics quiz-performance | 200 | Chart | **PASS** (API) |
| Quiz create/edit UI | — | InstructorQuizFormPage | **Not runtime tested** | Phase 3 |

---

### 2.6 Admin — Users / Courses / Classes / Search

| Entity | DB field (mẫu) | API list | UI AdminPage | Kết quả |
|--------|----------------|----------|--------------|---------|
| Users | `full_name`, `email`, `role`, `status` | `GET /admin/users` 200 | Table 20 rows | **PASS** |
| Users | `avatar_url` | ✓ (optional) | Avatar column | **PASS** / empty OK |
| Users detail/edit | có trong DB | **Không có** `GET/PUT /admin/users/{id}` trên UI | Chỉ Vai trò/Reset/Xóa | **PARTIAL** | API_NO_UI (by design list-only) |
| Courses | `title`, `category`, `level`, `status`, `course_type` | `GET /admin/courses` 200 | Courses tab | **PASS** |
| Courses | `enrollment_count` | ✓ | Cột enroll | **PASS** |
| Courses | author | `author.full_name` | Cột tác giả | **PASS** |
| Courses detail/edit | có | **API_NO_UI** | Chỉ create/delete | **PARTIAL** |
| Classes | `name`, `instructor`, counts | `GET /admin/classes` 200 | Classes tab | **PASS** (API) |
| System counts | 411 / 150 / 98 | `GET /dashboard/admin` | Admin tiles | **PASS** |
| Search analytics | — | `GET /search/analytics` 200 (admin) | SearchResultsPage panel | **PASS** (API) |

---

### 2.7 Dashboard payloads (field presence)

| Role | API keys (sample) | UI | Kết quả |
|------|-------------------|-----|---------|
| Student | `recent_courses`, `pending_quizzes`, `overview`, `performance_summary` | DashboardPage | **PASS** | **FIX** UIUX-027 — `QuizAttempt.started_at` + `passed` (trước: `created_at` gây lỗi log) |
| Instructor | `recent_classes`, `total_students`, `active_classes_count` | Dashboard | **PASS** | |
| Admin | `total_users`, `users_by_role`, `course_stats`, `class_stats` | Dashboard | **PASS** | |

---

### Phase 2 — Tóm tắt gaps

| ID | Severity | Tóm tắt | Trạng thái |
|----|----------|---------|------------|
| UIUX-002 | Medium | `avg_rating` thiếu trên CourseDetailPage (API đã có trong `course_statistics`) | **FIXED** |
| UIUX-003 | **Critical** | Instructor `GET /classes/my-classes` → 500 (`Progress.user_id.in_()` + sort) | **FIXED** — `In(Progress.user_id, …)` + `.sort("-created_at")` |
| UIUX-007 | **Critical** | `GET /courses/{cid}/lessons/{lid}` → 500 khi user có `Progress.lessons_progress` | **FIXED** — `learning_service.py` |
| UIUX-008 | **High** | `GET /quizzes/{id}` không trả `questions[]` | **FIXED** — `QuestionForAttempt` trong response |
| UIUX-009 | Medium | Module detail: **Điều kiện tiên quyết** hiển thị UUID thô | **FIXED** — BE enrich `prerequisites` → `{id, title}`; FE fallback |
| UIUX-010 | Low | **Mục tiêu học tập** hiển thị `skill_tag` thô khi mô tả trống | **FIXED** — format tag + fallback «Mục tiêu N» |
| UIUX-011 | **High** | Hết bài/module: nút «bài tiếp» → `/lessons/null` + empty state | **FIXED** — `getNavLesson`, panel hoàn thành, BE `navigation.next_lesson: null` |
| UIUX-012 | **High** | `GET /quizzes/{id}/class-results` → **500** (`'answer'`) | **FIXED** — `selected_option` + lọc `class.student_ids` |
| UIUX-013 | Medium | Quiz fill-in-blank: không có ô nhập trên AttemptPage | **FIXED** — input text khi không có `options` |
| UIUX-001 | Low | CORS khi FE `localhost` + API `127.0.0.1` | **FIXED** — default API `localhost:8000`; BE đã có cả hai origin |
| — | — | `owner_info.bio` / `experience_years` null — UI graceful (PARTIAL data) |
| — | N/A | Comments/reviews — không có product scope |

---

## Phase 3+ (tóm tắt smoke trước đó)

Student/Instructor/Admin auth flows smoke: PASS trên localhost:3000. Chi tiết flow sâu → Phase 3.

---

## Bugs (chi tiết)

### UIUX-002 — avg_rating thiếu trên course detail

| Field | Value |
|-------|--------|
| **Severity** | Medium |
| **DB** | `avg_rating: 4.6` |
| **API** | `GET /courses/search` ✓ · `GET /courses/{id}` ✗ |
| **UI** | Catalog có rating; detail không |
| **Fix** | Thêm field vào `CourseDetailResponse` + hiển thị hero |

### UIUX-003 — Instructor my-classes 500

| Field | Value |
|-------|--------|
| **Severity** | Critical |
| **API** | `GET /classes/my-classes` (role=instructor) |
| **Actual** | `500` — `ExpressionField object is not callable` |
| **Files** | `BE/services/class_service.py` ~L160 `.sort(-Class.created_at)` |
| **Fix** | Dùng `.sort([("created_at", -1)])` theo Beanie |

### UIUX-007 — Lesson content API 500

| Field | Value |
|-------|--------|
| **Severity** | Critical |
| **API** | `GET /courses/{courseId}/lessons/{lessonId}` |
| **UI** | `LessonPage.jsx` → toast "Không thể tải bài học" |
| **Fix** | Debug `learning_service.get_lesson_content` (có thể liên quan `created_at` / embedded lesson) |

### UIUX-008 — Quiz attempt thiếu questions trong API

| Field | Value |
|-------|--------|
| **Severity** | High |
| **API** | `GET /quizzes/{id}` trả `question_count` nhưng không `questions` |
| **UI** | `QuizAttemptPage` — `quiz.questions` undefined → empty state |
| **Fix** | Trả `questions` (sanitized) trong detail hoặc endpoint `GET .../attempt/start` |

### UIUX-001 — CORS `127.0.0.1:3000`

Low — workaround: dùng `localhost:3000`.

---

## FE UI/UX retest (localhost:3000) — sau fix 2026-05-19

| Bug | Trang / hành động | Kết quả FE |
|-----|-------------------|------------|
| UIUX-002 | `/dashboard/courses/{id}` — hero stats | ★ **4.6** hiển thị |
| UIUX-007 | `/dashboard/courses/.../lessons/{lid}` | Nội dung bài, video/đính kèm, nav, AI chat |
| UIUX-008 | `/dashboard/quiz/{id}/attempt` | Câu hỏi MCQ (không còn empty state) |
| UIUX-003 | Instructor `/dashboard/classes` + detail | **12 lớp**, detail tabs Thông tin/Học viên/Tiến độ |

**Còn mở (không phải bug):** gap **API_NO_UI** by design (orphan endpoints). **Không sửa trong scope:** admin user/course detail edit, PUT quiz edit form.

---

## Phase 2b — Ma trận API ↔ UI (runtime)

**Nguồn:** [`.cursor/plans/ui_ux_editorial_refactor_plan_e17edc9e.plan.md`](../../.cursor/plans/ui_ux_editorial_refactor_plan_e17edc9e.plan.md) §2b.1–2b.14, [`API_COVERAGE_LOG.md`](API_COVERAGE_LOG.md).

**Quy trình mỗi operation:** Mở **UI Route** trên `http://localhost:3000` → thao tác user → DevTools Network khớp **API** → field render OK.

**Cột:** `Wire` = OK | FAIL | N/A · `Gap` = — | API_NO_UI | UI_NO_API | PARTIAL | DEAD_ROUTE

| Nhóm | Ops | Trạng thái | Ghi chú |
|------|-----|------------|---------|
| 2b.1 Auth & Users | 11 | **Done** | Profile PATCH wired; refresh/verify-email cần token DB (N/A runtime) |
| 2b.2 Courses & enrollments | 8 | **Done** | Xem bảng §2b.2 bên dưới |
| 2b.3 Learning | 7 | **Done** | Browser + `phase2b_3_learning_audit.py` |
| 2b.4 Quizzes & practice | 10 | **Done** | Browser + `phase2b_4_quizzes_audit.py` |
| 2b.5 Assessments & rec | 7 | **Done** | Browser + `phase2b_5_assessments_audit.py` |
| 2b.6 Progress & dashboard | 9 | **Done** | Browser + `phase2b_6_progress_dashboard_audit.py` + wire fix |
| 2b.7 Classes | 10 | **Done** | Browser + `phase2b_7_classes_audit.py` |
| 2b.8 Personal courses | 6 | **Done** | Browser + `phase2b_8_personal_courses_audit.py` |
| 2b.9 Chat | 5 | **Done** | Browser + `phase2b_9_chat_audit.py` |
| 2b.10 Search | 4 | **Done** | Browser + `phase2b_10_search_audit.py` |
| 2b.11 Admin | 17 | **Done** | Browser + `phase2b_11_admin_audit.py` |
| 2b.12 System | 1 | **Done** | `GET /health` 200 |
| 2b.13–14 Routes / gaps | — | **Done** | Browser + `phase2b_13_14_gaps_audit.py` |

### 2b.1 Auth & Users (ghi nhận ban đầu)

| Method | API | UI Route | Wire | Gap | Note |
|--------|-----|----------|------|-----|------|
| POST | `/auth/login` | `/auth/login` | OK | — | 3 role demo |
| POST | `/auth/logout` | Sidebar | OK | — | |
| POST | `/auth/register` | `/auth/register` | OK | — | → verify-email |
| POST | `/auth/forgot-password` | `/auth/forgot-password` | OK | — | UI only (BE path thiếu trong openapi) |
| POST | `/auth/reset-password` | `/auth/reset-password?token=` | N/A | — | Cần token DB |
| POST | `/auth/verify-email` | `/auth/verify-email` | N/A | — | Cần token DB |
| POST | `/auth/resend-verification` | VerifyEmailPage | N/A | — | Chưa runtime |
| POST | `/auth/refresh` | api interceptor | N/A | — | Không UI riêng |
| — | OAuth | Login buttons | OK | API_NO_UI | Toast only — by design |
| GET | `/users/me` | Boot / Profile | OK | — | |
| PATCH | `/users/me` | `/dashboard/profile` | **OK** | — | `ProfilePage` → `userService.updateProfile` (form edit + save) |

### 2b.2 Courses catalog & enrollments (localhost:3000)

| Method | API | UI Route | Wire | Gap | Note |
|--------|-----|----------|------|-----|------|
| GET | `/courses/search` | `/dashboard/courses` | **OK** | — | Network: `courses/search?skip&limit`; grid + filter + pagination |
| GET | `/courses/public` | CoursesPage **không gọi** | N/A | **API_NO_UI** (catalog) | Dùng ở `ClassCreatePage`, `ChatPage` — **OK** tại đó |
| GET | `/courses/{id}` | `/dashboard/courses/:id` | **OK** | — | Hero, modules, ★ rating, enroll CTA |
| GET | `/courses/{id}/enrollment-status` | — | N/A | **API_NO_UI** | `courseService.getEnrollmentStatus` orphan; detail dùng `enrollment_info` embedded — đủ field |
| POST | `/enrollments` | CourseDetail «Đăng ký khóa học» | **OK** | — | API 201; toast + CTA → «Tiếp tục học» |
| GET | `/enrollments/my-courses` | `/dashboard/my-courses` | **OK** | — | Tabs Tất cả/Đang học/Hoàn thành/Đã hủy + summary |
| GET | `/enrollments/{id}` | `/dashboard/enrollment/:id` | **OK** | **PARTIAL→fixed** | Trước: route có, **không link** từ MyCourses — đã thêm «Chi tiết đăng ký» |
| DELETE | `/enrollments/{id}` | MyCourses modal «Hủy đăng ký» | **OK** | — | API 200; card biến mất khỏi list |

**UI/UX đã kiểm tra:** catalog card (`avg_rating`, `enrollment_count`, badge «Đã đăng ký»); course detail enrolled/unenrolled; my-courses progress + «Tiếp tục học».

**Fix trong phiên 2b.2:** `MyCoursesPage.jsx` — sửa đóng thẻ JSX sai (`</motion.div>` → `</div>`) + nút **Chi tiết đăng ký** → `GET /enrollments/{id}`.

**Bug ghi nhận (không chặn 2b.2):** UIUX-001 — chỉ test trên `localhost:3000`.

### 2b.3 Learning — modules, lessons, complete (localhost:3000)

**Tài khoản:** `student1@gmail.com` · **Khóa:** Bootcamp Business 3 (`6cec7c81-6ff4-425e-84c8-de3238e0b5a2`) · **Script:** `BE/scripts/phase2b_3_learning_audit.py`

| Method | API | UI Route | Wire | Gap | Note |
|--------|-----|----------|------|-----|------|
| GET | `/courses/{id}/modules` | `.../courses/:id/modules` | **OK** | — | DevTools: `GET .../modules` 200; 6 thẻ module, breadcrumb «Nội dung khóa học» |
| GET | `/courses/{id}/modules/{mid}` | `.../modules/:mid` | **OK** | — | Module 4 (`7ef11ad0-…`): lessons, outcomes, resources (2 PDF/link), tóm tắt 33% |
| GET | `.../modules/{mid}/outcomes` | — | **OK** (API) | **API_NO_UI** | Script 200, 4 outcomes; FE dùng **embedded** `learning_outcomes` — đủ cho list |
| GET | `.../modules/{mid}/resources` | — | **OK** (API) | **API_NO_UI** | Script 200, **18** resources; embedded detail chỉ **2** (subset module) — không gọi endpoint riêng |
| GET | `/courses/{id}/lessons/{lid}` | `.../lessons/:lid` | **OK** | — | Lesson 4.2 (`fc027579-…`): title, nội dung, đính kèm, «Làm quiz», AI FAB |
| POST | `.../lessons/{lid}/complete` | LessonPage «Đánh dấu đã học xong» | **OK** | — | Network `POST .../complete` **200** → badge **«✓ Đã hoàn thành»**, nút complete ẩn/disabled |
| POST | `.../modules/{mid}/assessments/generate` | — | **OK** (API) | **API_NO_UI** | Script **201** với `question_count: 5` (422 nếu &lt; 5); không có CTA trên ModuleDetail |

**UI/UX đã kiểm tra (browser + DevTools):** ModuleList → ModuleDetail → LessonPage; Network khớp từng bước; console chỉ cảnh báo framer-motion reduced-motion (không lỗi app).

**Ghi nhận UX (không chặn wire):**
- **UIUX-009:** Prerequisites = UUID — cần map `module_id` → title (FE lookup hoặc BE enrich).
- **UIUX-010:** Outcomes hiện `skill_tag` khi mô tả trống — cải thiện copy seed hoặc ẩn tag khi không có `outcome`.

**Đã xác nhận fix trước:** UIUX-007 lesson API 200 trên cùng khóa học.

### 2b.4 Quizzes & AI practice (localhost:3000)

**Script:** `BE/scripts/phase2b_4_quizzes_audit.py` · **Student:** `student1@gmail.com` · **Instructor:** `instructor1@ailearning.vn`

| Method | API | UI Route | Wire | Gap | Note |
|--------|-----|----------|------|-----|------|
| GET | `/quizzes` | `/dashboard/quiz` (student), `/dashboard/instructor/quizzes` | **OK** | — | Network `GET /quizzes?skip&limit=12` 200; grid + search + pagination |
| GET | `/quizzes/{id}` | `/dashboard/quiz/:id`, `/attempt` | **OK** | — | 10 câu MCQ + fill-blank; UIUX-008 `questions[]` |
| POST | `/quizzes/{id}/attempt` | `/dashboard/quiz/:id/attempt` «Nộp bài» | **OK** (API) | **PARTIAL** (UI E2E) | API 201 khi trả lời đủ câu; browser: detail→attempt, chọn đáp án, chưa nộp full 10 câu trong session |
| GET | `/quizzes/{id}/results` | `/dashboard/quiz/:id/results` | **OK** | — | 200; 10 câu + điểm + «Làm lại quiz»; DevTools khớp |
| POST | `/quizzes/{id}/retake` | QuizResults «Làm lại quiz» | **OK** (API) | — | API 201; nút hiển thị khi `can_retake` |
| POST | `/lessons/{lid}/quizzes` | `/dashboard/instructor/quizzes/create` | **OK** (API) | — | 422 nếu thiếu body (đúng schema); UI «+ Tạo quiz từ bài học» |
| PUT | `/quizzes/{id}` | — | **OK** (API) | **API_NO_UI** | 403 non-owner; endpoint tồn tại, không form edit |
| DELETE | `/quizzes/{id}` | Instructor QuizPage «Xóa» | **OK** (UI) | — | Nút + modal trên từng card; audit không xóa thật |
| GET | `/quizzes/{id}/class-results` | `/dashboard/instructor/quizzes/:id/results` | **OK** | — | UI combobox + `classId`; API 200 sau fix UIUX-012 |
| POST | `/ai/generate-practice` | — | **OK** (API) | **API_NO_UI** | 201 + `practice_id`; `quizService.generatePractice` không gọi từ FE |

**Luồng browser (student):** `/dashboard/quiz` → card → detail («Bắt đầu», «Xem kết quả») → attempt (câu hỏi + timer) → `/results` (chi tiết 10 câu, retake CTA).

**Luồng browser (instructor):** `/dashboard/instructor/quizzes` → «Kết quả lớp» → chọn lớp → `class-results` (empty hoặc lỗi 500); «+ Tạo quiz», «Xóa» trên card.

### 2b.5 Assessments & recommendations (localhost:3000)

**Script:** `BE/scripts/phase2b_5_assessments_audit.py` · **Student:** `student1@gmail.com` · **Phiên mẫu:** `14f3701b-f1f8-4c0f-9c1d-3f4fbf7f347d` (Python Beginner, 15 câu, điểm ~26)

| Method | API | UI Route | Wire | Gap | Note |
|--------|-----|----------|------|-----|------|
| POST | `/assessments/generate` | `/dashboard/assessment` «Bắt đầu đánh giá» | **OK** | **PARTIAL** (UI E2E) | API 201, 15 câu (~3 phút AI); browser: form category/subject/level hiển thị đúng, chưa chạy generate full trong session (latency) |
| GET | `/assessments/history` | Setup + Recommendations sidebar | **OK** | — | 200; 1 phiên `evaluated` trên setup; history picker trên `/dashboard/recommendations` |
| POST | `/assessments/{sid}/submit` | `/dashboard/assessment/:sid` «Nộp bài» | **OK** | **PARTIAL** (UI E2E) | API 200 sau generate; browser dùng phiên đã nộp (không retake generate mới) |
| GET | `/assessments/{sid}/results` | `/dashboard/assessment/:sid/results` | **OK** | — | 200 score=25.8; UI: phân tích kỹ năng, lỗ hổng, lời khuyên AI, CTA review/recommendations |
| GET | `/assessments/{sid}/review` | `/dashboard/assessment/:sid/review` | **OK** | — | 200 `items[]`×15; UI hiển thị đề + đáp án đã chọn + ghi chú chấm |
| GET | `/recommendations/from-assessment` | `/dashboard/recommendations?session_id=` | **OK** | — | 200, 5 khóa + lộ trình + lời khuyên; DevTools khớp |
| GET | `/recommendations` | `/dashboard/recommendations` (gợi ý chung) | **OK** | — | 200 `recommended_courses[]` (5 khóa sau khi có phiên evaluated); nút «Gợi ý chung» |

**Luồng browser (student):** `/dashboard/assessment` (lịch sử 1 phiên) → «Kết quả» → results (skill analysis) → «Xem lại bài làm» → review 15 câu → «Xem lộ trình học tập» → recommendations theo phiên (5 khóa) → «Gợi ý chung».

**Ghi chú:** Luồng AI generate + làm bài + nộp mất ~3 phút; đã verify đầy đủ qua script API; browser spot-check các màn sau evaluate.

**UI refactor (2026-05-20):** `RecommendationsPage` — layout editorial (hero → tab nguồn → chip phiên → aside AI + card list), ẩn mô tả lorem, responsive mobile/desktop, tab «Gợi ý chung» / «Theo đánh giá» rõ ràng.

### 2b.6 Progress, dashboard & analytics (localhost:3000)

**Script:** `BE/scripts/phase2b_6_progress_dashboard_audit.py` · **Student:** `student1@gmail.com` · **Instructor:** `instructor1@ailearning.vn` · **Admin:** `admin1@ailearning.vn` · **Course mẫu (enrolled):** `6cec7c81-6ff4-425e-84c8-de3238e0b5a2`

| Method | API | UI Route | Wire | Gap | Note |
|--------|-----|----------|------|-----|------|
| GET | `/progress/course/{id}` | `/dashboard/courses/:id` (enrolled) | **OK** | — | 200 overall ~67%; section «Tiến độ học tập» + modules/lessons status |
| GET | `/dashboard/student` | `/dashboard` (student) | **OK** | — | 200; cards khóa đang học, quiz, gợi ý; overview stats |
| GET | `/dashboard/instructor` | `/dashboard/instructor` | **OK** | **PARTIAL** (fixed) | 200 `active_classes_count=9`, `total_students=553`; FE map `active_classes_count`, `class_name` (UIUX-015) |
| GET | `/dashboard/admin` | `/dashboard/admin` (tab Tổng quan) | **OK** | — | 200 `total_users`, `total_courses`, `total_classes`; AdminPage summary |
| GET | `/analytics/learning-stats` | `/dashboard/progress` | **OK** | **PARTIAL** (fixed) | 200; FE merge với `/dashboard/student` overview → stats ring + achievements (UIUX-014) |
| GET | `/analytics/progress-chart` | `/dashboard/progress` | **OK** | — | 200, 5 điểm `chart_data`; Recharts line chart hiển thị |
| GET | `/analytics/instructor/classes` | `/dashboard/instructor/analytics` | **OK** | — | 200, 12 lớp; bảng «Theo lớp» |
| GET | `/analytics/instructor/progress-chart` | `/dashboard/instructor/analytics` | **OK** | — | 200, 5 điểm (week); biểu đồ «Tiến độ học viên» |
| GET | `/analytics/instructor/quiz-performance` | `/dashboard/instructor/analytics` | **OK** | — | 200, 56 quiz; bảng pass rate / điểm TB |

**Luồng browser (student):** `/dashboard` → stats + recent courses → `/dashboard/progress` → ring %, chart, 5 khóa progress bars, achievements 5/6 → course detail enrolled → «Tiến độ học tập» per-module.

**Luồng browser (instructor):** `/dashboard/instructor` → stats (9 lớp, 553 HV, 56 quiz) + recent classes → «Analytics» → chart + class list + quiz table (~15s load do aggregate).

**Luồng browser (admin):** `/dashboard/admin` → Admin Console overview + summary cards từ `GET /dashboard/admin`.

**Fix wire (phiên này):**
- **UIUX-014:** `ProgressPage` — `buildProgressStats()` ghép `learning-stats` + `dashboard/student` (trước đó stats cards = 0).
- **UIUX-015:** `InstructorDashboardPage` — map `active_classes_count`, `class_name`, `avg_completion_rate`, `quizzes_created_count`.
- **UIUX-016:** `GET /analytics/learning-stats` `by_course` — thêm `total_lessons`, `total_modules`, `completed_modules`, `progress_percent`; FE map đúng (trước: `0/0 modules`, `24/24` vs 67%).
- **UIUX-017:** `GET /dashboard/instructor` `avg_completion_rate` — tính từ `Progress.overall_progress_percent` theo lớp (trước: luôn 0% do dùng `completion_rate` alias chưa sync).
- **UIUX-018:** `StudentDashboard` — làm tròn `progress_percent` (trước: `66.666…%`).

**By design:** `ProgressPage` không gọi trực tiếp `GET /progress/course/{id}` — dùng analytics + dashboard; chi tiết per-course trên `CourseDetailPage`.

---

## Tổng hợp bug & UX (2026-05-19)

### Đã sửa (24 mục)

| ID | Mức | Vấn đề | Fix |
|----|-----|--------|-----|
| UIUX-002 | Medium | Thiếu ★ rating trên course detail | `CourseDetailPage` + API stats |
| UIUX-003 | Critical | Instructor `my-classes` 500 | `class_service.py` sort + `In()` |
| UIUX-007 | Critical | Lesson content 500 | `learning_service.py` progress attrs |
| UIUX-008 | High | Quiz thiếu `questions[]` | `QuestionForAttempt` trong GET quiz |
| UIUX-009 | Medium | Prerequisites hiện UUID | BE enrich title; FE `getPrerequisiteText` |
| UIUX-010 | Low | Outcomes hiện `skill_tag` thô | BE format + fallback text |
| UIUX-011 | High | `/lessons/null` khi hết bài | `getNavLesson`, completion panel, BE nav null |
| UIUX-012 | High | Class quiz results 500 | `_answer_value_from_item`, `class.student_ids` |
| UIUX-013 | Medium | Fill-blank không có input | `QuizAttemptPage` + CSS |
| UIUX-001 | Low | CORS origin lệch | `api.js` default `localhost:8000` |
| UIUX-014 | Medium | ProgressPage stats = 0 (wire lệch) | `buildProgressStats` merge analytics + dashboard |
| UIUX-015 | Medium | Instructor dashboard stats «—» | Map `active_classes_count`, `class_name`, etc. |
| UIUX-016 | Medium | ProgressPage `0/0 modules`, lesson count sai | BE enrich `by_course`; FE map fields |
| UIUX-017 | Medium | Instructor `avg_completion_rate` = 0% | BE dùng `Progress.overall_progress_percent` |
| UIUX-018 | Low | Student dashboard % thập phân dài | `Math.round` trên progress bar |
| UIUX-019 | High | GET class detail 500 khi có HV | `_quiz_attempts_for_course` trong `get_class_detail` |
| UIUX-020 | High | GET class students 500 / quiz TB sai | Fix quiz join + `enrolled_at` timestamps |
| UIUX-021 | High | GET student detail 500 | Fix `default_quiz_id` + lesson `quiz_id` lookup |
| UIUX-022 | Medium | ClassDetail không drill-down HV | Modal «Hồ sơ HV» wire `GET /classes/{id}/students/{sid}` |
| UIUX-023 | High | `POST /courses/from-prompt` 400 trên Windows | `_ai_log()` ASCII-safe thay emoji `print()` trong `generate_course_from_prompt` |
| UIUX-024 | Medium | HV join lớp không rõ bước học; AI thiếu trên vài màn học | Panel 3 bước + CTA; ChatWidget trên module/course/quiz; nav «← Lớp» |
| UIUX-025 | Medium | Resume / tab tiến độ HV / banner lớp / AI quiz results | `next_lesson`, `my-progress`, ClassLearningBanner, QuizWrongAnswerExplainer |
| UIUX-026 | Medium | Click kết quả search → 404 | `SearchResultsPage.resolveSearchItemUrl()` map API path → `/dashboard/*` |
| UIUX-027 | Medium | Student dashboard pending quiz log lỗi `created_at` | `dashboard_service.py`: sort `started_at`, check `attempt.passed` |
| UIUX-028 | Low | Landing footer thiếu link pháp lý | `LandingPage.jsx` footer `/terms`, `/privacy` |
| 2b.2 | — | MyCourses JSX + link enrollment detail | `MyCoursesPage.jsx` |
| 2b.3 | — | `CourseLearningNav` thiếu nút quay lại | Component dùng chung 3 trang học |

### Không sửa (by design / ngoài scope QA)

- Admin: không có form edit user/course chi tiết (list + actions only).
- `PUT /quizzes/{id}`: không có UI edit quiz (chỉ create/delete).
- `POST /ai/generate-practice`, module outcomes/resources standalone, enrollment-status: **API_NO_UI**.
- Comments/reviews: không có trong product scope.
- `owner_info.bio` null: UI ẩn field — chấp nhận được.

### File đã chạm (phiên fix tổng hợp)

- `BE/services/quiz_service.py`, `learning_service.py`, `class_service.py`
- `FE/.../LessonPage.jsx`, `ModuleDetailPage.jsx`, `ModuleListPage.jsx`, `CourseLearningNav.*`
- `FE/.../ProgressPage.jsx`, `InstructorDashboardPage.jsx`, `RecommendationsPage.*`
- `FE/.../ClassDetailPage.jsx`, `ClassDetailPage.css`
- `BE/services/dashboard_service.py` — pending quiz query (UIUX-027)
- `FE/src/pages/landing/LandingPage.jsx` — footer legal (UIUX-028)

---

## Phase 6 — Summary

| Phase | Trạng thái |
|-------|------------|
| 0 Pre-flight | Done |
| 1 Auth | Done |
| **2 Data audit** | Done |
| **2b API matrix** | **Done** |
| 3–4 Flows / AI | Pending |
| Bugs P0/P1 | **Đã fix** UIUX-001→028 |

**Tiếp theo:** Phase 3–4 Flows / AI UX sâu (theo plan).

---

## Phase 2 — Tổng hợp (2026-05-20)

### Phạm vi đã hoàn thành

| Khối | Nội dung | Kết quả |
|------|----------|---------|
| **Phase 2 Data audit** | DB↔API↔UI 6 nhóm (course, lesson, quiz, class, admin, dashboard) | **Done** — UIUX-001→013 |
| **Phase 2b API↔UI** | 14 nhóm, ~88 operations | **Done** — audit script + browser từng nhóm |
| **Scripts** | `phase2b_3` … `phase2b_11`, `phase2b_13_14_gaps` | Pass trên localhost |

### Fix phiên tổng hợp cuối (UIUX-027/028)

- **UIUX-027:** `get_student_dashboard` — sort `QuizAttempt.started_at` (không phải `created_at`); check `attempt.passed` thay `"passed"`.
- **UIUX-028:** `LandingPage` footer — link `/terms`, `/privacy`.

### Còn lại — không phải bug

| Loại | Chi tiết |
|------|----------|
| **API_NO_UI** | enrollment-status, module assessment generate, generate-practice, PUT quiz, admin detail |
| **N/A runtime** | verify-email, reset-password, refresh token |
| **PARTIAL E2E** | Quiz nộp full 10 câu, assessment generate mới — API script OK; browser spot-check |
| **Ngoài scope** | Comments/reviews, OAuth thật, admin edit form |

---

### 2b.7 Classes (localhost:3000)

**Script:** `BE/scripts/phase2b_7_classes_audit.py` · **Student:** `student1@gmail.com` · **Instructor:** `instructor1@ailearning.vn` · **Course mẫu:** `6cec7c81-6ff4-425e-84c8-de3238e0b5a2`

| Method | API | UI Route | Wire | Gap | Note |
|--------|-----|----------|------|-----|------|
| POST | `/classes` | `/dashboard/instructor/classes/create` | **OK** | — | 201 + `invite_code`; ClassCreatePage |
| GET | `/classes/my-classes` | `/dashboard/classes` (student) · `/dashboard/instructor/classes` | **OK** | — | Inst 13 lớp, student 16 lớp |
| GET | `/classes/{id}` | ClassDetail (student + instructor routes) | **OK** | **FIX** UIUX-019 | 200; invite code, stats, course link |
| PUT | `/classes/{id}` | ClassDetail modal «Chỉnh sửa» | **OK** | — | 200 rename |
| DELETE | `/classes/{id}` | ClassDetail «Xóa lớp» | **OK** | — | 200 lớp trống sau remove HV |
| POST | `/classes/join` | JoinClassModal | **OK** | — | 200 + auto enrollment |
| GET | `/classes/{id}/students` | ClassDetail tab «Học viên» | **OK** | **FIX** UIUX-020 | 200 `data[]`; table + nút Gỡ |
| GET | `/classes/{id}/students/{sid}` | ClassDetail modal «Hồ sơ HV» | **OK** | — | Click tên HV → `getStudentDetail` (UIUX-022) |
| DELETE | `/classes/{id}/students/{sid}` | ClassDetail tab HV «Gỡ» | **OK** | — | 200 soft remove |
| GET | `/classes/{id}/progress` | ClassDetail tab «Tiến độ lớp» | **OK** | — | 200 avg progress / completion / quiz TB |

**Luồng browser (instructor):** `/dashboard/instructor/classes` → cards → detail → tabs Thông tin / Học viên / Tiến độ lớp → **click tên HV** → modal hồ sơ (modules + quiz).

**Fix FE (phiên này):**
- **UIUX-022:** ClassDetailPage — modal drill-down học viên wire `GET /classes/{id}/students/{sid}`; làm tròn % tiến độ bảng HV.

**Luồng browser (student):** API join + my-classes verified; UI JoinClassModal trên ClassListPage (`/dashboard/classes`).

**Fix BE (phiên này):**
- **UIUX-019:** `get_class_detail` — bỏ query `QuizAttempt.course_id` (field không tồn tại) → 500 khi lớp có HV.
- **UIUX-020:** `get_class_students` — dùng `_quiz_attempts_for_course`, fix `enrolled_at`, module counts.
- **UIUX-021:** `get_student_detail` — `getattr` quiz id từ module/lesson thay `default_quiz_id`.

### 2b.8 Personal courses (localhost:3000)

**Script:** `BE/scripts/phase2b_8_personal_courses_audit.py` · **Student:** `student1@gmail.com` · **Instructor (browser):** `instructor1@ailearning.vn`

| Method | API | UI Route | Wire | Gap | Note |
|--------|-----|----------|------|-----|------|
| GET | `/courses/my-personal` | `/dashboard/personal-courses` | **OK** | — | Grid + empty state; sidebar link |
| POST | `/courses/personal` | `/dashboard/personal-courses/create` | **OK** | — | 201 → redirect editor |
| GET | `/courses/personal/{id}` | `/dashboard/personal-courses/:id/edit` | **OK** | — | Load title, category, modules |
| PUT | `/courses/personal/{id}` | CourseEditor «Lưu nháp» | **OK** | — | 200 update metadata |
| POST | `/courses/from-prompt` | PersonalCourses «Tạo bằng AI» | **OK** | **FIX** UIUX-023 | 201 + modules; prompt panel + templates |
| DELETE | `/courses/personal/{id}` | CourseEditor «Xóa khóa học» | **OK** | — | 200 → back to list |

**Luồng browser (instructor):** `/dashboard/personal-courses` → «+ Tạo thủ công» → form → editor (`88fc2f72-…`) → «Xóa khóa học» → list 0 khóa.

**Fix BE (phiên này):**
- **UIUX-023:** `generate_course_from_prompt` — emoji trong `print()` gây `UnicodeEncodeError` (cp1252) trên Windows → fallback path fail → API 400; thay bằng `_ai_log()` ASCII-safe.

**By design:** Personal courses dùng chung route cho student + instructor (`StudentOrInstructorRoute`); instructor sidebar không hiện link nhưng dashboard có CTA «Tạo khóa học AI».

### 2b.9 Chat (localhost:3000)

**Script:** `BE/scripts/phase2b_9_chat_audit.py` · **Student:** `student1@gmail.com` · **Route:** `/dashboard/chat`

| Method | API | UI Route | Wire | Gap | Note |
|--------|-----|----------|------|-----|------|
| POST | `/chat/course/{id}` | ChatPage input + «Gửi» | **OK** | — | Network 201; AI bubble + related_lessons + follow-up chips |
| GET | `/chat/history` | Chat sidebar | **OK** | — | Network 200; danh sách hội thoại + «Xóa tất cả» |
| GET | `/chat/conversations/{id}` | Click item sidebar | **OK** | — | Khôi phục user/AI messages; course dropdown sync |
| DELETE | `/chat/history/{id}` | Sidebar «×» + modal | **OK** | — | Modal xác nhận → 200; item biến mất |
| DELETE | `/chat/conversations` | Sidebar «Xóa tất cả» | **OK** | — | Modal → 200; sidebar empty state |

**Luồng browser (student):** Login → `/dashboard/chat` → chọn khóa enroll (`Complete Math 22`) → gợi ý «Giải thích khái niệm cơ bản» → Gửi → AI trả lời markdown + bài học liên quan; sidebar hiện thread sau load history.

**Fix FE (phiên này):** `ChatPage.handleSend` — gọi `loadHistory()` sau `sendMessage` để sidebar cập nhật ngay (trước đó chỉ refresh khi reload trang).

**Ghi nhận UX (không chặn wire):** Dropdown khóa học load async (~2–4s sau mount); instructor dùng `GET /courses/public` (không enroll) — by design theo `ChatPage.jsx`.

### 2b.10 Search (localhost:3000)

**Script:** `BE/scripts/phase2b_10_search_audit.py` · **Student:** `student1@gmail.com` · **Admin:** `admin1@ailearning.vn`

| Method | API | UI Route | Wire | Gap | Note |
|--------|-----|----------|------|-----|------|
| GET | `/search` | `/dashboard/search?q=` | **OK** | — | Network 200; 13+ khóa «math», filter category/level |
| GET | `/search/suggestions` | `GlobalSearchBar` dropdown | **OK** | — | Gõ «ma» → `GET .../suggestions?q=ma` 200 |
| GET | `/search/history` | `GlobalSearchBar` focus (empty q) | **OK** | — | Network 200; `search_history[]` sau khi đã search |
| GET | `/search/analytics` | `SearchResultsPage` panel | **OK** | — | Student **403** (không gọi panel); Admin **200** + «Thống kê tìm kiếm (admin)» |

**Luồng browser (student):** Header search → `/dashboard/search?q=math` → grid khóa học + bộ lọc; không thấy panel analytics.

**Luồng browser (admin):** `/dashboard/search?q=math` → kết quả + panel **Tổng truy vấn: 1500**; Network `GET /search/analytics` 200.

**By design:** Analytics chỉ render khi `user.role === 'admin'` (`SearchResultsPage.jsx`); suggestions debounce 200ms.

**Fix FE (phiên này):** **UIUX-026** — click kết quả search 404 vì BE trả URL `/courses/{id}` trong khi FE route là `/dashboard/courses/{id}`; `SearchResultsPage.resolveSearchItemUrl()` map course/class/module/lesson → dashboard routes.

### 2b.11 Admin (localhost:3000)

**Script:** `BE/scripts/phase2b_11_admin_audit.py` · **Admin:** `admin1@ailearning.vn` · **17/17 pass**

| Method | API | UI Route | Wire | Gap | Note |
|--------|-----|----------|------|-----|------|
| GET | `/admin/users` | `/dashboard/admin/users` | **OK** | — | Filter role/status, search, pagination 20/trang |
| POST | `/admin/users` | Modal «+ Tạo người dùng» | **OK** | — | 201 |
| GET | `/admin/users/{id}` | — | N/A | **API_NO_UI** | Audit 200; không trang/modal chi tiết |
| PUT | `/admin/users/{id}` | — | N/A | **API_NO_UI** | Audit 200; chỉ role/password/delete trên bảng |
| DELETE | `/admin/users/{id}` | Users table «Xóa» | **OK** | — | 200 |
| PUT | `/admin/users/{id}/role` | «Vai trò» dialog | **OK** | — | 200 |
| POST | `/admin/users/{id}/reset-password` | «Reset» dialog | **OK** | — | 200 |
| GET | `/admin/courses` | `/dashboard/admin/courses` | **OK** | — | Search + pagination |
| POST | `/admin/courses` | Modal «+ Tạo khóa học» | **OK** | — | 201 |
| GET | `/admin/courses/{id}` | — | N/A | **API_NO_UI** | Audit 200 |
| PUT | `/admin/courses/{id}` | — | N/A | **API_NO_UI** | Audit 200; chỉ create/delete trên list |
| DELETE | `/admin/courses/{id}` | Courses tab | **OK** | — | 200 |
| GET | `/admin/classes` | `/dashboard/admin/classes` | **OK** | — | Search + pagination |
| GET | `/admin/classes/{id}` | — | N/A | **API_NO_UI** | Audit 200 |
| GET | `/admin/analytics/users-growth` | `/dashboard/admin/analytics` | **OK** | — | Chart «Tăng trưởng người dùng (30 ngày)» |
| GET | `/admin/analytics/courses` | Admin analytics tab | **OK** | — | 200 |
| GET | `/admin/analytics/system-health` | Admin analytics tab | **OK** | — | Panel «Sức khỏe hệ thống» |

**Luồng browser (admin):** Login → `/dashboard/admin` → tabs Tổng quan / Người dùng (20 rows + Vai trò/Reset/Xóa) / Khóa học / Lớp học / Analytics (3 API load xong, không lỗi console).

**By design:** Không có UI edit user/course/class detail — list + actions only (theo plan §2b.14 #7).

### 2b.12 System (localhost:8000)

| Method | API | UI | Wire | Gap | Note |
|--------|-----|-----|------|-----|------|
| GET | `/health` | — | **OK** | **API_NO_UI** | `200 {"status":"ok"}` — ops curl, không UI |

### 2b.13 UI routes không map 1-1 API (localhost:3000)

**Browser:** public routes + role guards + sidebar + LessonPage instructor panel.

| UI Route | Kiểm tra | Wire | Gap | Note |
|----------|----------|------|-----|------|
| `/` LandingPage | Hero, CTA, footer nav + **Điều khoản / Bảo mật** | **OK** | — | Footer link `/terms`, `/privacy` (fix 2026-05-20) |
| `/auth/register` | Link «Điều khoản» + «Chính sách bảo mật» | **OK** | — | |
| `/terms` | 4 section + mục lục + «Quay lại đăng ký» / «Trang chủ»; **không** API | **OK** | — | Static LegalPage |
| `/privacy` | 4 section + nav; **không** API | **OK** | — | Static LegalPage |
| `/unauthorized` | Copy 403 + «Về Dashboard» / «Về trang chủ» | **OK** | — | |
| `/404` | Copy 404 + nav; catch-all `*` → redirect `/404` | **OK** | — | Verified `/dashboard/invalid-xyz` |
| Role guard | Student → `/dashboard/admin` **403 page**; Student → `/dashboard/instructor` **403** | **OK** | — | AdminRoute / InstructorRoute |
| Sidebar student | Có: Khóa học của tôi, Lớp học, **Đánh giá năng lực**, Gợi ý, Khóa cá nhân, Tiến độ; **không** Giảng dạy/Quản trị | **OK** | — | `Sidebar.jsx` filter role |
| Sidebar instructor | Có: Khóa học, Quiz, Chat, Tìm kiếm, **Giảng dạy**; **ẩn** my-courses, assessment, gợi ý, personal, progress | **OK** | — | By design plan §2b.13 |
| LessonPage instructor panel | Panel «Quiz cho bài học này» + «Tạo quiz mới» / «Xem trước» / «Kết quả lớp» | **OK** | — | Click «Kết quả lớp» → `/dashboard/instructor/quizzes/{id}/results` 200 |
| Assessment (student E2E) | Setup → lịch sử → «Kết quả» → results page (điểm, phân tích kỹ năng) | **OK** | — | `/dashboard/assessment/.../results` |

**Luồng browser (public):** `/` → Register CTA → `/auth/register` → click «Điều khoản» → `/terms` (4 sections) → `/privacy` → `/404` → `/unauthorized` (copy + buttons OK).

**Luồng browser (instructor lesson):** Login GV → enroll khóa → module detail (outcomes + resources embedded) → lesson → panel GV → «Kết quả lớp» load `InstructorQuizClassResultsPage`.

### 2b.14 Danh sách nghi ngờ thiếu UI (grep + browser)

**Script:** `BE/scripts/phase2b_13_14_gaps_audit.py`

| # | API / Service | Gap | Xác nhận |
|---|---------------|-----|----------|
| 1 | `GET /courses/{id}/enrollment-status` (`getEnrollmentStatus`) | **API_NO_UI** | Chỉ trong `courseService.js`; UI dùng `enrollment_info` từ `GET /courses/{id}` |
| 2 | `GET .../outcomes`, `GET .../resources` | **—** (embedded) | `ModuleDetailPage` render `learning_outcomes` + `resources` từ module detail — không cần UI riêng |
| 3 | `POST .../modules/{mid}/assessments/generate` | **API_NO_UI** | Chỉ `learningService.generateModuleAssessment`; không nút trên ModuleDetail — by design |
| 4 | `POST /ai/generate-practice` | **API_NO_UI** | Chỉ `quizService.generatePractice`; không flow luyện tập quiz — by design |
| 5 | `PUT /quizzes/{id}` | **API_NO_UI** | Chỉ `quizService.updateQuiz`; create/delete có UI, edit không — by design |
| 6 | `GET /classes/.../students/{sid}` | **—** (wired) | **UIUX-022:** `ClassDetailPage` modal «Hồ sơ HV» — đã wire (2b.7) |
| 7 | Admin GET/PUT user/course/class detail | **API_NO_UI** | Chỉ list + role/password/delete (2b.11) — by design |
| 8 | `adminService.updateCourse` / `quizService.updateQuiz` | **API_NO_UI** | Admin courses: create/delete only; `personalCourseService.updateCourse` **wired** tại CourseEditor |

**Kết luận 2b.14:** 6 mục **API_NO_UI by design**; 2 mục **wired/embedded** (outcomes/resources, student detail). Không phát hiện bug wire mới.

---

## Luồng học viên sau khi vào lớp (2026-05-20)

**Vấn đề:** Sau join lớp (GV tạo lớp → HV nhập mã), UI không làm rõ bước tiếp theo; AI chỉ có trên `LessonPage`.

### Luồng chuẩn (BE + FE)

```mermaid
flowchart LR
  A[Tham gia mã mời] --> B[POST /classes/join]
  B --> C[Tự tạo Enrollment]
  C --> D[Trang lớp /dashboard/classes/:id]
  D --> E[Tiếp tục học]
  E --> F[Modules /modules]
  F --> G[Module detail]
  G --> H[Lesson + AI FAB]
  H --> I[Quiz /dashboard/quiz]
```

| Bước | Route | Ghi chú |
|------|-------|---------|
| Join | `JoinClassModal` | BE auto-enroll khóa nền của lớp |
| Hub lớp | `/dashboard/classes` | Card lớp + «Tiếp tục học» |
| Chi tiết lớp | `/dashboard/classes/:id` | Panel 3 bước + CTA «Tiếp tục học» |
| Nội dung | `/dashboard/courses/:id/modules` → lesson | `CourseLearningNav` có link «← Lớp …» |
| Quiz | `/dashboard/quiz/:id/attempt` | AI gợi ý (không lộ đáp án) |

### Fix UX (phiên này — UIUX-024)

- **JoinClassModal:** redirect → trang lớp (không nhảy thẳng catalog); thêm «Bắt đầu học luôn».
- **ClassDetailPage (HV):** panel «Cách học trong lớp này» + CTA «Tiếp tục học» / «Bắt đầu học».
- **ClassListPage (HV):** nút «Tiếp tục học» trên card; hiện tên GV.
- **CourseLearningNav:** nút quay về lớp khi có `fromClass` trong navigation state.
- **ChatWidget:** thêm FAB AI trên `CourseDetailPage` (enrolled), `ModuleListPage`, `ModuleDetailPage`, `QuizAttemptPage` (trước chỉ `LessonPage`).

### Ý tưởng tiếp theo — **Đã triển khai (UIUX-025)**

- **Resume thông minh:** BE `next_lesson` trên `GET /classes/{id}` + `GET /classes/my-classes`; FE CTA «Tiếp tục học» mở thẳng `/lessons/{lesson_id}`.
- **Tab «Tiến độ của tôi»:** `GET /classes/{id}/my-progress` + tab ClassDetail (HV) — module/quiz từ Progress + QuizAttempt thật.
- **Banner lớp:** `ClassLearningBanner` trên module/lesson/course/quiz; sessionStorage theo `courseId`.
- **QuizResults AI:** `QuizWrongAnswerExplainer` gọi `POST /chat/course/{courseId}` với câu sai từ `GET /quizzes/{id}/results`; BE trả thêm `course_id`, `quiz_title`.

---
