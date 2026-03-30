import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import quizService from '@services/quizService'
import Button from '@components/ui/Button'
import Card, { CardHeader, CardBody } from '@components/ui/Card'
import './QuizResultsPage.css'

/**
 * Trang kết quả quiz chi tiết
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
        toast.error('Không thể tải kết quả')
      } finally {
        setLoading(false)
      }
    }
    fetchResults()
  }, [quizId])

  // Xử lý làm lại quiz (AI sinh câu hỏi mới)
  const handleRetake = async () => {
    try {
      await quizService.retakeQuiz(quizId)
      navigate(`/dashboard/quiz/${quizId}/attempt`)
    } catch (error) {
      toast.error(error.message || 'Không thể làm lại quiz')
    }
  }

  if (loading) return <div className="quiz-results-state">Đang tải kết quả...</div>
  if (!results) return <div className="quiz-results-state">Không tìm thấy kết quả</div>

  const isPassed = results.status === 'Pass'

  // Màu gradient cho vòng tròn điểm
  const circleStyle = {
    background: `conic-gradient(${isPassed ? '#10b981' : '#ef4444'} ${(results.total_score || 0) * 3.6}deg, #e5e7eb 0deg)`
  }

  return (
    <div className="quiz-results-page">
      {/* Tổng quan điểm số */}
      <Card className="quiz-results-section">
        <CardBody>
          <div className="quiz-results-overview">
            {/* Vòng tròn điểm */}
            <div className="quiz-results-circle" style={circleStyle}>
              <div className="quiz-results-circle__inner">
                <span className="quiz-results-circle__score">{Math.round(results.total_score || 0)}</span>
                <span className="quiz-results-circle__label">điểm</span>
              </div>
            </div>

            {/* Badge đạt/không đạt */}
            <div className={`quiz-results-badge ${isPassed ? 'quiz-results-badge--pass' : 'quiz-results-badge--fail'}`}>
              {isPassed ? '✓ Đạt' : '✗ Không đạt'}
            </div>

            {/* Điều kiện đạt + câu bắt buộc */}
            <div className="quiz-results-condition">
              Điều kiện: {results.pass_threshold}% | Câu bắt buộc: {results.mandatory_passed ? 'Đạt' : 'Chưa đạt'}
            </div>
          </div>
        </CardBody>
      </Card>

      {/* Chi tiết từng câu hỏi */}
      {results.results && results.results.length > 0 && (
        <Card className="quiz-results-section">
          <CardHeader><h3>Chi tiết câu hỏi</h3></CardHeader>
          <CardBody>
            {results.results.map((item, idx) => (
              <div
                key={item.question_id || idx}
                className={`quiz-results-item ${item.is_correct ? 'quiz-results-item--correct' : 'quiz-results-item--wrong'}`}
              >
                <div className="quiz-results-item__header">
                  <span className="quiz-results-item__question">
                    Câu {idx + 1}: {item.question_content}
                  </span>
                  <div className="quiz-results-item__badges">
                    {item.is_mandatory && (
                      <span className="quiz-results-item__badge quiz-results-item__badge--mandatory">Bắt buộc</span>
                    )}
                    <span className={`quiz-results-item__badge ${item.is_correct ? 'quiz-results-item__badge--score-correct' : 'quiz-results-item__badge--score-wrong'}`}>
                      {item.score || 0} điểm
                    </span>
                  </div>
                </div>

                <div className="quiz-results-item__answer">
                  <strong>Đáp án bạn chọn:</strong> {item.student_answer || '-'}
                </div>
                {!item.is_correct && (
                  <div className="quiz-results-item__correct-answer">
                    <strong>Đáp án đúng:</strong> {item.correct_answer}
                  </div>
                )}
                {item.explanation && (
                  <div className="quiz-results-item__explanation">
                    {item.explanation}
                  </div>
                )}
                {item.related_lesson_link && (
                  <a
                    href={item.related_lesson_link}
                    className="quiz-results-item__link"
                    onClick={(e) => { e.preventDefault(); navigate(item.related_lesson_link) }}
                  >
                    Xem lại bài học →
                  </a>
                )}
              </div>
            ))}
          </CardBody>
        </Card>
      )}

      {/* Hành động */}
      <div className="quiz-results-actions">
        {results.can_retake && !isPassed && (
          <Button onClick={handleRetake}>Làm lại quiz</Button>
        )}
        <Button variant="outline" onClick={() => navigate(-1)}>Quay lại</Button>
      </div>
    </div>
  )
}

export default QuizResultsPage
