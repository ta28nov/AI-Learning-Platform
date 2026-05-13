import { useEffect, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  motion,
  useReducedMotion,
  useInView,
  AnimatePresence,
  useMotionValue,
  useTransform,
  animate,
} from 'framer-motion'
import Button from '@components/ui/Button'
import './LandingPage.css'

/* ----- Static content ----- */
const FLOW_STEPS = [
  { title: 'Đánh giá', desc: 'Bài test ngắn giúp AI hiểu mức hiện tại của bạn.' },
  { title: 'Lộ trình', desc: 'AI dựng kế hoạch học theo mục tiêu cá nhân.' },
  { title: 'Bài học', desc: 'Học theo mô-đun, có trợ giảng AI theo ngữ cảnh.' },
  { title: 'Ôn tập', desc: 'Quiz thích ứng nhắc lại đúng phần còn yếu.' },
]

const CORE_FEATURES = [
  { icon: '↗', title: 'Lộ trình theo mục tiêu', desc: 'AI ưu tiên nội dung theo mục tiêu nghề nghiệp.' },
  { icon: '◐', title: 'Nhịp học linh hoạt', desc: 'Lịch bận hay rảnh đều có nhịp phù hợp.' },
  { icon: '✦', title: 'Phản hồi tức thì', desc: 'Hỏi trực tiếp trong bài, nhận giải thích ngay.' },
  { icon: '◇', title: 'Ôn tập đúng điểm yếu', desc: 'Hệ thống nhắc học đúng phần còn yếu.' },
]

const FAQ_ITEMS = [
  { q: 'Mình mới bắt đầu thì có dùng được không?', a: 'Có. Assessment đầu vào giúp AI tạo lộ trình từ mức hiện tại của bạn.' },
  { q: 'AI có thay được giảng viên không?', a: 'AI hỗ trợ kèm học hằng ngày, còn giảng viên giúp định hướng chuyên sâu.' },
  { q: 'Có cần học theo lịch cố định không?', a: 'Không. Bạn chọn quỹ thời gian mỗi tuần, AI điều phối bài học theo đó.' },
  { q: 'Dữ liệu học tập có riêng tư không?', a: 'Dữ liệu được mã hóa, không chia sẻ ra ngoài và bạn kiểm soát lịch sử bất cứ lúc nào.' },
]

const TRUST_ITEMS = [
  'Mã hóa dữ liệu học tập đầu cuối',
  'Không bán dữ liệu cá nhân cho bên thứ ba',
  'Kiểm soát và xóa lịch sử học tập bất kỳ lúc nào',
]

const CHAT_PREVIEW = [
  { role: 'user', text: 'Giải thích đoạn code này giúp mình?' },
  { role: 'ai',   text: 'Đoạn này dùng useEffect để gọi API khi mount...' },
  { role: 'user', text: 'Vậy tại sao cần cleanup?' },
]

/* ----- Animation variants ----- */
const tileDropVariants = {
  hidden: { opacity: 0, y: -72, scale: 0.9, rotate: -2, filter: 'blur(6px)' },
  show: {
    opacity: 1,
    y: 0,
    scale: 1,
    rotate: 0,
    filter: 'blur(0px)',
    transition: { type: 'spring', stiffness: 220, damping: 18, mass: 1 },
  },
}

const containerStagger = {
  hidden: {},
  show: { transition: { staggerChildren: 0.12, delayChildren: 0.08 } },
}

const wordVariants = {
  hidden: { opacity: 0, y: 32, rotate: 4 },
  show: {
    opacity: 1,
    y: 0,
    rotate: 0,
    transition: { type: 'spring', stiffness: 200, damping: 22 },
  },
}

/* ----- Reusable components ----- */
const Tile = ({ children, className, reduce, ...rest }) => {
  const props = reduce
    ? {}
    : { variants: tileDropVariants }

  return (
    <motion.article className={`bento-tile ${className || ''}`} {...props} {...rest}>
      {children}
    </motion.article>
  )
}

const MediaPlaceholder = ({ title, subtitle, ratio = 'landscape' }) => (
  <div className={`media-placeholder media-placeholder--${ratio}`} role="img" aria-label={subtitle}>
    <span className="media-placeholder__title">{title}</span>
    <span className="media-placeholder__subtitle">{subtitle}</span>
  </div>
)

