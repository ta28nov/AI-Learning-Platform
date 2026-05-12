import { useState, useEffect, useCallback } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { motion, AnimatePresence, useReducedMotion } from 'framer-motion'
import toast from 'react-hot-toast'
import assessmentService from '@services/assessmentService'
import Button from '@components/ui/Button'
import Card, { CardBody } from '@components/ui/Card'
import StateView from '@components/ui/StateView'
import AILoadingState from '@components/ui/AILoadingState'
import { pageTurn, pageFade } from '@/styles/motion'
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
  const shouldReduceMotion = useReducedMotion()

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
          const normalizedQuestions = (parsed.questions || []).map((q, idx) => ({
            ...q,
            // Defensive fallback: một số response AI có thể thiếu/trùng question_id
            question_id: q?.question_id || `local-q-${idx + 1}`,
          }))
          setQuestions(normalizedQuestions)
          setTimeLeft(parsed.time_limit_minutes * 60)
          setTotalTime(parsed.time_limit_minutes * 60)
        }
      } catch {
        toast.error('Không thể tải bài đánh giá')
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
    if (submitting || !questions.length) return
    setSubmitting(true)
    try {
      const formattedAnswers = questions.map((q) => ({
        question_id: q.question_id,
        // BE schema yêu cầu answer_content luôn là string (422 nếu gửi number/null)
        answer_content: String(answers[q.question_id] ?? ''),
        selected_option: q.question_type === 'multiple_choice' && typeof answers[q.question_id] === 'number'
          ? answers[q.question_id]
          : null,
        time_taken_seconds: 0
      }))

      await assessmentService.submit(sessionId, {
        answers: formattedAnswers,
        total_time_seconds: totalTime - timeLeft,
        submitted_at: new Date().toISOString()  // BE yêu cầu submitted_at (required)
      })

      toast.success('Nộp bài thành công!')
      sessionStorage.removeItem(`assessment_${sessionId}`)
      navigate(`/dashboard/assessment/${sessionId}/results`)
    } catch (error) {
      toast.error(error.message || 'Không thể nộp bài')
    } finally {
      setSubmitting(false)
    }
  }

  if (loading) {
    return (
      <AILoadingState
        title="Đang chuẩn bị bài đánh giá"
        message="Vui lòng chờ trong giây lát để đồng bộ dữ liệu phiên làm bài."
        steps={[
          'Đang đồng bộ phiên đánh giá...',
          'Đang nạp câu hỏi...',
          'Đang khởi tạo bộ đếm thời gian...',
        ]}
      />
    )
  }
  if (!questions.length) return <StateView type="empty" title="Không tìm thấy bài đánh giá" message="Session đánh giá không có câu hỏi khả dụng." actionLabel="Quay lại đánh giá" onAction={() => navigate('/dashboard/assessment')} />

  const safeIndex = Math.min(Math.max(currentIndex, 0), Math.max(questions.length - 1, 0))
  const currentQuestion = questions[safeIndex]
  const safeQuestionId = currentQuestion?.question_id || `local-q-${safeIndex + 1}`
  const answeredCount = Object.keys(answers).length
  const isWarning = timeLeft < 60

  return (
    <div className="assessment-quiz-page">
      {/* Header: timer + progress */}
      <div className="quiz-header">
        <div className="quiz-progress">
          <span>Câu {safeIndex + 1}/{questions.length}</span>
          <div className="quiz-progress__bar">
            <div
              className="quiz-progress__fill"
              style={{ width: `${((safeIndex + 1) / questions.length) * 100}%` }}
            />
          </div>
        </div>
        <div className={`quiz-timer ${isWarning ? 'quiz-timer--warning' : ''}`}>
          {formatTime(timeLeft)}
        </div>
      </div>

      {/* Cau hoi hien tai */}
      <AnimatePresence mode="wait">
      <motion.div
        key={`${safeQuestionId}-${safeIndex}`}
        variants={shouldReduceMotion ? pageFade : pageTurn}
        initial="initial"
        animate="animate"
        exit="exit"
      >
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
              <span className="points-badge">{currentQuestion.points} điểm</span>
            )}
          </div>

          <h3 className="question-text">{currentQuestion.question_text}</h3>

          {/* Render theo loai cau hoi */}
          {currentQuestion.question_type === 'multiple_choice' && currentQuestion.options && (
            <div className="options-list">
              {currentQuestion.options.map((option, idx) => (
                <label
                  key={idx}
                  className={`option-item ${answers[safeQuestionId] === idx ? 'option-item--selected' : ''}`}
                >
                  <input
                    type="radio"
                    name={`q_${safeQuestionId}`}
                    checked={answers[safeQuestionId] === idx}
                    onChange={() => handleAnswer(safeQuestionId, idx)}
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
                placeholder="Nhập câu trả lời..."
                value={answers[safeQuestionId] || ''}
                onChange={(e) => handleAnswer(safeQuestionId, e.target.value)}
              />
            </div>
          )}

          {currentQuestion.question_type === 'drag_and_drop' && (
            <div className="fill-input-wrapper">
              <input
                type="text"
                className="fill-input"
                placeholder="Nhập thứ tự/sắp xếp đáp án của bạn..."
                value={answers[safeQuestionId] || ''}
                onChange={(e) => handleAnswer(safeQuestionId, e.target.value)}
              />
            </div>
          )}

          {currentQuestion.question_type === 'true_false' && (
            <div className="options-list">
              {['True', 'False'].map((option, idx) => (
                <label
                  key={idx}
                  className={`option-item ${answers[safeQuestionId] === option ? 'option-item--selected' : ''}`}
                >
                  <input
                    type="radio"
                    name={`q_${safeQuestionId}`}
                    checked={answers[safeQuestionId] === option}
                    onChange={() => handleAnswer(safeQuestionId, option)}
                  />
                  <span className="option-text">{option}</span>
                </label>
              ))}
            </div>
          )}

          {!['multiple_choice', 'fill_in_blank', 'drag_and_drop', 'true_false'].includes(currentQuestion.question_type) && (
            <div className="fill-input-wrapper">
              <input
                type="text"
                className="fill-input"
                placeholder="Nhập câu trả lời..."
                value={answers[safeQuestionId] || ''}
                onChange={(e) => handleAnswer(safeQuestionId, e.target.value)}
              />
            </div>
          )}
        </CardBody>
      </Card>
      </motion.div>
      </AnimatePresence>

      {/* Navigation */}
      <div className="quiz-navigation">
        <Button
          variant="outline"
          onClick={() => setCurrentIndex((i) => Math.max(0, i - 1))}
          disabled={safeIndex === 0}
        >
          ← Câu trước
        </Button>

        {safeIndex < questions.length - 1 ? (
          <Button onClick={() => setCurrentIndex((i) => Math.min(i + 1, questions.length - 1))}>
            Câu tiếp →
          </Button>
        ) : (
          <Button
            variant="primary"
            onClick={handleSubmit}
            loading={submitting}
            disabled={submitting}
          >
            Nộp bài ({answeredCount}/{questions.length})
          </Button>
        )}
      </div>
    </div>
  )
}

export default AssessmentQuizPage
