# 📐 QUY TẮC CODE FE + LUỒNG UI CHI TIẾT

> Bổ sung cho `be_to_fe_mapping.md` — Quy tắc thực thi khi viết code frontend

// Dung tieng viet co dau chuan nhat, han che su dung icon nhe. luon comment logic quan trong. clean code, code ro rang, de hieu, khong can phai ngan gon nhung phai clean chuan.
---

## 📦 TECH STACK CHÍNH XÁC (theo `package.json`)

| Package | Version | Mục đích | Ghi chú |
|---|---|---|---|
| `react` | **18.2.0** | UI library | Dùng function components + hooks |
| `react-dom` | **18.2.0** | DOM rendering | — |
| `react-router-dom` | **6.26.1** | Routing | `Routes/Route`, `useNavigate`, `useParams` |
| `axios` | **1.4.0** | HTTP client | Instance cấu hình sẵn trong `api.js` |
| `zustand` | **4.5.4** | State management | Thay Redux, lightweight |
| `recharts` | **2.12.7** | Charts | `LineChart`, `BarChart`, `RadarChart`, `PieChart` |
| `framer-motion` | **10.12.5** | Animation | `motion.div`, `AnimatePresence` |
| `react-hook-form` | **7.62.0** | Form management | `useForm`, `register`, `handleSubmit` |
| `react-hot-toast` | **2.4.1** | Toast notifications | `toast.success()`, `toast.error()` |
| `react-dropzone` | **14.2.3** | File upload drag-drop | Avatar upload, tài liệu |
| `i18next` | **23.7.8** | i18n | Đa ngôn ngữ vi/en |
| `react-i18next` | **13.5.0** | React bindings | `useTranslation()` |
| `vite` | **7.1.6** | Build tool | Dev server port 3000 |

> [!CAUTION]
> **KHÔNG cài thêm package** ngoài danh sách trên trừ khi user yêu cầu rõ ràng.
> Đặc biệt: **KHÔNG cài icon library** (lucide, heroicons, react-icons...). Dùng emoji hoặc CSS tự tạo.
> **KHÔNG cài TailwindCSS** — dùng vanilla CSS thuần.

---

## 🏗️ CẤU TRÚC THƯ MỤC

```
src/
├── main.jsx                    # Entry point
├── App.jsx                     # Root component + providers
├── AppRouter.jsx               # Toan bo routing
├── components/
│   ├── ui/                     # Shared UI: Button, Card, Input, Modal
│   ├── layout/                 # DashboardLayout, ProtectedRoute
│   ├── charts/                 # Recharts wrappers
│   └── [feature]/              # Component theo feature
├── pages/
│   ├── admin/                  # AdminPage (sub-routes)
│   ├── assessment/             # AssessmentSetup, Quiz, Results
│   ├── auth/                   # Login, Register, ForgotPassword...
│   ├── chat/                   # ChatPage
│   ├── classes/                # ClassList, ClassCreate, ClassDetail
│   ├── courses/                # CoursesPage, CourseDetailPage
│   ├── dashboard/              # DashboardPage
│   ├── enrollment/             # MyCoursesPage, StudentEnrollment
│   ├── error/                  # NotFoundPage, UnauthorizedPage
│   ├── landing/                # LandingPage + CSS
│   ├── learning/               # ModuleList, ModuleDetail, Lesson
│   ├── personal-courses/       # PersonalCoursesPage
│   ├── profile/                # ProfilePage
│   ├── progress/               # ProgressPage
│   ├── quiz/                   # QuizPage, QuizDetail, Attempt, Results
│   ├── recommendations/        # RecommendationsPage
│   └── search/                 # SearchResultsPage
├── services/
│   ├── api.js                  # Axios instance (da co)
│   ├── authService.js          # (da co)
│   ├── courseService.js         # (da co)
│   ├── enrollmentService.js     # (da co)
│   ├── quizService.js           # (da co)
│   ├── userService.js           # 🆕
│   ├── assessmentService.js     # 🆕
│   ├── learningService.js       # 🆕
│   ├── chatService.js           # 🆕
│   ├── classService.js          # 🆕
│   ├── personalCourseService.js # 🆕
│   ├── dashboardService.js      # 🆕
│   ├── analyticsService.js      # 🆕
│   ├── searchService.js         # 🆕
│   ├── recommendationService.js # 🆕
│   ├── progressService.js       # 🆕
│   └── adminService.js          # 🆕
├── stores/
│   ├── authStore.js             # (da co)
│   ├── courseStore.js           # (da co)
│   ├── uiStore.js               # 🆕 sidebar, theme, loading
│   └── ...
├── styles/
│   └── index.css               # Tat ca CSS chung
├── utils/                      # Helper functions
└── contexts/                   # React contexts
```

