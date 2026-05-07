import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import { motion, useReducedMotion } from 'framer-motion'
import { useAuthStore } from '@stores/authStore'
import { useUiStore } from '@stores/uiStore'
import { staggerTight, fadeUp } from '@/styles/motion'
import Button from '@components/ui/Button'

/* =============================================================================
   NAV CONFIG — single source of truth for all sidebar items.
   isActive: function(pathname) → boolean
   roles: if defined, item only renders for those roles. undefined = all roles.
   ============================================================================= */
const PRIMARY_NAV = [
  {
    to: '/dashboard',
    label: 'Tổng quan',
    Icon: DashboardIcon,
    isActive: (p) => p === '/dashboard',
  },
  {
    to: '/dashboard/courses',
    label: 'Khóa học',
    Icon: CoursesIcon,
    isActive: (p) => p.startsWith('/dashboard/courses'),
  },
  {
    to: '/dashboard/my-courses',
    label: 'Khóa học của tôi',
    Icon: MyCoursesIcon,
    isActive: (p) => p.startsWith('/dashboard/my-courses') || p.startsWith('/dashboard/enrollment'),
  },
  {
    to: '/dashboard/assessment',
    label: 'Đánh giá năng lực',
    Icon: AssessmentIcon,
    isActive: (p) => p.startsWith('/dashboard/assessment'),
  },
  {
    to: '/dashboard/quiz',
    label: 'Bài kiểm tra',
    Icon: QuizIcon,
    isActive: (p) => p.startsWith('/dashboard/quiz'),
  },
  {
    to: '/dashboard/chat',
    label: 'AI Chat',
    Icon: ChatIcon,
    isActive: (p) => p.startsWith('/dashboard/chat'),
  },
]

const SECONDARY_NAV = [
  {
    to: '/dashboard/search',
    label: 'Tìm kiếm',
    Icon: SearchIcon,
    isActive: (p) => p.startsWith('/dashboard/search'),
  },
  {
    to: '/dashboard/recommendations',
    label: 'Gợi ý',
    Icon: RecommendationsIcon,
    isActive: (p) => p.startsWith('/dashboard/recommendations'),
  },
  {
    to: '/dashboard/personal-courses',
    label: 'Khóa học cá nhân',
    Icon: PersonalCoursesIcon,
    isActive: (p) => p.startsWith('/dashboard/personal-courses'),
  },
  {
    to: '/dashboard/progress',
    label: 'Tiến độ',
    Icon: ProgressIcon,
    isActive: (p) => p.startsWith('/dashboard/progress'),
  },
]

const INSTRUCTOR_NAV = [
  {
    to: '/dashboard/instructor',
    label: 'Giảng dạy',
    Icon: InstructorIcon,
    isActive: (p) => p.startsWith('/dashboard/instructor'),
  },
]

const ADMIN_NAV = [
  {
    to: '/dashboard/admin',
    label: 'Quản trị',
    Icon: AdminIcon,
    isActive: (p) => p.startsWith('/dashboard/admin'),
  },
]

/* =============================================================================
   SIDEBAR COMPONENT
   ============================================================================= */