/* Animated counter */
const Counter = ({ to, suffix = '', duration = 1.4 }) => {
  const reduce = useReducedMotion()
  const ref = useRef(null)
  const inView = useInView(ref, { once: true, amount: 0.6 })
  const value = useMotionValue(0)
  const rounded = useTransform(value, (v) => Math.round(v))
  const [display, setDisplay] = useState(0)

  useEffect(() => {
    if (!inView) return
    if (reduce) { setDisplay(to); return }
    const controls = animate(value, to, { duration, ease: [0.2, 0.7, 0.2, 1] })
    const unsub = rounded.on('change', (v) => setDisplay(v))
    return () => { controls.stop(); unsub() }
  }, [inView, to, duration, reduce, rounded, value])

  return <span ref={ref}>{display}{suffix}</span>
}

/* Accordion */
const Accordion = ({ items }) => {
  const [open, setOpen] = useState(0)
  const reduce = useReducedMotion()
  return (
    <div className="accordion">
      {items.map((item, idx) => {
        const expanded = open === idx
        return (
          <div key={item.q} className={`accordion__row${expanded ? ' is-open' : ''}`}>
            <button
              type="button"
              className="accordion__btn"
              aria-expanded={expanded}
              onClick={() => setOpen(expanded ? -1 : idx)}
            >
              <span className="accordion__q">{item.q}</span>
              <span className="accordion__plus" aria-hidden="true">
                <span /><span />
              </span>
            </button>
            <AnimatePresence initial={false}>
              {expanded && (
                <motion.div
                  key="content"
                  className="accordion__panel"
                  initial={reduce ? false : { height: 0, opacity: 0 }}
                  animate={reduce ? { height: 'auto', opacity: 1 } : { height: 'auto', opacity: 1 }}
                  exit={reduce ? { opacity: 0 } : { height: 0, opacity: 0 }}
                  transition={{ duration: 0.32, ease: [0.4, 0, 0.2, 1] }}
                >
                  <p>{item.a}</p>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        )
      })}
    </div>
  )
}

/* Roadmap stepper */
const RoadmapStepper = ({ steps }) => {
  const [active, setActive] = useState(0)
  return (
    <div className="stepper">
      <div className="stepper__rail">
        <motion.div
          className="stepper__progress"
          initial={{ scaleY: 0 }}
          animate={{ scaleY: (active + 1) / steps.length }}
          transition={{ type: 'spring', stiffness: 160, damping: 24 }}
          aria-hidden="true"
        />
      </div>
      <ol className="stepper__list">
        {steps.map((s, i) => (
          <li key={s.title} className={`stepper__item${i === active ? ' is-active' : ''}`}>
            <button
              type="button"
              className="stepper__btn"
              onClick={() => setActive(i)}
              aria-current={i === active ? 'step' : undefined}
            >
              <span className="stepper__num">{String(i + 1).padStart(2, '0')}</span>
              <span className="stepper__body">
                <strong>{s.title}</strong>
                <span>{s.desc}</span>
              </span>
            </button>
          </li>
        ))}
      </ol>
    </div>
  )
}

/* Chat preview */
const ChatPreview = ({ messages }) => {
  const reduce = useReducedMotion()
  const ref = useRef(null)
  const inView = useInView(ref, { once: true, amount: 0.4 })
  return (
    <div ref={ref} className="chat-preview" aria-hidden="true">
      {messages.map((m, i) => (
        <motion.div
          key={i}
          className={`chat-msg chat-msg--${m.role}`}
          initial={reduce ? false : { opacity: 0, y: 10 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.4, delay: 0.25 + i * 0.35, ease: [0.4, 0, 0.2, 1] }}
        >
          {m.text}
        </motion.div>
      ))}
      <motion.div
        className="chat-msg chat-msg--typing"
        initial={reduce ? { opacity: 1 } : { opacity: 0 }}
        animate={inView ? { opacity: 1 } : {}}
        transition={{ delay: 0.25 + messages.length * 0.35 }}
      >
        <span /><span /><span />
      </motion.div>
    </div>
  )
}

/* Assessment progress preview */
const AssessmentPreview = () => {
  const reduce = useReducedMotion()
  const ref = useRef(null)
  const inView = useInView(ref, { once: true, amount: 0.4 })
  return (
    <div ref={ref} className="assess-preview">
      <div className="assess-preview__head">
        <span className="assess-preview__label">Tiến độ đánh giá</span>
        <span className="assess-preview__pct">
          <Counter to={72} suffix="%" />
        </span>
      </div>
      <div className="assess-preview__bar">
        <motion.div
          className="assess-preview__fill"
          initial={reduce ? { width: '72%' } : { width: 0 }}
          animate={inView ? { width: '72%' } : {}}
          transition={{ duration: 1.4, ease: [0.2, 0.7, 0.2, 1], delay: 0.15 }}
        />
      </div>
      <div className="assess-preview__chips">
        <span className="assess-chip assess-chip--done">Đại số</span>
        <span className="assess-chip assess-chip--done">Hàm số</span>
        <span className="assess-chip assess-chip--active">Xác suất</span>
        <span className="assess-chip">Thống kê</span>
      </div>
    </div>
  )
}

/* Animated check list */
const CheckList = ({ items }) => {
  const reduce = useReducedMotion()
  const ref = useRef(null)
  const inView = useInView(ref, { once: true, amount: 0.4 })
  return (
    <ul ref={ref} className="check-list">
      {items.map((text, i) => (
        <motion.li
          key={text}
          initial={reduce ? false : { opacity: 0, x: -8 }}
          animate={inView ? { opacity: 1, x: 0 } : {}}
          transition={{ duration: 0.4, delay: 0.1 + i * 0.12, ease: [0.4, 0, 0.2, 1] }}
        >
          <span className="check-list__icon" aria-hidden="true">
            <svg viewBox="0 0 16 16" width="14" height="14">
              <motion.path
                d="M3 8.5 L7 12 L13 4.5"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                initial={reduce ? { pathLength: 1 } : { pathLength: 0 }}
                animate={inView ? { pathLength: 1 } : {}}
                transition={{ duration: 0.55, delay: 0.2 + i * 0.12, ease: [0.2, 0.7, 0.2, 1] }}
              />
            </svg>
          </span>
          <span>{text}</span>
        </motion.li>
      ))}
    </ul>
  )
}

/* ----- Header ----- */
const LandingHeader = ({ menuOpen, setMenuOpen, closeMenu }) => (
  <header className="landing-header">
    <Link to="/" className="landing-logo" aria-label="AI Learning Trang chủ">
      <span className="landing-logo__mark" aria-hidden="true">◆</span>
      <span className="landing-logo__text">AI Learning</span>
    </Link>

    <button
      className={`mobile-menu-btn${menuOpen ? ' is-open' : ''}`}
      type="button"
      aria-expanded={menuOpen}
      aria-controls="primary-nav"
      aria-label={menuOpen ? 'Đóng menu' : 'Mở menu'}
      onClick={() => setMenuOpen((prev) => !prev)}
    >
      <span /><span /><span />
    </button>

    <div className={`nav-overlay${menuOpen ? ' is-open' : ''}`} onClick={closeMenu} />

    <nav
      id="primary-nav"
      className={`primary-nav${menuOpen ? ' is-open' : ''}`}
      aria-label="Điều hướng chính"
      hidden={!menuOpen}
    >
      <div className="primary-nav__inner">
        <p className="primary-nav__eyebrow">Menu</p>
        <a href="#ca-nhan-hoa" onClick={closeMenu}>Cá nhân hóa</a>
        <a href="#ai-tutor" onClick={closeMenu}>AI Tutor</a>
        <a href="#assessment" onClick={closeMenu}>Assessment</a>
        <a href="#giang-vien" onClick={closeMenu}>Giảng viên</a>
        <div className="primary-nav__divider" />
        <Link to="/auth/login" onClick={closeMenu}>Đăng nhập</Link>
        <Link to="/auth/register" onClick={closeMenu} className="primary-nav__cta">
          Bắt đầu miễn phí
        </Link>
      </div>
    </nav>
  </header>
)

/* ----- BentoGroup wrapper for stagger ----- */
const BentoGroup = ({ children, reduce }) => (
  <motion.div
    className="bento-grid"
    variants={reduce ? undefined : containerStagger}
    initial="hidden"
    whileInView="show"
    viewport={{ once: true, amount: 0.12 }}
  >
    {children}
  </motion.div>
)

const BentoScreen = ({ children, reduce }) => (
  <motion.div
    className="bento-grid bento-grid--screen"
    variants={reduce ? undefined : containerStagger}
    initial="hidden"
    animate="show"
  >
    {children}
  </motion.div>
)

/* ----- Page ----- */
const LandingPage = () => {
  const [menuOpen, setMenuOpen] = useState(false)
  const shouldReduceMotion = useReducedMotion()

  useEffect(() => {
    const onEscape = (event) => {
      if (event.key === 'Escape') setMenuOpen(false)
    }
    window.addEventListener('keydown', onEscape)
    return () => window.removeEventListener('keydown', onEscape)
  }, [])

  useEffect(() => {
    document.body.style.overflow = menuOpen ? 'hidden' : ''
    return () => { document.body.style.overflow = '' }
  }, [menuOpen])

  const closeMenu = () => setMenuOpen(false)
  const r = shouldReduceMotion

  return (
    <div className="landing">
      <LandingHeader menuOpen={menuOpen} setMenuOpen={setMenuOpen} closeMenu={closeMenu} />

      <main className="landing-main" id="ca-nhan-hoa">
        <section className="bento" aria-labelledby="bento-heading">
          <h2 className="sr-only" id="bento-heading">AI learning bento layout</h2>

          {/* ---------- Hero row ---------- */}
          <BentoScreen reduce={r}>
            <Tile className="bento-tile--hero tone-ink deco-dots" reduce={r}>
              <div className="hero-aurora" aria-hidden="true" />
              <p className="tile-kicker">AI Learning Platform</p>
              <motion.h1
                className="tile-title tile-title--xxl hero-headline"
                variants={r ? undefined : containerStagger}
                initial="hidden"
                animate="show"
              >
                {'Học tập cá nhân hóa bằng AI, từ đánh giá năng lực đến lộ trình hàng ngày.'
                  .split(' ')
                  .map((w, i) => (
                    <motion.span
                      key={`${w}-${i}`}
                      className="hero-headline__w"
                      variants={r ? undefined : wordVariants}
                    >
                      {w}
                    </motion.span>
                  ))}
              </motion.h1>
              <p className="tile-copy">
                Hệ thống hiểu mục tiêu, gợi ý bài học phù hợp và hỗ trợ ngay khi bạn mắc kẹt.
              </p>
              <div className="tile-actions">
                <Link to="/auth/register"><Button size="lg">Bắt đầu miễn phí</Button></Link>
                <Link to="/auth/login" className="text-link">Tôi đã có tài khoản</Link>
              </div>
            </Tile>

            <Tile className="bento-tile--media-tall tone-paper-2" reduce={r}>
              <MediaPlaceholder title="Ảnh 01" subtitle="Dashboard học tập cá nhân" ratio="portrait" />
            </Tile>

            <Tile className="bento-tile--chips tone-cream tile-stack-top" reduce={r}>
              <p className="tile-kicker">Mới cho bạn</p>
              <div className="chip-list chip-list--interactive">
                <button type="button"><span className="chip-dot" aria-hidden="true" />Đánh giá năng lực</button>
                <button type="button"><span className="chip-dot" aria-hidden="true" />AI Tutor ngữ cảnh</button>
                <button type="button"><span className="chip-dot" aria-hidden="true" />Lộ trình tuần</button>
              </div>
            </Tile>

            <Tile className="bento-tile--stat-a tone-honey" reduce={r}>
              <p className="tile-kicker">Cá nhân hóa</p>
              <p className="tile-stat"><Counter to={1} />:<Counter to={1} /></p>
              <p className="tile-copy tile-copy--sm">Lộ trình riêng cho từng học viên theo mục tiêu cá nhân.</p>
            </Tile>
          </BentoScreen>

          {/* ---------- Main bento ---------- */}
          <BentoGroup reduce={r}>
            <Tile className="bento-tile--assessment tone-paper deco-grid" reduce={r} id="assessment">
              <p className="tile-kicker">Điểm khởi đầu rõ ràng</p>
              <h3 className="tile-title">Assessment xác định chính xác phần bạn cần học.</h3>
              <p className="tile-copy">Không bắt học lại từ đầu. Bạn nhận kế hoạch học tập theo năng lực thật.</p>
              <AssessmentPreview />
            </Tile>

            <Tile className="bento-tile--aichat tone-ink" reduce={r} id="ai-tutor">
              <p className="tile-kicker">AI Tutor</p>
              <h3 className="tile-title">Hỏi đúng bài đang học, nhận phản hồi ngay.</h3>
              <ChatPreview messages={CHAT_PREVIEW} />
            </Tile>

            <Tile className="bento-tile--roadmap tone-clay tile-stack-top" reduce={r}>
              <p className="tile-kicker">Quy trình học tập</p>
              <h3 className="tile-title">Đánh giá → Lộ trình → Bài học → Ôn tập</h3>
              <RoadmapStepper steps={FLOW_STEPS} />
            </Tile>

            <Tile className="bento-tile--capabilities tone-cream tile-stack-top" reduce={r}>
              <p className="tile-kicker">Khả năng cốt lõi</p>
              <ul className="feature-list">
                {CORE_FEATURES.map((item) => (
                  <li key={item.title}>
                    <span className="feature-icon" aria-hidden="true">{item.icon}</span>
                    <strong>{item.title}</strong>
                    <span>{item.desc}</span>
                  </li>
                ))}
              </ul>
            </Tile>

            <Tile className="bento-tile--media-wide tone-paper-2" reduce={r}>
              <MediaPlaceholder title="Ảnh 04" subtitle="Lộ trình học cá nhân hóa" ratio="wide" />
            </Tile>

            <Tile className="bento-tile--instructor tone-sage" reduce={r} id="giang-vien">
              <p className="tile-kicker">Dành cho giảng viên</p>
              <h3 className="tile-title">Soạn nội dung một lần, AI hỗ trợ quiz và theo dõi tiến độ lớp.</h3>
              <MediaPlaceholder title="Ảnh 05" subtitle="Giao diện quản lý lớp/khóa" ratio="landscape" />
            </Tile>

            <Tile className="bento-tile--trust tone-ink deco-dots tile-stack-top" reduce={r}>
              <p className="tile-kicker">Tin cậy</p>
              <h3 className="tile-title">Dữ liệu học tập tách biệt và bảo mật.</h3>
              <CheckList items={TRUST_ITEMS} />
              <div className="trust-meta">
                <div>
                  <strong><Counter to={256} /></strong>
                  <span>bit encryption</span>
                </div>
                <div>
                  <strong><Counter to={99} suffix=".9%" /></strong>
                  <span>uptime SLA</span>
                </div>
              </div>
            </Tile>

            <Tile className="bento-tile--faq tone-paper tile-stack-top" reduce={r}>
              <p className="tile-kicker">Câu hỏi nhanh</p>
              <Accordion items={FAQ_ITEMS} />
            </Tile>

            <Tile className="bento-tile--community tone-paper-2" reduce={r}>
              <MediaPlaceholder title="Ảnh 06" subtitle="Hình ảnh cộng đồng học viên" ratio="landscape" />
              <p className="tile-copy">“Lộ trình rõ ràng hơn hẳn và AI giải thích đúng chỗ mình vướng.”</p>
              <p className="tile-attribution">— Học viên Data Analytics</p>
            </Tile>

            <Tile className="bento-tile--cta tone-honey deco-stripes" reduce={r}>
              <h3 className="tile-title tile-title--xl">Sẵn sàng học theo cách của riêng bạn?</h3>
              <p className="tile-copy">Tạo tài khoản để bắt đầu bài đánh giá năng lực và nhận lộ trình cá nhân ngay hôm nay.</p>
              <div className="tile-actions">
                <Link to="/auth/register"><Button variant="secondary" size="lg">Tạo tài khoản</Button></Link>
                <Link to="/auth/login" className="text-link">Đăng nhập</Link>
              </div>
            </Tile>

            <Tile className="bento-tile--footer" reduce={r}>
              <div className="footer-row">
                <div className="landing-logo">
                  <span className="landing-logo__mark" aria-hidden="true">◆</span>
                  <span className="landing-logo__text">AI Learning</span>
                </div>
                <nav className="footer-links" aria-label="Liên kết footer">
                  <Link to="/dashboard/courses">Khóa học</Link>
                  <Link to="/dashboard/assessment">Assessment</Link>
                  <Link to="/dashboard/chat">AI Chat</Link>
                  <Link to="/auth/login">Đăng nhập</Link>
                  <Link to="/auth/register">Đăng ký</Link>
                </nav>
                <p className="footer-copy">© {new Date().getFullYear()} AI Learning Platform</p>
              </div>
            </Tile>
          </BentoGroup>
        </section>
      </main>
    </div>
  )
}

export default LandingPage
