import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import toast from 'react-hot-toast'
import quizService from '@services/quizService'
import Button from '@components/ui/Button'
import './QuizDetailPage.css'

/**
 * QuizDetailPage - Trang chi tiết quiz trước khi làm bài
 * Route: /dashboard/quiz/:quizId
 * API: GET /quizzes/{quizId} -> QuizDetailResponse
 * Hiển thị thông tin quiz, lịch sử làm bài, nút bắt đầu/xem kết quả
 */
const QuizDetailPage = () => {
  const { quizId } = useParams()
  const navigate = useNavigate()
  const [quiz, setQuiz] = useState(null)
  const [loading, setLoading] = useState(true)

  // Lấy chi tiết quiz khi mount
  useEffect(() => {
    const fetchQuiz = async () => {
      try {
        setLoading(true)
        const data = await quizService.getQuizDetail(quizId)
        setQuiz(data)
      } catch (error) {
        toast.error('Không thể tải thông tin quiz')
      } finally {
        setLoading(false)
      }
    }
    if (quizId) fetchQuiz()
  }, [quizId])

  const fadeUp = { hidden: { opacity: 0, y: 20 }, visible: { opacity: 1, y: 0 } }

  // Loading skeleton
  if (loading) {
    return (
      <div className="qd-page">
        <div className="qd-skeleton__header" />
        <div className="qd-skeleton__body" />
      </div>
    )
  }

  if (!quiz) {
    return (
      <div className="qd-page">
        <div className="quiz-empty">
          <span className="quiz-empty__icon">📝</span>
          <h3>Không tìm thấy quiz</h3>
          <p>Quiz này không tồn tại hoặc đã bị xóa</p>
          <Button variant="outline" onClick={() => navigate(-1)}>Quay lại</Button>
        </div>
      </div>
    )
  }

  return (
    <div className="qd-page">
      {/* Header */}
      <motion.div
        className="qd-header"
        initial="hidden"
        animate="visible"
        variants={fadeUp}
        transition={{ duration: 0.4 }}
      >
        <button className="qd-back" onClick={() => navigate(-1)}>← Quay lại</button>
        <h1 className="qd-header__title">{quiz.title}</h1>
        {quiz.description && <p className="qd-header__desc">{quiz.description}</p>}
      </motion.div>

      {/* Thông tin quiz */}
      <motion.div
        className="qd-info"
        initial="hidden"
        animate="visible"
        variants={fadeUp}
        transition={{ duration: 0.4, delay: 0.1 }}
      >
        <div className="qd-info__grid">
          <div className="qd-info__card">
            <span className="qd-info__card-label">Số câu hỏi</span>
            <span className="qd-info__card-value">{quiz.question_count || 0}</span>
          </div>
          <div className="qd-info__card">
            <span className="qd-info__card-label">Thời gian</span>
            <span className="qd-info__card-value">{quiz.time_limit || '—'} phút</span>
          </div>
          <div className="qd-info__card">
            <span className="qd-info__card-label">Điểm đạt</span>
            <span className="qd-info__card-value">{quiz.pass_threshold || 70}%</span>
          </div>
          <div className="qd-info__card">
            <span className="qd-info__card-label">Câu bắt buộc</span>
            <span className="qd-info__card-value">{quiz.mandatory_question_count || 0}</span>
          </div>
          {quiz.max_attempts != null && (
            <div className="qd-info__card">
              <span className="qd-info__card-label">Số lần làm tối đa</span>
              <span className="qd-info__card-value">{quiz.max_attempts || '∞'}</span>
            </div>
          )}
          {quiz.is_retakeable != null && (
            <div className="qd-info__card">
              <span className="qd-info__card-label">Làm lại</span>
              <span className="qd-info__card-value">{quiz.is_retakeable ? 'Được phép' : 'Không'}</span>
            </div>
          )}
        </div>
      </motion.div>

      {/* Lịch sử làm bài (nếu có) */}
      {quiz.user_attempts != null && quiz.user_attempts > 0 && (
        <motion.div
          className="qd-history"
          initial="hidden"
          animate="visible"
          variants={fadeUp}
          transition={{ duration: 0.4, delay: 0.15 }}
        >
          <h2 className="qd-section-title">Lịch sử làm bài</h2>
          <div className="qd-history__content">
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
          </div>
        </motion.div>
      )}

      {/* Hướng dẫn */}
      <motion.div
        className="qd-instructions"
        initial="hidden"
        animate="visible"
        variants={fadeUp}
        transition={{ duration: 0.4, delay: 0.2 }}
      >
        <h2 className="qd-section-title">Hướng dẫn</h2>
        <ul className="qd-instructions__list">
          <li>Đọc kỹ câu hỏi trước khi trả lời</li>
          <li>Chọn đáp án đúng nhất cho mỗi câu hỏi</li>
          <li>Có thể quay lại các câu hỏi trước đó</li>
          {quiz.time_limit && <li>Thời gian làm bài: {quiz.time_limit} phút</li>}
          <li>Điểm đạt tối thiểu: {quiz.pass_threshold || 70}%</li>
          {quiz.mandatory_question_count > 0 && (
            <li>Có {quiz.mandatory_question_count} câu hỏi bắt buộc phải trả lời đúng</li>
          )}
          <li>Nhấn "Nộp bài" khi hoàn thành</li>
        </ul>
      </motion.div>

      {/* Nút hành động */}
      <motion.div
        className="qd-actions"
        initial="hidden"
        animate="visible"
        variants={fadeUp}
        transition={{ duration: 0.4, delay: 0.25 }}
      >
        <Button
          variant="primary"
          size="lg"
          onClick={() => navigate(`/dashboard/quiz/${quizId}/attempt`)}
        >
          Bắt đầu làm bài
        </Button>
        {quiz.user_attempts > 0 && (
          <Button
            variant="outline"
            size="lg"
            onClick={() => navigate(`/dashboard/quiz/${quizId}/results`)}
          >
            Xem kết quả lần trước
          </Button>
        )}
      </motion.div>
    </div>
  )
}

export default QuizDetailPage