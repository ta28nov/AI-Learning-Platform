import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import quizService from '@services/quizService'
import Button from '@components/ui/Button'
import Card, { CardHeader, CardBody } from '@components/ui/Card'

/**
 * Trang ket qua quiz chi tiet
 * Route: /dashboard/quiz/:quizId/results
 * API: GET /quizzes/{quizId}/results
 */
const QuizResultsPage = () => {
  const { quizId } = useParams()
  const navigate = useNavigate()
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchResults = async () => {
      try {
        setLoading(true)
        const data = await quizService.getQuizResults(quizId)
        setResults(data)
      } catch (error) {
        toast.error('Khong the tai ket qua')
      } finally {
        setLoading(false)
      }
    }
    fetchResults()
  }, [quizId])

  // Xu ly lam lai quiz (AI sinh cau hoi moi)
  const handleRetake = async () => {
    try {
      await quizService.retakeQuiz(quizId)
      navigate(`/dashboard/quiz/${quizId}/attempt`)
    } catch (error) {
      toast.error(error.message || 'Khong the lam lai quiz')
    }
  }

  if (loading) return <div style={{ padding: 24, textAlign: 'center' }}>Dang tai ket qua...</div>
  if (!results) return <div style={{ padding: 24, textAlign: 'center' }}>Khong tim thay ket qua</div>

  const isPassed = results.status === 'Pass'

  return (
    <div style={{ padding: 16, maxWidth: 900, margin: '0 auto' }}>
      {/* Score overview */}
      <Card style={{ marginBottom: 16 }}>
        <CardBody>
          <div style={{ textAlign: 'center', padding: '20px 0' }}>
            {/* Score circle */}
            <div style={{
              width: 120, height: 120, borderRadius: '50%', margin: '0 auto 16px',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              background: `conic-gradient(${isPassed ? '#10b981' : '#ef4444'} ${(results.total_score || 0) * 3.6}deg, #e5e7eb 0deg)`
            }}>
              <div style={{
                width: 95, height: 95, borderRadius: '50%', background: '#fff',
                display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center'
              }}>
                <span style={{ fontSize: '2rem', fontWeight: 800 }}>{Math.round(results.total_score || 0)}</span>
                <span style={{ fontSize: '0.7rem', color: '#6b7280' }}>diem</span>
              </div>
            </div>

            {/* Status banner */}
            <div style={{
              display: 'inline-block', padding: '6px 20px', borderRadius: 20,
              fontWeight: 700, fontSize: '0.9rem',
              background: isPassed ? '#dcfce7' : '#fecaca',
              color: isPassed ? '#166534' : '#991b1b'
            }}>
              {isPassed ? '✓ Pass' : '✗ Fail'}
            </div>

            <div style={{ marginTop: 8, fontSize: '0.8rem', color: '#6b7280' }}>
              Dieu kien: {results.pass_threshold}% | Bat buoc: {results.mandatory_passed ? 'Dat' : 'Chua dat'}
            </div>
          </div>
        </CardBody>
      </Card>

      {/* Chi tiet tung cau hoi */}
      {results.results && results.results.length > 0 && (
        <Card style={{ marginBottom: 16 }}>
          <CardHeader><h3>Chi tiet cau hoi</h3></CardHeader>
          <CardBody>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
              {results.results.map((item, idx) => (
                <div
                  key={item.question_id || idx}
                  style={{
                    padding: '14px 16px', borderRadius: 10,
                    borderLeft: `4px solid ${item.is_correct ? '#10b981' : '#ef4444'}`,
                    background: item.is_correct ? '#f0fdf4' : '#fef2f2'
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 6 }}>
                    <span style={{ fontWeight: 600, fontSize: '0.85rem', flex: 1 }}>
                      Cau {idx + 1}: {item.question_content}
                    </span>
                    <div style={{ display: 'flex', gap: 4, flexShrink: 0, marginLeft: 8 }}>
                      {item.is_mandatory && (
                        <span style={{ fontSize: '0.6rem', padding: '1px 6px', background: '#fef3c7', color: '#92400e', borderRadius: 8 }}>Bat buoc</span>
                      )}
                      <span style={{ fontSize: '0.6rem', padding: '1px 6px', borderRadius: 8, background: item.is_correct ? '#dcfce7' : '#fecaca', color: item.is_correct ? '#166534' : '#991b1b' }}>
                        {item.score || 0} diem
                      </span>
                    </div>
                  </div>

                  <div style={{ fontSize: '0.8rem', color: '#6b7280', marginBottom: 4 }}>
                    <strong>Dap an ban chon:</strong> {item.student_answer || '-'}
                  </div>
                  {!item.is_correct && (
                    <div style={{ fontSize: '0.8rem', color: '#166534' }}>
                      <strong>Dap an dung:</strong> {item.correct_answer}
                    </div>
                  )}
                  {item.explanation && (
                    <div style={{ fontSize: '0.8rem', color: '#6b7280', marginTop: 6, fontStyle: 'italic' }}>
                      {item.explanation}
                    </div>
                  )}
                  {item.related_lesson_link && (
                    <a
                      href={item.related_lesson_link}
                      onClick={(e) => { e.preventDefault(); navigate(item.related_lesson_link) }}
                      style={{ fontSize: '0.75rem', color: '#6366f1', marginTop: 4, display: 'inline-block' }}
                    >
                      Xem lai bai hoc →
                    </a>
                  )}
                </div>
              ))}
            </div>
          </CardBody>
        </Card>
      )}

      {/* Actions */}
      <div style={{ display: 'flex', gap: 10, justifyContent: 'center', flexWrap: 'wrap' }}>
        {results.can_retake && !isPassed && (
          <Button onClick={handleRetake}>Lam lai quiz</Button>
        )}
        <Button variant="outline" onClick={() => navigate(-1)}>Quay lai</Button>
      </div>
    </div>
  )
}

export default QuizResultsPage
