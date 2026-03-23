import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import toast from 'react-hot-toast'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts'
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
        toast.error('Không thể tải dữ liệu tiến độ')
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
        <h1 className="progress-header__title">Tiến độ học tập</h1>
        <p className="progress-header__sub">Theo dõi quá trình và thành tựu của bạn</p>
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
          <span className="progress-stat__label">Tiến độ tổng thể</span>
        </motion.div>

        <motion.div className="progress-stat" variants={fadeUp}>
          <span className="progress-stat__icon">📚</span>
          <span className="progress-stat__value">{stats?.courses_enrolled || 0}</span>
          <span className="progress-stat__label">Khóa học đăng ký</span>
          <span className="progress-stat__sub">{stats?.courses_completed || 0} hoàn thành</span>
        </motion.div>

        <motion.div className="progress-stat" variants={fadeUp}>
          <span className="progress-stat__icon">📖</span>
          <span className="progress-stat__value">{stats?.lessons_completed || 0}</span>
          <span className="progress-stat__label">Bài học hoàn thành</span>
          <span className="progress-stat__sub">/ {stats?.total_lessons || 0} tổng</span>
        </motion.div>

        <motion.div className="progress-stat" variants={fadeUp}>
          <span className="progress-stat__icon">📝</span>
          <span className="progress-stat__value">{stats?.quizzes_taken || 0}</span>
          <span className="progress-stat__label">Quiz đã làm</span>
          <span className="progress-stat__sub">TB: {stats?.avg_quiz_score || 0}%</span>
        </motion.div>

        <motion.div className="progress-stat" variants={fadeUp}>
          <span className="progress-stat__icon">⏱</span>
          <span className="progress-stat__value">{stats?.total_study_hours || 0}h</span>
          <span className="progress-stat__label">Tổng giờ học</span>
          <span className="progress-stat__sub">~{stats?.avg_daily_hours || 0}h/ngày</span>
        </motion.div>

        <motion.div className="progress-stat" variants={fadeUp}>
          <span className="progress-stat__icon">🔥</span>
          <span className="progress-stat__value">{stats?.current_streak || 0}</span>
          <span className="progress-stat__label">Ngày liên tục</span>
          <span className="progress-stat__sub">Kỷ lục: {stats?.best_streak || 0} ngày</span>
        </motion.div>
      </motion.div>

      {/* Bieu do tien do theo tuan (Recharts LineChart) */}
      {chart?.chart_data?.length > 0 && (
        <motion.div
          className="progress-section"
          initial="hidden"
          animate="visible"
          variants={fadeUp}
          transition={{ delay: 0.25 }}
        >
          <h2>Biểu đồ tiến độ</h2>
          {chart.summary && (
            <div className="progress-chart-summary">
              <span>Tổng: {chart.summary.total_lessons || 0} bài</span>
              <span>·</span>
              <span>{chart.summary.total_hours || 0} giờ</span>
              <span>·</span>
              <span>TB: {chart.summary.avg_per_day || 0} bài/ngày</span>
            </div>
          )}
          <div className="progress-chart-wrap">
            <ResponsiveContainer width="100%" height={280}>
              <LineChart data={chart.chart_data} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border-light)" />
                <XAxis
                  dataKey="date"
                  tick={{ fontSize: 12, fill: 'var(--text-muted)' }}
                  tickFormatter={(d) => {
                    const date = new Date(d)
                    return `${date.getDate()}/${date.getMonth() + 1}`
                  }}
                />
                <YAxis tick={{ fontSize: 12, fill: 'var(--text-muted)' }} />
                <Tooltip
                  contentStyle={{
                    background: 'var(--bg-card)',
                    border: '1px solid var(--border-color)',
                    borderRadius: 8,
                    fontSize: 13
                  }}
                  labelFormatter={(d) => new Date(d).toLocaleDateString('vi-VN')}
                />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="lessons_completed"
                  name="Bài học"
                  stroke="var(--primary)"
                  strokeWidth={2}
                  dot={{ r: 3 }}
                  activeDot={{ r: 5 }}
                />
                <Line
                  type="monotone"
                  dataKey="hours_spent"
                  name="Giờ học"
                  stroke="var(--success)"
                  strokeWidth={2}
                  dot={{ r: 3 }}
                  activeDot={{ r: 5 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </motion.div>
      )}

      {/* Khoa hoc dang hoc */}
      <motion.div
        className="progress-section"
        initial="hidden"
        animate="visible"
        variants={fadeUp}
        transition={{ delay: 0.3 }}
      >
        <div className="progress-section__header">
          <h2>Khóa học đang học</h2>
          <Link to="/dashboard/my-courses" className="progress-section__link">Xem tất cả →</Link>
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
                    <span>{course.completed_lessons || 0}/{course.total_lessons || 0} bài học</span>
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
            <p>Bạn chưa đăng ký khóa học nào</p>
            <Link to="/dashboard/courses" className="progress-empty__action">Khám phá khóa học →</Link>
          </div>
        )}
      </motion.div>

      {/* Thanh tuu */}
      <motion.div
        className="progress-section"
        initial="hidden"
        animate="visible"
        variants={fadeUp}
        transition={{ delay: 0.35 }}
      >
        <h2>Thành tựu</h2>
        <div className="progress-achievements">
          <Achievement icon="🎯" title="Hoàn thành bài đầu tiên" unlocked={(stats?.lessons_completed || 0) >= 1} />
          <Achievement icon="📝" title="Làm 5 quiz" unlocked={(stats?.quizzes_taken || 0) >= 5} />
          <Achievement icon="🔥" title="7 ngày liên tục" unlocked={(stats?.best_streak || 0) >= 7} />
          <Achievement icon="⏱" title="Học 10 giờ" unlocked={(stats?.total_study_hours || 0) >= 10} />
          <Achievement icon="📚" title="Hoàn thành 1 khóa học" unlocked={(stats?.courses_completed || 0) >= 1} />
          <Achievement icon="🏆" title="Điểm quiz 90+" unlocked={(stats?.avg_quiz_score || 0) >= 90} />
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
