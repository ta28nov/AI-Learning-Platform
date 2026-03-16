import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import personalCourseService from '@services/personalCourseService'
import Button from '@components/ui/Button'
import Card, { CardBody } from '@components/ui/Card'
import Modal from '@components/ui/Modal'

/**
 * Trang danh sach khoa hoc ca nhan
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
        toast.error('Khong the tai khoa hoc ca nhan')
      } finally {
        setLoading(false)
      }
    }
    fetchCourses()
  }, [])

  // Tao khoa hoc bang AI prompt
  const handleCreateFromPrompt = async () => {
    if (prompt.length < 20) {
      toast.error('Prompt can it nhat 20 ky tu')
      return
    }
    setGenerating(true)
    try {
      const response = await personalCourseService.createFromPrompt({
        prompt,
        level: 'Beginner',
        language: 'vi'
      })
      toast.success('AI dang tao khoa hoc cho ban!')
      setShowPromptModal(false)
      setPrompt('')
      navigate(`/dashboard/personal-courses/${response.course_id || response.id}/edit`)
    } catch (error) {
      toast.error(error.message || 'Khong the tao khoa hoc')
    } finally {
      setGenerating(false)
    }
  }

  if (loading) return <div style={{ padding: 24, textAlign: 'center' }}>Dang tai...</div>

  return (
    <div style={{ padding: 16 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20, flexWrap: 'wrap', gap: 10 }}>
        <div>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 700 }}>Khoa hoc ca nhan</h1>
          <p style={{ color: '#6b7280', fontSize: '0.85rem' }}>{courses.length} khoa hoc</p>
        </div>
        <div style={{ display: 'flex', gap: 8 }}>
          <Button variant="outline" onClick={() => setShowPromptModal(true)}>
            Tao bang AI
          </Button>
          <Button onClick={() => navigate('/dashboard/personal-courses/create')}>
            + Tao thu cong
          </Button>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: 12 }}>
        {courses.map((course) => (
          <Card key={course.id || course.course_id} hover onClick={() => navigate(`/dashboard/courses/${course.id || course.course_id}`)}>
            <CardBody>
              <h3 style={{ fontWeight: 600, marginBottom: 4 }}>{course.title}</h3>
              <p style={{ fontSize: '0.8rem', color: '#6b7280', marginBottom: 6 }}>
                {course.description?.substring(0, 100)}
              </p>
              <div style={{ display: 'flex', gap: 8, fontSize: '0.7rem' }}>
                <span style={{ padding: '2px 8px', background: '#f3f4f6', borderRadius: 10 }}>{course.status || 'draft'}</span>
                <span style={{ padding: '2px 8px', background: '#e0e7ff', borderRadius: 10, color: '#3730a3' }}>{course.level}</span>
              </div>
            </CardBody>
          </Card>
        ))}
      </div>

      {courses.length === 0 && (
        <div style={{ textAlign: 'center', padding: 40, color: '#6b7280' }}>
          Ban chua co khoa hoc ca nhan nao. Hay tao khoa hoc bang AI hoac thu cong!
        </div>
      )}

      {/* Modal tao bang AI */}
      <Modal
        isOpen={showPromptModal}
        onClose={() => setShowPromptModal(false)}
        title="Tao khoa hoc bang AI"
      >
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          <p style={{ fontSize: '0.85rem', color: '#6b7280' }}>
            Mo ta nhung gi ban muon hoc, AI se tao khoa hoc phu hop:
          </p>
          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="VD: Toi muon hoc lap trinh Python co ban, tu cac khai niem bien, vong lap den ham va lop..."
            rows={4}
            style={{
              width: '100%', padding: '10px 12px', border: '1px solid #e5e7eb',
              borderRadius: 8, fontSize: '0.875rem', resize: 'vertical'
            }}
          />
          <span style={{ fontSize: '0.75rem', color: '#6b7280' }}>
            {prompt.length}/1000 ky tu (toi thieu 20)
          </span>
          <div style={{ display: 'flex', gap: 8, justifyContent: 'flex-end' }}>
            <Button variant="outline" onClick={() => setShowPromptModal(false)}>Huy</Button>
            <Button onClick={handleCreateFromPrompt} loading={generating}>
              Tao khoa hoc
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  )
}

export default PersonalCoursesPage
