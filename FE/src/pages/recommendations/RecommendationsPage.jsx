import { useState, useEffect, useMemo, useCallback } from 'react'
import { useNavigate, useSearchParams, Link } from 'react-router-dom'
import { motion, useReducedMotion } from 'framer-motion'
import toast from 'react-hot-toast'
import recommendationService from '@services/recommendationService'
import assessmentService from '@services/assessmentService'
import Button from '@components/ui/Button'
import StateView from '@components/ui/StateView'
import AILoadingState from '@components/ui/AILoadingState'
import './RecommendationsPage.css'

/**
 * Trang đề xuất lộ trình học tập
 * Route: /dashboard/recommendations?session_id= (optional — có = theo phiên đánh giá)
 */

const ArrowRightIcon = () => (
  <svg viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
    <path
      fillRule="evenodd"
      d="M3 10a.75.75 0 0 1 .75-.75h10.638L10.23 5.29a.75.75 0 1 1 1.04-1.08l5.5 5.25a.75.75
      0 0 1 0 1.08l-5.5 5.25a.75.75 0 1 1-1.04-1.08l4.158-3.96H3.75A.75.75 0 0 1 3 10Z"
      clipRule="evenodd"
    />
  </svg>
)

const ChartIcon = () => (
  <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="1.5" aria-hidden>
    <path d="M3 3v18h18" />
    <path d="M7 12v5M12 8v9M17 5v12" />
  </svg>
)

const ClipboardIcon = () => (
  <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="1.5" aria-hidden>
    <rect x="8" y="2" width="8" height="4" rx="1" />
    <path d="M8 4H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2h-2" />
  </svg>
)

const BookIcon = () => (
  <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="1.5" aria-hidden>
    <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" />
    <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z" />
  </svg>
)

function formatSessionWhen(iso) {
  if (!iso) return ''
  try {
    return new Date(iso).toLocaleString('vi-VN', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
    })
  } catch {
    return ''
  }
}

/** Ẩn mô tả seed lorem — chỉ hiện lý do AI hoặc mô tả thật */
function isPlaceholderDescription(text) {
  if (!text || typeof text !== 'string') return true
  const t = text.trim()
  if (t.length < 20) return true
  return /^(lorem|dignissimos|earum non|harum unde|maxime amet|sit animi)/i.test(t)
}

function courseTitleById(courses, courseId) {
  const hit = courses.find((c) => c.course_id === courseId)
  return hit?.title || 'Khóa học đề xuất'
}

