import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { motion, useReducedMotion, useScroll, useSpring } from 'framer-motion'
import toast from 'react-hot-toast'
import learningService from '@services/learningService'
import { useAuthStore } from '@stores/authStore'
import Button from '@components/ui/Button'
import Card, { CardHeader, CardBody } from '@components/ui/Card'
import StateView from '@components/ui/StateView'
import ChatWidget from '@components/chat/ChatWidget'
import ClassLearningBanner from '@components/classes/ClassLearningBanner'
import CourseLearningNav from './CourseLearningNav'
import './LessonPage.css'

/**
 * Trang hiển thị nội dung bài học
 * Route: /dashboard/courses/:courseId/lessons/:lessonId
 * API: GET /courses/{courseId}/lessons/{lessonId}
 * Render: text_content, video_info, attachments, navigation, quiz_info
 */
const LessonPage = () => {
  const { courseId, lessonId } = useParams()
  const navigate = useNavigate()
  const { user } = useAuthStore()
  const isInstructor = user?.role === 'instructor' || user?.role === 'admin'
  const [lesson, setLesson] = useState(null)
  const [loading, setLoading] = useState(true)
  const [completing, setCompleting] = useState(false)
  const [completionInfo, setCompletionInfo] = useState(null)
  const shouldReduceMotion = useReducedMotion()
  const { scrollYProgress } = useScroll()
  const progress = useSpring(scrollYProgress, { stiffness: 100, damping: 25 })

  const isInvalidLessonId = !lessonId || lessonId === 'null' || lessonId === 'undefined'

  useEffect(() => {
    setCompletionInfo(null)
  }, [lessonId])

  useEffect(() => {
    if (isInvalidLessonId) {
      toast.error('Không có bài học tiếp theo')
      navigate(`/dashboard/courses/${courseId}/modules`, { replace: true })
    }
  }, [isInvalidLessonId, courseId, navigate])

  // Lấy nội dung bài học khi mount hoặc khi lessonId thay đổi
  useEffect(() => {
    if (isInvalidLessonId) return

    const fetchLesson = async () => {
      try {
        setLoading(true)
        const data = await learningService.getLessonContent(courseId, lessonId)
        setLesson(data)
      } catch (error) {
        toast.error('Không thể tải bài học')
      } finally {
        setLoading(false)
      }
    }
    fetchLesson()
  }, [courseId, lessonId, isInvalidLessonId])

  const refetchLesson = async () => {
    const data = await learningService.getLessonContent(courseId, lessonId)
    setLesson(data)
  }

  const handleCompleteLesson = async () => {
    try {
      setCompleting(true)
      const result = await learningService.completeLesson(courseId, lessonId)
      setCompletionInfo(result)
      toast.success(result?.message || 'Đã đánh dấu hoàn thành bài học')
      await refetchLesson()
    } catch (error) {
      toast.error(error?.message || 'Không thể cập nhật trạng thái bài học')
    } finally {
      setCompleting(false)
    }
  }

  if (isInvalidLessonId) {
    return <motion.div className="loading-spinner">Đang chuyển hướng...</motion.div>
  }

  const previousLesson = getNavLesson(lesson?.navigation?.previous_lesson)
  const nextLesson = getNavLesson(lesson?.navigation?.next_lesson)
  const progressPercent = completionInfo?.progress_percent ?? null
  const isCourseComplete =
    completionInfo?.enrollment_status === 'completed' ||
    (progressPercent != null && progressPercent >= 100)
  const showCompletionPanel =
    lesson?.completion_status?.is_completed && !nextLesson

  if (loading) return <motion.div className="loading-spinner">Đang tải bài học...</motion.div>
  if (!lesson) return <StateView type="empty" title="Không tìm thấy bài học" message="Bài học không tồn tại hoặc đã bị xóa." actionLabel="Quay lại modules" onAction={() => navigate(`/dashboard/courses/${courseId}/modules`)} />

  return (
    <div className="lesson-page">
      <ClassLearningBanner />
      {!shouldReduceMotion && (
        <motion.div className="lesson-scroll-progress" style={{ scaleX: progress }} />
      )}
      {/* Breadcrumb */}
      <div className="lesson-breadcrumb">
        <span
          className="breadcrumb-link"
          onClick={() => navigate(`/dashboard/courses/${courseId}`)}
        >
          Khóa học
        </span>
        {lesson.module_title && (
          <>
            <span className="breadcrumb-sep">/</span>
            <span
              className="breadcrumb-link"
              onClick={() => navigate(
                lesson.module_id
                  ? `/dashboard/courses/${courseId}/modules/${lesson.module_id}`
                  : `/dashboard/courses/${courseId}/modules`
              )}
            >
              {lesson.module_title}
            </span>
          </>
        )}
        <span className="breadcrumb-sep">/</span>
        <span className="breadcrumb-current">{lesson.title}</span>
      </div>

      {/* Header */}
      <motion.div className="lesson-header" initial={shouldReduceMotion ? false : { opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}>
        <h1>{lesson.title}</h1>
        <div className="lesson-meta">
          <span>Bài {lesson.order}</span>
          <span>{lesson.duration_minutes} phút</span>
          {lesson.content_type && (
            <span>{contentTypeLabel(lesson.content_type)}</span>
          )}
          {lesson.completion_status?.is_completed && (
            <span className="completed-badge">✓ Đã hoàn thành</span>
          )}
        </div>
      </motion.div>

      {/* Video player */}
      {lesson.video_info && lesson.video_info.url && (
        <div className="lesson-video">
          {getYoutubeEmbedUrl(lesson.video_info.url) ? (
            <iframe
              className="video-player"
              src={getYoutubeEmbedUrl(lesson.video_info.url)}
              title={lesson.title}
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
              referrerPolicy="strict-origin-when-cross-origin"
              allowFullScreen
            />
          ) : (
            <video
              controls
              poster={lesson.video_info.thumbnail_url || ''}
              className="video-player"
            >
              <source src={lesson.video_info.url} type="video/mp4" />
              Trình duyệt không hỗ trợ video.
            </video>
          )}
        </div>
      )}

      {/* Text content */}
      {lesson.text_content && (
        <Card className="lesson-content-card">
          <CardBody>
            <div
              className="lesson-text-content"
              dangerouslySetInnerHTML={{ __html: lesson.text_content }}
            />
          </CardBody>
        </Card>
      )}

      {/* Learning objectives */}
      {lesson.learning_objectives && lesson.learning_objectives.length > 0 && (
        <Card>
          <CardHeader>
            <h3>Mục tiêu bài học</h3>
          </CardHeader>
          <CardBody>
            <ul className="objectives-list">
              {lesson.learning_objectives.map((obj, idx) => (
                <li key={`${obj}-${idx}`}>{obj}</li>
              ))}
            </ul>
          </CardBody>
        </Card>
      )}

      {/* Attachments / Resources */}
      {lesson.attachments && lesson.attachments.length > 0 && (
        <Card>
          <CardHeader>
            <h3>Tài liệu đính kèm</h3>
          </CardHeader>
          <CardBody>
            <div className="attachments-list">
              {lesson.attachments.map((file, idx) => (
                <a
                  key={file.id || `${file.url}-${idx}`}
                  href={file.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="attachment-item"
                >
                  <span className="attachment-icon">
                    {attachmentTypeLabel(file.file_type)}
                  </span>
                  <span className="attachment-name">{file.filename}</span>
                  {file.size_mb && <span className="attachment-size">{file.size_mb} MB</span>}
                </a>
              ))}
            </div>
          </CardBody>
        </Card>
      )}

      {isInstructor && (
        <Card className="quiz-prompt-card quiz-instructor-card">
          <CardBody>
            <motion.div className="quiz-prompt quiz-prompt--instructor">
              <div className="quiz-prompt__info">
                <span className="quiz-instructor-eyebrow">Giảng viên</span>
                <h3>Quiz cho bài học này</h3>
                <p className="lesson-instructor-hint">
                  {lesson.has_quiz
                    ? `Đã gắn quiz · ${lesson.quiz_info?.question_count || 0} câu hỏi`
                    : 'Chưa có quiz — tạo để học viên kiểm tra sau bài học'}
                </p>
              </div>
              <div className="quiz-instructor-actions">
                <Button
                  onClick={() =>
                    navigate(
                      `/dashboard/instructor/quizzes/create?lessonId=${lessonId}&courseId=${courseId}`
                    )
                  }
                >
                  {lesson.has_quiz ? 'Tạo quiz mới' : 'Tạo quiz'}
                </Button>
                {lesson.has_quiz && lesson.quiz_info?.quiz_id && (
                  <>
                    <Button
                      variant="outline"
                      onClick={() => navigate(`/dashboard/quiz/${lesson.quiz_info.quiz_id}`)}
                    >
                      Xem trước
                    </Button>
                    <Button
                      variant="outline"
                      onClick={() =>
                        navigate(`/dashboard/instructor/quizzes/${lesson.quiz_info.quiz_id}/results`)
                      }
                    >
                      Kết quả lớp
                    </Button>
                  </>
                )}
              </div>
            </motion.div>
          </CardBody>
        </Card>
      )}

      {/* Quiz prompt */}
      {lesson.has_quiz && lesson.quiz_info && (
        <Card className="quiz-prompt-card">
          <CardBody>
            <div className="quiz-prompt">
              <div className="quiz-prompt__info">
                <h3>Quiz: {lesson.quiz_info.question_count} câu hỏi</h3>
                {lesson.quiz_info.is_mandatory && (
                  <span className="mandatory-badge">Bắt buộc</span>
                )}
              </div>
              <Button
                onClick={() => navigate(`/dashboard/quiz/${lesson.quiz_info.quiz_id}`)}
              >
                Làm quiz
              </Button>
            </div>
          </CardBody>
        </Card>
      )}

      {showCompletionPanel && (
        <Card className="lesson-complete-card">
          <CardBody>
            <div className="lesson-complete-card__inner">
              <p className="lesson-complete-card__eyebrow">
                {isCourseComplete ? 'Hoàn thành khóa học' : 'Hết bài trong module'}
              </p>
              <h2 className="lesson-complete-card__title">
                {isCourseComplete
                  ? 'Chúc mừng! Bạn đã hoàn thành khóa học'
                  : 'Bạn đã hoàn thành bài học cuối trong module này'}
              </h2>
              <p className="lesson-complete-card__message">
                {isCourseComplete
                  ? progressPercent != null
                    ? `Tiến độ khóa học: ${Math.round(progressPercent)}%. Hãy xem lại nội dung hoặc khám phá khóa học khác.`
                    : 'Hãy xem lại nội dung hoặc khám phá khóa học khác.'
                  : 'Các bài học tiếp theo có thể nằm ở module khác. Quay lại danh sách module để tiếp tục.'}
              </p>
              <CourseLearningNav
                courseId={courseId}
                moduleId={lesson.module_id}
                sticky={false}
                className="lesson-complete-card__nav"
              />
            </div>
          </CardBody>
        </Card>
      )}

      {/* Navigation: bai truoc / bai tiep */}
      <div className="lesson-navigation">
        {previousLesson ? (
          <Button
            variant="outline"
            onClick={() => navigate(
              `/dashboard/courses/${courseId}/lessons/${previousLesson.id}`
            )}
          >
            ← {previousLesson.title || 'Bài trước'}
          </Button>
        ) : (
          <div />
        )}

        {nextLesson ? (
          <Button
            disabled={nextLesson.is_locked}
            onClick={() => navigate(
              `/dashboard/courses/${courseId}/lessons/${nextLesson.id}`
            )}
          >
            {nextLesson.title || 'Bài tiếp'} →
            {nextLesson.is_locked && ' (Khóa)'}
          </Button>
        ) : null}
      </div>

      {!lesson.completion_status?.is_completed && (
        <div className="lesson-navigation">
          <Button
            variant="primary"
            loading={completing}
            disabled={completing}
            onClick={handleCompleteLesson}
          >
            Đánh dấu đã học xong
          </Button>
        </div>
      )}

      {!showCompletionPanel && (
        <CourseLearningNav courseId={courseId} moduleId={lesson.module_id} />
      )}

      {/* AI Chat Widget (Vị trí 2 Dual-UI) */}
      <ChatWidget
        contextMeta={{
          lessonId: lesson?.id,
          lessonTitle: lesson?.title,
          moduleTitle: lesson?.module_title,
          suggestions: [
            `Tóm tắt nhanh bài "${lesson?.title || 'này'}"`,
            `Cho ví dụ thực tế cho kiến thức trong "${lesson?.title || 'bài này'}"`,
            'Tạo 3 câu hỏi ôn tập ngắn cho tôi',
          ],
        }}
      />
    </div>
  )
}

/** Chỉ dùng navigation khi có id hợp lệ (tránh /lessons/null). */
const getNavLesson = (navLesson) => {
  if (!navLesson?.id || navLesson.id === 'null' || navLesson.id === 'undefined') {
    return null
  }
  return navLesson
}

const contentTypeLabel = (type) => {
  if (type === 'text') return 'Văn bản'
  if (type === 'video') return 'Video'
  return 'Mixed'
}
const attachmentTypeLabel = (type) => {
  if (type === 'pdf') return 'PDF'
  if (type === 'code') return 'Code'
  return 'File'
}

const getYoutubeEmbedUrl = (url = '') => {
  if (!url) return ''
  if (url.includes('youtube.com/embed/')) return url
  const match = url.match(/(?:youtube\.com\/watch\?v=|youtu\.be\/)([\w-]{6,})/)
  return match?.[1] ? `https://www.youtube.com/embed/${match[1]}` : ''
}

export default LessonPage
