import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import recommendationService from '@services/recommendationService'
import Button from '@components/ui/Button'
import Card, { CardBody } from '@components/ui/Card'

/**
 * Trang de xuat lo trinh hoc tap
 * Route: /dashboard/recommendations
 * API: GET /recommendations/from-assessment, GET /recommendations
 */
const RecommendationsPage = () => {
  const navigate = useNavigate()
  const [recommendations, setRecommendations] = useState([])
  const [loading, setLoading] = useState(true)

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
        setRecommendations(data.recommendations || data.courses || [])
      } catch (error) {
        toast.error('Khong the tai de xuat')
      } finally {
        setLoading(false)
      }
    }
    fetchRecommendations()
  }, [])

  if (loading) return <div style={{ padding: 24, textAlign: 'center' }}>Dang tai de xuat...</div>

  return (
    <div style={{ padding: 16 }}>
      <div style={{ marginBottom: 20 }}>
        <h1 style={{ fontSize: '1.5rem', fontWeight: 700 }}>Lo trinh hoc tap goi y</h1>
        <p style={{ color: '#6b7280', fontSize: '0.85rem' }}>
          Dua tren ket qua danh gia nang luc cua ban
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: 12 }}>
        {recommendations.map((rec, idx) => (
          <Card key={rec.course_id || idx} hover>
            <CardBody>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <h3 style={{ fontWeight: 600, marginBottom: 4, flex: 1 }}>{rec.title}</h3>
                {rec.match_score != null && (
                  <span style={{
                    fontSize: '0.7rem', padding: '2px 8px', borderRadius: 10, fontWeight: 700,
                    background: rec.match_score >= 80 ? '#dcfce7' : '#e0e7ff',
                    color: rec.match_score >= 80 ? '#166534' : '#3730a3'
                  }}>
                    {Math.round(rec.match_score)}% phù hợp
                  </span>
                )}
              </div>
              {rec.reason && (
                <p style={{ fontSize: '0.8rem', color: '#6b7280', marginBottom: 8 }}>
                  {rec.reason}
                </p>
              )}
              <div style={{ display: 'flex', gap: 8, marginBottom: 8, flexWrap: 'wrap', fontSize: '0.7rem' }}>
                {rec.difficulty && (
                  <span style={{ padding: '2px 8px', background: '#f3f4f6', borderRadius: 10 }}>{rec.difficulty}</span>
                )}
                {rec.category && (
                  <span style={{ padding: '2px 8px', background: '#e0e7ff', borderRadius: 10, color: '#3730a3' }}>{rec.category}</span>
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
        ))}
      </div>

      {recommendations.length === 0 && !loading && (
        <div style={{ textAlign: 'center', padding: 40, color: '#6b7280' }}>
          <p>Chua co de xuat. Hay lam bai danh gia nang luc truoc!</p>
          <Button style={{ marginTop: 12 }} onClick={() => navigate('/dashboard/assessment')}>
            Bat dau danh gia
          </Button>
        </div>
      )}
    </div>
  )
}

export default RecommendationsPage
