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

const AI_RESPONSE = 'Hàm cleanup giúp tránh memory leak khi component bị unmount trước khi API trả về.'

const CHIP_LABELS = ['Đánh giá năng lực', 'AI Tutor ngữ cảnh', 'Lộ trình tuần']
const CHIP_STORIES = [
  'Hà, 23 tuổi, mất 12 phút. Nhận ra mình ổn về lý thuyết nhưng yếu ở bài tập ứng dụng.',
  'Mắc kẹt ở bài 4. Hỏi thẳng đoạn code. Hiểu ngay. Không cần Google.',
  'Tuần này bận. AI rút xuống 3 bài thay vì 7. Vẫn đúng hướng.',
]

const HEATMAP_OPACITIES = [
  0.3, 0.7, 0.2, 0.9, 0.5, 0.1, 0.8, 0.4,
  0.6, 0.3, 1.0, 0.2, 0.7, 0.5, 0.3, 0.9,
  0.1, 0.8, 0.4, 0.6, 0.2, 0.9, 0.5, 0.1,
  0.7, 0.4, 0.6, 0.3, 0.8, 0.2, 1.0, 0.5,
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

/* Chat preview — looping state machine */
const ChatPreview = ({ messages }) => {
  const reduce = useReducedMotion()
  const containerRef = useRef(null)
  const inView = useInView(containerRef, { once: false, amount: 0.4 })
  const [phase, setPhase] = useState(-1)
  const [visibleCount, setVisibleCount] = useState(0)
  const [showTyping, setShowTyping] = useState(false)
  const [showResponse, setShowResponse] = useState(false)
  const [scrollingOut, setScrollingOut] = useState(false)
  const responseRef = useRef(null)
  const timerRef = useRef(null)
  const wordTimerRef = useRef(null)
  const startedRef = useRef(false)

  const clearTimers = () => {
    if (timerRef.current) { clearTimeout(timerRef.current); timerRef.current = null }
    if (wordTimerRef.current) { clearTimeout(wordTimerRef.current); wordTimerRef.current = null }
  }

  const revealWords = () => {
    const words = AI_RESPONSE.split(' ')
    let idx = 0
    const tick = () => {
      idx++
      if (responseRef.current) responseRef.current.textContent = words.slice(0, idx).join(' ')
      if (idx >= words.length) { setPhase(6); return }
      const remaining = words.length - idx
      const delay = remaining <= 3 ? 120 + Math.random() * 40 : 50 + Math.random() * 30
      wordTimerRef.current = setTimeout(tick, delay)
    }
    tick()
  }

  /* Start loop when first in view */
  useEffect(() => {
    if (reduce || !inView) return
    if (!startedRef.current) { startedRef.current = true; setPhase(0) }
  }, [inView, reduce])

  /* Phase machine */
  useEffect(() => {
    if (reduce || phase < 0) return
    clearTimers()

    const delays = [500, 700, 500, 600, 1400, 0, 2000]
    const actions = {
      0: () => { setVisibleCount(1); setPhase(1) },
      1: () => { setVisibleCount(2); setPhase(2) },
      2: () => { setVisibleCount(3); setPhase(3) },
      3: () => { setShowTyping(true); setPhase(4) },
      4: () => { setShowTyping(false); setShowResponse(true); setPhase(5); revealWords() },
      5: () => {},
      6: () => {
        setScrollingOut(true)
        timerRef.current = setTimeout(() => {
          setScrollingOut(false); setVisibleCount(0)
          setShowTyping(false); setShowResponse(false)
          if (responseRef.current) responseRef.current.textContent = ''
          setPhase(0)
        }, 800)
      },
    }

    if (phase === 5) return
    timerRef.current = setTimeout(() => actions[phase]?.(), delays[phase] || 0)
    return clearTimers
  }, [phase, reduce])

  /* Reduced motion: static display */
  if (reduce) {
    return (
      <div ref={containerRef} className="chat-preview" aria-hidden="true">
        {messages.map((m, i) => (
          <div key={i} className={`chat-msg chat-msg--${m.role}`}>{m.text}</div>
        ))}
        <div className="chat-msg chat-msg--ai">{AI_RESPONSE}</div>
      </div>
    )
  }

  return (
    <div
      ref={containerRef}
      className={`chat-preview${scrollingOut ? ' chat-preview--scroll-out' : ''}`}
      aria-hidden="true"
    >
      <AnimatePresence>
        {visibleCount >= 1 && (
          <motion.div
            key="m0"
            className="chat-msg chat-msg--user"
            initial={{ opacity: 0, y: 12, scale: 0.92 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, transition: { duration: 0.15 } }}
            transition={{ type: 'spring', stiffness: 300, damping: 12 }}
          >{messages[0].text}</motion.div>
        )}
        {visibleCount >= 2 && (
          <motion.div
            key="m1"
            className="chat-msg chat-msg--ai"
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, transition: { duration: 0.15 } }}
            transition={{ duration: 0.35, ease: 'linear' }}
          >{messages[1].text}</motion.div>
        )}
        {visibleCount >= 3 && (
          <motion.div
            key="m2"
            className="chat-msg chat-msg--user"
            initial={{ opacity: 0, y: 12, scale: 0.92 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, transition: { duration: 0.15 } }}
            transition={{ type: 'spring', stiffness: 300, damping: 12 }}
          >{messages[2].text}</motion.div>
        )}
        {showTyping && (
          <motion.div
            key="typing"
            className="chat-msg chat-msg--typing"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
          ><span /><span /><span /></motion.div>
        )}
        {showResponse && (
          <motion.div
            key="response"
            className="chat-msg chat-msg--ai"
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, transition: { duration: 0.15 } }}
            transition={{ duration: 0.35, ease: 'linear' }}
          ><span ref={responseRef} /></motion.div>
        )}
      </AnimatePresence>
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

