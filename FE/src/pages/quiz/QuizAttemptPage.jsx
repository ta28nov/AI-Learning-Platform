import { useState, useEffect, useCallback } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import quizService from '@services/quizService'
import Button from '@components/ui/Button'
import Card, { CardBody } from '@components/ui/Card'

/**
 * Trang lam bai quiz
 * Route: /dashboard/quiz/:quizId/attempt
 * API: POST /quizzes/{quizId}/attempt
 */
const QuizAttemptPage = () => {
  const { quizId } = useParams()
  const navigate = useNavigate()

  const [quiz, setQuiz] = useState(null)
  const [answers, setAnswers] = useState({})
  const [currentIndex, setCurrentIndex] = useState(0)
  const [timeLeft, setTimeLeft] = useState(0)
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const startTime = useState(() => Date.now())[0]

  // Lay du lieu quiz khi mount
  useEffect(() => {
    const fetchQuiz = async () => {
      try {
        setLoading(true)
        const data = await quizService.getQuizDetail(quizId)
        setQuiz(data)
        // Thiet lap timer (phut → giay)
        if (data.time_limit) {
          setTimeLeft(data.time_limit * 60)
        }
      } catch (error) {
        toast.error('Khong the tai quiz')
      } finally {
        setLoading(false)
      }
    }
    fetchQuiz()
  }, [quizId])

  // Dong ho dem nguoc
  useEffect(() => {
    if (timeLeft <= 0 || loading || !quiz) return
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
  }, [timeLeft, loading, quiz])

  // Format thoi gian
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
      const timeSpentMinutes = Math.round((Date.now() - startTime) / 60000)
      const formattedAnswers = (quiz.questions || []).map((q) => ({
        question_id: q.question_id || q.id,
        selected_option: typeof answers[q.question_id || q.id] === 'number' ? answers[q.question_id || q.id] : null
      }))

      await quizService.submitAttempt(quizId, {
        answers: formattedAnswers,
        time_spent_minutes: timeSpentMinutes
      })

      toast.success('Nop bai thanh cong!')
      navigate(`/dashboard/quiz/${quizId}/results`)
    } catch (error) {
      toast.error(error.message || 'Khong the nop bai')
    } finally {
      setSubmitting(false)
    }
  }

  if (loading) return <div style={{ padding: 24, textAlign: 'center' }}>Dang tai quiz...</div>
  if (!quiz || !quiz.questions) return <div style={{ padding: 24, textAlign: 'center' }}>Khong co cau hoi</div>

  const currentQuestion = quiz.questions[currentIndex]
  const questionId = currentQuestion.question_id || currentQuestion.id
  const answeredCount = Object.keys(answers).length
  const isWarning = timeLeft < 60 && timeLeft > 0

  return (
    <div style={{ padding: 16, maxWidth: 900, margin: '0 auto' }}>
      {/* Header: timer + progress */}
      <div style={{
        display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 12,
        marginBottom: 20, padding: '12px 16px', background: '#f8f9fa', borderRadius: 10,
        position: 'sticky', top: 0, zIndex: 10
      }}>
        <div style={{ flex: 1 }}>
          <span style={{ fontSize: '0.8rem', fontWeight: 600, color: '#6b7280' }}>
            Cau {currentIndex + 1}/{quiz.questions.length}
          </span>
          <div style={{ height: 6, background: '#e5e7eb', borderRadius: 3, overflow: 'hidden', marginTop: 4 }}>
            <div style={{ height: '100%', width: `${((currentIndex + 1) / quiz.questions.length) * 100}%`, background: '#6366f1', borderRadius: 3, transition: 'width 0.3s' }} />
          </div>
        </div>
        {timeLeft > 0 && (
          <div style={{
            fontSize: '1.25rem', fontWeight: 700, fontVariantNumeric: 'tabular-nums',
            color: isWarning ? '#ef4444' : '#1a1a2e', minWidth: 70, textAlign: 'center',
            animation: isWarning ? 'pulse 1s infinite' : 'none'
          }}>
            {formatTime(timeLeft)}
          </div>
        )}
      </div>

      {/* Cau hoi */}
      <Card style={{ marginBottom: 20 }}>
        <CardBody>
          <div style={{ display: 'flex', gap: 8, marginBottom: 10, flexWrap: 'wrap' }}>
            {currentQuestion.is_mandatory && (
              <span style={{ fontSize: '0.65rem', padding: '2px 8px', background: '#fef3c7', color: '#92400e', borderRadius: 10, fontWeight: 600 }}>Bat buoc</span>
            )}
            {currentQuestion.points && (
              <span style={{ fontSize: '0.65rem', padding: '2px 8px', background: '#f3f4f6', color: '#6b7280', borderRadius: 10, fontWeight: 600 }}>{currentQuestion.points} diem</span>
            )}
          </div>

          <h3 style={{ fontSize: '1rem', fontWeight: 600, lineHeight: 1.6, marginBottom: 16 }}>
            {currentQuestion.question_text}
          </h3>

          {/* Options */}
          {currentQuestion.options && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              {currentQuestion.options.map((option, idx) => (
                <label
                  key={idx}
                  style={{
                    display: 'flex', alignItems: 'center', gap: 10, padding: '12px 14px',
                    border: `2px solid ${answers[questionId] === idx ? '#6366f1' : '#e5e7eb'}`,
                    borderRadius: 10, cursor: 'pointer', transition: 'all 0.15s',
                    background: answers[questionId] === idx ? 'rgba(99,102,241,0.06)' : 'transparent'
                  }}
                >
                  <input type="radio" name={`q_${questionId}`} checked={answers[questionId] === idx} onChange={() => handleAnswer(questionId, idx)} style={{ accentColor: '#6366f1' }} />
                  <span style={{
                    width: 28, height: 28, borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center',
                    fontWeight: 700, fontSize: '0.75rem', flexShrink: 0,
                    background: answers[questionId] === idx ? '#6366f1' : '#f3f4f6',
                    color: answers[questionId] === idx ? '#fff' : '#6b7280'
                  }}>
                    {String.fromCharCode(65 + idx)}
                  </span>
                  <span style={{ flex: 1, fontSize: '0.875rem' }}>{option}</span>
                </label>
              ))}
            </div>
          )}
        </CardBody>
      </Card>

      {/* Navigation */}
      <div style={{ display: 'flex', justifyContent: 'space-between', gap: 10 }}>
        <Button variant="outline" onClick={() => setCurrentIndex((i) => Math.max(0, i - 1))} disabled={currentIndex === 0}>
          ← Cau truoc
        </Button>
        {currentIndex < quiz.questions.length - 1 ? (
          <Button onClick={() => setCurrentIndex((i) => i + 1)}>Cau tiep →</Button>
        ) : (
          <Button variant="primary" onClick={handleSubmit} loading={submitting} disabled={submitting}>
            Nop bai ({answeredCount}/{quiz.questions.length})
          </Button>
        )}
      </div>
    </div>
  )
}

export default QuizAttemptPage
