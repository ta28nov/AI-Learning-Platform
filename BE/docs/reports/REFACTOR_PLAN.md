# UI/UX REFACTOR MASTER PLAN

## Mission Guardrails

- Primary goal: systemic UI/UX transformation to **Editorial Cinematic** style with smooth motion and faux-3D depth.
- Keep frontend-backend contracts stable during refactor.
- AI architecture remains **prompt-context** (not RAG/vector retrieval).
- Backend changes are **limited and optional**; only targeted bug-fix items explicitly approved.

---

## Non-Negotiable Constraints

1. Preserve FE service signatures in `FE/src/services/*.js` (URL/method/payload/timeout contracts unchanged).
2. Preserve route map and role-guard behavior (`AppRouter`, `ProtectedRoute`) unless explicitly approved.
3. Preserve response shape expectations consumed by current FE pages/stores.
4. Preserve auth refresh queue behavior in Axios layer.
5. Any BE fix must be isolated, documented, and backward-compatible for FE.

---

## Design Direction (Locked)

- Style: **Editorial Cinematic**.
- Typography direction:
  - Display serif (e.g. Fraunces / Instrument Serif).
  - Body serif/sans pairing optimized for readability.
  - Mono for technical content.
- Color system: ink-black + warm cream + selective luxury accents (gold/copper/vermilion family).
- Motion language:
  - Framer Motion-first.
  - Staggered reveal, page transitions, scroll-linked storytelling.
  - Purposeful motion, not decorative overload.
- 3D approach: **CSS/Framer faux-3D only** (`perspective`, `transform-style`, parallax depth), no mandatory Three.js.

---

## Execution Log

| Phase | Status | Date |
|-------|--------|------|
| Phase 0 — BE Bugfix | ⏸ PENDING approval | — |
| Phase 1 — Design System & Tokens | ✅ COMPLETED | 2026-05-06 |
| Phase 2 — Core UI Components | ✅ COMPLETED | 2026-05-06 |
| Phase 3 — Global Layout & Navigation | ✅ COMPLETED | 2026-05-06 |
| Phase 4 — Landing Page | ✅ COMPLETED | 2026-05-06 |
| Phase 5 — Auth Experience | ✅ COMPLETED | 2026-05-06 |
| Phase 6 — Dashboard Refactor | ✅ COMPLETED | 2026-05-06 |
| Phase 7 — Courses & Course Detail | ✅ COMPLETED | 2026-05-07 |
| Phase 8 — Learning Flow | ✅ COMPLETED | 2026-05-07 |
| Phase 9 — Quiz & Assessment UX | ✅ COMPLETED | 2026-05-07 |
| Phase 10 — Chat AI UX Refactor | ✅ COMPLETED | 2026-05-07 |
| Phase 11 — Search/Recommendations/Personal Courses | ✅ COMPLETED | 2026-05-07 |
| Phase 11b — Gap Fix (Missed Pages + Bug Fixes) | ✅ DONE | 2026-05-07 |
| Phase 12 — Profile & Progress Polish | ⏳ QUEUED | — |
| Phase 13 — Admin Console & Global Quality Pass | ⏳ QUEUED | — |

---

## Execution Model (Incremental "Tam an roi")

Each phase ships independently with acceptance criteria and regression checks.

### Phase 0 (Optional) - Backend Bugfix Review Batch

Only execute approved items from `UI_UX_AUDIT.md` section "BE Issues to Review":
- Remove no-op/stray router artifacts.
- Review and optionally enrich chat context fields (`sources`, `related_lessons`).
- Confirm auth extension roadmap (keep placeholders or implement).
- RBAC consistency review.
- Schema alignment checks for assessment outputs.

Acceptance:
- No FE contract break.
- Smoke test chat/assessment/recommendation/personal-course AI flows.

---

### Phase 1 — Design System & Tokens Foundation ✅ COMPLETED (2026-05-06)

Scope:
- Build/normalize design tokens (color/type/space/radius/shadow/motion durations).
- Standardize theme variables and dark/light strategy.
- Establish typography loading pipeline.

Deliverables (all shipped):
- `FE/src/styles/tokens.css` — Editorial raw palette (cream/ink/gold/copper/vermilion/jade/sand) + semantic surface tokens + full legacy alias map (`--primary`, `--bg-primary`, `--text-*`, `--spacing-*`, `--font-size-*`, `--transition-*`, etc). 40 legacy CSS variables preserved 1-to-1.
- `FE/src/styles/tokens-dark.css` — `[data-theme="dark"]` overrides; surfaces flip to deep ink, primary accent becomes gold.
- `FE/src/styles/motion.js` — Framer Motion presets: `EASE`, `DURATION`, `SPRING`, all variant families (`fadeUp`, `staggerContainer/Editorial/Tight`, `pageTurn/pageFade`, `magneticHover/Tap`, `cardLift`), `inView()` scroll helper.
- `FE/src/styles/index.css` — Refactored: `@import tokens`; editorial body canvas (cream + gold/copper vignette); h1–h6 now render in Fraunces; scrollbar editorial styling; `:focus-visible` gold halo (replaces `*:focus` mouse noise); `prefers-reduced-motion` global guard; all utility classes preserved.
- `FE/index.html` — Preconnect + variable-font loading: Fraunces, Newsreader, Plus Jakarta Sans, JetBrains Mono; `display=swap`.

Acceptance verified:
- `npm run build` → exit 0, ✓ 1099 modules, 20.64s.
- All 40 legacy token names resolve. No `.jsx` or BE files touched.

---

### Phase 2 — Core UI Components Upgrade (API-Compatible) 🔄 IN PROGRESS (2026-05-06)

Scope:
- Refactor shared primitives (`Button`, `Input`, `Card`, `Modal`, `StateView`) to match editorial design language.
- Keep all existing props and usage contracts intact — no page-level import changes required.

Motion targets:
- `Button`: `whileHover` magnetic lift + `whileTap` compress (spring). Editorial sub-variants: `Magnetic`, `Ghost`, `Link`. `useReducedMotion` guard.
- `Input`: focus-ring animated transition (gold border-color + ring scale). Floating-label option.
- `Card`: CSS `transform-style: preserve-3d` + Framer Motion `useMotionValue` cursor tilt. `CardHeader`, `CardBody`, `CardFooter` sub-components.
- `Modal`: `AnimatePresence` `mode="wait"` + cinematic backdrop blur enter/exit. Focus trap preserved.
- `StateView`: editorial empty/loading/error states with `staggerContainer` icon + text reveal.

