import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { motion, useReducedMotion } from 'framer-motion'
import toast from 'react-hot-toast'
import learningService from '@services/learningService'
import Card, { CardHeader, CardBody } from '@components/ui/Card'
import StateView from '@components/ui/StateView'
import ClassLearningBanner from '@components/classes/ClassLearningBanner'
import CourseLearningNav from './CourseLearningNav'
import ChatWidget from '@components/chat/ChatWidget'
import { fadeUp, staggerEditorial } from '@/styles/motion'
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
  const shouldReduceMotion = useReducedMotion()

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
  if (!module) return <StateView type="empty" title="Không tìm thấy module" message="Vui lòng quay lại danh sách modules." actionLabel="Danh sách modules" onAction={() => navigate(`/dashboard/courses/${courseId}/modules`)} />

  return (
    <div className="module-detail-page">
      <ClassLearningBanner />
      {/* Breadcrumb điều hướng */}
      <div className="module-detail-breadcrumb">
        <button type="button" className="module-detail-breadcrumb__link" onClick={() => navigate(`/dashboard/courses/${courseId}`)}>
          Khóa học
        </button>
        <span className="module-detail-breadcrumb__sep">/</span>
        <button type="button" className="module-detail-breadcrumb__link" onClick={() => navigate(`/dashboard/courses/${courseId}/modules`)}>
          Danh sách module
        </button>
        <span className="module-detail-breadcrumb__sep">/</span>
        <span className="module-detail-breadcrumb__current">{module.title}</span>
      </div>

      {/* Header module */}
      <motion.div className="module-detail-header" variants={fadeUp} initial={shouldReduceMotion ? false : 'hidden'} animate="show">
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
      </motion.div>

      <div className="module-detail-layout">
      <div>
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
      <motion.div variants={staggerEditorial} initial={shouldReduceMotion ? false : 'hidden'} animate="show">
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
                        <span>{contentTypeLabel(lesson.content_type)}</span>
                      )}
                      {lesson.has_quiz && <span>Quiz</span>}
                    </div>
                  </div>
                  {lesson.is_locked && <span className="module-detail-lesson__lock"><LockIcon /></span>}
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
                  <span className="module-detail-outcome__check"><CheckIcon /></span>
                  <span>{getOutcomeText(outcome)}</span>
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
                  <span>{resourceTypeLabel(res.type)}</span>
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
              {module.prerequisites.map((pre, idx) => <li key={idx}>{getPrerequisiteText(pre)}</li>)}
            </ul>
          </CardBody>
        </Card>
      )}

      <CourseLearningNav courseId={courseId} moduleId={moduleId} />
      </motion.div>
      </div>

      <aside className="module-detail-side">
        <Card className="module-detail-sidecard">
          <CardHeader><h3>Tóm tắt module</h3></CardHeader>
          <CardBody>
            <ul className="module-detail-side__list">
              <li><strong>{module.total_lessons || module.lessons?.length || 0}</strong> bài học</li>
              <li><strong>{module.estimated_hours || 0}h</strong> ước lượng</li>
              <li><strong>{Math.round(module.progress_percent || 0)}%</strong> hoàn thành</li>
            </ul>
          </CardBody>
        </Card>
      </aside>
      </div>

      <ChatWidget
        contextType="module"
        subtitle={`Hỏi về module «${module.title}»`}
        contextMeta={{ moduleTitle: module.title, moduleId }}
        suggestions={[
          `Tóm tắt module «${module.title}»`,
          'Giải thích mục tiêu học tập của module này',
          'Gợi ý thứ tự học các bài trong module',
        ]}
      />
    </div>
  )
}

const getOutcomeText = (outcome) => {
  if (!outcome) return ''
  if (typeof outcome === 'string') return outcome
  if (typeof outcome === 'object') return outcome.outcome || outcome.description || outcome.skill_tag || ''
  return String(outcome)
}

const getPrerequisiteText = (pre) => {
  if (!pre) return ''
  if (typeof pre === 'string') return pre
  if (typeof pre === 'object') {
    const title = pre.title || pre.name
    if (title && title !== pre.id) return title
    if (pre.id && /^[0-9a-f-]{36}$/i.test(String(pre.id))) {
      return 'Module tiên quyết'
    }
    return title || pre.id || ''
  }
  return String(pre)
}

const contentTypeLabel = (type) => {
  if (type === 'video') return 'Video'
  if (type === 'text') return 'Văn bản'
  return 'Mixed'
}
const resourceTypeLabel = (type) => {
  if (type === 'pdf') return 'PDF'
  if (type === 'video') return 'Video'
  if (type === 'code') return 'Code'
  return 'Tài liệu'
}
const CheckIcon = () => <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="m20 6-11 11-5-5"/></svg>
const LockIcon = () => <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="4" y="11" width="16" height="9" rx="2"/><path d="M8 11V8a4 4 0 1 1 8 0v3"/></svg>

export default ModuleDetailPage
