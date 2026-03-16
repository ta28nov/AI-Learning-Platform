import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import toast from 'react-hot-toast'
import { useAuthStore } from '@stores/authStore'
import dashboardService from '@services/dashboardService'
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
  const navigate = useNavigate()
  const { user } = useAuthStore()
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  // Lấy dữ liệu dashboard theo role
  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        setLoading(true)
        const role = user?.role || 'student'
        let result
        if (role === 'admin') result = await dashboardService.getAdminDashboard()
        else if (role === 'instructor') result = await dashboardService.getInstructorDashboard()
        else result = await dashboardService.getStudentDashboard()
        setData(result)
      } catch (error) {
        toast.error('Không thể tải dữ liệu dashboard')
      } finally {
        setLoading(false)
      }
    }
    fetchDashboard()
  }, [user?.role])

  const role = user?.role || 'student'
  const greeting = getGreeting()

  // Animation
  const fadeUp = { hidden: { opacity: 0, y: 20 }, visible: { opacity: 1, y: 0 } }
  const stagger = { visible: { transition: { staggerChildren: 0.08 } } }

  return (
    <div className="dashboard-page">
      {/* Header chào mừng */}
      <motion.div
        className="dash-welcome"
        initial="hidden"
        animate="visible"
        variants={fadeUp}
        transition={{ duration: 0.4 }}
      >
        <div className="dash-welcome__text">
          <h1 className="dash-welcome__greeting">
            {greeting}, <span className="dash-welcome__name">{user?.full_name || 'bạn'}</span> 👋
          </h1>
          <p className="dash-welcome__sub">
            {role === 'student' && 'Hãy tiếp tục hành trình học tập của bạn hôm nay.'}
            {role === 'instructor' && 'Quản lý lớp học và theo dõi tiến độ học viên.'}
            {role === 'admin' && 'Tổng quan hệ thống và quản lý người dùng.'}
          </p>
        </div>
        <div className="dash-welcome__actions">
          {role === 'student' && (
            <Link to="/dashboard/assessment" className="dash-action-btn">
              Đánh giá năng lực
            </Link>
          )}
          {role === 'instructor' && (
            <Link to="/dashboard/classes/create" className="dash-action-btn">
              + Tạo lớp mới
            </Link>
          )}
          {role === 'admin' && (
            <Link to="/dashboard/admin" className="dash-action-btn">
              Quản trị hệ thống
            </Link>
          )}
        </div>
      </motion.div>

      {/* Loading state */}
      {loading && (
        <div className="dash-loading">
          <div className="dash-loading__grid">
            {[1, 2, 3, 4].map(i => <div key={i} className="dash-skeleton" />)}
          </div>
        </div>
      )}

      {/* ========== STUDENT DASHBOARD ========== */}
      {/* Docs: overview{}, recent_courses[], pending_quizzes[], performance_summary{}, recommendations[] */}
      {!loading && role === 'student' && (
        <motion.div initial="hidden" animate="visible" variants={stagger}>
          {/* Stat cards — từ overview{} */}
          <motion.div className="dash-stats" variants={fadeUp}>
            <StatCard
              icon="📖"
              value={data?.overview?.total_lessons_completed || 0}
              label="Bài học hoàn thành"
              color="blue"
            />
            <StatCard
              icon="📝"
              value={`${data?.performance_summary?.average_quiz_score || 0}%`}
              label="Điểm trung bình"
              color="green"
            />
            <StatCard
              icon="🔥"
              value={data?.overview?.current_streak_days || 0}
              label="Ngày liên tục"
              color="orange"
            />
            <StatCard
              icon="⏱"
              value={`${data?.overview?.total_study_hours || 0}h`}
              label="Tổng giờ học"
              color="purple"
            />
          </motion.div>

          {/* Khóa học đang học — từ recent_courses[] */}
          <motion.div className="dash-section" variants={fadeUp}>
            <div className="dash-section__header">
              <h2 className="dash-section__title">Khóa học đang học</h2>
              <Link to="/dashboard/my-courses" className="dash-section__link">Xem tất cả →</Link>
            </div>
            <div className="dash-courses">
              {(data?.recent_courses || []).length > 0 ? (
                data.recent_courses.slice(0, 4).map((course, i) => (
                  <CourseCard
                    key={i}
                    course={course}
                    onClick={() => navigate(`/dashboard/courses/${course.course_id}/modules`)}
                  />
                ))
              ) : (
                <EmptyState icon="📚" message="Bạn chưa đăng ký khóa học nào" action="Khám phá khóa học" link="/dashboard/courses" />
              )}
            </div>
          </motion.div>

          {/* Quiz cần làm — từ pending_quizzes[] */}
          <motion.div className="dash-section" variants={fadeUp}>
            <div className="dash-section__header">
              <h2 className="dash-section__title">Quiz cần làm</h2>
              <Link to="/dashboard/quiz" className="dash-section__link">Xem tất cả →</Link>
            </div>
            <div className="dash-quizzes">
              {(data?.pending_quizzes || []).length > 0 ? (
                data.pending_quizzes.slice(0, 3).map((quiz, i) => (
                  <QuizCard key={i} quiz={quiz} onClick={() => navigate(`/dashboard/quiz/${quiz.quiz_id}`)} />
                ))
              ) : (
                <div className="dash-empty-inline">✓ Không có quiz cần làm</div>
              )}
            </div>
          </motion.div>

          {/* Gợi ý — từ recommendations[] */}
          {data?.recommendations && data.recommendations.length > 0 && (
            <motion.div className="dash-section" variants={fadeUp}>
              <div className="dash-section__header">
                <h2 className="dash-section__title">Gợi ý cho bạn</h2>
                <Link to="/dashboard/recommendations" className="dash-section__link">Xem tất cả →</Link>
              </div>
              <div className="dash-recs">
                {data.recommendations.slice(0, 3).map((rec, i) => (
                  <div key={i} className="dash-rec-card" onClick={() => navigate(`/dashboard/courses/${rec.course_id}`)}>
                    <h4 className="dash-rec-card__title">{rec.title}</h4>
                    <p className="dash-rec-card__reason">{rec.reason}</p>
                  </div>
                ))}
              </div>
            </motion.div>
          )}
        </motion.div>
      )}

      {/* ========== INSTRUCTOR DASHBOARD ========== */}
      {/* Docs: active_classes_count, total_students, quizzes_created_count, avg_completion_rate */}
      {!loading && role === 'instructor' && (
        <motion.div initial="hidden" animate="visible" variants={stagger}>
          <motion.div className="dash-stats" variants={fadeUp}>
            <StatCard icon="🏫" value={data?.active_classes_count || 0} label="Lớp đang hoạt động" color="blue" />
            <StatCard icon="👥" value={data?.total_students || 0} label="Tổng học viên" color="green" />
            <StatCard icon="📝" value={data?.quizzes_created_count || 0} label="Quiz đã tạo" color="orange" />
            <StatCard icon="📊" value={`${data?.avg_completion_rate || 0}%`} label="Hoàn thành TB" color="purple" />
          </motion.div>

          {/* Lớp học gần đây — từ recent_classes[] */}
          <motion.div className="dash-section" variants={fadeUp}>
            <div className="dash-section__header">
              <h2 className="dash-section__title">Lớp học gần đây</h2>
              <Link to="/dashboard/classes" className="dash-section__link">Tất cả lớp →</Link>
            </div>
            <div className="dash-courses">
              {(data?.recent_classes || []).length > 0 ? (
                data.recent_classes.map((cls, i) => (
                  <div key={i} className="dash-class-card" onClick={() => navigate(`/dashboard/classes/${cls.class_id}`)}>
                    <h4>{cls.name}</h4>
                    <div className="dash-class-card__meta">
                      <span>{cls.student_count || 0} học viên</span>
                      <span className={`dash-class-card__status dash-class-card__status--${cls.status}`}>
                        {cls.status === 'active' ? 'Đang hoạt động' : cls.status}
                      </span>
                    </div>
                  </div>
                ))
              ) : (
                <EmptyState icon="🏫" message="Chưa có lớp học nào" action="Tạo lớp mới" link="/dashboard/classes/create" />
              )}
            </div>
          </motion.div>

          {/* Quick actions — từ quick_actions[] hoặc mặc định */}
          <motion.div className="dash-section" variants={fadeUp}>
            <h2 className="dash-section__title">Hành động nhanh</h2>
            <div className="dash-quick-actions">
              <Link to="/dashboard/classes/create" className="dash-quick-card">
                <span className="dash-quick-card__icon">🏫</span>
                <span>Tạo lớp học</span>
              </Link>
              <Link to="/dashboard/courses" className="dash-quick-card">
                <span className="dash-quick-card__icon">📚</span>
                <span>Khóa học</span>
              </Link>
              <Link to="/dashboard/personal-courses" className="dash-quick-card">
                <span className="dash-quick-card__icon">✨</span>
                <span>Tạo khóa học AI</span>
              </Link>
            </div>
          </motion.div>
        </motion.div>
      )}

      {/* ========== ADMIN DASHBOARD ========== */}
      {/* Docs: total_users, users_by_role{}, total_courses, course_stats{},
               total_classes, class_stats{}, activity_stats{} */}
      {!loading && role === 'admin' && (
        <motion.div initial="hidden" animate="visible" variants={stagger}>
          <motion.div className="dash-stats" variants={fadeUp}>
            <StatCard icon="👥" value={data?.total_users || 0} label="Tổng người dùng" color="blue" />
            <StatCard icon="📚" value={data?.total_courses || 0} label="Tổng khóa học" color="green" />
            <StatCard icon="🏫" value={data?.total_classes || 0} label="Tổng lớp học" color="orange" />
            <StatCard
              icon="📈"
              value={data?.activity_stats?.active_users_today || 0}
              label="Đang hoạt động"
              color="purple"
            />
          </motion.div>

          {/* Thống kê chi tiết */}
          {data?.users_by_role && (
            <motion.div className="dash-section" variants={fadeUp}>
              <h2 className="dash-section__title">Phân bổ người dùng</h2>
              <div className="dash-admin-stats">
                <div className="dash-admin-stat">
                  <span className="dash-admin-stat__label">Học viên</span>
                  <span className="dash-admin-stat__value">{data.users_by_role.student || 0}</span>
                </div>
                <div className="dash-admin-stat">
                  <span className="dash-admin-stat__label">Giảng viên</span>
                  <span className="dash-admin-stat__value">{data.users_by_role.instructor || 0}</span>
                </div>
                <div className="dash-admin-stat">
                  <span className="dash-admin-stat__label">Quản trị</span>
                  <span className="dash-admin-stat__value">{data.users_by_role.admin || 0}</span>
                </div>
              </div>
            </motion.div>
          )}

          {/* Hoạt động gần đây */}
          {data?.activity_stats && (
            <motion.div className="dash-section" variants={fadeUp}>
              <h2 className="dash-section__title">Hoạt động gần đây</h2>
              <div className="dash-admin-stats">
                <div className="dash-admin-stat">
                  <span className="dash-admin-stat__label">Đăng ký tuần này</span>
                  <span className="dash-admin-stat__value">{data.activity_stats.new_enrollments_this_week || 0}</span>
                </div>
                <div className="dash-admin-stat">
                  <span className="dash-admin-stat__label">Quiz hôm nay</span>
                  <span className="dash-admin-stat__value">{data.activity_stats.quizzes_completed_today || 0}</span>
                </div>
                <div className="dash-admin-stat">
                  <span className="dash-admin-stat__label">Bài học hoàn thành</span>
                  <span className="dash-admin-stat__value">{data.activity_stats.total_lesson_completions || 0}</span>
                </div>
              </div>
            </motion.div>
          )}

          {/* Quản trị nhanh */}
          <motion.div className="dash-section" variants={fadeUp}>
            <h2 className="dash-section__title">Quản trị nhanh</h2>
            <div className="dash-quick-actions">
              <Link to="/dashboard/admin/users" className="dash-quick-card">
                <span className="dash-quick-card__icon">👥</span>
                <span>Quản lý Users</span>
              </Link>
              <Link to="/dashboard/admin/courses" className="dash-quick-card">
                <span className="dash-quick-card__icon">📚</span>
                <span>Quản lý Khóa học</span>
              </Link>
              <Link to="/dashboard/admin/classes" className="dash-quick-card">
                <span className="dash-quick-card__icon">🏫</span>
                <span>Quản lý Lớp học</span>
              </Link>
              <Link to="/dashboard/admin/analytics" className="dash-quick-card">
                <span className="dash-quick-card__icon">📊</span>
                <span>Analytics</span>
              </Link>
            </div>
          </motion.div>
        </motion.div>
      )}
    </div>
  )
}

