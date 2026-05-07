import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { motion, useReducedMotion } from 'framer-motion'
import { AnimatePresence } from 'framer-motion'
import toast from 'react-hot-toast'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import analyticsService from '@services/analyticsService'
import StateView from '@components/ui/StateView'
import './ProgressPage.css'

/* ─── SVG Icons ───────────────────────────────────── */
const BookOpenIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/>
  </svg>
)

const LessonIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
    <polyline points="14 2 14 8 20 8"/>
    <line x1="9" y1="13" x2="15" y2="13"/><line x1="9" y1="17" x2="13" y2="17"/>
  </svg>
)

const QuizIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="10"/>
    <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/><line x1="12" y1="17" x2="12.01" y2="17"/>
  </svg>
)

const ClockIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>
  </svg>
)

const FlameIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <path d="M8.5 14.5A2.5 2.5 0 0 0 11 17h2a2.5 2.5 0 0 0 0-5H7C5.34 12 4 10.66 4 9c0-4 3-6 6-6 0 4 3.5 6 3.5 9.5"/>
  </svg>
)

const TrophyIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="8 17 12 21 16 17"/>
    <path d="M5 3H19V11A7 7 0 0 1 12 18 7 7 0 0 1 5 11V3Z"/>
    <path d="M5 3H2V8A3 3 0 0 0 5 11"/>
    <path d="M19 3H22V8A3 3 0 0 1 19 11"/>
    <line x1="9" y1="21" x2="15" y2="21"/>
  </svg>
)

const TargetIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>
  </svg>
)

const StarIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
  </svg>
)

const CheckCircleIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
    <polyline points="22 4 12 14.01 9 11.01"/>
  </svg>
)

/* ─── Custom Recharts Tooltip ────────────────────── */
const ChartTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null
  const d = label ? new Date(label).toLocaleDateString('vi-VN') : ''
  return (
    <div className="pp-tooltip">
      <p className="pp-tooltip__date">{d}</p>
      {payload.map((p, i) => (
        <p key={i} className="pp-tooltip__item" style={{ color: p.color }}>
          {p.name}: <strong>{p.value}</strong>
        </p>
      ))}
    </div>
  )
}

/* ─── Achievement icons map ─────────────────────── */
const ACHIEVEMENT_DEF = [
  { id: 'lesson1', Icon: TargetIcon, title: 'Hoàn thành bài đầu tiên', check: (s) => (s?.lessons_completed || 0) >= 1 },
  { id: 'quiz5',   Icon: QuizIcon,   title: 'Làm 5 quiz',              check: (s) => (s?.quizzes_taken    || 0) >= 5 },
  { id: 'streak7', Icon: FlameIcon,  title: '7 ngày liên tục',         check: (s) => (s?.best_streak      || 0) >= 7 },
  { id: 'hours10', Icon: ClockIcon,  title: 'Học 10 giờ',              check: (s) => (s?.total_study_hours|| 0) >= 10 },
  { id: 'course1', Icon: BookOpenIcon, title: 'Hoàn thành 1 khóa học', check: (s) => (s?.courses_completed|| 0) >= 1 },
  { id: 'quiz90',  Icon: StarIcon,   title: 'Điểm quiz 90+',           check: (s) => (s?.avg_quiz_score   || 0) >= 90 },
]

/**
 * ProgressPage — Trang tiến độ học tập
 * Route: /dashboard/progress
 * API: GET /analytics/learning-stats → analyticsService.getLearningStats — unchanged
 *      GET /analytics/progress-chart → analyticsService.getProgressChart — unchanged
 */
