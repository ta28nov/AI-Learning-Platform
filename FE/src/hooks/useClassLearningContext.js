import { useParams, useLocation } from 'react-router-dom'
import { readClassLearningContext } from '@utils/classLearningContext'

/** Ngữ cảnh lớp khi học viên học qua lớp (state + sessionStorage). */
export default function useClassLearningContext(courseIdOverride) {
  const { courseId: courseIdParam } = useParams()
  const location = useLocation()
  const courseId = courseIdOverride || courseIdParam
  if (!courseId) return null
  return readClassLearningContext(courseId, location.state)
}