### Path Aliases (vite.config.js):
```js
// Su dung khi import:
import Button from '@components/ui/Button'
import CoursesPage from '@pages/courses/CoursesPage'
import courseService from '@services/courseService'
import useAuthStore from '@stores/authStore'
```

---

## ✍️ QUY TẮC CODE

### 1. Mobile-First CSS

```css
/* ❌ SAI - Desktop first */
.card { width: 300px; }
@media (max-width: 768px) { .card { width: 100%; } }

/* ✅ ĐÚNG - Mobile first */
.card {
  width: 100%;                  /* Mobile mac dinh */
}

@media (min-width: 768px) {
  .card { width: 50%; }        /* Tablet */
}

@media (min-width: 1024px) {
  .card { width: 33.33%; }     /* Desktop */
}
```

**Breakpoints chuẩn:**
| Tên | min-width | Mục đích |
|---|---|---|
| Mobile | mặc định | ≤ 767px |
| Tablet | `768px` | 768px - 1023px |
| Desktop | `1024px` | 1024px - 1279px |
| Wide | `1280px` | ≥ 1280px |

### 2. Comment bằng tiếng Việt (KHÔNG dấu)

```jsx
// ❌ SAI
// Get user data from API
// Handle form submission

// ✅ ĐÚNG (khong dau, ngan gon)
// Lay du lieu nguoi dung tu API
// Xu ly gui form dang ky

/**
 * Component hien thi thong tin khoa hoc
 * @param {string} courseId - UUID khoa hoc
 * @returns {JSX.Element}
 */
```

### 3. Clean Code Rules

```jsx
// ✅ Dat ten ro rang (tieng Anh cho ten bien/ham)
const [isLoading, setIsLoading] = useState(false)
const [courseList, setCourseList] = useState([])
const handleSubmitQuiz = async () => { /* ... */ }

// ✅ Tach logic ra custom hooks
const useCourseDetail = (courseId) => {
  const [course, setCourse] = useState(null)
  const [loading, setLoading] = useState(true)
  // ...
  return { course, loading, error }
}

// ✅ Early return
const CourseCard = ({ course }) => {
  if (!course) return null
  // ...
}

// ✅ Destructuring props
const QuizResult = ({ score, passed, results }) => {
  // ...
}

// ❌ TRÁNH
// - Component > 200 dong → tach nho
// - Props > 5 cai → dung object
// - Nested ternary
// - Magic numbers (dung constants)
// - Console.log trong code (xoa truoc commit)
```

### 4. Hạn chế Icon

```jsx
// ❌ SAI - Dung icon library
import { FiSearch, FiUser, FiBook } from 'react-icons/fi'

// ✅ ĐÚNG - Dung text hoac emoji trong code
<span className="status-badge">Đang học</span>
<span className="content-type">📝</span>  // text content
<span className="content-type">🎥</span>  // video content

// ✅ ĐÚNG - CSS icon don gian
.nav-arrow::before { content: '→'; }
.back-arrow::before { content: '←'; }
.check-mark::before { content: '✓'; }
.lock-icon::before { content: '🔒'; }
```

### 5. Service Pattern (theo api.js đã có)

```js
// services/learningService.js
import api from './api'

/**
 * Service xu ly cac API lien quan den hoc tap
 */
const learningService = {
  // Lay danh sach modules trong khoa hoc
  getCourseModules: (courseId) =>
    api.get(`/courses/${courseId}/modules`),

  // Lay chi tiet module
  getModuleDetail: (courseId, moduleId) =>
    api.get(`/courses/${courseId}/modules/${moduleId}`),

  // Lay noi dung bai hoc
  getLessonContent: (courseId, lessonId) =>
    api.get(`/courses/${courseId}/lessons/${lessonId}`),
}

export default learningService
```

### 6. Store Pattern (Zustand theo authStore đã có)

