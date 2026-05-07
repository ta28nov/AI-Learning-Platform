import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { motion, useReducedMotion } from 'framer-motion'
import toast from 'react-hot-toast'
import learningService from '@services/learningService'
import StateView from '@components/ui/StateView'
import { fadeUp, staggerEditorial } from '@/styles/motion'
import './ModuleListPage.css'

/**
 * Trang danh sách modules trong khóa học
 * Route: /dashboard/courses/:courseId/modules
 * API: GET /courses/{courseId}/modules
 */
const ModuleListPage = () => {
  const { courseId } = useParams()
  const navigate = useNavigate()
  const [modules, setModules] = useState([])
  const [loading, setLoading] = useState(true)
  const shouldReduceMotion = useReducedMotion()

  // Lấy danh sách modules khi mount
  useEffect(() => {
    const fetchModules = async () => {
      try {
        setLoading(true)
        const data = await learningService.getCourseModules(courseId)
        setModules(data.modules || [])
      } catch (error) {
        toast.error('Không thể tải danh sách module')
      } finally {
        setLoading(false)
      }
    }
    fetchModules()
  }, [courseId])

  // Chuyển đến trang module detail, kiểm tra locked trước
  const handleModuleClick = (module) => {
    if (module.is_locked) {
      toast.error('Module này chưa được mở khóa')
      return
    }
    navigate(`/dashboard/courses/${courseId}/modules/${module.id}`)
  }

  if (loading) return <div className="module-list-page__loading">Đang tải...</div>

  return (
    <div className="module-list-page">
      <motion.div className="module-list-page__header" variants={fadeUp} initial={shouldReduceMotion ? false : 'hidden'} animate="show">
        <div className="module-list-page__ornament" aria-hidden="true">
          <span className="module-list-page__line" />
          <SparkIcon />
          <span className="module-list-page__line" />
        </div>
        <h1>Nội dung khóa học</h1>
        <p>{modules.length} module</p>
      </motion.div>

      <motion.div className="module-list" variants={staggerEditorial} initial={shouldReduceMotion ? false : 'hidden'} animate="show">
        {modules.map((mod, idx) => (
          <motion.button
            key={mod.id}
            className={`module-card ${mod.is_locked ? 'module-card--locked' : ''}`}
            onClick={() => handleModuleClick(mod)}
            variants={fadeUp}
            whileHover={shouldReduceMotion || mod.is_locked ? undefined : { y: -3, rotateX: -1.3, rotateY: 1.3 }}
            transition={{ duration: 0.2 }}
          >
            <div className="module-card__body">
              <div className="module-card__header">
                <span className="module-card__order">{idx + 1}</span>
                <div className="module-card__info">
                  <h3 className="module-card__title">{mod.title}</h3>
                  {mod.description && (
                    <p className="module-card__desc">{mod.description}</p>
                  )}
                </div>
                {mod.is_locked && <span className="module-card__lock"><LockIcon /></span>}
              </div>

              <div className="module-card__meta">
                {/* Badge độ khó — dùng module-card__badge thay .badge chung */}
                {mod.difficulty && (
                  <span className={`module-card__badge module-card__badge--${mod.difficulty?.toLowerCase()}`}>
                    {mod.difficulty}
                  </span>
                )}
                <span className="module-card__lessons">{mod.lesson_count} bài học</span>
                {mod.estimated_hours && (
                  <span className="module-card__time">~{mod.estimated_hours}h</span>
                )}
              </div>

              {/* Thanh tiến độ — dùng module-card__progress-bar thay .progress-bar */}
              {mod.progress_percent !== undefined && mod.progress_percent > 0 && (
                <div className="module-card__progress">
                  <div className="module-card__progress-bar">
                    <div
                      className="module-card__progress-fill"
                      style={{ width: `${mod.progress_percent}%` }}
                    />
                  </div>
                  <span className="module-card__progress-text">{Math.round(mod.progress_percent)}%</span>
                </div>
              )}

              {/* Status dot — dùng module-card__status-dot thay .status-dot */}
              <div className={`module-card__status-dot module-card__status-dot--${mod.status || 'not-started'}`} />
            </div>
          </motion.button>
        ))}
      </motion.div>

      {modules.length === 0 && !loading && (
        <StateView
          type="empty"
          title="Khóa học chưa có module nào"
          message="Nội dung sẽ được cập nhật sớm."
          actionLabel="Quay lại khóa học"
          onAction={() => navigate(`/dashboard/courses/${courseId}`)}
        />
      )}
    </div>
  )
}

const SparkIcon = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
    <path d="m12 2 2.8 7.2L22 12l-7.2 2.8L12 22l-2.8-7.2L2 12l7.2-2.8L12 2Z" />
  </svg>
)
const LockIcon = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round">
    <rect x="4" y="11" width="16" height="9" rx="2" />
    <path d="M8 11V8a4 4 0 1 1 8 0v3" />
  </svg>
)

export default ModuleListPage