const RecommendationsPage = () => {
  const navigate = useNavigate()
  const prefersReduced = useReducedMotion()
  const [searchParams] = useSearchParams()
  const sessionId = searchParams.get('session_id')

  const [recommendations, setRecommendations] = useState([])
  const [assessmentContext, setAssessmentContext] = useState(null)
  const [source, setSource] = useState('general')
  const [historySessions, setHistorySessions] = useState([])
  const [loading, setLoading] = useState(true)

  const isAssessmentMode = Boolean(sessionId)

  useEffect(() => {
    let cancelled = false

    const load = async () => {
      try {
        setLoading(true)
        setAssessmentContext(null)
        setRecommendations([])

        const historyPromise = assessmentService.listHistory({ limit: 20 }).catch(() => ({ sessions: [] }))

        if (sessionId) {
          try {
            const data = await recommendationService.getFromAssessment(sessionId)
            if (cancelled) return
            setAssessmentContext(data)
            setRecommendations(data?.recommended_courses || [])
            setSource('assessment')
          } catch (e) {
            if (!cancelled) {
              toast.error(e?.message || 'Không tải được gợi ý theo phiên — chuyển sang gợi ý chung.')
              navigate('/dashboard/recommendations', { replace: true })
            }
          }
        } else {
          const data = await recommendationService.getRecommendations()
          if (cancelled) return
          setAssessmentContext(null)
          setRecommendations(data?.recommended_courses || [])
          setSource('general')
        }

        const histRes = await historyPromise
        if (!cancelled) setHistorySessions(histRes?.sessions || [])
      } catch {
        if (!cancelled) toast.error('Không thể tải đề xuất')
      } finally {
        if (!cancelled) setLoading(false)
      }
    }

    load()
    return () => {
      cancelled = true
    }
  }, [sessionId, navigate])

  const evaluatedSessions = useMemo(
    () => historySessions.filter((s) => s.status === 'evaluated'),
    [historySessions]
  )

  const activeMeta = useMemo(
    () => historySessions.find((s) => s.session_id === sessionId),
    [historySessions, sessionId]
  )

  const learningOrder = assessmentContext?.suggested_learning_order || []
  const practiceList = assessmentContext?.practice_exercises || []
  const aiAdvice = assessmentContext?.ai_personalized_advice
  const totalHours = assessmentContext?.total_estimated_hours

  const headerSub = useMemo(() => {
    if (source === 'assessment' && assessmentContext) {
      if (activeMeta) {
        return `Theo đánh giá ${activeMeta.subject} · ${activeMeta.level} · trình độ ${assessmentContext.user_proficiency_level}`
      }
      return `Theo phiên đánh giá · trình độ ${assessmentContext.user_proficiency_level}`
    }
    return `Gợi ý dựa trên lịch sử học tập (${recommendations.length} khóa)`
  }, [source, assessmentContext, activeMeta, recommendations.length])

  const hasCourseList = recommendations.length > 0
  const hasAssessmentExtras =
    !!assessmentContext &&
    (!!aiAdvice || learningOrder.length > 0 || practiceList.length > 0 || totalHours > 0)

  const switchToGeneral = useCallback(() => {
    navigate('/dashboard/recommendations')
  }, [navigate])

  const switchToAssessment = useCallback(
    (sid) => {
      const target = sid || evaluatedSessions[0]?.session_id
      if (target) {
        navigate(`/dashboard/recommendations?session_id=${target}`)
      } else {
        navigate('/dashboard/assessment')
      }
    },
    [navigate, evaluatedSessions]
  )

  if (loading) {
    return (
      <div className="rec-page">
        <AILoadingState
          title={isAssessmentMode ? 'AI đang dựng lộ trình học tập' : 'Đang tải gợi ý khóa học'}
          message={
            isAssessmentMode
              ? 'Hệ thống đang phân tích năng lực và ghép khóa học phù hợp nhất.'
              : 'Đang tổng hợp đề xuất từ lịch sử học tập của bạn.'
          }
          steps={
            isAssessmentMode
              ? [
                  'Đang đọc dữ liệu đánh giá...',
                  'Đang tính điểm phù hợp khóa học...',
                  'Đang xếp thứ tự lộ trình ưu tiên...',
                ]
              : ['Đang đọc tiến độ khóa học...', 'Đang xếp hạng đề xuất...']
          }
        />
      </div>
    )
  }

  return (
    <div className="rec-page">
      {/* Hero */}
      <motion.header
        className="rec-hero"
        initial={prefersReduced ? false : { opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.35, ease: [0.65, 0, 0.35, 1] }}
      >
        <svg className="rec-hero__ornament" viewBox="0 0 48 12" fill="none" aria-hidden="true">
          <line x1="0" y1="6" x2="16" y2="6" stroke="var(--gold-500)" strokeWidth="1" />
          <circle cx="24" cy="6" r="4" stroke="var(--gold-500)" strokeWidth="1" />
          <line x1="32" y1="6" x2="48" y2="6" stroke="var(--gold-500)" strokeWidth="1" />
        </svg>
        <h1 className="rec-hero__title">Lộ trình học tập gợi ý</h1>
        <p className="rec-hero__sub">{headerSub}</p>
      </motion.header>

      {/* Chế độ nguồn: theo đánh giá vs gợi ý chung */}
      <div className="rec-mode" role="tablist" aria-label="Nguồn gợi ý">
        <button
          type="button"
          role="tab"
          aria-selected={isAssessmentMode}
          className={`rec-mode__tab ${isAssessmentMode ? 'rec-mode__tab--active' : ''}`}
          onClick={() => switchToAssessment(sessionId)}
          disabled={evaluatedSessions.length === 0}
          title={evaluatedSessions.length === 0 ? 'Chưa có phiên đánh giá hoàn thành' : undefined}
        >
          Theo đánh giá năng lực
        </button>
        <button
          type="button"
          role="tab"
          aria-selected={!isAssessmentMode}
          className={`rec-mode__tab ${!isAssessmentMode ? 'rec-mode__tab--active' : ''}`}
          onClick={switchToGeneral}
        >
          Gợi ý chung
        </button>
      </div>

      {evaluatedSessions.length === 0 && (
        <div className="rec-banner rec-banner--info">
          <p>Làm bài đánh giá năng lực để nhận lộ trình cá nhân hóa chi tiết hơn.</p>
          <Button size="sm" onClick={() => navigate('/dashboard/assessment')}>
            Bắt đầu đánh giá
          </Button>
        </div>
      )}

      {/* Chọn phiên đánh giá */}
      {evaluatedSessions.length > 0 && (
        <section className="rec-sessions" aria-labelledby="rec-sessions-title">
          <div className="rec-sessions__head">
            <h2 id="rec-sessions-title" className="rec-sessions__title">
              Phiên đánh giá
            </h2>
            {isAssessmentMode && sessionId && (
              <div className="rec-sessions__actions">
                <Button
                  size="sm"
                  variant="outline"
                  type="button"
                  onClick={() => navigate(`/dashboard/assessment/${sessionId}/results`)}
                >
                  Kết quả
                </Button>
                <Button
                  size="sm"
                  variant="outline"
                  type="button"
                  onClick={() => navigate(`/dashboard/assessment/${sessionId}/review`)}
                >
                  Xem lại bài
                </Button>
              </div>
            )}
          </div>
          <ul className="rec-sessions__list">
            {evaluatedSessions.map((s) => {
              const active = sessionId === s.session_id
              return (
                <li key={s.session_id}>
                  <button
                    type="button"
                    className={`rec-session-chip ${active ? 'rec-session-chip--active' : ''}`}
                    onClick={() => switchToAssessment(s.session_id)}
                    aria-current={active ? 'true' : undefined}
                  >
                    <span className="rec-session-chip__subject">{s.subject}</span>
                    <span className="rec-session-chip__meta">
                      {s.level}
                      {s.overall_score != null && ` · ${Math.round(s.overall_score)} điểm`}
                      {' · '}
                      {formatSessionWhen(s.evaluated_at || s.created_at)}
                    </span>
                  </button>
                </li>
              )
            })}
          </ul>
        </section>
      )}

      {/* Nội dung chính: sidebar AI + danh sách khóa học */}
      <div className={`rec-layout ${hasAssessmentExtras ? 'rec-layout--with-aside' : ''}`}>
        {hasAssessmentExtras && (
          <aside className="rec-aside" aria-label="Phân tích và lộ trình AI">
            {totalHours > 0 && (
              <p className="rec-aside__hours">
                Ước tính tổng thời gian: <strong>{Math.round(totalHours)} giờ</strong>
              </p>
            )}
            {aiAdvice && (
              <div className="rec-panel rec-panel--advice">
                <h3 className="rec-panel__title">Lời khuyên cá nhân hóa</h3>
                <p className="rec-panel__body">{aiAdvice}</p>
              </div>
            )}
            {learningOrder.length > 0 && (
              <div className="rec-panel">
                <h3 className="rec-panel__title">Thứ tự học gợi ý</h3>
                <ol className="rec-learning-order">
                  {learningOrder.map((step) => (
                    <li key={`${step.step}-${step.course_id}`} className="rec-learning-order__item">
                      <span className="rec-learning-order__step">Bước {step.step}</span>
                      <button
                        type="button"
                        className="rec-learning-order__course"
                        onClick={() => step.course_id && navigate(`/dashboard/courses/${step.course_id}`)}
                      >
                        {courseTitleById(recommendations, step.course_id)}
                        <ArrowRightIcon />
                      </button>
                      {step.why_this_order && (
                        <p className="rec-learning-order__why">{step.why_this_order}</p>
                      )}
                      {step.focus_modules?.length > 0 && (
                        <p className="rec-learning-order__modules">
                          Trọng tâm: {step.focus_modules.join(', ')}
                        </p>
                      )}
                    </li>
                  ))}
                </ol>
              </div>
            )}
            {practiceList.length > 0 && (
              <div className="rec-panel">
                <h3 className="rec-panel__title">Bài tập luyện tập</h3>
                <ul className="rec-practice-list">
                  {practiceList.map((ex, i) => (
                    <li key={`${ex.skill_tag}-${i}`} className="rec-practice-item">
                      <div className="rec-practice-item__head">
                        <span className="rec-practice-item__skill">{ex.skill_tag}</span>
                        <span className="rec-practice-item__badge">{ex.exercise_type}</span>
                        <span className="rec-practice-item__diff">{ex.difficulty}</span>
                      </div>
                      <p className="rec-practice-item__desc">{ex.description}</p>
                      {ex.estimated_time_hours != null && (
                        <span className="rec-practice-item__time">~{ex.estimated_time_hours} giờ</span>
                      )}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </aside>
        )}

        <section className="rec-courses" aria-labelledby="rec-courses-title">
          <h2 id="rec-courses-title" className="rec-courses__title">
            {isAssessmentMode ? 'Khóa học đề xuất' : 'Khóa học phù hợp'}
            {hasCourseList && (
              <span className="rec-courses__count">{recommendations.length}</span>
            )}
          </h2>

          {hasCourseList ? (
            <ol className="rec-course-list">
              {recommendations.map((rec, idx) => {
                const scorePct = rec.relevance_score ?? rec.match_score ?? null
                const isHigh = (scorePct ?? 0) >= 80
                const levelTag = rec.level ?? rec.difficulty
                const showDesc = rec.description && !isPlaceholderDescription(rec.description)
                const delay = prefersReduced ? 0 : Math.min(idx * 0.05, 0.35)

                return (
                  <motion.li
                    key={rec.course_id || idx}
                    className="rec-course-card"
                    initial={prefersReduced ? false : { opacity: 0, y: 12 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.35, delay, ease: [0.65, 0, 0.35, 1] }}
                  >
                    <div className="rec-course-card__rank" aria-hidden="true">
                      {String(idx + 1).padStart(2, '0')}
                    </div>
                    <div className="rec-course-card__body">
                      <div className="rec-course-card__top">
                        <h3 className="rec-course-card__title">{rec.title}</h3>
                        {scorePct != null && (
                          <span
                            className={`rec-course-card__score ${isHigh ? 'rec-course-card__score--high' : ''}`}
                          >
                            {Math.round(scorePct)}% phù hợp
                          </span>
                        )}
                      </div>

                      {rec.reason && <p className="rec-course-card__reason">{rec.reason}</p>}
                      {showDesc && <p className="rec-course-card__desc">{rec.description}</p>}

                      <div className="rec-course-card__meta">
                        {levelTag && <span className="rec-course-card__tag">{levelTag}</span>}
                        {rec.category && <span className="rec-course-card__tag rec-course-card__tag--cat">{rec.category}</span>}
                        {rec.estimated_completion_days != null && (
                          <span className="rec-course-card__tag rec-course-card__tag--muted">
                            ~{rec.estimated_completion_days} ngày
                          </span>
                        )}
                        {rec.addresses_gaps?.length > 0 &&
                          rec.addresses_gaps.slice(0, 2).map((gap) => (
                            <span key={gap} className="rec-course-card__tag rec-course-card__tag--gap">
                              {gap}
                            </span>
                          ))}
                      </div>

                      <button
                        type="button"
                        className="rec-course-card__cta"
                        onClick={() => navigate(`/dashboard/courses/${rec.course_id}`)}
                      >
                        Xem khóa học
                        <ArrowRightIcon />
                      </button>
                    </div>
                  </motion.li>
                )
              })}
            </ol>
          ) : (
            <div className="rec-empty-wrap">
              <StateView
                type="empty"
                title={source === 'assessment' ? 'Chưa ghép được khóa học cụ thể' : 'Chưa có đề xuất khóa học'}
                message={
                  source === 'assessment'
                    ? 'Vẫn có thể xem lời khuyên phía trên (nếu có). Thử đánh giá khác hoặc duyệt kho khóa học.'
                    : 'Hãy làm bài đánh giá năng lực hoặc học thêm để hệ thống có dữ liệu gợi ý.'
                }
                action={
                  <Button onClick={() => navigate('/dashboard/assessment')}>Đến đánh giá năng lực</Button>
                }
              />
            </div>
          )}
        </section>
      </div>

      {/* Hub điều hướng — cuối trang, gọn */}
      <nav className="rec-hub" aria-label="Điều hướng liên quan">
        <Link className="rec-hub__link" to="/dashboard/assessment">
          <ClipboardIcon />
          <span>Đánh giá &amp; lịch sử</span>
        </Link>
        <Link className="rec-hub__link" to="/dashboard/progress">
          <ChartIcon />
          <span>Tiến độ học tập</span>
        </Link>
        <Link className="rec-hub__link" to="/dashboard/my-courses">
          <BookIcon />
          <span>Khóa học của tôi</span>
        </Link>
      </nav>
    </div>
  )
}

export default RecommendationsPage
