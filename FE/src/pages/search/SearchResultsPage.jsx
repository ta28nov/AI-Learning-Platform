import { useState, useEffect, useCallback } from 'react'
import { useSearchParams, useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import toast from 'react-hot-toast'
import searchService from '@services/searchService'
import Card, { CardBody } from '@components/ui/Card'
import Button from '@components/ui/Button'
import './SearchResultsPage.css'

/**
 * Trang ket qua tim kiem
 * Route: /dashboard/search?q=...&category=...&level=...&page=...
 * API: GET /search
 *
 * BE Response (SearchResponse):
 * - query: str
 * - total_results: int
 * - results_by_category: List[SearchCategoryGroup]
 *     moi item: { category, count, items[] }
 *     moi items[]: { id, type, title, description, relevance_score, url, metadata }
 * - suggestions: List[SearchSuggestion] { query, type, score }
 * - search_time_ms: int
 * - filters_applied: dict
 */
const SearchResultsPage = () => {
  const [searchParams, setSearchParams] = useSearchParams()
  const navigate = useNavigate()

  // Lay params tu URL
  const query = searchParams.get('q') || ''
  const page = parseInt(searchParams.get('page') || '1', 10)
  const categoryFilter = searchParams.get('category') || ''
  const levelFilter = searchParams.get('level') || ''

  // State
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(true)

  // Goi API tim kiem
  useEffect(() => {
    if (!query || query.length < 2) {
      setLoading(false)
      setResults(null)
      return
    }

    const fetchResults = async () => {
      try {
        setLoading(true)
        const data = await searchService.search({
          q: query,
          category: categoryFilter || undefined,
          level: levelFilter || undefined,
          page,
          limit: 20
        })
        setResults(data)
      } catch (error) {
        toast.error(error?.message || 'Lỗi khi tìm kiếm')
      } finally {
        setLoading(false)
      }
    }

    fetchResults()
  }, [query, page, categoryFilter, levelFilter])

  // Chuyen trang
  const goToPage = useCallback((newPage) => {
    const params = new URLSearchParams(searchParams)
    params.set('page', String(newPage))
    setSearchParams(params)
  }, [searchParams, setSearchParams])

  // Thay doi filter
  const handleFilterChange = useCallback((key, value) => {
    const params = new URLSearchParams(searchParams)
    if (value) {
      params.set(key, value)
    } else {
      params.delete(key)
    }
    // Reset ve trang 1 khi doi filter
    params.set('page', '1')
    setSearchParams(params)
  }, [searchParams, setSearchParams])

  // Xoa tat ca filter
  const clearFilters = useCallback(() => {
    const params = new URLSearchParams()
    params.set('q', query)
    params.set('page', '1')
    setSearchParams(params)
  }, [query, setSearchParams])

  // Click vao suggestion
  const handleSuggestionClick = useCallback((suggestionQuery) => {
    const params = new URLSearchParams()
    params.set('q', suggestionQuery)
    params.set('page', '1')
    setSearchParams(params)
  }, [setSearchParams])

  // Xu ly click vao result item - dieu huong theo type
  const handleItemClick = useCallback((item) => {
    if (item?.url) {
      // url tu BE co the la relative path
      navigate(item.url)
    } else {
      // Fallback dieu huong theo type
      const typeRoutes = {
        course: `/dashboard/courses/${item.id}`,
        user: `/dashboard/profile/${item.id}`,
        class: `/dashboard/classes/${item.id}`,
        module: `/dashboard/courses`, // Can courseId, fallback
        lesson: `/dashboard/courses`
      }
      navigate(typeRoutes[item.type] || `/dashboard/courses/${item.id}`)
    }
  }, [navigate])

  // Tinh tong pages
  const totalPages = Math.ceil((results?.total_results || 0) / 20)

  // Kiem tra co filter nao dang ap dung khong
  const hasActiveFilters = categoryFilter || levelFilter

  // Category labels tieng Viet
  const categoryLabels = {
    courses: 'Khóa học',
    users: 'Người dùng',
    classes: 'Lớp học',
    modules: 'Modules',
    lessons: 'Bài học'
  }

  // === RENDER STATES ===

  // Loading state
  if (loading) {
    return (
      <div className="search-results">
        <div className="search-results__loading">
          <div className="search-results__loading-spinner" />
          <span className="search-results__loading-text">
            Đang tìm kiếm "{query}"...
          </span>
        </div>
      </div>
    )
  }

  // Query qua ngan
  if (!query || query.length < 2) {
    return (
      <div className="search-results">
        <div className="search-results__min-query">
          <div className="search-results__min-query-icon">🔍</div>
          <p className="search-results__min-query-text">
            Nhập ít nhất 2 ký tự để tìm kiếm
          </p>
        </div>
      </div>
    )
  }

  return (
    <motion.div
      className="search-results"
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      {/* Header: tieu de + so ket qua + thoi gian */}
      <div className="search-results__header">
        <h1 className="search-results__title">Kết quả tìm kiếm</h1>
        <div className="search-results__meta">
          <span>
            {results?.total_results || 0} kết quả cho "
            <span className="search-results__query">{query}</span>"
          </span>
          {results?.search_time_ms != null && (
            <span className="search-results__meta-time">
              ({results.search_time_ms}ms)
            </span>
          )}
        </div>

        {/* Hien thi filters dang ap dung */}
        {hasActiveFilters && (
          <div className="search-results__applied-filters">
            {categoryFilter && (
              <span className="search-results__applied-chip">
                {categoryFilter}
                <span
                  className="search-results__applied-chip-remove"
                  onClick={() => handleFilterChange('category', '')}
                >
                  ✕
                </span>
              </span>
            )}
            {levelFilter && (
              <span className="search-results__applied-chip">
                {levelFilter}
                <span
                  className="search-results__applied-chip-remove"
                  onClick={() => handleFilterChange('level', '')}
                >
                  ✕
                </span>
              </span>
            )}
          </div>
        )}

        {/* Filters info tu BE */}
        {results?.filters_applied && Object.keys(results.filters_applied).length > 0 && (
          <p className="search-results__filters-info">
            Bộ lọc đang áp dụng: {Object.entries(results.filters_applied)
              .filter(([, v]) => v)
              .map(([k, v]) => `${k}: ${v}`)
              .join(', ')}
          </p>
        )}
      </div>

      {/* Layout: Filters sidebar + Content */}
      <div className="search-results__layout">
        {/* Filters sidebar */}
        <aside className="search-results__filters">
          <div className="search-results__filter-group">
            <label className="search-results__filter-label" htmlFor="filter-category">
              Danh mục
            </label>
            <select
              id="filter-category"
              className="search-results__filter-select"
              value={categoryFilter}
              onChange={(e) => handleFilterChange('category', e.target.value)}
            >
              <option value="">Tất cả danh mục</option>
              <option value="Programming">Lập trình</option>
              <option value="Math">Toán học</option>
              <option value="Business">Kinh doanh</option>
              <option value="Design">Thiết kế</option>
              <option value="Marketing">Marketing</option>
              <option value="Science">Khoa học</option>
              <option value="Language">Ngôn ngữ</option>
              <option value="Music">Âm nhạc</option>
              <option value="Health">Sức khỏe</option>
              <option value="Engineering">Kỹ thuật</option>
            </select>
          </div>

          <div className="search-results__filter-group">
            <label className="search-results__filter-label" htmlFor="filter-level">
              Cấp độ
            </label>
            <select
              id="filter-level"
              className="search-results__filter-select"
              value={levelFilter}
              onChange={(e) => handleFilterChange('level', e.target.value)}
            >
              <option value="">Tất cả cấp độ</option>
              <option value="Beginner">Beginner</option>
              <option value="Intermediate">Intermediate</option>
              <option value="Advanced">Advanced</option>
            </select>
          </div>

          {hasActiveFilters && (
            <button
              className="search-results__filter-reset"
              onClick={clearFilters}
            >
              Xóa bộ lọc
            </button>
          )}
        </aside>

        {/* Main content - ket qua theo category */}
        <div className="search-results__content">
          <AnimatePresence mode="wait">
            {results?.results_by_category?.length > 0 ? (
              <motion.div
                key="results"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
              >
                {results.results_by_category.map((group) => (
                  <div key={group.category} className="search-results__category">
                    {/* Category header */}
                    <div className="search-results__category-header">
                      <h2 className="search-results__category-title">
                        {categoryLabels[group.category] || group.category}
                      </h2>
                      <span className="search-results__category-count">
                        {group.count} kết quả
                      </span>
                    </div>

                    {/* Items grid */}
                    <div className="search-results__grid">
                      {group.items?.map((item, index) => (
                        <motion.div
                          key={item.id}
                          initial={{ opacity: 0, y: 10 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ delay: index * 0.05 }}
                        >
                          <Card
                            hover
                            className="search-results__item"
                            onClick={() => handleItemClick(item)}
                          >
                            <CardBody>
                              <h3 className="search-results__item-title">
                                {item.title}
                              </h3>
                              <p className="search-results__item-desc">
                                {item.description}
                              </p>
                              <div className="search-results__item-tags">
                                {/* Type badge */}
                                <span className="search-results__tag search-results__tag--type">
                                  {categoryLabels[item.type + 's'] || item.type}
                                </span>

                                {/* Relevance score */}
                                {item.relevance_score != null && (
                                  <span className="search-results__tag search-results__tag--score">
                                    {Math.round(item.relevance_score)}% phù hợp
                                  </span>
                                )}

                                {/* Metadata extras */}
                                {item.metadata?.category && (
                                  <span className="search-results__tag search-results__tag--type">
                                    {item.metadata.category}
                                  </span>
                                )}
                                {item.metadata?.level && (
                                  <span className="search-results__tag search-results__tag--type">
                                    {item.metadata.level}
                                  </span>
                                )}
                                {item.metadata?.instructor_name && (
                                  <span className="search-results__tag" style={{ color: 'var(--text-secondary)' }}>
                                    Bởi: {item.metadata.instructor_name}
                                  </span>
                                )}
                              </div>
                            </CardBody>
                          </Card>
                        </motion.div>
                      ))}
                    </div>
                  </div>
                ))}
              </motion.div>
            ) : (
              <motion.div
                key="empty"
                className="search-results__empty"
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
              >
                <div className="search-results__empty-icon">🔍</div>
                <h3 className="search-results__empty-title">
                  Không tìm thấy kết quả
                </h3>
                <p className="search-results__empty-desc">
                  Không tìm thấy kết quả phù hợp cho "{query}".
                  Thử dùng từ khóa khác hoặc bỏ bớt bộ lọc.
                </p>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Suggestions tu BE */}
          {results?.suggestions?.length > 0 && (
            <div className="search-results__suggestions">
              <div className="search-results__suggestions-title">
                Gợi ý tìm kiếm
              </div>
              <div className="search-results__suggestions-list">
                {results.suggestions.map((suggestion, idx) => (
                  <button
                    key={idx}
                    className="search-results__suggestion-item"
                    onClick={() => handleSuggestionClick(suggestion.query)}
                  >
                    {suggestion.query}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="search-results__pagination">
              <Button
                variant="outline"
                size="sm"
                disabled={page <= 1}
                onClick={() => goToPage(page - 1)}
              >
                ← Trước
              </Button>
              <span className="search-results__pagination-info">
                Trang {page} / {totalPages}
              </span>
              <Button
                variant="outline"
                size="sm"
                disabled={page >= totalPages}
                onClick={() => goToPage(page + 1)}
              >
                Tiếp →
              </Button>
            </div>
          )}
        </div>
      </div>
    </motion.div>
  )
}

export default SearchResultsPage
