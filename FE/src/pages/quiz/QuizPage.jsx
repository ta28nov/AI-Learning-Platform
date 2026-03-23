import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import toast from 'react-hot-toast'
import quizService from '@services/quizService'
import Button from '@components/ui/Button'
import './QuizPage.css'

/**
 * QuizPage - Trang danh sách quiz
 * Route: /dashboard/quiz
 * API: GET /quizzes (quizService.getQuizzes)
 * Hiển thị danh sách quiz với filter, search, pagination
 */
const QuizPage = () => {
  const navigate = useNavigate()
  const [quizzes, setQuizzes] = useState([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [pagination, setPagination] = useState({ total: 0, skip: 0, limit: 12, has_next: false })

  // Lấy danh sách quiz
  useEffect(() => {
    const fetchQuizzes = async () => {
      try {
        setLoading(true)
        const params = {
          skip: pagination.skip,
          limit: pagination.limit
        }
        if (searchTerm) params.search = searchTerm
        const data = await quizService.getQuizzes(params)
        setQuizzes(data?.data || [])
        setPagination(prev => ({
          ...prev,
          total: data?.total || 0,
          has_next: data?.has_next || false
        }))
      } catch (error) {
        toast.error('Không thể tải danh sách quiz')
      } finally {
        setLoading(false)
      }
    }
    fetchQuizzes()
  }, [pagination.skip, searchTerm])

  // Xử lý tìm kiếm
  const handleSearch = () => {
    setPagination(prev => ({ ...prev, skip: 0 }))
  }

  const fadeUp = { hidden: { opacity: 0, y: 20 }, visible: { opacity: 1, y: 0 } }

  return (
    <div className="quiz-page">
      <motion.div initial="hidden" animate="visible" variants={fadeUp} transition={{ duration: 0.3 }}>
        <h1 className="quiz-header__title">Bài Quiz</h1>
        <p className="quiz-header__sub">Kiểm tra và củng cố kiến thức với các bài quiz</p>
      </motion.div>

      {/* Thanh tìm kiếm */}
      <div className="quiz-search">
        <input
          type="text"
          className="quiz-search__input"
          placeholder="Tìm kiếm quiz theo tên..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
        />
      </div>

      {/* Đang tải */}
      {loading && (
        <div className="quiz-grid">
          {[1, 2, 3, 4].map(i => <div key={i} className="quiz-skeleton" />)}
        </div>
      )}

      {/* Danh sách quiz */}
      {!loading && quizzes.length > 0 && (
        <motion.div
          className="quiz-grid"
          initial="hidden"
          animate="visible"
          variants={{ visible: { transition: { staggerChildren: 0.06 } } }}
        >
          {quizzes.map((quiz) => (
            <motion.div
              key={quiz.quiz_id}
              className="quiz-card"
              variants={fadeUp}
              onClick={() => navigate(`/dashboard/quiz/${quiz.quiz_id}`)}
            >
              <div className="quiz-card__header">
                <h3 className="quiz-card__title">{quiz.title}</h3>
                <span className={`quiz-card__status quiz-card__status--${quiz.status || 'active'}`}>
                  {quiz.status === 'draft' ? 'Bản nháp' : 'Đang hoạt động'}
                </span>
              </div>

              {/* Thông tin khóa học/bài học liên quan */}
              {quiz.course_title && (
                <span className="quiz-card__course">{quiz.course_title}</span>
              )}
              {quiz.lesson_title && (
                <span className="quiz-card__lesson">{quiz.lesson_title}</span>
              )}
              {quiz.class_name && (
                <span className="quiz-card__class">Lớp: {quiz.class_name}</span>
              )}
              {quiz.description && (
                <p className="quiz-card__desc">
                  {quiz.description.length > 80 ? quiz.description.substring(0, 80) + '...' : quiz.description}
                </p>
              )}

              {/* Thống kê quiz */}
              <div className="quiz-card__stats">
                <div className="quiz-card__stat">
                  <span className="quiz-card__stat-value">{quiz.question_count || 0}</span>
                  <span className="quiz-card__stat-label">câu hỏi</span>
                </div>
                <div className="quiz-card__stat">
                  <span className="quiz-card__stat-value">{quiz.time_limit || '—'}</span>
                  <span className="quiz-card__stat-label">phút</span>
                </div>
                <div className="quiz-card__stat">
                  <span className="quiz-card__stat-value">{quiz.pass_threshold || 70}%</span>
                  <span className="quiz-card__stat-label">điểm đạt</span>
                </div>
              </div>

              {/* Thông tin thêm cho instructor */}
              {quiz.total_students != null && (
                <div className="quiz-card__meta">
                  <span>{quiz.completed_count || 0}/{quiz.total_students} đã làm</span>
                  {quiz.pass_count != null && <span>Đạt: {quiz.pass_count}</span>}
                  {quiz.pass_rate != null && <span>Tỉ lệ đạt: {Math.round(quiz.pass_rate)}%</span>}
                  {quiz.average_score != null && <span>Điểm TB: {Math.round(quiz.average_score)}</span>}
                </div>
              )}

              <div className="quiz-card__footer">
                <Button variant="primary" size="sm">Xem chi tiết</Button>
              </div>
            </motion.div>
          ))}
        </motion.div>
      )}

      {/* Trạng thái rỗng */}
      {!loading && quizzes.length === 0 && (
        <div className="quiz-empty">
          <span className="quiz-empty__icon">📝</span>
          <h3>Chưa có bài quiz nào</h3>
          <p>Các bài quiz sẽ xuất hiện khi bạn đăng ký khóa học</p>
          <Button
            variant="primary"
            onClick={() => navigate('/dashboard/courses')}
          >
            Khám phá khóa học
          </Button>
        </div>
      )}

      {/* Phân trang */}
      {!loading && pagination.total > pagination.limit && (
        <div className="quiz-pagination">
          <Button
            variant="outline"
            size="sm"
            disabled={pagination.skip <= 0}
            onClick={() => setPagination(prev => ({ ...prev, skip: prev.skip - prev.limit }))}
          >
            Trang trước
          </Button>
          <span className="quiz-pagination__info">
            Trang {Math.floor(pagination.skip / pagination.limit) + 1} / {Math.ceil(pagination.total / pagination.limit)}
          </span>
          <Button
            variant="outline"
            size="sm"
            disabled={!pagination.has_next}
            onClick={() => setPagination(prev => ({ ...prev, skip: prev.skip + prev.limit }))}
          >
            Trang sau
          </Button>
        </div>
      )}
    </div>
  )
}

export default QuizPage