```js
// stores/courseStore.js
import { create } from 'zustand'

const useCourseStore = create((set) => ({
  // State
  courses: [],
  currentCourse: null,
  isLoading: false,

  // Actions
  setCourses: (courses) => set({ courses }),
  setCurrentCourse: (course) => set({ currentCourse: course }),
  setLoading: (isLoading) => set({ isLoading }),

  // Reset
  reset: () => set({ courses: [], currentCourse: null, isLoading: false }),
}))

export default useCourseStore
```

### 7. Page Component Pattern

```jsx
import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import toast from 'react-hot-toast'
import learningService from '@services/learningService'
import './LessonPage.css'

/**
 * Trang hien thi noi dung bai hoc
 * Route: /dashboard/courses/:courseId/lessons/:lessonId
 */
const LessonPage = () => {
  const { courseId, lessonId } = useParams()
  const [lesson, setLesson] = useState(null)
  const [loading, setLoading] = useState(true)

  // Lay noi dung bai hoc khi mount
  useEffect(() => {
    const fetchLesson = async () => {
      try {
        setLoading(true)
        const { data } = await learningService.getLessonContent(courseId, lessonId)
        setLesson(data)
      } catch (err) {
        toast.error('Khong the tai bai hoc')
      } finally {
        setLoading(false)
      }
    }
    fetchLesson()
  }, [courseId, lessonId])

  if (loading) return <div className="loading-spinner" />
  if (!lesson) return <div className="empty-state">Khong tim thay bai hoc</div>

  return (
    <div className="lesson-page">
      {/* Noi dung bai hoc */}
    </div>
  )
}

export default LessonPage
```

---

## 🔄 LUỒNG UI CHI TIẾT

### Flow 1: Đăng nhập → Dashboard

```
LandingPage (/)
  └─ Click "Đăng nhập"
      └─ LoginPage (/auth/login)
          ├─ Form: email + password + remember_me checkbox
          ├─ Submit → POST /auth/login
          ├─ Thanh cong:
          │   ├─ Luu access_token + refresh_token vao localStorage
          │   ├─ Luu user info vao authStore
          │   └─ Redirect theo role:
          │       ├─ student → /dashboard (StudentDashboard)
          │       ├─ instructor → /dashboard (InstructorDashboard)
          │       └─ admin → /dashboard (AdminDashboard)
          └─ That bai: toast.error(message)
```

### Flow 2: Đánh giá năng lực AI

```
DashboardPage → Click "Đánh giá năng lực"
  └─ AssessmentSetupPage (/dashboard/assessment)
      ├─ Buoc 1: Dropdown chon category (Programming, Math...)
      ├─ Buoc 2: Dropdown chon subject (Python, JS...) 
      ├─ Buoc 3: Radio chon level (Beginner/Intermediate/Advanced)
      │   └─ Hien thi: "15 câu - 15 phút" / "25 câu - 22 phút" / "35 câu - 30 phút"
      ├─ Tuy chon: Multi-select focus_areas
      ├─ Submit → POST /assessments/generate
      └─ Thanh cong → redirect:
          └─ AssessmentQuizPage (/dashboard/assessment/:sessionId)
              ├─ CountdownTimer component (o goc tren)
              ├─ Progress bar: "Câu 3/15"
              ├─ QuestionCard (render theo question_type):
              │   ├─ multiple_choice → 4 radio buttons (A/B/C/D)
              │   ├─ fill_in_blank → text input
              │   └─ drag_and_drop → draggable items
              ├─ Navigation: "← Câu trước" / "Câu sau →"
              ├─ Nut "Nộp bài" (xac nhan modal)
              ├─ Submit → POST /assessments/{sessionId}/submit
              └─ Thanh cong → redirect:
                  └─ AssessmentResultsPage (/dashboard/assessment/:sessionId/results)
                      ├─ Section 1: Diem tong (CircularProgress 0-100) + Level badge
                      ├─ Section 2: Phan tich ky nang (RadarChart tu recharts)
                      ├─ Section 3: Lo hong kien thuc (cards voi mau theo importance)
                      ├─ Section 4: Phan tich thoi gian (stat cards)
                      ├─ Section 5: Loi khuyen AI (markdown rendered)
                      └─ CTA: "Xem lộ trình học tập" → GET /recommendations/from-assessment
```

### Flow 3: Khám phá → Đăng ký → Học khóa học

