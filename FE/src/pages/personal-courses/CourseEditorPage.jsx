import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { useReducedMotion } from 'framer-motion'
import toast from 'react-hot-toast'
import personalCourseService from '@services/personalCourseService'
import courseService from '@services/courseService'
import Button from '@components/ui/Button'
import StateView from '@components/ui/StateView'
import './CourseEditorPage.css'

/**
 * Trang chỉnh sửa khóa học cá nhân — cinematic 2-pane layout
 * Route: /dashboard/personal-courses/:courseId/edit
 * API: GET /courses/:courseId (courseService.getCourseDetail)
 *      PUT /courses/personal/:courseId (personalCourseService.updateCourse)
 */

const PuzzleIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.5} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round"
      d="M14.25 6.087c0-.355.186-.676.401-.959.221-.29.349-.634.349-1.003
         0-1.036-1.007-1.875-2.25-1.875s-2.25.84-2.25 1.875c0 .369.128.713.349 1.003
         .215.283.401.604.401.959v0a.64.64 0 0 1-.657.643
         48.39 48.39 0 0 1-4.163-.3c.186 1.613.293 3.25.315 4.907a.656.656 0 0 1-.658.663v0c-.355
         0-.676-.186-.959-.401a1.647 1.647 0 0 0-1.003-.349c-1.036 0-1.875 1.007-1.875
         2.25s.84 2.25 1.875 2.25c.369 0 .713-.128 1.003-.349.283-.215.604-.401.959-.401v0c.31
         0 .555.26.532.57a48.039 48.039 0 0 1-.642 5.056c1.518.19 3.058.309 4.616.354a.64.64
         0 0 0 .657-.643v0c0-.355-.186-.676-.401-.959a1.647 1.647 0 0 1-.349-1.003c0-1.035
         1.008-1.875 2.25-1.875 1.243 0 2.25.84 2.25 1.875 0 .369-.128.713-.349 1.003-.215.283
         -.401.604-.401.959v0c0 .31.26.555.57.532a48.074 48.074 0 0 0 5.056-.642
         c.19-1.518.309-3.058.354-4.616a.64.64 0 0 0-.643-.657v0c-.355 0-.676.186-.959.401
         a1.647 1.647 0 0 1-1.003.349c-1.035 0-1.875-1.007-1.875-2.25s.84-2.25 1.875-2.25
         c.369 0 .713.128 1.003.349.283.215.604.401.959.401v0a.656.656 0 0 0 .658-.663
         48.422 48.422 0 0 0-.37-5.36c-1.886.342-3.81.574-5.766.689a.578.578 0 0 1-.61-.58v0Z" />
  </svg>
)

const GripIcon = () => (
  <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true" className="editor-grip-icon">
    <circle cx="9" cy="7" r="1.5" /><circle cx="15" cy="7" r="1.5" />
    <circle cx="9" cy="12" r="1.5" /><circle cx="15" cy="12" r="1.5" />
    <circle cx="9" cy="17" r="1.5" /><circle cx="15" cy="17" r="1.5" />
  </svg>
)

const ChevronRightIcon = () => (
  <svg viewBox="0 0 20 20" fill="currentColor" className="editor-chevron" aria-hidden="true">
    <path fillRule="evenodd" d="M7.21 14.77a.75.75 0 0 1 .02-1.06L11.168 10 7.23 6.29a.75.75 0 1
      1 1.04-1.08l4.5 4.25a.75.75 0 0 1 0 1.08l-4.5 4.25a.75.75 0 0 1-1.06-.02Z"
      clipRule="evenodd" />
  </svg>
)

