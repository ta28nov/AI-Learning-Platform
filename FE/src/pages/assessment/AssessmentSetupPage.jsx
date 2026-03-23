import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import toast from 'react-hot-toast'
import assessmentService from '@services/assessmentService'
import Button from '@components/ui/Button'
import Card, { CardHeader, CardBody } from '@components/ui/Card'
import './AssessmentSetupPage.css'

/**
 * Trang thiet lap bai danh gia nang luc AI
 * Route: /dashboard/assessment
 * Flow: Chon category → subject → level → focus_areas → POST /assessments/generate
 */
const AssessmentSetupPage = () => {
  const navigate = useNavigate()
  const [isLoading, setIsLoading] = useState(false)
  const { register, handleSubmit, watch, formState: { errors } } = useForm({
    defaultValues: {
      category: '',
      subject: '',
      level: 'Beginner',
      focus_areas: []
    }
  })

  const selectedLevel = watch('level')

  // Cau hinh so cau hoi va thoi gian theo level
  const levelConfig = {
    Beginner: { questions: 15, time: 15 },
    Intermediate: { questions: 25, time: 22 },
    Advanced: { questions: 35, time: 30 }
  }

  // Danh sach categories va subjects
  const categories = ['Programming', 'Mathematics', 'Business', 'Science', 'Language']
  const subjectsByCategory = {
    Programming: ['Python', 'JavaScript', 'Java', 'C++', 'Web Development'],
    Mathematics: ['Algebra', 'Calculus', 'Statistics', 'Linear Algebra'],
    Business: ['Marketing', 'Finance', 'Management', 'Accounting'],
    Science: ['Physics', 'Chemistry', 'Biology', 'Computer Science'],
    Language: ['English', 'Japanese', 'Korean', 'Chinese']
  }

  const selectedCategory = watch('category')
  const availableSubjects = subjectsByCategory[selectedCategory] || []

  // Xu ly gui form tao bai danh gia
  const onSubmit = async (data) => {
    setIsLoading(true)
    try {
      const response = await assessmentService.generate(data)
      toast.success('Tạo bài đánh giá thành công!')
      navigate(`/dashboard/assessment/${response.session_id}`)
    } catch (error) {
      toast.error(error.message || 'Không thể tạo bài đánh giá')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="assessment-setup-page">
      <div className="page-header">
        <h1>Đánh giá năng lực</h1>
        <p>AI sẽ tạo bài kiểm tra phù hợp với trình độ của bạn</p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="assessment-form">
        {/* Buoc 1: Chon linh vuc */}
        <Card>
          <CardHeader>
            <h3>Bước 1: Chọn lĩnh vực</h3>
          </CardHeader>
          <CardBody>
            <div className="form-group">
              <label htmlFor="category">Lĩnh vực</label>
              <select
                id="category"
                {...register('category', { required: 'Vui lòng chọn lĩnh vực' })}
                className="form-select"
              >
                <option value="">-- Chọn lĩnh vực --</option>
                {categories.map((cat) => (
                  <option key={cat} value={cat}>{cat}</option>
                ))}
              </select>
              {errors.category && <span className="form-error">{errors.category.message}</span>}
            </div>
          </CardBody>
        </Card>

        {/* Buoc 2: Chon mon hoc */}
        {selectedCategory && (
          <Card>
            <CardHeader>
              <h3>Bước 2: Chọn môn học</h3>
            </CardHeader>
            <CardBody>
              <div className="form-group">
                <label htmlFor="subject">Môn học</label>
                <select
                  id="subject"
                  {...register('subject', { required: 'Vui lòng chọn môn học' })}
                  className="form-select"
                >
                  <option value="">-- Chọn môn học --</option>
                  {availableSubjects.map((sub) => (
                    <option key={sub} value={sub}>{sub}</option>
                  ))}
                </select>
                {errors.subject && <span className="form-error">{errors.subject.message}</span>}
              </div>
            </CardBody>
          </Card>
        )}

        {/* Buoc 3: Chon cap do */}
        <Card>
          <CardHeader>
            <h3>Bước 3: Chọn cấp độ</h3>
          </CardHeader>
          <CardBody>
            <div className="level-options">
              {Object.entries(levelConfig).map(([level, config]) => (
                <label
                  key={level}
                  className={`level-option ${selectedLevel === level ? 'level-option--active' : ''}`}
                >
                  <input
                    type="radio"
                    value={level}
                    {...register('level')}
                  />
                  <div className="level-option__content">
                    <span className="level-option__name">{level}</span>
                    <span className="level-option__info">
                      {config.questions} câu - {config.time} phút
                    </span>
                  </div>
                </label>
              ))}
            </div>
          </CardBody>
        </Card>

        {/* Nut gui */}
        <div className="form-actions">
          <Button
            type="submit"
            loading={isLoading}
            disabled={isLoading}
            size="lg"
          >
            Bắt đầu đánh giá
          </Button>
        </div>
      </form>
    </div>
  )
}

export default AssessmentSetupPage