```
CoursesPage (/dashboard/courses)
  ├─ SearchBar (goi GET /courses/search khi typing, debounce 300ms)
  ├─ Filter: category dropdown + level dropdown
  ├─ Grid cards: CourseCard component
  │   └─ Click card →
  │       └─ CourseDetailPage (/dashboard/courses/:courseId)
  │           ├─ GET /courses/:courseId → hien thi chi tiet
  │           ├─ GET /courses/:courseId/enrollment-status → check trang thai
  │           ├─ Neu chua dang ky: nut "Đăng ký học"
  │           │   └─ Click → POST /enrollments {course_id}
  │           │       └─ toast.success → reload page (nut doi thanh "Bắt đầu học")
  │           ├─ Neu da dang ky: nut "Tiếp tục học"
  │           │   └─ Click → redirect:
  │           │       └─ ModuleListPage (/dashboard/courses/:courseId/modules)
  │           │           ├─ GET /courses/:courseId/modules
  │           │           ├─ List ModuleCard: title, progress_percent, status dot, lock icon
  │           │           └─ Click module ko bi khoa →
  │           │               └─ ModuleDetailPage (/dashboard/courses/:courseId/modules/:moduleId)
  │           │                   ├─ GET /courses/:courseId/modules/:moduleId
  │           │                   ├─ Lesson list: click lesson →
  │           │                   │   └─ LessonPage (/dashboard/courses/:courseId/lessons/:lessonId)
  │           │                   │       ├─ GET /courses/:courseId/lessons/:lessonId
  │           │                   │       ├─ Render theo content_type:
  │           │                   │       │   ├─ text → MarkdownRenderer (dangerouslySetInnerHTML hoac parse)
  │           │                   │       │   ├─ video → <video> tag voi controls
  │           │                   │       │   └─ mixed → ca 2
  │           │                   │       ├─ Attachments: download list
  │           │                   │       ├─ Resources: grouped by type
  │           │                   │       ├─ Navigation: ← Bai truoc | Bai tiep →
  │           │                   │       ├─ Neu has_quiz = true:
  │           │                   │       │   └─ QuizPrompt: "Bạn cần làm quiz trước khi tiếp tục"
  │           │                   │       │       └─ Click → redirect QuizDetailPage
  │           │                   │       └─ Quiz flow → xem Flow 4
  │           │                   └─ Learning outcomes: checklist
  │           └─ Video preview modal (neu co preview_video_url)
  └─ Pagination component
```

### Flow 4: Làm Quiz

```
QuizDetailPage (/dashboard/quiz/:quizId)
  ├─ GET /quizzes/:quizId → hien thi:
  │   ├─ Title, description
  │   ├─ So cau hoi, thoi gian, dieu kien pass
  │   ├─ So lan da lam (user_attempts) / Diem cao nhat (best_score)
  │   └─ Nut "Bắt đầu làm bài"
  │       └─ QuizAttemptPage (/dashboard/quiz/:quizId/attempt)
  │           ├─ Timer countdown
  │           ├─ Question cards (render theo type: multiple_choice/fill_in_blank/true_false)
  │           ├─ Nut "Nộp bài" → POST /quizzes/:quizId/attempt
  │           └─ Response → redirect:
  │               └─ QuizResultsPage (/dashboard/quiz/:quizId/results)
  │                   ├─ Score: X/100 (CircularProgress)
  │                   ├─ Status banner: "Pass ✓" (xanh) hoac "Fail" (do)
  │                   ├─ Mandatory check: "Câu bắt buộc: Đạt/Chưa đạt"
  │                   ├─ Tung cau hoi: QuestionResultCard
  │                   │   ├─ Cau hoi + dap an hoc vien + dap an dung
  │                   │   ├─ Dung: nền xanh nhat / Sai: nền do nhat
  │                   │   ├─ Mandatory tag neu is_mandatory
  │                   │   ├─ Explanation (accordion mo rong)
  │                   │   └─ "Xem lai bai hoc" link (related_lesson_link)
  │                   ├─ Neu can_retake = true va passed = false:
  │                   │   └─ Nut "Làm lại" → POST /quizzes/:quizId/retake
  │                   │       → Nhan questions moi (AI generated) → quay lai QuizAttemptPage
  │                   └─ Neu passed = true:
  │                       └─ Nut "Tiếp tục bài học tiếp theo" → LessonPage(next_lesson)
```

### Flow 5: Chat với AI

