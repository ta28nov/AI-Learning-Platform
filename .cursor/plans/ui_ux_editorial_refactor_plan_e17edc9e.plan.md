---
name: UI/UX Editorial Refactor Plan
overview: "Audit toàn bộ FE+BE rồi sinh 2 file markdown: `UI_UX_AUDIT.md` (snapshot hệ thống + BE issues cần rà) và `REFACTOR_PLAN.md` (lộ trình refactor 13 phase theo hướng Editorial Cinematic + Faux-3D, BẢO TOÀN service layer / store action / API contract; BE chỉ sửa tối thiểu để fix bug đã note)."
todos:
  - id: audit-md
    content: "Ghi docs/reports/UI_UX_AUDIT.md (6 mục: Tech Stack, Backend Interface Map, Frontend Component Tree, Data & State Flow, Technical Debt, BE Issues to Review) — dùng full dữ liệu từ 2 explore agent."
    status: completed
  - id: plan-md
    content: "Ghi docs/reports/REFACTOR_PLAN.md (13 Phase + Phase 0 BE-Bugfix tùy chọn; mỗi Phase: Mục tiêu / Files / API Contracts bảo toàn / Motion patterns / Acceptance) theo hướng Editorial Cinematic + Faux-3D."
    status: completed
  - id: handoff
    content: "Trả về thông báo kết thúc đúng nguyên văn: Đã hoàn tất kiểm toán hệ thống. Xin mời bạn xem xét kế hoạch. Nếu bạn đồng ý, hãy yêu cầu tôi bắt đầu Phase 1."
    status: completed
  - id: phase1-design-tokens
    content: "Phase 1 COMPLETED 2026-05-06: tokens.css + tokens-dark.css + motion.js + index.css refactor + index.html font pipeline. Build pass exit 0."
    status: completed
  - id: phase2-button
    content: "Phase 2: Refactor Button.jsx + Button.css — keep all props, add Framer Motion whileHover/whileTap + editorial sub-variants (Magnetic, Ghost, Link)."
    status: in_progress
  - id: phase2-input
    content: "Phase 2: Refactor Input.jsx + Input.css — keep all props, gold focus ring animation."
    status: pending
  - id: phase2-card
    content: "Phase 2: Refactor Card.jsx + Card.css — keep all props, faux-3D tilt + cursor tracking."
    status: pending
  - id: phase2-modal
    content: "Phase 2: Refactor Modal.jsx + Modal.css — keep all props, AnimatePresence cinematic backdrop."
    status: pending
  - id: phase2-stateview
    content: "Phase 2: Refactor StateView.jsx — keep API, editorial empty-state with stagger motion."
    status: pending
isProject: false
---

# UI/UX Editorial Refactor Plan

## Phạm vi & Nguyên tắc bất biến

- **CHỈ** sinh 2 file markdown ở phase này: `UI_UX_AUDIT.md` và `REFACTOR_PLAN.md`. Không sửa `.jsx` / `.tsx` / `.css` / Python / config nào.
- Lộ trình refactor sau này phải tuân thủ rào chắn:
  - **HẠN CHẾ** sửa BE: ưu tiên giữ nguyên `BE/routers`, `BE/services`, `BE/schemas`, `BE/models`, MongoDB shape, AI prompt-context flow (single-shot Gemini, **không phải RAG**, không có vector store / retriever). Chỉ chạm BE khi gặp bug rõ ràng đã được note ở mục "BE Issues to Review"; mỗi lần chạm phải có acceptance riêng và không phá contract FE đang dùng.
  - **KHÔNG** đổi chữ ký service FE: 17 file [`FE/src/services/*.js`](FE/src/services) giữ nguyên hàm xuất, đường dẫn URL, query param, body, header, timeout (`AI_TIMEOUT = 120000` được bảo toàn).
  - **KHÔNG** đổi chữ ký action của Zustand stores: [`authStore`](FE/src/stores/authStore.js), [`courseStore`](FE/src/stores/courseStore.js), [`uiStore`](FE/src/stores/uiStore.js); chỉ được refactor *internal*.
  - **KHÔNG** đổi đường dẫn route hoặc role guard trong [`AppRouter.jsx`](FE/src/AppRouter.jsx) và [`ProtectedRoute.jsx`](FE/src/components/layout/ProtectedRoute.jsx); chỉ refactor JSX bên trong.
  - **KHÔNG** đổi shape dữ liệu response vào/ra; nếu UI cần derive thêm thì làm ở selector/hook ở FE, không gọi sang BE.

