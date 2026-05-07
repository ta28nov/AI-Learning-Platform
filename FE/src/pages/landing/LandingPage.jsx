import { useRef, useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import {
  motion,
  useScroll,
  useTransform,
  useReducedMotion,
  useSpring,
  useMotionValue,
  useInView,
} from 'framer-motion'
import Button from '@components/ui/Button'
import { staggerEditorial, fadeUp, fadeDown, inView, EASE } from '@/styles/motion'
import './LandingPage.css'

/* =============================================================================
   LANDING PAGE — Editorial Cinematic, COMPUTE-inspired layout
   Chapters:
     1. Hero
     2. Capabilities (numbered cards)
     3. Process — Define / Deploy / Scale → Đánh giá / Lộ trình / Học
     4. Catalog reach (regions-style grid: subject categories)
     5. Live metrics (animated counters)
     6. Subjects/Integrations grid
     7. Privacy & data safety
     8. For instructors (developer SDK analog)
     9. Testimonials
    10. Plans (pricing-style 3-tier)
    11. Final CTA
   CTA routes preserved: /auth/register, /auth/login
   ============================================================================= */

const LandingPage = () => {
  const [scrolled, setScrolled] = useState(false)
  const shouldReduceMotion = useReducedMotion()

  // Page-wide scroll progress (drives top progress bar)
  const { scrollYProgress } = useScroll()
  const scaleX = useSpring(scrollYProgress, { stiffness: 120, damping: 30, mass: 0.6 })

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 60)
    window.addEventListener('scroll', handleScroll, { passive: true })
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  return (
    <div className="landing">
      {!shouldReduceMotion && (
        <motion.div className="landing-progress" style={{ scaleX }} aria-hidden="true" />
      )}

      <LandingHeader scrolled={scrolled} />

      <HeroSection shouldReduceMotion={shouldReduceMotion} />
      <CapabilitiesSection shouldReduceMotion={shouldReduceMotion} />
      <ProcessSection shouldReduceMotion={shouldReduceMotion} />
      <ReachSection shouldReduceMotion={shouldReduceMotion} />
      <LiveMetricsSection shouldReduceMotion={shouldReduceMotion} />
      <SubjectsSection shouldReduceMotion={shouldReduceMotion} />
      <PrivacySection shouldReduceMotion={shouldReduceMotion} />
      <InstructorSection shouldReduceMotion={shouldReduceMotion} />
      <TestimonialSection shouldReduceMotion={shouldReduceMotion} />
      <PlansSection shouldReduceMotion={shouldReduceMotion} />
      <FinalCTASection shouldReduceMotion={shouldReduceMotion} />

      <LandingFooter />
    </div>
  )
}

/* =============================================================================
   HEADER
   ============================================================================= */
const LandingHeader = ({ scrolled }) => (
  <header className={`landing-header${scrolled ? ' landing-header--scrolled' : ''}`}>
    <div className="landing-container">
      <div className="landing-header__inner">
        <Link to="/" className="landing-logo" aria-label="AI Learning — Trang chủ">
          <span className="landing-logo__mark" aria-hidden="true">◆</span>
          <span className="landing-logo__text">AI Learning</span>
        </Link>

        <nav className="landing-nav" aria-label="Navigation chính">
          <a href="#capabilities" className="landing-nav__link">Bạn nhận được gì</a>
          <a href="#process" className="landing-nav__link">Cách bắt đầu</a>
          <a href="#subjects" className="landing-nav__link">Học gì</a>
          <a href="#plans" className="landing-nav__link">Gói</a>
          <Link to="/auth/login" className="landing-nav__link">Đăng nhập</Link>
          <Link to="/auth/register">
            <Button variant="primary" size="sm">Bắt đầu →</Button>
          </Link>
        </nav>
      </div>
    </div>
  </header>
)

/* =============================================================================
   1. HERO — Bold display + inline metrics (COMPUTE-style)
   ============================================================================= */