const Sidebar = ({ onLogout }) => {
  const location = useLocation()
  const { user } = useAuthStore()
  const { sidebarOpen, setSidebarOpen } = useUiStore()
  const shouldReduceMotion = useReducedMotion()

  const close = () => setSidebarOpen(false)
  const isInstructor = user?.role === 'instructor' || user?.role === 'admin'
  const isAdmin = user?.role === 'admin'

  const containerVariants = shouldReduceMotion ? {} : staggerTight
  const itemVariants = shouldReduceMotion ? {} : fadeUp

  return (
    <aside className={`dashboard-sidebar${sidebarOpen ? ' sidebar-open' : ''}`}>
      {/* Logo / Brand */}
      <div className="sidebar-header">
        <Link to="/dashboard" className="sidebar-logo-link" onClick={close} aria-label="Trang chủ">
          <span className="sidebar-logo-mark" aria-hidden="true">◆</span>
          <span className="sidebar-logo-text">AI Learning</span>
        </Link>
        <button
          className="sidebar-close"
          onClick={close}
          aria-label="Đóng sidebar"
        >
          <CloseIcon />
        </button>
      </div>

      {/* Primary navigation */}
      <nav className="sidebar-nav" aria-label="Navigation chính">
        <motion.ul
          className="sidebar-nav-list"
          variants={containerVariants}
          initial={shouldReduceMotion ? false : 'hidden'}
          animate="show"
        >
          {PRIMARY_NAV.map((item) => (
            <motion.li key={item.to} variants={itemVariants}>
              <NavItem {...item} active={item.isActive(location.pathname)} onClick={close} />
            </motion.li>
          ))}
        </motion.ul>

        {/* Divider + secondary nav */}
        <div className="sidebar-divider" role="separator" />

        <motion.ul
          className="sidebar-nav-list"
          variants={containerVariants}
          initial={shouldReduceMotion ? false : 'hidden'}
          animate="show"
        >
          {SECONDARY_NAV.map((item) => (
            <motion.li key={item.to} variants={itemVariants}>
              <NavItem {...item} active={item.isActive(location.pathname)} onClick={close} />
            </motion.li>
          ))}
        </motion.ul>

        {/* Instructor section */}
        {isInstructor && (
          <>
            <div className="sidebar-divider" role="separator" />
            <p className="sidebar-section-label">Giảng viên</p>
            <ul className="sidebar-nav-list">
              {INSTRUCTOR_NAV.map((item) => (
                <li key={item.to}>
                  <NavItem {...item} active={item.isActive(location.pathname)} onClick={close} />
                </li>
              ))}
            </ul>
          </>
        )}

        {/* Admin section */}
        {isAdmin && (
          <>
            <div className="sidebar-divider" role="separator" />
            <p className="sidebar-section-label">Admin</p>
            <ul className="sidebar-nav-list">
              {ADMIN_NAV.map((item) => (
                <li key={item.to}>
                  <NavItem {...item} active={item.isActive(location.pathname)} onClick={close} />
                </li>
              ))}
            </ul>
          </>
        )}
      </nav>

      {/* User footer */}
      <div className="sidebar-footer">
        <Link to="/dashboard/profile" className="user-info" onClick={close} aria-label="Hồ sơ cá nhân">
          <div className="user-avatar" aria-hidden="true">
            {user?.full_name?.charAt(0)?.toUpperCase() || 'U'}
          </div>
          <div className="user-details">
            <div className="user-name">{user?.full_name || 'Người dùng'}</div>
            <div className="user-role">{getRoleLabel(user?.role)}</div>
          </div>
        </Link>
        <Button variant="ghost" size="sm" onClick={onLogout} className="sidebar-logout-btn">
          Đăng xuất
        </Button>
      </div>
    </aside>
  )
}

/* =============================================================================
   NAV ITEM
   ============================================================================= */
const NavItem = ({ to, label, Icon, active, onClick }) => (
  <Link
    to={to}
    className={`sidebar-nav-item${active ? ' nav-item-active' : ''}`}
    onClick={onClick}
    aria-current={active ? 'page' : undefined}
  >
    <span className="nav-item-icon" aria-hidden="true"><Icon /></span>
    <span className="nav-item-label">{label}</span>
    {active && (
      <span className="nav-item-active-bar" aria-hidden="true" />
    )}
  </Link>
)

/* =============================================================================
   HELPERS
   ============================================================================= */
const getRoleLabel = (role) => ({
  student: 'Học viên',
  instructor: 'Giảng viên',
  admin: 'Quản trị viên',
}[role] || 'Người dùng')

/* =============================================================================
   SVG ICONS — inline, no external deps
   ============================================================================= */
const DashboardIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <rect x="3" y="3" width="7" height="9" /><rect x="14" y="3" width="7" height="5" />
    <rect x="14" y="12" width="7" height="9" /><rect x="3" y="16" width="7" height="5" />
  </svg>
)
const CoursesIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z" /><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z" />
  </svg>
)
const MyCoursesIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" /><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z" />
  </svg>
)
const AssessmentIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
  </svg>
)
const QuizIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="10" />
    <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3" /><line x1="12" y1="17" x2="12.01" y2="17" />
  </svg>
)
const ChatIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
  </svg>
)
const SearchIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="11" cy="11" r="8" /><line x1="21" y1="21" x2="16.65" y2="16.65" />
  </svg>
)
const RecommendationsIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" />
  </svg>
)
const PersonalCoursesIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M12 20h9" /><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z" />
  </svg>
)
const ProgressIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <line x1="18" y1="20" x2="18" y2="10" /><line x1="12" y1="20" x2="12" y2="4" /><line x1="6" y1="20" x2="6" y2="14" />
  </svg>
)
const InstructorIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" /><circle cx="9" cy="7" r="4" />
    <path d="M23 21v-2a4 4 0 0 0-3-3.87" /><path d="M16 3.13a4 4 0 0 1 0 7.75" />
  </svg>
)
const AdminIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="3" />
    <path d="M19.07 4.93a10 10 0 0 1 0 14.14" /><path d="M4.93 4.93a10 10 0 0 0 0 14.14" />
    <path d="M16.24 7.76a6 6 0 0 1 0 8.49" /><path d="M7.76 7.76a6 6 0 0 0 0 8.49" />
  </svg>
)
const CloseIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
    <line x1="18" y1="6" x2="6" y2="18" /><line x1="6" y1="6" x2="18" y2="18" />
  </svg>
)

export default Sidebar
