import { useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { motion } from 'framer-motion'
import toast from 'react-hot-toast'
import classService from '@services/classService'
import courseService from '@services/courseService'
import Button from '@components/ui/Button'
import './ClassCreatePage.css'

/**
 * ClassCreatePage — Tạo lớp học mới (Instructor)
 * Route: /dashboard/instructor/classes/create (InstructorRoute)
 * API: POST /classes via classService.createClass — unchanged
 */
const ClassCreatePage = () => {
  const navigate = useNavigate()
  const [isLoading, setIsLoading] = useState(false)
  const [loadingCourses, setLoadingCourses] = useState(true)
  const [coursesError, setCoursesError] = useState('')
  const [courses, setCourses] = useState([])
  const [courseKeyword, setCourseKeyword] = useState('')
  const { register, handleSubmit, watch, formState: { errors } } = useForm()

  const selectedCourseId = watch('course_id')

  const visibleCourses = useMemo(() => {
    const kw = courseKeyword.trim().toLowerCase()
    if (!kw) return courses
    return courses.filter((course) =>
      (course.title || '').toLowerCase().includes(kw) ||
      (course.category || '').toLowerCase().includes(kw) ||
      (course.level || '').toLowerCase().includes(kw)
    )
  }, [courses, courseKeyword])

  const loadCourses = async () => {
    try {
      setLoadingCourses(true)
      setCoursesError('')
      const res = await courseService.getPublicCourses({ skip: 0, limit: 50 })
      setCourses(res?.courses || res?.data || [])
    } catch (error) {
      setCoursesError(error.message || 'Không thể tải danh sách khóa học')
    } finally {
      setLoadingCourses(false)
    }
  }

  useEffect(() => {
    loadCourses()
  }, [])

  const onSubmit = async (data) => {
    setIsLoading(true)
    try {
      const response = await classService.createClass(data)
      toast.success(`Tạo lớp thành công! Mã mời: ${response.invite_code}`)
      navigate(`/dashboard/instructor/classes/${response.class_id}`)
    } catch (error) {
      toast.error(error.message || 'Không thể tạo lớp học')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="cc-page">
      {/* Header */}
      <motion.div
        className="cc-header"
        initial={{ opacity: 0, y: 24 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, ease: [0.65, 0, 0.35, 1] }}
      >
        <button className="cc-back" onClick={() => navigate('/dashboard/instructor/classes')}>
          <svg viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.5">
            <path d="M15 10H5m0 0 5-5M5 10l5 5" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
          Danh sách lớp
        </button>
        <svg className="cc-ornament" viewBox="0 0 48 12" fill="none">
          <line x1="0" y1="6" x2="16" y2="6" stroke="var(--gold-500)" strokeWidth="1"/>
          <circle cx="24" cy="6" r="4" stroke="var(--gold-500)" strokeWidth="1"/>
          <line x1="32" y1="6" x2="48" y2="6" stroke="var(--gold-500)" strokeWidth="1"/>
        </svg>
        <h1 className="cc-title">Tạo lớp học mới</h1>
      </motion.div>

      <motion.form
        onSubmit={handleSubmit(onSubmit)}
        className="cc-form"
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1, duration: 0.45 }}
      >
        <div className="cc-field">
          <label className="cc-label">Tên lớp <span className="cc-required">*</span></label>
          <input
            {...register('name', { required: 'Vui lòng nhập tên lớp' })}
            className={`cc-input ${errors.name ? 'cc-input--error' : ''}`}
            placeholder="VD: Lớp Python cơ bản — K1"
          />
          {errors.name && <p className="cc-error">{errors.name.message}</p>}
        </div>

        <div className="cc-field">
          <label className="cc-label">Mô tả</label>
          <textarea
            {...register('description')}
            className="cc-input cc-textarea"
            rows={3}
            placeholder="Mô tả ngắn về lớp học…"
          />
        </div>

        <div className="cc-field">
          <label className="cc-label">Khóa học nền tảng <span className="cc-required">*</span></label>
          <input
            value={courseKeyword}
            onChange={(e) => setCourseKeyword(e.target.value)}
            className="cc-input"
            placeholder="Tìm theo tên, danh mục, trình độ..."
          />
          <select
            {...register('course_id', { required: 'Vui lòng chọn khóa học' })}
            className={`cc-input ${errors.course_id ? 'cc-input--error' : ''}`}
            disabled={loadingCourses || visibleCourses.length === 0}
          >
            <option value="">
              {loadingCourses ? 'Đang tải khóa học...' : 'Chọn một khóa học'}
            </option>
            {visibleCourses.map((course) => (
              <option key={course.id} value={course.id}>
                {course.title} · {course.category || 'N/A'} · {course.level || 'N/A'}
              </option>
            ))}
          </select>
          {errors.course_id && <p className="cc-error">{errors.course_id.message}</p>}
          {!loadingCourses && visibleCourses.length > 0 && selectedCourseId && (
            <p className="cc-hint">
              Đã chọn: {visibleCourses.find((course) => course.id === selectedCourseId)?.title || 'Khóa học'}
            </p>
          )}
          {!loadingCourses && courses.length === 0 && !coursesError && (
            <p className="cc-hint">Chưa có khóa học công khai để tạo lớp.</p>
          )}
          {coursesError && (
            <p className="cc-error">
              {coursesError} {' '}
              <button
                type="button"
                className="cc-back"
                style={{ marginLeft: 6 }}
                onClick={loadCourses}
              >
                Tải lại
              </button>
            </p>
          )}
        </div>

        <div className="cc-row">
          <div className="cc-field">
            <label className="cc-label">Ngày bắt đầu</label>
            <input type="date" {...register('start_date')} className="cc-input" />
          </div>
          <div className="cc-field">
            <label className="cc-label">Ngày kết thúc</label>
            <input type="date" {...register('end_date')} className="cc-input" />
          </div>
        </div>

        <div className="cc-field cc-field--half">
          <label className="cc-label">Số học viên tối đa</label>
          <input
            type="number"
            {...register('max_students', { min: 1, valueAsNumber: true })}
            className="cc-input"
            placeholder="VD: 30"
          />
        </div>

        <div className="cc-actions">
          <Button variant="outline" type="button" onClick={() => navigate('/dashboard/instructor/classes')}>
            Hủy
          </Button>
          <Button type="submit" loading={isLoading}>
            Tạo lớp học
          </Button>
        </div>
      </motion.form>
    </div>
  )
}

export default ClassCreatePage