/* ========== Sub-components ========== */

// Stat card nhỏ
const StatCard = ({ icon, value, label, color }) => (
  <motion.div
    className={`dash-stat-card dash-stat-card--${color}`}
    variants={{ hidden: { opacity: 0, y: 20 }, visible: { opacity: 1, y: 0 } }}
  >
    <span className="dash-stat-card__icon">{icon}</span>
    <span className="dash-stat-card__value">{value}</span>
    <span className="dash-stat-card__label">{label}</span>
  </motion.div>
)

// Course card nhỏ — mapping: title, progress_percent, thumbnail_url, next_lesson
const CourseCard = ({ course, onClick }) => (
  <div className="dash-course-card" onClick={onClick}>
    <div className="dash-course-card__info">
      <h4 className="dash-course-card__title">{course.title}</h4>
      {course.next_lesson?.title && (
        <span className="dash-course-card__next">
          Tiếp: {course.next_lesson.title}
        </span>
      )}
    </div>
    <div className="dash-course-card__progress">
      <div className="dash-course-card__bar">
        <div
          className="dash-course-card__fill"
          style={{ width: `${course.progress_percent || 0}%` }}
        />
      </div>
      <span className="dash-course-card__percent">{course.progress_percent || 0}%</span>
    </div>
  </div>
)

