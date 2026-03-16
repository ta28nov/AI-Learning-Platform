import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import learningService from '@services/learningService'
import Card, { CardBody } from '@components/ui/Card'
import './ModuleListPage.css'

/**
 * Trang danh sach modules trong khoa hoc
 * Route: /dashboard/courses/:courseId/modules
 * API: GET /courses/{courseId}/modules
 */
const ModuleListPage = () => {
  const { courseId } = useParams()
  const navigate = useNavigate()
  const [modules, setModules] = useState([])
  const [loading, setLoading] = useState(true)

  // Lay danh sach modules khi mount
  useEffect(() => {
    const fetchModules = async () => {
      try {
        setLoading(true)
        const data = await learningService.getCourseModules(courseId)
        setModules(data.modules || [])
      } catch (error) {
        toast.error('Khong the tai danh sach module')
      } finally {
        setLoading(false)
      }
    }
    fetchModules()
  }, [courseId])

  // Chuyen den trang module detail
  const handleModuleClick = (module) => {
    if (module.is_locked) {
      toast.error('Module nay chua duoc mo khoa')
      return
    }
    navigate(`/dashboard/courses/${courseId}/modules/${module.id}`)
  }

  if (loading) return <div className="loading-spinner">Dang tai...</div>

  return (
    <div className="module-list-page">
      <div className="page-header">
        <h1>Noi dung khoa hoc</h1>
        <p>{modules.length} modules</p>
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
                {mod.difficulty && (
                  <span className={`badge badge--${mod.difficulty?.toLowerCase()}`}>
                    {mod.difficulty}
                  </span>
                )}
                <span className="module-card__lessons">{mod.lesson_count} bai hoc</span>
                {mod.estimated_hours && (
                  <span className="module-card__time">~{mod.estimated_hours}h</span>
                )}
              </div>

              {/* Progress bar */}
              {mod.progress_percent !== undefined && mod.progress_percent > 0 && (
                <div className="module-card__progress">
                  <div className="progress-bar">
                    <div
                      className="progress-bar__fill"
                      style={{ width: `${mod.progress_percent}%` }}
                    />
                  </div>
                  <span className="progress-text">{Math.round(mod.progress_percent)}%</span>
                </div>
              )}

              {/* Status dot */}
              <div className={`status-dot status-dot--${mod.status || 'not-started'}`} />
            </CardBody>
          </Card>
        ))}
      </div>

      {modules.length === 0 && !loading && (
        <div className="empty-state">Khoa hoc chua co module nao</div>
      )}
    </div>
  )
}

export default ModuleListPage
