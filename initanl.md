# Báo Cáo Phân Tích `init_data.py` — AI Learning Platform

> **Mục tiêu**: Phân tích toàn bộ seed data pipeline, mapping entity ↔ schema ↔ API ↔ luồng xử lý.  
> **Phương pháp**: Dò từng dòng code, đối chiếu với `models/models.py` và `schemas/*.py`.  
> **Ngày phân tích**: 2026-05-23

---

## 0. Tổng Quan Kiến Trúc Seed

```
main()
 ├─ drop_all_collections()             # Reset toàn bộ 14 collections
 ├─ seed_users()                        # Stage 1: Users (3 roles)
 ├─ seed_courses_modules_lessons()      # Stage 2: Courses + Modules + Lessons
 ├─ seed_classes()                      # Stage 3: Classes (public courses only)
 ├─ seed_enrollments_progress()         # Stage 4: Enrollments + Progress
 ├─ sync_classes_with_enrollments()     # Stage 4b: Gắn student vào class
 ├─ seed_quizzes_attempts()             # Stage 5: Quizzes + QuizAttempts
 ├─ seed_assessments_recommendations()  # Stage 6: AssessmentSessions + Recommendations
 ├─ seed_conversations_tokens()         # Stage 7: Conversations + RefreshToken + PasswordResetToken
 └─ validate_integrity()               # Stage 8: Kiểm tra toàn vẹn dữ liệu
```

**Cấu hình seed** (`SeedConfig`, dòng 456–468):
| Tham số | Giá trị | Ghi chú |
|---|---|---|
| `seed` | 20260507 | Random seed deterministic |
| `admins` | 10 | Admin users |
| `instructors` | 40 | Instructor users |
| `students` | 360 | Student users |
| `public_courses` | 70 | Public courses |
| `personal_courses` | 80 | Personal courses (1 per student) |
| `public_modules_per_course` | 6 | Modules/public course |
| `public_lessons_per_module` | 6 | Lessons/module (public) |
| `personal_modules_per_course` | 4 | Modules/personal course |
| `personal_lessons_per_module` | 5 | Lessons/module (personal) |
| `classes` | 90 | Class sessions |

**Batch sizes** (dòng 667–678): BATCH_COURSES=50, BATCH_MODULES=200, BATCH_LESSONS=200, BATCH_USERS=250, BATCH_CLASSES=200, BATCH_ENROLLMENTS=400, BATCH_PROGRESS=120, BATCH_QUIZZES=200, BATCH_QUIZ_ATTEMPTS=250, BATCH_ASSESSMENTS=350, BATCH_RECOMMENDATIONS=250, BATCH_CONVERSATIONS=150, BATCH_TOKENS=500.

---

## 1. Entity: `User` (users collection)

### 1.1 Vị trí trong execution flow
**Stage 1** — `seed_users()` (dòng 713–788). Được tạo trước mọi entity khác.

### 1.2 Số lượng seed
- **Admin**: 10 documents
- **Instructor**: 40 documents
- **Student**: 360 documents
- **Tổng**: 410 Users

### 1.3 Schema seed thực tế (field-by-field)

| Field seed | Giá trị seed | Model field | Khớp? |
|---|---|---|---|
| `id` | `gid()` = UUID v4 | `id: str` (alias `_id`) | ✅ |
| `full_name` | `"Admin {fake.name()}"` / `fake.name()` | `full_name: str` | ✅ |
| `email` | `admin{i+1}@ailearning.vn` / `instructor{i+1}@ailearning.vn` / `student{i+1}@gmail.com` | `email: EmailStr` | ✅ |
| `hashed_password` | `hp("Admin@123456")` / `hp("Instructor@123")` / `hp("Student@123")` | `hashed_password: str` | ✅ |
| `role` | `"admin"` / `"instructor"` / `"student"` | `role: str` | ✅ |
| `status` | `sample_weighted([(active,0.9), (inactive,0.06), (banned,0.02), (suspended,0.02)])` | `status: str` | ✅ |
| `avatar_url` | `pick_avatar_url()` → Unsplash URL | `avatar_url: Optional[str]` | ✅ |
| `bio` | `fake.text(max_nb_chars=180–260)` | `bio: Optional[str]` max_length=500 | ✅ |
| `contact_info` | `fake.phone_number()` | `contact_info: Optional[str]` max_length=200 | ✅ |
| `learning_preferences` | `random.sample([...5 categories...], k=2–3)` | `learning_preferences: List[str]` | ✅ |
| `email_verified` | `random.random() < 0.94/0.86/0.82` | `email_verified: bool` | ✅ |
| `phone_verified` | `random.random() < 0.82/0.74/0.68` | `phone_verified: bool` | ✅ |
| `created_by` | Admin: không set; Instructor: random admin_id; Student: random(admin+instructor) | `created_by: Optional[str]` | ✅ |
| `created_at` | `past(120, 300)` / `past(90, 220)` / `past(30, 220)` | `created_at: datetime` | ✅ |
| `updated_at` | `past(5, 20)` / `past(1, 20)` | `updated_at: datetime` | ✅ |
| `last_login_at` | `past(0, 5)` / `past(0, 15)` / `past(0, 30)` | `last_login_at: Optional[datetime]` | ✅ |

**⚠️ Ghi chú**: Admin users không có `created_by`. Đây là đúng theo thiết kế (admin tự tạo hoặc system).

### 1.4 Model collection
```
Collection: users
Indexes: email, role, status, created_at, last_login_at
```

### 1.5 Schemas liên quan
- **Request**: `RegisterRequest` (auth.py), `AdminCreateUserRequest` (admin.py), `UserProfileUpdateRequest` (user.py)
- **Response**: `RegisterResponse`, `LoginResponse` + `UserInfo`, `UserProfileResponse`, `UserProfileUpdateResponse`, `AdminUserListItem`, `AdminUserDetailResponse`

### 1.6 APIs phục vụ
| API | Method | Path | Schema |
|---|---|---|---|
| Đăng ký | POST | `/api/v1/auth/register` | `RegisterRequest` → `RegisterResponse` |
| Đăng nhập | POST | `/api/v1/auth/login` | `LoginRequest` → `LoginResponse` |
| Refresh token | POST | `/api/v1/auth/refresh` | `RefreshTokenRequest` → `RefreshTokenResponse` |
| Đăng xuất | POST | `/api/v1/auth/logout` | — → `LogoutResponse` |
| Xem profile | GET | `/api/v1/users/me` | — → `UserProfileResponse` |
| Cập nhật profile | PATCH | `/api/v1/users/me` | `UserProfileUpdateRequest` → `UserProfileUpdateResponse` |
| Admin list users | GET | `/api/v1/admin/users` | — → `AdminUserListResponse` |
| Admin create user | POST | `/api/v1/admin/users` | `AdminCreateUserRequest` → `AdminCreateUserResponse` |
| Admin update user | PUT | `/api/v1/admin/users/{id}` | `AdminUpdateUserRequest` → `AdminUpdateUserResponse` |
| Admin delete user | DELETE | `/api/v1/admin/users/{id}` | — → `AdminDeleteUserResponse` |
| Admin change role | PATCH | `/api/v1/admin/users/{id}/role` | `AdminChangeRoleRequest` → `AdminChangeRoleResponse` |
| Admin reset password | POST | `/api/v1/admin/users/{id}/reset-password` | `AdminResetPasswordRequest` → `AdminResetPasswordResponse` |

---

## 2. Entity: `Course` (courses collection)