> Đính chính thuật ngữ: hệ thống KHÔNG dùng RAG. AI flow (chat, assessment, recommendation, course-from-prompt) chỉ là **prompt engineering** — build context text từ MongoDB rồi gọi Gemini `generate_content` 1-shot. Không có embedding / vector store / retriever ở bất kỳ tầng nào.

## Định hướng thẩm mỹ đã chốt

- **Phong cách:** Editorial Cinematic — bố cục như tạp chí cao cấp, typography kịch tính, nền ink-black / cream warm, accent gold + copper + editorial vermilion.
- **Typography pairing (thay thế hoàn toàn Inter):**
  - Display: **Fraunces** (variable serif biểu cảm) hoặc **Instrument Serif** cho headline.
  - Body: **Newsreader** (Google Fonts, designed cho long-form reading).
  - Mono: **JetBrains Mono** (cho lesson code blocks).
- **3D:** Faux-3D bằng CSS `perspective` + `transform: rotateX/Y/Z` + Framer Motion `useScroll` / `useTransform` / `useSpring`. **Không** thêm `three`/`@react-three/fiber`.
- **Motion language:** scroll-linked parallax, page-turn transition (rotateY + perspective), stagger reveals, magnetic custom cursor, slow cinematic easing (`[0.65, 0, 0.35, 1]`).
- **Anti-pattern bị cấm:** gradient tím/xanh AI-slop, Inter/Roboto/Arial, emoji thay icon, monolith page > 600 dòng.

## Cấu trúc file `UI_UX_AUDIT.md` (Giai đoạn 1)

1. **Tech Stack & Libraries**
   - FE: liệt kê toàn bộ deps từ [`FE/package.json`](FE/package.json) (React 18.2, Vite 7.1, Axios 1.4, Zustand 4.5, React Router 6.26, Framer Motion 10.12, Recharts 2.12, react-hook-form 7.62, react-hot-toast 2.4, i18next stack hiện chưa dùng, react-dropzone hiện chưa dùng).
   - BE: từ [`BE/requirements.txt`](BE/requirements.txt) (FastAPI 0.116, Beanie 1.27, Motor 3.6, python-jose, passlib bcrypt, google-generativeai 0.8.3, **không có** vector store).
   - Cảnh báo dep dư thừa: `i18next*`, `react-dropzone`.

2. **Backend Interface Map**
   - Bảng endpoints FastAPI gắn `/api/v1`: Auth (4), Users (2), Courses (4), Modules+Lessons (6), Enrollments (4), Progress (1), Quiz (10), Assessment AI (3), Recommendation (2), Chat AI (5), Search (4), Analytics (8), Dashboard (3), Admin (15), Classes (10), Personal Courses (5).
   - Note AI prompt-context (KHÔNG phải RAG): chat AI dùng `_build_course_context` (text context từ Course/Module/Lesson titles + outcomes trong Mongo) + Gemini `generate_content` 1-shot, history 5 turn cuối, không streaming — implement trong [`BE/services/ai_service.py`](BE/services/ai_service.py). Tương tự cho assessment evaluation, recommendation reasons, course-from-prompt.
   - Note FE-BE alignment: bảng đối chiếu với `docs/reports/BE_FE_CONTRACT_MATRIX.md`.
   - Schema MongoDB cốt lõi từ [`BE/models/models.py`](BE/models/models.py): User, Course (embedded modules), Module, Lesson, Enrollment, Progress, Quiz, QuizAttempt, AssessmentSession, Conversation, Class, Recommendation.

