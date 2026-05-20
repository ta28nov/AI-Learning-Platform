const STORAGE_PREFIX = 'class_learning_ctx_'

/** Lưu ngữ cảnh lớp theo courseId (sessionStorage) để banner vẫn hiện sau refresh. */
export function saveClassLearningContext(courseId, ctx) {
  if (!courseId || !ctx?.fromClass) return ctx || null
  const payload = {
    fromClass: ctx.fromClass,
    fromClassName: ctx.fromClassName || '',
    instructorName: ctx.instructorName || '',
    courseId,
  }
  try {
    sessionStorage.setItem(STORAGE_PREFIX + courseId, JSON.stringify(payload))
  } catch {
    /* quota / private mode */
  }
  return payload
}

/** Đọc từ location.state hoặc sessionStorage. */
export function readClassLearningContext(courseId, locationState) {
  if (locationState?.fromClass) {
    return saveClassLearningContext(courseId, locationState)
  }
  if (!courseId) return null
  try {
    const raw = sessionStorage.getItem(STORAGE_PREFIX + courseId)
    if (raw) return JSON.parse(raw)
  } catch {
    /* ignore */
  }
  return null
}

export function buildClassNavigateState({ classId, className, instructorName, courseId }) {
  return saveClassLearningContext(courseId, {
    fromClass: classId,
    fromClassName: className,
    instructorName,
    courseId,
  })
}

/** Điều hướng học — resume mở thẳng next_lesson nếu BE trả lesson_id. */
export function navigateToCourseLearning(
  navigate,
  { courseId, classId, className, instructorName, nextLesson, resume = false }
) {
  if (!courseId) return
  const state = buildClassNavigateState({
    classId,
    className,
    instructorName,
    courseId,
  })
  const lessonId = nextLesson?.lesson_id
  if (resume && lessonId) {
    navigate(`/dashboard/courses/${courseId}/lessons/${lessonId}`, { state })
  } else {
    navigate(`/dashboard/courses/${courseId}/modules`, { state })
  }
}