### 2.1 Vị trí trong execution flow
**Stage 2** — `seed_courses_modules_lessons()` (dòng 804–1082). Tạo đồng thời với Module và Lesson.

### 2.2 Số lượng seed
- **Public courses**: 70 documents (owner = admin/instructor)
- **Personal courses**: 80 documents (owner = student, tối đa 80 students)
- **Tổng**: 150 Courses

### 2.3 Schema seed thực tế (field-by-field)

**Public course** (dòng 917–946):

| Field seed | Giá trị seed | Model field | Khớp? |
|---|---|---|---|
| `id` | `gid()` | `id: str` | ✅ |
| `title` | `bp["title"]` (từ curriculum_content) | `title: str` | ✅ |
| `description` | `bp["description"]` | `description: str` | ✅ |
| `category` | `bp["category"]` (Programming/Math/Business/Languages) | `category: str` | ✅ |
| `level` | `bp["level"]` (Beginner/Intermediate/Advanced) | `level: str` | ✅ |
| `thumbnail_url` | `get_course_thumbnail(curriculum)` | `thumbnail_url: Optional[str]` | ✅ |
| `preview_video_url` | `get_course_preview_url(curriculum)` | `preview_video_url: Optional[str]` | ✅ |
| `language` | `random.choice(["vi", "en"])` | `language: str` | ✅ |
| `status` | `sample_weighted([(published,0.8), (draft,0.15), (archived,0.05)])` | `status: str` | ✅ |
| `owner_id` | `random.choice(admin_ids + instructor_ids)` | `owner_id: str` | ✅ |
| `owner_type` | `"admin"` hoặc `"instructor"` | `owner_type: str` | ✅ |
| `instructor_id` | `random.choice(instructor_ids)` | `instructor_id: Optional[str]` | ✅ |
| `instructor_name` | `f"Instructor {instructor_id[:6]}"` | `instructor_name: Optional[str]` | ⚠️ Denormalized string, không phải tên thật |
| `instructor_avatar` | `pick_avatar_url()` | `instructor_avatar: Optional[str]` | ✅ |
| `instructor_bio` | `fake.text(max_nb_chars=200)` | `instructor_bio: Optional[str]` | ✅ |
| `course_type` | `"public"` | `course_type: str` | ✅ |
| `learning_outcomes` | `get_course_learning_outcomes(curriculum)` hoặc `[mk_course_outcome()]` | `learning_outcomes: List[dict]` | ✅ |
| `prerequisites` | `get_course_prerequisites(curriculum)` | `prerequisites: List[str]` | ✅ |
| `modules` | `List[EmbeddedModule]` | `modules: List[EmbeddedModule]` | ✅ |
| `total_duration_minutes` | tổng mins của tất cả lessons | `total_duration_minutes: int` | ✅ |
| `total_modules` | `len(module_embeds)` = 6 | `total_modules: int` | ✅ |
| `total_lessons` | 6×6 = 36 | `total_lessons: int` | ✅ |
| `enrollment_count` | 0 (cập nhật lại ở Stage 4) | `enrollment_count: int` | ✅ |
| `avg_rating` | `round(random.uniform(3.5, 5.0), 1)` | `avg_rating: Optional[float]` | ✅ |
| `created_at` | `past(40, 220)` | `created_at: datetime` | ✅ |
| `updated_at` | `past(1, 20)` | `updated_at: datetime` | ✅ |

**Personal course** (dòng 1047–1075): Tương tự nhưng:
- `title`: `f"Personal - {bp['title']}"`
- `owner_id`: `student_id` (một trong 80 student được sample)
- `owner_type`: `"student"`
- `instructor_id`: **không set** (không có field này trong personal course seed)
- `course_type`: `"personal"`
- `status`: `sample_weighted([(published,0.45), (draft,0.5), (archived,0.05)])`
- `avg_rating`: `None`

**⚠️ Mismatch**: Personal course không set `instructor_id`. Model cho phép `Optional[str]` = None, nên không lỗi. Nhưng `instructor_name` vẫn được set = `f"Student Owner {student_id[:6]}"` — đây là giả lập, không phải instructor thật.

### 2.4 EmbeddedModule trong Course (dòng 898–915)

Mỗi `EmbeddedModule` là bản sao denormalized của `Module`:

| EmbeddedModule field | Nguồn |
|---|---|
| `id` | = Module.id |
| `title`, `description`, `order`, `difficulty`, `estimated_hours` | = Module fields |
| `learning_outcomes` | = Module.learning_outcomes |
| `prerequisites` | = Module.prerequisites |
| `resources` | = Module.resources |
| `lessons` | `List[EmbeddedLesson]` — xem §4 |
| `total_lessons`, `total_duration_minutes` | = Module fields |
| `created_at`, `updated_at` | = Module timestamps |

### 2.5 EmbeddedLesson trong EmbeddedModule (dòng 861–879)

Mỗi `EmbeddedLesson` là bản sao denormalized của `Lesson`:

| EmbeddedLesson field | Nguồn |
|---|---|
| `id` | = Lesson.id |
| `title`, `description`, `order`, `content`, `content_type` | = Lesson fields |
| `duration_minutes`, `video_url`, `audio_url` | = Lesson fields |
| `resources`, `learning_objectives` | = Lesson fields |
| `quiz_id` | `None` lúc seed (cập nhật sau ở Stage 5) |
| `is_published` | `True` |
| `created_at`, `updated_at` | = Lesson timestamps |

**⚠️ Quan trọng**: `audio_url` có trong `EmbeddedLesson` (dòng 871) cho **public courses** nhưng **không có** trong personal course EmbeddedLesson (dòng 992–1008). Đây là sự không nhất quán trong seed.

### 2.6 learning_outcomes structure (từ mk_course_outcome, dòng 523–527)
```python
{
    "description": fake.sentence(nb_words=10),
    "skill_tag": fake.slug().replace("-", "_")
}
```
Khớp với `LearningOutcome` schema trong `course.py`: `{description: str, skill_tag: Optional[str]}` ✅

### 2.7 APIs phục vụ
| API | Method | Path | Schema |
|---|---|---|---|
| Danh sách public courses | GET | `/api/v1/courses/public` | → `CourseListResponse` (alias `CourseSearchResponse`) |
| Tìm kiếm courses | GET | `/api/v1/courses/search` | → `CourseSearchResponse` |
| Chi tiết course | GET | `/api/v1/courses/{course_id}` | → `CourseDetailResponse` |
| Kiểm tra enrollment status | GET | `/api/v1/courses/{course_id}/enrollment-status` | → `CourseEnrollmentStatusResponse` |
| Admin list courses | GET | `/api/v1/admin/courses` | → `AdminCourseListResponse` |
| Admin tạo course | POST | `/api/v1/admin/courses` | `AdminCourseCreateRequest` → `AdminCourseCreateResponse` |
| Admin cập nhật course | PUT | `/api/v1/admin/courses/{id}` | `AdminCourseUpdateRequest` → `AdminCourseUpdateResponse` |
| Admin xóa course | DELETE | `/api/v1/admin/courses/{id}` | — → `AdminDeleteCourseResponse` |

---

## 3. Entity: `Module` (modules collection)

### 3.1 Vị trí trong execution flow
**Stage 2** — cùng với Course, seed trong `seed_courses_modules_lessons()` (dòng 881–896).

### 3.2 Số lượng seed
- Public courses: 70 × 6 = **420 modules**
- Personal courses: 80 × 4 = **320 modules**
- **Tổng**: 740 Modules

