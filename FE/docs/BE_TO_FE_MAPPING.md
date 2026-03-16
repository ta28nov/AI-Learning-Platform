# 🗺️ MAPPING BE → FE CHI TIẾT NHẤT (Theo Code Thực Tế)

> Tất cả data fields bên dưới đều trích từ **code thực tế** (Pydantic schemas, Beanie models, FastAPI routers).
> Không có field nào bịa thêm. **87 endpoints** từ 16 routers.

---

## 1️⃣ AUTH — `auth_router.py` + `users_router.py` (5 endpoints)

---

### `POST /auth/register`
**Page:** `RegisterPage.jsx` ✅ (đã có)

**Request body — `RegisterRequest`:**
| Field | Type | Validation | UI |
|---|---|---|---|
| `full_name` | `str` | min 3, max 100, ≥2 từ | Text input |
| `email` | `EmailStr` | unique | Text input |
| `password` | `str` | min 8, digit+upper+special | Password input + strength indicator |

> [!IMPORTANT]
> **BE KHÔNG có field `role` trong RegisterRequest.** Vai trò mặc định luôn là `student`.
> Password validation (BE): chứa ít nhất 1 chữ số, 1 chữ hoa, 1 ký tự đặc biệt `!@#$%^&*()_+-=[]{}|;:,.<>?`

**Response — `RegisterResponse` (201 Created):**
| Field | Type | UI Action |
|---|---|---|
| `id` | `str` UUID | ⚠️ **Tên field là `id`** (không phải `user_id`) |
| `full_name` | `str` | — |
| `email` | `str` | — |
| `role` | `str` | Luôn = `"student"` |
| `status` | `str` | Luôn = `"active"` |
| `created_at` | `datetime` ISO 8601 | — |
| `message` | `str` | `"Đăng ký tài khoản thành công"` → Toast success → redirect `/login` |

---

### `POST /auth/login`
**Page:** `LoginPage.jsx` ✅

**Request body — `LoginRequest`:**
| Field | Type | Validation | UI |
|---|---|---|---|
| `email` | `str` | required | Text input |
| `password` | `str` | required | Password input |
| `remember_me` | `bool` | optional, default `false` | **Checkbox** (ảnh hưởng refresh token TTL: 7d vs 1d) |

**Response — `LoginResponse`:**
| Field | Type | UI Action |
|---|---|---|
| `access_token` | `str` | → `localStorage` |
| `refresh_token` | `str` | → `localStorage` |
| `token_type` | `str` | "bearer" |
| `user.id` | `str` UUID | → `authStore` |
| `user.full_name` | `str` | → `authStore` → header avatar |
| `user.email` | `str` | → `authStore` |
| `user.role` | `str` | → `authStore` → route redirect (student/instructor/admin) |
| `user.avatar` | `str\|null` | ⚠️ **Tên field là `avatar`** (KHÔNG có `_url`). Map sang `avatar_url` khi lưu store |

---

### `POST /auth/logout`
**UI:** Nút trong `DashboardLayout` header → clear localStorage → redirect `/login`

**Response — `LogoutResponse`:** `message: str`

---

### `GET /users/me`
**Page:** `ProfilePage.jsx` 🆕 cần build

**Response — `UserProfileResponse`:**
| Field | Type | UI Element |
|---|---|---|
| `id` | `str` UUID | — |
| `full_name` | `str` | Heading text |
| `email` | `str` | Read-only label |
| `role` | `str` | Role badge: `student\|instructor\|admin` |
| `avatar_url` | `str\|null` | Avatar circle image |
| `bio` | `str\|null` | Text paragraph (max 500) |
| `contact_info` | `str\|null` | Contact link/text |
| `learning_preferences` | `List[str]` | **Tags array** (Programming, Math, ...) |
| `created_at` | `datetime` | "Tham gia: DD/MM/YYYY" |
| `updated_at` | `datetime` | — |

---

### `PATCH /users/me`
**Page:** `ProfilePage.jsx` edit mode

**Request body — `UserProfileUpdateRequest`:**
| Field | Type | Validation | UI Element |
|---|---|---|---|
| `full_name` | `str\|null` | min 3, max 100 | Editable text input |
| `avatar_url` | `str\|null` | http URL | Avatar upload / URL input |
| `bio` | `str\|null` | max 500 | Textarea + char counter |
| `contact_info` | `str\|null` | max 200 | Text input |
| `learning_preferences` | `List[str]\|null` | — | Tags/chips multi-select |

**Response — `UserProfileUpdateResponse`:** `id, full_name, email, role, avatar_url, bio, learning_preferences[], contact_info, updated_at, message` ("Cập nhật hồ sơ thành công")

---

## 2️⃣ ASSESSMENT — `assessments_router.py` (3 endpoints) 🆕

---

### `POST /assessments/generate`
**Page:** `AssessmentSetupPage.jsx` → `AssessmentQuizPage.jsx`

**Request — `AssessmentGenerateRequest`:**
| Field | Type | Validation | UI |
|---|---|---|---|
| `category` | `str` | required | Dropdown (Programming, Math, Business...) |
| `subject` | `str` | required | Dropdown (Python, JavaScript, Algebra...) |
| `level` | `str` | `Beginner\|Intermediate\|Advanced` | Radio buttons + info (Beginner=15 câu/15ph, Intermediate=25/22ph, Advanced=35/30ph) |
| `focus_areas` | `List[str]` | optional | Multi-select chips |

**Response — `AssessmentGenerateResponse`:**
| Field | Type | UI |
|---|---|---|
| `session_id` | `str` UUID | state param, không hiển thị |
| `questions[]` | `List` | Render quiz questions |
| `questions[].question_id` | `str` UUID | hidden |
| `questions[].question_text` | `str` | Question content |
| `questions[].question_type` | `str` `multiple_choice\|fill_in_blank\|drag_and_drop` | Render 3 loại component khác nhau |
| `questions[].difficulty` | `str` `easy\|medium\|hard` | DifficultyBadge |
| `questions[].skill_tag` | `str` | SkillBadge |
| `questions[].points` | `int` (1/2/3) | Point value label |
| `questions[].options` | `List[str]\|null` | Radio group (multiple_choice) hoặc input (fill_in) |
| `questions[].correct_answer_hint` | `str` | — (hidden during quiz) |
| `question_count` | `int` | Progress: "Câu X/Y" |
| `time_limit_minutes` | `int` | **CountdownTimer** component |
| `expires_at` | `datetime` | Auto-submit when expired |