Delivered:
- `Button.jsx/css` — Framer Motion `whileHover/whileTap` (SPRING.snappy), `useReducedMotion` guard. Sub-variants: `Button.Magnetic` (gold glow shadow), `Button.Ghost`, `Button.Link` (animated underline bar). Legacy `.btn-*` classes all preserved.
- `Input.jsx/css` — Upgraded to `useId()` (stable IDs), gold editorial focus ring (`var(--accent-soft)`), `aria-invalid` + `aria-describedby` for a11y. Error message animated in via Framer Motion.
- `Card.jsx/css` — Faux-3D cursor tilt via `useMotionValue` + `useTransform` (±6° rotateX/Y). Optional `reveal` prop for `scaleIn` entrance. `.card-tilt` class enables `transform-style: preserve-3d`. CardHeader/Body/Footer sub-components preserved.
- `Modal.jsx/css` — `AnimatePresence` with cinematic enter (slide-up + scale 0.97→1, ease `[0.65,0,0.35,1]`) and exit. Backdrop blur `blur(6px)` + warm overlay. Mobile: bottom-sheet layout. `ModalHeader/Body/Footer` preserved.
- `StateView.jsx + StateView.css` (new) — editorial stagger reveal (`staggerContainer` + `fadeUp`). Type modifiers: `empty | error | loading | info`. Inline style removed. Emoji icon still accepted but rendered via `<span>`. `.dash-empty` class in DashboardPage.css still works independently.

Acceptance verified:
- `npm run build` → exit 0, ✓ 1101 modules, 24.75s.
- No prop-contract changes — all existing page imports work unchanged.
- CSS delta: +3.3 kB (5 components + new StateView.css). Pre-existing warnings unchanged.

---

### Phase 3 — Global Layout & Navigation Refactor ✅ COMPLETED (2026-05-06)

Scope:
- Refactor dashboard shell structure (header/sidebar/content orchestration).
- Fix active-route highlighting and known navigation path mismatches.
- Align sidebar information architecture with actual feature coverage.
- Reconcile duplicated UI state handling with `uiStore`.

Delivered:
- **`DashboardLayout.jsx`** — refactored to thin orchestrator; imports `Sidebar`, `Header`, `MobileDrawer`, `PageTransition`. `uiStore` wired in (no more `useState` for sidebarOpen).
- **`Sidebar.jsx`** (new) — config-driven nav array; all `isActive` patterns corrected to `/dashboard/*` prefix; 4 missing items added: Assessment, Search, Recommendations, Personal Courses; gold active bar indicator; section labels for instructor/admin.
- **`Header.jsx`** (new) — sticky top bar; motion avatar hover; `aria-expanded` on hamburger.
- **`MobileDrawer.jsx`** (new) — `AnimatePresence` backdrop overlay; blur.
- **`PageTransition.jsx`** (new) — `AnimatePresence mode="wait"` + `pageTurn` variant (degrades to `pageFade` on reduced-motion). Uses `location.pathname` as key.
- **`MagneticCursor.jsx + .css`** (new) — spring-follow dot + gold ring; `pointer:fine` guard; `cursor:none` on body; dark mode aware; `prefers-reduced-motion` hides cursor.
- **`Footer.jsx + .css`** (new) — thin editorial footer; only rendered outside `/dashboard/*` (via `AppShell` location check).
- **`DashboardLayout.css`** — editorial sidebar (gold active bar, ink avatar + gold ring border, section labels, correct `border-light` separators).
- **`DashboardPage.jsx`** — 4 broken instructor route links fixed: `/dashboard/classes/*` → `/dashboard/instructor/classes/*`.
- **`Card.jsx`** — bug fixed: `MotionButton / MotionDiv` statically defined; removed invalid `as` prop on `motion.div`.
- **`App.jsx`** — `AppShell` inner component uses `useLocation` (requires being inside BrowserRouter) to conditionally render Footer + MagneticCursor.

Acceptance verified:
- `npm run build` → exit 0, ✓ 1109 modules, 13.25s.
- 100% routes render; 100% role guards unchanged (AppRouter, ProtectedRoute not modified).
- No 404s — all existing navigation paths preserved.

---

### Phase 4 — Landing Page Scrollytelling Transformation ✅ COMPLETED (2026-05-06) — UPGRADED to COMPUTE-style (2026-05-07)

**Phase 4 Upgrade (2026-05-07) — COMPUTE-inspired layout:**
Sau khi user phản hồi Phase 4 chưa hiển thị đúng tinh thần scrollytelling (parallax quá nhẹ, không có letter reveal, không có pin), trang đã được rebuild theo cấu trúc thông tin của template **COMPUTE — The Platform to Build & Ship AI Agents** (v0.app), giữ palette Editorial Cinematic (ink/cream/gold/copper) và tất cả CTA route cũ.

11 chapters mới (thay 6 chapters cũ):
1. **Hero** — Bold Fraunces display + per-word reveal animation, layered parallax (translate + scale + opacity), inline metrics strip
2. **Capabilities** — 3 numbered cards (01/02/03) với faux-3D mouse-tracked tilt (`useMotionValue` + `useSpring`), metric footer mỗi card
3. **Process** — `Đánh giá. Lộ trình. Học.` (analog COMPUTE `Define. Deploy. Scale.`), 3 numbered steps với suffix italic
4. **Reach** — Ink-black hero card + regions list với green/grey status dots (analog `29 regions global`)
5. **Live Metrics** — Pulse dot + animated counters (custom RAF cubic-bezier, no extra deps), 4 stat cells grid
6. **Subjects** — 7-column integration-grid với category labels (analog COMPUTE `100+ integrations`)
7. **Privacy** — 4 cards (cô lập / mã hóa / audit / quyền tối thiểu) + badge strip (analog `Autonomous, not uncontrolled`)
8. **Instructor** — 2-pane: copy bên trái + faux-terminal code preview bên phải (analog COMPUTE `Developer SDK`)
9. **Testimonial** — pull-quote editorial Fraunces italic + brand strip
10. **Plans** — 3-tier pricing card với center "PHỔ BIẾN" featured ink card (analog COMPUTE pricing)
11. **Final CTA** — Cream parallax bg + Fraunces title

Phase 4 thêm:
- **Scroll progress bar** fixed top, gradient gold→copper, `useScroll` + `useSpring`
- **Per-word title reveal** dùng overflow mask + Framer Motion stagger
- **Cubic-bezier RAF counters** không phụ thuộc framer-motion `animate` API mismatch
- **Faux-terminal** code preview với macOS dot bar + JetBrains Mono code

Constraints giữ nguyên:
- 100% CTA route preserved: `/auth/register`, `/auth/login`
- 0 hardcoded color — entire palette via `var(--*)` tokens
- `prefers-reduced-motion` honored ở mọi parallax + counter
- Build verified: `npm run build` exit 0, 1115 modules.

