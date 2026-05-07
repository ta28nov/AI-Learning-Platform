import { motion, useReducedMotion } from 'framer-motion'
import { fadeUp, staggerEditorial } from '@/styles/motion'

const roleSubtitle = {
  student: 'Hãy tiếp tục hành trình học tập của bạn hôm nay.',
  instructor: 'Quản lý lớp học và theo dõi tiến độ học viên.',
  admin: 'Tổng quan hệ thống và quản lý người dùng.',
}

const DashboardShell = ({ userName, role, primaryAction, children }) => {
  const shouldReduceMotion = useReducedMotion()
  const greeting = getGreeting()

  return (
    <div className="dashboard-page">
      <motion.div
        className="dash-welcome"
        variants={fadeUp}
        initial={shouldReduceMotion ? false : 'hidden'}
        animate="show"
      >
        <div className="dash-welcome__text">
          <div className="dash-welcome__ornament" aria-hidden="true">
            <span className="dash-welcome__line" />
            <OrnamentIcon />
            <span className="dash-welcome__line" />
          </div>
          <h1 className="dash-welcome__greeting">
            {greeting}, <span className="dash-welcome__name">{userName || 'bạn'}</span>
          </h1>
          <p className="dash-welcome__sub">{roleSubtitle[role] || roleSubtitle.student}</p>
        </div>
        {primaryAction}
      </motion.div>

      <motion.div
        variants={staggerEditorial}
        initial={shouldReduceMotion ? false : 'hidden'}
        animate="show"
      >
        {children}
      </motion.div>
    </div>
  )
}

function getGreeting() {
  const h = new Date().getHours()
  if (h < 12) return 'Chào buổi sáng'
  if (h < 18) return 'Chào buổi chiều'
  return 'Chào buổi tối'
}

const OrnamentIcon = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
    <path d="m12 2 2.8 7.2L22 12l-7.2 2.8L12 22l-2.8-7.2L2 12l7.2-2.8L12 2Z" />
  </svg>
)

export default DashboardShell