```
ChatPage (/dashboard/chat)
  ├─ Layout: Sidebar (danh sach conversations) + Main (chat area)
  ├─ Sidebar:
  │   ├─ GET /chat/history → hien thi grouped_by_date
  │   │   ├─ "Hôm nay": conversation items
  │   │   ├─ "Hôm qua": ...
  │   │   └─ "Tuần này": ...
  │   ├─ Moi item: course_title, topic_summary, last_message_preview
  │   ├─ Click item → GET /chat/conversations/:id → load messages vao main area
  │   ├─ Nut "Xóa tất cả" → DELETE /chat/conversations (confirm modal)
  │   └─ Nut "X" tren moi item → DELETE /chat/history/:id (confirm)
  │
  └─ Main chat area:
      ├─ Messages list:
      │   ├─ User bubble (can phai, nen xam)
      │   └─ AI bubble (can trai, nen trang):
      │       ├─ Content: Markdown rendered
      │       ├─ Sources (collapsible): type icon + title + excerpt
      │       └─ Related lessons: clickable links
      ├─ Input area:
      │   ├─ Textarea (Enter gui, Shift+Enter xuong dong)
      │   └─ Nut "Gửi"
      └─ Submit → POST /chat/course/:courseId
          ├─ Hien thi typing indicator "AI đang trả lời..."
          └─ Nhan response → append AI bubble
```

### Flow 6: Quản lý lớp học (Instructor)

```
InstructorDashboard (/dashboard/instructor)
  ├─ GET /dashboard/instructor → widgets
  ├─ Quick actions: "Tạo lớp mới", "Xem tiến độ"
  └─ Click "Tạo lớp mới" →
      └─ ClassCreatePage (/dashboard/classes/create)
          ├─ Step 1: Chon khoa hoc (dropdown, load tu GET /courses/public)
          ├─ Step 2: Form: name, description, start_date, end_date, max_students
          ├─ Submit → POST /classes
          ├─ Thanh cong:
          │   ├─ Hien thi invite_code lon (copy-to-clipboard)
          │   └─ Nut "Xem lớp" → redirect ClassDetailPage
          └─ ClassListPage (/dashboard/classes)
              ├─ GET /classes/my-classes
              ├─ Cards: name, student_count ("25/30"), status badge, progress bar
              └─ Click → ClassDetailPage (/dashboard/classes/:classId)
                  ├─ GET /classes/:classId
                  ├─ Tab 1: Thong tin chung (name, invite_code, dates, stats)
                  ├─ Tab 2: Danh sach hoc vien
                  │   ├─ GET /classes/:classId/students
                  │   ├─ Table: name, email, progress bar, quiz_average, last_activity
                  │   ├─ Click row → StudentDetailModal
                  │   │   └─ GET /classes/:classId/students/:studentId
                  │   │       → quiz_scores[], modules_detail[], progress stats
                  │   └─ Nut "Xóa" → DELETE (confirm modal)
                  ├─ Tab 3: Tien do lop (GET /classes/:classId/progress)
                  └─ Tab 4: Quan ly quiz (link to quiz list filtered by class)
```

### Flow 7: Student tham gia lớp

```
DashboardPage hoac Sidebar → nut "Tham gia lớp"
  └─ JoinClassModal (modal overlay)
      ├─ Input: "Nhập mã mời" (6-8 ky tu)
      ├─ Submit → POST /classes/join {invite_code}
      ├─ Thanh cong:
      │   ├─ Hien thi: class_name, course_title, instructor_name
      │   ├─ Auto-enroll vao course lien ket (enrollment_id tra ve)
      │   └─ Nut "Bắt đầu học" → redirect CourseDetailPage/:courseId
      └─ That bai: "Mã mời không hợp lệ" / "Lớp đã đầy"
```

### Flow 8: Khóa học cá nhân

