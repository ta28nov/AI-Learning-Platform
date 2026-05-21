import { Link, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { fadeUp } from '@/styles/motion'
import StateView from '@components/ui/StateView'

const InstructorDashboard = ({ data }) => {
  const navigate = useNavigate()

  return (
    <>
      <motion.div className="dash-stats" variants={fadeUp}>
        <StatCard icon={<SchoolIcon />} value={data?.active_classes_count || 0} label="Lớp đang hoạt động" color="blue" />
        <StatCard icon={<UsersIcon />} value={data?.total_students || 0} label="Tổng học viên" color="green" />
        <StatCard icon={<EditIcon />} value={data?.quizzes_created_count || 0} label="Quiz đã tạo" color="orange" />
        <StatCard icon={<TrendIcon />} value={`${data?.avg_completion_rate || 0}%`} label="Hoàn thành TB" color="purple" />
      </motion.div>

      <motion.section className="dash-section" variants={fadeUp}>
        <div className="dash-section__header">
          <h2 className="dash-section__title">Lớp học gần đây</h2>
          <Link to="/dashboard/instructor/classes" className="dash-section__link">Tất cả lớp →</Link>
        </div>
        <div className="dash-courses">
          {(data?.recent_classes || []).length > 0 ? (
            data.recent_classes.map((cls) => (
              <button key={cls.class_id} className="dash-class-card" onClick={() => navigate(`/dashboard/instructor/classes/${cls.class_id}`)}>
                <h4>{cls.class_name || cls.name}</h4>
                <div className="dash-class-card__meta">
                  <span>{cls.student_count || 0} học viên</span>
                  <span className={`dash-class-card__status dash-class-card__status--${cls.status}`}>
                    {cls.status === 'active' ? 'Đang hoạt động' : cls.status}
                  </span>
                </div>
              </button>
            ))
          ) : (
            <StateView
              type="empty"
              title="Chưa có lớp học nào"
              message="Tạo lớp mới để bắt đầu quản lý học viên."
              actionLabel="Tạo lớp mới"
              onAction={() => navigate('/dashboard/instructor/classes/create')}
            />
          )}
        </div>
      </motion.section>

      <motion.section className="dash-section" variants={fadeUp}>
        <h2 className="dash-section__title">Hành động nhanh</h2>
        <div className="dash-quick-actions">
          <Link to="/dashboard/instructor/classes/create" className="dash-quick-card"><span>Tạo lớp học</span></Link>
          <Link to="/dashboard/courses" className="dash-quick-card"><span>Khóa học</span></Link>
          <Link to="/dashboard/instructor/quizzes" className="dash-quick-card"><span>Quản lý quiz</span></Link>
          <Link to="/dashboard/instructor/analytics" className="dash-quick-card"><span>Analytics</span></Link>
        </div>
      </motion.section>
    </>
  )
}

const StatCard = ({ icon, value, label, color }) => (
  <motion.div className={`dash-stat-card dash-stat-card--${color}`} variants={fadeUp}>
    <span className="dash-stat-card__icon">{icon}</span>
    <span className="dash-stat-card__value">{value}</span>
    <span className="dash-stat-card__label">{label}</span>
  </motion.div>
)
const SchoolIcon = () => <Icon><path d="M22 10 12 5 2 10l10 5 10-5Z" /><path d="M6 12v5c0 1.6 2.7 3 6 3s6-1.4 6-3v-5" /></Icon>
const UsersIcon = () => <Icon><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" /><circle cx="9" cy="7" r="4" /><path d="M22 21v-2a4 4 0 0 0-3-3.87" /><path d="M16 3.13a4 4 0 0 1 0 7.75" /></Icon>
const EditIcon = () => <Icon><path d="M12 20h9" /><path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4 12.5-12.5Z" /></Icon>
const TrendIcon = () => <Icon><polyline points="22 7 13.5 15.5 8.5 10.5 2 17" /><polyline points="16 7 22 7 22 13" /></Icon>
const Icon = ({ children }) => <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">{children}</svg>

export default InstructorDashboard
