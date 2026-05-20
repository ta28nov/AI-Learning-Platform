import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import toast from 'react-hot-toast'
import quizService from '@services/quizService'
import Button from '@components/ui/Button'
import StateView from '@components/ui/StateView'
import ClassLearningBanner from '@components/classes/ClassLearningBanner'
import QuizWrongAnswerExplainer from '@components/quiz/QuizWrongAnswerExplainer'
import ChatWidget from '@components/chat/ChatWidget'
import './QuizResultsPage.css'

const CheckIcon = () => (
  <svg viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="m4 10 4 4 8-8"/>
  </svg>
)
const XIcon = () => (
  <svg viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="m5 5 10 10M15 5 5 15"/>
  </svg>
)
const ChevronIcon = ({ open }) => (
  <svg viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"
    style={{ transform: open ? 'rotate(180deg)' : 'none', transition: 'transform 0.25s ease' }}>
    <path d="m5 8 5 5 5-5"/>
  </svg>
)

/**
 * QuizResultsPage — Kết quả quiz chi tiết
 * Route: /dashboard/quiz/:quizId/results
 * API: GET /quizzes/{quizId}/results via quizService.getQuizResults — unchanged
 */
const QuizResultsPage = () => {
  const { quizId } = useParams()
  const navigate = useNavigate()
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(true)
  const [expanded, setExpanded] = useState({})

  useEffect(() => {
    const fetchResults = async () => {
      try {
        setLoading(true)
        const data = await quizService.getQuizResults(quizId)
        setResults(data)
      } catch {
        toast.error('Không thể tải kết quả')
      } finally {
        setLoading(false)
      }
    }
    fetchResults()
  }, [quizId])

  const handleRetake = async () => {
    try {
      await quizService.retakeQuiz(quizId)
      navigate(`/dashboard/quiz/${quizId}/attempt`)
    } catch (error) {
      toast.error(error.message || 'Không thể làm lại quiz')
    }
  }

  const toggleExpand = (id) => setExpanded(prev => ({ ...prev, [id]: !prev[id] }))

  if (loading) return <div className="qr-page"><StateView type="loading" message="Đang tải kết quả…" /></div>
  if (!results) return <div className="qr-page"><StateView type="empty" message="Không tìm thấy kết quả" action={{ label: 'Quay lại', onClick: () => navigate(-1) }} /></div>

  const isPassed = results.status === 'Pass' || results.status === 'pass'
  const score = Math.round(results.total_score || 0)
  const wrongItems = (results.results || []).filter((item) => !item.is_correct)
  const courseId = results.course_id
  const circumference = 2 * Math.PI * 44
  const dashOffset = circumference - (score / 100) * circumference

  return (
    <div className="qr-page">
      <ClassLearningBanner courseId={courseId} />
      {/* Score hero */}
      <motion.div
        className="qr-hero"
        initial={{ opacity: 0, y: 24 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, ease: [0.65, 0, 0.35, 1] }}
      >
        {/* SVG ring */}
        <div className="qr-ring-wrap">
          <svg className="qr-ring" viewBox="0 0 100 100">
            <circle className="qr-ring__track" cx="50" cy="50" r="44" />
            <motion.circle
              className={`qr-ring__fill qr-ring__fill--${isPassed ? 'pass' : 'fail'}`}
              cx="50" cy="50" r="44"
              strokeDasharray={circumference}
              initial={{ strokeDashoffset: circumference }}
              animate={{ strokeDashoffset: dashOffset }}
              transition={{ duration: 1, delay: 0.3, ease: [0.65, 0, 0.35, 1] }}
            />
          </svg>
          <div className="qr-ring__inner">
            <span className="qr-ring__score">{score}</span>
            <span className="qr-ring__label">điểm</span>
          </div>
        </div>

        {/* Pass/fail badge */}
        <div className={`qr-badge qr-badge--${isPassed ? 'pass' : 'fail'}`}>
          <span className="qr-badge__icon">{isPassed ? <CheckIcon /> : <XIcon />}</span>
          <span className="qr-badge__text">{isPassed ? 'Đạt' : 'Không đạt'}</span>
        </div>

        <p className="qr-condition">
          Điều kiện: {results.pass_threshold}%&nbsp;·&nbsp;
          Câu bắt buộc: <strong>{results.mandatory_passed ? 'Đạt' : 'Chưa đạt'}</strong>
        </p>
      </motion.div>

      {/* Question accordion */}
      {results.results && results.results.length > 0 && (
        <motion.div
          className="qr-questions"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.45, delay: 0.2 }}
        >
          <h2 className="qr-section-title">Chi tiết từng câu</h2>
          {results.results.map((item, idx) => {
            const key = item.question_id || idx
            const open = !!expanded[key]
            return (
              <div
                key={key}
                className={`qr-item qr-item--${item.is_correct ? 'correct' : 'wrong'}`}
              >
                <button
                  className="qr-item__header"
                  onClick={() => toggleExpand(key)}
                  aria-expanded={open}
                >
                  <div className="qr-item__header-left">
                    <span className={`qr-item__dot qr-item__dot--${item.is_correct ? 'correct' : 'wrong'}`} />
                    <span className="qr-item__q-label">Câu {idx + 1}</span>
                    <span className="qr-item__q-text">{item.question_content}</span>
                  </div>
                  <div className="qr-item__header-right">
                    {item.is_mandatory && <span className="qr-item__mandatory">Bắt buộc</span>}
                    <span className="qr-item__score-badge">{item.score || 0} điểm</span>
                    <span className="qr-item__chevron"><ChevronIcon open={open} /></span>
                  </div>
                </button>

                <AnimatePresence initial={false}>
                  {open && (
                    <motion.div
                      key="content"
                      className="qr-item__body"
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: 'auto', opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      transition={{ duration: 0.28, ease: [0.65, 0, 0.35, 1] }}
                    >
                      <div className="qr-item__body-inner">
                        <div className="qr-item__answer">
                          <span className="qr-item__answer-label">Đáp án của bạn:</span>
                          <span className={`qr-item__answer-val ${item.is_correct ? 'qr-item__answer-val--correct' : 'qr-item__answer-val--wrong'}`}>
                            {item.student_answer || '(Không trả lời)'}
                          </span>
                        </div>
                        {!item.is_correct && (
                          <div className="qr-item__answer">
                            <span className="qr-item__answer-label">Đáp án đúng:</span>
                            <span className="qr-item__answer-val qr-item__answer-val--correct">{item.correct_answer}</span>
                          </div>
                        )}
                        {item.explanation && (
                          <p className="qr-item__explanation">{item.explanation}</p>
                        )}
                        {item.related_lesson_link && (
                          <button
                            className="qr-item__lesson-link"
                            onClick={() => navigate(item.related_lesson_link)}
                          >
                            Xem lại bài học →
                          </button>
                        )}
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            )
          })}
        </motion.div>
      )}

      <QuizWrongAnswerExplainer
        courseId={courseId}
        quizTitle={results.quiz_title}
        wrongItems={wrongItems}
      />

      {courseId && (
        <ChatWidget
          courseId={courseId}
          contextType="general"
          subtitle="Hỏi thêm về kết quả quiz"
          suggestions={[
            'Tóm tắt các lỗi sai chính trong bài vừa làm',
            'Gợi ý cách ôn lại phần kiến thức liên quan',
          ]}
        />
      )}

      {/* Actions */}
      <div className="qr-actions">
        {results.can_retake && !isPassed && (
          <Button variant="primary" onClick={handleRetake}>Làm lại quiz</Button>
        )}
        <Button variant="outline" onClick={() => navigate(-1)}>Quay lại</Button>
      </div>
    </div>
  )
}

export default QuizResultsPage
