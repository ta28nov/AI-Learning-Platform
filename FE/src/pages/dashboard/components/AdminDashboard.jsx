import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { fadeUp } from '@/styles/motion'

const AdminDashboard = ({ data }) => (
  <>
    <motion.div className="dash-stats" variants={fadeUp}>
      <StatCard icon={<UsersIcon />} value={data?.total_users || 0} label="Tổng người dùng" color="blue" />
      <StatCard icon={<BookIcon />} value={data?.total_courses || 0} label="Tổng khóa học" color="green" />
      <StatCard icon={<SchoolIcon />} value={data?.total_classes || 0} label="Tổng lớp học" color="orange" />
      <StatCard icon={<PulseIcon />} value={data?.activity_stats?.active_users_today || 0} label="Đang hoạt động" color="purple" />
    </motion.div>

    {data?.users_by_role && (
      <motion.section className="dash-section" variants={fadeUp}>
        <h2 className="dash-section__title">Phân bổ người dùng</h2>
        <div className="dash-admin-stats">
          <div className="dash-admin-stat"><span className="dash-admin-stat__label">Học viên</span><span className="dash-admin-stat__value">{data.users_by_role.student || 0}</span></div>
          <div className="dash-admin-stat"><span className="dash-admin-stat__label">Giảng viên</span><span className="dash-admin-stat__value">{data.users_by_role.instructor || 0}</span></div>
          <div className="dash-admin-stat"><span className="dash-admin-stat__label">Quản trị</span><span className="dash-admin-stat__value">{data.users_by_role.admin || 0}</span></div>
        </div>
      </motion.section>
    )}

    {data?.activity_stats && (
      <motion.section className="dash-section" variants={fadeUp}>
        <h2 className="dash-section__title">Hoạt động gần đây</h2>
        <div className="dash-admin-stats">
          <div className="dash-admin-stat"><span className="dash-admin-stat__label">Đăng ký tuần này</span><span className="dash-admin-stat__value">{data.activity_stats.new_enrollments_this_week || 0}</span></div>
          <div className="dash-admin-stat"><span className="dash-admin-stat__label">Quiz hôm nay</span><span className="dash-admin-stat__value">{data.activity_stats.quizzes_completed_today || 0}</span></div>
          <div className="dash-admin-stat"><span className="dash-admin-stat__label">Bài học hoàn thành</span><span className="dash-admin-stat__value">{data.activity_stats.total_lesson_completions || 0}</span></div>
        </div>
      </motion.section>
    )}

    <motion.section className="dash-section" variants={fadeUp}>
      <h2 className="dash-section__title">Quản trị nhanh</h2>
      <div className="dash-quick-actions">
        <Link to="/dashboard/admin/users" className="dash-quick-card"><span>Quản lý Users</span></Link>
        <Link to="/dashboard/admin/courses" className="dash-quick-card"><span>Quản lý Khóa học</span></Link>
        <Link to="/dashboard/admin/classes" className="dash-quick-card"><span>Quản lý Lớp học</span></Link>
        <Link to="/dashboard/admin/analytics" className="dash-quick-card"><span>Analytics</span></Link>
      </div>
    </motion.section>
  </>
)

const StatCard = ({ icon, value, label, color }) => (
  <motion.div className={`dash-stat-card dash-stat-card--${color}`} variants={fadeUp}>
    <span className="dash-stat-card__icon">{icon}</span>
    <span className="dash-stat-card__value">{value}</span>
    <span className="dash-stat-card__label">{label}</span>
  </motion.div>
)
const UsersIcon = () => <Icon><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" /><circle cx="9" cy="7" r="4" /><path d="M22 21v-2a4 4 0 0 0-3-3.87" /><path d="M16 3.13a4 4 0 0 1 0 7.75" /></Icon>
const BookIcon = () => <Icon><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" /><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2Z" /></Icon>
const SchoolIcon = () => <Icon><path d="M22 10 12 5 2 10l10 5 10-5Z" /><path d="M6 12v5c0 1.6 2.7 3 6 3s6-1.4 6-3v-5" /></Icon>
const PulseIcon = () => <Icon><polyline points="22 12 18 12 15 21 9 3 6 12 2 12" /></Icon>
const Icon = ({ children }) => <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">{children}</svg>

export default AdminDashboard
