import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import toast from 'react-hot-toast'
import enrollmentService from '@services/enrollmentService'
import Button from '@components/ui/Button'
import StateView from '@components/ui/StateView'
import Modal, { ModalFooter } from '@components/ui/Modal'
import './MyCoursesPage.css'

const BookOpenIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z" />
    <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z" />
  </svg>
)

const ClockIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="10" /><path d="M12 6v6l4 2" />
  </svg>
)

const TrophyIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <path d="M6 9H4.5a2.5 2.5 0 0 1 0-5H6" /><path d="M18 9h1.5a2.5 2.5 0 0 0 0-5H18" />
    <path d="M4 22h16" /><path d="M10 14.66V17c0 .55-.47.98-.97 1.21C7.85 18.75 7 20.24 7 22" />
    <path d="M14 14.66V17c0 .55.47.98.97 1.21C16.15 18.75 17 20.24 17 22" />
    <path d="M18 2H6v7a6 6 0 0 0 12 0V2z" />
  </svg>
)

/**
 * MyCoursesPage - Khóa học đã đăng ký
 * Route: /dashboard/my-courses
 * API: GET /enrollments/my-courses (enrollmentService.getMyCourses) — unchanged
 */
const MyCoursesPage = () => {
  const navigate = useNavigate()
  const [enrollments, setEnrollments] = useState([])
  const [summary, setSummary] = useState(null)
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState('')
  const [cancelTarget, setCancelTarget] = useState(null)

  useEffect(() => {
    const fetchMyCourses = async () => {
      try {
        setLoading(true)
        const params = {}
        if (activeTab) params.status = activeTab
        const data = await enrollmentService.getMyCourses(params)
        setEnrollments(data?.enrollments || [])
        if (data?.summary && !summary) setSummary(data.summary)
      } catch {
        toast.error('Không thể tải danh sách khóa học')
      } finally {
        setLoading(false)
      }
    }
    fetchMyCourses()
  }, [activeTab])

  const handleCancel = async (enrollmentId, courseTitle) => {
    try {
      await enrollmentService.cancelEnrollment(enrollmentId)
      toast.success('Đã hủy đăng ký thành công')
      setCancelTarget(null)
      setEnrollments(prev => prev.filter(e => (e.id || e.enrollment_id) !== enrollmentId))
    } catch (error) {
      toast.error(error?.message || 'Không thể hủy đăng ký')
    }
  }

  const formatStudyTime = (minutes) => {
    if (!minutes) return '0 phút'
    const hours = Math.floor(minutes / 60)
    const mins = minutes % 60
    if (hours > 0) return `${hours}h${mins > 0 ? ` ${mins}ph` : ''}`
    return `${mins} phút`
  }

  const tabs = [
    { key: '', label: 'Tất cả', count: summary?.total_enrollments },
    { key: 'in-progress', label: 'Đang học', count: summary?.in_progress },
    { key: 'completed', label: 'Hoàn thành', count: summary?.completed },
    { key: 'cancelled', label: 'Đã hủy', count: summary?.cancelled },
  ]

  const statusLabel = { 'in-progress': 'Đang học', completed: 'Hoàn thành', cancelled: 'Đã hủy' }
  const emptyMessage = {
    completed: 'Bạn chưa hoàn thành khóa học nào',
    cancelled: 'Không có khóa học đã hủy',
    '': 'Hãy bắt đầu bằng cách khám phá các khóa học có sẵn',
  }

  return (
    <div className="mc-page">
      {/* Header ornament */}
      <motion.div
        className="mc-hero"
        initial={{ opacity: 0, y: 24 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, ease: [0.65, 0, 0.35, 1] }}
      >
        <svg className="mc-ornament" viewBox="0 0 48 12" fill="none">
          <line x1="0" y1="6" x2="16" y2="6" stroke="var(--gold-500)" strokeWidth="1" />
          <circle cx="24" cy="6" r="4" stroke="var(--gold-500)" strokeWidth="1" />
          <line x1="32" y1="6" x2="48" y2="6" stroke="var(--gold-500)" strokeWidth="1" />
        </svg>
        <h1 className="mc-hero__title">Khóa học của tôi</h1>
        <p className="mc-hero__sub">Tiếp tục hành trình học tập, theo dõi tiến độ của bạn</p>
      </motion.div>

      {/* Summary strip */}
      {summary && (
        <motion.div
          className="mc-summary"
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.1 }}
        >
          <div className="mc-summary__stat">
            <span className="mc-summary__icon"><BookOpenIcon /></span>
            <span className="mc-summary__value">{summary.total_enrollments ?? 0}</span>
            <span className="mc-summary__label">Tổng khóa học</span>
          </div>
          <div className="mc-summary__stat">
            <span className="mc-summary__icon mc-summary__icon--progress"><ClockIcon /></span>
            <span className="mc-summary__value">{summary.in_progress ?? 0}</span>
            <span className="mc-summary__label">Đang học</span>
          </div>
          <div className="mc-summary__stat">
            <span className="mc-summary__icon mc-summary__icon--done"><TrophyIcon /></span>
            <span className="mc-summary__value">{summary.completed ?? 0}</span>
            <span className="mc-summary__label">Hoàn thành</span>
          </div>
        </motion.div>
      )}

      {/* Tabs */}
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

      {/* Loading */}
      {loading && <StateView type="loading" message="Đang tải khóa học của bạn…" />}

      {/* List */}
      <AnimatePresence mode="wait">
        {!loading && enrollments.length > 0 && (
          <motion.div
            key={activeTab || 'all'}
            className="mc-list"
            initial="hidden"
            animate="visible"
            exit={{ opacity: 0 }}
            variants={{ visible: { transition: { staggerChildren: 0.07 } } }}
          >
            {enrollments.map((enrollment) => {
              const eid = enrollment.id || enrollment.enrollment_id
              const progress = Math.round(enrollment.progress_percent || 0)
              return (
                <motion.div
                  key={eid}
                  className="mc-card"
                  variants={{ hidden: { opacity: 0, y: 16 }, visible: { opacity: 1, y: 0, transition: { duration: 0.4, ease: [0.65, 0, 0.35, 1] } } }}
                  whileHover={{ y: -2 }}
                >
                  {/* Thumbnail */}
                  <div className="mc-card__img-wrap">
                    {enrollment.course_thumbnail ? (
                      <img src={enrollment.course_thumbnail} alt="" className="mc-card__img" />
                    ) : (
                      <div className="mc-card__img-ph">
                        <BookOpenIcon />
                      </div>
                    )}
                  </div>

                  <div className="mc-card__body">
                    <div className="mc-card__top">
                      <h3
                        className="mc-card__title"
                        onClick={() => navigate(`/dashboard/courses/${enrollment.course_id}`)}
                      >
                        {enrollment.course_title}
                      </h3>
                      <span className={`mc-card__status mc-card__status--${enrollment.status}`}>
                        {statusLabel[enrollment.status] ?? enrollment.status}
                      </span>
                    </div>

                    <div className="mc-card__meta">
                      {enrollment.course_level && <span className="mc-card__level">{enrollment.course_level}</span>}
                      {enrollment.instructor_name && <span>GV: {enrollment.instructor_name}</span>}
                      {enrollment.enrolled_at && (
                        <span>Đăng ký: {new Date(enrollment.enrolled_at).toLocaleDateString('vi-VN')}</span>
                      )}
                      {enrollment.total_time_spent_minutes != null && (
                        <span>Đã học: {formatStudyTime(enrollment.total_time_spent_minutes)}</span>
                      )}
                      {enrollment.avg_quiz_score != null && (
                        <span>Quiz TB: {Math.round(enrollment.avg_quiz_score)}%</span>
                      )}
                    </div>

                    {/* Progress bar — animated on mount */}
                    {enrollment.status === 'in-progress' && (
                      <div className="mc-card__progress">
                        <div className="mc-card__progress-bar">
                          <motion.div
                            className="mc-card__progress-fill"
                            initial={{ width: 0 }}
                            animate={{ width: `${progress}%` }}
                            transition={{ duration: 0.7, delay: 0.2, ease: [0.65, 0, 0.35, 1] }}
                          />
                        </div>
                        <span className="mc-card__progress-text">{progress}%</span>
                      </div>
                    )}

                    <div className="mc-card__actions">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => navigate(`/dashboard/enrollment/${eid}`)}
                      >
                        Chi tiết đăng ký
                      </Button>
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
                            onClick={() => setCancelTarget({ enrollmentId: eid, courseTitle: enrollment.course_title })}
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
              )
            })}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Empty */}
      {!loading && enrollments.length === 0 && (
        <StateView
          type="empty"
          message={emptyMessage[activeTab] ?? 'Chưa có khóa học nào'}
          action={
            activeTab === '' || activeTab === 'in-progress'
              ? { label: 'Khám phá khóa học', onClick: () => navigate('/dashboard/courses') }
              : undefined
          }
        />
      )}
      <Modal
        isOpen={Boolean(cancelTarget)}
        onClose={() => setCancelTarget(null)}
        title="Hủy đăng ký khóa học"
        size="sm"
      >
        <p>Bạn có chắc muốn hủy đăng ký "{cancelTarget?.courseTitle}"?</p>
        <ModalFooter>
          <Button variant="outline" onClick={() => setCancelTarget(null)}>Giữ lại</Button>
          <Button variant="danger" onClick={() => handleCancel(cancelTarget.enrollmentId, cancelTarget.courseTitle)}>Hủy đăng ký</Button>
        </ModalFooter>
      </Modal>
    </div>
  )
}

export default MyCoursesPage
