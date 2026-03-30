import { useState, useCallback, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import searchService from '@services/searchService'
import './GlobalSearchBar.css'

/**
 * GlobalSearchBar — Thanh tìm kiếm toàn cục trong header DashboardLayout
 * - Gõ ≥ 1 ký tự → autocomplete (GET /search/suggestions, debounce 200ms)
 * - Enter hoặc click Tìm → chuyển đến SearchResultsPage (GET /search)
 * - Focus + lịch sử → GET /search/history (20 recent terms)
 * Theo BE API: q param bắt buộc min 1 (suggestions) hoặc min 2 (search)
 */
const GlobalSearchBar = () => {
  const navigate = useNavigate()
  const [query, setQuery] = useState('')
  const [suggestions, setSuggestions] = useState([])
  const [history, setHistory] = useState([])
  const [showDropdown, setShowDropdown] = useState(false)
  const [loadingSug, setLoadingSug] = useState(false)
  const debounceRef = useRef(null)
  const wrapperRef = useRef(null)

  // Lay goi y autocomplete (debounce 200ms theo thiet ke)
  const fetchSuggestions = useCallback((q) => {
    clearTimeout(debounceRef.current)
    if (!q || q.trim().length < 1) {
      setSuggestions([])
      return
    }
    debounceRef.current = setTimeout(async () => {
      setLoadingSug(true)
      try {
        const data = await searchService.getSuggestions(q.trim())
        // BE tra ve mang suggestions truc tiep hoac object { suggestions: [] }
        setSuggestions(data?.suggestions || data || [])
      } catch {
        setSuggestions([])
      } finally {
        setLoadingSug(false)
      }
    }, 200)
  }, [])

  // Lay lich su tim kiem khi focus va chua co query
  const fetchHistory = useCallback(async () => {
    try {
      const data = await searchService.getHistory()
      setHistory(data?.recent_searches || data || [])
    } catch {
      setHistory([])
    }
  }, [])

  const handleChange = (e) => {
    const val = e.target.value
    setQuery(val)
    setShowDropdown(true)
    if (val.trim()) {
      fetchSuggestions(val)
    } else {
      setSuggestions([])
      fetchHistory()
    }
  }

  const handleFocus = () => {
    setShowDropdown(true)
    if (!query.trim()) fetchHistory()
  }

  // Dong dropdown khi click ngoai
  const handleBlur = () => {
    // Delay de cho phep click vao suggestion truoc khi dong
    setTimeout(() => setShowDropdown(false), 150)
  }

  // Thuc hien tim kiem day du (min 2 ky tu theo BE)
  const handleSearch = (q = query) => {
    const term = (q || '').trim()
    if (!term || term.length < 2) return
    setShowDropdown(false)
    setQuery(term)
    navigate(`/dashboard/search?q=${encodeURIComponent(term)}`)
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') handleSearch()
    if (e.key === 'Escape') {
      setShowDropdown(false)
      e.target.blur()
    }
  }

  // Click vao goi y hoac lich su
  const handlePickSuggestion = (term) => {
    handleSearch(term)
  }

  const showHistory = showDropdown && !query.trim() && history.length > 0
  const showSuggestions = showDropdown && query.trim() && suggestions.length > 0

  return (
    <div className="global-search" ref={wrapperRef}>
      <div className="global-search__input-wrap">
        <span className="global-search__icon" aria-hidden="true">🔍</span>
        <input
          id="global-search-input"
          type="text"
          className="global-search__input"
          placeholder="Tìm kiếm khóa học, bài học..."
          value={query}
          onChange={handleChange}
          onFocus={handleFocus}
          onBlur={handleBlur}
          onKeyDown={handleKeyDown}
          autoComplete="off"
          aria-label="Tìm kiếm toàn hệ thống"
          aria-expanded={showDropdown}
          aria-haspopup="listbox"
        />
        {query && (
          <button
            className="global-search__clear"
            onClick={() => { setQuery(''); setSuggestions([]) }}
            aria-label="Xóa từ khóa"
            tabIndex={-1}
          >
            ✕
          </button>
        )}
        {loadingSug && <span className="global-search__loading" aria-live="polite" />}
      </div>

      {/* Dropdown: suggestions hoặc history */}
      {(showSuggestions || showHistory) && (
        <div className="global-search__dropdown" role="listbox" aria-label="Gợi ý tìm kiếm">
          {showHistory && (
            <>
              <div className="global-search__dropdown-label">Tìm kiếm gần đây</div>
              {history.slice(0, 8).map((item, idx) => (
                <button
                  key={idx}
                  className="global-search__suggestion global-search__suggestion--history"
                  onClick={() => handlePickSuggestion(item?.query || item)}
                  role="option"
                >
                  <span className="global-search__suggestion-icon">🕐</span>
                  <span>{item?.query || item}</span>
                </button>
              ))}
            </>
          )}

          {showSuggestions && (
            <>
              <div className="global-search__dropdown-label">Gợi ý</div>
              {suggestions.slice(0, 8).map((sug, idx) => (
                <button
                  key={idx}
                  className="global-search__suggestion"
                  onClick={() => handlePickSuggestion(sug?.text || sug?.title || sug)}
                  role="option"
                >
                  <span className="global-search__suggestion-icon">
                    {sug?.type === 'course' ? '📚' : sug?.type === 'lesson' ? '📝' : '🔍'}
                  </span>
                  <span className="global-search__suggestion-text">
                    {sug?.text || sug?.title || sug}
                  </span>
                  {sug?.category && (
                    <span className="global-search__suggestion-tag">{sug.category}</span>
                  )}
                </button>
              ))}
            </>
          )}
        </div>
      )}
    </div>
  )
}

export default GlobalSearchBar
