import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { motion, AnimatePresence } from 'framer-motion'
import toast from 'react-hot-toast'
import assessmentService from '@services/assessmentService'
import Button from '@components/ui/Button'
import './AssessmentSetupPage.css'

const CodeIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/>
  </svg>
)
const DataIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/>
    <path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/>
  </svg>
)
const MathIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <path d="M4 7h16M4 17h16M9 3 7 21M17 3l-2 18"/>
  </svg>
)
const BusinessIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <rect x="2" y="7" width="20" height="14" rx="2"/><path d="M16 7V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v2"/>
    <line x1="12" y1="12" x2="12" y2="16"/><line x1="10" y1="14" x2="14" y2="14"/>
  </svg>
)
const LanguageIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <path d="m5 8 6 6"/><path d="m4 14 6-6 2-3"/><path d="M2 5h12"/><path d="M7 2h1"/>
    <path d="m22 22-5-10-5 10"/><path d="M14 18h6"/>
  </svg>
)

const CATEGORY_ICONS = {
  Programming: CodeIcon,
  'Data Science': DataIcon,
  Math: MathIcon,
  Business: BusinessIcon,
  Languages: LanguageIcon,
}

const LEVEL_CONFIG = {
  Beginner: { questions: 15, time: 15, desc: 'Kiến thức nền tảng, phù hợp người mới bắt đầu' },
  Intermediate: { questions: 25, time: 22, desc: 'Kiến thức trung cấp, cần có nền tảng cơ bản' },
  Advanced: { questions: 35, time: 30, desc: 'Kiến thức chuyên sâu, dành cho người có kinh nghiệm' },
}

const SUBJECTS_BY_CATEGORY = {
  Programming: ['Python', 'JavaScript', 'Java', 'C++', 'Web Development'],
  'Data Science': ['Data Analysis', 'Machine Learning', 'Statistics', 'Pandas'],
  Math: ['Algebra', 'Calculus', 'Statistics', 'Linear Algebra'],
  Business: ['Marketing', 'Finance', 'Management', 'Accounting'],
  Languages: ['English', 'Japanese', 'Korean', 'Chinese'],
}

/**
 * AssessmentSetupPage — Đánh giá năng lực AI
 * Route: /dashboard/assessment
 * API: POST /assessments/generate via assessmentService.generate — unchanged
 */
