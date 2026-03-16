import { useState, useEffect } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import toast from 'react-hot-toast'
import courseService from '@services/courseService'
import enrollmentService from '@services/enrollmentService'
import Button from '@components/ui/Button'
import './CourseDetailPage.css'

/**
 * CourseDetailPage - Trang chi tiết khóa học
 * Route: /dashboard/courses/:courseId
 * API: GET /courses/{courseId} -> CourseDetailResponse
 *      POST /enrollments -> đăng ký khóa học
 * Hiển thị: thông tin chi tiết, modules accordion, learning outcomes,
 *           thông tin giảng viên, nút đăng ký/tiếp tục học
 */
const CourseDetailPage = () => {
  const { courseId } = useParams()
  const navigate = useNavigate()
  const [course, setCourse] = useState(null)
  const [loading, setLoading] = useState(true)
  const [enrolling, setEnrolling] = useState(false)
  // Theo dõi module nào đang mở trong accordion
  const [expandedModules, setExpandedModules] = useState({})

  // Lấy chi tiết khóa học khi mount
  useEffect(() => {
    const fetchCourse = async () => {
      try {
        setLoading(true)
        const data = await courseService.getCourseDetail(courseId)
        setCourse(data)
      } catch (error) {
        toast.error('Không thể tải thông tin khóa học')
      } finally {
        setLoading(false)
      }
    }
    if (courseId) fetchCourse()
  }, [courseId])

  // Xử lý đăng ký khóa học
  const handleEnroll = async () => {
    try {
      setEnrolling(true)
      const result = await enrollmentService.enrollCourse(courseId)
      toast.success(result?.message || 'Đăng ký thành công!')
      // Cập nhật lại trạng thái enrollment trong state
      setCourse(prev => ({
        ...prev,
        enrollment_info: {
          ...prev?.enrollment_info,
          is_enrolled: true,
          enrollment_id: result?.enrollment_id,
          progress_percent: 0,
          can_access_content: true
        }
      }))
    } catch (error) {
      toast.error(error?.message || 'Không thể đăng ký khóa học')
    } finally {
      setEnrolling(false)
    }
  }

  // Toggle accordion module
  const toggleModule = (moduleId) => {
    setExpandedModules(prev => ({
      ...prev,
      [moduleId]: !prev[moduleId]
    }))
  }

  // Hiển thị thời lượng dạng dễ đọc
  const formatDuration = (minutes) => {
    if (!minutes) return ''
    const hours = Math.floor(minutes / 60)
    const mins = minutes % 60
    if (hours > 0) return `${hours} giờ ${mins > 0 ? `${mins} phút` : ''}`
    return `${mins} phút`
  }

  // Biểu tượng theo loại nội dung
  const contentTypeLabel = (type) => {
    const map = { text: '📝 Văn bản', video: '🎥 Video', mixed: '📝🎥 Hỗn hợp', audio: '🎵 Audio', code: '💻 Code' }
    return map[type] || type
  }

  const fadeUp = { hidden: { opacity: 0, y: 20 }, visible: { opacity: 1, y: 0 } }

  // Loading skeleton
  if (loading) {
    return (
      <div className="cd-page">
        <div className="cd-skeleton__hero" />
        <div className="cd-skeleton__body">
          <div className="cd-skeleton__block" />
          <div className="cd-skeleton__block cd-skeleton__block--sm" />
        </div>
      </div>
    )
  }

  if (!course) {
    return (
      <div className="cd-page">
        <div className="courses-empty">
          <span className="courses-empty__icon">📭</span>
          <h3>Không tìm thấy khóa học</h3>
          <p>Khóa học này không tồn tại hoặc đã bị xóa</p>
          <Button variant="outline" onClick={() => navigate('/dashboard/courses')}>
            Quay lại danh sách
          </Button>
        </div>
      </div>
    )
  }

  const enrolled = course.enrollment_info?.is_enrolled
  const stats = course.course_statistics

  return (
    <div className="cd-page">
      {/* Hero section - thông tin chính */}
      <motion.div
        className="cd-hero"
        initial="hidden"
        animate="visible"
        variants={fadeUp}
        transition={{ duration: 0.4 }}
      >
        {course.thumbnail_url && (
          <img src={course.thumbnail_url} alt={course.title} className="cd-hero__bg-img" />
        )}
        <div className="cd-hero__overlay" />
        <div className="cd-hero__content">
          <div className="cd-hero__badges">
            {course.category && <span className="cd-badge cd-badge--cat">{course.category}</span>}
            {course.level && (
              <span className={`cd-badge cd-badge--${course.level}`}>
                {course.level === 'beginner' ? 'Cơ bản' : course.level === 'intermediate' ? 'Trung cấp' : 'Nâng cao'}
              </span>
            )}
            {course.language && <span className="cd-badge">{course.language === 'vi' ? '🇻🇳 Tiếng Việt' : '🇬🇧 English'}</span>}
          </div>
          <h1 className="cd-hero__title">{course.title}</h1>
          {course.description && <p className="cd-hero__desc">{course.description}</p>}

          {/* Thống kê nhanh */}
          <div className="cd-hero__stats">
            {stats?.total_modules != null && <span>{stats.total_modules} modules</span>}
            {stats?.total_lessons != null && <span>{stats.total_lessons} bài học</span>}
            {stats?.total_duration_minutes != null && <span>{formatDuration(stats.total_duration_minutes)}</span>}
            {stats?.enrollment_count != null && <span>{stats.enrollment_count} học viên</span>}
          </div>

          {/* Nút hành động chính */}
          <div className="cd-hero__actions">
            {enrolled ? (
              <Button
                variant="primary"
                size="lg"
                onClick={() => navigate(`/dashboard/courses/${courseId}/modules`)}
              >
                Tiếp tục học
              </Button>
            ) : (
              <Button
                variant="primary"
                size="lg"
                loading={enrolling}
                disabled={enrolling}
                onClick={handleEnroll}
              >
                Đăng ký khóa học
              </Button>
            )}
            {course.preview_video_url && (
              <Button
                variant="outline"
                size="lg"
                onClick={() => window.open(course.preview_video_url, '_blank')}
              >
                🎥 Xem video giới thiệu
              </Button>
            )}
          </div>

          {/* Thanh tiến độ nếu đã đăng ký */}
          {enrolled && course.enrollment_info?.progress_percent != null && (
            <div className="cd-hero__progress">
              <div className="cd-hero__progress-bar">
                <div
                  className="cd-hero__progress-fill"
                  style={{ width: `${course.enrollment_info.progress_percent}%` }}
                />
              </div>
              <span className="cd-hero__progress-text">
                {Math.round(course.enrollment_info.progress_percent)}% hoàn thành
              </span>
            </div>
          )}
        </div>
      </motion.div>

      <div className="cd-body">
        <div className="cd-main">
          {/* Mục tiêu học tập */}
          {course.learning_outcomes?.length > 0 && (
            <motion.div className="cd-section" initial="hidden" animate="visible" variants={fadeUp} transition={{ delay: 0.1 }}>
              <h2 className="cd-section__title">Bạn sẽ học được gì</h2>
              <div className="cd-outcomes">
                {course.learning_outcomes.map((outcome, i) => (
                  <div key={i} className="cd-outcome">
                    <span className="cd-outcome__check">✓</span>
                    <div>
                      <span className="cd-outcome__text">{outcome.description}</span>
                      {outcome.skill_tag && (
                        <span className="cd-outcome__skill">{outcome.skill_tag}</span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </motion.div>
          )}

          {/* Yêu cầu tiên quyết */}
          {course.prerequisites?.length > 0 && (
            <motion.div className="cd-section" initial="hidden" animate="visible" variants={fadeUp} transition={{ delay: 0.15 }}>
              <h2 className="cd-section__title">Yêu cầu tiên quyết</h2>
              <ul className="cd-prereqs">
                {course.prerequisites.map((prereq, i) => (
                  <li key={i}>{prereq}</li>
                ))}
              </ul>
            </motion.div>
          )}

          {/* Chương trình học - Modules Accordion */}
          {course.modules?.length > 0 && (
            <motion.div className="cd-section" initial="hidden" animate="visible" variants={fadeUp} transition={{ delay: 0.2 }}>
              <h2 className="cd-section__title">
                Chương trình học
                <span className="cd-section__count">{course.modules.length} modules</span>
              </h2>
              <div className="cd-modules">
                {course.modules.map((mod) => (
                  <div key={mod.id} className={`cd-module ${expandedModules[mod.id] ? 'cd-module--open' : ''}`}>
                    {/* Header module - click để toggle */}
                    <div className="cd-module__header" onClick={() => toggleModule(mod.id)}>
                      <div className="cd-module__info">
                        <h3 className="cd-module__title">{mod.title}</h3>
                        <div className="cd-module__meta">
                          {mod.difficulty && (
                            <span className={`cd-badge cd-badge--sm cd-badge--${mod.difficulty}`}>
                              {mod.difficulty}
                            </span>
                          )}
                          {mod.lessons?.length > 0 && <span>{mod.lessons.length} bài học</span>}
                          {mod.estimated_hours && <span>~{mod.estimated_hours}h</span>}
                        </div>
                      </div>
                      <span className="cd-module__arrow">{expandedModules[mod.id] ? '▲' : '▼'}</span>
                    </div>

                    {/* Danh sách bài học bên trong (chỉ hiện khi mở) */}
                    {expandedModules[mod.id] && (
                      <div className="cd-module__lessons">
                        {mod.description && (
                          <p className="cd-module__desc">{mod.description}</p>
                        )}
                        {(mod.lessons || []).map((lesson) => (
                          <div
                            key={lesson.id}
                            className={`cd-lesson ${lesson.is_completed ? 'cd-lesson--done' : ''}`}
                          >
                            <span className="cd-lesson__status">
                              {lesson.is_completed ? '✅' : '⬜'}
                            </span>
                            <div className="cd-lesson__info">
                              <span className="cd-lesson__title">{lesson.title}</span>
                              <span className="cd-lesson__meta">
                                {contentTypeLabel(lesson.content_type)}
                                {lesson.duration_minutes && ` · ${lesson.duration_minutes} phút`}
                              </span>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </motion.div>
          )}
        </div>

        {/* Sidebar - thông tin giảng viên */}
        <div className="cd-sidebar">
          {course.owner_info && (
            <div className="cd-instructor-card">
              <h3 className="cd-instructor-card__label">Giảng viên</h3>
              <div className="cd-instructor-card__profile">
                {course.owner_info.avatar_url ? (
                  <img src={course.owner_info.avatar_url} alt="" className="cd-instructor-card__avatar" />
                ) : (
                  <div className="cd-instructor-card__avatar-ph">
                    {(course.owner_info.name || 'G').charAt(0)}
                  </div>
                )}
                <div>
                  <span className="cd-instructor-card__name">{course.owner_info.name}</span>
                  {course.owner_info.experience_years && (
                    <span className="cd-instructor-card__exp">
                      {course.owner_info.experience_years} năm kinh nghiệm
                    </span>
                  )}
                </div>
              </div>
              {course.owner_info.bio && (
                <p className="cd-instructor-card__bio">{course.owner_info.bio}</p>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default CourseDetailPage