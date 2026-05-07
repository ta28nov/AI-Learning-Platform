import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import toast from 'react-hot-toast'
import quizService from '@services/quizService'
import Button from '@components/ui/Button'
import StateView from '@components/ui/StateView'
import './QuizDetailPage.css'

/**
 * QuizDetailPage — Chi tiết quiz trước khi làm bài
 * Route: /dashboard/quiz/:quizId
 * API: GET /quizzes/{quizId} via quizService.getQuizDetail — unchanged
 */
const QuizDetailPage = () => {
  const { quizId } = useParams()
  const navigate = useNavigate()
  const [quiz, setQuiz] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchQuiz = async () => {
      try {
        setLoading(true)
        const data = await quizService.getQuizDetail(quizId)
        setQuiz(data)
      } catch {
        toast.error('Không thể tải thông tin quiz')
      } finally {
        setLoading(false)
      }
    }
    if (quizId) fetchQuiz()
  }, [quizId])

  if (loading) return <div className="qd-page"><StateView type="loading" message="Đang tải quiz…" /></div>
  if (!quiz) return (
    <div className="qd-page">
      <StateView
        type="empty"
        message="Không tìm thấy quiz"
        action={{ label: 'Quay lại', onClick: () => navigate(-1) }}
      />
    </div>
  )

  const fadeUp = { hidden: { opacity: 0, y: 20 }, visible: { opacity: 1, y: 0 } }

  return (
    <div className="qd-page">
      {/* Back + Header */}
      <motion.div className="qd-header" initial="hidden" animate="visible" variants={fadeUp} transition={{ duration: 0.4 }}>
        <button className="qd-back" onClick={() => navigate(-1)}>
          <svg viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.5">
            <path d="M15 10H5m0 0 5-5M5 10l5 5" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
          Quay lại
        </button>
        <svg className="qd-ornament" viewBox="0 0 48 12" fill="none">
          <line x1="0" y1="6" x2="16" y2="6" stroke="var(--gold-500)" strokeWidth="1" />
          <circle cx="24" cy="6" r="4" stroke="var(--gold-500)" strokeWidth="1" />
          <line x1="32" y1="6" x2="48" y2="6" stroke="var(--gold-500)" strokeWidth="1" />
        </svg>
        <h1 className="qd-title">{quiz.title}</h1>
        {quiz.description && <p className="qd-desc">{quiz.description}</p>}
      </motion.div>

      {/* Info grid */}
      <motion.div className="qd-info-grid" initial="hidden" animate="visible" variants={fadeUp} transition={{ duration: 0.4, delay: 0.1 }}>
        {[
          { label: 'Số câu hỏi', value: quiz.question_count || 0, unit: 'câu' },
          { label: 'Thời gian', value: quiz.time_limit || '—', unit: 'phút' },
          { label: 'Điểm đạt', value: `${quiz.pass_threshold || 70}%`, unit: '' },
          { label: 'Câu bắt buộc', value: quiz.mandatory_question_count || 0, unit: 'câu' },
          ...(quiz.max_attempts != null ? [{ label: 'Số lần tối đa', value: quiz.max_attempts || '∞', unit: '' }] : []),
          ...(quiz.is_retakeable != null ? [{ label: 'Làm lại', value: quiz.is_retakeable ? 'Được phép' : 'Không', unit: '' }] : []),
        ].map(({ label, value, unit }) => (
          <div key={label} className="qd-stat-card">
            <span className="qd-stat-card__label">{label}</span>
            <span className="qd-stat-card__value">{value}</span>
            {unit && <span className="qd-stat-card__unit">{unit}</span>}
          </div>
        ))}
      </motion.div>

      {/* History */}
      {quiz.user_attempts != null && quiz.user_attempts > 0 && (
        <motion.div className="qd-history" initial="hidden" animate="visible" variants={fadeUp} transition={{ duration: 0.4, delay: 0.15 }}>
          <h2 className="qd-section-title">Lịch sử làm bài</h2>
          <div className="qd-history__stats">
            <div className="qd-history__stat">
              <span className="qd-history__stat-label">Số lần đã làm</span>
              <span className="qd-history__stat-value">{quiz.user_attempts}</span>
            </div>
            {quiz.best_score != null && (
              <div className="qd-history__stat">
                <span className="qd-history__stat-label">Điểm cao nhất</span>
                <span className={`qd-history__stat-value ${quiz.best_score >= (quiz.pass_threshold || 70) ? 'qd-history__stat-value--pass' : 'qd-history__stat-value--fail'}`}>
                  {Math.round(quiz.best_score)}%
                </span>
              </div>
            )}
            {quiz.last_attempt_at && (
              <div className="qd-history__stat">
                <span className="qd-history__stat-label">Lần cuối</span>
                <span className="qd-history__stat-value">
                  {new Date(quiz.last_attempt_at).toLocaleDateString('vi-VN')}
                </span>
              </div>
            )}
          </div>
        </motion.div>
      )}

      {/* Instructions */}
      <motion.div className="qd-instructions" initial="hidden" animate="visible" variants={fadeUp} transition={{ duration: 0.4, delay: 0.2 }}>
        <h2 className="qd-section-title">Hướng dẫn</h2>
        <ul className="qd-instructions__list">
          <li>Đọc kỹ câu hỏi trước khi trả lời</li>
          <li>Chọn đáp án đúng nhất cho mỗi câu hỏi</li>
          <li>Có thể quay lại các câu hỏi trước đó</li>
          {quiz.time_limit && <li>Thời gian làm bài: {quiz.time_limit} phút</li>}
          <li>Điểm đạt tối thiểu: {quiz.pass_threshold || 70}%</li>
          {quiz.mandatory_question_count > 0 && <li>Có {quiz.mandatory_question_count} câu bắt buộc phải trả lời đúng</li>}
          <li>Nhấn "Nộp bài" khi hoàn thành</li>
        </ul>
      </motion.div>

      {/* Actions */}
      <motion.div className="qd-actions" initial="hidden" animate="visible" variants={fadeUp} transition={{ duration: 0.4, delay: 0.25 }}>
        <Button variant="primary" size="lg" onClick={() => navigate(`/dashboard/quiz/${quizId}/attempt`)}>
          Bắt đầu làm bài
        </Button>
        {quiz.user_attempts > 0 && (
          <Button variant="outline" size="lg" onClick={() => navigate(`/dashboard/quiz/${quizId}/results`)}>
            Xem kết quả lần trước
          </Button>
        )}
      </motion.div>
    </div>
  )
}

export default QuizDetailPage
