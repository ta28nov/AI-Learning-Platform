import { useState, useEffect, useCallback } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { motion, AnimatePresence, useReducedMotion } from 'framer-motion'
import toast from 'react-hot-toast'
import quizService from '@services/quizService'
import Button from '@components/ui/Button'
import Card, { CardBody } from '@components/ui/Card'
import StateView from '@components/ui/StateView'
import { pageTurn, pageFade } from '@/styles/motion'
import './QuizAttemptPage.css'

/**
 * Trang làm bài quiz
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
  const shouldReduceMotion = useReducedMotion()

  // Lấy dữ liệu quiz khi mount
  useEffect(() => {
    const fetchQuiz = async () => {
      try {
        setLoading(true)
        const data = await quizService.getQuizDetail(quizId)
        setQuiz(data)
        // Thiết lập timer (phút → giây)
        if (data.time_limit) {
          setTimeLeft(data.time_limit * 60)
        }
      } catch (error) {
        toast.error('Không thể tải quiz')
      } finally {
        setLoading(false)
      }
    }
    fetchQuiz()
  }, [quizId])

  // Đồng hồ đếm ngược
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

  // Format thời gian mm:ss
  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }

  // Xử lý chọn đáp án
  const handleAnswer = useCallback((questionId, value) => {
    setAnswers((prev) => ({ ...prev, [questionId]: value }))
  }, [])

  // Xử lý nộp bài
  const handleSubmit = async () => {
    setSubmitting(true)
    try {
      const timeSpentMinutes = Math.round((Date.now() - startTime) / 60000)
      // BE QuizAttemptRequest.AnswerItem: question_id (str), selected_option (str: "A"|"B"|"C"|"D" or fill-in text)
      const formattedAnswers = (quiz.questions || []).map((q) => ({
        question_id: q.question_id || q.id,
        selected_option: typeof answers[q.question_id || q.id] === 'number'
          ? String.fromCharCode(65 + answers[q.question_id || q.id])  // 0→"A", 1→"B", 2→"C", 3→"D"
          : (answers[q.question_id || q.id] || '')
      }))

      await quizService.submitAttempt(quizId, {
        answers: formattedAnswers,
        time_spent_minutes: timeSpentMinutes
      })

      toast.success('Nộp bài thành công!')
      navigate(`/dashboard/quiz/${quizId}/results`)
    } catch (error) {
      toast.error(error.message || 'Không thể nộp bài')
    } finally {
      setSubmitting(false)
    }
  }

  if (loading) return <div className="quiz-attempt-state">Đang tải quiz...</div>
  if (!quiz || !quiz.questions) return <StateView type="empty" title="Không có câu hỏi" message="Quiz hiện không có dữ liệu hợp lệ." actionLabel="Quay lại Quiz" onAction={() => navigate('/dashboard/quiz')} />

  const currentQuestion = quiz.questions[currentIndex]
  const questionId = currentQuestion.question_id || currentQuestion.id
  const answeredCount = Object.keys(answers).length
  const isWarning = timeLeft < 60 && timeLeft > 0
  const progressPercent = ((currentIndex + 1) / quiz.questions.length) * 100

  return (
    <div className="quiz-attempt-page">
      {/* Header: timer + thanh tiến trình */}
      <div className="quiz-attempt-header">
        <div className="quiz-attempt-header__progress">
          <span className="quiz-attempt-header__label">
            Câu {currentIndex + 1}/{quiz.questions.length}
          </span>
          <div className="quiz-attempt-header__bar">
            <div
              className="quiz-attempt-header__bar-fill"
              style={{ width: `${progressPercent}%` }}
            />
          </div>
        </div>
        {timeLeft > 0 && (
          <div className={`quiz-attempt-timer ${isWarning ? 'quiz-attempt-timer--warning' : ''}`}>
            {formatTime(timeLeft)}
          </div>
        )}
      </div>

      {/* Câu hỏi */}
      <AnimatePresence mode="wait">
      <motion.div
        key={questionId}
        variants={shouldReduceMotion ? pageFade : pageTurn}
        initial="initial"
        animate="animate"
        exit="exit"
      >
      <Card className="quiz-attempt-question">
        <CardBody>
          {/* Metadata: bắt buộc + điểm */}
          <div className="quiz-attempt-question__meta">
            {currentQuestion.is_mandatory && (
              <span className="quiz-attempt-question__badge quiz-attempt-question__badge--mandatory">
                Bắt buộc
              </span>
            )}
            {currentQuestion.points && (
              <span className="quiz-attempt-question__badge quiz-attempt-question__badge--points">
                {currentQuestion.points} điểm
              </span>
            )}
          </div>

          <h3 className="quiz-attempt-question__text">
            {currentQuestion.question_text}
          </h3>

          {/* Danh sách lựa chọn */}
          {currentQuestion.options && (
            <div className="quiz-attempt-options">
              {currentQuestion.options.map((option, idx) => {
                const isSelected = answers[questionId] === idx
                return (
                  <label
                    key={idx}
                    className={`quiz-attempt-option ${isSelected ? 'quiz-attempt-option--selected' : ''}`}
                  >
                    <input
                      type="radio"
                      className="quiz-attempt-option__input"
                      name={`q_${questionId}`}
                      checked={isSelected}
                      onChange={() => handleAnswer(questionId, idx)}
                    />
                    <span className={`quiz-attempt-option__letter ${isSelected ? 'quiz-attempt-option__letter--selected' : 'quiz-attempt-option__letter--default'}`}>
                      {String.fromCharCode(65 + idx)}
                    </span>
                    <span className="quiz-attempt-option__text">{option}</span>
                  </label>
                )
              })}
            </div>
          )}
        </CardBody>
      </Card>
      </motion.div>
      </AnimatePresence>

      {/* Điều hướng câu hỏi */}
      <div className="quiz-attempt-nav">
        <Button
          variant="outline"
          onClick={() => setCurrentIndex((i) => Math.max(0, i - 1))}
          disabled={currentIndex === 0}
        >
          ← Câu trước
        </Button>
        {currentIndex < quiz.questions.length - 1 ? (
          <Button onClick={() => setCurrentIndex((i) => i + 1)}>Câu tiếp →</Button>
        ) : (
          <Button
            variant="primary"
            onClick={handleSubmit}
            loading={submitting}
            disabled={submitting}
          >
            Nộp bài ({answeredCount}/{quiz.questions.length})
          </Button>
        )}
      </div>
    </div>
  )
}

export default QuizAttemptPage