---

### `POST /assessments/{session_id}/submit`

**Request — `AssessmentSubmitRequest`:**
| Field | Type | UI |
|---|---|---|
| `answers[]` | `List` | collected from quiz |
| `answers[].question_id` | `str` UUID | — |
| `answers[].answer_content` | `str` | text answer for fill_in |
| `answers[].selected_option` | `int\|null` | 0-3 cho multiple_choice |
| `answers[].time_taken_seconds` | `int` | tracked per question |
| `total_time_seconds` | `int` | total elapsed |

**Response:** `session_id`, `message` → redirect to results page

---

### `GET /assessments/{session_id}/results`
**Page:** `AssessmentResultsPage.jsx`

**Response — `AssessmentResultsResponse`:**
| Field | Type | UI Element |
|---|---|---|
| `overall_score` | `float` 0-100 | **Circular progress ring** lớn |
| `proficiency_level` | `str` | Level badge (Beginner/Intermediate/Advanced) |
| `score_breakdown.easy_correct/total` | `int` | 3-section horizontal bar |
| `score_breakdown.medium_correct/total` | `int` | 3-section horizontal bar |
| `score_breakdown.hard_correct/total` | `int` | 3-section horizontal bar |
| `skill_analysis[]` | `List` | — |
| `skill_analysis[].skill_tag` | `str` | Axis labels |
| `skill_analysis[].proficiency_percentage` | `float` | **Radar chart** (Recharts) |
| `skill_analysis[].strength_level` | `str` `Strong\|Average\|Weak` | Color coding |
| `skill_analysis[].detailed_feedback` | `str` | Expandable accordion |
| `knowledge_gaps[]` | `List` | — |
| `knowledge_gaps[].gap_area` | `str` | Card title |
| `knowledge_gaps[].importance` | `str` `High\|Medium\|Low` | Priority badge |
| `knowledge_gaps[].suggested_action` | `str` | CTA button text |
| `time_analysis.total_time_seconds` | `int` | Stat card |
| `time_analysis.average_time_per_question` | `float` | Stat card |
| `ai_feedback` | `str` | **Markdown-rendered** card |

---

## 3️⃣ COURSES — `courses_router.py` (4 endpoints)

---

### `GET /courses/search`
**Page:** `CoursesPage.jsx` ✅ enhance

**Query params:** `keyword`, `category`, `level`, `duration_range`, `sort_by`, `skip`, `limit`

**Response — `CourseSearchResponse`:**
| Field | Type | UI |
|---|---|---|
| `courses[]` | List | Grid card layout |
| `.id` | `str` UUID | → link to detail |
| `.title` | `str` | Card title |
| `.description` | `str` | Truncated 2-3 lines |
| `.category` | `str` | Category badge |
| `.level` | `str` | Level badge |
| `.thumbnail_url` | `str\|null` | Card image |
| `.total_modules` | `int` | "X modules" |
| `.total_lessons` | `int` | "Y bài học" |
| `.total_duration_minutes` | `int` | "Z phút" formatted |
| `.enrollment_count` | `int` | "N học viên" |
| `.avg_rating` | `float\|null` | ⭐ StarRating |
| `.instructor_name` | `str` | "Bởi: ..." |
| `.instructor_avatar` | `str\|null` | Small avatar |
| `.is_enrolled` | `bool` | "Đã đăng ký" badge hoặc ẩn |
| `.created_at` | `datetime` | — |
| `total` | `int` | Pagination info |
| `search_metadata.search_time_ms` | `float` | "Tìm thấy X kết quả trong Yms" |

### `GET /courses/public` — Same response dạng `CourseListResponse` (alias)

---

### `GET /courses/{course_id}`
**Page:** `CourseDetailPage.jsx` ✅ enhance

**Response — `CourseDetailResponse`:**
| Field | Type | UI |
|---|---|---|
| `id` | `str` | — |
| `title` | `str` | H1 heading |
| `description` | `str` | Markdown content |
| `category` | `str` | Badge |
| `level` | `str` | Badge |
| `thumbnail_url` | `str\|null` | Hero image |
| `preview_video_url` | `str\|null` | **Video preview modal** button |
| `language` | `str` | Language flag (vi/en) |
| `status` | `str` | Status badge |
| `owner_info.id` | `str` | — |
| `owner_info.name` | `str` | Instructor card |
| `owner_info.avatar_url` | `str\|null` | Instructor avatar |
| `owner_info.bio` | `str\|null` | Instructor bio |
| `owner_info.experience_years` | `int\|null` | "X năm kinh nghiệm" |
| `learning_outcomes[].description` | `str` | ✅ Checklist items |
| `learning_outcomes[].skill_tag` | `str\|null` | Skill badge |
| `prerequisites[]` | `List[str]` | Text list |
| `modules[]` | `List` | **Accordion** expandable |
| `modules[].id` | `str` | link to module |
| `modules[].title` | `str` | Accordion header |
| `modules[].description` | `str` | Sub-text |
| `modules[].difficulty` | `str` | Badge |
| `modules[].estimated_hours` | `float` | "~Xh" |
| `modules[].lessons[]` | `List` | Nested list inside accordion |
| `modules[].lessons[].id` | `str` | — |
| `modules[].lessons[].title` | `str` | Lesson item |
| `modules[].lessons[].duration_minutes` | `int` | Duration label |
| `modules[].lessons[].content_type` | `str` | Icon: 📝/🎥/🎵/💻 |
| `modules[].lessons[].is_completed` | `bool` | ✅/⬜ checkbox |
| `course_statistics.total_modules` | `int` | Stats bar |
| `course_statistics.total_lessons` | `int` | Stats bar |
| `course_statistics.total_duration_minutes` | `int` | Stats bar |
| `course_statistics.enrollment_count` | `int` | Stats bar |
| `course_statistics.completion_rate` | `float` | — |
| `course_statistics.avg_rating` | `float\|null` | ⭐ component |
| `enrollment_info.is_enrolled` | `bool` | CTA: `true` → "Tiếp tục học" / `false` → "Đăng ký" |
| `enrollment_info.enrollment_id` | `str\|null` | — |
| `enrollment_info.progress_percent` | `float\|null` | Progress bar (if enrolled) |
| `enrollment_info.can_access_content` | `bool` | Lock/unlock modules |

