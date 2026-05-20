import { Link } from 'react-router-dom'
import useClassLearningContext from '@hooks/useClassLearningContext'
import './ClassLearningBanner.css'

/**
 * Banner cố định khi HV học khóa qua lớp — dữ liệu từ navigation state / sessionStorage.
 */
const ClassLearningBanner = ({ courseId: courseIdProp }) => {
  const ctx = useClassLearningContext(courseIdProp)
  if (!ctx?.fromClass) return null

  return (
    <div className="class-learning-banner" role="status">
      <span className="class-learning-banner__text">
        Đang học qua lớp <strong>{ctx.fromClassName || '—'}</strong>
        {ctx.instructorName ? (
          <> — GV: <strong>{ctx.instructorName}</strong></>
        ) : null}
      </span>
      <Link to={`/dashboard/classes/${ctx.fromClass}`} className="class-learning-banner__link">
        Xem lớp
      </Link>
    </div>
  )
}

export default ClassLearningBanner