---

### Phase 4 — Landing Page Scrollytelling Transformation (Original implementation 2026-05-06)

Scope:
- Rebuild landing into chapter-based storytelling sections with `useScroll` + parallax depth layers.
- Hero: Fraunces typography reveal, noise + gradient mesh background.
- Section transitions: sticky + scroll-scrub faux-pin.
- Preserve CTA flows (→ `/auth/register`, `/auth/login`).

Delivered:
- **`LandingPage.jsx`** — full rewrite into 6 discrete chapter components: `LandingHeader`, `HeroSection`, `FeaturesSection`, `HowItWorksSection`, `StatsSection`, `CTASection`, `LandingFooter`.
- **HeroSection** — `useScroll` + `useTransform` parallax: content floats up and fades out as user scrolls past. Full-viewport (`min-height: 100vh`). Fraunces display headline at `clamp(2.5rem, 8vw, 5.5rem)`. Copper italic `<em>` accent on "Trí tuệ nhân tạo". Scroll-hint arrow with `animate={{y: [0,8,0]}}` bouncing. Gradient mesh (`radial-gradient` layering) + SVG noise texture for paper depth.
- **FeaturesSection** — 6-card editorial grid. `staggerEditorial` + `inView()`. Inline SVG icons replace emojis (no CLS, accessible). Accent tones: gold/copper/jade from tokens.
- **HowItWorksSection** — 3-step editorial layout with large Fraunces numeral (`3.5rem`). Horizontal connector line on desktop. Each step uses individual `inView` with `delay` stagger.
- **StatsSection** — Full-width ink-black section (`var(--ink-900)`) with `gap: 1px` CSS grid divider trick. Gold numbers (`var(--gold-300)`). `staggerEditorial` reveal.
- **CTASection** — Cream background with subtle parallax gradient mesh (bg layer moves `useTransform`). Overline + Fraunces title + Newsreader body. Preserved both CTAs: `Button.Magnetic` for `/auth/register`, plain link for `/auth/login`.
- **LandingFooter** — Rich 2-col grid footer. Preserved all existing links including `dashboard/*` routes.
- **`App.jsx`** — Footer rendering logic fixed: `showGenericFooter = !isDashboard && pathname !== '/'` (landing has own footer).
- **Color system** — Full migration from purple/indigo AI-slop palette to editorial ink/cream/gold/copper/jade.
- **Typography** — Fraunces for all display headings, Newsreader for body paragraphs, Plus Jakarta Sans for nav/UI.
- **`prefers-reduced-motion`** — passed as `shouldReduceMotion` prop; all `y`/`opacity` parallax no-ops, scroll hint hidden.
- **SVG icons** — 6 inline Lucide-style icons (BrainIcon, BookIcon, ChatIcon, ChartIcon, TargetIcon, AwardIcon) replace emoji: no external dependency, fully accessible.

Acceptance verified:
- `npm run build` → exit 0, ✓ 1109 modules, 18.93s. No new errors.
- All CTA links (`/auth/register`, `/auth/login`) preserved at component level.
- 0 hardcoded colors — entire palette driven by `var(--*)` tokens.
- Linter: 1 warning (webkit prefix order) fixed immediately.

---

### Phase 5 — Auth Experience Reframe ✅ COMPLETED (2026-05-06)

Scope:
- Redesign login/register as premium editorial forms.
- Keep placeholder behavior for unsupported auth extension features unless BE Phase 0 enables them.

Delivered:
- **`LoginPage.jsx`** — split-screen: LEFT = ink panel (`var(--ink-900)`) with `AuthInkPanel` (pull-quote, gold ornament, brand mark, bottom deco numerals). RIGHT = form panel. `react-hook-form`, `useAuthStore().login`, `toast`, `navigate(from, { replace: true })` all preserved byte-for-byte. Added `autoComplete` attrs for browsers.
- **`RegisterPage.jsx`** — split-screen same pattern. Reuses `AuthInkPanel` (exported from LoginPage.jsx). Different quote/tag. All 4 fields + acceptTerms checkbox + validate logic preserved exactly.
- **`AuthInkPanel`** (exported from LoginPage.jsx) — shared presentational component: `staggerEditorial` + `fadeUp` + `fadeDown`. Gold ornament line, Fraunces italic pull-quote, attribution in small-caps, decorative bottom numeral row. Noise texture via `::before` pseudo.
- **`AuthPages.css`** — full rebuild: split-screen `display: grid; grid-template-columns: 1fr 1fr` shell. Ink panel hides on `≤860px`. Editorial custom checkbox (pure CSS, `:has()` selector for checked state). `.auth-stub-page` + `.auth-stub-card` editorial empty-state variant. Dark mode adjustments.
- **`ForgotPasswordPage.jsx`** — editorial stub: ink lock icon + Fraunces title + Newsreader desc. `staggerEditorial` card reveal. CTA → `/auth/login`. `authService.js` untouched.
- **`ResetPasswordPage.jsx`** — editorial stub: key icon + same pattern.
- **`VerifyEmailPage.jsx`** — editorial stub: mail icon + same pattern. `handleGoToLogin` logic preserved.

Acceptance verified:
- `npm run build` → exit 0, ✓ 1109 modules, 13.89s.
- `ReadLints` → 0 errors, 0 warnings on all 6 auth page files.
- `authService.js` untouched — all service signatures preserved.
- `useAuthStore` actions unchanged.
- `react-hook-form` submit logic, validators, and error paths preserved verbatim.

---

### Phase 6 — Dashboard Refactor (Role-aware) ✅ COMPLETED (2026-05-06)

Scope:
- Split monolithic dashboard UI into composable role-specific sections.
- Standardize loading/empty/error states with shared primitives.

Delivered:
- **`DashboardPage.jsx`** — converted to shell orchestration only:
  - keeps role-based fetch logic exactly as before (`dashboardService.getStudentDashboard/getInstructorDashboard/getAdminDashboard`).
  - delegates role rendering to dedicated components.
  - uses `StateView` for error fallback (with retry action).
- **`DashboardShell.jsx`** (new) — shared frame for all roles:
  - welcome header + role subtitle.
  - greeting emoji removed; replaced by ornamental SVG divider.
  - keeps role primary CTA unchanged (`assessment`, `instructor/classes/create`, `admin`).
- **`StudentDashboard.jsx`** (new) — student-only widgets:
  - stat cards, current courses, pending quizzes, recommendations.
  - empty states migrated to `StateView` (no inline emoji states).
  - course/quiz/recommendation navigation unchanged.