3. **Frontend Component Tree** — sơ đồ tree phân loại Core UI / Layouts / Feature Pages, có mermaid diagram + bảng thống kê line count cho 30+ pages.

4. **Data & State Flow** — diagram + bảng:
   - Auth: Zustand persist + tokens trong localStorage, axios interceptor refresh-queue.
   - Chat AI: state cục bộ trong [`useChatLogic.js`](FE/src/hooks/useChatLogic.js) (không có store global). Gọi `chatService.sendMessage` → BE prompt-context Gemini → response 1-shot.
   - Learning progress: không có store, mỗi page tự fetch.
   - UI: `uiStore` định nghĩa nhưng [`DashboardLayout.jsx`](FE/src/components/layout/DashboardLayout.jsx) dùng local `useState` ⇒ disconnect.

5. **Technical Debt & UI Inconsistencies (FE)** — 14+ mục concrete, mỗi mục có file path + line:
   - Sidebar active state sai prefix (`startsWith('/courses')` thay vì `/dashboard/courses`).
   - Instructor CTA hỏng (`/dashboard/classes/create` thay vì `/dashboard/instructor/classes/create`).
   - Sidebar thiếu Assessment / Personal Courses / Recommendations / Search.
   - `uiStore` không được wire vào layout.
   - InstructorDashboardPage là placeholder dead-end.
   - Inline `<button>` raw, không dùng `Button` component.
   - Emoji 👋 📖 thay icon (cross-platform drift).
   - Inline styles `style={{ marginBottom: '0.5rem' }}` bypass tokens.
   - Chat error handling không phân biệt timeout / 401.
   - Inter font khai báo nhưng không load trong [`FE/index.html`](FE/index.html).
   - `userService` overlap `authService` ở `/users/me`.
   - Global `*:focus` outline noise cho mouse user (cần `:focus-visible`).
   - Forgot/reset/verify pages là stub do BE chưa có route.
   - Auth route layer phụ thuộc tokens trong localStorage (chấp nhận, ghi note).