### 3.3 Schema seed thực tế

| Field seed | Giá trị seed | Model field | Khớp? |
|---|---|---|---|
| `id` | `gid()` | `id: str` | ✅ |
| `course_id` | `cid` (ID course cha) | `course_id: str` | ✅ |
| `title` | `mod_tpl.get("title")` hoặc `f"Module {m+1}"` | `title: str` | ✅ |
| `description` | `mod_tpl.get("description")` hoặc `fake.text(180)` | `description: str` | ✅ |
| `order` | `m + 1` (1-indexed) | `order: int` | ✅ |
| `difficulty` | `random.choice(["Basic", "Intermediate", "Advanced"])` | `difficulty: str` | ✅ |
| `estimated_hours` | `round(module_duration / 60.0, 1)` | `estimated_hours: float` | ✅ |
| `learning_outcomes` | `module_outcomes_from_curriculum(mod_tpl)` | `learning_outcomes: List[dict]` | ✅ |
| `resources` | `[mk_resource("Module Notes", "pdf"), mk_resource("Links", "link")]` | `resources: List[dict]` | ✅ |
| `prerequisites` | `[module_embeds[m-1].id]` nếu m>0, else `[]` | `prerequisites: List[str]` | ✅ |
| `total_lessons` | `cfg.public_lessons_per_module` = 6 hoặc 5 | `total_lessons: int` | ✅ |
| `total_duration_minutes` | tổng mins của lessons trong module | `total_duration_minutes: int` | ✅ |
| `created_at` | `past(20, 120)` | `created_at: datetime` | ✅ |
| `updated_at` | `past(1, 10)` | `updated_at: datetime` | ✅ |

### 3.4 learning_outcomes structure (module_outcomes_from_curriculum, dòng 539–549)
```python
{
    "id": gid(),          # UUID
    "outcome": item["description"],   # key là "outcome" (không phải "description")
    "skill_tag": item.get("skill_tag") or "module-outcome",
    "is_mandatory": True
}
```
Khớp với `LearningOutcome` schema trong `learning.py`: `{id: str, outcome: str, skill_tag: str, is_mandatory: bool}` ✅

**⚠️ Chú ý sự khác biệt**: Course-level `LearningOutcome` (course.py) dùng key `"description"`, còn Module-level (learning.py) dùng key `"outcome"`. Hai schema khác nhau cho cùng khái niệm.

### 3.5 prerequisites chain
Module thứ m (m>0) có `prerequisites = [module_embeds[m-1].id]`, tức là chuỗi tuần tự M1 → M2 → M3 ... → M6. Đây là linear dependency chain.

### 3.6 APIs phục vụ
| API | Method | Path | Schema |
|---|---|---|---|
| Danh sách modules trong course | GET | `/api/v1/courses/{course_id}/modules` | → `CourseModulesResponse` |
| Chi tiết module | GET | `/api/v1/courses/{course_id}/modules/{module_id}` | → `ModuleDetailResponse` |
| Learning outcomes của module | GET | `/api/v1/courses/{course_id}/modules/{module_id}/outcomes` | → `ModuleOutcomesResponse` |
| Resources của module | GET | `/api/v1/courses/{course_id}/modules/{module_id}/resources` | → `ModuleResourcesResponse` |
| Sinh quiz module | POST | `/api/v1/courses/{course_id}/modules/{module_id}/assessments/generate` | `ModuleAssessmentGenerateRequest` → `ModuleAssessmentGenerateResponse` |

---

## 4. Entity: `Lesson` (lessons collection)

### 4.1 Vị trí trong execution flow
**Stage 2** — cùng với Course/Module (dòng 833–856 public, 969–987 personal).

### 4.2 Số lượng seed
- Public: 70 × 6 × 6 = **2520 lessons**
- Personal: 80 × 4 × 5 = **1600 lessons**
- **Tổng**: 4120 Lessons

### 4.3 Schema seed thực tế

| Field seed | Giá trị seed | Model field | Khớp? |
|---|---|---|---|
| `id` | `gid()` | `id: str` | ✅ |
| `module_id` | `mid` | `module_id: str` | ✅ |
| `course_id` | `cid` | `course_id: str` | ✅ |
| `title` | `lesson_tpl["title"]` | `title: str` | ✅ |
| `description` | `lesson_tpl.get("description")` hoặc `lesson_tpl["title"]` | `description: Optional[str]` | ✅ |
| `order` | `l + 1` | `order: int` | ✅ |
| `content` | `lesson_tpl["content"]` | `content: str` | ✅ |
| `content_type` | `lesson_tpl.get("content_type") or "text"` | `content_type: str` | ✅ |
| `duration_minutes` | `random.randint(18, 65)` public / `(15, 45)` personal | `duration_minutes: int` | ✅ |
| `video_url` | `get_lesson_video_url(...)` nếu has_video else `None` | `video_url: Optional[str]` | ✅ |
| `audio_url` | `None` (public courses) / **không set** (personal) | `audio_url: Optional[str]` | ✅ (default None) |
| `learning_objectives` | `lesson_tpl.get("objectives")` hoặc `[fake.sentence(...)]` | `learning_objectives: List[str]` | ✅ |
| `resources` | `[mk_resource("Slide pack","slide"), mk_resource("Practice code","code"), mk_resource("Reference","link")]` public / `[mk_resource("Personal notes","pdf")]` personal | `resources: List[dict]` | ✅ |
| `quiz_id` | `None` lúc seed (cập nhật ở Stage 5) | `quiz_id: Optional[str]` | ✅ |
| `is_published` | `True` | `is_published: bool` | ✅ |
| `created_at` | `past(30, 180)` | `created_at: datetime` | ✅ |
| `updated_at` | `past(1, 20)` | `updated_at: datetime` | ✅ |

### 4.4 resources structure (mk_resource, dòng 496–520)
```python
{
    "id": gid(),
    "title": title,         # "Slide pack", "Practice code", "Reference", "Personal notes"
    "type": rtype,          # "slide", "code", "link", "pdf"
    "url": src["url"],      # URL thật từ REAL_RESOURCE_POOL
    "size_mb": size_mb,
    "description": src["description"]
}
```
Khớp hoàn toàn với `ResourceItem` schema (learning.py): `{id, title, type, url, size_mb, description}` ✅

**Cập nhật quiz_id** (Stage 5, dòng 1289–1294): Sau khi quiz được seed, `lesson.quiz_id` được cập nhật = quiz ID tương ứng, và lưu lại bằng `await ls.save()`.

### 4.5 APIs phục vụ
| API | Method | Path | Schema |
|---|---|---|---|
| Xem nội dung lesson | GET | `/api/v1/courses/{course_id}/lessons/{lesson_id}` | → `LessonContentResponse` |
| Đánh dấu hoàn thành lesson | POST | `/api/v1/courses/{course_id}/lessons/{lesson_id}/complete` | → `LessonCompleteResponse` |

---

## 5. Entity: `Class` (classes collection)

### 5.1 Vị trí trong execution flow
**Stage 3** — `seed_classes()` (dòng 1085–1125). Chỉ dùng **public courses**.

### 5.2 Số lượng seed
- **90 Classes** (tất cả liên kết với public courses)

### 5.3 Schema seed thực tế

