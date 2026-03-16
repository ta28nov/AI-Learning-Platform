import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import toast from 'react-hot-toast'
import analyticsService from '@services/analyticsService'
import './ProgressPage.css'

/**
 * ProgressPage - Trang tien do hoc tap chi tiet
 * Route: /dashboard/progress
 * API: GET /analytics/student/learning-stats, GET /analytics/student/progress-chart
 */
const ProgressPage = () => {
  const [stats, setStats] = useState(null)
  const [chart, setChart] = useState(null)
  const [loading, setLoading] = useState(true)

  // Lay du lieu analytics khi mount
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true)
        const [statsData, chartData] = await Promise.allSettled([
          analyticsService.getLearningStats(),
          analyticsService.getProgressChart()
        ])
        if (statsData.status === 'fulfilled') setStats(statsData.value)
        if (chartData.status === 'fulfilled') setChart(chartData.value)
      } catch (error) {
        toast.error('Khong the tai du lieu tien do')
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [])

  const fadeUp = { hidden: { opacity: 0, y: 20 }, visible: { opacity: 1, y: 0 } }
  const stagger = { visible: { transition: { staggerChildren: 0.1 } } }

  if (loading) {
    return (
      <div className="progress-page">
        <div className="progress-skeleton__grid">
          {[1, 2, 3, 4].map(i => <div key={i} className="progress-skeleton" />)}
        </div>
        <div className="progress-skeleton progress-skeleton--lg" />
      </div>
    )
  }

  return (
    <div className="progress-page">
      {/* Header */}
      <motion.div
        className="progress-header"
        initial="hidden"
        animate="visible"
        variants={fadeUp}
        transition={{ duration: 0.4 }}
      >
        <h1 className="progress-header__title">Tien do hoc tap</h1>
        <p className="progress-header__sub">Theo doi qua trinh va thanh tuu cua ban</p>
      </motion.div>

      {/* Stat cards */}
      <motion.div
        className="progress-stats"
        initial="hidden"
        animate="visible"
        variants={stagger}
      >
        <motion.div className="progress-stat progress-stat--primary" variants={fadeUp}>
          <div className="progress-stat__ring">
            <svg viewBox="0 0 100 100" className="progress-stat__svg">
              <circle cx="50" cy="50" r="42" className="progress-stat__bg-ring" />
              <circle
                cx="50" cy="50" r="42"
                className="progress-stat__fill-ring"
                style={{ strokeDasharray: `${(stats?.overall_progress || 0) * 2.64} 264` }}
              />
            </svg>
            <span className="progress-stat__ring-value">{Math.round(stats?.overall_progress || 0)}%</span>
          </div>
          <span className="progress-stat__label">Tien do tong the</span>
        </motion.div>

        <motion.div className="progress-stat" variants={fadeUp}>
          <span className="progress-stat__icon">📚</span>
          <span className="progress-stat__value">{stats?.courses_enrolled || 0}</span>
          <span className="progress-stat__label">Khoa hoc dang ky</span>
          <span className="progress-stat__sub">{stats?.courses_completed || 0} hoan thanh</span>
        </motion.div>

        <motion.div className="progress-stat" variants={fadeUp}>
          <span className="progress-stat__icon">📖</span>
          <span className="progress-stat__value">{stats?.lessons_completed || 0}</span>
          <span className="progress-stat__label">Bai hoc hoan thanh</span>
          <span className="progress-stat__sub">/ {stats?.total_lessons || 0} tong</span>
        </motion.div>

        <motion.div className="progress-stat" variants={fadeUp}>
          <span className="progress-stat__icon">📝</span>
          <span className="progress-stat__value">{stats?.quizzes_taken || 0}</span>
          <span className="progress-stat__label">Quiz da lam</span>
          <span className="progress-stat__sub">TB: {stats?.avg_quiz_score || 0}%</span>
        </motion.div>

        <motion.div className="progress-stat" variants={fadeUp}>
          <span className="progress-stat__icon">⏱</span>
          <span className="progress-stat__value">{stats?.total_study_hours || 0}h</span>
          <span className="progress-stat__label">Tong gio hoc</span>
          <span className="progress-stat__sub">~{stats?.avg_daily_hours || 0}h/ngay</span>
        </motion.div>

        <motion.div className="progress-stat" variants={fadeUp}>
          <span className="progress-stat__icon">🔥</span>
          <span className="progress-stat__value">{stats?.current_streak || 0}</span>
          <span className="progress-stat__label">Ngay lien tuc</span>
          <span className="progress-stat__sub">Ky luc: {stats?.best_streak || 0} ngay</span>
        </motion.div>
      </motion.div>

      {/* Tien do khoa hoc */}
      <motion.div
        className="progress-section"
        initial="hidden"
        animate="visible"
        variants={fadeUp}
        transition={{ delay: 0.2 }}
      >
        <div className="progress-section__header">
          <h2>Khoa hoc dang hoc</h2>
          <Link to="/dashboard/my-courses" className="progress-section__link">Xem tat ca →</Link>
        </div>

        {(stats?.course_progress || []).length > 0 ? (
          <div className="progress-courses">
            {stats.course_progress.map((course, i) => (
              <Link
                key={i}
                to={`/dashboard/courses/${course.course_id}/modules`}
                className="progress-course"
              >
                <div className="progress-course__info">
                  <h4 className="progress-course__title">{course.title}</h4>
                  <div className="progress-course__meta">
                    <span>{course.completed_lessons || 0}/{course.total_lessons || 0} bai hoc</span>
                    <span>·</span>
                    <span>{course.completed_modules || 0}/{course.total_modules || 0} modules</span>
                  </div>
                </div>
                <div className="progress-course__bar-wrap">
                  <div className="progress-course__bar">
                    <div
                      className="progress-course__fill"
                      style={{
                        width: `${course.progress || 0}%`,
                        background: course.progress >= 80
                          ? 'linear-gradient(90deg, #10b981, #34d399)'
                          : course.progress >= 40
                          ? 'linear-gradient(90deg, #6366f1, #8b5cf6)'
                          : 'linear-gradient(90deg, #f59e0b, #fbbf24)'
                      }}
                    />
                  </div>
                  <span className="progress-course__percent">{Math.round(course.progress || 0)}%</span>
                </div>
              </Link>
            ))}
          </div>
        ) : (
          <div className="progress-empty">
            <span className="progress-empty__icon">📚</span>
            <p>Ban chua dang ky khoa hoc nao</p>
            <Link to="/dashboard/courses" className="progress-empty__action">Kham pha khoa hoc →</Link>
          </div>
        )}
      </motion.div>

      {/* Thanh tuu */}
      <motion.div
        className="progress-section"
        initial="hidden"
        animate="visible"
        variants={fadeUp}
        transition={{ delay: 0.3 }}
      >
        <h2>Thanh tuu</h2>
        <div className="progress-achievements">
          <Achievement icon="🎯" title="Hoan thanh bai dau tien" unlocked={(stats?.lessons_completed || 0) >= 1} />
          <Achievement icon="📝" title="Lam 5 quiz" unlocked={(stats?.quizzes_taken || 0) >= 5} />
          <Achievement icon="🔥" title="7 ngay lien tuc" unlocked={(stats?.best_streak || 0) >= 7} />
          <Achievement icon="⏱" title="Hoc 10 gio" unlocked={(stats?.total_study_hours || 0) >= 10} />
          <Achievement icon="📚" title="Hoan thanh 1 khoa hoc" unlocked={(stats?.courses_completed || 0) >= 1} />
          <Achievement icon="🏆" title="Diem quiz 90+" unlocked={(stats?.avg_quiz_score || 0) >= 90} />
        </div>
      </motion.div>
    </div>
  )
}

// Sub-component: Achievement badge
const Achievement = ({ icon, title, unlocked }) => (
  <div className={`achievement ${unlocked ? 'achievement--unlocked' : ''}`}>
    <span className="achievement__icon">{icon}</span>
    <span className="achievement__title">{title}</span>
    {unlocked && <span className="achievement__check">✓</span>}
  </div>
)

export default ProgressPage