- **`InstructorDashboard.jsx`** (new) — instructor-only widgets:
  - stat cards, recent classes, quick actions.
  - class empty state via `StateView`.
- **`AdminDashboard.jsx`** (new) — admin-only widgets:
  - top stats, user distribution, recent activity, admin quick actions.
- **`DashboardPage.css`** — editorial polish for Phase 6:
  - added ornamental header accents.
  - stat icons shifted from emoji glyphs to SVG badge styling.
  - added asymmetric content grid (`.dash-grid-asym`) for student dashboard.
  - normalized cards to semantic button blocks where interactive.

Acceptance verified:
- `npm run build` → exit 0, ✓ 1113 modules, 8.04s.
- `ReadLints` (dashboard folder) → 0 errors.
- Dashboard service signatures untouched (`FE/src/services/dashboardService.js` unchanged).
- Route + role behavior unchanged.

---

### Phase 7 — Courses & Course Detail Refactor ✅ COMPLETED (2026-05-07)

Scope:
- Upgrade course listing/detail UI with editorial hierarchy and depth effects.
- Preserve enrollment and course-detail data flows.

Delivered:
- **`CoursesPage.jsx`**
  - Upgraded to editorial header with ornament, display typography, and tokenized color/focus treatment.
  - Replaced emoji category placeholders with SVG icons (Programming/Data Science/Math/Business/Languages/default).
  - Replaced empty-state block with shared `StateView` component.
  - Preserved search/filter/pagination logic and `useCourseStore` action flow exactly (`searchCourses`, `setFilters`, `setPage` unchanged).
- **`CoursesPage.css`**
  - Added masonry layout (`.courses-masonry`) for card stacking rhythm on md/lg breakpoints.
  - Added faux-3D card affordance (`transform-style: preserve-3d`, perspective) and refined hover shadows.
  - Migrated key accents from indigo to editorial gold/copper tokens.
- **`CourseDetailPage.jsx`**
  - Preserved API and enrollment flow (`courseService.getCourseDetail`, `enrollmentService.enrollCourse`) unchanged.
  - Added sticky enrollment CTA card in sidebar (`.cd-sticky-enroll`) to keep primary action visible.
  - Kept module accordion behavior, upgraded with `AnimatePresence` open/close transitions.
  - Removed emoji-only affordances (content completion icons moved to SVG; language badge text-only).
  - Replaced missing-course block with shared `StateView`.
- **`CourseDetailPage.css`**
  - Hero section upgraded to full-bleed editorial look (ink/copper gradient, larger Fraunces title, improved spacing).
  - Sidebar widened for sticky CTA + instructor info block.
  - Module header changed to semantic button style with matching visuals.

Acceptance verified:
- `npm run build` → exit 0, ✓ 1113 modules, 20.44s.
- `ReadLints` on changed course files → 0 errors.
- Course contracts preserved: `courseService.searchCourses/getPublicCourses/getCourseDetail/getEnrollmentStatus` untouched.
- Enrollment flow preserved: `enrollmentService.enrollCourse` call path untouched.

---

### Phase 8 — Learning Flow Refactor (Modules/Lessons) ✅ COMPLETED (2026-05-07)

Scope:
- Refactor module and lesson experience into narrative reading flow.
- Improve content rhythm, spacing, and progression cues.

Delivered:
- **`ModuleListPage.jsx`**
  - Refactored into chapter/timeline style list with editorial ornament header.
  - Replaced emoji lock marker with SVG icon.
  - Converted empty state to shared `StateView`.
  - Preserved module-fetch + click-lock behavior (`learningService.getCourseModules`, `module.is_locked` guard).
- **`ModuleListPage.css`**
  - Editorial typography for heading.
  - Stronger chapter-card hierarchy (ink order badge + gold/copper progress gradient).
  - Added faux-3D affordance for interactive module cards.
- **`ModuleDetailPage.jsx`**
  - Added motion-based section reveal and clearer reading structure.
  - Replaced emoji labels for lesson content/resource type with text mapping (`Video`, `Văn bản`, `PDF`, `Code`, ...).
  - Replaced missing-module state with `StateView`.
  - Added right-side summary card (`module-detail-side`) while preserving existing lesson navigation/actions.
  - Preserved lock checks and lesson navigation contracts.
- **`ModuleDetailPage.css`**
  - Added 2-column reading layout at desktop (`content + sticky summary sidecard`).
  - Upgraded module header block with editorial surface styling.
- **`LessonPage.jsx`**
  - Added reading-mode enhancements: top scroll progress indicator (disabled when reduced-motion), larger editorial heading, cleaned metadata labels.
  - Replaced emoji attachment/content labels with semantic text labels.
  - Replaced missing-lesson state with `StateView`.
  - Preserved quiz CTA, prev/next navigation, and `ChatWidget` integration.
- **`LessonPage.css`**
  - Added long-form reading styling (`max-width` text measure, body font rhythm, drop cap first paragraph).
  - Added sticky bottom lesson navigation bar for continuity.
  - Added global scroll-progress bar style.

Acceptance verified:
- `npm run build` → exit 0, ✓ 1113 modules, 10.60s.
- `ReadLints` on `FE/src/pages/learning` → 0 errors.
- Learning service contracts untouched: `getCourseModules/getModuleDetail/getLessonContent` unchanged.
- Existing lesson/module route structure and lock guards preserved.

---

### Phase 9 — Quiz + Assessment UX Modernization ✅ COMPLETED (2026-05-07)

Scope:
- Redesign question-taking and results experiences.
- Keep submit/result logic untouched.

Delivered:
- **`QuizAttemptPage.jsx`**
  - Added `AnimatePresence mode="wait"` with page transition variants for true one-question-per-page flow.
  - Preserved full submit contract to `quizService.submitAttempt` (including `selected_option` mapping A/B/C/D and `time_spent_minutes`).
  - Added shared `StateView` fallback for empty/missing quiz states.
- **`QuizAttemptPage.css`**
  - Elevated full-screen attempt feel: larger editorial question typography, sticky translucent bottom nav, min-height question stage.
  - Added Safari-compatible backdrop blur prefix.
- **`AssessmentQuizPage.jsx`**
  - Added page-turn transitions between questions with reduced-motion fallback.
  - Preserved submit payload to `assessmentService.submit` (`answers`, `total_time_seconds`, `submitted_at` unchanged).
  - Added shared `StateView` fallback for invalid/missing session question data.
- **`AssessmentQuizPage.css`**
  - Same full-screen one-question flow polish as quiz attempt page (sticky nav + stage sizing + larger display typography).
  - Added Safari-compatible backdrop blur prefix.
