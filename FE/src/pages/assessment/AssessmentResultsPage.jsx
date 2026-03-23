import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import assessmentService from '@services/assessmentService'
import Button from '@components/ui/Button'
import Card, { CardHeader, CardBody } from '@components/ui/Card'
import './AssessmentResultsPage.css'

/**
 * Trang ket qua danh gia nang luc
 * Route: /dashboard/assessment/:sessionId/results
 * Hien thi: diem tong, radar chart ky nang, lo hong, loi khuyen AI
 */
const AssessmentResultsPage = () => {
  const { sessionId } = useParams()
  const navigate = useNavigate()
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(true)

  // Lay ket qua khi mount
  useEffect(() => {
    const fetchResults = async () => {
      try {
        setLoading(true)
        const data = await assessmentService.getResults(sessionId)
        setResults(data)
      } catch (error) {
        toast.error('Không thể tải kết quả')
      } finally {
        setLoading(false)
      }
    }
    fetchResults()
  }, [sessionId])

  if (loading) return <div className="loading-spinner">Đang tải kết quả...</div>
  if (!results) return <div className="empty-state">Không tìm thấy kết quả</div>

  // Xac dinh mau theo diem
  const getScoreColor = (score) => {
    if (score >= 80) return 'var(--color-success, #10b981)'
    if (score >= 50) return 'var(--color-warning, #f59e0b)'
    return 'var(--color-danger, #ef4444)'
  }

  return (
    <div className="assessment-results-page">
      <div className="page-header">
        <h1>Kết quả đánh giá</h1>
      </div>

      {/* Section 1: Diem tong */}
      <Card className="score-card">
        <CardBody>
          <div className="score-display">
            <div
              className="score-circle"
              style={{
                background: `conic-gradient(${getScoreColor(results.overall_score)} ${results.overall_score * 3.6}deg, #e5e7eb 0deg)`
              }}
            >
              <div className="score-circle__inner">
                <span className="score-circle__value">{Math.round(results.overall_score)}</span>
                <span className="score-circle__label">điểm</span>
              </div>
            </div>
            <div className="score-info">
              <span className="proficiency-badge">
                {results.proficiency_level}
              </span>
              <p className="score-summary">
                {results.overall_score >= 80
                  ? 'Xuất sắc! Bạn có nền tảng vững chắc.'
                  : results.overall_score >= 50
                  ? 'Khá tốt! Cần luyện tập thêm một số kỹ năng.'
                  : 'Cần cố gắng thêm. Hãy xem lộ trình học tập gợi ý.'}
              </p>
            </div>
          </div>
        </CardBody>
      </Card>

      {/* Section 2: Phan tich ky nang */}
      {results.skill_analysis && results.skill_analysis.length > 0 && (
        <Card>
          <CardHeader>
            <h3>Phân tích kỹ năng</h3>
          </CardHeader>
          <CardBody>
            <div className="skills-list">
              {results.skill_analysis.map((skill, idx) => (
                <div key={idx} className="skill-item">
                  <div className="skill-item__header">
                    <span className="skill-item__name">{skill.skill_tag}</span>
                    <span className={`strength-badge strength-badge--${skill.strength_level?.toLowerCase()}`}>
                      {skill.strength_level}
                    </span>
                  </div>
                  <div className="skill-bar">
                    <div
                      className="skill-bar__fill"
                      style={{
                        width: `${skill.proficiency_percentage}%`,
                        backgroundColor: getScoreColor(skill.proficiency_percentage)
                      }}
                    />
                  </div>
                  <span className="skill-item__percent">
                    {Math.round(skill.proficiency_percentage)}%
                  </span>
                  {skill.detailed_feedback && (
                    <p className="skill-item__feedback">{skill.detailed_feedback}</p>
                  )}
                </div>
              ))}
            </div>
          </CardBody>
        </Card>
      )}

      {/* Section 3: Lo hong kien thuc */}
      {results.knowledge_gaps && results.knowledge_gaps.length > 0 && (
        <Card>
          <CardHeader>
            <h3>Lỗ hổng kiến thức</h3>
          </CardHeader>
          <CardBody>
            <div className="gaps-list">
              {results.knowledge_gaps.map((gap, idx) => (
                <div key={idx} className={`gap-item gap-item--${gap.importance?.toLowerCase()}`}>
                  <div className="gap-item__header">
                    <span className="gap-item__area">{gap.gap_area}</span>
                    <span className={`importance-badge importance-badge--${gap.importance?.toLowerCase()}`}>
                      {gap.importance}
                    </span>
                  </div>
                  {gap.suggested_action && (
                    <p className="gap-item__action">{gap.suggested_action}</p>
                  )}
                </div>
              ))}
            </div>
          </CardBody>
        </Card>
      )}

      {/* Section 4: Thoi gian */}
      {results.time_analysis && (
        <Card>
          <CardHeader>
            <h3>Phân tích thời gian</h3>
          </CardHeader>
          <CardBody>
            <div className="time-stats">
              <div className="stat-card">
                <span className="stat-card__value">
                  {Math.round(results.time_analysis.total_time_seconds / 60)} phút
                </span>
                <span className="stat-card__label">Tổng thời gian</span>
              </div>
              <div className="stat-card">
                <span className="stat-card__value">
                  {Math.round(results.time_analysis.average_time_per_question)}s
                </span>
                <span className="stat-card__label">TB mỗi câu</span>
              </div>
            </div>
          </CardBody>
        </Card>
      )}

      {/* Section 5: Loi khuyen AI */}
      {results.ai_feedback && (
        <Card>
          <CardHeader>
            <h3>Lời khuyên từ AI</h3>
          </CardHeader>
          <CardBody>
            <div className="ai-feedback">{results.ai_feedback}</div>
          </CardBody>
        </Card>
      )}

      {/* Actions */}
      <div className="results-actions">
        <Button
          variant="outline"
          onClick={() => navigate('/dashboard/assessment')}
        >
          Làm lại đánh giá
        </Button>
        <Button onClick={() => navigate('/dashboard/recommendations')}>
          Xem lộ trình học tập
        </Button>
      </div>
    </div>
  )
}

export default AssessmentResultsPage