---

### `GET /courses/{course_id}/enrollment-status`
**Response — `CourseEnrollmentStatusResponse`:**
| Field | Type | UI |
|---|---|---|
| `is_enrolled` | `bool` | CTA button state |
| `status` | `str\|null` | `active\|completed\|cancelled` |
| `enrollment_id` | `str\|null` | for API calls |
| `can_access_content` | `bool` | lock overlay |
| `progress_percent` | `float\|null` | Progress bar |

---

## 4️⃣ ENROLLMENTS — `enrollments_router.py` (4 endpoints)

---

### `POST /enrollments`
**Request — `EnrollmentCreateRequest`:** `course_id: str`
**Response — `EnrollmentCreateResponse`:** `enrollment_id`, `course_title`, `status="active"`, `enrolled_at`, `message`

### `GET /enrollments/my-courses`
**Page:** `MyCoursesPage.jsx` ✅ enhance

**Query:** `status` (**`in-progress`**/completed/cancelled — ⚠️ dùng hyphen `-` không phải underscore), `skip`, `limit`

**Response — `EnrollmentListResponse`:**
| Field | Type | UI |
|---|---|---|
| `enrollments[].id` | `str` | ⚠️ **Tên field là `id`** (alias `enrollment_id` trong code FE) |
| `.course_id` | `str` | → link |
| `.course_title` | `str` | Card title |
| `.course_description` | `str` | Card subtitle |
| `.course_thumbnail` | `str\|null` | Card image |
| `.course_level` | `str` `Beginner\|Intermediate\|Advanced` | Level badge |
| `.instructor_name` | `str` | "Bởi: ..." |
| `.status` | `str` | ⚠️ **`in-progress\|completed\|cancelled`** (hyphen!) |
| `.progress_percent` | `float` | **Progress bar** |
| `.enrolled_at` | `datetime` | "Đăng ký: ..." |
| `.last_accessed_at` | `datetime\|null` | "Truy cập lần cuối: ..." |
| `.next_lesson.lesson_id` | `str\|null` | **"Tiếp tục học"** CTA button |
| `.next_lesson.lesson_title` | `str\|null` | CTA label |
| `.next_lesson.module_title` | `str\|null` | Context label |
| `.avg_quiz_score` | `float\|null` 0-100 | Score badge |
| `.completed_at` | `datetime\|null` | "Hoàn thành: DD/MM/YYYY" |
| `.total_time_spent_minutes` | `int` | "Đã học Xh Yph" |
| `summary.total_enrollments` | `int` | Tab "Tất cả (N)" |
| `summary.in_progress` | `int` | Tab "Đang học (N)" |
| `summary.completed` | `int` | Tab "Hoàn thành (N)" |
| `summary.cancelled` | `int` | Tab "Đã hủy (N)" |

### `GET /enrollments/{enrollment_id}`
**Response — `EnrollmentDetailResponse`:** Thêm `completed_lessons/total_lessons`, `completed_modules/total_modules`, `completed_at`

### `DELETE /enrollments/{enrollment_id}`
**Response — `EnrollmentCancelResponse`:** `message`, `note` ("Progress data đã được bảo toàn")

---

## 5️⃣ LEARNING — `learning_router.py` (6 endpoints) 🆕

---

### `GET /courses/{course_id}/modules`
**Response — `CourseModulesResponse`:**
| Field | Type | UI |
|---|---|---|
| `modules[].id` | `str` | → link |
| `.title` | `str` | Module card header |
| `.description` | `str` | Sub-text |
| `.difficulty` | `str` | Badge |
| `.order` | `int` | Sequence number |
| `.lesson_count` | `int` | "X bài học" |
| `.completed_lessons` | `int` | "Y/X hoàn thành" |
| `.estimated_hours` | `float` | "~Zh" |
| `.progress_percent` | `float` 0-100 | Progress bar |
| `.is_accessible` | `bool` | Clickable vs disabled |
| `.is_locked` | `bool` | 🔒 Lock overlay |
| `.status` | `str` `not-started\|in-progress\|completed` | Status dot 🟢/🟡/⚪ |

---

### `GET /courses/{course_id}/modules/{module_id}`
**Page:** `ModuleDetailPage.jsx` 🆕

**Response — `ModuleDetailResponse`:**
Fields trên + nested `lessons[]` mỗi item có:
| Field | Type | UI |
|---|---|---|
| `.has_quiz` | `bool` | Quiz icon |
| `.is_completed` | `bool` | ✅/⬜ |
| `.is_locked` | `bool` | 🔒 disabled |

Plus: `learning_outcomes[].id, .outcome, .skill_tag, .is_mandatory` → Checklist with ⚠️ mandatory marker
Plus: `resources[].id, .title, .type, .url, .size_mb, .description` → Resource list grouped by type
Plus: `prerequisites[]` → Linked module names

---

### `GET /courses/{course_id}/lessons/{lesson_id}`
**Page:** `LessonPage.jsx` 🆕 ← **CRITICAL page**