6. **BE Issues to Review** — các điểm phát hiện trong lúc audit BE, **chưa fix**, để bạn quyết định scope. Mỗi mục có severity + file path + đề xuất:
   - **[Bug nhẹ]** [`BE/routers/recommendation_router.py`](BE/routers/recommendation_router.py) ~line 37: có một stray string expression giữa 2 handler (no-op runtime nhưng dirty). → đề xuất xoá.
   - **[Feature gap]** Chat controller [`BE/controllers/chat_controller.py`](BE/controllers/chat_controller.py): luôn trả `sources: []` và `related_lessons: []` mặc dù schema [`BE/schemas/chat.py`](BE/schemas/chat.py) hỗ trợ. → đề xuất populate từ context đã build trong `_build_course_context` (chỉ cần map module/lesson title đã đưa vào prompt).
   - **[Inconsistency]** Auth flows mở rộng: BE thiếu endpoints `forgot-password`, `reset-password`, `verify-email`, `resend-verification` nhưng FE đã có pages stub (đối chiếu `docs/reports/BE_FE_CONTRACT_MATRIX.md`). Có model `PasswordResetTokenDocument` trong [`BE/models/models.py`](BE/models/models.py) sẵn nhưng chỉ dùng cho admin reset. → quyết định: ship feature đầy đủ hay giữ stub.
   - **[Inconsistency]** RBAC enforcement không đồng nhất: `BE/middleware/rbac.py` định nghĩa `Permission` sets phong phú nhưng routers chủ yếu chỉ `get_current_user`, role gating nằm rải rác trong controllers/services (vd. `quiz_controller`, `chat_controller`, `admin_*`). → đề xuất gom guard về middleware bằng decorator chuẩn.
   - **[Schema alignment]** [`BE/services/assessment_service.py`](BE/services/assessment_service.py) khi submit, pack nested dict + breakdown vào field `skill_analysis` trên `AssessmentSession`; cần xác nhận khớp với `AssessmentResultsResponse` (kiểu list) trong [`BE/schemas/assessment.py`](BE/schemas/assessment.py). → cần kiểm tra runtime hoặc pydantic validation.
   - **[Search behavior]** [`BE/services/search_service.py`](BE/services/search_service.py): result `User` chỉ trả cho admin/instructor (instructor giới hạn students). Đây là intent hay restriction quá chặt? → confirm với product.
   - **[Search history]** Endpoint `GET /search/history` hiện stub trả empty + popular terms (theo audit). → đề xuất implement persistence nếu dùng cho UX gợi ý.
   - **[Analytics guard]** `GET /analytics/learning-stats` và `GET /analytics/progress-chart` hiện không strict role-check trong controller — bất kỳ user authenticated nào cũng gọi được. → confirm có cố ý không (chấp nhận) hay cần thêm guard student-only.
   - **[AI prompt]** [`BE/services/ai_service.py`](BE/services/ai_service.py) `_build_course_context` chỉ đưa **title/description/outcomes/module-lesson titles** chứ **không** đưa nội dung lesson body vào prompt → chất lượng câu trả lời AI bị giới hạn. Nếu muốn nâng độ liên quan, vẫn có thể giữ "không phải RAG" bằng cách stuff thêm `excerpt` body vào prompt (vẫn là prompt engineering). → đề xuất nâng cấp prompt-builder, không cần thêm vector store.
   - **[Bundle dọn dẹp BE]** Windows-only deps (`python-magic-bin`) trong [`BE/requirements.txt`](BE/requirements.txt) sẽ vỡ trên Linux/Mac CI. → tách thành `requirements-dev-windows.txt` hoặc bọc bằng marker `; sys_platform == "win32"`.
   - **[Init data]** [`BE/scripts/init_data.py`](BE/scripts/init_data.py) seed mật khẩu mặc định in plain trong code. → OK cho demo; nếu deploy phải override qua env.

   **Quy tắc xử lý:** Mỗi issue nếu fix sẽ có 1 entry trong `REFACTOR_PLAN.md` Phase 0 (BE Bugfix tùy chọn) — bạn duyệt từng item, không fix ngầm.

## Cấu trúc file `REFACTOR_PLAN.md` (Giai đoạn 2)

13 Phase chính theo nguyên tắc "tằm ăn rỗi" + 1 **Phase 0 BE-Bugfix tùy chọn** (chỉ chạy khi bạn duyệt từng item). Mỗi phase có: **Mục tiêu / Files chạm vào / API contracts được bảo toàn / Motion patterns / Acceptance criteria**.

- **Phase 0 (tùy chọn) — BE Bugfix theo danh sách "BE Issues to Review"**
  - Mỗi issue audit là một sub-task riêng, có toggle `[ ] enable / [x] enable` để bạn check.
  - Các fix ưu tiên (gợi ý): xoá stray string ở `recommendation_router.py`; populate `sources` + `related_lessons` từ context có sẵn trong chat controller; bọc Windows deps trong `requirements.txt`; (lớn hơn — bạn duyệt mới làm) nâng `_build_course_context` để stuff lesson excerpt; gom RBAC; ship đủ auth extension routes.
  - **Nguyên tắc:** mọi fix BE phải giữ shape response cũ hoặc chỉ thêm field optional; FE service không phải đổi.
  - Acceptance: pytest BE pass, smoke test 4 luồng AI chính (chat, assessment, recommendation, course-from-prompt), `BE_FE_CONTRACT_MATRIX.md` cập nhật trạng thái.

