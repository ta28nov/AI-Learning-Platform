import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import personalCourseService from '@services/personalCourseService'
import courseService from '@services/courseService'
import Button from '@components/ui/Button'
import Card, { CardHeader, CardBody } from '@components/ui/Card'
import './CourseEditorPage.css'

/**
 * Trang chỉnh sửa khóa học cá nhân (Rich Text Editor + Drag-drop modules)
 * Route: /dashboard/personal-courses/:courseId/edit
 * API: PUT /courses/personal/{courseId}
 */
const CourseEditorPage = () => {
  const { courseId } = useParams()
  const navigate = useNavigate()
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [course, setCourse] = useState({
    title: '',
    description: '',
    category: '',
    level: 'Beginner',
    modules: []
  })

  // Theo rule: loading state, fetch data
  useEffect(() => {
    const fetchCourse = async () => {
      try {
        setLoading(true)
        // Dùng courseService để lấy chi tiết hiện tại (mockup api logic)
        const data = await courseService.getCourseDetail(courseId)
        setCourse({
          title: data.title || '',
          description: data.description || '',
          category: data.category || '',
          level: data.level || 'Beginner',
          modules: data.modules || []
        })
      } catch (error) {
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

  // Handle nested update
  const handleSave = async (e) => {
    e.preventDefault()
    if (!course.title.trim()) {
      toast.error('Tiêu đề khóa học là bắt buộc')
      return
    }

    try {
      setSaving(true)
      // Call PUT /courses/personal/{course_id}
      await personalCourseService.updateCourse(courseId, course)
      toast.success('Lưu khóa học thành công')
      navigate('/dashboard/personal-courses')
    } catch (error) {
      toast.error('Lưu thất bại. Vui lòng thử lại')
    } finally {
      setSaving(false)
    }
  }

  if (loading) return <div className="loading-spinner">Đang tải trình chỉnh sửa...</div>

  return (
    <div className="course-editor-page">
      <div className="course-editor-page__header">
        <h1>Chỉnh sửa khóa học cá nhân</h1>
        <div className="course-editor-page__actions">
          <Button variant="outline" onClick={() => navigate('/dashboard/personal-courses')} disabled={saving}>
            Hủy
          </Button>
          <Button variant="primary" onClick={handleSave} disabled={saving}>
            {saving ? 'Đang lưu...' : 'Lưu thay đổi'}
          </Button>
        </div>
      </div>

      <div className="course-editor-page__content">
        <Card className="course-editor-page__main-info">
          <CardHeader>
            <h3>Thông tin chung</h3>
          </CardHeader>
          <CardBody>
            <form className="course-editor-page__form" onSubmit={handleSave}>
              <div className="form-group">
                <label htmlFor="title">Tiêu đề khóa học</label>
                <input
                  id="title"
                  name="title"
                  className="form-select"
                  value={course.title}
                  onChange={handleChange}
                  placeholder="Nhập tiêu đề..."
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="category">Danh mục</label>
                <select
                  id="category"
                  name="category"
                  className="form-select"
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

              <div className="form-group">
                <label htmlFor="level">Độ khó</label>
                <select
                  id="level"
                  name="level"
                  className="form-select"
                  value={course.level}
                  onChange={handleChange}
                >
                  <option value="Beginner">Người mới bắt đầu</option>
                  <option value="Intermediate">Trung bình</option>
                  <option value="Advanced">Nâng cao</option>
                </select>
              </div>

              <div className="form-group">
                <label htmlFor="description">Mô tả (Rich Text)</label>
                <textarea
                  id="description"
                  name="description"
                  className="form-select course-editor-page__textarea"
                  value={course.description}
                  onChange={handleChange}
                  placeholder="Mô tả chi tiết về khóa học..."
                  rows="6"
                />
              </div>
            </form>
          </CardBody>
        </Card>

        {/* Mockup area for Modules/Lessons Builder */}
        <Card className="course-editor-page__modules">
          <CardHeader>
            <h3>Cấu trúc khóa học (Build & Drag-drop)</h3>
          </CardHeader>
          <CardBody>
            <div className="course-editor-page__builder">
              <div className="course-editor-page__builder-empty">
                <span className="course-editor-page__builder-icon">🧩</span>
                <p>Kéo thả các bài học vào đây để sắp xếp</p>
                <Button variant="outline" size="sm">
                  + Thêm Module
                </Button>
              </div>
              
              {/* Nếu có module render danh sách */}
              {course.modules && course.modules.length > 0 && (
                <div className="course-editor-page__module-list">
                  {course.modules.map((m, idx) => (
                    <div key={idx} className="course-editor-page__module-item">
                      <span className="course-editor-page__drag-handle">☰</span>
                      <div className="course-editor-page__module-info">
                        <strong>Module {idx + 1}:</strong> {m.title}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </CardBody>
        </Card>
      </div>
    </div>
  )
}

export default CourseEditorPage
