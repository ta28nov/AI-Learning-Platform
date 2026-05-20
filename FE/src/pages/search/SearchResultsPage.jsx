import { useState, useEffect, useCallback } from 'react'
import { useSearchParams, useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import toast from 'react-hot-toast'
import searchService from '@services/searchService'
import { useAuthStore } from '@stores/authStore'
import Card, { CardBody } from '@components/ui/Card'
import Button from '@components/ui/Button'
import StateView from '@components/ui/StateView'
import AILoadingState from '@components/ui/AILoadingState'
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
  const [error, setError] = useState('')
  const [searchAnalytics, setSearchAnalytics] = useState(null)
  const { user } = useAuthStore()

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
        setError('')
        const data = await searchService.search({
          q: query,
          category: categoryFilter || undefined,
          level: levelFilter || undefined,
          page,
          limit: 20
        })
        setResults(data)
      } catch (error) {
        const message = error?.message || 'Lỗi khi tìm kiếm'
        setError(message)
        toast.error(message)
      } finally {
        setLoading(false)
      }
    }

    fetchResults()
  }, [query, page, categoryFilter, levelFilter])

  useEffect(() => {
    if (user?.role !== 'admin') return
    searchService.getAnalytics().then(setSearchAnalytics).catch(() => {})
  }, [user?.role])

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

  // Map URL API (/courses/...) sang route dashboard (/dashboard/courses/...)
  const resolveSearchItemUrl = useCallback((item) => {
    const url = item?.url || ''
    if (url.startsWith('/dashboard/')) return url

    const courseMatch = url.match(/^\/courses\/([^/]+)$/)
    if (courseMatch) return `/dashboard/courses/${courseMatch[1]}`

    const classMatch = url.match(/^\/classes\/([^/]+)$/)
    if (classMatch) return `/dashboard/classes/${classMatch[1]}`

    const moduleMatch = url.match(/^\/courses\/([^/]+)\/modules\/([^/]+)$/)
    if (moduleMatch) return `/dashboard/courses/${moduleMatch[1]}/modules/${moduleMatch[2]}`

    const lessonMatch = url.match(/^\/courses\/([^/]+)\/modules\/[^/]+\/lessons\/([^/]+)$/)
    if (lessonMatch) return `/dashboard/courses/${lessonMatch[1]}/lessons/${lessonMatch[2]}`

    if (url) return url.startsWith('/') ? `/dashboard${url}` : url

    const typeRoutes = {
      course: `/dashboard/courses/${item.id}`,
      user: '/dashboard/profile',
      class: `/dashboard/classes/${item.id}`,
      module: '/dashboard/courses',
      lesson: '/dashboard/courses',
    }
    return typeRoutes[item?.type] || `/dashboard/courses/${item?.id}`
  }, [])

  // Xu ly click vao result item - dieu huong theo type
  const handleItemClick = useCallback((item) => {
    navigate(resolveSearchItemUrl(item))
  }, [navigate, resolveSearchItemUrl])

  // Tinh tong pages
  const totalPages = Math.ceil((results?.total_results || 0) / 20)
  const groupedResults = results?.results_by_category || []

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
        <AILoadingState
          title="AI đang tìm kiếm"
          message={`Đang truy xuất và xếp hạng kết quả cho "${query}"...`}
          steps={[
            'Đang tìm trong khóa học, lớp học, bài học...',
            'Đang tính độ phù hợp kết quả...',
            'Đang chuẩn bị danh sách hiển thị...',
          ]}
        />
      </div>
    )
  }

  // Query qua ngan
  if (!query || query.length < 2) {
    return (
      <div className="search-results">
        <StateView
          type="info"
          title="Bắt đầu tìm kiếm"
          message="Nhập ít nhất 2 ký tự để tìm kiếm"
        />
      </div>
    )
  }

  if (error) {
    return (
      <div className="search-results">
        <StateView
          type="error"
          title="Không thể tải kết quả tìm kiếm"
          message={error}
        />
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
        <div className="search-results__ornament" aria-hidden="true">
          <svg viewBox="0 0 120 14" fill="none">
            <path d="M2 7H48" stroke="currentColor" strokeWidth="1.5" />
            <circle cx="60" cy="7" r="4.5" stroke="currentColor" strokeWidth="1.5" />
            <path d="M72 7H118" stroke="currentColor" strokeWidth="1.5" />
          </svg>
        </div>
        <h1 className="search-results__title">Bản đồ kết quả tìm kiếm</h1>
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
            {groupedResults.length > 0 ? (
              <motion.div
                key="results"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
              >
                {groupedResults.map((group, groupIndex) => (
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
                          key={`${group.category}-${item.type}-${item.id || index}-${groupIndex}`}
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
                                  <span className="search-results__tag search-results__tag--muted">
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
                className="search-results__empty-wrap"
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
              >
                <StateView
                  type="empty"
                  title="Không tìm thấy kết quả"
                  message={`Không tìm thấy kết quả phù hợp cho "${query}". Thử dùng từ khóa khác hoặc bỏ bớt bộ lọc.`}
                />
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

      {user?.role === 'admin' && searchAnalytics && (
        <Card className="search-analytics-panel">
          <CardBody>
            <h3 className="search-analytics-title">Thống kê tìm kiếm (admin)</h3>
            <p className="search-analytics-meta">
              Tổng truy vấn: {searchAnalytics.total_searches ?? searchAnalytics.total ?? '—'}
              {searchAnalytics.top_queries?.length > 0 && (
                <> · Top: {searchAnalytics.top_queries.slice(0, 3).map((q) => q.query || q).join(', ')}</>
              )}
            </p>
          </CardBody>
        </Card>
      )}
    </motion.div>
  )
}

export default SearchResultsPage
