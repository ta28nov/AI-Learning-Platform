import { useState, useEffect, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import toast from 'react-hot-toast'
import classService from '@services/classService'
import { useAuthStore } from '@stores/authStore'
import Button from '@components/ui/Button'
import StateView from '@components/ui/StateView'
import JoinClassModal from '@components/classes/JoinClassModal'
import { navigateToCourseLearning } from '@utils/classLearningContext'

const UsersIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
    <circle cx="9" cy="7" r="4"/>
    <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
    <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
  </svg>
)
const KeyIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <path d="m21 2-2 2m-7.61 7.61a5.5 5.5 0 1 1-7.778 7.778 5.5 5.5 0 0 1 7.777-7.777zm0 0L15.5 7.5m0 0 3 3L22 7l-3-3m-3.5 3.5L19 4"/>
  </svg>
)
const PlusIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <path d="M12 5v14M5 12h14"/>
  </svg>
)

/**
 * ClassListPage — Danh sách lớp học
 * Route: /dashboard/instructor/classes (InstructorRoute)
 * API: GET /classes/my-classes via classService.getMyClasses — unchanged
 */
const ClassListPage = () => {
  const navigate = useNavigate()
  const { user } = useAuthStore()
  const [classes, setClasses] = useState([])
  const [loading, setLoading] = useState(true)
  const [joinModalOpen, setJoinModalOpen] = useState(false)

  const fetchClasses = useCallback(async () => {
    try {
      setLoading(true)
      const data = await classService.getMyClasses()
      setClasses(data.classes || data || [])
    } catch {
      toast.error('Không thể tải danh sách lớp học')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { fetchClasses() }, [fetchClasses])

  const statusLabel = { active: 'Đang hoạt động', completed: 'Đã kết thúc', preparing: 'Chuẩn bị', cancelled: 'Đã hủy' }
  const statusClass = { active: 'cls-card__status--active', completed: 'cls-card__status--completed', cancelled: 'cls-card__status--cancelled', preparing: 'cls-card__status--preparing' }

  return (
    <div className="cls-page">
      {/* Hero */}
      <motion.div className="cls-hero" initial={{ opacity: 0, y: 24 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5, ease: [0.65, 0, 0.35, 1] }}>
        <svg className="cls-ornament" viewBox="0 0 48 12" fill="none">
          <line x1="0" y1="6" x2="16" y2="6" stroke="var(--gold-500)" strokeWidth="1"/>
          <circle cx="24" cy="6" r="4" stroke="var(--gold-500)" strokeWidth="1"/>
          <line x1="32" y1="6" x2="48" y2="6" stroke="var(--gold-500)" strokeWidth="1"/>
        </svg>
        <div className="cls-hero__text">
          <h1 className="cls-hero__title">Lớp học của tôi</h1>
          <p className="cls-hero__count">{classes.length} lớp học</p>
        </div>
        <div className="cls-hero__actions">
          {user?.role === 'student' && (
            <Button variant="outline" onClick={() => setJoinModalOpen(true)}>
              <KeyIcon /> Tham gia lớp
            </Button>
          )}
          {(user?.role === 'instructor' || user?.role === 'admin') && (
            <Button onClick={() => navigate('/dashboard/instructor/classes/create')}>
              <PlusIcon /> Tạo lớp mới
            </Button>
          )}
        </div>
      </motion.div>

      {/* Loading */}
      {loading && <StateView type="loading" message="Đang tải danh sách lớp học…" />}

      {/* Grid */}
      {!loading && classes.length > 0 && (
        <motion.div
          className="cls-grid"
          initial="hidden"
          animate="visible"
          variants={{ visible: { transition: { staggerChildren: 0.07 } } }}
        >
          {classes.map((cls) => {
            const id = cls.id || cls.class_id
            const courseId = cls.course_id
            const isStudent = user?.role === 'student'
            return (
            <motion.div
              key={id}
              className="cls-card"
              variants={{ hidden: { opacity: 0, y: 16 }, visible: { opacity: 1, y: 0, transition: { duration: 0.4, ease: [0.65, 0, 0.35, 1] } } }}
              whileHover={{ y: -3 }}
              onClick={() => {
                if (user?.role === 'instructor' || user?.role === 'admin') {
                  navigate(`/dashboard/instructor/classes/${id}`)
                } else {
                  navigate(`/dashboard/classes/${id}`)
                }
              }}
              style={{ cursor: 'pointer' }}
            >
              <div className="cls-card__top">
                <h3 className="cls-card__name">{cls.name}</h3>
                <span className={`cls-card__status ${statusClass[cls.status] || ''}`}>
                  {statusLabel[cls.status] || cls.status || 'Không rõ'}
                </span>
              </div>

              {cls.course_title && <p className="cls-card__course">{cls.course_title}</p>}
              {isStudent && cls.instructor_name && (
                <p className="cls-card__course">GV: {cls.instructor_name}</p>
              )}

              <div className="cls-card__meta">
                <span className="cls-card__meta-item">
                  <UsersIcon /> {cls.student_count ?? 0} học viên
                </span>
                {cls.start_date && (
                  <span className="cls-card__meta-item">
                    Bắt đầu: {new Date(cls.start_date).toLocaleDateString('vi-VN')}
                  </span>
                )}
              </div>

              {cls.progress != null && (
                <div className="cls-card__progress">
                  <div className="cls-card__progress-bar">
                    <div className="cls-card__progress-fill" style={{ width: `${cls.progress}%` }} />
                  </div>
                  <span className="cls-card__progress-pct">{Math.round(cls.progress)}%</span>
                </div>
              )}

              {isStudent && courseId && (
                <div className="cls-card__actions">
                  <Button
                    size="sm"
                    onClick={(e) => {
                      e.stopPropagation()
                      navigateToCourseLearning(navigate, {
                        courseId,
                        classId: id,
                        className: cls.name,
                        instructorName: cls.instructor_name,
                        nextLesson: cls.next_lesson,
                        resume: true,
                      })
                    }}
                  >
                    {(cls.progress ?? 0) > 0 ? 'Tiếp tục học' : 'Bắt đầu học'}
                  </Button>
                </div>
              )}
            </motion.div>
          )})}
        </motion.div>
      )}

      {/* Empty */}
      {!loading && classes.length === 0 && (
        <StateView
          type="empty"
          message={user?.role === 'student' ? 'Bạn chưa tham gia lớp học nào' : 'Bạn chưa có lớp học nào'}
          action={
            user?.role === 'student'
              ? { label: 'Tham gia bằng mã mời', onClick: () => setJoinModalOpen(true) }
              : { label: 'Tạo lớp mới', onClick: () => navigate('/dashboard/instructor/classes/create') }
          }
        />
      )}

      <JoinClassModal
        isOpen={joinModalOpen}
        onClose={() => setJoinModalOpen(false)}
        onSuccess={() => fetchClasses()}
      />
    </div>
  )
}

export default ClassListPage
