import { useState, useEffect } from 'react'
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
 * Trang đề xuất lộ trình học tập — kết nối phiên đánh giá, lộ trình AI, tiến độ học tập
 * Route: /dashboard/recommendations?session_id= (optional)
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

const RecommendationsPage = () => {
  const navigate = useNavigate()
  const prefersReduced = useReducedMotion()
  const [searchParams] = useSearchParams()
  const sessionId = searchParams.get('session_id')

  const [recommendations, setRecommendations] = useState([])
  /** Payload đầy đủ từ GET /recommendations/from-assessment */
  const [assessmentContext, setAssessmentContext] = useState(null)
  /** Nguồn hiển thị: assessment | general */
  const [source, setSource] = useState('general')
  const [historySessions, setHistorySessions] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let cancelled = false

    const load = async () => {
      try {
        setLoading(true)
        setAssessmentContext(null)

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
              toast.error(e?.message || 'Không tải được gợi ý theo phiên đánh giá — hiển thị gợi ý chung.')
            }
            try {
              const fallback = await recommendationService.getRecommendations()
              if (cancelled) return
              setAssessmentContext(null)
              setRecommendations(fallback?.recommended_courses || [])
              setSource('general')
            } catch {
              if (!cancelled) setRecommendations([])
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
  }, [sessionId])

  const activeMeta = historySessions.find((s) => s.session_id === sessionId)
  const evaluatedSessions = historySessions.filter((s) => s.status === 'evaluated')

  const learningOrder = assessmentContext?.suggested_learning_order || []
  const practiceList = assessmentContext?.practice_exercises || []
  const aiAdvice = assessmentContext?.ai_personalized_advice
  const totalHours = assessmentContext?.total_estimated_hours

  const headerSub =
    source === 'assessment' && assessmentContext
      ? activeMeta
        ? `Theo đánh giá: ${activeMeta.subject} · ${activeMeta.level} · ${assessmentContext.user_proficiency_level}`
        : `Theo phiên đánh giá · Trình độ gợi ý: ${assessmentContext.user_proficiency_level}`
      : `Gợi ý khóa học dựa trên lịch sử học tập trên nền tảng (${recommendations.length} khóa).`

  const hasCourseList = recommendations.length > 0
  const hasAssessmentExtras =
    !!assessmentContext &&
    (!!aiAdvice || learningOrder.length > 0 || practiceList.length > 0 || totalHours > 0)

  if (loading) {
    return (
      <div className="rec-page">
        <AILoadingState
          title="AI đang dựng lộ trình học tập"
          message="Hệ thống đang phân tích năng lực và ghép khóa học phù hợp nhất."
          steps={[
            'Đang đọc dữ liệu đánh giá...',
            'Đang tính điểm phù hợp khóa học...',
            'Đang xếp thứ tự lộ trình ưu tiên...',
          ]}
        />
      </div>
    )
  }

  return (
    <div className="rec-page">
      {/* Hub: liên kết trực tiếp đánh giá / tiến độ / khóa học */}
      <nav className="rec-hub" aria-label="Điều hướng nhanh">
        <Link className="rec-hub__card" to="/dashboard/assessment">
          <span className="rec-hub__icon" aria-hidden>
            <ClipboardIcon />
          </span>
          <span className="rec-hub__label">Đánh giá &amp; lịch sử</span>
          <span className="rec-hub__hint">Làm bài mới hoặc xem các phiên đã hoàn thành</span>
        </Link>
        <Link className="rec-hub__card" to="/dashboard/progress">
          <span className="rec-hub__icon" aria-hidden>
            <ChartIcon />
          </span>
          <span className="rec-hub__label">Tiến độ &amp; kết quả học tập</span>
          <span className="rec-hub__hint">Biểu đồ, hoạt động và điểm số theo thời gian</span>
        </Link>
        <Link className="rec-hub__card" to="/dashboard/my-courses">
          <span className="rec-hub__icon" aria-hidden>
            <BookIcon />
          </span>
          <span className="rec-hub__label">Khóa học của tôi</span>
          <span className="rec-hub__hint">Khóa đang học và chứng chỉ</span>
        </Link>
      </nav>

      {/* Header */}
      <motion.div
        className="rec-header"
        initial={prefersReduced ? false : { opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.35, ease: [0.65, 0, 0.35, 1] }}
      >
        <div className="rec-header__ornament" aria-hidden="true">
          <svg viewBox="0 0 120 14" fill="none">
            <path d="M2 7H48" stroke="currentColor" strokeWidth="1.5" />
            <circle cx="60" cy="7" r="4.5" stroke="currentColor" strokeWidth="1.5" />
            <path d="M72 7H118" stroke="currentColor" strokeWidth="1.5" />
          </svg>
        </div>
        <h1 className="rec-header__title">Lộ trình học tập gợi ý</h1>
        <p className="rec-header__sub">{headerSub}</p>
        {sessionId && assessmentContext && (
          <div className="rec-context-actions">
            <Button
              size="sm"
              variant="outline"
              type="button"
              onClick={() => navigate(`/dashboard/assessment/${sessionId}/results`)}
            >
              Xem kết quả đánh giá
            </Button>
            <Button
              size="sm"
              variant="outline"
              type="button"
              onClick={() => navigate(`/dashboard/assessment/${sessionId}/review`)}
            >
              Xem lại bài làm
            </Button>
            <Button size="sm" variant="outline" type="button" onClick={() => navigate('/dashboard/recommendations')}>
              Gợi ý chung (không theo phiên)
            </Button>
          </div>
        )}
      </motion.div>

      {/* Chọn phiên đánh giá để xem lộ trình chi tiết */}
      {evaluatedSessions.length > 0 && (
        <section className="rec-history" aria-labelledby="rec-history-title">
          <h2 id="rec-history-title" className="rec-history__title">
            Lịch sử đánh giá — chọn phiên để tải gợi ý theo kết quả
          </h2>
          <ul className="rec-history__list">
            {evaluatedSessions.map((s) => (
              <li key={s.session_id} className="rec-history__item">
                <div className="rec-history__main">
                  <span className="rec-history__subject">{s.subject}</span>
                  <span className="rec-history__meta">
                    {s.level}
                    <span className="rec-history__dot">·</span>
                    {formatSessionWhen(s.evaluated_at || s.created_at)}
                    {s.overall_score != null && (
                      <>
                        <span className="rec-history__dot">·</span>
                        Điểm {Math.round(s.overall_score)}
                      </>
                    )}
                  </span>
                </div>
                <Button
                  size="sm"
                  variant={sessionId === s.session_id ? 'primary' : 'outline'}
                  type="button"
                  onClick={() => navigate(`/dashboard/recommendations?session_id=${s.session_id}`)}
                >
                  {sessionId === s.session_id ? 'Đang xem' : 'Lộ trình theo phiên này'}
                </Button>
              </li>
            ))}
          </ul>
        </section>
      )}

      {/* Khối AI bổ sung từ API from-assessment (trước đây không hiển thị) */}
      {hasAssessmentExtras && (
        <section className="rec-ai-extra">
          {totalHours > 0 && (
            <p className="rec-ai-extra__hours">
              Ước tính tổng thời gian học (tham khảo): <strong>{Math.round(totalHours)} giờ</strong>
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
                      Mở khóa học
                      <ArrowRightIcon />
                    </button>
                    {step.why_this_order && <p className="rec-learning-order__why">{step.why_this_order}</p>}
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
              <h3 className="rec-panel__title">Bài tập / luyện tập gợi ý</h3>
              <ul className="rec-practice-list">
                {practiceList.map((ex, i) => (
                  <li key={`${ex.skill_tag}-${i}`} className="rec-practice-item">
                    <span className="rec-practice-item__skill">{ex.skill_tag}</span>
                    <span className="rec-practice-item__badge">{ex.exercise_type}</span>
                    <span className="rec-practice-item__diff">{ex.difficulty}</span>
                    <p className="rec-practice-item__desc">{ex.description}</p>
                    {ex.estimated_time_hours != null && (
                      <span className="rec-practice-item__time">~{ex.estimated_time_hours} h</span>
                    )}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </section>
      )}

      {/* Infographic khóa học */}
      {hasCourseList ? (
        <div className="rec-track">
          <div className="rec-track__spine" aria-hidden="true" />

          {recommendations.map((rec, idx) => {
            const scorePct = rec.relevance_score ?? rec.match_score ?? null
            const isHigh = (scorePct ?? 0) >= 80
            const delay = prefersReduced ? 0 : Math.min(idx * 0.06, 0.4)
            const levelTag = rec.level ?? rec.difficulty

            return (
              <motion.div
                key={rec.course_id || idx}
                className={`rec-item ${idx % 2 === 0 ? 'rec-item--right' : 'rec-item--left'}`}
                initial={prefersReduced ? false : { opacity: 0, x: idx % 2 === 0 ? 24 : -24 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true, margin: '-60px' }}
                transition={{ duration: 0.4, delay, ease: [0.65, 0, 0.35, 1] }}
              >
                <div className="rec-item__dot" aria-hidden="true" />

                <div className="rec-item__meta">
                  <span className="rec-item__step">{String(idx + 1).padStart(2, '0')}</span>
                  {scorePct != null && (
                    <span
                      className={`rec-item__match ${isHigh ? 'rec-item__match--high' : 'rec-item__match--medium'}`}
                    >
                      {Math.round(scorePct)}%
                    </span>
                  )}
                </div>

                <div className="rec-item__card">
                  <div className="rec-item__card-top">
                    <h3 className="rec-item__title">{rec.title}</h3>
                  </div>

                  {rec.description && <p className="rec-item__desc">{rec.description}</p>}

                  {rec.reason && <p className="rec-item__reason">{rec.reason}</p>}

                  <div className="rec-item__tags">
                    {levelTag && <span className="rec-item__tag rec-item__tag--diff">{levelTag}</span>}
                    {rec.category && <span className="rec-item__tag rec-item__tag--cat">{rec.category}</span>}
                  </div>

                  <button
                    type="button"
                    className="rec-item__cta"
                    onClick={() => navigate(`/dashboard/courses/${rec.course_id}`)}
                  >
                    <span>Xem khóa học</span>
                    <ArrowRightIcon />
                  </button>
                </div>
              </motion.div>
            )
          })}

          <div className="rec-track__end">
            <span className="rec-track__end-label">Hoàn thành lộ trình</span>
          </div>
        </div>
      ) : (
        <div className="rec-empty-wrap">
          <StateView
            type="empty"
            title={source === 'assessment' ? 'Chưa ghép được khóa học cụ thể' : 'Chưa có đề xuất khóa học'}
            message={
              source === 'assessment'
                ? 'Vẫn có thể xem lời khuyên và thứ tự học phía trên (nếu có). Thử làm đánh giá khác hoặc duyệt khóa học trong kho.'
                : 'Hãy làm bài đánh giá năng lực hoặc học thêm để hệ thống có dữ liệu gợi ý.'
            }
            action={
              <Button onClick={() => navigate('/dashboard/assessment')}>Đến đánh giá năng lực</Button>
            }
          />
        </div>
      )}
    </div>
  )
}

export default RecommendationsPage
