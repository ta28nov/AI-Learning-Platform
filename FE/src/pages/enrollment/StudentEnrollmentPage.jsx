import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import toast from 'react-hot-toast'
import enrollmentService from '@services/enrollmentService'
import Button from '@components/ui/Button'
import StateView from '@components/ui/StateView'
import Modal from '@components/ui/Modal'
import './StudentEnrollmentPage.css'

const ClockIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>
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
const ProgressIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <path d="M12 20V10"/><path d="M18 20V4"/><path d="M6 20v-4"/>
  </svg>
)

/**
 * StudentEnrollmentPage — Chi tiết đăng ký khóa học
 * Route: /dashboard/enrollment/:enrollmentId
 * API: GET /enrollments/{enrollmentId} via enrollmentService.getEnrollmentDetail — unchanged
 */
const StudentEnrollmentPage = () => {
  const { enrollmentId } = useParams()
  const navigate = useNavigate()
  const [enrollment, setEnrollment] = useState(null)
  const [loading, setLoading] = useState(true)
  const [showCancelModal, setShowCancelModal] = useState(false)
  const [cancelling, setCancelling] = useState(false)

  useEffect(() => {
    const fetchDetail = async () => {
      try {
        setLoading(true)
        const data = await enrollmentService.getEnrollmentDetail(enrollmentId)
        setEnrollment(data)
      } catch {
        toast.error('Không thể tải thông tin đăng ký')
      } finally {
        setLoading(false)
      }
    }
    if (enrollmentId) fetchDetail()
  }, [enrollmentId])

  const handleCancel = async () => {
    try {
      setCancelling(true)
      await enrollmentService.cancelEnrollment(enrollmentId)
      toast.success('Đã hủy đăng ký thành công')
      navigate('/dashboard/my-courses')
    } catch (error) {
      toast.error(error?.message || 'Không thể hủy đăng ký')
    } finally {
      setCancelling(false)
      setShowCancelModal(false)
    }
  }

  const formatStudyTime = (minutes) => {
    if (!minutes) return '0 phút'
    const h = Math.floor(minutes / 60)
    const m = minutes % 60
    return h > 0 ? `${h}h${m > 0 ? ` ${m}ph` : ''}` : `${m} phút`
  }

  if (loading) return <div className="se-page"><StateView type="loading" message="Đang tải thông tin đăng ký…" /></div>
  if (!enrollment) return (
    <div className="se-page">
      <StateView type="empty" message="Không tìm thấy thông tin đăng ký" action={{ label: 'Quay lại', onClick: () => navigate('/dashboard/my-courses') }} />
    </div>
  )

  const progress = Math.round(enrollment.progress_percent || 0)
  const statusLabel = { 'in-progress': 'Đang học', completed: 'Hoàn thành', cancelled: 'Đã hủy' }

  return (
    <div className="se-page">
      {/* Header */}
      <motion.div
        className="se-header"
        initial={{ opacity: 0, y: 24 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, ease: [0.65, 0, 0.35, 1] }}
      >
        <button className="se-back" onClick={() => navigate('/dashboard/my-courses')}>
          <svg viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.5">
            <path d="M15 10H5m0 0 5-5M5 10l5 5" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
          Khóa học của tôi
        </button>

        <div className="se-header__title-row">
          <h1 className="se-header__title">{enrollment.course_title || 'Chi tiết đăng ký'}</h1>
          <span className={`se-status se-status--${enrollment.status}`}>
            {statusLabel[enrollment.status] ?? enrollment.status}
          </span>
        </div>
        {enrollment.instructor_name && (
          <p className="se-header__instructor">Giảng viên: {enrollment.instructor_name}</p>
        )}
      </motion.div>

      {/* Stats strip */}
      <motion.div
        className="se-stats"
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.45, delay: 0.1 }}
      >
        <div className="se-stat">
          <span className="se-stat__icon"><ProgressIcon /></span>
          <span className="se-stat__value">{progress}%</span>
          <span className="se-stat__label">Tiến độ</span>
        </div>
        {enrollment.total_time_spent_minutes != null && (
          <div className="se-stat">
            <span className="se-stat__icon"><ClockIcon /></span>
            <span className="se-stat__value">{formatStudyTime(enrollment.total_time_spent_minutes)}</span>
            <span className="se-stat__label">Đã học</span>
          </div>
        )}
        {enrollment.avg_quiz_score != null && (
          <div className="se-stat">
            <span className="se-stat__icon"><TrophyIcon /></span>
            <span className="se-stat__value">{Math.round(enrollment.avg_quiz_score)}%</span>
            <span className="se-stat__label">Quiz TB</span>
          </div>
        )}
      </motion.div>

      {/* Progress bar */}
      {enrollment.status === 'in-progress' && (
        <motion.div
          className="se-progress"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
        >
          <div className="se-progress__bar">
            <motion.div
              className="se-progress__fill"
              initial={{ width: 0 }}
              animate={{ width: `${progress}%` }}
              transition={{ duration: 0.8, delay: 0.35, ease: [0.65, 0, 0.35, 1] }}
            />
          </div>
          <span className="se-progress__text">{progress}% hoàn thành</span>
        </motion.div>
      )}

      {/* Next lesson */}
      {enrollment.next_lesson?.lesson_id && (
        <motion.div
          className="se-next"
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.25 }}
        >
          <p className="se-next__label">Tiếp tục từ</p>
          <p className="se-next__lesson">
            {enrollment.next_lesson.module_title && `${enrollment.next_lesson.module_title} · `}
            {enrollment.next_lesson.lesson_title}
          </p>
        </motion.div>
      )}

      {/* Actions */}
      <motion.div
        className="se-actions"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.3 }}
      >
        {enrollment.status === 'in-progress' && (
          <>
            <Button
              variant="primary"
              size="lg"
              onClick={() => {
                if (enrollment.next_lesson?.lesson_id) {
                  navigate(`/dashboard/courses/${enrollment.course_id}/lessons/${enrollment.next_lesson.lesson_id}`)
                } else {
                  navigate(`/dashboard/courses/${enrollment.course_id}/modules`)
                }
              }}
            >
              Tiếp tục học
            </Button>
            <Button variant="outline" size="lg" onClick={() => navigate(`/dashboard/courses/${enrollment.course_id}`)}>
              Thông tin khóa học
            </Button>
            <button className="se-cancel-link" onClick={() => setShowCancelModal(true)}>
              Hủy đăng ký
            </button>
          </>
        )}
        {enrollment.status === 'completed' && (
          <Button variant="outline" onClick={() => navigate(`/dashboard/courses/${enrollment.course_id}/modules`)}>
            Xem lại khóa học
          </Button>
        )}
      </motion.div>

      {/* Cancel modal */}
      <Modal isOpen={showCancelModal} onClose={() => setShowCancelModal(false)} title="Xác nhận hủy đăng ký">
        <p style={{ fontSize: '0.9rem', color: 'var(--ink-400)', marginBottom: 'var(--space-5)' }}>
          Bạn có chắc muốn hủy đăng ký khóa học <strong style={{ color: 'var(--ink-900)' }}>{enrollment.course_title}</strong>? Tiến độ học tập sẽ bị mất.
        </p>
        <div style={{ display: 'flex', gap: 'var(--space-3)', justifyContent: 'flex-end' }}>
          <Button variant="outline" onClick={() => setShowCancelModal(false)}>Không, giữ lại</Button>
          <Button variant="primary" loading={cancelling} onClick={handleCancel}>Xác nhận hủy</Button>
        </div>
      </Modal>
    </div>
  )
}

export default StudentEnrollmentPage
