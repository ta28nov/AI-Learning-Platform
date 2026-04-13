import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import learningService from '@services/learningService'
import Button from '@components/ui/Button'
import Card, { CardHeader, CardBody } from '@components/ui/Card'
import './ModuleDetailPage.css'

/**
 * Trang chi tiết module (lessons, outcomes, resources)
 * Route: /dashboard/courses/:courseId/modules/:moduleId
 * API: GET /courses/{courseId}/modules/{moduleId}
 */
const ModuleDetailPage = () => {
  const { courseId, moduleId } = useParams()
  const navigate = useNavigate()
  const [module, setModule] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchModule = async () => {
      try {
        setLoading(true)
        const data = await learningService.getModuleDetail(courseId, moduleId)
        setModule(data)
      } catch (error) {
        toast.error('Không thể tải thông tin module')
      } finally {
        setLoading(false)
      }
    }
    fetchModule()
  }, [courseId, moduleId])

  if (loading) return <div className="module-detail-state">Đang tải...</div>
  if (!module) return <div className="module-detail-state">Không tìm thấy module</div>

  return (
    <div className="module-detail-page">
      {/* Breadcrumb điều hướng */}
      <div className="module-detail-breadcrumb">
        <button className="module-detail-breadcrumb__link" onClick={() => navigate(`/dashboard/courses/${courseId}`)}>
          Khóa học
        </button>
        <span className="module-detail-breadcrumb__sep">/</span>
        <button className="module-detail-breadcrumb__link" onClick={() => navigate(`/dashboard/courses/${courseId}/modules`)}>
          Modules
        </button>
        <span className="module-detail-breadcrumb__sep">/</span>
        <span className="module-detail-breadcrumb__current">{module.title}</span>
      </div>

      {/* Header module */}
      <div className="module-detail-header">
        <h1 className="module-detail-header__title">{module.title}</h1>
        {module.description && (
          <p className="module-detail-header__desc">{module.description}</p>
        )}
        <div className="module-detail-header__badges">
          {module.difficulty && (
            <span className={`module-detail-badge module-detail-badge--${module.difficulty}`}>
              {module.difficulty}
            </span>
          )}
          {module.estimated_hours && (
            <span className="module-detail-header__meta">~{module.estimated_hours} giờ</span>
          )}
          {module.total_lessons && (
            <span className="module-detail-header__meta">{module.total_lessons} bài học</span>
          )}
        </div>
      </div>

      {/* Thanh tiến độ */}
      {module.progress_percent !== undefined && (
        <Card>
          <CardBody>
            <div className="module-detail-progress">
              <div className="module-detail-progress__bar">
                <div
                  className="module-detail-progress__fill"
                  style={{ width: `${module.progress_percent}%` }}
                />
              </div>
              <span className="module-detail-progress__text">
                {Math.round(module.progress_percent)}%
              </span>
            </div>
          </CardBody>
        </Card>
      )}

      {/* Danh sách bài học */}
      <Card className="module-detail-section">
        <CardHeader><h3>Danh sách bài học</h3></CardHeader>
        <CardBody>
          {module.lessons && module.lessons.length > 0 ? (
            <div className="module-detail-lessons">
              {module.lessons.map((lesson, idx) => (
                <div
                  key={lesson.id}
                  className={`module-detail-lesson ${lesson.is_locked ? 'module-detail-lesson--locked' : ''}`}
                  onClick={() => {
                    if (lesson.is_locked) {
                      toast.error('Bài học này chưa được mở khóa')
                      return
                    }
                    navigate(`/dashboard/courses/${courseId}/lessons/${lesson.id}`)
                  }}
                >
                  <span className={`module-detail-lesson__number ${lesson.is_completed ? 'module-detail-lesson__number--completed' : 'module-detail-lesson__number--default'}`}>
                    {lesson.is_completed ? '✓' : idx + 1}
                  </span>
                  <div className="module-detail-lesson__info">
                    <div className="module-detail-lesson__title">{lesson.title}</div>
                    <div className="module-detail-lesson__meta">
                      {lesson.duration_minutes && <span>{lesson.duration_minutes} phút</span>}
                      {lesson.content_type && (
                        <span>{lesson.content_type === 'video' ? '🎥' : lesson.content_type === 'text' ? '📝' : '📝🎥'}</span>
                      )}
                      {lesson.has_quiz && <span>📋 Quiz</span>}
                    </div>
                  </div>
                  {lesson.is_locked && <span className="module-detail-lesson__lock">🔒</span>}
                </div>
              ))}
            </div>
          ) : (
            <p className="module-detail-empty">Chưa có bài học nào</p>
          )}
        </CardBody>
      </Card>

      {/* Mục tiêu học tập */}
      {module.learning_outcomes && module.learning_outcomes.length > 0 && (
        <Card className="module-detail-section">
          <CardHeader><h3>Mục tiêu học tập</h3></CardHeader>
          <CardBody>
            <ul className="module-detail-outcomes">
              {module.learning_outcomes.map((outcome, idx) => (
                <li key={idx} className="module-detail-outcome">
                  <span className="module-detail-outcome__check">✓</span>
                  <span>{outcome.outcome || outcome}</span>
                  {outcome.is_mandatory && (
                    <span className="module-detail-outcome__mandatory">Bắt buộc</span>
                  )}
                </li>
              ))}
            </ul>
          </CardBody>
        </Card>
      )}

      {/* Tài nguyên học tập */}
      {module.resources && module.resources.length > 0 && (
        <Card className="module-detail-section">
          <CardHeader><h3>Tài nguyên</h3></CardHeader>
          <CardBody>
            <div className="module-detail-resources">
              {module.resources.map((res, idx) => (
                <a
                  key={idx}
                  href={res.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="module-detail-resource"
                >
                  <span>{res.type === 'pdf' ? '📄' : res.type === 'video' ? '🎥' : res.type === 'code' ? '💻' : '📎'}</span>
                  <span className="module-detail-resource__title">{res.title}</span>
                  {res.size_mb && <span className="module-detail-resource__size">{res.size_mb} MB</span>}
                </a>
              ))}
            </div>
          </CardBody>
        </Card>
      )}

      {/* Điều kiện tiên quyết */}
      {module.prerequisites && module.prerequisites.length > 0 && (
        <Card className="module-detail-section">
          <CardHeader><h3>Điều kiện tiên quyết</h3></CardHeader>
          <CardBody>
            <ul className="module-detail-prerequisites">
              {module.prerequisites.map((pre, idx) => <li key={idx}>{pre}</li>)}
            </ul>
          </CardBody>
        </Card>
      )}

      {/* Điều hướng */}
      <div className="module-detail-actions">
        <Button variant="outline" onClick={() => navigate(`/dashboard/courses/${courseId}/modules`)}>
          ← Danh sách modules
        </Button>
      </div>
    </div>
  )
}

export default ModuleDetailPage