const CourseEditorPage = () => {
  const { courseId } = useParams()
  const navigate = useNavigate()
  const prefersReduced = useReducedMotion()
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [expandedModule, setExpandedModule] = useState(null)
  const [course, setCourse] = useState({
    title: '',
    description: '',
    category: '',
    level: 'Beginner',
    modules: []
  })

  useEffect(() => {
    const fetchCourse = async () => {
      try {
        setLoading(true)
        const data = await courseService.getCourseDetail(courseId)
        setCourse({
          title: data.title || '',
          description: data.description || '',
          category: data.category || '',
          level: data.level || 'Beginner',
          modules: data.modules || []
        })
      } catch {
        toast.error('Không thể tải dữ liệu khóa học')
      } finally {
        setLoading(false)
      }
    }
    fetchCourse()
  }, [courseId])

  const handleChange = (e) => {
    const { name, value } = e.target
    setCourse((prev) => ({ ...prev, [name]: value }))
  }

  const handleSave = async (e) => {
    e.preventDefault()
    if (!course.title.trim()) {
      toast.error('Tiêu đề khóa học là bắt buộc')
      return
    }
    try {
      setSaving(true)
      await personalCourseService.updateCourse(courseId, course)
      toast.success('Lưu khóa học thành công')
      navigate('/dashboard/personal-courses')
    } catch {
      toast.error('Lưu thất bại. Vui lòng thử lại')
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return (
      <div className="course-editor-shell">
        <StateView type="loading" title="Đang tải trình chỉnh sửa" />
      </div>
    )
  }

  const pageVariants = prefersReduced
    ? {}
    : { hidden: { opacity: 0, y: 12 }, visible: { opacity: 1, y: 0, transition: { duration: 0.35, ease: [0.65, 0, 0.35, 1] } } }

  const moduleVariants = {
    hidden: { height: 0, opacity: 0 },
    visible: { height: 'auto', opacity: 1, transition: { duration: 0.28, ease: [0.65, 0, 0.35, 1] } },
    exit: { height: 0, opacity: 0, transition: { duration: 0.2 } },
  }

  return (
    <motion.div
      className="course-editor-shell"
      initial={prefersReduced ? false : 'hidden'}
      animate="visible"
      variants={pageVariants}
    >
      {/* Sticky top bar */}
      <div className="course-editor-bar">
        <div className="course-editor-bar__left">
          <div className="course-editor-bar__ornament" aria-hidden="true">
            <svg viewBox="0 0 120 14" fill="none">
              <path d="M2 7H48" stroke="currentColor" strokeWidth="1.5" />
              <circle cx="60" cy="7" r="4.5" stroke="currentColor" strokeWidth="1.5" />
              <path d="M72 7H118" stroke="currentColor" strokeWidth="1.5" />
            </svg>
          </div>
          <h1 className="course-editor-bar__title">Chỉnh sửa khóa học</h1>
        </div>
        <div className="course-editor-bar__actions">
          <Button variant="outline" onClick={() => navigate('/dashboard/personal-courses')} disabled={saving}>
            Hủy
          </Button>
          <Button variant="primary" onClick={handleSave} loading={saving} disabled={saving}>
            {saving ? 'Đang lưu...' : 'Lưu thay đổi'}
          </Button>
        </div>
      </div>

      {/* 2-pane body */}
      <div className="course-editor-body">

        {/* LEFT PANE — metadata form */}
        <section className="course-editor-form-pane">
          <form onSubmit={handleSave} className="course-editor-form">
            <div className="course-editor-section-label">Thông tin chung</div>

            <div className="course-editor-field">
              <label htmlFor="title" className="course-editor-field__label">Tiêu đề khóa học</label>
              <input
                id="title"
                name="title"
                className="course-editor-field__input"
                value={course.title}
                onChange={handleChange}
                placeholder="Nhập tiêu đề khóa học..."
                required
                autoComplete="off"
              />
            </div>

            <div className="course-editor-field">
              <label htmlFor="category" className="course-editor-field__label">Danh mục</label>
              <select
                id="category"
                name="category"
                className="course-editor-field__select"
                value={course.category}
                onChange={handleChange}
              >
                <option value="">Chọn danh mục</option>
                <option value="Programming">Lập trình</option>
                <option value="Data Science">Khoa học dữ liệu</option>
                <option value="Math">Toán học</option>
                <option value="Business">Kinh doanh</option>
                <option value="Languages">Ngôn ngữ</option>
              </select>
            </div>

            <div className="course-editor-field">
              <label htmlFor="level" className="course-editor-field__label">Độ khó</label>
              <select
                id="level"
                name="level"
                className="course-editor-field__select"
                value={course.level}
                onChange={handleChange}
              >
                <option value="Beginner">Người mới bắt đầu</option>
                <option value="Intermediate">Trung bình</option>
                <option value="Advanced">Nâng cao</option>
              </select>
            </div>

            <div className="course-editor-field">
              <label htmlFor="description" className="course-editor-field__label">Mô tả</label>
              <textarea
                id="description"
                name="description"
                className="course-editor-field__textarea"
                value={course.description}
                onChange={handleChange}
                placeholder="Mô tả chi tiết về khóa học..."
                rows={6}
              />
            </div>
          </form>
        </section>

        {/* RIGHT PANE — module builder */}
        <section className="course-editor-modules-pane">
          <div className="course-editor-section-label">Cấu trúc khóa học</div>

          {course.modules && course.modules.length > 0 ? (
            <div className="course-editor-module-list">
              {course.modules.map((mod, idx) => (
                <motion.div
                  key={idx}
                  className="course-editor-module"
                  initial={prefersReduced ? false : { opacity: 0, x: 10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: idx * 0.04, duration: 0.25 }}
                >
                  <button
                    type="button"
                    className="course-editor-module__header"
                    onClick={() => setExpandedModule(expandedModule === idx ? null : idx)}
                    aria-expanded={expandedModule === idx}
                  >
                    <span className="course-editor-module__grip">
                      <GripIcon />
                    </span>
                    <span className="course-editor-module__order">{String(idx + 1).padStart(2, '0')}</span>
                    <span className="course-editor-module__title">{mod.title || `Module ${idx + 1}`}</span>
                    <span className={`course-editor-module__chevron ${expandedModule === idx ? 'expanded' : ''}`}>
                      <ChevronRightIcon />
                    </span>
                  </button>

                  <AnimatePresence>
                    {expandedModule === idx && (
                      <motion.div
                        className="course-editor-module__body"
                        variants={moduleVariants}
                        initial="hidden"
                        animate="visible"
                        exit="exit"
                        style={{ overflow: 'hidden' }}
                      >
                        {(mod.lessons || []).length > 0 ? (
                          <ul className="course-editor-lesson-list">
                            {mod.lessons.map((lesson, lIdx) => (
                              <li key={lIdx} className="course-editor-lesson">
                                <span className="course-editor-lesson__dot" />
                                <span className="course-editor-lesson__title">
                                  {lesson.title || `Bài ${lIdx + 1}`}
                                </span>
                              </li>
                            ))}
                          </ul>
                        ) : (
                          <p className="course-editor-module__empty">Chưa có bài học</p>
                        )}
                      </motion.div>
                    )}
                  </AnimatePresence>
                </motion.div>
              ))}
            </div>
          ) : (
            <div className="course-editor-builder-empty">
              <span className="course-editor-builder-empty__icon">
                <PuzzleIcon />
              </span>
              <p className="course-editor-builder-empty__text">
                Khóa học này chưa có module nào.
              </p>
              <p className="course-editor-builder-empty__sub">
                Sau khi AI tạo xong, nội dung sẽ xuất hiện tại đây.
              </p>
            </div>
          )}
        </section>
      </div>
    </motion.div>
  )
}

export default CourseEditorPage