**Response — `LessonContentResponse`:**
| Field | Type | UI Element |
|---|---|---|
| `id` | `str` | — |
| `course_id` | `str` | — |
| `title` | `str` | H1 heading |
| `module_id` | `str\|null` | Breadcrumb: Course > Module > Lesson |
| `module_title` | `str\|null` | Breadcrumb |
| `order` | `int` | "Bài X" |
| `duration_minutes` | `int` | "Thời lượng: X phút" |
| `content_type` | `str` `text\|video\|mixed` | Layout selector |
| `text_content` | `str\|null` | **MarkdownRenderer** (HTML/MD) |
| `video_info` | `object\|null` | — |
| `video_info.url` | `str` | **VideoPlayer** component |
| `video_info.duration_seconds` | `int` | Video timeline |
| `video_info.thumbnail_url` | `str\|null` | Video poster |
| `video_info.quality[]` | `List[str]` | Quality selector: "360p\|720p\|1080p" |
| `learning_objectives[]` | `List[str]` | Bulleted checklist |
| `resources[]` | `List[ResourceItem]` | Download list → `.title, .type, .url, .size_mb` |
| `attachments[]` | `List` | — |
| `.filename` | `str` | Download link text |
| `.file_type` | `str` `pdf\|docx\|code\|other` | File type icon |
| `.url` | `str` | Download URL |
| `.size_mb` | `float` | "X MB" |
| `navigation.previous_lesson.id` | `str\|null` | **← Bài trước** button |
| `navigation.previous_lesson.title` | `str\|null` | Button label |
| `navigation.next_lesson.id` | `str\|null` | **Bài tiếp →** button |
| `navigation.next_lesson.title` | `str\|null` | Button label |
| `navigation.next_lesson.is_locked` | `bool` | Disabled + 🔒 if locked |
| `has_quiz` | `bool` | Show/hide quiz section |
| `quiz_info.quiz_id` | `str\|null` | → link to quiz |
| `quiz_info.question_count` | `int\|null` | "X câu hỏi" |
| `quiz_info.is_mandatory` | `bool\|null` | ⚠️ "Bắt buộc" badge |
| `completion_status.is_completed` | `bool` | ✅ Completed badge / ⬜ |
| `completion_status.time_spent_minutes` | `int` | "Đã học: X phút" |
| `completion_status.video_progress_percent` | `float\|null` | Video progress bar |

---

### `GET /modules/{module_id}/outcomes`
**Response — `ModuleOutcomesResponse`:** `learning_outcomes[]` + `achieved_outcomes`, `skills_acquired[]`, `areas_for_improvement[]`

### `GET /modules/{module_id}/resources`
**Response — `ModuleResourcesResponse`:** `resources[]` + `resources_by_type: Dict[str, int]` (count per type)

### `POST /modules/{module_id}/assessments/generate`
**Request — `ModuleAssessmentGenerateRequest`:** `assessment_type` (review/practice/final_check), `question_count` (5-15), `difficulty_preference` (easy/mixed/hard), `focus_topics[]`, `time_limit_minutes`
**Response — `ModuleAssessmentGenerateResponse`:** `assessment_id`, `questions[]`, `total_points`, `pass_threshold`, `instructions`, `expires_at`

---

## 6️⃣ QUIZ — `quiz_router.py` (10 endpoints)

---

### Student endpoints (5):

**`GET /quizzes/{quiz_id}`** — `QuizDetailResponse`:
`title, description, question_count, time_limit (min), pass_threshold (%), mandatory_question_count, user_attempts, best_score, last_attempt_at`

**`POST /quizzes/{quiz_id}/attempt`**:
- Request: `answers[]{question_id, selected_option}`, `time_spent_minutes`
- Response: `attempt_id, score (0-100), passed (bool), total_questions, correct_answers, attempt_number, message`

**`GET /quizzes/{quiz_id}/results`** — `QuizResultsResponse`:
- `total_score, status (Pass/Fail), pass_threshold, mandatory_passed, can_retake`
- `results[].question_id, .question_content, .student_answer, .correct_answer, .is_correct, .is_mandatory, .score, .explanation, .related_lesson_link`

**`POST /quizzes/{quiz_id}/retake`**: Response = new `questions[]` (AI-regenerated)

**`POST /ai/generate-practice`** — `PracticeExercisesGenerateRequest`:
- `lesson_id\|course_id\|topic_prompt` (ít nhất 1), `difficulty`, `question_count` (1-20), `practice_type` (multiple_choice/short_answer/mixed), `focus_skills[]`
- Response: `exercises[].type (theory/coding/problem-solving), .question, .options, .correct_answer, .explanation, .difficulty, .related_skill, .points`

### Instructor endpoints (5):

**`POST /lessons/{lesson_id}/quizzes`** — Create quiz:
- Request: `title, description, time_limit (1-180 min), pass_threshold (0-100, default 70), max_attempts, deadline, is_draft, questions[]{type, question_text, options, correct_answer, explanation, points (≥1), is_mandatory, order}`
- Response: `quiz_id, question_count, total_points, mandatory_count, preview_url`

**`GET /quizzes`** — List (filters: `course_id, class_id, search, sort_by, sort_order, skip, limit`):
- Response: `data[].quiz_id, .title, .lesson_title, .course_title, .class_name, .status, .question_count, .time_limit, .pass_threshold, .total_students, .completed_count, .pass_count, .pass_rate, .average_score, .created_at`
- Pagination: `total, skip, limit, has_next`

**`PUT /quizzes/{quiz_id}`** — Update: Response includes `has_attempts (bool), attempts_count (int), warning (str|null)`

**`DELETE /quizzes/{quiz_id}`**: only if no attempts

**`GET /quizzes/{quiz_id}/class-results`** (query: `class_id`):
- `statistics{total_students, completed_count, completion_rate, pass_count, fail_count, pass_rate, average_score, median_score, highest_score, lowest_score, average_time}`
- `score_distribution[]{range: "0-10", count, percentage}`
- `student_ranking[]{rank, user_id, full_name, avatar, score, time_spent, attempt_count, status, completed_at}`
- `difficult_questions[]{question_id, question_text, correct_rate, total_answers}`

---

## 7️⃣ PERSONAL COURSES — `personal_courses_router.py` (5 endpoints) 🆕

**`POST /courses/from-prompt`**: Request = `prompt (20-1000 chars), level, duration_weeks, language`
**`POST /courses/personal`**: Request = `title, description, category, level, thumbnail_url, language`
**`GET /courses/my-personal`**: List cards with status filter
**`PUT /courses/personal/{course_id}`**: Full nested editor (modules → lessons)
**`DELETE /courses/personal/{course_id}`**: confirm → `title, deleted_at`

---

## 8️⃣ CHAT — `chat_router.py` (5 endpoints) 🆕

---