- **Phase 1 — Design System & Tokens**
  - Refactor [`FE/src/styles/index.css`](FE/src/styles/index.css): thay palette → ink/cream/gold/copper/vermilion; bộ token semantic (`--ink-900`, `--cream-50`, `--gold-500`, `--copper-600`, `--vermilion-500`, `--jade-500`); spacing scale dạng editorial (4/8/16/32/64/128); type scale (12/14/16/20/28/40/64/96).
  - Tạo `FE/src/styles/tokens.css` (light) + `FE/src/styles/tokens-dark.css` (dark) với `[data-theme]` switch giữ nguyên cơ chế [`ThemeContext.jsx`](FE/src/contexts/ThemeContext.jsx).
  - Load fonts qua `<link>` ở [`FE/index.html`](FE/index.html) hoặc `@import` ở `index.css`: Fraunces, Newsreader, JetBrains Mono.
  - Tạo `FE/src/styles/motion.js` chứa easing constants + variants chuẩn (`fadeUp`, `staggerContainer`, `pageTurn`, `magneticHover`).
  - Sản phẩm: tokens + fonts + motion preset. Không component nào đổi behavior.

- **Phase 2 — Core UI Components**
  - Nâng cấp [`Button.jsx`](FE/src/components/ui/Button.jsx), [`Card.jsx`](FE/src/components/ui/Card.jsx), [`Input.jsx`](FE/src/components/ui/Input.jsx), [`Modal.jsx`](FE/src/components/ui/Modal.jsx), [`StateView.jsx`](FE/src/components/ui/StateView.jsx).
  - Bắt buộc giữ nguyên props API (variant, size, onClick, type, ...).
  - Thêm internal: Framer Motion `whileHover`/`whileTap` với spring; magnetic effect cho primary Button; Card có `transform-style: preserve-3d` + tilt theo cursor; Modal dùng `AnimatePresence` + backdrop blur cinematic.
  - Tách `Button` con: `Button.Magnetic`, `Button.Ghost`, `Button.Editorial` (text-link với underline animated).
  - Acceptance: Mọi import cũ vẫn build & runtime ok, không trang nào vỡ.

- **Phase 3 — Global Layout & Navigation**
  - Tách monolith [`DashboardLayout.jsx`](FE/src/components/layout/DashboardLayout.jsx) → 4 file: `DashboardShell.jsx`, `Header.jsx`, `Sidebar.jsx`, `MobileDrawer.jsx`.
  - Wire `uiStore` thật sự vào sidebar/drawer (xóa local state).
  - **Fix bug**: `isActive` dùng `startsWith('/dashboard/courses')` đúng prefix.
  - **Fix bug**: link instructor `/dashboard/classes/create` → `/dashboard/instructor/classes/create` ở [`DashboardPage.jsx`](FE/src/pages/dashboard/DashboardPage.jsx).
  - Bổ sung mục sidebar còn thiếu: Đánh giá năng lực, Khóa học cá nhân, Tìm kiếm, Gợi ý.
  - Custom magnetic cursor (`MagneticCursor.jsx`) overlay toàn app, ẩn trên touch device.
  - Page transition wrapper dùng `AnimatePresence mode="wait"` với hiệu ứng page-turn (rotateY 0→-15deg + opacity).
  - Footer editorial mỏng (chỉ hiện ngoài dashboard).
  - Acceptance: 100% routes cũ render, 100% role guard giữ nguyên, không nhảy 404.

- **Phase 4 — Landing Page**
  - Refactor [`LandingPage.jsx`](FE/src/pages/landing/LandingPage.jsx) thành scrollytelling 6 chapter với `useScroll` + parallax depth layers (CSS `transform: translateZ()` + Framer Motion `useTransform`).
  - Hero: typography reveal letter-by-letter (Fraunces 96px), background noise + gradient mesh tĩnh.
  - Section transitions: pin + scrub (faux-pin bằng `position: sticky` + `useScroll`).
  - Acceptance: load < 2s trên LAN, không phá CTA `/auth/register`.