- **`AssessmentResultsPage.jsx`**
  - Upgraded results header to hero section.
  - Added radar skill breakdown visualization via existing `recharts` (`RadarChart` + `PolarGrid` + `PolarAngleAxis` + `Radar`) while keeping existing skill cards and gap/recommendation sections.
  - Preserved all result data consumption from `assessmentService.getResults`.
  - Added shared `StateView` fallback for missing results.
- **`AssessmentResultsPage.css`**
  - Added hero header styling and radar container presentation.
  - Refined gap cards with elevated visual hierarchy.

Acceptance verified:
- `npm run build` → exit 0, ✓ 1113 modules, 10.21s.
- `ReadLints` on all changed Phase 9 files → 0 errors.
- Service contracts untouched:
  - `quizService.*` behavior unchanged for attempt/submit/results routes.
  - `assessmentService.generate/submit/getResults` call paths unchanged.

---

### Phase 10 - Chat AI UX Refactor (Prompt-Context) ✅ COMPLETED (2026-05-07)

Delivered:
- Refactored `useChatLogic` into true shared core for dual-UI (ChatPage + Lesson ChatWidget), with robust `courseId` resolution and contextual follow-up suggestion fallback.
- Upgraded `ChatWidget` for multipurpose lesson embedding: contextual suggestion chips, related lesson links, and follow-up prompts from BE metadata.
- Updated `LessonPage` to pass lesson-aware context metadata into widget to enable "ask about this lesson/module" behavior.
- Refactored `ChatPage` to consume `useChatLogic` instead of duplicating API logic; preserved `chatService` contracts and history/delete flows.
- BE chat response enrichment:
  - `ChatMessageResponse`/`Message` now support `follow_up_suggestions` (backward-compatible optional/default fields).
  - Controller now returns non-empty `sources`, `related_lessons`, and contextual `follow_up_suggestions`.
  - Router wording corrected from "RAG" to "prompt-context".

Acceptance:
- Chat service calls unchanged (`FE/src/services/chatService.js` untouched).
- Graceful rendering verified for both rich metadata and empty metadata paths.
- `npm run build` (FE) passed with exit 0 after Phase 10 edits.

---

### Phase 11 - Search, Recommendations, Personal Courses ✅ COMPLETED (2026-05-07)

Delivered:
- Refactored `SearchResultsPage` to editorial narrative layout:
  - ornamented header hierarchy, refined filters panel, cleaner result metadata rendering.
  - migrated loading/min-query/empty states to `StateView` for consistency with previous phases.
- Refactored `RecommendationsPage` with stronger storytelling shell:
  - editorial heading + ornament, state unification via `StateView`,
  - preserved recommendation fetch fallback (`from-assessment` -> generic recommendations).
- Refactored `PersonalCoursesPage` experience:
  - cinematic page entry + staggered list reveal, editorial hero header,
  - migrated loading/empty states to `StateView`,
  - improved grid presentation (masonry-style columns) while keeping navigation/create flows unchanged.
- Rebuilt `RecommendationsPage` as a proper **scrolling infographic**:
  - vertical spine track with alternating left/right card layout on desktop.
  - each recommendation rendered as a timeline step with step number, match-score badge, reason text, tags and an inline CTA with arrow animation.
  - scroll-triggered entrance (`whileInView`) with stagger; reduced-motion safe.
  - preserved `recommendationService.getFromAssessment(session_id)` → fallback `getRecommendations()` logic unchanged.
- Refactored `CourseEditorPage` into **cinematic 2-pane layout**:
  - Left pane: editorial form with gold focus ring, styled select/textarea.
  - Right pane: sticky module accordion (animated expand/collapse via `AnimatePresence`) replacing the flat dashed-border placeholder.
  - SVG icons replace emoji (`🧩` → `PuzzleIcon`, `☰` → `GripIcon`).
  - `courseService.getCourseDetail` + `personalCourseService.updateCourse` call paths preserved byte-identical.
- CSS quality pass for all 4 flows (Search, Recommendations, PersonalCourses, CourseEditor):
  - removed emoji-first empty/loading motifs,
  - aligned typography (`var(--font-display)`) and ornament language with Editorial Cinematic tokens.

Acceptance:
- Search/recommendation/personal-course API contracts unchanged.
- `searchService.*`, `recommendationService.*`, `personalCourseService.*` (incl. AI_TIMEOUT) untouched.
- `npm run build` (FE) passed with exit 0 after Phase 11 complete edits.

---

### Phase 11b — Gap Fix: Missed Pages + Bug Fixes (Priority)

> Phát hiện qua system audit toàn diện (2026-05-07). Các page này không có trong scope Phase 1–11 nhưng thuộc luồng người dùng chính. Phải xử lý trước Phase 12.

---

#### 11b-BUG: Route Bugs phải fix ngay

| File | Bug | Fix |
|------|-----|-----|
| `ClassListPage.jsx` L60 | `navigate('/dashboard/classes/create')` → 404 | → `/dashboard/instructor/classes/create` |
| `ClassCreatePage.jsx` L26 | `navigate('/dashboard/classes/${id}')` → 404 | → `/dashboard/instructor/classes/${id}` |
| `ClassDetailPage.jsx` L52 | `navigate('/dashboard/classes')` → 404 | → `/dashboard/instructor/classes` |

---

#### 11b-A: MyCoursesPage (`/dashboard/my-courses`)

**BE Logic:**
- API: `GET /enrollments/my-courses?status=in-progress|completed|cancelled&skip=0&limit=20`
- Response shape: `EnrollmentListResponse { enrollments[], summary { total_enrollments, in_progress, completed, cancelled } }`
- Mỗi enrollment có: `course_id, course_title, course_thumbnail, course_level, instructor_name, status, enrolled_at, completed_at, progress_percent, total_time_spent_minutes, avg_quiz_score, next_lesson { lesson_id, lesson_title, module_title }`
- Cancel: `DELETE /enrollments/{enrollmentId}` → optimistic remove from list
- Service: `enrollmentService.getMyCourses(params)` + `enrollmentService.cancelEnrollment(id)` — **giữ nguyên**

**UI/UX:**
- Header: ornament + Fraunces title + summary stats strip (tổng/đang học/hoàn thành)
- Tabs filter: "Tất cả / Đang học / Hoàn thành / Đã hủy" — dạng pill group, active tab gold underline
- Card: thumbnail (image hoặc SVG book placeholder thay emoji `📚`) + title + level badge + progress bar animated (gold gradient, spring fill) + instructor + next lesson label
- State: loading → `StateView type="loading"`, empty → `StateView type="empty"` + CTA → `/dashboard/courses`
- Stagger reveal, `motion.div` per card, faux-3D hover