```
PersonalCoursesPage (/dashboard/personal-courses)
  ├─ GET /courses/my-personal → cards list
  ├─ Filter tabs: Tất cả / Nháp / Đã xuất bản
  ├─ Nut "Tạo bằng AI" →
  │   └─ Modal/Page:
  │       ├─ Textarea: prompt (20-1000 chars)
  │       │   Placeholder: "Toi muon hoc lap trinh Python co ban..."
  │       ├─ Select: level, duration_weeks, language
  │       ├─ Submit → POST /courses/from-prompt
  │       └─ Loading animation → redirect CourseEditorPage
  ├─ Nut "Tạo thủ công" →
  │   └─ Form: title, description, category, level
  │       ├─ Submit → POST /courses/personal
  │       └─ Redirect → CourseEditorPage
  └─ Click card →
      └─ CourseEditorPage (/dashboard/personal-courses/:courseId/edit)
          ├─ GET /courses/:courseId → load data
          ├─ Sidebar: Modules tree (drag-drop reorder)
          │   ├─ Click module → expand lessons
          │   ├─ Click lesson → load editor
          │   └─ Nut "+Thêm module" / "+Thêm bài học"
          ├─ Main area: Rich text editor (content editable)
          │   ├─ Text content: contentEditable div + formatting toolbar
          │   ├─ Video URL input
          │   └─ Attachments: react-dropzone
          ├─ Auto-save indicator: "Đã lưu" / "Đang lưu..."
          │   └─ Debounce 2-3 giay → PUT /courses/personal/:courseId
          └─ Nut "Xóa khóa học" → confirm → DELETE
```

### Flow 9: Admin Dashboard

```
AdminPage (/dashboard/admin)
  ├─ GET /dashboard/admin → overview cards:
  │   ├─ Tong users (breakdown: students/instructors/admins)
  │   ├─ Tong courses (public/personal, published/draft)
  │   ├─ Tong classes (active/completed/preparing)
  │   └─ Activity stats (enrollments/week, quizzes/today, active users)
  ├─ Sub-routes:
  │   ├─ /dashboard/admin/users → AdminUserListPage
  │   │   ├─ GET /admin/users (filters: role, status, search, sort)
  │   │   ├─ Table: avatar, name, email, role badge, status badge, last_login
  │   │   ├─ Click row → AdminUserDetailPage
  │   │   │   └─ GET /admin/users/:userId
  │   │   │       ├─ Profile card
  │   │   │       ├─ Activity summary
  │   │   │       ├─ Actions: "Đổi role", "Reset password", "Xóa"
  │   │   │       │   ├─ Doi role → Modal: select new_role → PUT /admin/users/:id/role
  │   │   │       │   │   → Hien thi impact analysis (affected_classes, affected_enrollments)
  │   │   │       │   ├─ Reset PW → Modal: input new password → POST /admin/users/:id/reset-password
  │   │   │       │   └─ Xoa → Confirm modal → DELETE /admin/users/:id
  │   │   └─ Nut "Tạo user mới" → Modal form → POST /admin/users
  │   │
  │   ├─ /dashboard/admin/courses → AdminCourseListPage
  │   │   ├─ GET /admin/courses (filter: author, type, status, category, search)
  │   │   └─ CRUD tương tự users
  │   │
  │   ├─ /dashboard/admin/classes → AdminClassListPage
  │   │   └─ GET /admin/classes → read-only monitoring
  │   │
  │   └─ /dashboard/admin/analytics → AdminAnalyticsPage
  │       ├─ Tab "Users": GET /admin/analytics/users-growth → LineChart
  │       ├─ Tab "Courses": GET /admin/analytics/courses → BarChart + Table top courses
  │       └─ Tab "System Health": GET /admin/analytics/system-health
  │           ├─ Status banner: healthy (xanh) / warning (vang) / critical (do)
  │           ├─ Gauge meters: CPU, Memory, Storage, Response Time
  │           └─ Alerts list: alert cards theo alert_type
```

### Flow 10: Dashboard theo role

```
DashboardPage (/dashboard)
  ├─ Lay user.role tu authStore
  ├─ Neu role === 'student':
  │   └─ GET /dashboard/student → render:
  │       ├─ Widget 1: "Khóa học đang học" → recent_courses[] (max 5)
  │       │   └─ Moi item: thumbnail, title, progress bar, "Tiep tuc" CTA
  │       ├─ Widget 2: "Quiz cần làm" → pending_quizzes[]
  │       │   └─ Moi item: title, course, due_date, status badge
  │       ├─ Widget 3: Stats cards (thong ke tong quan)
  │       │   ├─ Lessons: total_lessons_completed
  │       │   ├─ Score: average_quiz_score
  │       │   ├─ Streak: current_streak_days
  │       │   └─ Hours: total_study_hours
  │       └─ Widget 4: "Gợi ý" → recommendations[] (max 3)
  │
  ├─ Neu role === 'instructor':
  │   └─ GET /dashboard/instructor → render:
  │       ├─ Stat cards: active_classes, total_students, quizzes_created, avg_completion
  │       ├─ Recent classes (3 items)
  │       └─ Quick actions buttons
  │
  └─ Neu role === 'admin':
      └─ GET /dashboard/admin → render admin overview widgets
```