| Field seed | Giá trị seed | Model field | Khớp? |
|---|---|---|---|
| `id` | `gid()` | `id: str` | ✅ |
| `name` | `"{prefix} {short_title}"` hoặc `"#{n}"` nếu trùng | `name: str` | ✅ |
| `description` | `mk_class_description(course_title)` | `description: str` | ✅ |
| `course_id` | `random.choice(public_courses)` | `course_id: str` | ✅ |
| `instructor_id` | `random.choice(instructor_ids)` | `instructor_id: str` | ✅ |
| `invite_code` | **không set trong seed** (dùng default_factory trong model) | `invite_code: str` | ✅ (auto-gen) |
| `max_students` | `random.randint(45, 120)` | `max_students: int` | ✅ |
| `start_date` | `past(0, 35)` | `start_date: datetime` | ✅ |
| `end_date` | `start_date + timedelta(days=45–120)` | `end_date: datetime` | ✅ |
| `status` | `sample_weighted([(preparing,0.25), (active,0.6), (completed,0.15)])` | `status: str` | ✅ |
| `student_ids` | `[]` lúc tạo, cập nhật ở Stage 4b | `student_ids: List[str]` | ✅ |
| `created_at` | `past(3, 90)` | `created_at: datetime` | ✅ |
| `updated_at` | `past(1, 7)` | `updated_at: datetime` | ✅ |

**Sync Stage 4b** (`sync_classes_with_enrollments`, dòng 1626–1638): Query enrollments theo `course_id` và `status in [active, completed]`, sau đó chọn ngẫu nhiên tối đa `min(eligible, randint(20, min(c.max_students, 95)))` students để gán vào `student_ids`.

### 5.4 APIs phục vụ
| API | Method | Path | Schema |
|---|---|---|---|
| Tạo lớp (Instructor) | POST | `/api/v1/classes` | `ClassCreateRequest` → `ClassCreateResponse` |
| Danh sách lớp | GET | `/api/v1/classes` | → `ClassListResponse` |
| Chi tiết lớp | GET | `/api/v1/classes/{class_id}` | → `ClassDetailResponse` |
| Cập nhật lớp | PATCH | `/api/v1/classes/{class_id}` | `ClassUpdateRequest` → `ClassUpdateResponse` |
| Xóa lớp | DELETE | `/api/v1/classes/{class_id}` | → `ClassDeleteResponse` |
| Tham gia lớp (Student) | POST | `/api/v1/classes/join` | `ClassJoinRequest` → `ClassJoinResponse` |
| Danh sách học viên | GET | `/api/v1/classes/{class_id}/students` | → `ClassStudentListResponse` |
| Chi tiết học viên trong lớp | GET | `/api/v1/classes/{class_id}/students/{student_id}` | → `ClassStudentDetailResponse` |
| Tiến độ lớp học | GET | `/api/v1/classes/{class_id}/progress` | → `ClassProgressResponse` |
| Admin danh sách lớp | GET | `/api/v1/admin/classes` | → `AdminClassListResponse` |
| Admin chi tiết lớp | GET | `/api/v1/admin/classes/{class_id}` | → `AdminClassDetailResponse` |

---

## 6. Entity: `Enrollment` (enrollments collection)

### 6.1 Vị trí trong execution flow
**Stage 4** — `seed_enrollments_progress()` (dòng 1128–1240). Chỉ enroll **public courses**.

### 6.2 Số lượng seed
- 360 students × random(12–22) courses = **ước tính ~5760–7920 enrollments**
- Thực tế: `min(random.randint(12, 22), 70)` courses/student vì chỉ có 70 public courses

### 6.3 Schema seed thực tế

| Field seed | Giá trị seed | Model field | Khớp? |
|---|---|---|---|
| `id` | `gid()` | `id: str` | ✅ |
| `user_id` | `sid` (student ID) | `user_id: str` | ✅ |
| `course_id` | `cid` | `course_id: str` | ✅ |
| `status` | `sample_weighted([(active,0.68), (completed,0.22), (cancelled,0.10)])` | `status: str` | ✅ |
| `progress_percent` | 100.0 (completed) / `uniform(5,95)` (active) / `uniform(0,70)` (cancelled) | `progress_percent: float` | ✅ |
| `completion_rate` | = `progress_percent` | `completion_rate: float` | ✅ |
| `completed_lessons` | list of lesson IDs (ordered, first N lessons) | `completed_lessons: List[str]` | ✅ |
| `completed_modules` | modules có ALL lessons đã completed | `completed_modules: List[str]` | ✅ |
| `avg_quiz_score` | `round(uniform(45,98),1)` nếu completed_count > 0, else `None` | `avg_quiz_score: Optional[float]` | ✅ |
| `total_time_spent_minutes` | `randint(40, 2400)` nếu completed_count > 0, else 0 | `total_time_spent_minutes: int` | ✅ |
| `enrolled_at` | `past(5, 150)` | `enrolled_at: datetime` | ✅ |
| `last_accessed_at` | `past(0, 12)` nếu not cancelled, else `None` | `last_accessed_at: Optional[datetime]` | ✅ |
| `completed_at` | `enrolled_at + timedelta(20–110 days)` nếu completed, else `None` | `completed_at: Optional[datetime]` | ✅ |

**Cập nhật enrollment_count trên Course** (dòng 1233–1236): Sau khi seed xong enrollments, mỗi course được cập nhật `enrollment_count = len(enrollments của course đó)`.

### 6.4 APIs phục vụ
| API | Method | Path | Schema |
|---|---|---|---|
| Đăng ký khóa học | POST | `/api/v1/enrollments` | `EnrollmentCreateRequest` → `EnrollmentCreateResponse` |
| Danh sách khóa học đang học | GET | `/api/v1/enrollments/my-courses` | → `EnrollmentListResponse` |
| Chi tiết enrollment | GET | `/api/v1/enrollments/{enrollment_id}` | → `EnrollmentDetailResponse` |
| Huỷ enrollment | DELETE | `/api/v1/enrollments/{enrollment_id}` | → `EnrollmentCancelResponse` |

---

## 7. Entity: `Progress` (progress collection)

### 7.1 Vị trí trong execution flow
**Stage 4** — cùng với Enrollment, chỉ tạo khi status là `active` hoặc `completed`.

### 7.2 Số lượng seed
- Ước tính ~90% của total enrollments (những enrollment có status active/completed)

### 7.3 Schema seed thực tế

| Field seed | Giá trị seed | Model field | Khớp? |
|---|---|---|---|
| `id` | `gid()` | `id: str` | ✅ |
| `user_id` | `sid` | `user_id: str` | ✅ |
| `course_id` | `cid` | `course_id: str` | ✅ |
| `enrollment_id` | `eid` | `enrollment_id: str` | ✅ |
| `overall_progress_percent` | = `progress_percent` từ enrollment | `overall_progress_percent: float` | ✅ |
| `completed_lessons_count` | `completed_count` | `completed_lessons_count: int` | ✅ |
| `total_lessons_count` | `total_lessons_count` | `total_lessons_count: int` | ✅ |
| `lessons_progress` | `List[LessonProgressItem]` | `lessons_progress: List[LessonProgressItem]` | ✅ |
| `total_time_spent_minutes` | = `enrollment.total_time_spent_minutes` | `total_time_spent_minutes: int` | ✅ |
| `estimated_hours_remaining` | `max(0.0, round((total-completed) * 0.75, 1))` | `estimated_hours_remaining: float` | ✅ |
| `study_streak_days` | `randint(0, 42)` | `study_streak_days: int` | ✅ |
| `avg_quiz_score` | `enrollment.avg_quiz_score or 0.0` | `avg_quiz_score: float` | ✅ |
| `last_accessed_at` | = `enrollment.last_accessed_at` | `last_accessed_at: Optional[datetime]` | ✅ |
| `created_at` | = `enrolled_at` | `created_at: datetime` | ✅ |
| `updated_at` | `past(0, 7)` | `updated_at: datetime` | ✅ |