const AssessmentSetupPage = () => {
  const navigate = useNavigate()
  const [isLoading, setIsLoading] = useState(false)
  const { register, handleSubmit, watch, setValue, formState: { errors } } = useForm({
    defaultValues: { category: '', subject: '', level: 'Beginner', focus_areas: [] },
  })

  const selectedCategory = watch('category')
  const selectedSubject = watch('subject')
  const selectedLevel = watch('level')
  const availableSubjects = SUBJECTS_BY_CATEGORY[selectedCategory] || []

  const handleCategorySelect = (cat) => {
    setValue('category', cat)
    setValue('subject', '') // reset subject when category changes
  }

  const onSubmit = async (data) => {
    setIsLoading(true)
    try {
      const response = await assessmentService.generate(data)
      // Persist generated questions so AssessmentQuizPage can load them
      sessionStorage.setItem(
        `assessment_${response.session_id}`,
        JSON.stringify({
          questions: response.questions || [],
          time_limit_minutes: response.time_limit_minutes || 15,
        })
      )
      toast.success('Tạo bài đánh giá thành công!')
      navigate(`/dashboard/assessment/${response.session_id}`)
    } catch (error) {
      toast.error(error.message || 'Không thể tạo bài đánh giá')
    } finally {
      setIsLoading(false)
    }
  }

  const stepVariant = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.45, ease: [0.65, 0, 0.35, 1] } },
    exit: { opacity: 0, y: -10, transition: { duration: 0.2 } },
  }

  return (
    <div className="asp-page">
      {/* Header */}
      <motion.div
        className="asp-hero"
        initial={{ opacity: 0, y: 24 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, ease: [0.65, 0, 0.35, 1] }}
      >
        <svg className="asp-ornament" viewBox="0 0 48 12" fill="none">
          <line x1="0" y1="6" x2="16" y2="6" stroke="var(--gold-500)" strokeWidth="1" />
          <circle cx="24" cy="6" r="4" stroke="var(--gold-500)" strokeWidth="1" />
          <line x1="32" y1="6" x2="48" y2="6" stroke="var(--gold-500)" strokeWidth="1" />
        </svg>
        <h1 className="asp-hero__title">Đánh giá năng lực</h1>
        <p className="asp-hero__sub">AI tạo bài kiểm tra cá nhân hóa theo trình độ của bạn</p>
      </motion.div>

      <form onSubmit={handleSubmit(onSubmit)} className="asp-form">
        {/* Step 1: Category */}
        <motion.div
          className="asp-step"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.45, delay: 0.1 }}
        >
          <div className="asp-step__label">
            <span className="asp-step__num">01</span>
            <span className="asp-step__title">Chọn lĩnh vực</span>
          </div>
          <div className="asp-category-grid">
            {Object.entries(CATEGORY_ICONS).map(([cat, Icon]) => (
              <button
                key={cat}
                type="button"
                className={`asp-category-btn ${selectedCategory === cat ? 'asp-category-btn--active' : ''}`}
                onClick={() => handleCategorySelect(cat)}
              >
                <span className="asp-category-btn__icon"><Icon /></span>
                <span className="asp-category-btn__label">{cat}</span>
              </button>
            ))}
          </div>
          {errors.category && <p className="asp-error">{errors.category.message}</p>}
          {/* hidden input for react-hook-form validation */}
          <input type="hidden" {...register('category', { required: 'Vui lòng chọn lĩnh vực' })} />
        </motion.div>

        {/* Step 2: Subject — revealed after category selected */}
        <AnimatePresence>
          {selectedCategory && (
            <motion.div
              className="asp-step"
              key="step-subject"
              variants={stepVariant}
              initial="hidden"
              animate="visible"
              exit="exit"
            >
              <div className="asp-step__label">
                <span className="asp-step__num">02</span>
                <span className="asp-step__title">Chọn môn học</span>
              </div>
              <div className="asp-subject-pills">
                {availableSubjects.map((sub) => (
                  <button
                    key={sub}
                    type="button"
                    className={`asp-subject-pill ${selectedSubject === sub ? 'asp-subject-pill--active' : ''}`}
                    onClick={() => setValue('subject', sub)}
                  >
                    {sub}
                  </button>
                ))}
              </div>
              {errors.subject && <p className="asp-error">{errors.subject.message}</p>}
              <input type="hidden" {...register('subject', { required: 'Vui lòng chọn môn học' })} />
            </motion.div>
          )}
        </AnimatePresence>

        {/* Step 3: Level */}
        <motion.div
          className="asp-step"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.45, delay: 0.2 }}
        >
          <div className="asp-step__label">
            <span className="asp-step__num">03</span>
            <span className="asp-step__title">Chọn cấp độ</span>
          </div>
          <div className="asp-level-grid">
            {Object.entries(LEVEL_CONFIG).map(([level, cfg]) => (
              <label
                key={level}
                className={`asp-level-card ${selectedLevel === level ? 'asp-level-card--active' : ''}`}
              >
                <input type="radio" value={level} {...register('level')} className="asp-level-radio" />
                <div className="asp-level-card__name">{level}</div>
                <div className="asp-level-card__stats">
                  <span className="asp-level-card__num">{cfg.questions}</span>
                  <span className="asp-level-card__unit">câu</span>
                  <span className="asp-level-card__sep">·</span>
                  <span className="asp-level-card__num">{cfg.time}</span>
                  <span className="asp-level-card__unit">phút</span>
                </div>
                <p className="asp-level-card__desc">{cfg.desc}</p>
              </label>
            ))}
          </div>
        </motion.div>

        {/* Submit */}
        <motion.div
          className="asp-submit"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.35 }}
        >
          <Button
            type="submit"
            size="lg"
            loading={isLoading}
            disabled={isLoading || !selectedCategory || !selectedSubject}
          >
            {isLoading ? 'AI đang tạo bài đánh giá…' : 'Bắt đầu đánh giá'}
          </Button>
        </motion.div>
      </form>
    </div>
  )
}

export default AssessmentSetupPage
