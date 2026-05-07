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
| Phase 7 → 13 | ⏳ QUEUED | — |

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

### Phase 4 — Landing Page Scrollytelling Transformation ✅ COMPLETED (2026-05-06)

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

### Phase 7 - Courses & Course Detail Refactor

Scope:
- Upgrade course listing/detail UI with editorial hierarchy and depth effects.
- Preserve enrollment and course-detail data flows.

Acceptance:
- No contract changes for course services.
- Improved scanability and conversion UX.

---

### Phase 8 - Learning Flow Refactor (Modules/Lessons)

Scope:
- Refactor module and lesson experience into narrative reading flow.
- Improve content rhythm, spacing, and progression cues.

Acceptance:
- Learning endpoints and progress hooks remain unchanged.
- Higher content comprehension UX.

---

### Phase 9 - Quiz + Assessment UX Modernization

Scope:
- Redesign question-taking and results experiences.
- Keep submit/result logic untouched.

Acceptance:
- Quiz/assessment services operate exactly as before.
- Better cognitive load handling in interactive sessions.

---

### Phase 10 - Chat AI UX Refactor (Prompt-Context)

Scope:
- Decompose chat page into modular UI building blocks.
- Improve conversation readability, composer ergonomics, and state feedback.
- Keep current hook/service behavior and payload contracts.

Acceptance:
- Chat service calls unchanged.
- Graceful rendering whether BE provides rich context metadata or empty arrays.

---

### Phase 11 - Search, Recommendations, Personal Courses

Scope:
- Refactor discovery/recommendation/editor experiences into cohesive narrative UX.
- Improve filter/result hierarchy and recommendation storytelling.

Acceptance:
- Search/recommendation/personal-course API contracts unchanged.

---

### Phase 12 - Profile & Progress Polish

Scope:
- Refine profile editing and progress storytelling.
- Harmonize chart visual language with design system.

Acceptance:
- Existing progress/analytics integrations unchanged.
- Better interpretation of learning outcomes.

---

### Phase 13 - Admin Console & Global Quality Pass

Scope:
- Modularize admin console UI for long-term maintainability.
- Final accessibility, motion reduction, and performance quality sweep.
- Remove/confirm unused frontend dependencies and visual debt.

Acceptance:
- Admin workflows remain intact.
- Production-ready consistency and accessibility baseline achieved.

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