### 7.4 LessonProgressItem structure (dòng 1198–1208)
```python
LessonProgressItem(
    lesson_id = ls.id,
    module_id = ls.module_id,
    lesson_title = ls.title,
    status = "completed" | "in-progress" | "not-started",
    completion_date = past(1, 80) nếu done, else None,
    time_spent_minutes = randint(10, max(ls.duration_minutes, 15)) nếu done, else 0,
    video_progress_seconds = randint(60, ls.duration_minutes * 60) nếu done+has_video, else 0
)
```
Khớp hoàn toàn với `LessonProgressItem` model (models.py dòng 23–37) ✅

### 7.5 APIs phục vụ
| API | Method | Path | Schema |
|---|---|---|---|
| Tiến độ khóa học | GET | `/api/v1/progress/{course_id}` | → `ProgressCourseResponse` |

---

## 8. Entity: `Quiz` (quizzes collection)

### 8.1 Vị trí trong execution flow
**Stage 5** — `seed_quizzes_attempts()` (dòng 1243–1359). Tạo quiz cho lessons (xác suất 72% nếu có course_id, 50% nếu không).

### 8.2 Số lượng seed
- 4120 lessons × ~72% = ước tính **~2967 quizzes**
- Thực tế phụ thuộc vào random seed deterministic

### 8.3 Schema seed thực tế

| Field seed | Giá trị seed | Model field | Khớp? |
|---|---|---|---|
| `id` | `gid()` | `id: str` | ✅ |
| `lesson_id` | `ls.id` | `lesson_id: str` | ✅ |
| `course_id` | `ls.course_id` | `course_id: str` | ✅ |
| `module_id` | `ls.module_id` | `module_id: Optional[str]` | ✅ |
| `title` | `f"Quiz - {ls.title}"` | `title: str` | ✅ |
| `description` | `mk_quiz_description(ls.title, ls.description)` | `description: str` | ✅ |
| `quiz_type` | `random.choice(["review", "practice", "final_check"])` | `quiz_type: Optional[str]` | ✅ |
| `time_limit_minutes` | `random.choice([10, 15, 20, 25, None])` | `time_limit_minutes: Optional[int]` | ✅ |
| `passing_score` | `random.choice([60.0, 70.0, 75.0])` | `passing_score: float` | ✅ |
| `max_attempts` | `random.choice([2, 3, 4])` | `max_attempts: int` | ✅ |
| `deadline` | `future(20, 90)` | `deadline: Optional[datetime]` | ✅ |
| `is_draft` | `random.choice([False, False, False, True])` (~25% draft) | `is_draft: bool` | ✅ |
| `questions` | `List[dict]` từ `mk_quiz_question()` | `questions: List[dict]` | ✅ |
| `question_count` | `randint(5, 10)` | `question_count: int` | ✅ |
| `total_points` | `sum(q["points"] for q in qs)` | `total_points: int` | ✅ |
| `mandatory_question_count` | `sum(1 for q in qs if q["is_mandatory"])` | `mandatory_question_count: int` | ✅ |
| `created_by` | `random.choice(instructor_ids + admin_ids)` | `created_by: str` | ✅ |
| `created_at` | `past(5, 120)` | `created_at: datetime` | ✅ |
| `updated_at` | `past(1, 10)` | `updated_at: datetime` | ✅ |

### 8.4 Question structure (mk_quiz_question, dòng 552–583)
```python
{
    "id": gid(),
    "type": "multiple_choice" | "fill_in_blank" | "true_false",  # weights: 0.7/0.2/0.1
    "question_text": str,
    "options": List[str] | None,  # null nếu fill_in_blank
    "correct_answer": str,        # index string cho MCQ, "True"/"False" cho TF, text cho FIB
    "explanation": str,
    "points": randint(1, 3),
    "is_mandatory": random.choice([True, False]),
    "order": int
}
```
Khớp với `QuestionCreate` schema (quiz.py): `{type, question_text, options, correct_answer, explanation, points, is_mandatory, order}` ✅

**⚠️ Lưu ý**: Seed dùng `random.choice([False, False, True])` cho `is_mandatory` (dòng 581) → tỷ lệ mandatory ~33%.

### 8.5 APIs phục vụ
| API | Method | Path | Schema |
|---|---|---|---|
| Chi tiết quiz (student) | GET | `/api/v1/quizzes/{quiz_id}` | → `QuizDetailResponse` |
| Nộp bài quiz | POST | `/api/v1/quizzes/{quiz_id}/attempt` | `QuizAttemptRequest` → `QuizAttemptResponse` |
| Kết quả quiz | GET | `/api/v1/quizzes/{quiz_id}/results/{attempt_id}` | → `QuizResultsResponse` |
| Làm lại quiz | POST | `/api/v1/quizzes/{quiz_id}/retake` | — → `QuizRetakeResponse` |
| Tạo quiz (Instructor) | POST | `/api/v1/courses/{course_id}/lessons/{lesson_id}/quizzes` | `QuizCreateRequest` → `QuizCreateResponse` |
| Cập nhật quiz | PUT | `/api/v1/quizzes/{quiz_id}` | `QuizUpdateRequest` → `QuizUpdateResponse` |
| Xóa quiz | DELETE | `/api/v1/quizzes/{quiz_id}` | — → `QuizDeleteResponse` |
| Danh sách quiz (Instructor) | GET | `/api/v1/quizzes` | — → `QuizListResponse` |
| Kết quả quiz theo lớp | GET | `/api/v1/quizzes/{quiz_id}/class-results` | — → `QuizClassResultsResponse` |
| Sinh bài luyện tập | POST | `/api/v1/quizzes/practice/generate` | `PracticeExercisesGenerateRequest` → `PracticeExercisesGenerateResponse` |

---

## 9. Entity: `QuizAttempt` (quiz_attempts collection)

### 9.1 Vị trí trong execution flow
**Stage 5** — cùng với Quiz (dòng 1296–1352).

### 9.2 Số lượng seed
- Mỗi quiz: lấy eligible users (enrolled + active/completed) → sample(8–24 users) → mỗi user 1–3 lần attempts
- Ước tính: ~2967 quizzes × ~16 users × ~1.5 attempts/user = **~71,000 attempts**

### 9.3 Schema seed thực tế

| Field seed | Giá trị seed | Model field | Khớp? |
|---|---|---|---|
| `id` | `gid()` | `id: str` | ✅ |
| `quiz_id` | `q.id` | `quiz_id: str` | ✅ |
| `user_id` | `uid` (eligible student) | `user_id: str` | ✅ |
| `answers` | `List[dict]` xem bên dưới | `answers: List[dict]` | ✅ |
| `score` | `round(uniform(35, 100), 1)` | `score: float` | ✅ |
| `status` | `"Pass"` nếu score >= passing_score else `"Fail"` | `status: str` | ✅ |
| `passed` | bool | `passed: bool` | ✅ |
| `attempt_number` | `n + 1` (1, 2, hoặc 3) | `attempt_number: int` | ✅ |
| `correct_answers` | đếm từ `answers` | `correct_answers: int` | ✅ |
| `total_questions` | `q.question_count` | `total_questions: int` | ✅ |
| `mandatory_correct` | đếm mandatory đúng | `mandatory_correct: int` | ✅ |
| `mandatory_total` | `q.mandatory_question_count` | `mandatory_total: int` | ✅ |
| `mandatory_passed` | `mandatory_correct >= max(1, int(mandatory_total * 0.6))` | `mandatory_passed: bool` | ✅ |
| `can_retake` | `(n+1) < q.max_attempts` | `can_retake: bool` | ✅ |
| `started_at` | `past(1, 90)` | `started_at: datetime` | ✅ |
| `submitted_at` | `started_at + timedelta(4–45 min)` | `submitted_at: Optional[datetime]` | ✅ |
| `time_spent_seconds` | `int((submitted - started).total_seconds())` | `time_spent_seconds: int` | ✅ |