- **Phase 5 — Auth Pages**
  - Refactor [`LoginPage.jsx`](FE/src/pages/auth/LoginPage.jsx), [`RegisterPage.jsx`](FE/src/pages/auth/RegisterPage.jsx) thành split-screen editorial: trái là editorial pull-quote động, phải là form pixel-perfect.
  - Stub pages (forgot/reset/verify) giữ logic "throw" trong [`authService.js`](FE/src/services/authService.js); chỉ đổi visual sang editorial empty-state.
  - Acceptance: react-hook-form vẫn submit như cũ, error path từ BE hiển thị qua `react-hot-toast`.

- **Phase 6 — Dashboard (Student/Instructor/Admin)**
  - Refactor [`DashboardPage.jsx`](FE/src/pages/dashboard/DashboardPage.jsx) (441 dòng) thành 1 shell + 3 widget files: `StudentDashboard.jsx`, `InstructorDashboard.jsx`, `AdminDashboard.jsx`.
  - Editorial card grid bất đối xứng, stagger reveal khi vào trang.
  - Greeting `👋` thay bằng thời điểm trong ngày + ornament SVG.
  - Acceptance: gọi `dashboardService.getStudent/Instructor/Admin` đúng như cũ, fallback skeleton + empty state qua `StateView`.

- **Phase 7 — Courses Catalog + Course Detail**
  - [`CoursesPage.jsx`](FE/src/pages/courses/CoursesPage.jsx): masonry grid editorial, course card có cover image + cinematic tilt 3D (CSS perspective).
  - [`CourseDetailPage.jsx`](FE/src/pages/courses/CourseDetailPage.jsx): hero full-bleed + sticky enrollment CTA + module accordion với expand transition.
  - Acceptance: `courseService.searchCourses` / `getPublicCourses` / `getCourseDetail` / `getEnrollmentStatus` không đổi.

- **Phase 8 — Learning Flow (sweet spot scrollytelling)**
  - [`ModuleListPage.jsx`](FE/src/pages/learning/ModuleListPage.jsx): timeline dọc editorial, mỗi module là 1 chapter card.
  - [`ModuleDetailPage.jsx`](FE/src/pages/learning/ModuleDetailPage.jsx): 2-column reading layout (TOC sticky trái, content phải).
  - [`LessonPage.jsx`](FE/src/pages/learning/LessonPage.jsx): long-form reading mode, progress bar scroll-linked, drop cap đầu đoạn, code block JetBrains Mono.
  - Acceptance: `learningService.*` 6 endpoint không đổi (kể cả AI generate quiz module).

- **Phase 9 — Quiz + Assessment + Results**
  - [`QuizAttemptPage.jsx`](FE/src/pages/quiz/QuizAttemptPage.jsx) + [`AssessmentQuizPage.jsx`](FE/src/pages/assessment/AssessmentQuizPage.jsx): full-screen editorial 1 câu/trang, transition page-turn giữa câu.
  - [`AssessmentResultsPage.jsx`](FE/src/pages/assessment/AssessmentResultsPage.jsx): hero kết quả + skill breakdown (Recharts radar custom theme), knowledge gaps cards.
  - Acceptance: `assessmentService.generate/submit/getResults` (giữ `AI_TIMEOUT`) + `quizService.*` không đổi.

- **Phase 10 — Chat AI (prompt-context, KHÔNG phải RAG)**
  - [`ChatPage.jsx`](FE/src/pages/chat/ChatPage.jsx) (378 dòng) tách: `ChatShell.jsx`, `ConversationSidebar.jsx`, `MessageStream.jsx`, `MessageBubble.jsx`, `Composer.jsx`, `ContextDrawer.jsx` (hiển thị `sources` + `related_lessons` nếu BE populate).
  - Bubble editorial: assistant nền cream + serif body; user nền ink + sans subtle.
  - `AnimatePresence` cho từng message + typing indicator dạng ellipsis editorial.
  - **Giữ nguyên** [`useChatLogic.js`](FE/src/hooks/useChatLogic.js) — chỉ tách presentational layer.
  - Note (đã ghi ở "BE Issues to Review"): hiện `sources` và `related_lessons` trả `[]`. FE render forward-compatible: nếu BE Phase 0 populate, drawer tự bật; nếu không, ẩn drawer mà không gây lỗi.
  - Acceptance: `chatService.sendMessage/getHistory/getConversation/deleteAll/deleteOne` byte-identical.

