import { useState, useEffect } from 'react'
import { useSearchParams, useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import searchService from '@services/searchService'
import Card, { CardBody } from '@components/ui/Card'

/**
 * Trang ket qua tim kiem
 * Route: /dashboard/search?q=...
 * API: GET /search
 */
const SearchResultsPage = () => {
  const [searchParams, setSearchParams] = useSearchParams()
  const navigate = useNavigate()
  const query = searchParams.get('q') || ''
  const page = parseInt(searchParams.get('page') || '1', 10)
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!query || query.length < 2) {
      setLoading(false)
      return
    }
    const fetchResults = async () => {
      try {
        setLoading(true)
        const data = await searchService.search({
          q: query,
          category: searchParams.get('category') || '',
          level: searchParams.get('level') || '',
          skip: (page - 1) * 20,
          limit: 20
        })
        setResults(data)
      } catch (error) {
        toast.error('Lỗi khi tìm kiếm')
      } finally {
        setLoading(false)
      }
    }
    fetchResults()
  }, [query, page])

  // Chuyen trang
  const goToPage = (newPage) => {
    searchParams.set('page', String(newPage))
    setSearchParams(searchParams)
  }

  const totalPages = results?.search_metadata?.total_pages || Math.ceil((results?.total || 0) / 20)

  if (loading) return <div style={{ padding: 24, textAlign: 'center' }}>Đang tìm kiếm...</div>

  return (
    <div style={{ padding: 16 }}>
      <div style={{ marginBottom: 20 }}>
        <h1 style={{ fontSize: '1.5rem', fontWeight: 700 }}>Kết quả tìm kiếm</h1>
        <p style={{ color: '#6b7280', fontSize: '0.85rem' }}>
          {results?.total || 0} kết quả cho "{query}"
          {results?.search_metadata?.search_time_ms && (
            <span> ({results.search_metadata.search_time_ms}ms)</span>
          )}
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: 12 }}>
        {results?.courses?.map((course) => (
          <Card
            key={course.id}
            hover
            onClick={() => navigate(`/dashboard/courses/${course.id}`)}
          >
            <CardBody>
              <h3 style={{ fontWeight: 600, marginBottom: 4 }}>{course.title}</h3>
              <p style={{ fontSize: '0.8rem', color: '#6b7280', marginBottom: 6 }}>
                {course.description?.substring(0, 120)}...
              </p>
              <div style={{ display: 'flex', gap: 8, fontSize: '0.7rem', flexWrap: 'wrap' }}>
                {course.category && (
                  <span style={{ padding: '2px 8px', background: '#e0e7ff', borderRadius: 10, color: '#3730a3' }}>{course.category}</span>
                )}
                {course.level && (
                  <span style={{ padding: '2px 8px', background: '#f3f4f6', borderRadius: 10 }}>{course.level}</span>
                )}
                {course.instructor_name && (
                  <span style={{ color: '#6b7280' }}>Bởi: {course.instructor_name}</span>
                )}
                {course.match_score != null && (
                  <span style={{ padding: '2px 8px', background: '#dcfce7', borderRadius: 10, color: '#166534', fontWeight: 600 }}>
                    {Math.round(course.match_score)}% phù hợp
                  </span>
                )}
              </div>
            </CardBody>
          </Card>
        ))}
      </div>

      {(!results?.courses || results.courses.length === 0) && !loading && (
        <div style={{ textAlign: 'center', padding: 40, color: '#6b7280' }}>
          Không tìm thấy kết quả phù hợp
        </div>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <div style={{ display: 'flex', justifyContent: 'center', gap: 8, marginTop: 20 }}>
          <Button variant="outline" size="sm" disabled={page <= 1} onClick={() => goToPage(page - 1)}>
            ← Trước
          </Button>
          <span style={{ padding: '6px 12px', fontSize: '0.85rem', color: '#6b7280' }}>
            Trang {page} / {totalPages}
          </span>
          <Button variant="outline" size="sm" disabled={page >= totalPages} onClick={() => goToPage(page + 1)}>
            Tiếp →
          </Button>
        </div>
      )}
    </div>
  )
}

export default SearchResultsPage