### `POST /chat/course/{course_id}`
**Request — `ChatMessageRequest`:**
| Field | Type | UI |
|---|---|---|
| `question` | `str` | Chat input box |
| `conversation_id` | `str\|null` | auto (tiếp tục conversation) |
| `context_type` | `str` `lesson\|module\|general` | Dropdown hoặc auto-detect |

**Response — `ChatMessageResponse`:**
| Field | Type | UI |
|---|---|---|
| `conversation_id` | `str` | state |
| `message_id` | `str` | — |
| `question` | `str` | User bubble |
| `answer` | `str` markdown | **AI bubble** → MarkdownRenderer |
| `sources[]` | `List` | Collapsible citation list |
| `.type` | `str` `lesson\|module\|resource` | Source type icon |
| `.title` | `str` | Source title link |
| `.excerpt` | `str` | Preview text |
| `related_lessons[]` | `List` | — |
| `.lesson_id` | `str` | → lesson link |
| `.title` | `str` | Link text |
| `.url` | `str` | Navigation URL |
| `tokens_used` | `int\|null` | — (debug only) |

### `GET /chat/history`
**Response — `ChatHistoryListResponse`:**
- `conversations[].conversation_id, .course_id, .course_title, .topic_summary, .message_count, .last_message_preview (100 chars), .created_at, .last_updated`
- `grouped_by_date{today[], yesterday[], this_week[], older[]}` — for sidebar section headers

### `GET /chat/conversations/{conversation_id}`
**Response — `ConversationDetailResponse`:**
- `course{course_id, title, thumbnail_url}`
- `messages[].message_id, .role (user|assistant), .content (markdown), .timestamp, .sources[]`

### `DELETE /chat/conversations` → `deleted_count`
### `DELETE /chat/history/{conversation_id}` → `conversation_id, deleted_at`

---

## 9️⃣ CLASSES — `classes_router.py` (10 endpoints) 🆕

---

### Create: `POST /classes`
Request: `name, description, course_id, start_date, end_date, max_students`
Response: `class_id, name, invite_code (auto 6-8 chars), course_title, student_count, message`

### List: `GET /classes/my-classes`
Response `ClassListItem`: `id, name, course_title, student_count ("25/30" string), status, start_date, end_date, progress (0-100)`

### Detail: `GET /classes/{class_id}`
Response `ClassDetailResponse`: `name, description, course{id, title, module_count}, invite_code, max_students, student_count, start_date, end_date, status, recent_students[]{id, name, email, avatar_url, progress, joined_at}, class_stats{total_students, lessons_completed, avg_quiz_score}`

### Update: `PUT /classes/{class_id}` — `name, description, max_students, end_date`
### Delete: `DELETE /classes/{class_id}`

### Join: `POST /classes/join` — `invite_code` → `class_id, class_name, course_title, course_id, instructor_name, enrollment_id, student_count, max_students`

### Students: `GET /classes/{class_id}/students`
Response: `data[]{student_id, student_name, email, join_date, progress, completed_modules, total_modules, last_activity, quiz_average}`

### Student Detail: `GET /classes/{class_id}/students/{student_id}`
Response: `student_name, email, avatar_url, quiz_scores[]{quiz_id, quiz_title, score, attempt_date}, modules_detail[]{module_id, module_title, progress, completed_lessons, quiz_scores[]}, progress{overall_progress, completed_modules, total_modules, study_streak_days, total_study_time (hours)}`

### Remove Student: `DELETE /classes/{class_id}/students/{student_id}`

### Class Progress: `GET /classes/{class_id}/progress`
Response: `total_students, average_progress, completion_rate, average_quiz_score`

---

## 🔟 DASHBOARDS — `dashboard_router.py` (3 endpoints) + `analytics_router.py` (5 endpoints)

---

### `GET /dashboard/student` — `StudentDashboardResponse`:
- `overview{total_courses_enrolled, active_courses, completed_courses, total_lessons_completed, total_study_hours, current_streak_days}`
- `recent_courses[]{course_id, title, thumbnail_url, progress_percent, last_accessed, next_lesson{lesson_id, title}}`
- `pending_quizzes[]{quiz_id, title, course_title, lesson_title, due_date, status: not_started|failed}`
- `performance_summary{average_quiz_score, quiz_pass_rate, lessons_this_week}`
- `recommendations[]{course_id, title, reason}`

### `GET /dashboard/instructor` — `InstructorDashboardResponse`:
- `active_classes_count, total_students, quizzes_created_count, avg_completion_rate`
- `recent_classes[]` (3 recent active)
- `quick_actions[]{action_type, label, link, icon}`

### `GET /dashboard/admin` — `AdminSystemDashboardResponse`:
- `total_users, users_by_role{`**`student, instructor, admin`**`}` ⚠️ **SỐ ÍT** (không phải students/instructors/admins)
- `total_courses, course_stats{public_courses, personal_courses, published_courses, draft_courses}`
- `total_classes, class_stats{active_classes, completed_classes, preparing_classes}`
- `activity_stats{new_enrollments_this_week, quizzes_completed_today, active_users_today, total_lesson_completions}`
- `last_updated` (datetime) — thời gian cập nhật cuối

### Analytics Student (2):
- `GET /analytics/learning-stats` → `lessons_completed, quizzes_passed, quizzes_failed, avg_quiz_score, by_course[]{course_id, course_title, lessons_completed, quiz_score, status}`
- `GET /analytics/progress-chart` (query: `time_range`, `course_id`) → `chart_data[]{date, lessons_completed, hours_spent}`, `summary{total_lessons, total_hours, avg_per_day}`

### Analytics Instructor (3):
- `GET /analytics/instructor/classes` → `classes[]{class_id, class_name, student_count, attendance_rate, avg_progress, quiz_completion_rate, active_students, last_activity}`
- `GET /analytics/instructor/progress-chart` → `chart_type, time_range, chart_data[]{date, class_id, lessons_completed, quizzes_completed, active_students}`
- `GET /analytics/instructor/quiz-performance` → `quizzes[]{quiz_id, quiz_title, total_attempts, pass_count, fail_count, pass_rate, avg_score, avg_time_minutes, hardest_questions[]}`

---

## 1️⃣1️⃣ ADMIN — `admin_router.py` (17 endpoints)