const ProgressPage = () => {
  const [stats, setStats] = useState(null)
  const [chart, setChart] = useState(null)
  const [loading, setLoading] = useState(true)
  const shouldReduce = useReducedMotion()

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true)
        const [statsData, chartData] = await Promise.allSettled([
          analyticsService.getLearningStats(),
          analyticsService.getProgressChart(),
        ])
        if (statsData.status === 'fulfilled') setStats(statsData.value)
        if (chartData.status === 'fulfilled') setChart(chartData.value)
      } catch {
        toast.error('Không thể tải dữ liệu tiến độ')
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [])

  if (loading) return <div className="pp-page"><StateView type="loading" message="Đang tải tiến độ…" /></div>

  const progress = Math.round(stats?.overall_progress || 0)
  const circumference = 2 * Math.PI * 42 // r=42

  const fadeUp = { hidden: { opacity: 0, y: 20 }, visible: { opacity: 1, y: 0 } }
  const stagger = { visible: { transition: { staggerChildren: shouldReduce ? 0 : 0.08 } } }

  return (
    <div className="pp-page">
      {/* ── Header ── */}
      <motion.div className="pp-header" initial="hidden" animate="visible" variants={fadeUp} transition={{ duration: 0.5 }}>
        <div className="pp-header__eyebrow">Hành trình học tập</div>
        <h1 className="pp-header__title">Tiến độ của bạn</h1>
        <p className="pp-header__sub">Theo dõi từng bước và thành tựu trên con đường tri thức</p>
      </motion.div>

      {/* ── Stat cards ── */}
      <motion.div className="pp-stats" initial="hidden" animate="visible" variants={stagger}>
        {/* Primary: overall progress ring */}
        <motion.div className="pp-stat pp-stat--primary" variants={fadeUp}>
          <div className="pp-ring-wrap">
            <svg viewBox="0 0 100 100" className="pp-ring">
              <circle cx="50" cy="50" r="42" className="pp-ring__bg" />
              <motion.circle
                cx="50" cy="50" r="42"
                className="pp-ring__fill"
                initial={{ strokeDashoffset: circumference }}
                animate={{ strokeDashoffset: circumference - (progress / 100) * circumference }}
                transition={{ duration: shouldReduce ? 0 : 1.2, ease: 'easeOut', delay: 0.4 }}
              />
            </svg>
            <span className="pp-ring__val">{progress}%</span>
          </div>
          <span className="pp-stat__label">Tiến độ tổng thể</span>
        </motion.div>

        {/* Secondary stats */}
        {[
          { Icon: BookOpenIcon, value: stats?.courses_enrolled || 0, label: 'Khóa học đăng ký', sub: `${stats?.courses_completed || 0} hoàn thành` },
          { Icon: LessonIcon,   value: stats?.lessons_completed || 0, label: 'Bài học xong', sub: `/ ${stats?.total_lessons || 0} tổng` },
          { Icon: QuizIcon,     value: stats?.quizzes_taken || 0, label: 'Quiz đã làm', sub: `TB: ${stats?.avg_quiz_score || 0}%` },
          { Icon: ClockIcon,    value: `${stats?.total_study_hours || 0}h`, label: 'Tổng giờ học', sub: `~${stats?.avg_daily_hours || 0}h/ngày` },
          { Icon: FlameIcon,    value: stats?.current_streak || 0, label: 'Ngày liên tục', sub: `Kỷ lục: ${stats?.best_streak || 0} ngày`, flame: true },
        ].map(({ Icon, value, label, sub, flame }) => (
          <motion.div key={label} className={`pp-stat ${flame ? 'pp-stat--flame' : ''}`} variants={fadeUp}>
            <div className="pp-stat__icon-wrap">
              <Icon />
            </div>
            <span className="pp-stat__value">{value}</span>
            <span className="pp-stat__label">{label}</span>
            <span className="pp-stat__sub">{sub}</span>
          </motion.div>
        ))}
      </motion.div>

      {/* ── Chart ── */}
      <AnimatePresence>
        {chart?.chart_data?.length > 0 && (
          <motion.div
            className="pp-section"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2, duration: 0.5 }}
          >
            <div className="pp-section__header">
              <h2 className="pp-section__title">Biểu đồ tiến độ</h2>
              {chart.summary && (
                <div className="pp-chart-summary">
                  <span>{chart.summary.total_lessons || 0} bài</span>
                  <span className="pp-dot">·</span>
                  <span>{chart.summary.total_hours || 0} giờ</span>
                  <span className="pp-dot">·</span>
                  <span>TB {chart.summary.avg_per_day || 0} bài/ngày</span>
                </div>
              )}
            </div>
            <div className="pp-chart">
              <ResponsiveContainer width="100%" height={260}>
                <LineChart data={chart.chart_data} margin={{ top: 5, right: 16, left: 0, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--border-light, #f1f5f9)" />
                  <XAxis
                    dataKey="date"
                    tick={{ fontSize: 11, fill: 'var(--text-muted)' }}
                    tickFormatter={(d) => { const dt = new Date(d); return `${dt.getDate()}/${dt.getMonth() + 1}` }}
                    axisLine={false}
                    tickLine={false}
                  />
                  <YAxis
                    tick={{ fontSize: 11, fill: 'var(--text-muted)' }}
                    axisLine={false}
                    tickLine={false}
                    width={28}
                  />
                  <Tooltip content={<ChartTooltip />} cursor={{ stroke: 'var(--border-color)', strokeWidth: 1, strokeDasharray: '4 4' }} />
                  <Line
                    type="monotone"
                    dataKey="lessons_completed"
                    name="Bài học"
                    stroke="var(--gold, #c9a84c)"
                    strokeWidth={2.5}
                    dot={false}
                    activeDot={{ r: 5, stroke: 'var(--gold)', fill: 'var(--bg-card)' }}
                  />
                  <Line
                    type="monotone"
                    dataKey="hours_spent"
                    name="Giờ học"
                    stroke="var(--primary, #6366f1)"
                    strokeWidth={2}
                    dot={false}
                    activeDot={{ r: 4, stroke: 'var(--primary)', fill: 'var(--bg-card)' }}
                    strokeDasharray="5 3"
                  />
                </LineChart>
              </ResponsiveContainer>
              <div className="pp-chart-legend">
                <span className="pp-legend-item"><span className="pp-legend-dot pp-legend-dot--gold" />Bài học</span>
                <span className="pp-legend-item"><span className="pp-legend-dot pp-legend-dot--purple" />Giờ học</span>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* ── Courses in progress ── */}
      <motion.div
        className="pp-section"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.28, duration: 0.5 }}
      >
        <div className="pp-section__header">
          <h2 className="pp-section__title">Khóa học đang học</h2>
          <Link to="/dashboard/my-courses" className="pp-section__link">Xem tất cả →</Link>
        </div>

        {(stats?.course_progress || []).length > 0 ? (
          <div className="pp-courses">
            {stats.course_progress.map((course, i) => {
              const pct = Math.round(course.progress || 0)
              const barClass = pct >= 80 ? 'pp-bar-fill--green' : pct >= 40 ? 'pp-bar-fill--purple' : 'pp-bar-fill--gold'
              return (
                <Link key={i} to={`/dashboard/courses/${course.course_id}/modules`} className="pp-course">
                  <div className="pp-course__info">
                    <h4 className="pp-course__title">{course.title}</h4>
                    <p className="pp-course__meta">
                      {course.completed_lessons || 0}/{course.total_lessons || 0} bài học
                      <span className="pp-dot">·</span>
                      {course.completed_modules || 0}/{course.total_modules || 0} modules
                    </p>
                  </div>
                  <div className="pp-course__bar-area">
                    <div className="pp-bar">
                      <motion.div
                        className={`pp-bar-fill ${barClass}`}
                        initial={{ width: 0 }}
                        animate={{ width: `${pct}%` }}
                        transition={{ duration: shouldReduce ? 0 : 0.8, delay: i * 0.05, ease: 'easeOut' }}
                      />
                    </div>
                    <span className="pp-course__pct">{pct}%</span>
                  </div>
                </Link>
              )
            })}
          </div>
        ) : (
          <StateView
            type="empty"
            icon={<BookOpenIcon />}
            title="Chưa có khóa học nào"
            message="Đăng ký khóa học để bắt đầu hành trình"
            actionLabel="Khám phá khóa học"
            actionHref="/dashboard/courses"
          />
        )}
      </motion.div>

      {/* ── Achievements ── */}
      <motion.div
        className="pp-section"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.36, duration: 0.5 }}
      >
        <div className="pp-section__header">
          <h2 className="pp-section__title">Thành tựu</h2>
          <span className="pp-achieve-count">
            {ACHIEVEMENT_DEF.filter(a => a.check(stats)).length}/{ACHIEVEMENT_DEF.length} mở khóa
          </span>
        </div>
        <div className="pp-achievements">
          {ACHIEVEMENT_DEF.map(({ id, Icon, title, check }) => {
            const unlocked = check(stats)
            return (
              <motion.div
                key={id}
                className={`pp-achieve ${unlocked ? 'pp-achieve--unlocked' : ''}`}
                whileHover={!shouldReduce ? { y: -3 } : {}}
              >
                <div className="pp-achieve__icon">
                  <Icon />
                  {unlocked && (
                    <div className="pp-achieve__check">
                      <CheckCircleIcon />
                    </div>
                  )}
                </div>
                <span className="pp-achieve__title">{title}</span>
              </motion.div>
            )
          })}
        </div>
      </motion.div>
    </div>
  )
}

export default ProgressPage