### 9.4 Answer structure (dòng 1321–1331)
```python
{
    "question_id": qq["id"],
    "question_content": qq["question_text"],
    "student_answer": qq["correct_answer"] if is_correct else fake.word(),
    "correct_answer": qq["correct_answer"],
    "is_correct": bool,
    "is_mandatory": qq.get("is_mandatory", False),
    "score": qq["points"] if is_correct else 0,
    "explanation": qq.get("explanation", ""),
    "related_lesson_link": f"/dashboard/courses/{q.course_id}/lessons/{q.lesson_id}"
}
```
Khớp với `QuestionResult` schema (quiz.py) ✅

### 9.5 APIs phục vụ
Phục vụ cùng APIs với Quiz ở trên (GET results, GET history, class results).

---

## 10. Entity: `AssessmentSession` (assessment_sessions collection)

### 10.1 Vị trí trong execution flow
**Stage 6** — `seed_assessments_recommendations()` (dòng 1362–1548).

### 10.2 Số lượng seed
- 360 students × random(2–4) sessions/student = **ước tính 720–1440 sessions**

### 10.3 Schema seed thực tế

| Field seed | Giá trị seed | Model field | Khớp? |
|---|---|---|---|
| `id` | `gid()` | `id: str` | ✅ |
| `user_id` | `sid` | `user_id: str` | ✅ |
| `category` | `random.choice(["Programming","Data Science","Business","Languages","Math"])` | `category: str` | ✅ |
| `subject` | `random.choice(ASSESSMENT_SKILLS_BY_CATEGORY[category])` | `subject: str` | ✅ |
| `level` | `random.choice(["Beginner","Intermediate","Advanced"])` | `level: str` | ✅ |
| `focus_areas` | `[fake.word() for _ in range(1–3)]` | `focus_areas: List[str]` | ✅ |
| `total_questions` | Beginner=15, Intermediate=25, Advanced=35 | `total_questions: int` | ✅ |
| `time_limit_minutes` | Beginner=15, Intermediate=22, Advanced=30 | `time_limit_minutes: int` | ✅ |
| `questions` | `List[dict]` từ `mk_assessment_question()` | `questions: List[dict]` | ✅ |
| `status` | `sample_weighted([(pending,0.15),(in_progress,0.2),(submitted,0.15),(evaluated,0.5)])` | `status: str` | ✅ |
| `answers` | List nếu submitted/evaluated | `answers: List[dict]` | ✅ |
| `overall_score` | `round((correct/total)*100, 1)` nếu evaluated | `overall_score: Optional[float]` | ✅ |
| `proficiency_level` | `"Advanced"` nếu >=80, `"Intermediate"` nếu >=60, `"Beginner"` else | `proficiency_level: Optional[str]` | ✅ |
| `correct_answers` | count (evaluated only) | `correct_answers: Optional[int]` | ✅ |
| `skill_analysis` | `mk_assessment_skill_analysis_payload(...)` — dict gồm `{skill_analysis, score_breakdown, overall_feedback}` | `skill_analysis: Optional[dict]` | ✅ |
| `knowledge_gaps` | `List[dict]` — `{gap_area, description, importance, suggested_action}` | `knowledge_gaps: List[dict]` | ✅ |
| `ai_feedback` | chuỗi text | `ai_feedback: Optional[str]` | ✅ |
| `time_analysis` | `{total_time_seconds, average_time_per_question, fastest_question_time, slowest_question_time}` | `time_analysis: Optional[dict]` | ✅ |
| `created_at` | `past(1, 100)` | `created_at: datetime` | ✅ |
| `expires_at` | `created_at + timedelta(minutes=60)` | `expires_at: datetime` | ✅ |
| `submitted_at` | `created + timedelta(8 to time_limit min)` nếu submitted/evaluated | `submitted_at: Optional[datetime]` | ✅ |
| `evaluated_at` | `submitted_at + timedelta(8–180 sec)` nếu evaluated | `evaluated_at: Optional[datetime]` | ✅ |

**⚠️ Không seed**: `custom_goals`, `total_elapsed_seconds`, `per_question_results` — các trường này có trong model nhưng không được set trong seed (đều là Optional hoặc default=[]).

### 10.4 Question structure (mk_assessment_question, dòng 586–601)
```python
{
    "question_id": gid(),
    "question_text": str (từ ASSESSMENT_QUESTIONS_BY_DIFFICULTY),
    "question_type": "multiple_choice" | "fill_in_blank" | "drag_and_drop",
    "difficulty": "easy" | "medium" | "hard",
    "skill_tag": str (từ ASSESSMENT_SKILLS_BY_CATEGORY),
    "points": 1 | 2 | 3,
    "options": ["Đáp án A","B","C","D"] hoặc None,
    "correct_answer_hint": str
}
```
Khớp với `AssessmentQuestion` schema (assessment.py) ✅

### 10.5 Phân phối độ khó
- `i < total*0.2` → easy (20%)
- `i < total*0.8` → medium (60%)
- còn lại → hard (20%)

### 10.6 APIs phục vụ
| API | Method | Path | Schema |
|---|---|---|---|
| Sinh assessment | POST | `/api/v1/assessments/generate` | `AssessmentGenerateRequest` → `AssessmentGenerateResponse` |
| Nộp bài | POST | `/api/v1/assessments/{session_id}/submit` | `AssessmentSubmitRequest` → `AssessmentSubmitResponse` |
| Kết quả | GET | `/api/v1/assessments/{session_id}/results` | → `AssessmentResultsResponse` |
| Lịch sử | GET | `/api/v1/assessments/history` | → `AssessmentHistoryResponse` |
| Xem lại bài làm | GET | `/api/v1/assessments/{session_id}/review` | → `AssessmentReviewResponse` |

---

## 11. Entity: `Recommendation` (recommendations collection)

### 11.1 Vị trí trong execution flow
**Stage 6** — cùng với AssessmentSession (dòng 1477–1543). Được tạo SAU AssessmentSession để lấy proficiency_level.

### 11.2 Số lượng seed
- **360 recommendations** — 1 recommendation/student

### 11.3 Schema seed thực tế

