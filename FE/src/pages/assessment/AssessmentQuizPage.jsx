import { useState, useEffect, useCallback } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import assessmentService from '@services/assessmentService'
import Button from '@components/ui/Button'
import Card, { CardBody } from '@components/ui/Card'
import './AssessmentQuizPage.css'

/**
 * Trang lam bai danh gia nang luc
 * Route: /dashboard/assessment/:sessionId
 * Nhan questions tu generate → user tra loi → submit
 */
const AssessmentQuizPage = () => {
  const { sessionId } = useParams()
  const navigate = useNavigate()

  const [questions, setQuestions] = useState([])
  const [answers, setAnswers] = useState({})
  const [currentIndex, setCurrentIndex] = useState(0)
  const [timeLeft, setTimeLeft] = useState(0)
  const [totalTime, setTotalTime] = useState(0)
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)

  // Lay du lieu bai danh gia khi mount
  useEffect(() => {
    const fetchAssessment = async () => {
      try {
        setLoading(true)
        const data = await assessmentService.getResults(sessionId)
        // Neu da co ket qua, chuyen sang trang results
        if (data.overall_score !== undefined) {
          navigate(`/dashboard/assessment/${sessionId}/results`, { replace: true })
          return
        }
      } catch {
        // Chua co ket qua = chua lam → tiep tuc
      }

      try {
        // Lay questions tu session (response tu generate da luu trong state truoc do)
        // Fallback: doc tu sessionStorage
        const saved = sessionStorage.getItem(`assessment_${sessionId}`)
        if (saved) {
          const parsed = JSON.parse(saved)
          setQuestions(parsed.questions || [])
          setTimeLeft(parsed.time_limit_minutes * 60)
          setTotalTime(parsed.time_limit_minutes * 60)
        }
      } catch {
        toast.error('Khong the tai bai danh gia')
      } finally {
        setLoading(false)
      }
    }
    fetchAssessment()
  }, [sessionId, navigate])

  // Dong ho dem nguoc
  useEffect(() => {
    if (timeLeft <= 0 || loading) return
    const timer = setInterval(() => {
      setTimeLeft((prev) => {
        if (prev <= 1) {
          clearInterval(timer)
          handleSubmit()
          return 0
        }
        return prev - 1
      })
    }, 1000)
    return () => clearInterval(timer)
  }, [timeLeft, loading])

  // Format thoi gian MM:SS
  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }

  // Xu ly chon dap an
  const handleAnswer = useCallback((questionId, value) => {
    setAnswers((prev) => ({ ...prev, [questionId]: value }))
  }, [])

  // Xu ly nop bai
  const handleSubmit = async () => {
    setSubmitting(true)
    try {
      const formattedAnswers = questions.map((q) => ({
        question_id: q.question_id,
        answer_content: answers[q.question_id] || '',
        selected_option: typeof answers[q.question_id] === 'number' ? answers[q.question_id] : null,
        time_taken_seconds: 0
      }))

      await assessmentService.submit(sessionId, {
        answers: formattedAnswers,
        total_time_seconds: totalTime - timeLeft
      })

      toast.success('Nop bai thanh cong!')
      sessionStorage.removeItem(`assessment_${sessionId}`)
      navigate(`/dashboard/assessment/${sessionId}/results`)
    } catch (error) {
      toast.error(error.message || 'Khong the nop bai')
    } finally {
      setSubmitting(false)
    }
  }

  if (loading) return <div className="loading-spinner">Dang tai...</div>
  if (!questions.length) return <div className="empty-state">Khong tim thay bai danh gia</div>

  const currentQuestion = questions[currentIndex]
  const answeredCount = Object.keys(answers).length
  const isWarning = timeLeft < 60

  return (
    <div className="assessment-quiz-page">
      {/* Header: timer + progress */}
      <div className="quiz-header">
        <div className="quiz-progress">
          <span>Cau {currentIndex + 1}/{questions.length}</span>
          <div className="quiz-progress__bar">
            <div
              className="quiz-progress__fill"
              style={{ width: `${((currentIndex + 1) / questions.length) * 100}%` }}
            />
          </div>
        </div>
        <div className={`quiz-timer ${isWarning ? 'quiz-timer--warning' : ''}`}>
          {formatTime(timeLeft)}
        </div>
      </div>

      {/* Cau hoi hien tai */}
      <Card className="question-card">
        <CardBody>
          <div className="question-meta">
            {currentQuestion.difficulty && (
              <span className={`difficulty-badge difficulty-badge--${currentQuestion.difficulty}`}>
                {currentQuestion.difficulty}
              </span>
            )}
            {currentQuestion.skill_tag && (
              <span className="skill-badge">{currentQuestion.skill_tag}</span>
            )}
            {currentQuestion.points && (
              <span className="points-badge">{currentQuestion.points} diem</span>
            )}
          </div>

          <h3 className="question-text">{currentQuestion.question_text}</h3>

          {/* Render theo loai cau hoi */}
          {currentQuestion.question_type === 'multiple_choice' && currentQuestion.options && (
            <div className="options-list">
              {currentQuestion.options.map((option, idx) => (
                <label
                  key={idx}
                  className={`option-item ${answers[currentQuestion.question_id] === idx ? 'option-item--selected' : ''}`}
                >
                  <input
                    type="radio"
                    name={`q_${currentQuestion.question_id}`}
                    checked={answers[currentQuestion.question_id] === idx}
                    onChange={() => handleAnswer(currentQuestion.question_id, idx)}
                  />
                  <span className="option-label">{String.fromCharCode(65 + idx)}</span>
                  <span className="option-text">{option}</span>
                </label>
              ))}
            </div>
          )}

          {currentQuestion.question_type === 'fill_in_blank' && (
            <div className="fill-input-wrapper">
              <input
                type="text"
                className="fill-input"
                placeholder="Nhap cau tra loi..."
                value={answers[currentQuestion.question_id] || ''}
                onChange={(e) => handleAnswer(currentQuestion.question_id, e.target.value)}
              />
            </div>
          )}

          {currentQuestion.question_type === 'true_false' && (
            <div className="options-list">
              {['True', 'False'].map((option, idx) => (
                <label
                  key={idx}
                  className={`option-item ${answers[currentQuestion.question_id] === option ? 'option-item--selected' : ''}`}
                >
                  <input
                    type="radio"
                    name={`q_${currentQuestion.question_id}`}
                    checked={answers[currentQuestion.question_id] === option}
                    onChange={() => handleAnswer(currentQuestion.question_id, option)}
                  />
                  <span className="option-text">{option}</span>
                </label>
              ))}
            </div>
          )}
        </CardBody>
      </Card>

      {/* Navigation */}
      <div className="quiz-navigation">
        <Button
          variant="outline"
          onClick={() => setCurrentIndex((i) => Math.max(0, i - 1))}
          disabled={currentIndex === 0}
        >
          ← Cau truoc
        </Button>

        {currentIndex < questions.length - 1 ? (
          <Button onClick={() => setCurrentIndex((i) => i + 1)}>
            Cau tiep →
          </Button>
        ) : (
          <Button
            variant="primary"
            onClick={handleSubmit}
            loading={submitting}
            disabled={submitting}
          >
            Nop bai ({answeredCount}/{questions.length})
          </Button>
        )}
      </div>
    </div>
  )
}

export default AssessmentQuizPage
