import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { useReducedMotion } from 'framer-motion'
import toast from 'react-hot-toast'
import personalCourseService from '@services/personalCourseService'
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

const CourseEditorPage = () => {
  const { courseId } = useParams()
  const navigate = useNavigate()
  const prefersReduced = useReducedMotion()
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [savingAndLearn, setSavingAndLearn] = useState(false)
  const [course, setCourse] = useState({
    title: '',
    description: '',
    category: '',
    level: 'Beginner',
    status: 'draft',
    learning_outcomes_text: '',
    prerequisites_text: '',
    modules: [],
  })

  useEffect(() => {
    const fetchCourse = async () => {
      try {
        setLoading(true)
        const data = await personalCourseService.getPersonalCourseDetail(courseId)
        const modules = (data.modules || []).map((m, mIdx) => ({
          id: m.id,
          title: m.title || `Module ${mIdx + 1}`,
          description: m.description || '',
          order: m.order || mIdx + 1,
          difficulty: m.difficulty || 'Basic',
          estimated_hours: m.estimated_hours || 0,
          learning_outcomes: m.learning_outcomes || [],
          lessons: (m.lessons || []).map((l, lIdx) => ({
            id: l.id,
            title: l.title || `Bài ${lIdx + 1}`,
            description: l.description || '',
            order: l.order || lIdx + 1,
            content: l.content || '',
            content_type: l.content_type || 'text',
            duration_minutes: l.duration_minutes || 0,
            video_url: l.video_url || '',
          })),
        }))

        setCourse({
          title: data.title || '',
          description: data.description || '',
          category: data.category || '',
          level: data.level || 'Beginner',
          status: data.status || 'draft',
          learning_outcomes_text: (data.learning_outcomes || []).join('\n'),
          prerequisites_text: (data.prerequisites || []).join('\n'),
          modules,
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

  const updateModuleField = (moduleIdx, field, value) => {
    setCourse((prev) => {
      const modules = [...prev.modules]
      modules[moduleIdx] = { ...modules[moduleIdx], [field]: value }
      return { ...prev, modules }
    })
  }

  const updateLessonField = (moduleIdx, lessonIdx, field, value) => {
    setCourse((prev) => {
      const modules = [...prev.modules]
      const lessons = [...(modules[moduleIdx].lessons || [])]
      lessons[lessonIdx] = { ...lessons[lessonIdx], [field]: value }
      modules[moduleIdx] = { ...modules[moduleIdx], lessons }
      return { ...prev, modules }
    })
  }

  const addModule = () => {
    setCourse((prev) => ({
      ...prev,
      modules: [
        ...prev.modules,
        {
          id: undefined,
          title: `Module ${prev.modules.length + 1}`,
          description: '',
          order: prev.modules.length + 1,
          difficulty: 'Basic',
          estimated_hours: 1,
          learning_outcomes: [],
          lessons: [],
        },
      ],
    }))
  }

  const removeModule = (moduleIdx) => {
    setCourse((prev) => {
      const modules = prev.modules.filter((_, i) => i !== moduleIdx)
      return {
        ...prev,
        modules: modules.map((m, idx) => ({ ...m, order: idx + 1 })),
      }
    })
  }

  const addLesson = (moduleIdx) => {
    setCourse((prev) => {
      const modules = [...prev.modules]
      const lessons = [...(modules[moduleIdx].lessons || [])]
      lessons.push({
        id: undefined,
        title: `Bài ${lessons.length + 1}`,
        description: '',
        order: lessons.length + 1,
        content: '',
        content_type: 'text',
        duration_minutes: 10,
        video_url: '',
      })
      modules[moduleIdx] = { ...modules[moduleIdx], lessons }
      return { ...prev, modules }
    })
  }

  const removeLesson = (moduleIdx, lessonIdx) => {
    setCourse((prev) => {
      const modules = [...prev.modules]
      const lessons = (modules[moduleIdx].lessons || [])
        .filter((_, i) => i !== lessonIdx)
        .map((l, idx) => ({ ...l, order: idx + 1 }))
      modules[moduleIdx] = { ...modules[moduleIdx], lessons }
      return { ...prev, modules }
    })
  }

  const buildPayload = (nextStatus) => {
    const modules = course.modules.map((m, mIdx) => ({
      id: m.id,
      title: (m.title || '').trim() || `Module ${mIdx + 1}`,
      description: (m.description || '').trim(),
      order: mIdx + 1,
      difficulty: m.difficulty || 'Basic',
      estimated_hours: Number(m.estimated_hours || 0),
      learning_outcomes: m.learning_outcomes || [],
      lessons: (m.lessons || []).map((l, lIdx) => ({
        id: l.id,
        title: (l.title || '').trim() || `Bài ${lIdx + 1}`,
        order: lIdx + 1,
        description: (l.description || '').trim(),
        content: l.content || '',
        content_type: l.content_type || 'text',
        video_url: l.video_url || null,
        duration_minutes: Number(l.duration_minutes || 0),
        resources: [],
      })),
    }))

    return {
      title: course.title.trim(),
      description: course.description.trim(),
      category: course.category,
      level: course.level,
      status: nextStatus || course.status || 'draft',
      learning_outcomes: course.learning_outcomes_text
        .split('\n')
        .map((x) => x.trim())
        .filter(Boolean),
      prerequisites: course.prerequisites_text
        .split('\n')
        .map((x) => x.trim())
        .filter(Boolean),
      modules,
    }
  }

  const handleSave = async (e, { publishAndLearn = false } = {}) => {
    if (e) e.preventDefault()
    if (!course.title.trim()) {
      toast.error('Tiêu đề khóa học là bắt buộc')
      return
    }
    if (course.modules.length === 0) {
      toast.error('Hãy thêm ít nhất 1 module')
      return
    }
    if (course.modules.some((m) => (m.lessons || []).length === 0)) {
      toast.error('Mỗi module cần có ít nhất 1 bài học')
      return
    }

    try {
      setSaving(!publishAndLearn)
      setSavingAndLearn(publishAndLearn)
      const nextStatus = publishAndLearn ? 'published' : course.status || 'draft'
      const payload = buildPayload(nextStatus)
      await personalCourseService.updateCourse(courseId, payload)
      toast.success(publishAndLearn ? 'Đã xuất bản và mở khóa học' : 'Lưu khóa học thành công')
      if (publishAndLearn) {
        navigate(`/dashboard/courses/${courseId}/modules`)
      } else {
        navigate('/dashboard/personal-courses')
      }
    } catch {
      toast.error('Lưu thất bại. Vui lòng thử lại')
    } finally {
      setSaving(false)
      setSavingAndLearn(false)
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
          <Button variant="outline" onClick={() => navigate('/dashboard/personal-courses')} disabled={saving || savingAndLearn}>
            Hủy
          </Button>
          <Button variant="outline" onClick={(e) => handleSave(e, { publishAndLearn: false })} loading={saving} disabled={saving || savingAndLearn}>
            {saving ? 'Đang lưu...' : 'Lưu nháp'}
          </Button>
          <Button variant="primary" onClick={(e) => handleSave(e, { publishAndLearn: true })} loading={savingAndLearn} disabled={saving || savingAndLearn}>
            {savingAndLearn ? 'Đang xuất bản...' : 'Xuất bản & vào học'}
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
            <div className="course-editor-field">
              <label htmlFor="learning_outcomes_text" className="course-editor-field__label">Kết quả đầu ra (mỗi dòng 1 ý)</label>
              <textarea
                id="learning_outcomes_text"
                name="learning_outcomes_text"
                className="course-editor-field__textarea"
                value={course.learning_outcomes_text}
                onChange={handleChange}
                rows={4}
                placeholder="Ví dụ: Viết được API CRUD cơ bản"
              />
            </div>
            <div className="course-editor-field">
              <label htmlFor="prerequisites_text" className="course-editor-field__label">Yêu cầu đầu vào (mỗi dòng 1 ý)</label>
              <textarea
                id="prerequisites_text"
                name="prerequisites_text"
                className="course-editor-field__textarea"
                value={course.prerequisites_text}
                onChange={handleChange}
                rows={3}
                placeholder="Ví dụ: Biết cú pháp JavaScript cơ bản"
              />
            </div>
          </form>
        </section>

        {/* RIGHT PANE — module builder */}
        <section className="course-editor-modules-pane">
          <div className="course-editor-section-label">Cấu trúc khóa học</div>

          <div className="course-editor-module-actions">
            <Button size="sm" onClick={addModule}>+ Thêm module</Button>
          </div>
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
                  <div className="course-editor-module__body course-editor-module__body--always-open">
                    <div className="course-editor-module-row">
                      <label className="course-editor-field course-editor-field--compact">
                        <span className="course-editor-field__label">Tên module</span>
                        <input
                          className="course-editor-field__input"
                          value={mod.title || ''}
                          onChange={(e) => updateModuleField(idx, 'title', e.target.value)}
                        />
                      </label>
                      <label className="course-editor-field course-editor-field--compact">
                        <span className="course-editor-field__label">Độ khó</span>
                        <select
                          className="course-editor-field__select"
                          value={mod.difficulty || 'Basic'}
                          onChange={(e) => updateModuleField(idx, 'difficulty', e.target.value)}
                        >
                          <option value="Basic">Basic</option>
                          <option value="Intermediate">Intermediate</option>
                          <option value="Advanced">Advanced</option>
                        </select>
                      </label>
                    </div>
                    <label className="course-editor-field course-editor-field--compact">
                      <span className="course-editor-field__label">Mô tả module</span>
                      <textarea
                        className="course-editor-field__textarea"
                        rows={2}
                        value={mod.description || ''}
                        onChange={(e) => updateModuleField(idx, 'description', e.target.value)}
                      />
                    </label>
                    <div className="course-editor-module-toolbar">
                      <Button size="sm" variant="outline" onClick={() => addLesson(idx)}>+ Thêm bài học</Button>
                      <Button size="sm" variant="danger" onClick={() => removeModule(idx)}>Xóa module</Button>
                    </div>
                    {(mod.lessons || []).length > 0 ? (
                      <ul className="course-editor-lesson-list">
                        {mod.lessons.map((lesson, lIdx) => (
                          <li key={lesson.id || lIdx} className="course-editor-lesson course-editor-lesson--editor">
                            <div className="course-editor-lesson-head">
                              <strong>Bài {lIdx + 1}</strong>
                              <Button size="sm" variant="ghost" onClick={() => removeLesson(idx, lIdx)}>Xóa</Button>
                            </div>
                            <input
                              className="course-editor-field__input"
                              placeholder="Tiêu đề bài học"
                              value={lesson.title || ''}
                              onChange={(e) => updateLessonField(idx, lIdx, 'title', e.target.value)}
                            />
                            <textarea
                              className="course-editor-field__textarea"
                              rows={3}
                              placeholder="Nội dung bài học"
                              value={lesson.content || ''}
                              onChange={(e) => updateLessonField(idx, lIdx, 'content', e.target.value)}
                            />
                            <div className="course-editor-module-row">
                              <label className="course-editor-field course-editor-field--compact">
                                <span className="course-editor-field__label">Thời lượng (phút)</span>
                                <input
                                  type="number"
                                  min={0}
                                  className="course-editor-field__input"
                                  value={lesson.duration_minutes || 0}
                                  onChange={(e) => updateLessonField(idx, lIdx, 'duration_minutes', Number(e.target.value || 0))}
                                />
                              </label>
                              <label className="course-editor-field course-editor-field--compact">
                                <span className="course-editor-field__label">Video URL (tuỳ chọn)</span>
                                <input
                                  className="course-editor-field__input"
                                  value={lesson.video_url || ''}
                                  onChange={(e) => updateLessonField(idx, lIdx, 'video_url', e.target.value)}
                                />
                              </label>
                            </div>
                          </li>
                        ))}
                      </ul>
                    ) : (
                      <p className="course-editor-module__empty">Chưa có bài học trong module này</p>
                    )}
                  </div>
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
