import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import toast from 'react-hot-toast'
import dashboardService from '@services/dashboardService'
import Button from '@components/ui/Button'
import StateView from '@components/ui/StateView'
import './InstructorDashboardPage.css'

const ClassIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
    <circle cx="9" cy="7" r="4"/>
    <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
    <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
  </svg>
)
const StudentIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <path d="M22 10v6M2 10l10-5 10 5-10 5z"/>
    <path d="M6 12v5c3 3 9 3 12 0v-5"/>
  </svg>
)
const TrophyIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <path d="M6 9H4.5a2.5 2.5 0 0 1 0-5H6"/><path d="M18 9h1.5a2.5 2.5 0 0 0 0-5H18"/>
    <path d="M4 22h16"/><path d="M10 14.66V17c0 .55-.47.98-.97 1.21C7.85 18.75 7 20.24 7 22"/>
    <path d="M14 14.66V17c0 .55.47.98.97 1.21C16.15 18.75 17 20.24 17 22"/>
    <path d="M18 2H6v7a6 6 0 0 0 12 0V2z"/>
  </svg>
)
const ScoreIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <path d="M12 20V10"/><path d="M18 20V4"/><path d="M6 20v-4"/>
  </svg>
)
const ArrowIcon = () => (
  <svg viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <path d="M5 10h10m0 0-4-4m4 4-4 4"/>
  </svg>
)

/**
 * InstructorDashboardPage — Dashboard giảng viên
 * Route: /dashboard/instructor (InstructorRoute)
 * API: GET /dashboard/instructor via dashboardService.getInstructorDashboard — unchanged
 */
const InstructorDashboardPage = () => {
  const navigate = useNavigate()
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        setLoading(true)
        const res = await dashboardService.getInstructorDashboard()
        setData(res)
      } catch {
        toast.error('Không thể tải dashboard giảng viên')
      } finally {
        setLoading(false)
      }
    }
    fetchDashboard()
  }, [])

  if (loading) return <div className="id-page"><StateView type="loading" message="Đang tải dashboard…" /></div>
  if (!data) return (
    <div className="id-page">
      <StateView type="empty" message="Không tải được dữ liệu" action={{ label: 'Thử lại', onClick: () => window.location.reload() }} />
    </div>
  )

  const stats = [
    { icon: ClassIcon, label: 'Lớp học', value: data.active_classes_count ?? data.total_classes ?? data.classes?.length ?? 0, color: 'gold' },
    { icon: StudentIcon, label: 'Tổng học viên', value: data.total_students ?? 0, color: 'copper' },
    { icon: TrophyIcon, label: 'Hoàn thành TB', value: data.avg_completion_rate != null ? `${Math.round(data.avg_completion_rate)}%` : (data.quiz_pass_rate != null ? `${Math.round(data.quiz_pass_rate)}%` : '—'), color: 'jade' },
    { icon: ScoreIcon, label: 'Quiz đã tạo', value: data.quizzes_created_count ?? data.average_score ?? '—', color: 'ink' },
  ]

  const recentClasses = data.recent_classes || data.classes?.slice(0, 5) || []

  return (
    <div className="id-page">
      {/* Hero */}
      <motion.div
        className="id-hero"
        initial={{ opacity: 0, y: 24 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, ease: [0.65, 0, 0.35, 1] }}
      >
        <svg className="id-ornament" viewBox="0 0 48 12" fill="none">
          <line x1="0" y1="6" x2="16" y2="6" stroke="var(--gold-500)" strokeWidth="1"/>
          <circle cx="24" cy="6" r="4" stroke="var(--gold-500)" strokeWidth="1"/>
          <line x1="32" y1="6" x2="48" y2="6" stroke="var(--gold-500)" strokeWidth="1"/>
        </svg>
        <h1 className="id-hero__title">Dashboard Giảng viên</h1>
        <p className="id-hero__sub">Quản lý lớp học và theo dõi tiến độ học viên</p>
      </motion.div>

      {/* Stats */}
      <motion.div
        className="id-stats"
        initial="hidden"
        animate="visible"
        variants={{ visible: { transition: { staggerChildren: 0.08 } } }}
      >
        {stats.map(({ icon: Icon, label, value, color }) => (
          <motion.div
            key={label}
            className={`id-stat id-stat--${color}`}
            variants={{ hidden: { opacity: 0, y: 16 }, visible: { opacity: 1, y: 0, transition: { duration: 0.4, ease: [0.65, 0, 0.35, 1] } } }}
          >
            <span className="id-stat__icon"><Icon /></span>
            <span className="id-stat__value">{value}</span>
            <span className="id-stat__label">{label}</span>
          </motion.div>
        ))}
      </motion.div>

      {/* Quick actions */}
      <motion.div
        className="id-actions"
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3, duration: 0.4 }}
      >
        <Button
          variant="primary"
          onClick={() => navigate('/dashboard/instructor/classes/create')}
        >
          + Tạo lớp học mới
        </Button>
        <Button
          variant="outline"
          onClick={() => navigate('/dashboard/instructor/classes')}
        >
          Quản lý lớp học
        </Button>
        <Button variant="outline" onClick={() => navigate('/dashboard/instructor/quizzes')}>
          Quản lý quiz
        </Button>
        <Button variant="outline" onClick={() => navigate('/dashboard/instructor/analytics')}>
          Analytics
        </Button>
      </motion.div>

      {/* Recent classes */}
      {recentClasses.length > 0 && (
        <motion.div
          className="id-classes"
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.35, duration: 0.4 }}
        >
          <h2 className="id-section-title">Lớp học gần đây</h2>
          {recentClasses.map((cls) => (
            <div
              key={cls.class_id || cls.id}
              className="id-class-row"
              onClick={() => navigate(`/dashboard/instructor/classes/${cls.class_id || cls.id}`)}
            >
              <div className="id-class-row__info">
                <span className="id-class-row__name">{cls.class_name || cls.name}</span>
                <span className="id-class-row__meta">
                  {cls.student_count != null && `${cls.student_count} học viên`}
                  {cls.course_title && ` · ${cls.course_title}`}
                </span>
              </div>
              {cls.progress != null && (
                <div className="id-class-row__progress">
                  <div className="id-class-row__bar">
                    <div className="id-class-row__fill" style={{ width: `${cls.progress}%` }} />
                  </div>
                  <span className="id-class-row__pct">{Math.round(cls.progress)}%</span>
                </div>
              )}
              <span className="id-class-row__arrow"><ArrowIcon /></span>
            </div>
          ))}
        </motion.div>
      )}
    </div>
  )
}

export default InstructorDashboardPage
