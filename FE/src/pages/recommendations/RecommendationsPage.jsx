import { useState, useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { motion, useReducedMotion } from 'framer-motion'
import toast from 'react-hot-toast'
import recommendationService from '@services/recommendationService'
import Button from '@components/ui/Button'
import StateView from '@components/ui/StateView'
import AILoadingState from '@components/ui/AILoadingState'
import './RecommendationsPage.css'

/**
 * Trang đề xuất lộ trình học tập — infographic cuộn dọc
 * Route: /dashboard/recommendations
 * API: GET /recommendations/from-assessment (nếu có session_id)
 *      GET /recommendations (fallback)
 */

const TargetIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.5} aria-hidden="true">
    <circle cx="12" cy="12" r="10" />
    <circle cx="12" cy="12" r="6" />
    <circle cx="12" cy="12" r="2" />
  </svg>
)

const ArrowRightIcon = () => (
  <svg viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
    <path fillRule="evenodd"
      d="M3 10a.75.75 0 0 1 .75-.75h10.638L10.23 5.29a.75.75 0 1 1 1.04-1.08l5.5 5.25a.75.75
      0 0 1 0 1.08l-5.5 5.25a.75.75 0 1 1-1.04-1.08l4.158-3.96H3.75A.75.75 0 0 1 3 10Z"
      clipRule="evenodd" />
  </svg>
)

const RecommendationsPage = () => {
  const navigate = useNavigate()
  const prefersReduced = useReducedMotion()
  const [searchParams] = useSearchParams()
  const [recommendations, setRecommendations] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchRecommendations = async () => {
      try {
        setLoading(true)
        let data
        const sessionId = searchParams.get('session_id')
        if (sessionId) {
          try {
            data = await recommendationService.getFromAssessment(sessionId)
          } catch {
            data = await recommendationService.getRecommendations()
          }
        } else {
          data = await recommendationService.getRecommendations()
        }
        setRecommendations(data?.recommended_courses || data?.recommendations || data?.courses || [])
      } catch {
        toast.error('Không thể tải đề xuất')
      } finally {
        setLoading(false)
      }
    }
    fetchRecommendations()
  }, [searchParams])

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
        <p className="rec-header__sub">
          Dựa trên kết quả đánh giá năng lực, hệ thống đề xuất {recommendations.length} khóa học phù hợp.
        </p>
      </motion.div>

      {/* Infographic scroll track */}
      {recommendations.length > 0 ? (
        <div className="rec-track">
          {/* Vertical spine */}
          <div className="rec-track__spine" aria-hidden="true" />

          {recommendations.map((rec, idx) => {
            const isHigh = (rec.match_score ?? 0) >= 80
            const delay = prefersReduced ? 0 : Math.min(idx * 0.06, 0.4)

            return (
              <motion.div
                key={rec.course_id || idx}
                className={`rec-item ${idx % 2 === 0 ? 'rec-item--right' : 'rec-item--left'}`}
                initial={prefersReduced ? false : { opacity: 0, x: idx % 2 === 0 ? 24 : -24 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true, margin: '-60px' }}
                transition={{ duration: 0.4, delay, ease: [0.65, 0, 0.35, 1] }}
              >
                {/* Connector dot on spine */}
                <div className="rec-item__dot" aria-hidden="true" />

                {/* Step number + match badge */}
                <div className="rec-item__meta">
                  <span className="rec-item__step">{String(idx + 1).padStart(2, '0')}</span>
                  {rec.match_score != null && (
                    <span className={`rec-item__match ${isHigh ? 'rec-item__match--high' : 'rec-item__match--medium'}`}>
                      {Math.round(rec.match_score)}%
                    </span>
                  )}
                </div>

                {/* Card body */}
                <div className="rec-item__card">
                  <div className="rec-item__card-top">
                    <h3 className="rec-item__title">{rec.title}</h3>
                  </div>

                  {rec.reason && (
                    <p className="rec-item__reason">{rec.reason}</p>
                  )}

                  <div className="rec-item__tags">
                    {rec.difficulty && (
                      <span className="rec-item__tag rec-item__tag--diff">{rec.difficulty}</span>
                    )}
                    {rec.category && (
                      <span className="rec-item__tag rec-item__tag--cat">{rec.category}</span>
                    )}
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

          {/* Track end marker */}
          <div className="rec-track__end">
            <span className="rec-track__end-label">Hoàn thành lộ trình</span>
          </div>
        </div>
      ) : (
        <StateView
          type="empty"
          title="Chưa có đề xuất phù hợp"
          message="Hãy làm bài đánh giá năng lực để hệ thống gợi ý lộ trình học tối ưu."
          action={(
            <Button onClick={() => navigate('/dashboard/assessment')}>
              Bắt đầu đánh giá
            </Button>
          )}
        />
      )}
    </div>
  )
}

export default RecommendationsPage