// Quiz card nhỏ — mapping: title, course_title, lesson_title, due_date, status
const QuizCard = ({ quiz, onClick }) => (
  <div className="dash-quiz-card" onClick={onClick}>
    <div className="dash-quiz-card__info">
      <h4>{quiz.title}</h4>
      <span className="dash-quiz-card__course">{quiz.course_title}</span>
      {quiz.lesson_title && (
        <span className="dash-quiz-card__lesson">{quiz.lesson_title}</span>
      )}
    </div>
    <div className="dash-quiz-card__right">
      {quiz.status && (
        <span className={`dash-quiz-card__status dash-quiz-card__status--${quiz.status}`}>
          {quiz.status === 'not_started' ? 'Chưa làm' : quiz.status === 'failed' ? 'Chưa đạt' : quiz.status}
        </span>
      )}
      {quiz.due_date && (
        <span className="dash-quiz-card__due">
          Hạn: {new Date(quiz.due_date).toLocaleDateString('vi-VN')}
        </span>
      )}
    </div>
  </div>
)

// Empty state
const EmptyState = ({ icon, message, action, link }) => (
  <div className="dash-empty">
    <span className="dash-empty__icon">{icon}</span>
    <p className="dash-empty__msg">{message}</p>
    <Link to={link} className="dash-empty__action">{action} →</Link>
  </div>
)

// Helper: lấy lời chào theo giờ
function getGreeting() {
  const h = new Date().getHours()
  if (h < 12) return 'Chào buổi sáng'
  if (h < 18) return 'Chào buổi chiều'
  return 'Chào buổi tối'
}

export default DashboardPage
