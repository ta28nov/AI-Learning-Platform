import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import toast from 'react-hot-toast'
import recommendationService from '@services/recommendationService'
import Button from '@components/ui/Button'
import Card, { CardBody } from '@components/ui/Card'
import './RecommendationsPage.css'

/**
 * Trang de xuat lo trinh hoc tap
 * Route: /dashboard/recommendations
 * API: GET /recommendations/from-assessment, GET /recommendations
 */
const RecommendationsPage = () => {
  const navigate = useNavigate()
  const [recommendations, setRecommendations] = useState([])
  const [loading, setLoading] = useState(true)

  // Lay de xuat khi mount
  useEffect(() => {
    const fetchRecommendations = async () => {
      try {
        setLoading(true)
        // Thu lay de xuat tu assessment truoc
        let data
        try {
          data = await recommendationService.getFromAssessment()
        } catch {
          // Neu chua co assessment, lay de xuat chung
          data = await recommendationService.getRecommendations()
        }
        setRecommendations(data?.recommendations || data?.courses || [])
      } catch (error) {
        toast.error('Không thể tải đề xuất')
      } finally {
        setLoading(false)
      }
    }
    fetchRecommendations()
  }, [])

  const fadeUp = { hidden: { opacity: 0, y: 20 }, visible: { opacity: 1, y: 0 } }

  // Loading state
  if (loading) {
    return (
      <div className="rec-page">
        <div className="rec-loading">
          <div className="rec-loading__spinner" />
          <span className="rec-loading__text">Đang tải đề xuất...</span>
        </div>
      </div>
    )
  }

  return (
    <motion.div
      className="rec-page"
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      {/* Header */}
      <div className="rec-header">
        <h1 className="rec-header__title">Lộ trình học tập gợi ý</h1>
        <p className="rec-header__sub">
          Dựa trên kết quả đánh giá năng lực của bạn
        </p>
      </div>

      {/* Danh sach de xuat */}
      {recommendations.length > 0 ? (
        <motion.div
          className="rec-grid"
          initial="hidden"
          animate="visible"
          variants={{ visible: { transition: { staggerChildren: 0.06 } } }}
        >
          {recommendations.map((rec, idx) => (
            <motion.div key={rec.course_id || idx} variants={fadeUp}>
              <Card hover className="rec-card">
                <CardBody>
                  <div className="rec-card__top">
                    <h3 className="rec-card__title">{rec.title}</h3>
                    {rec.match_score != null && (
                      <span className={`rec-card__match ${rec.match_score >= 80 ? 'rec-card__match--high' : 'rec-card__match--medium'}`}>
                        {Math.round(rec.match_score)}% phù hợp
                      </span>
                    )}
                  </div>
                  {rec.reason && (
                    <p className="rec-card__reason">{rec.reason}</p>
                  )}
                  <div className="rec-card__tags">
                    {rec.difficulty && (
                      <span className="rec-card__tag rec-card__tag--diff">{rec.difficulty}</span>
                    )}
                    {rec.category && (
                      <span className="rec-card__tag rec-card__tag--cat">{rec.category}</span>
                    )}
                  </div>
                  <Button
                    size="sm"
                    onClick={() => navigate(`/dashboard/courses/${rec.course_id}`)}
                  >
                    Xem khóa học
                  </Button>
                </CardBody>
              </Card>
            </motion.div>
          ))}
        </motion.div>
      ) : (
        <div className="rec-empty">
          <div className="rec-empty__icon">🎯</div>
          <p className="rec-empty__text">
            Chưa có đề xuất. Hãy làm bài đánh giá năng lực trước!
          </p>
          <Button
            className="rec-empty__btn"
            onClick={() => navigate('/dashboard/assessment')}
          >
            Bắt đầu đánh giá
          </Button>
        </div>
      )}
    </motion.div>
  )
}

export default RecommendationsPage
