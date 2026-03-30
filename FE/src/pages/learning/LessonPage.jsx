import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import learningService from '@services/learningService'
import Button from '@components/ui/Button'
import Card, { CardHeader, CardBody } from '@components/ui/Card'
import ChatWidget from '@components/chat/ChatWidget'
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
  const [lesson, setLesson] = useState(null)
  const [loading, setLoading] = useState(true)

  // Lấy nội dung bài học khi mount hoặc khi lessonId thay đổi
  useEffect(() => {
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
  }, [courseId, lessonId])

  if (loading) return <div className="loading-spinner">Đang tải bài học...</div>
  if (!lesson) return <div className="empty-state">Không tìm thấy bài học</div>

  return (
    <div className="lesson-page">
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
              onClick={() => navigate(`/dashboard/courses/${courseId}/modules`)}
            >
              {lesson.module_title}
            </span>
          </>
        )}
        <span className="breadcrumb-sep">/</span>
        <span className="breadcrumb-current">{lesson.title}</span>
      </div>

      {/* Header */}
      <div className="lesson-header">
        <h1>{lesson.title}</h1>
        <div className="lesson-meta">
          <span>Bài {lesson.order}</span>
          <span>{lesson.duration_minutes} phút</span>
          {lesson.content_type && (
            <span>
              {lesson.content_type === 'text' ? '📝' : lesson.content_type === 'video' ? '🎥' : '📝🎥'}
            </span>
          )}
          {lesson.completion_status?.is_completed && (
            <span className="completed-badge">✓ Đã hoàn thành</span>
          )}
        </div>
      </div>

      {/* Video player */}
      {lesson.video_info && lesson.video_info.url && (
        <div className="lesson-video">
          <video
            controls
            poster={lesson.video_info.thumbnail_url || ''}
            className="video-player"
          >
            <source src={lesson.video_info.url} type="video/mp4" />
            Trình duyệt không hỗ trợ video.
          </video>
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
                <li key={idx}>{obj}</li>
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
                  key={idx}
                  href={file.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="attachment-item"
                >
                  <span className="attachment-icon">
                    {file.file_type === 'pdf' ? '📄' : file.file_type === 'code' ? '💻' : '📎'}
                  </span>
                  <span className="attachment-name">{file.filename}</span>
                  {file.size_mb && <span className="attachment-size">{file.size_mb} MB</span>}
                </a>
              ))}
            </div>
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

      {/* Navigation: bai truoc / bai tiep */}
      <div className="lesson-navigation">
        {lesson.navigation?.previous_lesson ? (
          <Button
            variant="outline"
            onClick={() => navigate(
              `/dashboard/courses/${courseId}/lessons/${lesson.navigation.previous_lesson.id}`
            )}
          >
            ← {lesson.navigation.previous_lesson.title}
          </Button>
        ) : (
          <div />
        )}

        {lesson.navigation?.next_lesson && (
          <Button
            disabled={lesson.navigation.next_lesson.is_locked}
            onClick={() => navigate(
              `/dashboard/courses/${courseId}/lessons/${lesson.navigation.next_lesson.id}`
            )}
          >
            {lesson.navigation.next_lesson.title} →
            {lesson.navigation.next_lesson.is_locked && ' 🔒'}
          </Button>
        )}
      </div>

      {/* AI Chat Widget (Vị trí 2 Dual-UI) */}
      <ChatWidget />
    </div>
  )
}

export default LessonPage
