import { useState, useEffect, useCallback } from 'react'
import { Link } from 'react-router-dom'
import toast from 'react-hot-toast'
import { useAuthStore } from '@stores/authStore'
import dashboardService from '@services/dashboardService'
import StateView from '@components/ui/StateView'
import DashboardShell from './components/DashboardShell'
import StudentDashboard from './components/StudentDashboard'
import InstructorDashboard from './components/InstructorDashboard'
import AdminDashboard from './components/AdminDashboard'
import './DashboardPage.css'

/**
 * DashboardPage - Trang dashboard, render theo role
 * Route: /dashboard
 * API theo docs BE_TO_FE_MAPPING.md line 537-557:
 *   Student: GET /dashboard/student -> StudentDashboardResponse
 *     overview{total_courses_enrolled, active_courses, completed_courses,
 *              total_lessons_completed, total_study_hours, current_streak_days}
 *     recent_courses[]{course_id, title, thumbnail_url, progress_percent, last_accessed, next_lesson{lesson_id,title}}
 *     pending_quizzes[]{quiz_id, title, course_title, lesson_title, due_date, status}
 *     performance_summary{average_quiz_score, quiz_pass_rate, lessons_this_week}
 *     recommendations[]{course_id, title, reason}
 *
 *   Instructor: GET /dashboard/instructor -> InstructorDashboardResponse
 *     active_classes_count, total_students, quizzes_created_count, avg_completion_rate
 *     recent_classes[]
 *     quick_actions[]{action_type, label, link, icon}
 *
 *   Admin: GET /dashboard/admin -> AdminSystemDashboardResponse
 *     total_users, users_by_role{student, instructor, admin} — SỐ ÍT!
 *     total_courses, course_stats{...}
 *     total_classes, class_stats{...}
 *     activity_stats{new_enrollments_this_week, quizzes_completed_today, active_users_today, total_lesson_completions}
 */
const DashboardPage = () => {
  const { user } = useAuthStore()
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const role = user?.role || 'student'

  const fetchDashboard = useCallback(async (showToast = true) => {
    try {
      setLoading(true)
      setError(null)
      let result
      if (role === 'admin') result = await dashboardService.getAdminDashboard()
      else if (role === 'instructor') result = await dashboardService.getInstructorDashboard()
      else result = await dashboardService.getStudentDashboard()
      setData(result)
    } catch (err) {
      setError(err.message || 'Không thể tải dữ liệu dashboard')
      if (showToast) toast.error('Không thể tải dữ liệu dashboard')
    } finally {
      setLoading(false)
    }
  }, [role])

  useEffect(() => {
    fetchDashboard(false)
  }, [fetchDashboard])

  const retryDashboard = () => fetchDashboard(true)

  return (
    <DashboardShell
      userName={user?.full_name}
      role={role}
      primaryAction={<PrimaryAction role={role} />}
    >
      {loading && (
        <div className="dash-loading">
          <div className="dash-loading__grid">
            {[1, 2, 3, 4].map((i) => <div key={i} className="dash-skeleton" />)}
          </div>
        </div>
      )}

      {!loading && error && (
        <StateView
          type="error"
          title="Không thể tải dữ liệu dashboard"
          message={error}
          actionLabel="Thử lại"
          onAction={retryDashboard}
        />
      )}

      {!loading && !error && role === 'student' && <StudentDashboard data={data} />}
      {!loading && !error && role === 'instructor' && <InstructorDashboard data={data} />}
      {!loading && !error && role === 'admin' && <AdminDashboard data={data} />}
    </DashboardShell>
  )
}

const PrimaryAction = ({ role }) => {
  if (role === 'student') return <Link to="/dashboard/assessment" className="dash-action-btn">Đánh giá năng lực</Link>
  if (role === 'instructor') return <Link to="/dashboard/instructor/classes/create" className="dash-action-btn">+ Tạo lớp mới</Link>
  return <Link to="/dashboard/admin" className="dash-action-btn">Quản trị hệ thống</Link>
}

export default DashboardPage
