import { useNavigate, useLocation } from 'react-router-dom'
import Button from '@components/ui/Button'
import './CourseLearningNav.css'

/**
 * Điều hướng quay lại trong luồng học: module → khóa học → khóa học của tôi.
 */
const CourseLearningNav = ({ courseId, moduleId, classId, className: classLabel, sticky = true, className: rootClassName = '' }) => {
  const navigate = useNavigate()
  const location = useLocation()
  const fromClass = classId || location.state?.fromClass
  const fromClassName = classLabel || location.state?.fromClassName
  if (!courseId) return null

  const rootClass = [
    'course-learning-nav',
    sticky ? 'course-learning-nav--sticky' : '',
    rootClassName,
  ]
    .filter(Boolean)
    .join(' ')

  return (
    <nav className={rootClass} aria-label="Điều hướng khóa học">
      {fromClass && (
        <Button
          variant="ghost"
          size="sm"
          onClick={() => navigate(`/dashboard/classes/${fromClass}`)}
        >
          ← {fromClassName ? `Lớp ${fromClassName}` : 'Lớp học'}
        </Button>
      )}
      {moduleId && (
        <Button
          variant="outline"
          size="sm"
          onClick={() => navigate(`/dashboard/courses/${courseId}/modules/${moduleId}`)}
        >
          ← Module này
        </Button>
      )}
      <Button
        variant="outline"
        size="sm"
        onClick={() => navigate(`/dashboard/courses/${courseId}/modules`)}
      >
        Danh sách module
      </Button>
      <Button
        variant="outline"
        size="sm"
        onClick={() => navigate(`/dashboard/courses/${courseId}`)}
      >
        Trang khóa học
      </Button>
      <Button
        variant="ghost"
        size="sm"
        onClick={() => navigate('/dashboard/my-courses')}
      >
        Khóa học của tôi
      </Button>
    </nav>
  )
}

export default CourseLearningNav