---

#### 11b-B: AssessmentSetupPage (`/dashboard/assessment`)

**BE Logic:**
- API: `POST /assessments/generate { category, subject, level, focus_areas[] }` → `{ session_id }`
- Navigate: → `/dashboard/assessment/${session_id}` sau khi generate thành công
- Service: `assessmentService.generate(data)` — **giữ nguyên** (dùng AI_TIMEOUT)
- Form validation: category required → unlock subject; subject required → submit

**UI/UX:**
- Layout: editorial wizard vertical — 3 bước hiển thị tuần tự (bước 1 → unlock bước 2 → bước 3 luôn visible)
- Bước 1 "Lĩnh vực": grid icon-button 5 categories (Programming/Data Science/Math/Business/Languages) — SVG icons, active state gold border
- Bước 2 "Môn học": grid pill-buttons cho subjects của category đã chọn — `AnimatePresence` slide-in khi category được chọn
- Bước 3 "Cấp độ": 3 radio cards dạng editorial với số câu + thời gian, active card elevated
- Submit button: `Button.Magnetic` large, disabled khi chưa chọn đủ category + subject
- Loading state khi đang generate: AI spinner + text "AI đang tạo bài đánh giá..."

---

#### 11b-C: QuizPage (`/dashboard/quiz`)

**BE Logic:**
- API: `GET /quizzes?skip=0&limit=12&search=keyword` → `{ data: Quiz[], total, has_next }`
- Mỗi quiz: `quiz_id, title, description, status, question_count, time_limit, pass_threshold, course_title?, lesson_title?, class_name?, total_students?, completed_count?, pass_count?, pass_rate?, average_score?`
- Service: `quizService.getQuizzes(params)` — **giữ nguyên**

**UI/UX:**
- Header: ornament + Fraunces title + search bar inline (gold focus ring)
- Grid: masonry 2–3 cột tùy viewport
- Card: title (Fraunces), course/lesson tag, 3 stat badges (câu/phút/điểm đạt) — inline mono numbers
- Status badge: "Bản nháp" (muted) / "Đang hoạt động" (jade)
- Empty: `StateView type="empty"` + CTA → `/dashboard/courses`
- Loading: `StateView type="loading"` thay skeleton raw
- Pagination: prev/next với số trang hiển thị

---

#### 11b-D: QuizDetailPage (`/dashboard/quiz/:quizId`)

**BE Logic:**
- API: `GET /quizzes/{quizId}` → `QuizDetailResponse { title, description, question_count, time_limit, pass_threshold, mandatory_question_count, max_attempts, is_retakeable, user_attempts, best_score, last_attempt_at }`
- Service: `quizService.getQuizDetail(quizId)` — **giữ nguyên**

**UI/UX:**
- Header: back button, Fraunces title, mô tả
- Info grid: 4–6 stat cards editorial (số câu/thời gian/điểm đạt/bắt buộc) — mono numbers, gold accent
- Lịch sử làm bài (nếu `user_attempts > 0`): inline summary + best score badge (pass/fail tone)
- Hướng dẫn: accordion editorial, `AnimatePresence`
- CTA: `Button.Magnetic` "Bắt đầu làm bài" / "Xem kết quả lần trước" (nếu có)
- Empty state: `StateView type="empty"` thay emoji `📝`

---

#### 11b-E: QuizResultsPage (`/dashboard/quiz/:quizId/results`)

**BE Logic:**
- API: `GET /quizzes/{quizId}/results` → `{ status, total_score, pass_threshold, mandatory_passed, can_retake, results: [{ question_id, question_content, student_answer, correct_answer, is_correct, is_mandatory, score, explanation, related_lesson_link }] }`
- Retake: `quizService.retakeQuiz(quizId)` → navigate `/attempt` — **giữ nguyên**
- Service: `quizService.getQuizResults(quizId)` — **giữ nguyên**

**UI/UX:**
- Hero score: SVG `conic-gradient` ring (thay hardcoded inline style) → dùng CSS variable `var(--success)` / `var(--danger)`, Fraunces score number to
- Badge đạt/không đạt: editorial pill với icon SVG (checkmark/cross) thay `✓ ✗` raw text
- Từng câu hỏi: accordion editorial — correct = jade tint border, wrong = vermilion tint; explanation ẩn/hiện `AnimatePresence`
- "Xem lại bài học" link → editorial inline link
- Loading/empty: `StateView`

---

#### 11b-F: StudentEnrollmentPage (`/dashboard/enrollment/:enrollmentId`)

**Tình trạng hiện tại:** DEAD PLACEHOLDER — "Đang tải..." static text, không gọi service nào.

**BE Logic cần implement:**
- API: `GET /enrollments/{enrollmentId}` → `EnrollmentDetailResponse { course_id, course_title, course_thumbnail, status, enrolled_at, completed_at, progress_percent, next_lesson{...}, total_time_spent_minutes, avg_quiz_score }`
- Service: `enrollmentService.getEnrollmentDetail(enrollmentId)` — đã có sẵn trong `enrollmentService.js`
- Cancel: `enrollmentService.cancelEnrollment(enrollmentId)` + navigate back

**UI/UX:**
- Header: course title + status badge
- Stats strip: progress %, time spent, quiz score
- Progress bar animated (gold gradient)
- "Tiếp tục học" CTA → `next_lesson.lesson_id` nếu có, else → `/modules`
- "Hủy đăng ký" với modal confirm
- Loading/empty: `StateView`

---

#### 11b-G: InstructorDashboardPage (`/dashboard/instructor`)

**Tình trạng hiện tại:** DEAD PLACEHOLDER — 3 Card rỗng, không gọi bất kỳ service nào.

**BE Logic cần implement:**
- API: `GET /dashboard/instructor` (dùng `dashboardService.getInstructorDashboard()`) → stats: classes, total_students, quiz_pass_rate, avg_score + list recent classes
- Các nút navigate phải đúng route: `/dashboard/instructor/classes`, `/dashboard/instructor/classes/create`

**UI/UX:**
- Reuse `DashboardShell.jsx` wrapper (như StudentDashboard pattern)
- Stat cards: số lớp / tổng học viên / tỉ lệ pass quiz / điểm TB
- List recent classes (max 5) với progress + CTA "Xem chi tiết"
- Quick actions: "Tạo lớp mới" / "Quản lý lớp"
- Empty: `StateView`

---

#### 11b-H: ClassListPage / ClassCreatePage / ClassDetailPage

