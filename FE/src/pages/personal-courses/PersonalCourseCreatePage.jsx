import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import toast from 'react-hot-toast'
import personalCourseService from '@services/personalCourseService'
import Button from '@components/ui/Button'
import './PersonalCourseCreatePage.css'

const PersonalCourseCreatePage = () => {
  const navigate = useNavigate()
  const [submitting, setSubmitting] = useState(false)
  const [form, setForm] = useState({
    title: '',
    description: '',
    category: 'Programming',
    level: 'Beginner',
    language: 'vi',
    thumbnail_url: '',
  })

  const handleChange = (key, value) => {
    setForm((prev) => ({ ...prev, [key]: value }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (form.title.trim().length < 5) {
      toast.error('Tiêu đề cần ít nhất 5 ký tự')
      return
    }
    if (form.description.trim().length < 20) {
      toast.error('Mô tả cần ít nhất 20 ký tự')
      return
    }

    try {
      setSubmitting(true)
      const payload = {
        title: form.title.trim(),
        description: form.description.trim(),
        category: form.category,
        level: form.level,
        language: form.language,
        thumbnail_url: form.thumbnail_url.trim() || undefined,
      }
      const res = await personalCourseService.createManual(payload)
      const createdId = res.course_id || res.id
      toast.success('Đã tạo khóa học nháp. Chuyển sang trang chỉnh sửa...')
      navigate(`/dashboard/personal-courses/${createdId}/edit`)
    } catch (error) {
      toast.error(error.message || 'Không thể tạo khóa học thủ công')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <motion.div
      className="personal-course-create-page"
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25 }}
    >
      <div className="personal-course-create-header">
        <div className="personal-course-create-header__ornament" aria-hidden="true">
          <svg viewBox="0 0 120 14" fill="none">
            <path d="M2 7H48" stroke="currentColor" strokeWidth="1.5" />
            <circle cx="60" cy="7" r="4.5" stroke="currentColor" strokeWidth="1.5" />
            <path d="M72 7H118" stroke="currentColor" strokeWidth="1.5" />
          </svg>
        </div>
        <h1>Tạo khóa học thủ công</h1>
        <p>Nhập thông tin cơ bản để tạo khóa học nháp, sau đó bạn chỉnh sửa modules/lessons chi tiết.</p>
      </div>

      <form className="personal-course-create-form" onSubmit={handleSubmit}>
        <label className="personal-course-create-field">
          <span>Tiêu đề khóa học *</span>
          <input
            type="text"
            value={form.title}
            onChange={(e) => handleChange('title', e.target.value)}
            placeholder="Ví dụ: Python cho người mới bắt đầu"
            maxLength={200}
            required
          />
        </label>

        <label className="personal-course-create-field">
          <span>Mô tả khóa học *</span>
          <textarea
            value={form.description}
            onChange={(e) => handleChange('description', e.target.value)}
            placeholder="Mô tả mục tiêu, đối tượng phù hợp, nội dung chính..."
            rows={6}
            maxLength={2000}
            required
          />
          <small>{form.description.length}/2000 ký tự</small>
        </label>

        <div className="personal-course-create-grid">
          <label className="personal-course-create-field">
            <span>Danh mục *</span>
            <select value={form.category} onChange={(e) => handleChange('category', e.target.value)}>
              <option value="Programming">Programming</option>
              <option value="Data Science">Data Science</option>
              <option value="Math">Math</option>
              <option value="Business">Business</option>
              <option value="Languages">Languages</option>
            </select>
          </label>

          <label className="personal-course-create-field">
            <span>Trình độ *</span>
            <select value={form.level} onChange={(e) => handleChange('level', e.target.value)}>
              <option value="Beginner">Beginner</option>
              <option value="Intermediate">Intermediate</option>
              <option value="Advanced">Advanced</option>
            </select>
          </label>

          <label className="personal-course-create-field">
            <span>Ngôn ngữ</span>
            <select value={form.language} onChange={(e) => handleChange('language', e.target.value)}>
              <option value="vi">Tiếng Việt</option>
              <option value="en">English</option>
            </select>
          </label>
        </div>

        <label className="personal-course-create-field">
          <span>Thumbnail URL (tuỳ chọn)</span>
          <input
            type="url"
            value={form.thumbnail_url}
            onChange={(e) => handleChange('thumbnail_url', e.target.value)}
            placeholder="https://..."
          />
        </label>

        <div className="personal-course-create-actions">
          <Button type="button" variant="outline" onClick={() => navigate('/dashboard/personal-courses')} disabled={submitting}>
            Hủy
          </Button>
          <Button type="submit" loading={submitting} disabled={submitting}>
            Tạo khóa học
          </Button>
        </div>
      </form>
    </motion.div>
  )
}

export default PersonalCourseCreatePage