const HeroSection = ({ shouldReduceMotion }) => {
  const ref = useRef(null)
  const { scrollYProgress } = useScroll({ target: ref, offset: ['start start', 'end start'] })
  const y = useTransform(scrollYProgress, [0, 1], shouldReduceMotion ? [0, 0] : [0, -180])
  const scale = useTransform(scrollYProgress, [0, 1], shouldReduceMotion ? [1, 1] : [1, 0.92])
  const opacity = useTransform(scrollYProgress, [0, 0.6], shouldReduceMotion ? [1, 1] : [1, 0])
  const meshY = useTransform(scrollYProgress, [0, 1], shouldReduceMotion ? [0, 0] : [0, 80])

  const titleLine1 = ['Học', 'theo', 'cách', 'của', 'bạn,']
  const titleLine2Static = ['cùng', 'người', 'bạn']
  const titleLine2Em = 'tên là AI'

  return (
    <section className="hero" ref={ref} aria-labelledby="hero-heading">
      <div className="hero__bg" aria-hidden="true">
        <motion.div className="hero__mesh" style={{ y: meshY }} />
        <div className="hero__noise" />
      </div>

      <div className="landing-container">
        <motion.div
          className="hero__content"
          style={{ y, opacity, scale }}
          variants={staggerEditorial}
          initial={shouldReduceMotion ? false : 'hidden'}
          animate="show"
        >
          <motion.div className="hero__eyebrow" variants={fadeDown}>
            <span className="hero__eyebrow-line" aria-hidden="true" />
            <span>Nơi học tập trở nên dễ chịu hơn</span>
          </motion.div>

          <h1 id="hero-heading" className="hero__title">
            <span className="hero__title-line">
              {titleLine1.map((w, i) => (
                <SplitWord key={`l1-${i}`} delay={0.15 + i * 0.07} reduce={shouldReduceMotion}>
                  {w}
                </SplitWord>
              ))}
            </span>
            <span className="hero__title-line">
              {titleLine2Static.map((w, i) => (
                <SplitWord key={`l2-${i}`} delay={0.45 + i * 0.07} reduce={shouldReduceMotion}>
                  {w}
                </SplitWord>
              ))}
              <SplitWord delay={0.7} reduce={shouldReduceMotion}>
                <em className="hero__title-em">{titleLine2Em}</em>
              </SplitWord>
            </span>
          </h1>

          <motion.p className="hero__desc" variants={fadeUp}>
            Bạn không cần học theo khuôn mẫu. AI sẽ hiểu bạn đang ở đâu,
            chỉ cho bạn cần học gì tiếp theo, và luôn ở bên cạnh khi bạn
            có câu hỏi — kể cả lúc 2 giờ sáng.
          </motion.p>

          <motion.div className="hero__actions" variants={fadeUp}>
            <Link to="/auth/register">
              <Button.Magnetic size="lg">Học thử miễn phí →</Button.Magnetic>
            </Link>
            <Link to="/auth/login">
              <Button variant="ghost" size="lg" className="hero__ghost-cta">
                Mình đã có tài khoản
              </Button>
            </Link>
          </motion.div>

          <motion.div className="hero__metrics" variants={fadeUp}>
            {METRICS.map((m, i) => (
              <span key={m.label} className="hero__metric-group">
                {i > 0 && <span className="hero__metric-sep" aria-hidden="true" />}
                <span className="hero__metric">
                  <strong className="hero__metric-value">{m.value}</strong>
                  <span className="hero__metric-label">{m.label}</span>
                </span>
              </span>
            ))}
          </motion.div>
        </motion.div>
      </div>

      {!shouldReduceMotion && (
        <motion.div
          className="hero__scroll-hint"
          animate={{ y: [0, 8, 0] }}
          transition={{ duration: 1.8, repeat: Infinity, ease: 'easeInOut' }}
          aria-hidden="true"
        >
          <ScrollDownIcon />
        </motion.div>
      )}
    </section>
  )
}

const SplitWord = ({ children, delay = 0, reduce = false }) => (
  <span className="hero__title-word">
    <motion.span
      className="hero__title-word-inner"
      initial={reduce ? false : { y: '110%', opacity: 0 }}
      animate={{ y: '0%', opacity: 1 }}
      transition={{ duration: reduce ? 0 : 0.9, ease: EASE.cinematic, delay: reduce ? 0 : delay }}
    >
      {children}
    </motion.span>
  </span>
)

/* =============================================================================
   2. CAPABILITIES — numbered cards, COMPUTE "Intelligent workers" analog
   ============================================================================= */
const CapabilitiesSection = ({ shouldReduceMotion }) => (
  <section className="cap" id="capabilities" aria-labelledby="cap-heading">
    <div className="landing-container">
      <SectionLabel text="Bạn nhận được gì" />
      <motion.h2
        id="cap-heading"
        className="cap__title"
        variants={fadeUp}
        {...(shouldReduceMotion ? {} : inView())}
      >
        Học vui hơn, <em>nhớ lâu hơn</em>.
      </motion.h2>
      <motion.p
        className="cap__lead"
        variants={fadeUp}
        {...(shouldReduceMotion ? {} : inView())}
      >
        Không phải lớp học đại trà, cũng không phải chatbot trả lời cho có.
        Đây là một trải nghiệm học được thiết kế riêng cho cách bạn suy nghĩ.
      </motion.p>

      <motion.div
        className="cap__grid"
        variants={staggerEditorial}
        initial={shouldReduceMotion ? false : 'hidden'}
        {...(shouldReduceMotion ? {} : inView({ amount: 0.15 }))}
      >
        {CAPABILITIES.map((c, i) => (
          <CapabilityCard key={c.title} cap={c} idx={i} reduce={shouldReduceMotion} />
        ))}
      </motion.div>
    </div>
  </section>
)