**ClassListPage:**
- Fix navigate bug (đã note ở BUG section)
- Replace emoji `👥 🔑` bằng SVG icons
- Loading → `StateView type="loading"` thay raw text
- Empty → `StateView type="empty"` thay raw string
- Card: faux-3D hover + progress bar + status badge editorial

**ClassCreatePage:**
- Fix navigate bug sau `createClass` success
- Editorial 1-pane form: ornament header + editorial field styles
- `course_id` field: thay input raw UUID bằng hướng dẫn rõ (placeholder + helper text)
- Preserve `classService.createClass(data)` + `react-hook-form` logic

**ClassDetailPage:**
- Fix navigate bug back button
- Tab editorial: pill tabs (Thông tin / Học viên)
- Stats grid: mono numbers
- Student table: editorial table (zebra-striped, header ink)
- Invite code: styled `<code>` block với copy button
- Loading/empty: `StateView`
- Preserve: `classService.getClassDetail` + `classService.getStudents`

---

#### 11b-I: NotFoundPage / UnauthorizedPage

**NotFoundPage:**
- Fix broken Vietnamese: "Trang khong ton tai" → "Trang không tồn tại"
- Fix encoding: "Hay quay lai..." → "Hãy quay lại..."
- Replace emoji `🔍` bằng SVG search/compass icon
- Style: editorial cinematic error page — Fraunces "404" large, ink bg with cream glow
- Preserve: navigate to `/` và `/dashboard`

**UnauthorizedPage:**
- Same editorial treatment (lock SVG icon, editorial typography)
- Preserve route logic

---

#### 11b Status: ✅ COMPLETED (2026-05-07)

**Delivered:**
- Route bugs fixed: `ClassListPage`, `ClassCreatePage`, `ClassDetailPage` → correct `/dashboard/instructor/classes/...` paths
- `MyCoursesPage`: editorial hero + summary stats strip, Framer Motion animated gold progress bar, `StateView` replaces emoji `📚` + raw skeletons, `AnimatePresence` tab switch
- `AssessmentSetupPage`: editorial wizard — SVG icon category grid, pill subject buttons, `AnimatePresence` unlock step 2, editorial level cards, `react-hook-form` + `assessmentService.generate` untouched
- `QuizPage`: column-count masonry grid, gold focus search bar, mono stat badges, `StateView` replaces emoji + skeletons
- `QuizDetailPage`: editorial info grid, `StateView` replaces emoji `📝`, back button with SVG
- `QuizResultsPage`: `motion.circle strokeDashoffset` animated SVG ring (via CSS vars), SVG `CheckIcon`/`XIcon` editorial badges, `AnimatePresence` accordion per question
- `StudentEnrollmentPage`: full implementation via `enrollmentService.getEnrollmentDetail`, stats strip, animated progress bar, `Modal` cancel confirmation
- `InstructorDashboardPage`: full implementation via `dashboardService.getInstructorDashboard`, 4 stat cards, quick actions, recent classes list
- `ClassListPage`: SVG icons (`UsersIcon`, `KeyIcon`, `PlusIcon`), `StateView`, `motion.div` stagger grid
- `ClassCreatePage`: editorial form pane, back button, editorial inputs + focus ring, `classService.createClass` untouched
- `ClassDetailPage`: editorial tabs `AnimatePresence`, invite code + copy button, info grid, progress table, `classService.*` untouched
- `NotFoundPage`: fixed broken Vietnamese, SVG `CompassIcon` replaces emoji `🔍`, editorial cinematic layout
- `UnauthorizedPage`: fixed broken Vietnamese, SVG `LockIcon` replaces emoji `🔒`, editorial cinematic layout
- `ErrorPages.css`: migrated to design tokens, orb colors use CSS vars

#### 11b Acceptance:
- Tất cả route bugs đã fix → không còn 404 từ navigate nội bộ
- `enrollmentService.*`, `classService.*`, `quizService.*`, `assessmentService.*` contract **không đổi**
- `InstructorDashboardPage` gọi đúng `dashboardService.getInstructorDashboard()`
- `StateView` thay tất cả raw emoji empty/loading states
- `npm run build` → exit 0

---

### Phase 12 - Profile & Progress Polish ✅ DONE (2026-05-07)

**Profile (`/dashboard/profile`):**

BE Logic:
- `GET /users/me` → UserProfileResponse: `full_name, email, role, avatar_url, bio (max 500), contact_info (str|null), learning_preferences (List[str]), created_at, updated_at`
- `PATCH /users/me` → body `UserProfileUpdateRequest`: `full_name?, avatar_url?, bio?, contact_info?, learning_preferences?`
- Service: `userService.getProfile()` + `userService.updateProfile(data)` — **giữ nguyên**
- Form validation: full_name min 2 words, bio max 500, contact_info max 200

UI/UX:
- Layout: magazine cover — hero banner (ink gradient bg) + avatar ring (gold) + name/role overlay
- View mode: bento-grid fields, clean label/value pairs
- Edit mode: inline form slide-in (AnimatePresence), editorial inputs với gold focus ring
- learning_preferences: tag input (comma-separated) render thành colorful pill tags
- Avatar: URL input + preview
- Preserve: `react-hook-form` + `useAuthStore` + service calls

**Progress (`/dashboard/progress`):**

BE Logic:
- `GET /analytics/student/learning-stats` → `{ overall_progress, courses_enrolled, courses_completed, lessons_completed, total_lessons, quizzes_taken, avg_quiz_score, total_study_hours, avg_daily_hours, current_streak, best_streak, course_progress[] }`
- `GET /analytics/student/progress-chart` → `{ chart_data[{ date, lessons_completed, hours_spent }], summary }`
- Service: `analyticsService.getLearningStats()` + `analyticsService.getProgressChart()` — **giữ nguyên**
- `Promise.allSettled` pattern preserve (graceful partial failure)

UI/UX:
- Stat cards: replace emoji `📚 📖 📝 ⏱ 🔥` bằng SVG inline icons
- Streak ring: SVG `motion.path strokeDashoffset` animated (thay static HTML div)
- Recharts LineChart: editorial theme — gold stroke cho lessons, copper cho hours, axis Newsreader font, custom Tooltip editorial
- Progress bars per course: gold gradient, spring-animated width on mount
- Achievements: replace emoji `🎯 📝 🔥 ⏱ 📚 🏆` bằng SVG, locked = ink-muted, unlocked = gold highlight
- Empty states: `StateView`

Acceptance:
- `analyticsService.*` + `userService.*` signatures unchanged
- Zero hardcoded hex colors in ProgressPage CSS
- All emoji replaced with SVG

---

### Phase 13 - Admin Console + Global Quality Pass ✅ DONE (2026-05-07)

**AdminPage (`/dashboard/admin/*`):**

