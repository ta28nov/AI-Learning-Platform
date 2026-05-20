import { Link, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { fadeUp } from '@/styles/motion'
import StateView from '@components/ui/StateView'

const StudentDashboard = ({ data }) => {
  const navigate = useNavigate()

  return (
    <>
      <motion.div className="dash-stats" variants={fadeUp}>
        <StatCard icon={<BookIcon />} value={data?.overview?.total_lessons_completed || 0} label="Bài học hoàn thành" color="blue" />
        <StatCard icon={<ChartIcon />} value={`${data?.performance_summary?.average_quiz_score || 0}%`} label="Điểm trung bình" color="green" />
        <StatCard icon={<StreakIcon />} value={data?.overview?.current_streak_days || 0} label="Ngày liên tục" color="orange" />
        <StatCard icon={<ClockIcon />} value={`${data?.overview?.total_study_hours || 0}h`} label="Tổng giờ học" color="purple" />
      </motion.div>

      <div className="dash-grid-asym">
        <motion.section className="dash-section" variants={fadeUp}>
          <div className="dash-section__header">
            <h2 className="dash-section__title">Khóa học đang học</h2>
            <Link to="/dashboard/my-courses" className="dash-section__link">Xem tất cả →</Link>
          </div>
          <div className="dash-courses">
            {(data?.recent_courses || []).length > 0 ? (
              data.recent_courses.slice(0, 4).map((course) => (
                <button
                  key={course.course_id}
                  className="dash-course-card"
                  onClick={() => navigate(`/dashboard/courses/${course.course_id}/modules`)}
                >
                  <div className="dash-course-card__info">
                    <h4 className="dash-course-card__title">{course.title}</h4>
                    {course.next_lesson?.title && <span className="dash-course-card__next">Tiếp: {course.next_lesson.title}</span>}
                  </div>
                  <div className="dash-course-card__progress">
                    <div className="dash-course-card__bar">
                      <div className="dash-course-card__fill" style={{ width: `${Math.round(course.progress_percent || 0)}%` }} />
                    </div>
                    <span className="dash-course-card__percent">{Math.round(course.progress_percent || 0)}%</span>
                  </div>
                </button>
              ))
            ) : (
              <StateView
                type="empty"
                title="Bạn chưa đăng ký khóa học"
                message="Khám phá danh mục để bắt đầu hành trình học tập."
                actionLabel="Khám phá khóa học"
                onAction={() => navigate('/dashboard/courses')}
              />
            )}
          </div>
        </motion.section>

        <motion.section className="dash-section" variants={fadeUp}>
          <div className="dash-section__header">
            <h2 className="dash-section__title">Quiz cần làm</h2>
            <Link to="/dashboard/quiz" className="dash-section__link">Xem tất cả →</Link>
          </div>
          <div className="dash-quizzes">
            {(data?.pending_quizzes || []).length > 0 ? (
              data.pending_quizzes.slice(0, 3).map((quiz) => (
                <button key={quiz.quiz_id} className="dash-quiz-card" onClick={() => navigate(`/dashboard/quiz/${quiz.quiz_id}`)}>
                  <div className="dash-quiz-card__info">
                    <h4>{quiz.title}</h4>
                    <span className="dash-quiz-card__course">{quiz.course_title}</span>
                    {quiz.lesson_title && <span className="dash-quiz-card__lesson">{quiz.lesson_title}</span>}
                  </div>
                  <div className="dash-quiz-card__right">
                    {quiz.status && (
                      <span className={`dash-quiz-card__status dash-quiz-card__status--${quiz.status}`}>
                        {quiz.status === 'not_started' ? 'Chưa làm' : quiz.status === 'failed' ? 'Chưa đạt' : quiz.status}
                      </span>
                    )}
                    {quiz.due_date && <span className="dash-quiz-card__due">Hạn: {new Date(quiz.due_date).toLocaleDateString('vi-VN')}</span>}
                  </div>
                </button>
              ))
            ) : (
              <StateView type="info" title="Không có quiz cần làm" message="Bạn đã hoàn thành toàn bộ quiz đang mở." />
            )}
          </div>
        </motion.section>
      </div>

      {data?.recommendations?.length > 0 && (
        <motion.section className="dash-section" variants={fadeUp}>
          <div className="dash-section__header">
            <h2 className="dash-section__title">Gợi ý cho bạn</h2>
            <Link to="/dashboard/recommendations" className="dash-section__link">Xem tất cả →</Link>
          </div>
          <div className="dash-recs">
            {data.recommendations.slice(0, 3).map((rec) => (
              <button key={rec.course_id} className="dash-rec-card" onClick={() => navigate(`/dashboard/courses/${rec.course_id}`)}>
                <h4 className="dash-rec-card__title">{rec.title}</h4>
                <p className="dash-rec-card__reason">{rec.reason}</p>
              </button>
            ))}
          </div>
        </motion.section>
      )}
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

const BookIcon = () => <Icon><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" /><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2Z" /></Icon>
const ChartIcon = () => <Icon><line x1="18" y1="20" x2="18" y2="10" /><line x1="12" y1="20" x2="12" y2="4" /><line x1="6" y1="20" x2="6" y2="14" /></Icon>
const StreakIcon = () => <Icon><path d="M12 2s4 4 4 8a4 4 0 1 1-8 0c0-4 4-8 4-8Z" /><path d="M12 14v8" /></Icon>
const ClockIcon = () => <Icon><circle cx="12" cy="12" r="9" /><path d="M12 7v6l4 2" /></Icon>
const Icon = ({ children }) => <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">{children}</svg>

export default StudentDashboard