- **Phase 11 — Search + Recommendations + Personal Courses**
  - [`SearchResultsPage.jsx`](FE/src/pages/search/SearchResultsPage.jsx): kết quả editorial grouped by category + filter chips.
  - [`RecommendationsPage.jsx`](FE/src/pages/recommendations/RecommendationsPage.jsx): "Lộ trình đề xuất" như infographic dài cuộn dọc, mỗi recommended course là card editorial.
  - [`PersonalCoursesPage.jsx`](FE/src/pages/personal-courses/PersonalCoursesPage.jsx) + [`CourseEditorPage.jsx`](FE/src/pages/personal-courses/CourseEditorPage.jsx): editor cinematic 2-pane.
  - Acceptance: `searchService.*`, `recommendationService.*`, `personalCourseService.*` (`/courses/from-prompt` với `AI_TIMEOUT`) không đổi.

- **Phase 12 — Profile + Progress**
  - [`ProfilePage.jsx`](FE/src/pages/profile/ProfilePage.jsx): magazine cover layout, edit mode inline.
  - [`ProgressPage.jsx`](FE/src/pages/progress/ProgressPage.jsx): Recharts theme editorial (gold gradient line, axis Newsreader 12px), streak ring với `motion.path strokeDashoffset`.
  - Acceptance: `progressService.getCourseProgress` + `analyticsService.*` (8 endpoint) không đổi.

- **Phase 13 — Admin Console + Polish**
  - [`AdminPage.jsx`](FE/src/pages/admin/AdminPage.jsx) (686 dòng) tách: `AdminShell.jsx`, `UsersTab.jsx`, `CoursesTab.jsx`, `ClassesTab.jsx`, `AnalyticsTab.jsx`. Editorial denser nhưng vẫn nhịp typography.
  - Polish toàn cục:
    - `:focus-visible` (thay `*:focus`).
    - `prefers-reduced-motion` → disable parallax + page-turn.
    - Lazy-load font-display swap, preload Fraunces variable.
    - Bundle audit: gỡ `i18next*`, `react-dropzone` nếu không dùng.
    - A11y: aria-label cho nav, focus trap trong Modal, contrast AAA cho ink-on-cream.
  - Acceptance: Lighthouse a11y ≥ 95, không trang nào còn dùng emoji thay icon, không file > 400 dòng (trừ AdminPage tabs hợp lý).

## Quy trình thực hiện sau khi bạn duyệt plan này

1. Tôi switch sang Agent mode (chỉ để cho phép ghi file).
2. Ghi `UI_UX_AUDIT.md` ở đường dẫn `docs/reports/UI_UX_AUDIT.md` (cùng folder với `BE_FE_CONTRACT_MATRIX.md`) với 6 mục bao gồm "BE Issues to Review".
3. Ghi `REFACTOR_PLAN.md` ở đường dẫn `docs/reports/REFACTOR_PLAN.md` với Phase 0 (BE Bugfix tùy chọn) + 13 Phase FE.
4. Trả về thông báo: "Đã hoàn tất kiểm toán hệ thống. Xin mời bạn xem xét kế hoạch. Nếu bạn đồng ý, hãy yêu cầu tôi bắt đầu Phase 1."
5. **Không** đụng bất kỳ file `.jsx` / `.css` / Python nào ở giai đoạn này.

## Câu hỏi mở (không chặn plan, có thể xử lý sau)

- Có muốn tôi đặt 2 file ở `docs/reports/` (gần `BE_FE_CONTRACT_MATRIX.md`) hay ở root repo? Mặc định tôi chọn `docs/reports/` để gom doc về một chỗ. Nếu bạn muốn root, báo lại trước khi tôi ghi.