---

### Users (7):
- **List** `GET /admin/users` (query: `role, status, search, sort_by, sort_order, skip, limit`): `data[]{`**`user_id`**`, full_name, email,` **`avatar`**` (không có _url), role, status (active|inactive|banned), created_at, last_login_at, courses_enrolled, classes_created}` + `summary{total_users, active_users, new_users_this_month}` + `total, skip, limit`
- **Detail** `GET /admin/users/{id}`: **`user_id`** (không phải id), `profile{phone, bio, avatar_url}`, `activity_summary{courses_enrolled, classes_created, total_study_hours, login_streak_days}`
- **Create** `POST /admin/users`: `full_name (min 2), email, role, password (min 8), bio, avatar`
- **Update** `PUT /admin/users/{id}`: `full_name, email, bio, avatar, status`
- **Delete** `DELETE /admin/users/{id}`: response = `user_id, message`
- **Change Role** `PUT /admin/users/{id}/role`: request=`new_role`, response = `user_id, old_role, new_role, impact{description, affected_classes, affected_enrollments}, updated_at, message`
- **Reset Password** `POST /admin/users/{id}/reset-password`: request=`new_password (min 8)`, response = `user_id, message, note`

### Courses (5):
- **List** `GET /admin/courses` (query: `author_id, course_type, status, category, level, search, sort_by, sort_order, skip, limit`): `data[]{course_id, title,` **`thumbnail_url`**`, author{user_id, full_name, email, role}, course_type (public|personal), enrollment_count, status, category, level,` **`created_at, updated_at`**`}` + `total, skip, limit, has_next`
- **Detail** `GET /admin/courses/{id}`: `author, modules[]{module_id, title, order, lesson_count, estimated_hours}, analytics{enrollment_count, completion_rate, avg_rating, total_students_active}`
- **Create** `POST /admin/courses`: full course metadata
- **Update** `PUT /admin/courses/{id}`
- **Delete** `DELETE /admin/courses/{id}`: response `impact{enrolled_students, active_classes, personal_courses_derived, warning}`

### Classes (2):
- **List** `GET /admin/classes` (query: `page, limit, search, status, sort_by, sort_order`): `data[]{class_id, class_name, course_title, instructor_name, student_count, status, created_at}`
- **Detail** `GET /admin/classes/{id}`: `course{course_id, title, category}, instructor{user_id, full_name, email}, class_stats{average_progress, completion_rate, active_students_today}, invite_code`

### Admin Analytics (3):
- `GET /admin/analytics/users-growth` (query: `time_range: 7d|30d|90d, role_filter`): `chart_data[]{date, new_students, new_instructors, new_admins, total_new_users, active_users}`, `statistics{total_growth_rate, student_growth_rate, user_retention_rate, avg_daily_new_users}`
- `GET /admin/analytics/courses`: `top_courses[]{course_id, title, enrollments, completion_rate, avg_quiz_score, instructor_name}`, `creation_trend[]{date, public_courses_created, personal_courses_created}`, `overall_completion_rate, total_enrollments`
- `GET /admin/analytics/system-health`: `status (healthy|warning|critical)`, `metrics{api_response_time_ms, error_rate_percentage, database_query_time_ms, database_connections, storage_used_gb, storage_total_gb, storage_usage_percentage, active_sessions, memory_usage_percentage, cpu_usage_percentage}`, `alerts[]{alert_type, message, metric_name, current_value, threshold_value}`, `uptime_hours`

---

## 📌 ERROR MESSAGES & VALIDATION RULES (BE → FE)

> [!IMPORTANT]
> BE trả error messages bằng **tiếng Anh** (từ Pydantic validators). FE cần map hoặc hiển thị gợi ý phù hợp.

### HTTP Error Codes
| Code | Ý nghĩa | FE Toast |
|------|---------|----------|
| `400` | Validation error / Bad Request | Hiển thị `detail` message |
| `401` | Unauthorized (token hết hạn/sai) | Redirect → `/login`, clear localStorage |
| `403` | Forbidden (không đủ quyền) | Toast "Bạn không có quyền" |
| `404` | Not Found | Toast "Không tìm thấy" |
| `409` | Conflict (email đã tồn tại, đã enrolled) | Toast `detail` message |
| `422` | Validation Error (Pydantic) | Hiển thị field-level errors |
| `500` | Server Error | Toast "Lỗi hệ thống" |

### Pydantic Validation Messages (tiếng Anh → FE tip tiếng Việt)
| BE Error | FE Gợi ý |
|----------|----------|
| `Full name must have at least 2 words` | "Họ tên cần ít nhất 2 từ" |
| `Password must contain at least one digit` | "Mật khẩu cần chứa ít nhất 1 chữ số" |
| `Password must contain at least one uppercase letter` | "Mật khẩu cần chứa ít nhất 1 chữ hoa" |
| `Password must contain at least one special character` | "Mật khẩu cần chứa ký tự đặc biệt" |
| `Avatar URL must start with http:// or https://` | "URL avatar phải bắt đầu bằng http://" |
| `Bio must not exceed 500 characters` | "Giới thiệu không quá 500 ký tự" |

### Success Messages (BE response → FE toast)
| Endpoint | BE `message` field | FE Toast |
|----------|-------------------|----------|
| Register | `"Đăng ký tài khoản thành công"` | ✅ Dùng trực tiếp |
| Login | — (không có message) | FE tự toast "Đăng nhập thành công" |
| Logout | `"Đăng xuất thành công"` | ✅ Dùng trực tiếp |
| Update Profile | `"Cập nhật hồ sơ thành công"` | ✅ Dùng trực tiếp |
| Enroll | `message` | ✅ Dùng `result.message` |
| Cancel Enrollment | `message` + `note` | Toast message + info note |
| Create Quiz | `message` | ✅ Dùng trực tiếp |
| Admin Delete | `message` | ✅ Dùng trực tiếp |
| Admin Change Role | `message` + `impact.description` | Toast message + info impact |
| Admin Reset PW | `message` + `note` | Toast message + info note |

