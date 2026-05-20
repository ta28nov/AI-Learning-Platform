import { useState, useEffect, useMemo } from 'react'
import { useNavigate, useSearchParams, Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import toast from 'react-hot-toast'
import quizService from '@services/quizService'
import learningService from '@services/learningService'
import Button from '@components/ui/Button'
import Input from '@components/ui/Input'
import StateView from '@components/ui/StateView'
import AILoadingState from '@components/ui/AILoadingState'
import Modal, { ModalFooter } from '@components/ui/Modal'
import './InstructorQuizFormPage.css'

const QUESTION_TYPES = [
  { value: 'multiple_choice', label: 'Trắc nghiệm' },
  { value: 'true_false', label: 'Đúng / Sai' },
  { value: 'fill_in_blank', label: 'Điền đáp án' },
]

const emptyQuestion = (order) => ({
  type: 'multiple_choice',
  question_text: '',
  options: ['', '', '', ''],
  correct_answer: '',
  points: 10,
  is_mandatory: false,
  order,
})

const normalizeOptions = (type, options) => {
  if (type === 'true_false') return ['Đúng', 'Sai']
  if (type === 'fill_in_blank') return null
  return (options || []).map((o) => o.trim()).filter(Boolean)
}

/**
 * InstructorQuizFormPage — Tạo quiz gắn với bài học
 * Route: /dashboard/instructor/quizzes/create?lessonId=&courseId=
 */
const InstructorQuizFormPage = () => {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const lessonId = searchParams.get('lessonId') || ''
  const courseId = searchParams.get('courseId') || ''

  const [lessonCtx, setLessonCtx] = useState(null)
  const [lessonLoading, setLessonLoading] = useState(Boolean(courseId && lessonId))
  const [lessonError, setLessonError] = useState('')
  const [saving, setSaving] = useState(false)
  const [cancelOpen, setCancelOpen] = useState(false)
  const [form, setForm] = useState({
    title: '',
    description: '',
    time_limit: 30,
    pass_threshold: 70,
    max_attempts: 3,
    is_draft: false,
  })
  const [questions, setQuestions] = useState([emptyQuestion(1)])
  const [fieldErrors, setFieldErrors] = useState({})

  useEffect(() => {
    if (!courseId || !lessonId) {
      setLessonLoading(false)
      return
    }
    const load = async () => {
      try {
        setLessonLoading(true)
        setLessonError('')
        const data = await learningService.getLessonContent(courseId, lessonId)
        setLessonCtx(data)
        if (!form.title.trim() && data?.title) {
          setForm((f) => ({ ...f, title: `Quiz: ${data.title}` }))
        }
      } catch {
        setLessonError('Không tải được thông tin bài học. Kiểm tra quyền truy cập hoặc thử lại.')
      } finally {
        setLessonLoading(false)
      }
    }
    load()
  }, [courseId, lessonId])

  const totalPoints = useMemo(
    () => questions.reduce((sum, q) => sum + (Number(q.points) || 0), 0),
    [questions]
  )

  const updateQuestion = (index, patch) => {
    setQuestions((prev) =>
      prev.map((q, i) => {
        if (i !== index) return q
        const next = { ...q, ...patch }
        if (patch.type === 'true_false') {
          next.options = ['Đúng', 'Sai']
          if (!next.correct_answer) next.correct_answer = 'Đúng'
        }
        if (patch.type === 'fill_in_blank') {
          next.options = []
        }
        if (patch.type === 'multiple_choice' && (!next.options || next.options.length < 2)) {
          next.options = ['', '', '', '']
        }
        return next
      })
    )
  }

  const addQuestion = () => {
    if (questions.length >= 50) {
      toast.error('Tối đa 50 câu hỏi mỗi quiz')
      return
    }
    setQuestions((prev) => [...prev, emptyQuestion(prev.length + 1)])
  }

  const removeQuestion = (index) => {
    if (questions.length <= 1) {
      toast.error('Quiz cần ít nhất 1 câu hỏi')
      return
    }
    setQuestions((prev) =>
      prev.filter((_, i) => i !== index).map((q, i) => ({ ...q, order: i + 1 }))
    )
  }

  const validate = () => {
    const errs = {}
    if (!form.title.trim()) errs.title = 'Nhập tiêu đề quiz'
    const tl = Number(form.time_limit)
    if (!tl || tl < 1 || tl > 180) errs.time_limit = 'Thời gian từ 1–180 phút'
    const pt = Number(form.pass_threshold)
    if (pt < 0 || pt > 100) errs.pass_threshold = 'Điểm đạt từ 0–100%'

    const qErrs = questions.map((q) => {
      const e = {}
      if (!q.question_text.trim()) e.text = 'Nhập nội dung câu hỏi'
      const opts = normalizeOptions(q.type, q.options)
      if (q.type === 'multiple_choice' && (!opts || opts.length < 2)) {
        e.options = 'Cần ít nhất 2 lựa chọn'
      }
      if (!q.correct_answer?.trim()) e.answer = 'Chọn hoặc nhập đáp án đúng'
      if (q.type === 'multiple_choice' && opts && !opts.includes(q.correct_answer.trim())) {
        e.answer = 'Đáp án đúng phải trùng một lựa chọn'
      }
      return e
    })
    setFieldErrors({ ...errs, questions: qErrs })
    const hasQ = qErrs.some((e) => Object.keys(e).length > 0)
    return Object.keys(errs).length === 0 && !hasQ
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!lessonId) {
      toast.error('Mở trang từ bài học để gắn quiz với lesson')
      return
    }
    if (!validate()) {
      toast.error('Kiểm tra lại các trường được đánh dấu')
      return
    }

    const prepared = questions.map((q, i) => ({
      type: q.type,
      question_text: q.question_text.trim(),
      options: normalizeOptions(q.type, q.options),
      correct_answer: q.correct_answer.trim(),
      points: Number(q.points) || 10,
      is_mandatory: Boolean(q.is_mandatory),
      order: i + 1,
    }))

    setSaving(true)
    try {
      const res = await quizService.createQuiz(lessonId, {
        title: form.title.trim(),
        description: form.description.trim(),
        time_limit: Number(form.time_limit),
        pass_threshold: Number(form.pass_threshold),
        max_attempts: Number(form.max_attempts) || undefined,
        is_draft: form.is_draft,
        questions: prepared,
      })
      toast.success(res?.message || 'Đã tạo quiz thành công')
      navigate(`/dashboard/instructor/quizzes/${res.quiz_id}/results`, { replace: true })
    } catch (error) {
      toast.error(error?.message || 'Không thể tạo quiz')
    } finally {
      setSaving(false)
    }
  }

  if (!lessonId) {
    return (
      <motion.div className="iqf-page" initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}>
        <PageHeader onBack={() => navigate('/dashboard/instructor/quizzes')} title="Tạo quiz mới" />
        <StateView
          type="empty"
          title="Chưa chọn bài học"
          message="Quiz phải gắn với một bài học cụ thể. Mở khóa học → chọn module → vào bài học, rồi bấm «Tạo quiz»."
          action={{
            label: 'Đến khóa học',
            onClick: () => navigate('/dashboard/courses'),
          }}
        />
        <div className="iqf-empty-actions">
          <Button variant="outline" onClick={() => navigate('/dashboard/instructor/quizzes')}>
            Quay lại danh sách quiz
          </Button>
        </div>
      </motion.div>
    )
  }

  if (lessonLoading) {
    return (
      <motion.div className="iqf-page">
        <AILoadingState
          title="Đang tải bài học"
          message="Chuẩn bị form tạo quiz…"
          steps={['Đang lấy tiêu đề bài học…', 'Đang kiểm tra quyền giảng viên…', 'Sẵn sàng soạn câu hỏi…']}
        />
      </motion.div>
    )
  }

  if (lessonError) {
    return (
      <motion.div className="iqf-page">
        <PageHeader onBack={() => navigate(-1)} title="Tạo quiz mới" />
        <StateView
          type="error"
          title="Không tải được bài học"
          message={lessonError}
          action={{ label: 'Thử lại', onClick: () => window.location.reload() }}
        />
      </motion.div>
    )
  }

  return (
    <motion.div className="iqf-page" initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}>
      <PageHeader onBack={() => navigate(-1)} title="Tạo quiz mới" />

      {lessonCtx && (
        <div className="iqf-context">
          <span className="iqf-context__eyebrow">Gắn với bài học</span>
          <p className="iqf-context__lesson">{lessonCtx.title}</p>
          {lessonCtx.module_title && (
            <p className="iqf-context__meta">
              {lessonCtx.module_title}
              {courseId && (
                <>
                  {' · '}
                  <Link to={`/dashboard/courses/${courseId}/lessons/${lessonId}`} className="iqf-context__link">
                    Xem bài học
                  </Link>
                </>
              )}
            </p>
          )}
        </div>
      )}

      <form className="iqf-form" onSubmit={handleSubmit} noValidate>
        <section className="iqf-section-block">
          <h2 className="iqf-section-title">Thông tin chung</h2>
          <Input
            label="Tiêu đề quiz"
            value={form.title}
            error={fieldErrors.title}
            onChange={(e) => setForm((f) => ({ ...f, title: e.target.value }))}
            placeholder="VD: Kiểm tra cuối chương 1"
          />
          <label className="iqf-label">
            Mô tả <span className="iqf-optional">(tùy chọn)</span>
            <textarea
              className="iqf-textarea"
              rows={3}
              value={form.description}
              onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))}
              placeholder="Hướng dẫn ngắn cho học viên trước khi làm bài…"
            />
          </label>
          <div className="iqf-row">
            <Input
              type="number"
              min={1}
              max={180}
              label="Thời gian (phút)"
              value={form.time_limit}
              error={fieldErrors.time_limit}
              onChange={(e) => setForm((f) => ({ ...f, time_limit: e.target.value }))}
            />
            <Input
              type="number"
              min={0}
              max={100}
              label="Điểm đạt (%)"
              value={form.pass_threshold}
              error={fieldErrors.pass_threshold}
              onChange={(e) => setForm((f) => ({ ...f, pass_threshold: e.target.value }))}
            />
            <Input
              type="number"
              min={1}
              label="Số lần làm tối đa"
              value={form.max_attempts}
              onChange={(e) => setForm((f) => ({ ...f, max_attempts: e.target.value }))}
            />
          </div>
          <label className="iqf-check">
            <input
              type="checkbox"
              checked={form.is_draft}
              onChange={(e) => setForm((f) => ({ ...f, is_draft: e.target.checked }))}
            />
            Lưu dạng nháp (học viên chưa thấy)
          </label>
        </section>

        <section className="iqf-section-block">
          <div className="iqf-section-head">
            <h2 className="iqf-section-title">Câu hỏi ({questions.length})</h2>
            <span className="iqf-points-badge">Tổng {totalPoints} điểm</span>
          </div>

          {questions.map((q, index) => (
            <div key={index} className="iqf-question">
              <div className="iqf-question__head">
                <span className="iqf-question__num">Câu {index + 1}</span>
                <div className="iqf-question__head-actions">
                  <select
                    className="iqf-select iqf-select--sm"
                    value={q.type}
                    onChange={(e) => updateQuestion(index, { type: e.target.value })}
                    aria-label="Loại câu hỏi"
                  >
                    {QUESTION_TYPES.map((t) => (
                      <option key={t.value} value={t.value}>{t.label}</option>
                    ))}
                  </select>
                  <button
                    type="button"
                    className="iqf-link-btn"
                    onClick={() => removeQuestion(index)}
                    disabled={questions.length <= 1}
                  >
                    Xóa câu
                  </button>
                </div>
              </div>

              <Input
                label="Nội dung câu hỏi"
                value={q.question_text}
                error={fieldErrors.questions?.[index]?.text}
                onChange={(e) => updateQuestion(index, { question_text: e.target.value })}
              />

              {q.type === 'multiple_choice' && (
                <div className="iqf-options">
                  <span className="iqf-label">Các lựa chọn</span>
                  {(q.options || []).map((opt, oi) => (
                    <Input
                      key={oi}
                      placeholder={`Lựa chọn ${oi + 1}`}
                      value={opt}
                      onChange={(e) => {
                        const next = [...(q.options || [])]
                        next[oi] = e.target.value
                        updateQuestion(index, { options: next })
                      }}
                    />
                  ))}
                  {fieldErrors.questions?.[index]?.options && (
                    <span className="iqf-field-error">{fieldErrors.questions[index].options}</span>
                  )}
                </div>
              )}

              {q.type === 'multiple_choice' && normalizeOptions(q.type, q.options)?.length > 0 ? (
                <label className="iqf-label">
                  Đáp án đúng
                  <select
                    className="iqf-select"
                    value={q.correct_answer}
                    onChange={(e) => updateQuestion(index, { correct_answer: e.target.value })}
                  >
                    <option value="">— Chọn đáp án —</option>
                    {normalizeOptions(q.type, q.options).map((opt) => (
                      <option key={opt} value={opt}>{opt}</option>
                    ))}
                  </select>
                  {fieldErrors.questions?.[index]?.answer && (
                    <span className="iqf-field-error">{fieldErrors.questions[index].answer}</span>
                  )}
                </label>
              ) : q.type === 'true_false' ? (
                <label className="iqf-label">
                  Đáp án đúng
                  <select
                    className="iqf-select"
                    value={q.correct_answer || 'Đúng'}
                    onChange={(e) => updateQuestion(index, { correct_answer: e.target.value })}
                    aria-label="Đáp án đúng/sai"
                  >
                    <option value="Đúng">Đúng</option>
                    <option value="Sai">Sai</option>
                  </select>
                  {fieldErrors.questions?.[index]?.answer && (
                    <span className="iqf-field-error">{fieldErrors.questions[index].answer}</span>
                  )}
                </label>
              ) : (
                <Input
                  label="Đáp án đúng"
                  value={q.correct_answer}
                  error={fieldErrors.questions?.[index]?.answer}
                  onChange={(e) => updateQuestion(index, { correct_answer: e.target.value })}
                  placeholder="Nhập đáp án chính xác"
                />
              )}

              <div className="iqf-question__footer">
                <Input
                  type="number"
                  min={1}
                  label="Điểm"
                  className="iqf-points-input"
                  value={q.points}
                  onChange={(e) => updateQuestion(index, { points: e.target.value })}
                />
                <label className="iqf-check">
                  <input
                    type="checkbox"
                    checked={q.is_mandatory}
                    onChange={(e) => updateQuestion(index, { is_mandatory: e.target.checked })}
                  />
                  Câu bắt buộc (phải đúng mới đạt)
                </label>
              </div>
            </div>
          ))}

          <Button type="button" variant="outline" className="iqf-add-btn" onClick={addQuestion}>
            + Thêm câu hỏi
          </Button>
        </section>

        <div className="iqf-summary">
          <p>{questions.length} câu · {totalPoints} điểm · Đạt từ {form.pass_threshold}% · {form.time_limit} phút</p>
        </div>

        <div className="iqf-actions">
          <Button type="button" variant="outline" onClick={() => setCancelOpen(true)}>
            Hủy
          </Button>
          <Button type="submit" loading={saving}>
            {form.is_draft ? 'Lưu nháp' : 'Tạo và xuất bản quiz'}
          </Button>
        </div>
      </form>

      <Modal isOpen={cancelOpen} onClose={() => setCancelOpen(false)} title="Hủy tạo quiz?" size="sm">
        <p className="iqf-modal-text">Nội dung chưa lưu sẽ bị mất.</p>
        <ModalFooter>
          <Button variant="outline" onClick={() => setCancelOpen(false)}>Tiếp tục soạn</Button>
          <Button onClick={() => navigate('/dashboard/instructor/quizzes')}>Rời trang</Button>
        </ModalFooter>
      </Modal>
    </motion.div>
  )
}

function PageHeader({ onBack, title }) {
  return (
    <header className="iqf-header">
      <button type="button" className="iqf-back" onClick={onBack}>
        <svg viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.5" aria-hidden>
          <path d="M15 10H5m0 0 5-5M5 10l5 5" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
        Quay lại
      </button>
      <svg className="iqf-ornament" viewBox="0 0 48 12" fill="none" aria-hidden>
        <line x1="0" y1="6" x2="16" y2="6" stroke="var(--gold-500)" strokeWidth="1" />
        <circle cx="24" cy="6" r="4" stroke="var(--gold-500)" strokeWidth="1" />
        <line x1="32" y1="6" x2="48" y2="6" stroke="var(--gold-500)" strokeWidth="1" />
      </svg>
      <h1 className="iqf-title">{title}</h1>
    </header>
  )
}

export default InstructorQuizFormPage