/* ----- Inline data visualizations ----- */

/* Portrait — concentric arcs (dashboard) */
const DashboardViz = () => (
  <div className="viz-arcs" aria-hidden="true">
    <svg viewBox="0 0 200 260" fill="none">
      <g transform="translate(75, 90)">
        <circle
          r="90" stroke="var(--c-honey)" strokeWidth="6"
          strokeDasharray="407.15 158.34" transform="rotate(-90)"
        />
        <circle
          r="68" stroke="var(--c-clay)" strokeWidth="6"
          strokeDasharray="234.99 192.27" transform="rotate(-90)"
        />
        <circle
          r="46" stroke="var(--c-sage)" strokeWidth="6"
          strokeDasharray="254.35 34.68" transform="rotate(-90)"
        />
      </g>
    </svg>
  </div>
)

/* Wide — bezier curve with stage dots (roadmap) */
const RoadmapViz = () => (
  <div className="viz-curve" aria-hidden="true">
    <svg viewBox="0 0 500 160" preserveAspectRatio="xMidYMid meet" fill="none">
      <path
        d="M0,130 C31,130 31,30 62,30 C93,30 93,130 125,130 C156,130 156,30 187,30 C218,30 218,130 250,130 C281,130 281,30 312,30 C343,30 343,130 375,130 C406,130 406,30 437,30 C468,30 468,130 500,130"
        stroke="var(--c-honey)" strokeWidth="1.5"
      />
      <circle cx="62"  cy="30" r="4" fill="var(--c-honey)" />
      <circle cx="187" cy="30" r="6" fill="var(--c-honey)" className="viz-curve__dot-active" />
      <circle cx="312" cy="30" r="4" fill="var(--c-honey)" />
      <circle cx="437" cy="30" r="4" fill="var(--c-honey)" />
    </svg>
  </div>
)

/* Landscape — 8×4 heatmap grid (instructor) */
const HeatmapGrid = () => (
  <div className="viz-heatmap" aria-hidden="true">
    {HEATMAP_OPACITIES.map((op, i) => (
      <span key={i} className="heatmap-cell" style={{ opacity: op }} />
    ))}
  </div>
)