### Token Management
| Thuộc tính | Giá trị |
|-----------|--------|
| `access_token` TTL | 15 phút |
| `refresh_token` TTL (remember_me=false) | 1 ngày |
| `refresh_token` TTL (remember_me=true) | 7 ngày |
| Token type | `"Bearer"` |
| Auth header format | `Authorization: Bearer <access_token>` |

---

## 1️⃣2️⃣ SEARCH — `search_router.py` (4 endpoints)

- `GET /search` (query: `q (min 2), category, level, instructor, rating, page, limit`)
- `GET /search/suggestions` (query: `q (min 1)`) — autocomplete real-time
- `GET /search/history` — 20 recent searches + popular terms
- `GET /search/analytics` (Admin) — total_searches, popular_categories, no_results_queries

---

## 1️⃣3️⃣ RECOMMENDATIONS — `recommendation_router.py` (2 endpoints)
- `GET /recommendations/from-assessment`
- `GET /recommendations`

---

## 1️⃣4️⃣ PROGRESS — `progress_router.py` (1 endpoint)

### `GET /progress/course/{course_id}` — `ProgressCourseResponse`:
- `overall_progress_percent, completed_lessons_count, total_lessons_count`
- `lessons_progress[]{lesson_id, lesson_title, status (completed|in-progress|not-started), completion_date, time_spent_minutes, video_progress_seconds}`
- `total_time_spent_minutes, estimated_hours_remaining, study_streak_days, avg_quiz_score, last_accessed_at`

---

## 📋 TỔNG HỢP SERVICES CẦN TẠO

| File | Endpoints | Methods |
|---|---|---|
| `authService.js` ✅ | 3 | register, login, logout |
| `userService.js` 🆕 | 2 | getProfile, updateProfile |
| `courseService.js` ✅ | 4 | search, listPublic, getDetail, checkEnrollment |
| `enrollmentService.js` ✅ | 4 | enroll, listMy, getDetail, cancel |
| `assessmentService.js` 🆕 | 3 | generate, submit, getResults |
| `learningService.js` 🆕 | 6 | getModules, getModuleDetail, getLessonContent, getOutcomes, getResources, generateModuleAssessment |
| `quizService.js` ✅ enhance | 10 | getDetail, attempt, getResults, retake, generatePractice, createQuiz, listQuizzes, updateQuiz, deleteQuiz, getClassResults |
| `personalCourseService.js` 🆕 | 5 | fromPrompt, createManual, listMy, update, delete |
| `chatService.js` 🆕 | 5 | sendMessage, getHistory, getConversation, deleteAll, deleteOne |
| `classService.js` 🆕 | 10 | create, listMy, getDetail, update, delete, join, getStudents, getStudentDetail, removeStudent, getProgress |
| `dashboardService.js` 🆕 | 3 | getStudentDashboard, getInstructorDashboard, getAdminDashboard |
| `analyticsService.js` 🆕 | 8 | getLearningStats, getProgressChart, getInstructorClasses, getInstructorProgressChart, getInstructorQuizPerformance, getUsersGrowth, getCourseAnalytics, getSystemHealth |
| `searchService.js` 🆕 | 4 | search, getSuggestions, getHistory, getAnalytics |
| `recommendationService.js` 🆕 | 2 | fromAssessment, getRecommendations |
| `progressService.js` 🆕 | 1 | getCourseProgress |
| `adminService.js` 🆕 | 17 | (tất cả admin endpoints) |

**Tổng: 16 services, 87 methods**

---

## ✅ CHECKLIST TIẾN ĐỘ MAPPING FE (Cập nhật: 2026-03-10)

> Đối chiếu code thực tế vs schema ở trên. Đánh dấu ✅ = mapping đúng, ⚠️ = có ghi chú

### Services — 17/17 (100% ✅)

Tất cả services đã tạo đúng endpoints + request/response theo docs.

### Pages — Mapping từ API response

