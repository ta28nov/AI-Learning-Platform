import { useRef, useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import {
  motion,
  useScroll,
  useTransform,
  useReducedMotion,
  useSpring,
  AnimatePresence,
} from 'framer-motion'
import Button from '@components/ui/Button'
import { staggerEditorial, fadeUp, fadeDown, inView, DURATION, EASE } from '@/styles/motion'
import './LandingPage.css'

/* =============================================================================
   LANDING PAGE — Editorial Cinematic Scrollytelling
   Chapters: Hero → Features → How It Works → Stats → CTA → Footer
   CTA routes preserved: /auth/register, /auth/login
   ============================================================================= */

const LandingPage = () => {
  const [scrolled, setScrolled] = useState(false)
  const shouldReduceMotion = useReducedMotion()

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 60)
    window.addEventListener('scroll', handleScroll, { passive: true })
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  return (
    <div className="landing">
      {/* ── HEADER ── */}
      <LandingHeader scrolled={scrolled} />

      {/* ── CH.1: HERO ── */}
      <HeroSection shouldReduceMotion={shouldReduceMotion} />

      {/* ── CH.2: FEATURES ── */}
      <FeaturesSection shouldReduceMotion={shouldReduceMotion} />

      {/* ── CH.3: HOW IT WORKS ── */}
      <HowItWorksSection shouldReduceMotion={shouldReduceMotion} />

      {/* ── CH.4: STATS / SOCIAL PROOF ── */}
      <StatsSection shouldReduceMotion={shouldReduceMotion} />

      {/* ── CH.5: CTA ── */}
      <CTASection shouldReduceMotion={shouldReduceMotion} />

      {/* ── CH.6: FOOTER ── */}
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
          <a href="#features" className="landing-nav__link">Tính năng</a>
          <a href="#how-it-works" className="landing-nav__link">Cách hoạt động</a>
          <a href="#stats" className="landing-nav__link">Thành tựu</a>
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
   CHAPTER 1: HERO — full-viewport, Fraunces display, scroll-parallax
   ============================================================================= */
const HeroSection = ({ shouldReduceMotion }) => {
  const ref = useRef(null)
  const { scrollYProgress } = useScroll({ target: ref, offset: ['start start', 'end start'] })

  // Parallax: content floats upward as user scrolls out of hero
  const y = useTransform(scrollYProgress, [0, 1], shouldReduceMotion ? [0, 0] : [0, -80])
  const opacity = useTransform(scrollYProgress, [0, 0.6], shouldReduceMotion ? [1, 1] : [1, 0])

  // Gold accent line width — expands on load
  const lineScale = useSpring(1, { stiffness: 80, damping: 20 })

  return (
    <section className="hero" ref={ref} aria-labelledby="hero-heading">
      {/* Noise + mesh background */}
      <div className="hero__bg" aria-hidden="true">
        <div className="hero__mesh" />
        <div className="hero__noise" />
      </div>

      <div className="landing-container">
        <motion.div
          className="hero__content"
          style={{ y, opacity }}
          variants={staggerEditorial}
          initial={shouldReduceMotion ? false : 'hidden'}
          animate="show"
        >
          {/* Chapter label */}
          <motion.div className="hero__eyebrow" variants={fadeDown}>
            <span className="hero__eyebrow-line" aria-hidden="true" />
            <span>Nền tảng học tập thế hệ mới</span>
          </motion.div>

          {/* Display headline — Fraunces */}
          <motion.h1
            id="hero-heading"
            className="hero__title"
            variants={fadeUp}
          >
            Học tập thông minh hơn
            <br />
            với{' '}
            <em className="hero__title-em">Trí tuệ nhân tạo</em>
          </motion.h1>

          {/* Body description — Newsreader */}
          <motion.p className="hero__desc" variants={fadeUp}>
            AI phân tích trình độ của bạn, tạo lộ trình cá nhân hóa,
            và đồng hành suốt quá trình học tập.
            Hiệu quả gấp 3 lần phương pháp truyền thống.
          </motion.p>

          {/* CTA row */}
          <motion.div className="hero__actions" variants={fadeUp}>
            <Link to="/auth/register">
              <Button.Magnetic size="lg">Bắt đầu học tập →</Button.Magnetic>
            </Link>
            <Link to="/auth/login">
              <Button variant="ghost" size="lg" className="hero__ghost-cta">
                Đã có tài khoản
              </Button>
            </Link>
          </motion.div>

          {/* Metrics strip */}
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

      {/* Scroll indicator */}
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

/* =============================================================================
   CHAPTER 2: FEATURES
   ============================================================================= */
const FeaturesSection = ({ shouldReduceMotion }) => (
  <section className="features" id="features" aria-labelledby="features-heading">
    <div className="landing-container">
      <motion.div
        className="section-header"
        variants={fadeUp}
        {...(shouldReduceMotion ? {} : inView())}
      >
        <span className="section-eyebrow">Tính năng</span>
        <h2 id="features-heading" className="section-title">
          Mọi thứ bạn cần để học tập hiệu quả
        </h2>
        <p className="section-desc">
          Hệ thống tích hợp AI tiên tiến, giúp bạn học đúng cách và nhanh hơn
        </p>
      </motion.div>

      <motion.div
        className="features__grid"
        variants={staggerEditorial}
        initial={shouldReduceMotion ? false : 'hidden'}
        {...(shouldReduceMotion ? {} : inView({ amount: 0.15 }))}
      >
        {FEATURES.map((f) => (
          <motion.article
            key={f.title}
            className="feature-card"
            variants={fadeUp}
            whileHover={shouldReduceMotion ? {} : { y: -4, transition: { duration: 0.2 } }}
          >
            <div className={`feature-card__icon feature-card__icon--${f.accent}`} aria-hidden="true">
              {f.icon}
            </div>
            <h3 className="feature-card__title">{f.title}</h3>
            <p className="feature-card__desc">{f.desc}</p>
          </motion.article>
        ))}
      </motion.div>
    </div>
  </section>
)

/* =============================================================================
   CHAPTER 3: HOW IT WORKS — editorial numbered steps
   ============================================================================= */
const HowItWorksSection = ({ shouldReduceMotion }) => (
  <section className="how-it-works" id="how-it-works" aria-labelledby="steps-heading">
    <div className="landing-container">
      <motion.div
        className="section-header"
        variants={fadeUp}
        {...(shouldReduceMotion ? {} : inView())}
      >
        <span className="section-eyebrow">Quy trình</span>
        <h2 id="steps-heading" className="section-title">3 bước bắt đầu hành trình</h2>
      </motion.div>

      <div className="steps">
        {STEPS.map((s, i) => (
          <motion.div
            key={s.title}
            className="step"
            variants={fadeUp}
            {...(shouldReduceMotion ? {} : inView({ amount: 0.4 }))}
            transition={{ delay: shouldReduceMotion ? 0 : i * 0.12 }}
          >
            <div className="step__numeral" aria-hidden="true">
              {String(i + 1).padStart(2, '0')}
            </div>
            <div className="step__body">
              <div className="step__connector" aria-hidden="true" />
              <h3 className="step__title">{s.title}</h3>
              <p className="step__desc">{s.desc}</p>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  </section>
)

/* =============================================================================
   CHAPTER 4: STATS — large editorial number display
   ============================================================================= */
const StatsSection = ({ shouldReduceMotion }) => (
  <section className="stats" id="stats" aria-label="Số liệu">
    <div className="landing-container">
      <motion.div
        className="stats__grid"
        variants={staggerEditorial}
        initial={shouldReduceMotion ? false : 'hidden'}
        {...(shouldReduceMotion ? {} : inView({ amount: 0.2 }))}
      >
        {STATS.map((s) => (
          <motion.div key={s.label} className="stat-card" variants={fadeUp}>
            <strong className="stat-card__value">{s.value}</strong>
            <span className="stat-card__label">{s.label}</span>
          </motion.div>
        ))}
      </motion.div>
    </div>
  </section>
)

/* =============================================================================
   CHAPTER 5: CTA — ink-black full-width editorial block
   ============================================================================= */
const CTASection = ({ shouldReduceMotion }) => {
  const ref = useRef(null)
  const { scrollYProgress } = useScroll({ target: ref, offset: ['start end', 'end start'] })
  const bgY = useTransform(scrollYProgress, [0, 1], shouldReduceMotion ? [0, 0] : [30, -30])

  return (
    <section className="cta" ref={ref} aria-labelledby="cta-heading">
      <motion.div className="cta__bg-layer" style={{ y: bgY }} aria-hidden="true" />

      <div className="landing-container">
        <motion.div
          className="cta__content"
          variants={fadeUp}
          {...(shouldReduceMotion ? {} : inView())}
        >
          <p className="cta__overline">Sẵn sàng chưa?</p>
          <h2 id="cta-heading" className="cta__title">
            Thay đổi cách học tập của bạn
          </h2>
          <p className="cta__desc">
            Tham gia cùng hàng nghìn học viên đã tin tưởng nền tảng của chúng tôi.
            Bắt đầu miễn phí, không cần thẻ tín dụng.
          </p>
          <div className="cta__actions">
            <Link to="/auth/register">
              <Button variant="secondary" size="lg">Đăng ký miễn phí →</Button>
            </Link>
            <Link to="/auth/login" className="cta__login-link">
              Đăng nhập tài khoản có sẵn
            </Link>
          </div>
        </motion.div>
      </div>
    </section>
  )
}

/* =============================================================================
   CHAPTER 6: FOOTER — full landing-specific footer
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
   STATIC DATA — không thay đổi content, chỉ cập nhật icon sang SVG inline
   ============================================================================= */
const METRICS = [
  { value: '10K+', label: 'Học viên' },
  { value: '500+', label: 'Khóa học' },
  { value: '95%', label: 'Hài lòng' },
]

const FEATURES = [
  {
    icon: <BrainIcon />,
    accent: 'gold',
    title: 'Đánh giá năng lực AI',
    desc: 'Hệ thống AI tự động đánh giá trình độ và đề xuất lộ trình học tập phù hợp nhất với bạn.',
  },
  {
    icon: <BookIcon />,
    accent: 'copper',
    title: 'Khóa học cá nhân hóa',
    desc: 'Nội dung được AI tự điều chỉnh theo tốc độ và phong cách học của từng học viên.',
  },
  {
    icon: <ChatIcon />,
    accent: 'jade',
    title: 'Trợ lý AI 24/7',
    desc: 'Trợ lý ảo thông minh giải đáp thắc mắc bất cứ lúc nào, như có gia sư riêng.',
  },
  {
    icon: <ChartIcon />,
    accent: 'gold',
    title: 'Phân tích chi tiết',
    desc: 'Theo dõi tiến độ, điểm mạnh, điểm yếu với biểu đồ và báo cáo trực quan.',
  },
  {
    icon: <TargetIcon />,
    accent: 'copper',
    title: 'Quiz thông minh',
    desc: 'Bài tập và quiz tự động sinh bởi AI, phù hợp với trình độ hiện tại của bạn.',
  },
  {
    icon: <AwardIcon />,
    accent: 'jade',
    title: 'Chứng chỉ hoàn thành',
    desc: 'Nhận chứng chỉ sau khi hoàn thành khóa học, chia sẻ trên hồ sơ chuyên nghiệp.',
  },
]

const STEPS = [
  {
    title: 'Đăng ký tài khoản',
    desc: 'Tạo tài khoản miễn phí chỉ trong 30 giây với email của bạn.',
  },
  {
    title: 'Làm bài đánh giá',
    desc: 'AI sẽ phân tích trình độ và tạo lộ trình học tập riêng cho bạn.',
  },
  {
    title: 'Bắt đầu học tập',
    desc: 'Truy cập khóa học, làm quiz, và chat với AI để nâng cao kỹ năng.',
  },
]

const STATS = [
  { value: '10,000+', label: 'Học viên đang hoạt động' },
  { value: '500+', label: 'Khóa học chất lượng' },
  { value: '95%', label: 'Tỷ lệ hài lòng' },
  { value: '3×', label: 'Hiệu quả học tập' },
]

/* =============================================================================
   SVG ICONS — inline, no emoji, editorial weight
   ============================================================================= */
const BrainIcon = () => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v15a2.5 2.5 0 0 1-4.96-.44 2.5 2.5 0 0 1-2.96-3.08 3 3 0 0 1-.34-5.58 2.5 2.5 0 0 1 1.32-4.24 2.5 2.5 0 0 1 4.44-1.66" />
    <path d="M14.5 2A2.5 2.5 0 0 0 12 4.5v15a2.5 2.5 0 0 0 4.96-.44 2.5 2.5 0 0 0 2.96-3.08 3 3 0 0 0 .34-5.58 2.5 2.5 0 0 0-1.32-4.24 2.5 2.5 0 0 0-4.44-1.66" />
  </svg>
)
const BookIcon = () => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z" /><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z" />
  </svg>
)
const ChatIcon = () => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
  </svg>
)
const ChartIcon = () => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <line x1="18" y1="20" x2="18" y2="10" /><line x1="12" y1="20" x2="12" y2="4" /><line x1="6" y1="20" x2="6" y2="14" />
  </svg>
)
const TargetIcon = () => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="10" /><circle cx="12" cy="12" r="6" /><circle cx="12" cy="12" r="2" />
  </svg>
)
const AwardIcon = () => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="8" r="6" /><path d="M15.477 12.89 17 22l-5-3-5 3 1.523-9.11" />
  </svg>
)
const ScrollDownIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <path d="M12 5v14" /><path d="m19 12-7 7-7-7" />
  </svg>
)

export default LandingPage