const CapabilityCard = ({ cap, idx, reduce }) => {
  const cardRef = useRef(null)
  const mx = useMotionValue(0)
  const my = useMotionValue(0)
  const rx = useSpring(useTransform(my, [-0.5, 0.5], [4, -4]), { stiffness: 150, damping: 18 })
  const ry = useSpring(useTransform(mx, [-0.5, 0.5], [-6, 6]), { stiffness: 150, damping: 18 })

  const onMove = (e) => {
    if (reduce) return
    const r = cardRef.current?.getBoundingClientRect()
    if (!r) return
    mx.set((e.clientX - r.left) / r.width - 0.5)
    my.set((e.clientY - r.top) / r.height - 0.5)
  }
  const onLeave = () => { mx.set(0); my.set(0) }

  return (
    <motion.article
      ref={cardRef}
      className="cap-card"
      variants={fadeUp}
      onMouseMove={onMove}
      onMouseLeave={onLeave}
      style={reduce ? undefined : { rotateX: rx, rotateY: ry, transformPerspective: 800 }}
    >
      <span className="cap-card__num">{String(idx + 1).padStart(2, '0')}</span>
      <div className={`cap-card__icon cap-card__icon--${cap.accent}`}>{cap.icon}</div>
      <h3 className="cap-card__title">{cap.title}</h3>
      <p className="cap-card__desc">{cap.desc}</p>
      <div className="cap-card__metric">
        <strong>{cap.metric}</strong>
        <span>{cap.metricLabel}</span>
      </div>
    </motion.article>
  )
}

/* =============================================================================
   3. PROCESS — Define. Deploy. Scale. → Đánh giá. Lộ trình. Học.
   ============================================================================= */