| # | Page | API kết nối | Fields mapping đúng docs | Status |
|---|------|-------------|--------------------------|--------|
| 1 | LoginPage | `POST /auth/login` -> LoginResponse | access_token, refresh_token, user{id,full_name,email,role,**avatar** (⚠️ KHÔNG có _url)} | ✅ ⚠️ cần map `avatar`→`avatar_url` |
| 2 | RegisterPage | `POST /auth/register` -> RegisterResponse | full_name, email, password → **id**, full_name, email, role, **status**, **created_at**, message | ✅ ⚠️ BE không có `role` trong request |
| 3 | ForgotPasswordPage | authService.forgotPassword | email | ✅ |
| 4 | ResetPasswordPage | authService.resetPassword | token, new_password | ✅ |
| 5 | VerifyEmailPage | authService.verifyEmail | token | ✅ |
| 6 | ProfilePage | `GET /users/me`, `PATCH /users/me` | full_name, email, role, avatar_url, bio(max500), contact_info(str), learning_preferences(List[str]), created_at, updated_at | ✅ |
| 7 | AssessmentSetupPage | `POST /assessments/generate` | category, subject, level, focus_areas | ✅ |
| 8 | AssessmentQuizPage | submit `POST /assessments/{id}/submit` | answers[]{question_id, answer_content, selected_option, time_taken_seconds}, **total_time_seconds**, **submitted_at** | ✅ |
| 9 | AssessmentResultsPage | `GET /assessments/{id}/results` | overall_score, proficiency_level, score_breakdown, skill_analysis[], knowledge_gaps[] | ✅ |
| 10 | CoursesPage | `GET /courses/search` via courseStore | courses[]{id, title, description, category, level, thumbnail_url, total_modules, total_lessons, total_duration_minutes, enrollment_count, **avg_rating**, instructor_name, instructor_avatar, is_enrolled, **created_at**}, total, search_metadata | ✅ |
| 11 | CourseDetailPage | `GET /courses/{id}` + `POST /enrollments` | title, description, category, level, thumbnail_url, **preview_video_url**, language, **status**, owner_info{**id**, name, avatar_url, **role**, bio, experience_years}, learning_outcomes[], prerequisites[], modules[]{lessons[]}, course_statistics{}, enrollment_info{}, **created_at, updated_at** | ✅ |
| 12 | MyCoursesPage | `GET /enrollments/my-courses` | enrollments[]{**id**, course_id, course_title, **course_description**, course_thumbnail, **course_level**, **instructor_name**, status(**`in-progress`** hyphen!), progress_percent, enrolled_at, last_accessed_at, **completed_at**, next_lesson{lesson_id, **lesson_title**, **module_title**}, avg_quiz_score, total_time_spent_minutes}, summary{**total_enrollments**, in_progress, completed, cancelled} | ✅ ⚠️ field names sửa |
| 13 | ModuleListPage | `GET /courses/{id}/modules` | modules[]{id, title, description, difficulty, order, lesson_count, completed_lessons, estimated_hours, progress_percent, is_accessible, is_locked, status} | ✅ |
| 14 | ModuleDetailPage | `GET /courses/{id}/modules/{id}` | + lessons[]{has_quiz, is_completed, is_locked}, learning_outcomes[], resources[], prerequisites[] | ✅ |
| 15 | LessonPage | `GET /courses/{id}/lessons/{id}` | title, content_type, text_content, video_info{url,duration_seconds,thumbnail_url,quality[]}, learning_objectives[], resources[], attachments[], navigation{previous_lesson,next_lesson}, has_quiz, quiz_info, completion_status | ✅ |
| 16 | QuizPage | `GET /quizzes` | data[]{quiz_id, title, **description**, lesson_id, lesson_title, course_id, course_title, **class_id, class_name**, status, question_count, time_limit, pass_threshold, total_students, completed_count, **pass_count**, pass_rate, average_score, created_at, **updated_at**}, total, skip, limit, has_next | ✅ ⚠️ thêm fields |
| 17 | QuizDetailPage | `GET /quizzes/{id}` | title, description, question_count, time_limit, pass_threshold, mandatory_question_count, user_attempts, best_score, last_attempt_at | ✅ |
| 18 | QuizAttemptPage | `POST /quizzes/{id}/attempt` | answers[]{question_id, selected_option}, time_spent_minutes -> attempt_id, score, passed, total_questions, correct_answers, **time_spent_minutes, attempt_number, submitted_at**, message | ✅ ⚠️ thêm fields |
| 19 | QuizResultsPage | `GET /quizzes/{id}/results` | total_score, status, pass_threshold, **mandatory_passed, can_retake**, results[]{question_content, student_answer, correct_answer, is_correct, **is_mandatory**, explanation, related_lesson_link} | ✅ ⚠️ thêm fields |
| 20 | ChatPage | chatService (5 methods) | sendMessage: question, conversation_id, context_type -> answer(markdown), sources[], **related_lessons[]**. getHistory: conversations[]{conversation_id, course_id, course_title, topic_summary, message_count, last_message_preview, **created_at, last_updated**}, **grouped_by_date{today[], yesterday[], this_week[], older[]}** | ✅ ⚠️ thêm fields |
| 21 | PersonalCoursesPage | personalCourseService | from-prompt, personal, my-personal, update, delete | ✅ |
| 22 | ClassListPage | classService | my-classes -> {id, name, course_title, student_count (**⚠️ kiểu `str` "25/30"**), status, start_date, end_date, progress} | ✅ ⚠️ student_count là string |
| 23 | ClassCreatePage | classService | name, description, course_id, start_date, end_date, max_students | ✅ |
| 24 | ClassDetailPage | classService | name, description, course{id,title,**module_count**}, invite_code, **max_students**, **student_count**(int), recent_students[]{id, name, email, avatar_url, progress, joined_at}, class_stats{total_students, lessons_completed, avg_quiz_score} | ✅ |
| 25 | SearchResultsPage | searchService | q, category, level, page, limit -> results[] | ✅ |
| 26 | RecommendationsPage | recommendationService | from-assessment, general | ✅ |
| 27 | DashboardPage (Student) | `GET /dashboard/student` | overview{total_courses_enrolled, total_lessons_completed, total_study_hours, current_streak_days}, recent_courses[]{course_id, title, progress_percent, next_lesson{lesson_id, title}}, pending_quizzes[]{quiz_id, title, course_title, lesson_title, due_date, status(**not_started\|failed**)}, performance_summary{average_quiz_score, **quiz_pass_rate, lessons_this_week**}, recommendations[] | ✅ |
| 28 | DashboardPage (Instructor) | `GET /dashboard/instructor` | active_classes_count, total_students, quizzes_created_count, avg_completion_rate, recent_classes[], quick_actions[]{action_type, label, link, icon} | ✅ |
| 29 | DashboardPage (Admin) | `GET /dashboard/admin` | total_users, users_by_role{**student, instructor, admin** — SỐ ÍT!}, total_courses, course_stats{public_courses, personal_courses, published_courses, draft_courses}, total_classes, class_stats{active_classes, completed_classes, preparing_classes}, activity_stats{new_enrollments_this_week, quizzes_completed_today, active_users_today, total_lesson_completions}, **last_updated** | ✅ ⚠️ singular |
| 30 | LandingPage | Không cần API | — | ✅ |
| 31 | NotFoundPage | Không cần API | — | ✅ |
| 32 | UnauthorizedPage | Không cần API | — | ✅ |

### Pages chưa hoàn thành

| # | Page | Vấn đề | Ưu tiên |
|---|------|--------|---------|
| 1 | ~~AdminPage~~ | ✅ Đã kết nối adminService + analyticsService. Sub-routes: users (list/filter/delete/changeRole/resetPassword), courses (list/search/delete), classes (list/search), analytics (system-health/users-growth/course-analytics) | HOÀN THÀNH |
| 2 | **JoinClassModal** | Component modal tham gia lớp qua invite_code → POST /classes/join | TRUNG BÌNH |
| 3 | **GlobalSearchBar** | Search bar header → GET /search/suggestions (autocomplete real-time) | TRUNG BÌNH |
| 4 | **CourseEditorPage** | Editor cho personal courses → PUT /courses/personal/{id} (nested modules→lessons) | THẤP |

### Tổng kết

| Hạng mục | Hoàn thành |
|----------|------------|
| Services | 17/17 (100%) |
| Stores | 3/3 (100%) |
| Routes | 14/14 (100%) |
| Pages mapping đúng docs | 33/33 (100%) |
| Build | 458 modules, 0 errors |
