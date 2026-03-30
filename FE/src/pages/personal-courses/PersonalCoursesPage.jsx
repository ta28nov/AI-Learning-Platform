import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import personalCourseService from '@services/personalCourseService'
import Button from '@components/ui/Button'
import Card, { CardBody } from '@components/ui/Card'
import Modal from '@components/ui/Modal'
import './PersonalCoursesPage.css'

/**
 * Trang danh sách khóa học cá nhân
 * Route: /dashboard/personal-courses
 * API: GET /courses/my-personal, POST /courses/from-prompt
 */
const PersonalCoursesPage = () => {
  const navigate = useNavigate()
  const [courses, setCourses] = useState([])
  const [loading, setLoading] = useState(true)
  const [showPromptModal, setShowPromptModal] = useState(false)
  const [prompt, setPrompt] = useState('')
  const [generating, setGenerating] = useState(false)

  useEffect(() => {
    const fetchCourses = async () => {
      try {
        setLoading(true)
        const data = await personalCourseService.getMyPersonalCourses()
        setCourses(data.courses || data || [])
      } catch (error) {
        toast.error('Không thể tải khóa học cá nhân')
      } finally {
        setLoading(false)
      }
    }
    fetchCourses()
  }, [])

  // Tạo khóa học bằng AI prompt
  const handleCreateFromPrompt = async () => {
    if (prompt.length < 20) {
      toast.error('Mô tả cần ít nhất 20 ký tự')
      return
    }
    setGenerating(true)
    try {
      const response = await personalCourseService.createFromPrompt({
        prompt,
        level: 'Beginner',
        language: 'vi'
      })
      toast.success('AI đang tạo khóa học cho bạn!')
      setShowPromptModal(false)
      setPrompt('')
      navigate(`/dashboard/personal-courses/${response.course_id || response.id}/edit`)
    } catch (error) {
      toast.error(error.message || 'Không thể tạo khóa học')
    } finally {
      setGenerating(false)
    }
  }

  if (loading) return <div className="personal-courses-loading">Đang tải...</div>

  return (
    <div className="personal-courses-page">
      <div className="personal-courses-header">
        <div>
          <h1 className="personal-courses-header__title">Khóa học cá nhân</h1>
          <p className="personal-courses-header__count">{courses.length} khóa học</p>
        </div>
        <div className="personal-courses-actions">
          <Button variant="outline" onClick={() => setShowPromptModal(true)}>
            🤖 Tạo bằng AI
          </Button>
          <Button onClick={() => navigate('/dashboard/personal-courses/create')}>
            + Tạo thủ công
          </Button>
        </div>
      </div>

      <div className="personal-courses-grid">
        {courses.map((course) => (
          <Card
            key={course.id || course.course_id}
            hover
            className="personal-course-card"
            onClick={() => navigate(`/dashboard/courses/${course.id || course.course_id}`)}
          >
            <CardBody>
              <h3 className="personal-course-card__title">{course.title}</h3>
              {course.description && (
                <p className="personal-course-card__desc">
                  {course.description.substring(0, 100)}
                  {course.description.length > 100 && '...'}
                </p>
              )}
              <div className="personal-course-card__badges">
                <span className={`personal-course-card__badge personal-course-card__badge--status${course.status === 'published' ? '-published' : ''}`}>
                  {course.status === 'published' ? 'Đã xuất bản' : 'Bản nháp'}
                </span>
                {course.level && (
                  <span className="personal-course-card__badge personal-course-card__badge--level">
                    {course.level}
                  </span>
                )}
              </div>
            </CardBody>
          </Card>
        ))}
      </div>

      {courses.length === 0 && (
        <div className="personal-courses-empty">
          Bạn chưa có khóa học cá nhân nào. Hãy tạo bằng AI hoặc thủ công!
        </div>
      )}

      {/* Modal tạo bằng AI */}
      <Modal
        isOpen={showPromptModal}
        onClose={() => setShowPromptModal(false)}
        title="Tạo khóa học bằng AI"
      >
        <div className="personal-courses-prompt">
          <p className="personal-courses-prompt__desc">
            Mô tả những gì bạn muốn học, AI sẽ tạo khóa học phù hợp:
          </p>
          <textarea
            className="personal-courses-prompt__textarea"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="VD: Tôi muốn học lập trình Python cơ bản, từ các khái niệm biến, vòng lặp đến hàm và lớp..."
            rows={4}
            maxLength={1000}
          />
          <span className="personal-courses-prompt__counter">
            {prompt.length}/1000 ký tự (tối thiểu 20)
          </span>
          <div className="personal-courses-prompt__actions">
            <Button variant="outline" onClick={() => setShowPromptModal(false)}>Hủy</Button>
            <Button onClick={handleCreateFromPrompt} loading={generating}>
              Tạo khóa học
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  )
}

export default PersonalCoursesPage
