import { useState, useEffect } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { motion, AnimatePresence, useReducedMotion } from 'framer-motion'
import toast from 'react-hot-toast'
import courseService from '@services/courseService'
import enrollmentService from '@services/enrollmentService'
import progressService from '@services/progressService'
import Button from '@components/ui/Button'
import StateView from '@components/ui/StateView'
import ChatWidget from '@components/chat/ChatWidget'
import ClassLearningBanner from '@components/classes/ClassLearningBanner'
import { fadeUp, staggerEditorial, inView } from '@/styles/motion'
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
  const [courseProgress, setCourseProgress] = useState(null)
  const [progressLoading, setProgressLoading] = useState(false)
  const shouldReduceMotion = useReducedMotion()

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

  const enrolled = course?.enrollment_info?.is_enrolled

  useEffect(() => {
    if (!enrolled || !courseId) {
      setCourseProgress(null)
      return
    }
    const loadProgress = async () => {
      try {
        setProgressLoading(true)
        const data = await progressService.getCourseProgress(courseId)
        setCourseProgress(data)
      } catch {
        setCourseProgress(null)
      } finally {
        setProgressLoading(false)
      }
    }
    loadProgress()
  }, [enrolled, courseId])

  // Xử lý đăng ký khóa học
  const handleEnroll = async () => {
    try {
      setEnrolling(true)
      const result = await enrollmentService.enrollCourse(courseId)
      toast.success(result?.message || 'Đăng ký thành công!')
      // Cập nhật lại trạng thái enrollment trong state
      setCourse((prev) => ({
        ...prev,
        enrollment_info: {
          ...prev?.enrollment_info,
          is_enrolled: true,
          enrollment_id: result?.id,
          progress_percent: 0,
          can_access_content: true,
        },
      }))
      try {
        const prog = await progressService.getCourseProgress(courseId)
        setCourseProgress(prog)
      } catch {
        /* progress record có thể chưa tạo ngay */
      }
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
          <StateView
            type="empty"
            title="Không tìm thấy khóa học"
            message="Khóa học này không tồn tại hoặc đã bị xóa."
            actionLabel="Quay lại danh sách"
            onAction={() => navigate('/dashboard/courses')}
          />
        </div>
      </div>
    )
  }

  const stats = course.course_statistics

  const lessonStatusLabel = (status) => {
    if (status === 'completed') return 'Hoàn thành'
    if (status === 'in-progress') return 'Đang học'
    return 'Chưa bắt đầu'
  }

  return (
    <div className="cd-page">
      {enrolled && <ClassLearningBanner />}
      {/* Hero section - thông tin chính */}
      <motion.div className="cd-hero" variants={fadeUp} initial={shouldReduceMotion ? false : 'hidden'} animate="show">
        {course.thumbnail_url && (
          <img src={course.thumbnail_url} alt={course.title} className="cd-hero__bg-img" />
        )}
        <div className="cd-hero__overlay" />
        <div className="cd-hero__content">
          <div className="cd-hero__badges">
            {course.category && <span className="cd-badge cd-badge--cat">{course.category}</span>}
            {course.level && (
              <span className={`cd-badge cd-badge--${course.level?.toLowerCase()}`}>
                {course.level === 'Beginner' ? 'Cơ bản' : course.level === 'Intermediate' ? 'Trung cấp' : course.level === 'Advanced' ? 'Nâng cao' : course.level}
              </span>
            )}
            {course.language && <span className="cd-badge">{course.language === 'vi' ? 'Tiếng Việt' : 'English'}</span>}
          </div>
          <h1 className="cd-hero__title">{course.title}</h1>
          {course.description && <p className="cd-hero__desc">{course.description}</p>}

          {/* Thống kê nhanh */}
          <div className="cd-hero__stats">
            {stats?.total_modules != null && <span>{stats.total_modules} modules</span>}
            {stats?.total_lessons != null && <span>{stats.total_lessons} bài học</span>}
            {stats?.total_duration_minutes != null && <span>{formatDuration(stats.total_duration_minutes)}</span>}
            {stats?.enrollment_count != null && <span>{stats.enrollment_count} học viên</span>}
            {stats?.avg_rating != null && stats.avg_rating > 0 && (
              <span>★ {Number(stats.avg_rating).toFixed(1)}</span>
            )}
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
            {course.preview_video_url && <Button variant="outline" size="lg" onClick={() => window.open(course.preview_video_url, '_blank')}>Xem video giới thiệu</Button>}
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
          {enrolled && (
            <motion.div className="cd-section cd-progress-detail" variants={fadeUp} {...(shouldReduceMotion ? {} : inView())}>
              <h2 className="cd-section__title">Tiến độ học tập</h2>
              {progressLoading && (
                <StateView type="loading" message="Đang tải tiến độ chi tiết…" />
              )}
              {!progressLoading && courseProgress && (
                <>
                  <div className="cd-progress-stats">
                    <div className="cd-progress-stat">
                      <span className="cd-progress-stat__val">{Math.round(courseProgress.overall_progress)}%</span>
                      <span className="cd-progress-stat__lbl">Tổng tiến độ</span>
                    </div>
                    <div className="cd-progress-stat">
                      <span className="cd-progress-stat__val">{courseProgress.study_streak_days}</span>
                      <span className="cd-progress-stat__lbl">Ngày liên tiếp</span>
                    </div>
                    <div className="cd-progress-stat">
                      <span className="cd-progress-stat__val">{Math.round(courseProgress.avg_quiz_score)}%</span>
                      <span className="cd-progress-stat__lbl">Điểm quiz TB</span>
                    </div>
                    <div className="cd-progress-stat">
                      <span className="cd-progress-stat__val">{Number(courseProgress.total_hours_spent || 0).toFixed(1)}h</span>
                      <span className="cd-progress-stat__lbl">Đã học</span>
                    </div>
                  </div>
                  {courseProgress.modules?.length > 0 && (
                    <div className="cd-progress-modules">
                      {courseProgress.modules.map((mod) => (
                        <motion.div key={mod.id} className="cd-progress-mod">
                          <div className="cd-progress-mod__head">
                            <span className="cd-progress-mod__title">{mod.title}</span>
                            <span className="cd-progress-mod__pct">{Math.round(mod.progress)}%</span>
                          </div>
                          <div className="cd-progress-mod__bar">
                            <div className="cd-progress-mod__fill" style={{ width: `${mod.progress}%` }} />
                          </div>
                          {mod.lessons?.length > 0 && (
                            <ul className="cd-progress-lessons">
                              {mod.lessons.map((les) => (
                                <li key={les.id} className={`cd-progress-lesson cd-progress-lesson--${les.status}`}>
                                  <span>{les.title}</span>
                                  <span className="cd-progress-lesson__status">{lessonStatusLabel(les.status)}</span>
                                </li>
                              ))}
                            </ul>
                          )}
                        </motion.div>
                      ))}
                    </div>
                  )}
                </>
              )}
              {!progressLoading && !courseProgress && (
                <StateView
                  type="empty"
                  message="Chưa có dữ liệu tiến độ chi tiết. Bắt đầu bài học đầu tiên để cập nhật."
                />
              )}
            </motion.div>
          )}

          {/* Mục tiêu học tập */}
          {course.learning_outcomes?.length > 0 && (
            <motion.div className="cd-section" variants={fadeUp} {...(shouldReduceMotion ? {} : inView())}>
              <h2 className="cd-section__title">Bạn sẽ học được gì</h2>
              <div className="cd-outcomes">
                {course.learning_outcomes.map((outcome, i) => (
                  <div key={i} className="cd-outcome">
                    <span className="cd-outcome__check"><CheckIcon /></span>
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
            <motion.div className="cd-section" variants={fadeUp} {...(shouldReduceMotion ? {} : inView({ amount: 0.25 }))}>
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
            <motion.div className="cd-section" variants={fadeUp} {...(shouldReduceMotion ? {} : inView({ amount: 0.2 }))}>
              <h2 className="cd-section__title">
                Chương trình học
                <span className="cd-section__count">{course.modules.length} modules</span>
              </h2>
              <div className="cd-modules">
                {course.modules.map((mod) => (
                  <div key={mod.id} className={`cd-module ${expandedModules[mod.id] ? 'cd-module--open' : ''}`}>
                    {/* Header module - click để toggle */}
                    <button className="cd-module__header" onClick={() => toggleModule(mod.id)}>
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
                    </button>

                    {/* Danh sách bài học bên trong (chỉ hiện khi mở) */}
                    <AnimatePresence initial={false}>
                    {expandedModules[mod.id] && (
                      <motion.div
                        className="cd-module__lessons"
                        initial={shouldReduceMotion ? false : { height: 0, opacity: 0 }}
                        animate={shouldReduceMotion ? {} : { height: 'auto', opacity: 1 }}
                        exit={shouldReduceMotion ? {} : { height: 0, opacity: 0 }}
                        transition={{ duration: 0.24 }}
                      >
                        {mod.description && (
                          <p className="cd-module__desc">{mod.description}</p>
                        )}
                        {(mod.lessons || []).map((lesson) => (
                          <div
                            key={lesson.id}
                            className={`cd-lesson ${lesson.is_completed ? 'cd-lesson--done' : ''}`}
                          >
                            <span className="cd-lesson__status">
                              {lesson.is_completed ? <DoneIcon /> : <TodoIcon />}
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
                      </motion.div>
                    )}
                    </AnimatePresence>
                  </div>
                ))}
              </div>
            </motion.div>
          )}
        </div>

        {/* Sidebar - thông tin giảng viên */}
        <div className="cd-sidebar">
          <motion.div className="cd-sticky-enroll" variants={fadeUp} initial={shouldReduceMotion ? false : 'hidden'} animate="show">
            <h3 className="cd-sticky-enroll__title">{enrolled ? 'Bạn đã đăng ký khóa học này' : 'Sẵn sàng bắt đầu?'}</h3>
            <p className="cd-sticky-enroll__meta">{stats?.total_lessons || 0} bài học · {formatDuration(stats?.total_duration_minutes || 0)}</p>
            {enrolled ? (
              <Button variant="primary" className="cd-sticky-enroll__btn" onClick={() => navigate(`/dashboard/courses/${courseId}/modules`)}>
                Tiếp tục học
              </Button>
            ) : (
              <Button variant="primary" className="cd-sticky-enroll__btn" loading={enrolling} disabled={enrolling} onClick={handleEnroll}>
                Đăng ký khóa học
              </Button>
            )}
          </motion.div>
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

      {enrolled && (
        <ChatWidget
          contextType="general"
          subtitle="Hỏi AI về khóa học & tiến độ của bạn"
          suggestions={[
            'Tóm tắt nội dung chính của khóa học này',
            'Tôi nên bắt đầu từ module nào?',
            'Giải thích mục tiêu học tập của khóa',
          ]}
        />
      )}
    </div>
  )
}

const CheckIcon = () => <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="m20 6-11 11-5-5"/></svg>
const DoneIcon = () => <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10"/><path d="m9 12 2 2 4-4"/></svg>
const TodoIcon = () => <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10"/></svg>

export default CourseDetailPage