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
      toast.success('Tao bai danh gia thanh cong!')
      navigate(`/dashboard/assessment/${response.session_id}`)
    } catch (error) {
      toast.error(error.message || 'Khong the tao bai danh gia')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="assessment-setup-page">
      <div className="page-header">
        <h1>Danh gia nang luc</h1>
        <p>AI se tao bai kiem tra phu hop voi trinh do cua ban</p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="assessment-form">
        {/* Buoc 1: Chon linh vuc */}
        <Card>
          <CardHeader>
            <h3>Buoc 1: Chon linh vuc</h3>
          </CardHeader>
          <CardBody>
            <div className="form-group">
              <label htmlFor="category">Linh vuc</label>
              <select
                id="category"
                {...register('category', { required: 'Vui long chon linh vuc' })}
                className="form-select"
              >
                <option value="">-- Chon linh vuc --</option>
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
              <h3>Buoc 2: Chon mon hoc</h3>
            </CardHeader>
            <CardBody>
              <div className="form-group">
                <label htmlFor="subject">Mon hoc</label>
                <select
                  id="subject"
                  {...register('subject', { required: 'Vui long chon mon hoc' })}
                  className="form-select"
                >
                  <option value="">-- Chon mon hoc --</option>
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
            <h3>Buoc 3: Chon cap do</h3>
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
                      {config.questions} cau - {config.time} phut
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
            Bat dau danh gia
          </Button>
        </div>
      </form>
    </div>
  )
}

export default AssessmentSetupPage
