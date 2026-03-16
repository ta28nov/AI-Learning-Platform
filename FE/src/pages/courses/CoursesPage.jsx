import { useState, useEffect, useCallback } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { motion } from 'framer-motion'
import toast from 'react-hot-toast'
import { useCourseStore } from '@stores/courseStore'
import Button from '@components/ui/Button'
import './CoursesPage.css'

/**
 * CoursesPage - Trang danh sách và tìm kiếm khóa học
 * Route: /dashboard/courses
 * API: GET /courses/search (courseStore.searchCourses)
 * Hiển thị grid card, filter category/level, search keyword, pagination skip/limit
 */
const CoursesPage = () => {
  const navigate = useNavigate()
  const [searchParams, setSearchParams] = useSearchParams()

  const {
    courses, isLoading, pagination, filters,
    searchCourses, setFilters, setPage
  } = useCourseStore()

  const [searchInput, setSearchInput] = useState(filters.keyword || '')

  // Lấy dữ liệu lần đầu và khi filter thay đổi
  useEffect(() => {
    searchCourses().catch(() => {
      toast.error('Không thể tải danh sách khóa học')
    })
  }, [filters.keyword, filters.category, filters.level, filters.sort_by, pagination.skip])

  // Xử lý tìm kiếm khi nhấn Enter hoặc click nút
  const handleSearch = useCallback(() => {
    setFilters({ keyword: searchInput })
  }, [searchInput, setFilters])

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') handleSearch()
  }

  // Xử lý chuyển trang
  const totalPages = Math.ceil(pagination.total / pagination.limit)
  const currentPage = Math.floor(pagination.skip / pagination.limit) + 1

  const goToPage = (page) => {
    const newSkip = (page - 1) * pagination.limit
    setPage(newSkip)
  }

  // Tính thời gian hiển thị
  const formatDuration = (minutes) => {
    if (!minutes) return ''
    const hours = Math.floor(minutes / 60)
    const mins = minutes % 60
    if (hours > 0) return `${hours}h${mins > 0 ? ` ${mins}ph` : ''}`
    return `${mins} phút`
  }

  // Animation
  const fadeUp = { hidden: { opacity: 0, y: 20 }, visible: { opacity: 1, y: 0 } }
  const stagger = { visible: { transition: { staggerChildren: 0.06 } } }

  return (
    <div className="courses-page">
      {/* Tiêu đề và thanh tìm kiếm */}
      <motion.div
        className="courses-header"
        initial="hidden"
        animate="visible"
        variants={fadeUp}
        transition={{ duration: 0.3 }}
      >
        <h1 className="courses-header__title">Khám phá khóa học</h1>
        <p className="courses-header__sub">
          Tìm kiếm và đăng ký các khóa học phù hợp với trình độ của bạn
        </p>

        {/* Thanh tìm kiếm */}
        <div className="courses-search">
          <input
            type="text"
            className="courses-search__input"
            placeholder="Tìm kiếm theo tên khóa học, chủ đề..."
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
            onKeyDown={handleKeyDown}
          />
          <Button variant="primary" size="sm" onClick={handleSearch}>
            Tìm kiếm
          </Button>
        </div>
      </motion.div>

      {/* Bộ lọc */}
      <motion.div
        className="courses-filters"
        initial="hidden"
        animate="visible"
        variants={fadeUp}
        transition={{ duration: 0.3, delay: 0.1 }}
      >
        <div className="courses-filters__group">
          <label className="courses-filters__label">Danh mục</label>
          <select
            className="courses-filters__select"
            value={filters.category}
            onChange={(e) => setFilters({ category: e.target.value })}
          >
            <option value="">Tất cả danh mục</option>
            <option value="programming">Lập trình</option>
            <option value="data_science">Khoa học dữ liệu</option>
            <option value="ai_ml">AI / Machine Learning</option>
            <option value="web_dev">Phát triển Web</option>
            <option value="mobile">Phát triển Mobile</option>
            <option value="database">Cơ sở dữ liệu</option>
            <option value="devops">DevOps</option>
            <option value="other">Khác</option>
          </select>
        </div>

        <div className="courses-filters__group">
          <label className="courses-filters__label">Trình độ</label>
          <select
            className="courses-filters__select"
            value={filters.level}
            onChange={(e) => setFilters({ level: e.target.value })}
          >
            <option value="">Tất cả trình độ</option>
            <option value="beginner">Cơ bản</option>
            <option value="intermediate">Trung cấp</option>
            <option value="advanced">Nâng cao</option>
          </select>
        </div>

        <div className="courses-filters__group">
          <label className="courses-filters__label">Sắp xếp</label>
          <select
            className="courses-filters__select"
            value={filters.sort_by}
            onChange={(e) => setFilters({ sort_by: e.target.value })}
          >
            <option value="newest">Mới nhất</option>
            <option value="popular">Phổ biến nhất</option>
            <option value="rating">Đánh giá cao</option>
          </select>
        </div>
      </motion.div>

      {/* Thông tin kết quả */}
      {!isLoading && (
        <div className="courses-result-info">
          <span>
            {pagination.total > 0
              ? `Tìm thấy ${pagination.total} khóa học`
              : 'Không tìm thấy khóa học nào'
            }
          </span>
          {filters.keyword && (
            <span className="courses-result-info__keyword">
              cho "{filters.keyword}"
              <button
                className="courses-result-info__clear"
                onClick={() => { setSearchInput(''); setFilters({ keyword: '' }) }}
              >
                Xóa
              </button>
            </span>
          )}
        </div>
      )}

      {/* Trạng thái đang tải */}
      {isLoading && (
        <div className="courses-grid">
          {[1, 2, 3, 4, 5, 6].map(i => (
            <div key={i} className="course-skeleton">
              <div className="course-skeleton__img" />
              <div className="course-skeleton__body">
                <div className="course-skeleton__line course-skeleton__line--title" />
                <div className="course-skeleton__line" />
                <div className="course-skeleton__line course-skeleton__line--short" />
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Danh sách khóa học */}
      {!isLoading && courses.length > 0 && (
        <motion.div
          className="courses-grid"
          initial="hidden"
          animate="visible"
          variants={stagger}
        >
          {courses.map((course) => (
            <motion.div
              key={course.id}
              className="course-card"
              variants={fadeUp}
              onClick={() => navigate(`/dashboard/courses/${course.id}`)}
            >
              {/* Ảnh đại diện */}
              <div className="course-card__img-wrap">
                {course.thumbnail_url ? (
                  <img src={course.thumbnail_url} alt={course.title} className="course-card__img" />
                ) : (
                  <div className="course-card__img-placeholder">
                    <span>{course.category === 'programming' ? '💻' : course.category === 'ai_ml' ? '🤖' : '📚'}</span>
                  </div>
                )}
                {course.is_enrolled && (
                  <span className="course-card__enrolled-badge">Đã đăng ký</span>
                )}
              </div>

              {/* Nội dung card */}
              <div className="course-card__body">
                <div className="course-card__badges">
                  {course.category && (
                    <span className="course-card__badge course-card__badge--category">
                      {course.category}
                    </span>
                  )}
                  {course.level && (
                    <span className={`course-card__badge course-card__badge--${course.level}`}>
                      {course.level === 'beginner' ? 'Cơ bản'
                        : course.level === 'intermediate' ? 'Trung cấp'
                        : 'Nâng cao'}
                    </span>
                  )}
                </div>

                <h3 className="course-card__title">{course.title}</h3>

                {course.description && (
                  <p className="course-card__desc">
                    {course.description.length > 100
                      ? course.description.substring(0, 100) + '...'
                      : course.description}
                  </p>
                )}

                {/* Thông tin phụ */}
                <div className="course-card__meta">
                  {course.total_modules != null && (
                    <span>{course.total_modules} modules</span>
                  )}
                  {course.total_lessons != null && (
                    <span>{course.total_lessons} bài học</span>
                  )}
                  {course.total_duration_minutes != null && (
                    <span>{formatDuration(course.total_duration_minutes)}</span>
                  )}
                </div>

                {/* Footer: giảng viên + số học viên */}
                <div className="course-card__footer">
                  <div className="course-card__instructor">
                    {course.instructor_avatar ? (
                      <img src={course.instructor_avatar} alt="" className="course-card__instructor-avatar" />
                    ) : (
                      <div className="course-card__instructor-avatar-placeholder">
                        {(course.instructor_name || 'G').charAt(0)}
                      </div>
                    )}
                    <span className="course-card__instructor-name">
                      {course.instructor_name || 'Giảng viên'}
                    </span>
                  </div>
                  {course.enrollment_count != null && (
                    <span className="course-card__students">
                      {course.enrollment_count} học viên
                    </span>
                  )}
                  {course.avg_rating != null && course.avg_rating > 0 && (
                    <span className="course-card__rating">
                      ⭐ {course.avg_rating.toFixed(1)}
                    </span>
                  )}
                </div>
              </div>
            </motion.div>
          ))}
        </motion.div>
      )}

      {/* Trạng thái rỗng */}
      {!isLoading && courses.length === 0 && (
        <div className="courses-empty">
          <span className="courses-empty__icon">📚</span>
          <h3>Không tìm thấy khóa học</h3>
          <p>Thử thay đổi bộ lọc hoặc từ khóa tìm kiếm</p>
          <Button
            variant="outline"
            onClick={() => {
              setSearchInput('')
              setFilters({ keyword: '', category: '', level: '', sort_by: 'newest' })
            }}
          >
            Xóa bộ lọc
          </Button>
        </div>
      )}

      {/* Phân trang */}
      {!isLoading && totalPages > 1 && (
        <div className="courses-pagination">
          <button
            className="courses-pagination__btn"
            disabled={currentPage <= 1}
            onClick={() => goToPage(currentPage - 1)}
          >
            Trước
          </button>

          {Array.from({ length: Math.min(totalPages, 5) }, (_, i) => {
            // Hiển thị tối đa 5 nút trang
            let pageNum
            if (totalPages <= 5) {
              pageNum = i + 1
            } else if (currentPage <= 3) {
              pageNum = i + 1
            } else if (currentPage >= totalPages - 2) {
              pageNum = totalPages - 4 + i
            } else {
              pageNum = currentPage - 2 + i
            }
            return (
              <button
                key={pageNum}
                className={`courses-pagination__btn ${currentPage === pageNum ? 'courses-pagination__btn--active' : ''}`}
                onClick={() => goToPage(pageNum)}
              >
                {pageNum}
              </button>
            )
          })}

          <button
            className="courses-pagination__btn"
            disabled={currentPage >= totalPages}
            onClick={() => goToPage(currentPage + 1)}
          >
            Sau
          </button>
        </div>
      )}
    </div>
  )
}

export default CoursesPage