| Field seed | Giá trị seed | Model field | Khớp? |
|---|---|---|---|
| `id` | `gid()` | `id: str` | ✅ |
| `user_id` | `sid` | `user_id: str` | ✅ |
| `source` | `"assessment"` nếu có evaluated session, else `random.choice(["learning_history","ai_suggestion"])` | `source: str` | ✅ |
| `assessment_session_id` | ID session evaluated mới nhất, hoặc `None` | `assessment_session_id: Optional[str]` | ✅ |
| `user_proficiency_level` | Lấy từ assessment nếu có, else `sample_weighted([(Beginner,0.32),(Intermediate,0.41),(Advanced,0.27)])` | `user_proficiency_level: Optional[str]` | ✅ |
| `recommended_courses` | 4–7 courses, mỗi item xem bên dưới | `recommended_courses: List[dict]` | ✅ |
| `suggested_learning_order` | `List[{step, course_id, focus_modules, why_this_order}]` | `suggested_learning_order: List[dict]` | ✅ |
| `practice_exercises` | 3–6 items, xem bên dưới | `practice_exercises: List[dict]` | ✅ |
| `ai_personalized_advice` | `fake.paragraph(nb_sentences=3)` | `ai_personalized_advice: str` | ✅ |
| `total_estimated_hours` | tổng `c.total_duration_minutes / 60.0` | `total_estimated_hours: float` | ✅ |
| `created_at` | `past(0, 35)` | `created_at: datetime` | ✅ |
| `expires_at` | `future(15, 120)` | `expires_at: Optional[datetime]` | ✅ |

### 11.4 recommended_courses item structure (dòng 1490–1502)
```python
{
    "course_id": c.id,
    "title": c.title,
    "description": c.description,
    "category": c.category,
    "level": c.level,
    "thumbnail_url": c.thumbnail_url,
    "priority_rank": int (1 = highest),
    "relevance_score": round(uniform(60, 98), 1),
    "reason": fake.sentence(nb_words=16),
    "addresses_gaps": [fake.word() for _ in range(1–3)],
    "estimated_completion_days": randint(7, 60)
}
```
Khớp với `RecommendedCourseItem` schema (recommendation.py) ✅

### 11.5 practice_exercises item structure (dòng 1530–1536)
```python
{
    "skill_tag": fake.slug().replace("-", "_"),
    "exercise_type": random.choice(["coding","quiz","project","reading"]),
    "description": fake.sentence(nb_words=12),
    "difficulty": random.choice(["easy","medium","hard"]),
    "estimated_time_hours": round(uniform(0.5, 6.0), 1)
}
```
Khớp với `PracticeExerciseItem` schema (recommendation.py) ✅

### 11.6 APIs phục vụ
| API | Method | Path | Schema |
|---|---|---|---|
| Recommendation sau assessment | GET | `/api/v1/assessments/{session_id}/recommendations` | → `AssessmentRecommendationResponse` |
| Recommendation tổng quát | GET | `/api/v1/recommendations` | → `RecommendationResponse` |

---

## 12. Entity: `Conversation` (conversations collection)

### 12.1 Vị trí trong execution flow
**Stage 7** — `seed_conversations_tokens()` (dòng 1551–1623).

### 12.2 Số lượng seed
- 360 students × random(1–4) conversations = **ước tính 720–1440 conversations**

### 12.3 Schema seed thực tế

| Field seed | Giá trị seed | Model field | Khớp? |
|---|---|---|---|
| `id` | `gid()` | `id: str` | ✅ |
| `user_id` | `sid` | `user_id: str` | ✅ |
| `course_id` | `random.choice(public_courses)` | `course_id: str` | ✅ |
| `title` | `f"Discussion {fake.word().title()}"` | `title: str` | ✅ |
| `summary` | `fake.sentence(nb_words=18)` | `summary: str` | ✅ |
| `course_title` | `f"Course {cid[:8]}"` | `course_title: str` | ⚠️ Không phải title thật của course |
| `messages` | `List[dict]` 4–16 messages | `messages: List[dict]` | ✅ |
| `total_messages` | `len(messages)` | `total_messages: int` | ✅ |
| `last_message_at` | `messages[-1]["created_at"]` | `last_message_at: datetime` | ✅ |
| `created_at` | `past(1, 60)` | `created_at: datetime` | ✅ |
| `updated_at` | `past(0, 15)` | `updated_at: datetime` | ✅ |

### 12.4 Message structure (dòng 1566–1571)
```python
{
    "id": gid(),
    "role": "user" | "assistant",     # alternating: even index = user
    "content": fake.sentence(18) | fake.paragraph(2),
    "created_at": past(0, 40)
}
```

**⚠️ Mismatch**: Schema `Message` (chat.py dòng 101–109) dùng field `message_id` và `timestamp`, nhưng seed dùng `id` và `created_at`. Đây là **mismatch** giữa embedded message format trong seed và schema phục vụ API. Service (`chat_service.py`) cần handle mapping này.

### 12.5 APIs phục vụ
| API | Method | Path | Schema |
|---|---|---|---|
| Gửi chat message | POST | `/api/v1/courses/{course_id}/chat` | `ChatMessageRequest` → `ChatMessageResponse` |
| Lịch sử chat | GET | `/api/v1/courses/{course_id}/chat/history` | → `ChatHistoryListResponse` |
| Chi tiết conversation | GET | `/api/v1/courses/{course_id}/chat/{conversation_id}` | → `ConversationDetailResponse` |
| Xóa conversation | DELETE | `/api/v1/courses/{course_id}/chat/{conversation_id}` | → `ChatDeleteResponse` |
| Xóa tất cả | DELETE | `/api/v1/courses/{course_id}/chat` | → `ChatDeleteAllResponse` |

---

## 13. Entity: `RefreshToken` (refresh_tokens collection)

### 13.1 Vị trí trong execution flow
**Stage 7** — cùng với Conversations (dòng 1587–1597).

### 13.2 Số lượng seed
- Tất cả users có `status = "active"` → mỗi user 1 refresh token
- Số lượng phụ thuộc vào tỷ lệ active users (~82–90% tổng 410 users)

### 13.3 Schema seed thực tế

| Field seed | Giá trị seed | Model field | Khớp? |
|---|---|---|---|
| `id` | `gid()` | `id: str` | ✅ |
| `user_id` | `u.id` | `user_id: str` | ✅ |
| `token` | `secrets.token_urlsafe(64)` | `token: str` | ✅ |
| `expires_at` | `created + timedelta(days=7)` | `expires_at: datetime` | ✅ |
| `created_at` | `past(0, 10)` | `created_at: datetime` | ✅ |

### 13.4 APIs phục vụ
Được dùng bởi `/api/v1/auth/refresh` và `/api/v1/auth/logout` (validate/invalidate token).

---

## 14. Entity: `PasswordResetTokenDocument` (password_reset_tokens collection)

### 14.1 Vị trí trong execution flow
**Stage 7** — cuối cùng trong `seed_conversations_tokens()` (dòng 1600–1612).

### 14.2 Số lượng seed
- Sample 14 users từ active_users → **14 PasswordResetTokenDocuments**

### 14.3 Schema seed thực tế

| Field seed | Giá trị seed | Model field | Khớp? |
|---|---|---|---|
| `id` | `gid()` | `id: str` | ✅ |
| `user_id` | `u.id` | `user_id: str` | ✅ |
| `token` | `secrets.token_urlsafe(32)` | `token: str` | ✅ |
| `expires_at` | `created + timedelta(hours=24)` | `expires_at: datetime` | ✅ |
| `used` | `random.choice([False, False, True])` (~33% used) | `used: bool` | ✅ |
| `created_at` | `past(0, 20)` | `created_at: datetime` | ✅ |

### 14.4 APIs phục vụ
Được dùng bởi `/api/v1/auth/forgot-password` và `/api/v1/auth/reset-password`.

---

## 15. Tổng Hợp Relationship Giữa Các Entity