const ProcessSection = ({ shouldReduceMotion }) => (
  <section className="proc" id="process" aria-labelledby="proc-heading">
    <div className="landing-container">
      <SectionLabel text="Cách bắt đầu" />
      <motion.h2
        id="proc-heading"
        className="proc__title"
        variants={fadeUp}
        {...(shouldReduceMotion ? {} : inView())}
      >
        Đơn giản như <span className="proc__title-dim">pha một ly</span> cà phê.
      </motion.h2>

      <div className="proc__grid">
        {STEPS.map((s, i) => (
          <motion.div
            key={s.title}
            className="proc__step"
            variants={fadeUp}
            {...(shouldReduceMotion ? {} : inView({ amount: 0.4 }))}
            transition={{ delay: shouldReduceMotion ? 0 : i * 0.18, duration: 0.8, ease: EASE.cinematic }}
          >
            <span className="proc__num">{String(i + 1).padStart(2, '0')}</span>
            <div className="proc__step-body">
              <h3 className="proc__step-title">
                {s.title}
                <span className="proc__step-suffix">{s.suffix}</span>
              </h3>
              <p className="proc__step-desc">{s.desc}</p>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  </section>
)

/* =============================================================================
   4. REACH — analog of "Global by default" 29 regions
   For us: course categories with student counts
   ============================================================================= */
const ReachSection = ({ shouldReduceMotion }) => (
  <section className="reach" aria-labelledby="reach-heading">
    <div className="landing-container">
      <SectionLabel text="Bạn muốn học gì cũng có" />
      <motion.h2
        id="reach-heading"
        className="reach__title"
        variants={fadeUp}
        {...(shouldReduceMotion ? {} : inView())}
      >
        Có thứ <em>bạn cần</em>, ở đây.
      </motion.h2>
      <motion.p
        className="reach__lead"
        variants={fadeUp}
        {...(shouldReduceMotion ? {} : inView())}
      >
        Học để chuyển nghề, học để lên lương, hay học vì tò mò — đều ổn cả.
        Chọn một lĩnh vực bạn quan tâm và bắt đầu, không ai vội cả.
      </motion.p>

      <div className="reach__layout">
        <motion.div
          className="reach__hero"
          variants={fadeUp}
          {...(shouldReduceMotion ? {} : inView())}
        >
          <span className="reach__hero-num">5</span>
          <span className="reach__hero-label">lĩnh vực chính</span>
          <p className="reach__hero-desc">
            Chương trình từ cơ bản tới chuyên sâu, được cập nhật liên tục theo
            nhu cầu thị trường lao động.
          </p>
          <div className="reach__hero-stats">
            <div><strong>99.5%</strong><span>Uptime nền tảng</span></div>
            <div><strong>&lt;200ms</strong><span>Phản hồi AI</span></div>
          </div>
        </motion.div>

        <motion.div
          className="reach__regions"
          variants={staggerEditorial}
          initial={shouldReduceMotion ? false : 'hidden'}
          {...(shouldReduceMotion ? {} : inView({ amount: 0.2 }))}
        >
          {REGIONS.map((r) => (
            <motion.div key={r.name} className="reach__region" variants={fadeUp}>
              <span className="reach__region-status" data-status={r.status} />
              <div className="reach__region-info">
                <strong>{r.name}</strong>
                <span>{r.nodes}</span>
              </div>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </div>
  </section>
)

/* =============================================================================
   5. LIVE METRICS — animated counters (COMPUTE "Real-time agent metrics")
   ============================================================================= */
const LiveMetricsSection = ({ shouldReduceMotion }) => {
  const ref = useRef(null)
  const isVisible = useInView(ref, { once: true, amount: 0.3 })

  return (
    <section className="live" ref={ref} aria-labelledby="live-heading">
      <div className="landing-container">
        <span className="live__pulse">
          <span className="live__pulse-dot" />
          LIVE
        </span>
        <motion.h2
          id="live-heading"
          className="live__title"
          variants={fadeUp}
          {...(shouldReduceMotion ? {} : inView())}
        >
          Đang học <em>ngay lúc này</em>.
        </motion.h2>

        <div className="live__grid">
          <div className="live__big">
            <Counter
              from={0}
              to={183420}
              active={isVisible || shouldReduceMotion}
              instant={shouldReduceMotion}
            />
            <span className="live__big-label">bài học hoàn thành hôm nay</span>
            <span className="live__big-sub">trên toàn nền tảng</span>
          </div>

          <div className="live__side">
            <div className="live__cell">
              <span className="live__cell-label">Học viên đang online</span>
              <strong>
                <Counter from={0} to={2347} active={isVisible || shouldReduceMotion} instant={shouldReduceMotion} />
              </strong>
            </div>
            <div className="live__cell">
              <span className="live__cell-label">Quiz đang làm</span>
              <strong>
                <Counter from={0} to={184} active={isVisible || shouldReduceMotion} instant={shouldReduceMotion} />
              </strong>
            </div>
            <div className="live__cell">
              <span className="live__cell-label">Thời gian phản hồi AI TB</span>
              <strong>148<small>ms</small></strong>
            </div>
            <div className="live__cell">
              <span className="live__cell-label">Tỉ lệ học viên đạt</span>
              <strong>92<small>%</small></strong>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}

/* Counter — animated integer counter using motion */
const Counter = ({ from = 0, to = 0, active = false, instant = false }) => {
  const mv = useMotionValue(from)
  const [display, setDisplay] = useState(from)

  useEffect(() => {
    if (!active) return
    if (instant) {
      setDisplay(to)
      return
    }
    const controls = animateMotionValue(mv, to, 1.6, EASE.cinematic, (v) => {
      setDisplay(Math.round(v))
    })
    return controls
  }, [active, to, instant, mv])

  return <span className="counter">{display.toLocaleString('vi-VN')}</span>
}

// Manual animation helper — avoids depending on framer-motion 'animate' import quirks across versions
const animateMotionValue = (mv, target, duration, ease, onUpdate) => {
  const start = mv.get()
  const startTime = performance.now()
  let raf
  const tick = (now) => {
    const t = Math.min(1, (now - startTime) / (duration * 1000))
    // cubic bezier approximation for [0.65, 0, 0.35, 1] (cinematic) by default — good enough
    const eased = ease ? cubicBezier(ease[0], ease[1], ease[2], ease[3])(t) : t
    const value = start + (target - start) * eased
    mv.set(value)
    onUpdate?.(value)
    if (t < 1) raf = requestAnimationFrame(tick)
  }
  raf = requestAnimationFrame(tick)
  return () => cancelAnimationFrame(raf)
}

const cubicBezier = (p1x, p1y, p2x, p2y) => (t) => {
  const cx = 3 * p1x
  const bx = 3 * (p2x - p1x) - cx
  const ax = 1 - cx - bx
  const cy = 3 * p1y
  const by = 3 * (p2y - p1y) - cy
  const ay = 1 - cy - by
  let x = t
  for (let i = 0; i < 5; i++) {
    const dx = ((ax * x + bx) * x + cx) * x - t
    const ddx = (3 * ax * x + 2 * bx) * x + cx
    if (Math.abs(dx) < 1e-4) break
    if (ddx === 0) break
    x = x - dx / ddx
  }
  return ((ay * x + by) * x + cy) * x
}

/* =============================================================================
   6. SUBJECTS — analog of "Connect everything" 100+ integrations
   ============================================================================= */
const SubjectsSection = ({ shouldReduceMotion }) => (
  <section className="subj" id="subjects" aria-labelledby="subj-heading">
    <div className="landing-container">
      <SectionLabel text="Lĩnh vực phổ biến" />
      <motion.h2
        id="subj-heading"
        className="subj__title"
        variants={fadeUp}
        {...(shouldReduceMotion ? {} : inView())}
      >
        Học <em>mọi thứ</em>.
      </motion.h2>
      <motion.p
        className="subj__lead"
        variants={fadeUp}
        {...(shouldReduceMotion ? {} : inView())}
      >
        Từ lập trình tới ngôn ngữ, từ khoa học dữ liệu tới kinh doanh. AI đồng hành
        xuyên suốt mọi chủ đề.
      </motion.p>

      <motion.div
        className="subj__grid"
        variants={staggerEditorial}
        initial={shouldReduceMotion ? false : 'hidden'}
        {...(shouldReduceMotion ? {} : inView({ amount: 0.1 }))}
      >
        {SUBJECTS.map((s) => (
          <motion.div key={s.name} className="subj__cell" variants={fadeUp}>
            <span className="subj__cell-cat">{s.cat}</span>
            <strong className="subj__cell-name">{s.name}</strong>
          </motion.div>
        ))}
      </motion.div>

      <div className="subj__bottom">
        <span><strong>500+</strong> khóa học</span>
        <span><strong>95%</strong> đánh giá ≥ 4 sao</span>
        <span><strong>Mới hằng tuần</strong></span>
      </div>
    </div>
  </section>
)

/* =============================================================================
   7. PRIVACY — COMPUTE "Autonomous, not uncontrolled" analog
   ============================================================================= */
const PrivacySection = ({ shouldReduceMotion }) => (
  <section className="priv" aria-labelledby="priv-heading">
    <div className="landing-container">
      <SectionLabel text="Bảo mật" />
      <motion.h2
        id="priv-heading"
        className="priv__title"
        variants={fadeUp}
        {...(shouldReduceMotion ? {} : inView())}
      >
        Mạnh mẽ, <em>không xâm phạm</em>.
      </motion.h2>
      <motion.p
        className="priv__lead"
        variants={fadeUp}
        {...(shouldReduceMotion ? {} : inView())}
      >
        Dữ liệu học tập của bạn được mã hóa toàn phần. Không lưu trữ lịch sử
        chat ngoài bối cảnh học. Không huấn luyện model bằng dữ liệu cá nhân.
      </motion.p>

      <motion.div
        className="priv__grid"
        variants={staggerEditorial}
        initial={shouldReduceMotion ? false : 'hidden'}
        {...(shouldReduceMotion ? {} : inView({ amount: 0.2 }))}
      >
        {PRIVACY_ITEMS.map((p) => (
          <motion.div key={p.title} className="priv__card" variants={fadeUp}>
            <div className="priv__icon">{p.icon}</div>
            <h3 className="priv__card-title">{p.title}</h3>
            <p className="priv__card-desc">{p.desc}</p>
          </motion.div>
        ))}
      </motion.div>

      <div className="priv__badges">
        <span>Mã hóa AES-256</span>
        <span>HTTPS toàn site</span>
        <span>Không bán dữ liệu</span>
        <span>Quyền xóa toàn phần</span>
      </div>
    </div>
  </section>
)

/* =============================================================================
   8. INSTRUCTOR — COMPUTE "Developer SDK" analog
   ============================================================================= */
const InstructorSection = ({ shouldReduceMotion }) => (
  <section className="inst" aria-labelledby="inst-heading">
    <div className="landing-container">
      <div className="inst__layout">
        <motion.div
          className="inst__copy"
          variants={fadeUp}
          {...(shouldReduceMotion ? {} : inView())}
        >
          <SectionLabel text="Dành cho giảng viên" />
          <h2 id="inst-heading" className="inst__title">
            Tạo khóa học. <em>AI lo phần còn lại.</em>
          </h2>
          <p className="inst__lead">
            Soạn nội dung một lần, AI tự sinh quiz, gợi ý bài tập, và tinh chỉnh
            khóa học theo phản hồi học viên. Quản lý lớp, theo dõi tiến độ.
          </p>
          <ul className="inst__list">
            <li><span className="inst__bullet" aria-hidden="true" />AI sinh quiz tự động từ nội dung</li>
            <li><span className="inst__bullet" aria-hidden="true" />Theo dõi tiến độ học viên realtime</li>
            <li><span className="inst__bullet" aria-hidden="true" />Bảng điều khiển lớp học chuyên nghiệp</li>
            <li><span className="inst__bullet" aria-hidden="true" />Phân tích điểm mạnh / điểm yếu lớp</li>
          </ul>
          <Link to="/auth/register" className="inst__cta">
            Trở thành giảng viên →
          </Link>
        </motion.div>

        <motion.div
          className="inst__visual"
          variants={fadeUp}
          {...(shouldReduceMotion ? {} : inView())}
        >
          <div className="inst__terminal">
            <div className="inst__terminal-bar">
              <span /><span /><span />
              <code>course-editor.tsx</code>
            </div>
            <pre className="inst__code">
{`{
  "title": "Lập trình Python cơ bản",
  "modules": 8,
  "ai_quiz_generation": true,
  "progress_tracking": "real-time",
  "auto_recommend": ["Algorithms", "OOP"]
}`}
            </pre>
          </div>
        </motion.div>
      </div>
    </div>
  </section>
)

/* =============================================================================
   9. TESTIMONIAL
   ============================================================================= */
const TestimonialSection = ({ shouldReduceMotion }) => (
  <section className="testi" aria-label="Đánh giá">
    <div className="landing-container">
      <motion.blockquote
        className="testi__quote"
        variants={fadeUp}
        {...(shouldReduceMotion ? {} : inView())}
      >
        <span className="testi__mark" aria-hidden="true">“</span>
        AI đề xuất đúng phần tôi yếu, không bắt tôi học lại từ đầu. Sau 3 tháng,
        tôi đã chuyển job sang vị trí Data Analyst.
        <footer className="testi__by">
          <strong>Nguyễn Minh Hà</strong>
          <span>Data Analyst @ Tiki — học viên Khóa Khoa học dữ liệu</span>
        </footer>
      </motion.blockquote>

      <motion.div
        className="testi__brands"
        variants={fadeUp}
        {...(shouldReduceMotion ? {} : inView())}
      >
        <span>Tiki</span>
        <span>Shopee</span>
        <span>FPT Software</span>
        <span>VinAI</span>
        <span>VPBank</span>
      </motion.div>
    </div>
  </section>
)

/* =============================================================================
   10. PLANS — 3-tier pricing-style
   ============================================================================= */
const PlansSection = ({ shouldReduceMotion }) => (
  <section className="plans" id="plans" aria-labelledby="plans-heading">
    <div className="landing-container">
      <SectionLabel text="Học theo cách bạn thích" />
      <motion.h2
        id="plans-heading"
        className="plans__title"
        variants={fadeUp}
        {...(shouldReduceMotion ? {} : inView())}
      >
        Bắt đầu <em>miễn phí</em>, nâng cấp khi bạn muốn.
      </motion.h2>

      <motion.div
        className="plans__grid"
        variants={staggerEditorial}
        initial={shouldReduceMotion ? false : 'hidden'}
        {...(shouldReduceMotion ? {} : inView({ amount: 0.15 }))}
      >
        {PLANS.map((p, i) => (
          <motion.div
            key={p.name}
            className={`plan${p.featured ? ' plan--featured' : ''}`}
            variants={fadeUp}
          >
            <span className="plan__num">{String(i + 1).padStart(2, '0')}</span>
            {p.featured && <span className="plan__tag">Phổ biến</span>}
            <h3 className="plan__name">{p.name}</h3>
            <p className="plan__pitch">{p.pitch}</p>
            <div className="plan__price">
              <strong>{p.price}</strong>
              {p.priceSuffix && <span>{p.priceSuffix}</span>}
            </div>
            <ul className="plan__list">
              {p.features.map((f) => <li key={f}>{f}</li>)}
            </ul>
            <Link to={p.cta.to} className={`plan__cta${p.featured ? ' plan__cta--featured' : ''}`}>
              {p.cta.label}
            </Link>
          </motion.div>
        ))}
      </motion.div>
    </div>
  </section>
)

/* =============================================================================
   11. FINAL CTA
   ============================================================================= */
const FinalCTASection = ({ shouldReduceMotion }) => {
  const ref = useRef(null)
  const { scrollYProgress } = useScroll({ target: ref, offset: ['start end', 'end start'] })
  const bgY = useTransform(scrollYProgress, [0, 1], shouldReduceMotion ? [0, 0] : [60, -60])
  const bgScale = useTransform(scrollYProgress, [0, 1], shouldReduceMotion ? [1, 1] : [1, 1.15])

  return (
    <section className="cta" ref={ref} aria-labelledby="cta-heading">
      <motion.div className="cta__bg-layer" style={{ y: bgY, scale: bgScale }} aria-hidden="true" />
      <div className="landing-container">
        <motion.div
          className="cta__content"
          variants={fadeUp}
          {...(shouldReduceMotion ? {} : inView())}
        >
          <p className="cta__overline">Khi nào bạn sẵn sàng</p>
          <h2 id="cta-heading" className="cta__title">
            Hôm nay là một ngày tốt để bắt đầu.
          </h2>
          <p className="cta__desc">
            Bạn không cần lý do hoành tráng. Chỉ cần một chút tò mò là đủ.
            Đăng ký miễn phí, không cần thẻ tín dụng.
          </p>
          <div className="cta__actions">
            <Link to="/auth/register">
              <Button variant="secondary" size="lg">Tạo tài khoản miễn phí →</Button>
            </Link>
            <Link to="/auth/login" className="cta__login-link">
              Tôi đã có tài khoản
            </Link>
          </div>
        </motion.div>
      </div>
    </section>
  )
}

/* Section header label helper */
const SectionLabel = ({ text }) => (
  <span className="section-label" aria-hidden="true">
    <span className="section-label__dash" />
    {text}
  </span>
)

/* =============================================================================
   FOOTER
   ============================================================================= */
const LandingFooter = () => (
  <footer className="landing-footer" role="contentinfo">
    <div className="landing-container">
      <div className="landing-footer__grid">
        <div className="landing-footer__brand">
          <div className="landing-logo">
            <span className="landing-logo__mark" aria-hidden="true">◆</span>
            <span className="landing-logo__text">AI Learning</span>
          </div>
          <p className="landing-footer__tagline">
            Nền tảng học tập thông minh cho tương lai
          </p>
        </div>

        <div className="landing-footer__links">
          <div className="landing-footer__col">
            <h4>Sản phẩm</h4>
            <Link to="/dashboard/courses">Khóa học</Link>
            <Link to="/dashboard/assessment">Đánh giá năng lực</Link>
            <Link to="/dashboard/chat">AI Chat</Link>
          </div>
          <div className="landing-footer__col">
            <h4>Tài khoản</h4>
            <Link to="/auth/login">Đăng nhập</Link>
            <Link to="/auth/register">Đăng ký</Link>
          </div>
        </div>
      </div>

      <div className="landing-footer__bottom">
        <p>© {new Date().getFullYear()} AI Learning Platform. Bảo lưu mọi quyền.</p>
      </div>
    </div>
  </footer>
)

/* =============================================================================
   STATIC DATA
   ============================================================================= */
const METRICS = [
  { value: '10K+', label: 'Bạn học cùng' },
  { value: '500+', label: 'Khóa học chờ bạn' },
  { value: '95%', label: 'Cảm thấy tiến bộ' },
]

const CAPABILITIES = [
  {
    icon: <BrainIcon />,
    accent: 'gold',
    title: 'Bắt đầu đúng chỗ bạn đang đứng',
    desc: 'Một bài kiểm tra ngắn để biết bạn đã giỏi gì rồi và chỗ nào còn lăn tăn — không bắt bạn học lại từ A.',
    metric: '~5 phút',
    metricLabel: 'để biết bạn ở đâu',
  },
  {
    icon: <BookIcon />,
    accent: 'copper',
    title: 'Đường đi riêng cho bạn',
    desc: 'Bài học được sắp xếp theo nhịp của bạn. Đang bận thì lùi, đang hăng thì đi nhanh hơn.',
    metric: 'Theo bạn',
    metricLabel: 'không theo lịch ai cả',
  },
  {
    icon: <ChatIcon />,
    accent: 'jade',
    title: 'Có người để hỏi mọi lúc',
    desc: 'Kẹt một đoạn code, không hiểu một định nghĩa? Hỏi luôn. AI nhớ bạn đang học gì để trả lời sát sườn.',
    metric: '24/7',
    metricLabel: 'không cần hẹn lịch',
  },
]

const STEPS = [
  { title: 'Đăng ký', suffix: 'mất 30 giây', desc: 'Email, mật khẩu, xong. Không cần thẻ tín dụng, không cần khai báo gì lằng nhằng.' },
  { title: 'Trò chuyện', suffix: 'với AI một lúc', desc: 'Một bài kiểm tra nhỏ giúp AI hiểu bạn đang ở đâu — bạn không cần làm gì khác ngoài trả lời thật.' },
  { title: 'Học', suffix: 'theo nhịp của bạn', desc: 'AI dẫn bạn đi từng bước. Bí chỗ nào hỏi luôn chỗ đó, có người trả lời ngay.' },
]

const REGIONS = [
  { name: 'Lập trình', nodes: '142 khóa học', status: 'live' },
  { name: 'Khoa học dữ liệu', nodes: '88 khóa học', status: 'live' },
  { name: 'Toán & Logic', nodes: '76 khóa học', status: 'live' },
  { name: 'Kinh doanh', nodes: '120 khóa học', status: 'live' },
  { name: 'Ngôn ngữ', nodes: '94 khóa học', status: 'live' },
  { name: 'Thiết kế', nodes: 'Sắp ra mắt', status: 'soon' },
]

const SUBJECTS = [
  { cat: 'Lập trình', name: 'Python' },
  { cat: 'Lập trình', name: 'JavaScript' },
  { cat: 'Data', name: 'SQL' },
  { cat: 'Data', name: 'Pandas' },
  { cat: 'AI', name: 'Machine Learning' },
  { cat: 'AI', name: 'Deep Learning' },
  { cat: 'Web', name: 'React' },
  { cat: 'Web', name: 'Node.js' },
  { cat: 'Toán', name: 'Đại số tuyến tính' },
  { cat: 'Toán', name: 'Giải tích' },
  { cat: 'Kinh doanh', name: 'Marketing' },
  { cat: 'Kinh doanh', name: 'Tài chính' },
  { cat: 'Ngôn ngữ', name: 'Tiếng Anh' },
  { cat: 'Ngôn ngữ', name: 'Tiếng Nhật' },
]

const PRIVACY_ITEMS = [
  { icon: <ShieldIcon />, title: 'Cô lập dữ liệu', desc: 'Mỗi học viên có không gian học tập độc lập.' },
  { icon: <LockIcon />, title: 'Mã hóa toàn phần', desc: 'AES-256 ở mức nghỉ và TLS khi truyền.' },
  { icon: <EyeIcon />, title: 'Audit minh bạch', desc: 'Bạn xem được lịch sử AI tương tác bất cứ lúc nào.' },
  { icon: <KeyIcon />, title: 'Quyền tối thiểu', desc: 'AI chỉ truy cập đúng module bạn đang học.' },
]

const PLANS = [
  {
    name: 'Khám phá',
    pitch: 'Bắt đầu thử xem có hợp với bạn không.',
    price: 'Miễn phí',
    features: [
      'Truy cập các khóa cơ bản',
      'Hỏi AI 50 câu mỗi ngày',
      'Một lộ trình đơn giản',
      'Theo dõi tiến độ học của mình',
    ],
    cta: { label: 'Bắt đầu, không cần thẻ', to: '/auth/register' },
  },
  {
    name: 'Pro',
    pitch: 'Nếu bạn nghiêm túc và muốn đi xa hơn.',
    price: '199K',
    priceSuffix: '/tháng',
    featured: true,
    features: [
      'Mở khóa toàn bộ khóa học',
      'Hỏi AI thoải mái, không giới hạn',
      'Lộ trình AI sâu hơn theo mục tiêu',
      'Báo cáo tiến độ hằng tuần',
      'Chứng chỉ khi hoàn thành khóa',
    ],
    cta: { label: 'Học thử 7 ngày, hủy lúc nào cũng được', to: '/auth/register' },
  },
  {
    name: 'Đội nhóm',
    pitch: 'Cho công ty muốn đào tạo nhân sự thật sự dùng được.',
    price: 'Liên hệ',
    features: [
      'Mọi tính năng của Pro',
      'Quản lý lớp & báo cáo cho leader',
      'Kết nối hệ thống nội bộ (HR / SSO)',
      'Có người hỗ trợ riêng',
      'Khóa học theo yêu cầu của công ty',
    ],
    cta: { label: 'Nói chuyện với chúng tôi', to: '/auth/register' },
  },
]

/* =============================================================================
   SVG ICONS — function declarations (hoisted)
   ============================================================================= */
function BrainIcon() {
  return (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v15a2.5 2.5 0 0 1-4.96-.44 2.5 2.5 0 0 1-2.96-3.08 3 3 0 0 1-.34-5.58 2.5 2.5 0 0 1 1.32-4.24 2.5 2.5 0 0 1 4.44-1.66" />
      <path d="M14.5 2A2.5 2.5 0 0 0 12 4.5v15a2.5 2.5 0 0 0 4.96-.44 2.5 2.5 0 0 0 2.96-3.08 3 3 0 0 0 .34-5.58 2.5 2.5 0 0 0-1.32-4.24 2.5 2.5 0 0 0-4.44-1.66" />
    </svg>
  )
}
function BookIcon() {
  return (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z" /><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z" />
    </svg>
  )
}
function ChatIcon() {
  return (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
    </svg>
  )
}
function ShieldIcon() {
  return (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
    </svg>
  )
}
function LockIcon() {
  return (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <rect x="3" y="11" width="18" height="11" rx="2" /><path d="M7 11V7a5 5 0 0 1 10 0v4" />
    </svg>
  )
}
function EyeIcon() {
  return (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" /><circle cx="12" cy="12" r="3" />
    </svg>
  )
}
function KeyIcon() {
  return (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="7.5" cy="15.5" r="5.5" /><path d="m21 2-9.6 9.6" /><path d="m15.5 7.5 3 3L22 7l-3-3" />
    </svg>
  )
}
function ScrollDownIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 5v14" /><path d="m19 12-7 7-7-7" />
    </svg>
  )
}

export default LandingPage
