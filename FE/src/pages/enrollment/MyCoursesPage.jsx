import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import toast from 'react-hot-toast'
import enrollmentService from '@services/enrollmentService'
import Button from '@components/ui/Button'
import './MyCoursesPage.css'

/**
 * MyCoursesPage - Trang khóa học đã đăng ký của học viên
 * Route: /dashboard/my-courses
 * API: GET /enrollments/my-courses (filter status, pagination skip/limit)
 * Response: EnrollmentListResponse (enrollments[], summary)
 */
const MyCoursesPage = () => {
  const navigate = useNavigate()
  const [enrollments, setEnrollments] = useState([])
  const [summary, setSummary] = useState(null)
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState('') // rỗng = tất cả

  // Lấy danh sách khóa học đã đăng ký, filter theo tab
  useEffect(() => {
    const fetchMyCourses = async () => {
      try {
        setLoading(true)
        const params = {}
        if (activeTab) params.status = activeTab
        const data = await enrollmentService.getMyCourses(params)
        setEnrollments(data?.enrollments || [])
        // Chỉ cập nhật summary lần đầu (khi chưa filter)
        if (data?.summary && !summary) setSummary(data.summary)
      } catch (error) {
        toast.error('Không thể tải danh sách khóa học')
      } finally {
        setLoading(false)
      }
    }
    fetchMyCourses()
  }, [activeTab])

  // Xử lý hủy đăng ký
  const handleCancel = async (enrollmentId, courseTitle) => {
    if (!window.confirm(`Bạn có chắc muốn hủy đăng ký khóa học "${courseTitle}"?`)) return
    try {
      await enrollmentService.cancelEnrollment(enrollmentId)
      toast.success('Đã hủy đăng ký thành công')
      // Cập nhật danh sách bằng cách loại bỏ enrollment đã hủy
      setEnrollments(prev => prev.filter(e => (e.id || e.enrollment_id) !== enrollmentId))
    } catch (error) {
      toast.error(error?.message || 'Không thể hủy đăng ký')
    }
  }

  // Hiển thị thời gian đã học dạng dễ đọc
  const formatStudyTime = (minutes) => {
    if (!minutes) return '0 phút'
    const hours = Math.floor(minutes / 60)
    const mins = minutes % 60
    if (hours > 0) return `${hours}h ${mins > 0 ? `${mins}ph` : ''}`
    return `${mins} phút`
  }

  const fadeUp = { hidden: { opacity: 0, y: 20 }, visible: { opacity: 1, y: 0 } }

  // Tên hiển thị cho các tab
  const tabs = [
    { key: '', label: 'Tất cả', count: summary?.total_enrollments },
    { key: 'in-progress', label: 'Đang học', count: summary?.in_progress },
    { key: 'completed', label: 'Hoàn thành', count: summary?.completed },
    { key: 'cancelled', label: 'Đã hủy', count: summary?.cancelled }
  ]

  return (
    <div className="mc-page">
      <motion.div initial="hidden" animate="visible" variants={fadeUp} transition={{ duration: 0.3 }}>
        <h1 className="mc-header__title">Khóa học của tôi</h1>
        <p className="mc-header__sub">Quản lý và theo dõi các khóa học bạn đã đăng ký</p>
      </motion.div>

      {/* Tabs lọc theo trạng thái */}
      <div className="mc-tabs">
        {tabs.map(tab => (
          <button
            key={tab.key}
            className={`mc-tab ${activeTab === tab.key ? 'mc-tab--active' : ''}`}
            onClick={() => setActiveTab(tab.key)}
          >
            {tab.label}
            {tab.count != null && <span className="mc-tab__count">{tab.count}</span>}
          </button>
        ))}
      </div>

      {/* Trạng thái đang tải */}
      {loading && (
        <div className="mc-list">
          {[1, 2, 3].map(i => <div key={i} className="mc-skeleton" />)}
        </div>
      )}

      {/* Danh sách khóa học */}
      {!loading && enrollments.length > 0 && (
        <motion.div className="mc-list" initial="hidden" animate="visible" variants={{ visible: { transition: { staggerChildren: 0.06 } } }}>
          {enrollments.map((enrollment) => (
            <motion.div key={enrollment.id || enrollment.enrollment_id} className="mc-card" variants={fadeUp}>
              {/* Ảnh đại diện */}
              <div className="mc-card__img-wrap">
                {enrollment.course_thumbnail ? (
                  <img src={enrollment.course_thumbnail} alt="" className="mc-card__img" />
                ) : (
                  <div className="mc-card__img-ph">📚</div>
                )}
              </div>

              {/* Nội dung chính */}
              <div className="mc-card__body">
                <div className="mc-card__top">
                  <h3
                    className="mc-card__title"
                    onClick={() => navigate(`/dashboard/courses/${enrollment.course_id}`)}
                  >
                    {enrollment.course_title}
                  </h3>
                  <span className={`mc-card__status mc-card__status--${enrollment.status}`}>
                    {enrollment.status === 'in-progress' ? 'Đang học'
                      : enrollment.status === 'completed' ? 'Hoàn thành'
                      : 'Đã hủy'}
                  </span>
                </div>

                {/* Thông tin phụ */}
                <div className="mc-card__meta">
                  {enrollment.course_level && (
                    <span className="mc-card__level">{enrollment.course_level}</span>
                  )}
                  {enrollment.instructor_name && (
                    <span>GV: {enrollment.instructor_name}</span>
                  )}
                  {enrollment.enrolled_at && (
                    <span>Đăng ký: {new Date(enrollment.enrolled_at).toLocaleDateString('vi-VN')}</span>
                  )}
                  {enrollment.completed_at && (
                    <span>Hoàn thành: {new Date(enrollment.completed_at).toLocaleDateString('vi-VN')}</span>
                  )}
                  {enrollment.total_time_spent_minutes != null && (
                    <span>Đã học: {formatStudyTime(enrollment.total_time_spent_minutes)}</span>
                  )}
                  {enrollment.avg_quiz_score != null && (
                    <span>Quiz TB: {Math.round(enrollment.avg_quiz_score)}%</span>
                  )}
                </div>

                {/* Thanh tiến độ */}
                {enrollment.status === 'in-progress' && (
                  <div className="mc-card__progress">
                    <div className="mc-card__progress-bar">
                      <div
                        className="mc-card__progress-fill"
                        style={{ width: `${enrollment.progress_percent || 0}%` }}
                      />
                    </div>
                    <span className="mc-card__progress-text">
                      {Math.round(enrollment.progress_percent || 0)}%
                    </span>
                  </div>
                )}

                {/* Hành động */}
                <div className="mc-card__actions">
                  {enrollment.status === 'in-progress' && (
                    <>
                      {enrollment.next_lesson?.lesson_id ? (
                        <>
                          <Button
                            variant="primary"
                            size="sm"
                            onClick={() => navigate(`/dashboard/courses/${enrollment.course_id}/lessons/${enrollment.next_lesson.lesson_id}`)}
                          >
                            Tiếp tục học
                          </Button>
                          {/* Hien thi thong tin bai hoc tiep theo */}
                          {enrollment.next_lesson?.lesson_title && (
                            <span className="mc-card__next-lesson">
                              {enrollment.next_lesson.module_title && `${enrollment.next_lesson.module_title} · `}
                              {enrollment.next_lesson.lesson_title}
                            </span>
                          )}
                        </>
                      ) : (
                        <Button
                          variant="primary"
                          size="sm"
                          onClick={() => navigate(`/dashboard/courses/${enrollment.course_id}/modules`)}
                        >
                          Xem modules
                        </Button>
                      )}
                      <button
                        className="mc-card__cancel-btn"
                        onClick={() => handleCancel(enrollment.id || enrollment.enrollment_id, enrollment.course_title)}
                      >
                        Hủy đăng ký
                      </button>
                    </>
                  )}
                  {enrollment.status === 'completed' && (
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => navigate(`/dashboard/courses/${enrollment.course_id}/modules`)}
                    >
                      Xem lại
                    </Button>
                  )}
                </div>
              </div>
            </motion.div>
          ))}
        </motion.div>
      )}

      {/* Trạng thái rỗng */}
      {!loading && enrollments.length === 0 && (
        <div className="mc-empty">
          <span className="mc-empty__icon">📚</span>
          <h3>Chưa có khóa học nào</h3>
          <p>
            {activeTab === 'completed' ? 'Bạn chưa hoàn thành khóa học nào'
              : activeTab === 'cancelled' ? 'Không có khóa học đã hủy'
              : 'Hãy bắt đầu bằng cách khám phá các khóa học có sẵn'}
          </p>
          <Button variant="primary" onClick={() => navigate('/dashboard/courses')}>
            Khám phá khóa học
          </Button>
        </div>
      )}
    </div>
  )
}

export default MyCoursesPage