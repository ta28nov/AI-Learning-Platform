import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import learningService from '@services/learningService'
import Card, { CardBody } from '@components/ui/Card'
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
      <div className="module-list-page__header">
        <h1>Nội dung khóa học</h1>
        <p>{modules.length} module</p>
      </div>

      <div className="module-list">
        {modules.map((mod, idx) => (
          <Card
            key={mod.id}
            hover
            className={`module-card ${mod.is_locked ? 'module-card--locked' : ''}`}
            onClick={() => handleModuleClick(mod)}
          >
            <CardBody>
              <div className="module-card__header">
                <span className="module-card__order">{idx + 1}</span>
                <div className="module-card__info">
                  <h3 className="module-card__title">{mod.title}</h3>
                  {mod.description && (
                    <p className="module-card__desc">{mod.description}</p>
                  )}
                </div>
                {mod.is_locked && <span className="module-card__lock">🔒</span>}
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
            </CardBody>
          </Card>
        ))}
      </div>

      {modules.length === 0 && !loading && (
        <div className="module-list-page__empty">Khóa học chưa có module nào</div>
      )}
    </div>
  )
}

export default ModuleListPage
