import { useState, useEffect, useCallback } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { motion, useReducedMotion } from 'framer-motion'
import toast from 'react-hot-toast'
import { useCourseStore } from '@stores/courseStore'
import Button from '@components/ui/Button'
import StateView from '@components/ui/StateView'
import appLogger from '@utils/logger'
import { fadeUp, staggerEditorial, inView } from '@/styles/motion'
import './CoursesPage.css'

/**
 * CoursesPage - Trang danh sách và tìm kiếm khóa học
 * Route: /dashboard/courses
 * API: GET /courses/search (courseStore.searchCourses)
 * Hiển thị grid card, filter category/level, search keyword, pagination skip/limit
 */
const CoursesPage = () => {
  const navigate = useNavigate()
  const [, setSearchParams] = useSearchParams()
  const shouldReduceMotion = useReducedMotion()

  const {
    courses, isLoading, pagination, filters,
    searchCourses, setFilters, setPage
  } = useCourseStore()

  const [searchInput, setSearchInput] = useState(filters.keyword || '')
  const [pageError, setPageError] = useState('')

  // Lấy dữ liệu lần đầu và khi filter thay đổi
  useEffect(() => {
    searchCourses().catch(() => {
      setPageError('Không thể tải danh sách khóa học. Vui lòng thử lại.')
      appLogger.error(new Error('Load courses failed'), { feature: 'CoursesPage' })
      toast.error('Không thể tải danh sách khóa học')
    })
  }, [filters.keyword, filters.category, filters.level, filters.sort_by, pagination.skip])
  const retryLoad = () => {
    setPageError('')
    searchCourses().catch(() => {
      setPageError('Không thể tải danh sách khóa học. Vui lòng thử lại.')
    })
  }


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

  return (
    <div className="courses-page">
      {/* Tiêu đề và thanh tìm kiếm */}
      <motion.div className="courses-header" variants={fadeUp} initial={shouldReduceMotion ? false : 'hidden'} animate="show">
        <div className="courses-header__ornament" aria-hidden="true">
          <span className="courses-header__line" />
          <StarIcon />
          <span className="courses-header__line" />
        </div>
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
      <motion.div className="courses-filters" variants={fadeUp} initial={shouldReduceMotion ? false : 'hidden'} animate="show">
        <div className="courses-filters__group">
          <label className="courses-filters__label">Danh mục</label>
          <select
            className="courses-filters__select"
            value={filters.category}
            onChange={(e) => setFilters({ category: e.target.value })}
            data-testid="filter-category"
          >
            <option value="">Tất cả danh mục</option>
            <option value="Programming">Lập trình</option>
            <option value="Data Science">Khoa học dữ liệu</option>
            <option value="Math">Toán học</option>
            <option value="Business">Kinh doanh</option>
            <option value="Languages">Ngôn ngữ</option>
          </select>
        </div>

        <div className="courses-filters__group">
          <label className="courses-filters__label">Trình độ</label>
          <select
            className="courses-filters__select"
            value={filters.level}
            onChange={(e) => setFilters({ level: e.target.value })}
            data-testid="filter-level"
          >
            <option value="">Tất cả trình độ</option>
            <option value="Beginner">Cơ bản</option>
            <option value="Intermediate">Trung cấp</option>
            <option value="Advanced">Nâng cao</option>
          </select>
        </div>

        <div className="courses-filters__group">
          <label className="courses-filters__label">Sắp xếp</label>
          <select
            className="courses-filters__select"
            value={filters.sort_by}
            onChange={(e) => setFilters({ sort_by: e.target.value })}
            data-testid="filter-sort"
            title="Sắp xếp (client-side vì BE chưa hỗ trợ sort param)"
          >
            <option value="">Mặc định</option>
            <option value="newest">Mới nhất</option>
            <option value="popular">Phổ biến nhất</option>
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

      {!isLoading && pageError && (
        <StateView
          icon="⚠️"
          title="Lỗi tải dữ liệu"
          message={pageError}
          actionLabel="Thử lại"
          onAction={retryLoad}
        />
      )}

      {/* Danh sách khóa học */}
      {!isLoading && !pageError && courses.length > 0 && (
        <motion.div className="courses-masonry" variants={staggerEditorial} initial={shouldReduceMotion ? false : 'hidden'} animate="show">
          {courses.map((course) => (
            <motion.div
              key={course.id}
              className="course-card"
              variants={fadeUp}
              whileHover={shouldReduceMotion ? undefined : { y: -4, rotateX: 1.5, rotateY: -1.5 }}
              transition={{ duration: 0.22 }}
              {...(shouldReduceMotion ? {} : inView({ amount: 0.18 }))}
              onClick={() => navigate(`/dashboard/courses/${course.id}`)}
            >
              {/* Ảnh đại diện */}
              <div className="course-card__img-wrap">
                {course.thumbnail_url ? (
                  <img src={course.thumbnail_url} alt={course.title} className="course-card__img" />
                ) : (
                  <div className="course-card__img-placeholder">
                    <CategoryIcon category={course.category} />
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
                    <span className={`course-card__badge course-card__badge--${course.level?.toLowerCase()}`}>
                      {course.level === 'Beginner' ? 'Cơ bản'
                        : course.level === 'Intermediate' ? 'Trung cấp'
                        : course.level === 'Advanced' ? 'Nâng cao'
                        : course.level}
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
                      <RatingIcon /> {course.avg_rating.toFixed(1)}
                    </span>
                  )}
                </div>
              </div>
            </motion.div>
          ))}
        </motion.div>
      )}

      {/* Trạng thái rỗng */}
      {!isLoading && !pageError && courses.length === 0 && (
        <StateView
          type="empty"
          title="Không tìm thấy khóa học"
          message="Thử thay đổi bộ lọc hoặc từ khóa tìm kiếm."
          actionLabel="Xóa bộ lọc"
          onAction={() => {
            setSearchInput('')
            setFilters({ keyword: '', category: '', level: '', sort_by: '' })
            setSearchParams({})
          }}
        />
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

const CategoryIcon = ({ category }) => {
  if (category === 'Programming') return <Icon><path d="M16 18 22 12 16 6" /><path d="m8 6-6 6 6 6" /></Icon>
  if (category === 'Data Science') return <Icon><ellipse cx="12" cy="5" rx="8" ry="3" /><path d="M4 5v6c0 1.7 3.6 3 8 3s8-1.3 8-3V5" /><path d="M4 11v6c0 1.7 3.6 3 8 3s8-1.3 8-3v-6" /></Icon>
  if (category === 'Math') return <Icon><path d="M8 6h12" /><path d="M8 12h12" /><path d="M8 18h12" /><path d="m3 6 2 2 2-2" /><path d="m3 12 2 2 2-2" /><path d="m3 18 2 2 2-2" /></Icon>
  if (category === 'Business') return <Icon><rect x="3" y="7" width="18" height="13" rx="2" /><path d="M8 7V5a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" /></Icon>
  if (category === 'Languages') return <Icon><path d="M2 12h20" /><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10Z" /></Icon>
  return <Icon><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" /><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2Z" /></Icon>
}
const StarIcon = () => <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"><path d="m12 2 2.8 7.2L22 12l-7.2 2.8L12 22l-2.8-7.2L2 12l7.2-2.8L12 2Z" /></svg>
const RatingIcon = () => <svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor"><path d="m12 2 2.83 6.63L22 9.27l-5.4 4.73L18.18 22 12 18.27 5.82 22l1.58-7.99L2 9.27l7.17-.64L12 2Z"/></svg>
const Icon = ({ children }) => <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">{children}</svg>

export default CoursesPage