### Flow 11: Tìm kiếm

```
GlobalSearchBar (trong DashboardLayout header)
  ├─ Input field
  ├─ Khi typing (min 1 ky tu):
  │   └─ GET /search/suggestions?q=... (debounce 200ms)
  │       → Dropdown suggestions realtime
  ├─ Khi Enter hoac click "Tim" (min 2 ky tu):
  │   └─ GET /search?q=...&category=...&level=...
  │       → SearchResultsPage (/dashboard/search?q=...)
  │           ├─ Ket qua grouped by category (courses, users, classes...)
  │           ├─ Filters sidebar
  │           └─ "X kết quả trong Yms"
  └─ Khi focus va co lich su:
      └─ GET /search/history → recent searches dropdown
```

---

## 🎨 CSS CONVENTIONS

### Naming: BEM-like

```css
/* Block */
.course-card { }

/* Element */
.course-card__title { }
.course-card__thumbnail { }
.course-card__stats { }

/* Modifier */
.course-card--enrolled { }
.course-card--completed { }
```

### Layout Mobile-First

```css
/* Container chuan */
.page-container {
  padding: 16px;                /* Mobile */
  max-width: 100%;
}

@media (min-width: 768px) {
  .page-container {
    padding: 24px;
  }
}

@media (min-width: 1024px) {
  .page-container {
    padding: 32px;
    max-width: 1200px;
    margin: 0 auto;
  }
}

/* Grid responsive */
.card-grid {
  display: grid;
  grid-template-columns: 1fr;  /* Mobile: 1 cot */
  gap: 16px;
}

@media (min-width: 768px) {
  .card-grid {
    grid-template-columns: repeat(2, 1fr); /* Tablet: 2 cot */
  }
}

@media (min-width: 1024px) {
  .card-grid {
    grid-template-columns: repeat(3, 1fr); /* Desktop: 3 cot */
    gap: 24px;
  }
}
```

### Animation (framer-motion)

```jsx
import { motion } from 'framer-motion'

// Fade in khi mount
<motion.div
  initial={{ opacity: 0, y: 20 }}
  animate={{ opacity: 1, y: 0 }}
  transition={{ duration: 0.3 }}
>
  {/* content */}
</motion.div>
```

---

## 📐 ROUTING PLAN (bo sung routes can them)

```jsx
// Cac route can bo sung trong AppRouter.jsx:
// Tat ca nam trong <Route path="/dashboard" element={<DashboardLayout/>}>

// Assessment
<Route path="assessment" element={<AssessmentSetupPage />} />
<Route path="assessment/:sessionId" element={<AssessmentQuizPage />} />
<Route path="assessment/:sessionId/results" element={<AssessmentResultsPage />} />

// Learning
<Route path="courses/:courseId/modules" element={<ModuleListPage />} />
<Route path="courses/:courseId/modules/:moduleId" element={<ModuleDetailPage />} />
<Route path="courses/:courseId/lessons/:lessonId" element={<LessonPage />} />

// Quiz (bo sung)
<Route path="quiz/:quizId/attempt" element={<QuizAttemptPage />} />
<Route path="quiz/:quizId/results" element={<QuizResultsPage />} />

// Personal Courses
<Route path="personal-courses" element={<PersonalCoursesPage />} />
<Route path="personal-courses/:courseId/edit" element={<CourseEditorPage />} />

// Classes (Instructor)
<Route path="classes" element={<InstructorRoute><ClassListPage /></InstructorRoute>} />
<Route path="classes/create" element={<InstructorRoute><ClassCreatePage /></InstructorRoute>} />
<Route path="classes/:classId" element={<InstructorRoute><ClassDetailPage /></InstructorRoute>} />

// Search
<Route path="search" element={<SearchResultsPage />} />

// Recommendations
<Route path="recommendations" element={<RecommendationsPage />} />

// Admin sub-routes (trong AdminPage da co path="admin/*")
// /dashboard/admin/users, /users/:userId
// /dashboard/admin/courses, /courses/:courseId
// /dashboard/admin/classes, /classes/:classId
// /dashboard/admin/analytics
```