/* Full-bleed — animated data flow network (capabilities) */
const CapabilitiesViz = () => (
  <div className="viz-network" aria-hidden="true">
    <svg viewBox="0 0 600 400" fill="none" preserveAspectRatio="xMidYMid slice">
      {/* Flow paths — each represents a capability stream */}
      <path
        d="M-20,200 C80,200 130,60 230,60 S380,200 480,200 S560,100 620,100"
        stroke="var(--c-honey)" strokeWidth="1.5" className="viz-flow viz-flow--1"
      />
      <path
        d="M-20,300 C60,300 100,340 200,340 S340,100 440,100 S560,300 620,300"
        stroke="var(--c-clay)" strokeWidth="1.5" className="viz-flow viz-flow--2"
      />
      <path
        d="M-20,100 C80,100 180,360 300,200 S460,40 620,200"
        stroke="var(--c-sage)" strokeWidth="1.5" className="viz-flow viz-flow--3"
      />
      <path
        d="M-20,360 C130,360 180,200 300,200 S470,360 620,60"
        stroke="var(--c-honey-2)" strokeWidth="1" opacity="0.45" className="viz-flow viz-flow--4"
      />
      {/* Connector threads */}
      <path
        d="M230,60 Q265,130 300,200" stroke="var(--c-line-2)" strokeWidth="0.8"
      />
      <path
        d="M440,100 Q370,150 300,200" stroke="var(--c-line-2)" strokeWidth="0.8"
      />
      {/* Intersection nodes */}
      <circle cx="230" cy="60"  r="6" fill="var(--c-honey)" className="viz-node viz-node--1" />
      <circle cx="300" cy="200" r="9" fill="var(--c-clay)"  className="viz-node viz-node--2" />
      <circle cx="440" cy="100" r="5" fill="var(--c-sage)"  className="viz-node viz-node--3" />
      <circle cx="200" cy="340" r="5" fill="var(--c-honey)" className="viz-node viz-node--4" />
      {/* Small accent dots */}
      <circle cx="480" cy="200" r="3" fill="var(--c-honey)" opacity="0.5" />
      <circle cx="100" cy="200" r="3" fill="var(--c-clay)" opacity="0.4" />
      <circle cx="380" cy="320" r="2.5" fill="var(--c-sage)" opacity="0.4" />
    </svg>
  </div>
)
/* Chip tile with micro-story morph */
const ChipListTile = () => {
  const reduce = useReducedMotion()
  const [activeChip, setActiveChip] = useState(-1)
  const storyRef = useRef(null)
  const charTimerRef = useRef(null)

  const handleClick = (idx) => {
    if (charTimerRef.current) { clearInterval(charTimerRef.current); charTimerRef.current = null }

    if (activeChip === idx) { setActiveChip(-1); return }
    setActiveChip(idx)

    /* character-by-character reveal via direct DOM */
    if (reduce) return
    const text = CHIP_STORIES[idx]
    let pos = 0
    /* clear previous text — will be set once AnimatePresence renders the node */
    const startReveal = () => {
      if (!storyRef.current) {
        /* wait for DOM node from AnimatePresence */
        requestAnimationFrame(startReveal)
        return
      }
      storyRef.current.textContent = ''
      charTimerRef.current = setInterval(() => {
        pos++
        if (storyRef.current) storyRef.current.textContent = text.slice(0, pos)
        if (pos >= text.length && charTimerRef.current) clearInterval(charTimerRef.current)
      }, 30)
    }
    requestAnimationFrame(startReveal)
  }

  useEffect(() => () => {
    if (charTimerRef.current) clearInterval(charTimerRef.current)
  }, [])

  return (
    <>
      <p className="tile-kicker">Mới cho bạn</p>
      <div className="chip-list chip-list--interactive">
        {CHIP_LABELS.map((label, i) => (
          <button
            key={label}
            type="button"
            className={activeChip === i ? 'is-active' : ''}
            onClick={() => handleClick(i)}
          >
            <span className="chip-dot" aria-hidden="true" />{label}
          </button>
        ))}
      </div>
      <AnimatePresence mode="wait">
        {activeChip >= 0 ? (
          <motion.p
            key={`story-${activeChip}`}
            className="chip-story"
            initial={reduce ? false : { opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.22 }}
          >
            <span ref={storyRef}>{reduce ? CHIP_STORIES[activeChip] : ''}</span>
          </motion.p>
        ) : null}
      </AnimatePresence>
    </>
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
              <DashboardViz />
            </Tile>

            <Tile className="bento-tile--chips tone-cream tile-stack-top" reduce={r}>
              <ChipListTile />
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

            <Tile className="bento-tile--capabilities tone-cream" reduce={r}>
              <CapabilitiesViz />
            </Tile>

            <Tile className="bento-tile--media-wide tone-paper-2" reduce={r}>
              <RoadmapViz />
            </Tile>

            <Tile className="bento-tile--instructor tone-sage" reduce={r} id="giang-vien">
              <p className="tile-kicker">Dành cho giảng viên</p>
              <h3 className="tile-title">Soạn nội dung một lần, AI hỗ trợ quiz và theo dõi tiến độ lớp.</h3>
              <HeatmapGrid />
            </Tile>

            <Tile className="bento-tile--trust tone-ink deco-dots tile-stack-top" reduce={r}>
              <p className="tile-kicker">Tin cậy</p>
              <h3 className="tile-title">Dữ liệu học tập tách biệt và bảo mật.</h3>
              <img
                src="/landing/trust-security.png"
                alt="Mã hóa dữ liệu đầu cuối, bảo mật 256-bit, 99.9% uptime"
                className="tile-hero-img tile-hero-img--dark"
                loading="lazy"
              />
            </Tile>

            <Tile className="bento-tile--faq tone-paper tile-stack-top" reduce={r}>
              <p className="tile-kicker">Câu hỏi nhanh</p>
              <Accordion items={FAQ_ITEMS} />
            </Tile>

            <Tile className="bento-tile--community tone-paper-2" reduce={r}>
              <img
                src="/landing/community-learners.png"
                alt="Cộng đồng học viên AI Learning"
                className="community-img"
                loading="lazy"
              />
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
                  <Link to="/terms">Điều khoản</Link>
                  <Link to="/privacy">Bảo mật</Link>
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
