import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import toast from 'react-hot-toast'
import quizService from '@services/quizService'
import { useAuthStore } from '@stores/authStore'
import Button from '@components/ui/Button'
import StateView from '@components/ui/StateView'
import AILoadingState from '@components/ui/AILoadingState'
import Modal, { ModalFooter } from '@components/ui/Modal'
import './QuizPage.css'

const SearchIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
  </svg>
)

/**
 * QuizPage — Danh sách bài quiz
 * Route: /dashboard/quiz
 * API: GET /quizzes via quizService.getQuizzes — unchanged
 */
const QuizPage = () => {
  const navigate = useNavigate()
  const { user } = useAuthStore()
  const isInstructor = user?.role === 'instructor' || user?.role === 'admin'
  const [quizzes, setQuizzes] = useState([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [pagination, setPagination] = useState({ total: 0, skip: 0, limit: 12, has_next: false })
  const [deleteTarget, setDeleteTarget] = useState(null)
  const [deleting, setDeleting] = useState(false)
  const searchRef = useRef(null)

  useEffect(() => {
    const fetchQuizzes = async () => {
      try {
        setLoading(true)
        const params = { skip: pagination.skip, limit: pagination.limit }
        if (searchTerm) params.search = searchTerm
        const data = await quizService.getQuizzes(params)
        setQuizzes(data?.data || [])
        setPagination(prev => ({ ...prev, total: data?.total || 0, has_next: data?.has_next || false }))
      } catch {
        toast.error('Không thể tải danh sách quiz')
      } finally {
        setLoading(false)
      }
    }
    fetchQuizzes()
  }, [pagination.skip, searchTerm])

  const handleSearch = () => setPagination(prev => ({ ...prev, skip: 0 }))

  const confirmDeleteQuiz = async () => {
    if (!deleteTarget) return
    setDeleting(true)
    try {
      await quizService.deleteQuiz(deleteTarget.quiz_id)
      toast.success('Đã xóa quiz')
      setQuizzes((prev) => prev.filter((q) => q.quiz_id !== deleteTarget.quiz_id))
      setDeleteTarget(null)
    } catch (err) {
      toast.error(err?.message || 'Không thể xóa (có thể đã có người làm bài)')
    } finally {
      setDeleting(false)
    }
  }

  const totalPages = Math.ceil(pagination.total / pagination.limit)
  const currentPage = Math.floor(pagination.skip / pagination.limit) + 1

  return (
    <div className="qp-page">
      {/* Hero */}
      <motion.div
        className="qp-hero"
        initial={{ opacity: 0, y: 24 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, ease: [0.65, 0, 0.35, 1] }}
      >
        <svg className="qp-ornament" viewBox="0 0 48 12" fill="none">
          <line x1="0" y1="6" x2="16" y2="6" stroke="var(--gold-500)" strokeWidth="1" />
          <circle cx="24" cy="6" r="4" stroke="var(--gold-500)" strokeWidth="1" />
          <line x1="32" y1="6" x2="48" y2="6" stroke="var(--gold-500)" strokeWidth="1" />
        </svg>
        <h1 className="qp-hero__title">{isInstructor ? 'Quản lý Quiz' : 'Bài Quiz'}</h1>
        <p className="qp-hero__sub">
          {isInstructor
            ? 'Tạo, chỉnh sửa và xem kết quả quiz theo lớp'
            : 'Kiểm tra và củng cố kiến thức với các bài quiz'}
        </p>
        {isInstructor && (
          <div className="qp-hero__actions">
            <Button onClick={() => navigate('/dashboard/courses')}>
              + Tạo quiz từ bài học
            </Button>
            <Button variant="outline" onClick={() => navigate('/dashboard/instructor/analytics')}>
              Analytics
            </Button>
          </div>
        )}
      </motion.div>

      {/* Search */}
      <div className="qp-search">
        <span className="qp-search__icon"><SearchIcon /></span>
        <input
          ref={searchRef}
          type="text"
          className="qp-search__input"
          placeholder="Tìm kiếm quiz theo tên…"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
        />
      </div>

      {/* Loading */}
      {loading && (
        <AILoadingState
          compact
          title="Đang tải ngân hàng quiz"
          message="Hệ thống đang đồng bộ danh sách bài kiểm tra."
          steps={[
            'Đang tải danh sách quiz...',
            'Đang sắp xếp theo bộ lọc...',
            'Sẵn sàng hiển thị...',
          ]}
        />
      )}

      {/* Grid */}
      {!loading && quizzes.length > 0 && (
        <motion.div
          className="qp-grid"
          initial="hidden"
          animate="visible"
          variants={{ visible: { transition: { staggerChildren: 0.07 } } }}
        >
          {quizzes.map((quiz) => (
            <motion.div
              key={quiz.quiz_id}
              className="qp-card"
              variants={{ hidden: { opacity: 0, y: 20 }, visible: { opacity: 1, y: 0, transition: { duration: 0.4, ease: [0.65, 0, 0.35, 1] } } }}
              whileHover={{ y: -3 }}
              onClick={() => {
                if (isInstructor) {
                  navigate(`/dashboard/instructor/quizzes/${quiz.quiz_id}/results`)
                } else {
                  navigate(`/dashboard/quiz/${quiz.quiz_id}`)
                }
              }}
            >
              <div className="qp-card__top">
                <h3 className="qp-card__title">{quiz.title}</h3>
                <span className={`qp-card__status qp-card__status--${quiz.status || 'active'}`}>
                  {quiz.status === 'draft' ? 'Nháp' : 'Hoạt động'}
                </span>
              </div>

              {(quiz.course_title || quiz.lesson_title || quiz.class_name) && (
                <div className="qp-card__tags">
                  {quiz.course_title && <span className="qp-tag">{quiz.course_title}</span>}
                  {quiz.lesson_title && <span className="qp-tag qp-tag--muted">{quiz.lesson_title}</span>}
                  {quiz.class_name && <span className="qp-tag qp-tag--muted">Lớp: {quiz.class_name}</span>}
                </div>
              )}

              {quiz.description && (
                <p className="qp-card__desc">
                  {quiz.description.length > 80 ? quiz.description.substring(0, 80) + '…' : quiz.description}
                </p>
              )}

              {/* Stats */}
              <div className="qp-card__stats">
                <div className="qp-stat">
                  <span className="qp-stat__value">{quiz.question_count || 0}</span>
                  <span className="qp-stat__label">câu</span>
                </div>
                <span className="qp-stat__sep">·</span>
                <div className="qp-stat">
                  <span className="qp-stat__value">{quiz.time_limit || '—'}</span>
                  <span className="qp-stat__label">phút</span>
                </div>
                <span className="qp-stat__sep">·</span>
                <div className="qp-stat">
                  <span className="qp-stat__value">{quiz.pass_threshold || 70}%</span>
                  <span className="qp-stat__label">đạt</span>
                </div>
              </div>

              {quiz.total_students != null && (
                <div className="qp-card__meta">
                  <span>{quiz.completed_count || 0}/{quiz.total_students} đã làm</span>
                  {quiz.pass_rate != null && <span>Đạt: {Math.round(quiz.pass_rate)}%</span>}
                </div>
              )}

              {isInstructor && (
                <div className="qp-card__actions" onClick={(e) => e.stopPropagation()}>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => navigate(`/dashboard/instructor/quizzes/${quiz.quiz_id}/results`)}
                  >
                    Kết quả lớp
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => setDeleteTarget(quiz)}
                  >
                    Xóa
                  </Button>
                </div>
              )}
            </motion.div>
          ))}
        </motion.div>
      )}

      {/* Empty */}
      {!loading && quizzes.length === 0 && (
        <StateView
          type="empty"
          message={
            searchTerm
              ? `Không tìm thấy quiz cho "${searchTerm}"`
              : isInstructor
                ? 'Chưa có quiz. Vào khóa học → bài học → «Tạo quiz» để gắn với lesson.'
                : 'Chưa có bài quiz nào'
          }
          action={
            !searchTerm
              ? {
                  label: isInstructor ? 'Mở khóa học' : 'Khám phá khóa học',
                  onClick: () => navigate('/dashboard/courses'),
                }
              : undefined
          }
        />
      )}

      <Modal
        isOpen={Boolean(deleteTarget)}
        onClose={() => !deleting && setDeleteTarget(null)}
        title="Xóa quiz?"
        size="sm"
      >
        <p className="qp-modal-text">
          Xóa <strong>{deleteTarget?.title}</strong>? Chỉ xóa được khi chưa có học viên làm bài.
        </p>
        <ModalFooter>
          <Button variant="outline" disabled={deleting} onClick={() => setDeleteTarget(null)}>Hủy</Button>
          <Button loading={deleting} onClick={confirmDeleteQuiz}>Xóa quiz</Button>
        </ModalFooter>
      </Modal>

      {/* Pagination */}
      {!loading && pagination.total > pagination.limit && (
        <div className="qp-pagination">
          <Button
            variant="outline" size="sm"
            disabled={pagination.skip <= 0}
            onClick={() => setPagination(prev => ({ ...prev, skip: prev.skip - prev.limit }))}
          >← Trước</Button>
          <span className="qp-pagination__info">{currentPage} / {totalPages}</span>
          <Button
            variant="outline" size="sm"
            disabled={!pagination.has_next}
            onClick={() => setPagination(prev => ({ ...prev, skip: prev.skip + prev.limit }))}
          >Sau →</Button>
        </div>
      )}
    </div>
  )
}

export default QuizPage
