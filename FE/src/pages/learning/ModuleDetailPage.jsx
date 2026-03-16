import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import learningService from '@services/learningService'
import Button from '@components/ui/Button'
import Card, { CardHeader, CardBody } from '@components/ui/Card'

/**
 * Trang chi tiet module (lessons, outcomes, resources)
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
        toast.error('Khong the tai thong tin module')
      } finally {
        setLoading(false)
      }
    }
    fetchModule()
  }, [courseId, moduleId])

  if (loading) return <div style={{ padding: 24, textAlign: 'center' }}>Dang tai...</div>
  if (!module) return <div style={{ padding: 24, textAlign: 'center' }}>Khong tim thay module</div>

  return (
    <div style={{ padding: 16 }}>
      {/* Breadcrumb */}
      <div style={{ display: 'flex', gap: 6, fontSize: '0.75rem', color: '#6b7280', marginBottom: 16, flexWrap: 'wrap' }}>
        <span style={{ cursor: 'pointer', color: '#6366f1' }} onClick={() => navigate(`/dashboard/courses/${courseId}`)}>Khoa hoc</span>
        <span>/</span>
        <span style={{ cursor: 'pointer', color: '#6366f1' }} onClick={() => navigate(`/dashboard/courses/${courseId}/modules`)}>Modules</span>
        <span>/</span>
        <span style={{ fontWeight: 500, color: '#1a1a2e' }}>{module.title}</span>
      </div>

      {/* Header */}
      <div style={{ marginBottom: 20 }}>
        <h1 style={{ fontSize: '1.5rem', fontWeight: 700, marginBottom: 6 }}>{module.title}</h1>
        {module.description && (
          <p style={{ fontSize: '0.85rem', color: '#6b7280', lineHeight: 1.6 }}>{module.description}</p>
        )}
        <div style={{ display: 'flex', gap: 8, marginTop: 8, flexWrap: 'wrap', fontSize: '0.75rem' }}>
          {module.difficulty && (
            <span style={{
              padding: '2px 8px', borderRadius: 10, fontWeight: 600, textTransform: 'uppercase', fontSize: '0.65rem',
              background: module.difficulty === 'Beginner' ? '#dcfce7' : module.difficulty === 'Intermediate' ? '#fef3c7' : '#fecaca',
              color: module.difficulty === 'Beginner' ? '#166534' : module.difficulty === 'Intermediate' ? '#92400e' : '#991b1b'
            }}>
              {module.difficulty}
            </span>
          )}
          {module.estimated_hours && <span style={{ color: '#6b7280' }}>~{module.estimated_hours}h</span>}
          {module.lesson_count && <span style={{ color: '#6b7280' }}>{module.lesson_count} bai hoc</span>}
        </div>
      </div>

      {/* Progress */}
      {module.progress_percent !== undefined && (
        <Card>
          <CardBody>
            <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
              <div style={{ flex: 1, height: 8, background: '#e5e7eb', borderRadius: 4, overflow: 'hidden' }}>
                <div style={{ height: '100%', width: `${module.progress_percent}%`, background: '#6366f1', borderRadius: 4, transition: 'width 0.4s' }} />
              </div>
              <span style={{ fontSize: '0.8rem', fontWeight: 600, color: '#6b7280' }}>{Math.round(module.progress_percent)}%</span>
            </div>
          </CardBody>
        </Card>
      )}

      {/* Lessons list */}
      <Card style={{ marginTop: 12 }}>
        <CardHeader><h3>Danh sach bai hoc</h3></CardHeader>
        <CardBody>
          {module.lessons && module.lessons.length > 0 ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
              {module.lessons.map((lesson, idx) => (
                <div
                  key={lesson.id}
                  onClick={() => {
                    if (lesson.is_locked) {
                      toast.error('Bai hoc nay chua duoc mo khoa')
                      return
                    }
                    navigate(`/dashboard/courses/${courseId}/lessons/${lesson.id}`)
                  }}
                  style={{
                    display: 'flex', alignItems: 'center', gap: 10, padding: '10px 12px',
                    borderRadius: 8, cursor: lesson.is_locked ? 'not-allowed' : 'pointer',
                    opacity: lesson.is_locked ? 0.5 : 1, transition: 'background 0.15s',
                    background: 'transparent'
                  }}
                  onMouseEnter={(e) => { if (!lesson.is_locked) e.currentTarget.style.background = '#f8f9fa' }}
                  onMouseLeave={(e) => { e.currentTarget.style.background = 'transparent' }}
                >
                  <span style={{
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    width: 28, height: 28, borderRadius: '50%', fontSize: '0.75rem', fontWeight: 700, flexShrink: 0,
                    background: lesson.is_completed ? '#10b981' : '#f3f4f6',
                    color: lesson.is_completed ? '#fff' : '#6b7280'
                  }}>
                    {lesson.is_completed ? '✓' : idx + 1}
                  </span>
                  <div style={{ flex: 1 }}>
                    <div style={{ fontWeight: 500, fontSize: '0.85rem' }}>{lesson.title}</div>
                    <div style={{ fontSize: '0.7rem', color: '#6b7280', display: 'flex', gap: 8, marginTop: 2 }}>
                      {lesson.duration_minutes && <span>{lesson.duration_minutes} phut</span>}
                      {lesson.content_type && <span>{lesson.content_type === 'video' ? '🎥' : lesson.content_type === 'text' ? '📝' : '📝🎥'}</span>}
                      {lesson.has_quiz && <span>📋 Quiz</span>}
                    </div>
                  </div>
                  {lesson.is_locked && <span>🔒</span>}
                </div>
              ))}
            </div>
          ) : (
            <p style={{ textAlign: 'center', color: '#6b7280', padding: 20 }}>Chua co bai hoc nao</p>
          )}
        </CardBody>
      </Card>

      {/* Learning Outcomes */}
      {module.learning_outcomes && module.learning_outcomes.length > 0 && (
        <Card style={{ marginTop: 12 }}>
          <CardHeader><h3>Muc tieu hoc tap</h3></CardHeader>
          <CardBody>
            <ul style={{ listStyle: 'none', padding: 0, display: 'flex', flexDirection: 'column', gap: 6 }}>
              {module.learning_outcomes.map((outcome, idx) => (
                <li key={idx} style={{ display: 'flex', gap: 8, fontSize: '0.85rem', alignItems: 'flex-start' }}>
                  <span style={{ color: '#10b981', fontWeight: 700 }}>✓</span>
                  <span>{outcome.outcome || outcome}</span>
                  {outcome.is_mandatory && <span style={{ fontSize: '0.65rem', padding: '1px 6px', background: '#fef3c7', color: '#92400e', borderRadius: 8 }}>Bat buoc</span>}
                </li>
              ))}
            </ul>
          </CardBody>
        </Card>
      )}

      {/* Resources */}
      {module.resources && module.resources.length > 0 && (
        <Card style={{ marginTop: 12 }}>
          <CardHeader><h3>Tai nguyen</h3></CardHeader>
          <CardBody>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
              {module.resources.map((res, idx) => (
                <a
                  key={idx}
                  href={res.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  style={{
                    display: 'flex', alignItems: 'center', gap: 8, padding: '8px 12px',
                    background: '#f8f9fa', borderRadius: 8, textDecoration: 'none', color: '#1a1a2e', fontSize: '0.85rem'
                  }}
                >
                  <span>{res.type === 'pdf' ? '📄' : res.type === 'video' ? '🎥' : res.type === 'code' ? '💻' : '📎'}</span>
                  <span style={{ flex: 1, fontWeight: 500 }}>{res.title}</span>
                  {res.size_mb && <span style={{ fontSize: '0.7rem', color: '#6b7280' }}>{res.size_mb} MB</span>}
                </a>
              ))}
            </div>
          </CardBody>
        </Card>
      )}

      {/* Prerequisites */}
      {module.prerequisites && module.prerequisites.length > 0 && (
        <Card style={{ marginTop: 12 }}>
          <CardHeader><h3>Dieu kien tien quyet</h3></CardHeader>
          <CardBody>
            <ul style={{ margin: 0, paddingLeft: 20, fontSize: '0.85rem', color: '#6b7280' }}>
              {module.prerequisites.map((pre, idx) => <li key={idx} style={{ marginBottom: 4 }}>{pre}</li>)}
            </ul>
          </CardBody>
        </Card>
      )}

      {/* Actions */}
      <div style={{ display: 'flex', gap: 10, marginTop: 16 }}>
        <Button variant="outline" onClick={() => navigate(`/dashboard/courses/${courseId}/modules`)}>
          ← Danh sach modules
        </Button>
      </div>
    </div>
  )
}

export default ModuleDetailPage
