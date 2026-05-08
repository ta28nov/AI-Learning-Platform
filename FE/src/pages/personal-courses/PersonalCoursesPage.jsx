import { useState, useEffect, useMemo, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import toast from 'react-hot-toast'
import personalCourseService from '@services/personalCourseService'
import Button from '@components/ui/Button'
import Card, { CardBody } from '@components/ui/Card'
import Modal from '@components/ui/Modal'
import StateView from '@components/ui/StateView'
import AILoadingState from '@components/ui/AILoadingState'
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
  const [aiLevel, setAiLevel] = useState('Beginner')
  const [aiDurationWeeks, setAiDurationWeeks] = useState(4)
  const [aiLanguage, setAiLanguage] = useState('vi')
  const promptRef = useRef(null)

  const promptTemplates = useMemo(() => ([
    'Tôi muốn học Python từ cơ bản đến làm project thực tế: biến, hàm, OOP, xử lý file, và mini project quản lý dữ liệu.',
    'Tôi muốn học ReactJS bài bản để tự xây dashboard: hooks, state management, gọi API, routing, và tối ưu hiệu năng.',
    'Tôi muốn học Data Analysis thực chiến với SQL + Pandas + trực quan hóa để làm báo cáo phân tích cho doanh nghiệp.',
  ]), [])

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

  useEffect(() => {
    if (!showPromptModal) return
    const timer = window.setTimeout(() => promptRef.current?.focus(), 80)
    return () => window.clearTimeout(timer)
  }, [showPromptModal])

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
        level: aiLevel,
        estimated_duration_weeks: Number(aiDurationWeeks) || 4,
        language: aiLanguage,
      })
      toast.success('AI đang tạo khóa học cho bạn!')
      setShowPromptModal(false)
      setPrompt('')
      setAiLevel('Beginner')
      setAiDurationWeeks(4)
      setAiLanguage('vi')
      navigate(`/dashboard/personal-courses/${response.course_id || response.id}/edit`)
    } catch (error) {
      toast.error(error.message || 'Không thể tạo khóa học')
    } finally {
      setGenerating(false)
    }
  }

  if (loading) {
    return (
      <div className="personal-courses-loading">
        <AILoadingState
          title="AI đang tải khóa học cá nhân"
          message="Đang đồng bộ danh sách khóa học do bạn tạo."
          steps={[
            'Đang tải dữ liệu khóa học cá nhân...',
            'Đang kiểm tra trạng thái xuất bản...',
            'Đang hoàn tất giao diện hiển thị...',
          ]}
        />
      </div>
    )
  }

  return (
    <motion.div
      className="personal-courses-page"
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <div className="personal-courses-header">
        <div>
          <div className="personal-courses-header__ornament" aria-hidden="true">
            <svg viewBox="0 0 120 14" fill="none">
              <path d="M2 7H48" stroke="currentColor" strokeWidth="1.5" />
              <circle cx="60" cy="7" r="4.5" stroke="currentColor" strokeWidth="1.5" />
              <path d="M72 7H118" stroke="currentColor" strokeWidth="1.5" />
            </svg>
          </div>
          <h1 className="personal-courses-header__title">Khóa học cá nhân</h1>
          <p className="personal-courses-header__count">{courses.length} khóa học</p>
        </div>
        <div className="personal-courses-actions">
          <Button variant="outline" onClick={() => setShowPromptModal(true)}>
            Tạo bằng AI
          </Button>
          <Button onClick={() => navigate('/dashboard/personal-courses/create')}>
            + Tạo thủ công
          </Button>
        </div>
      </div>

      <div className="personal-courses-grid">
        {courses.map((course, index) => (
          <motion.div
            key={course.id || course.course_id}
            initial={{ opacity: 0, y: 14 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: Math.min(index * 0.04, 0.25) }}
          >
            <Card
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
          </motion.div>
        ))}
      </div>

      {courses.length === 0 && (
        <StateView
          type="empty"
          title="Bạn chưa có khóa học cá nhân"
          message="Hãy tạo khóa học bằng AI hoặc thủ công để bắt đầu lộ trình riêng."
        />
      )}

      {/* Modal tạo bằng AI */}
      <Modal
        isOpen={showPromptModal}
        onClose={() => {
          setShowPromptModal(false)
          setPrompt('')
        }}
        title="Tạo khóa học bằng AI"
      >
        <div className="personal-courses-prompt">
          <p className="personal-courses-prompt__desc">
            Mô tả những gì bạn muốn học, AI sẽ tạo khóa học phù hợp:
          </p>
          <div className="personal-courses-prompt__templates">
            {promptTemplates.map((template, idx) => (
              <button
                key={idx}
                type="button"
                className="personal-courses-prompt__template-btn"
                onClick={() => {
                  setPrompt(template)
                  window.setTimeout(() => promptRef.current?.focus(), 0)
                }}
              >
                Mẫu {idx + 1}
              </button>
            ))}
          </div>

          <textarea
            ref={promptRef}
            className="personal-courses-prompt__textarea"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Mô tả mục tiêu học tập, năng lực hiện tại, kết quả mong muốn... (>= 20 ký tự)"
            rows={7}
            maxLength={1000}
            autoFocus
          />

          <div className="personal-courses-prompt__config">
            <label className="personal-courses-prompt__config-item">
              <span>Trình độ</span>
              <select value={aiLevel} onChange={(e) => setAiLevel(e.target.value)}>
                <option value="Beginner">Beginner</option>
                <option value="Intermediate">Intermediate</option>
                <option value="Advanced">Advanced</option>
              </select>
            </label>

            <label className="personal-courses-prompt__config-item">
              <span>Thời lượng</span>
              <select value={aiDurationWeeks} onChange={(e) => setAiDurationWeeks(Number(e.target.value))}>
                <option value={2}>2 tuần</option>
                <option value={4}>4 tuần</option>
                <option value={6}>6 tuần</option>
                <option value={8}>8 tuần</option>
              </select>
            </label>

            <label className="personal-courses-prompt__config-item">
              <span>Ngôn ngữ</span>
              <select value={aiLanguage} onChange={(e) => setAiLanguage(e.target.value)}>
                <option value="vi">Tiếng Việt</option>
                <option value="en">English</option>
              </select>
            </label>
          </div>

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
    </motion.div>
  )
}

export default PersonalCoursesPage