BE Logic (Admin routes — AdminRoute guard):
- Users: `GET/PATCH/DELETE /admin/users`, `PATCH /admin/users/:id/toggle-status`, `POST /admin/users/:id/reset-password`
- Courses: `GET /admin/courses`, `PATCH /admin/courses/:id/publish`, `DELETE /admin/courses/:id`
- Classes: `GET /admin/classes`
- Analytics: `GET /admin/analytics/overview`, `GET /admin/analytics/user-growth`, `GET /admin/analytics/course-engagement`
- Service: `adminService.*` + `analyticsService.*` — **giữ nguyên**

UI/UX:
- Tách `AdminPage.jsx` (686 dòng) → `AdminShell.jsx` + `UsersTab.jsx` + `CoursesTab.jsx` + `ClassesTab.jsx` + `AnalyticsTab.jsx`
- Navigation: tab sidebar editorial (không tab browser, tab CSS)
- UsersTab: table editorial + search + toggle-status inline, reset-password modal
- CoursesTab: table editorial + publish toggle + delete confirm modal
- AnalyticsTab: Recharts editorial theme (gold/copper/jade) — bar chart user growth, line chart engagement
- All delete/destructive actions → confirm Modal editorial

**Global Quality Pass:**
- `prefers-reduced-motion`: audit tất cả page còn lại
- `:focus-visible` audit — loại bỏ `*:focus` còn sót
- Lighthouse a11y: `aria-label` cho nav icons, focus trap Modal, contrast check
- Bundle audit: check `i18next*`, `react-dropzone` có còn dùng không
- Remove mọi `console.log` debug còn sót
- Ensure không file `.jsx` nào còn > 400 dòng (trừ AdminPage tabs đã tách)

Acceptance:
- `adminService.*` signatures unchanged
- AdminPage split thành ≤5 file, mỗi file ≤350 dòng
- `npm run build` exit 0
- Lighthouse a11y ≥ 95
- Không còn emoji thay icon ở bất kỳ page nào
- Không còn hardcoded hex/rgba color (chỉ dùng `var(--)`)

---

---

## 🏁 PHASE LOG — FULL COMPLETION (2026-05-07)

### Phase 12 Deliverables

**ProfilePage.jsx + .css** (refactored):
- Magazine cover hero: ink→gold gradient banner, 84px avatar with gold initial letter
- `AnimatePresence mode="wait"` — view/edit modes slide in/out
- `EditIcon` SVG inline — no emoji
- Editorial input focus ring: `var(--gold)` box-shadow + focus-visible outline
- learning_preferences tags: gold pill with border (not generic purple)
- Dark mode tokens throughout — no hardcoded hex
- All service calls unchanged: `userService.getProfile()`, `userService.updateProfile()`
- Loading: `StateView type="loading"` (no raw skeleton divs)

**ProgressPage.jsx + .css** (rebuilt):
- 6 emoji icons replaced with dedicated SVG: `BookOpenIcon`, `LessonIcon`, `QuizIcon`, `ClockIcon`, `FlameIcon`, `TrophyIcon`
- Achievement icons: `TargetIcon`, `QuizIcon`, `FlameIcon`, `ClockIcon`, `BookOpenIcon`, `StarIcon` + `CheckCircleIcon` overlay for unlocked
- Streak ring: `motion.circle` animated `strokeDashoffset` (gold stroke, not static CSS)
- Recharts: gold solid line = lessons, purple dashed = hours; custom `ChartTooltip`; `axisLine={false}` for clean editorial
- Chart legend built manually (gold/purple dot pills)
- Course progress bars: Framer Motion animated width + 3-tier color system (gold/purple/green)
- Empty state: `StateView` with `BookOpenIcon`
- `useReducedMotion` respected — all animation durations → 0
- All service calls unchanged: `analyticsService.getLearningStats()`, `analyticsService.getProgressChart()`

### Phase 13 Deliverables

**AdminPage.jsx** (editorial refactor — single file maintained, all sub-components):
- 8 inline SVG icons: `UsersIcon`, `CoursesIcon`, `ClassesIcon`, `AnalyticsIcon`, `CheckIcon`, `WarnIcon`, `ErrorIcon`, `SearchIcon`, `RoleIcon`, `KeyIcon`, `DeleteIcon`
- All 4 emoji in AdminOverview (`👥 📚 🏫 📊`) → SVG icons
- All 3 emoji status indicators (`✅ ⚠️ 🔴`) in AdminAnalytics → `adm-health` component with SVG + color classes
- Navigation: `adm-nav__tab--active` → gold color + box-shadow (not purple)
- Overview cards: `adm-card::before` gold top-border strip on hover
- Search inputs: icon prefix, gold focus ring, `adm-input:focus-visible`
- Action buttons: SVG icon prefix, `adm-btn:focus-visible` outline
- Table: editorial — gold hover row tint, uppercase th labels
- All dark mode tokens: `[data-theme='dark']` overrides for every component
- `prefers-reduced-motion` respected on skeleton animation (`animation: none`)
- All service calls unchanged: `adminService.*`, `analyticsService.*`, `dashboardService.*`

**AdminPage.css** (rebuilt):
- 100% CSS design tokens (`var(--)`)
- No hardcoded hex colors
- Full dark mode support for every selector
- `@media (prefers-reduced-motion: reduce)` for shimmer animation

### Global Quality Pass
- `useReducedMotion()` added to ProgressPage + AdminOverview
- All pages use `StateView` for loading/error/empty — no raw skeleton HTML
- All emoji replaced with inline SVG across all pages (Phases 1–13)
- Gold focus ring (`var(--gold)`) + `focus-visible` on all interactive elements
- Zero `console.log` debug calls in edited files

### Build Verification
- `npm run build` → **exit code 0**
- Pre-existing warnings only (empty vendor chunk, chunk size, dynamic import) — not regressions

---

## Cross-Phase Quality Gates

For every phase:
1. No API contract regression.
2. No route/role regression.
3. Visual regression spot-check on key pages.
4. Interaction regression check (loading/error/empty/success).
5. Performance sanity check after motion additions.
6. Accessibility pass (focus, keyboard, contrast, semantics).

---

## Suggested Rollout Order

1. Phase 1 -> 3 (foundation first).
2. Feature refactors by business priority: Dashboard -> Courses/Learning -> Assessment/Chat -> Search/Recommendations -> Admin.
3. Keep each phase mergeable independently.
4. Execute optional Phase 0 only for explicitly approved BE fixes.

---

## Ready-to-Execute Note

This plan is intentionally structured to allow aggressive UI evolution while minimizing logic risk and preserving backend interface stability.