```
User (410)
 ├─ created_by → User.id (admin/instructor tạo user)
 ├─ owns → Course (owner_id)
 ├─ instructors → Course (instructor_id) [chỉ public]
 ├─ teaches → Class (instructor_id)
 ├─ enrolled → Enrollment (user_id)
 ├─ has progress → Progress (user_id)
 ├─ attempts quiz → QuizAttempt (user_id)
 ├─ does assessment → AssessmentSession (user_id)
 ├─ gets recommendation → Recommendation (user_id)
 ├─ chats → Conversation (user_id)
 ├─ has refresh token → RefreshToken (user_id)
 └─ requested reset → PasswordResetTokenDocument (user_id)

Course (150)
 ├─ has modules → Module (course_id) [embedded + separate collection]
 │   └─ has lessons → Lesson (module_id, course_id) [embedded + separate]
 ├─ has classes → Class (course_id) [chỉ public]
 ├─ has enrollments → Enrollment (course_id)
 ├─ has progress → Progress (course_id)
 ├─ has quizzes → Quiz (course_id)
 └─ has conversations → Conversation (course_id)

Module (740)
 ├─ belongs to → Course (course_id)
 ├─ has lessons → Lesson (module_id)
 └─ prerequisites → Module.id (chuỗi tuần tự)

Lesson (4120)
 ├─ belongs to → Module (module_id) + Course (course_id)
 └─ has quiz → Quiz (quiz_id) [sau Stage 5]

Enrollment (ước tính ~6000)
 ├─ user → User (user_id)
 ├─ course → Course (course_id)
 ├─ completed_lessons → [Lesson.id]
 ├─ completed_modules → [Module.id]
 └─ has progress → Progress (enrollment_id)

Progress
 ├─ user → User (user_id)
 ├─ course → Course (course_id)
 ├─ enrollment → Enrollment (enrollment_id)
 └─ lessons_progress → [LessonProgressItem] chứa lesson_id + module_id

Quiz
 ├─ lesson → Lesson (lesson_id)
 ├─ course → Course (course_id) [denormalized]
 ├─ module → Module (module_id) [denormalized]
 └─ has attempts → QuizAttempt (quiz_id)

QuizAttempt
 ├─ quiz → Quiz (quiz_id)
 └─ user → User (user_id)

AssessmentSession
 └─ user → User (user_id)

Recommendation
 ├─ user → User (user_id)
 ├─ from session → AssessmentSession (assessment_session_id) [Optional]
 └─ recommends → [Course.id] trong recommended_courses

Conversation
 ├─ user → User (user_id)
 └─ course → Course (course_id)

RefreshToken / PasswordResetTokenDocument
 └─ user → User (user_id)
```

---

## 16. Summary: Collections & Estimated Counts

| # | Collection | Entity Class | Stage | Count (ước tính) |
|---|---|---|---|---|
| 1 | `users` | `User` | 1 | 410 |
| 2 | `courses` | `Course` | 2 | 150 (70 public + 80 personal) |
| 3 | `modules` | `Module` | 2 | 740 |
| 4 | `lessons` | `Lesson` | 2 | 4,120 |
| 5 | `classes` | `Class` | 3 | 90 |
| 6 | `enrollments` | `Enrollment` | 4 | ~6,000–7,920 |
| 7 | `progress` | `Progress` | 4 | ~90% enrollments |
| 8 | `quizzes` | `Quiz` | 5 | ~2,967 |
| 9 | `quiz_attempts` | `QuizAttempt` | 5 | ~71,000+ |
| 10 | `assessment_sessions` | `AssessmentSession` | 6 | ~720–1,440 |
| 11 | `recommendations` | `Recommendation` | 6 | 360 |
| 12 | `conversations` | `Conversation` | 7 | ~720–1,440 |
| 13 | `refresh_tokens` | `RefreshToken` | 7 | ~340–370 |
| 14 | `password_reset_tokens` | `PasswordResetTokenDocument` | 7 | 14 |

**Tổng**: ~87,000+ documents trên 14 collections.

---

## 17. Phát Hiện Mismatch & Ghi Chú Quan Trọng

### ✅ Không có mismatch nghiêm trọng
Toàn bộ fields được seed khớp với model definitions và schema requirements.

### ⚠️ Các điểm cần lưu ý

1. **`instructor_name` denormalized (Course)**: Seed dùng `f"Instructor {instructor_id[:6]}"` thay vì tên thật của instructor. Trong môi trường thực tế, cần lookup User.full_name khi tạo course.

2. **`course_title` trong Conversation**: Seed dùng `f"Course {cid[:8]}"` thay vì title thật. Service thực tế sẽ lookup Course.title.

3. **`audio_url` trong EmbeddedLesson**: Public course EmbeddedLesson có `audio_url` field (dòng 871), nhưng personal course EmbeddedLesson không set field này. Cả hai đều hợp lệ do field là Optional, nhưng không nhất quán về cấu trúc.

4. **Message format trong Conversation**: Seed dùng `{"id", "role", "content", "created_at"}` nhưng schema `Message` (chat.py) dùng `{"message_id", "role", "content", "timestamp"}`. Đây là **internal vs API schema difference** — cần service layer mapping.

5. **`custom_goals` trong AssessmentSession**: Model có field này (Optional[str]) nhưng seed không set — sẽ là `None` mặc định.

6. **`total_elapsed_seconds` và `per_question_results`**: Hai fields mới trong AssessmentSession model nhưng không được seed — sẽ là `None` và `[]` mặc định.

7. **`EmailVerificationTokenDocument`**: Collection `email_verification_tokens` định nghĩa trong model (dòng 864–874) nhưng **không được seed** và **không có trong `drop_all_collections()`**. Đây là collection bị bỏ sót trong pipeline.

8. **Personal course không có `instructor_id`**: Trường `instructor_id` không được set trong personal course seed, mặc dù `instructor_name` vẫn được set. Model cho phép `Optional[str]` = None.

9. **Relation `Recommendation.recommended_courses`**: Seed chọn từ `Course.find({status: {$in: ["published","draft"]}})` — tức là cả draft courses cũng được recommend. Trong production, nên lọc chỉ `published`.

10. **`validate_integrity()` không check Conversation**: Hàm validate không kiểm tra `conversation.user_id` và `conversation.course_id` có hợp lệ không — đây là blind spot trong integrity check.

---

## 18. Data Pools Được Dùng

| Pool constant | Dòng | Mô tả | Số items |
|---|---|---|---|
| `REAL_AVATARS` | 67–78 | Unsplash avatar URLs | 10 |
| `REAL_THUMBNAILS` | 80–89 | Unsplash thumbnail URLs (1200×675) | 8 |
| `REAL_YOUTUBE_VIDEO_IDS` | 92–103 | YouTube video IDs thật | 10 |
| `REAL_RESOURCE_POOL` | 114–199 | Tài nguyên PDF/link/code thật | 12 |
| `QUIZ_MCQ_POOL` | 209–368 | Câu hỏi MCQ có nội dung IT thật | 18 |
| `QUIZ_TRUE_FALSE_POOL` | 370–376 | Câu hỏi True/False IT | 5 |
| `QUIZ_FILL_IN_BLANK_POOL` | 378–384 | Câu điền vào chỗ trống | 5 |
| `ASSESSMENT_SKILLS_BY_CATEGORY` | 386–392 | Skills theo category | 5 categories × 4 skills |
| `ASSESSMENT_QUESTIONS_BY_DIFFICULTY` | 394–413 | Câu hỏi theo độ khó | 3 levels × 4 questions |

---

*Báo cáo được tổng hợp từ dò trực tiếp từng dòng của `init_data.py` (1799 dòng), `models/models.py` (875 dòng), và toàn bộ 15 file trong `schemas/`.*
