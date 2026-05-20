import { useState, useEffect, useCallback } from 'react'
import { useParams, useNavigate, useSearchParams } from 'react-router-dom'
import { motion } from 'framer-motion'
import toast from 'react-hot-toast'
import quizService from '@services/quizService'
import classService from '@services/classService'
import Button from '@components/ui/Button'
import StateView from '@components/ui/StateView'
import AILoadingState from '@components/ui/AILoadingState'
import './InstructorQuizClassResultsPage.css'

const PageHeader = ({ onBack, title, subtitle }) => (
  <header className="iqcr-header">
    <button type="button" className="iqcr-back" onClick={onBack}>
      <svg viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.5" aria-hidden>
        <path d="M15 10H5m0 0 5-5M5 10l5 5" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
      Danh sách quiz
    </button>
    <svg className="iqcr-ornament" viewBox="0 0 48 12" fill="none" aria-hidden>
      <line x1="0" y1="6" x2="16" y2="6" stroke="var(--gold-500)" strokeWidth="1" />
      <circle cx="24" cy="6" r="4" stroke="var(--gold-500)" strokeWidth="1" />
      <line x1="32" y1="6" x2="48" y2="6" stroke="var(--gold-500)" strokeWidth="1" />
    </svg>
    <h1 className="iqcr-title">{title}</h1>
    {subtitle && <p className="iqcr-subtitle">{subtitle}</p>}
  </header>
)

/**
 * InstructorQuizClassResultsPage — Kết quả quiz theo lớp
 */
const InstructorQuizClassResultsPage = () => {
  const { quizId } = useParams()
  const navigate = useNavigate()
  const [searchParams, setSearchParams] = useSearchParams()
  const classId = searchParams.get('classId') || ''

  const [classes, setClasses] = useState([])
  const [classesLoading, setClassesLoading] = useState(true)
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    classService
      .getMyClasses()
      .then((data) => setClasses(data?.classes || data || []))
      .catch(() => toast.error('Không thể tải danh sách lớp'))
      .finally(() => setClassesLoading(false))
  }, [])

  const fetchResults = useCallback(async () => {
    if (!classId) {
      setResults(null)
      setError('')
      setLoading(false)
      return
    }
    try {
      setLoading(true)
      setError('')
      const data = await quizService.getClassResults(quizId, { class_id: classId })
      setResults(data)
    } catch (err) {
      setError(err?.message || 'Không thể tải kết quả lớp')
      setResults(null)
    } finally {
      setLoading(false)
    }
  }, [quizId, classId])

  useEffect(() => { fetchResults() }, [fetchResults])

  const stats = results?.statistics
  const selectedClass = classes.find((c) => (c.id || c.class_id) === classId)

  return (
    <motion.div className="iqcr-page" initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}>
      <PageHeader
        onBack={() => navigate('/dashboard/instructor/quizzes')}
        title={results?.quiz_title || 'Kết quả theo lớp'}
        subtitle={selectedClass ? `Lớp: ${selectedClass.name}` : 'Chọn lớp để xem báo cáo chi tiết'}
      />

      <motion.div className="iqcr-filter-card">
        <label className="iqcr-label" htmlFor="iqcr-class-select">Lớp học</label>
        {classesLoading ? (
          <p className="iqcr-filter-hint">Đang tải lớp…</p>
        ) : classes.length === 0 ? (
          <StateView
            type="empty"
            message="Bạn chưa có lớp nào. Tạo lớp trước khi xem kết quả quiz."
            action={{ label: 'Tạo lớp học', onClick: () => navigate('/dashboard/instructor/classes/create') }}
          />
        ) : (
          <select
            id="iqcr-class-select"
            className="iqcr-select"
            value={classId}
            onChange={(e) => setSearchParams(e.target.value ? { classId: e.target.value } : {})}
          >
            <option value="">— Chọn lớp học —</option>
            {classes.map((c) => (
              <option key={c.id || c.class_id} value={c.id || c.class_id}>
                {c.name}
                {c.course_title ? ` · ${c.course_title}` : ''}
              </option>
            ))}
          </select>
        )}
      </motion.div>

      {!classId && !classesLoading && classes.length > 0 && (
        <StateView
          type="empty"
          title="Chọn lớp để bắt đầu"
          message="Thống kê gồm tỷ lệ đạt, điểm trung bình, bảng xếp hạng học viên và các câu khó nhất."
        />
      )}

      {classId && loading && (
        <AILoadingState
          compact
          title="Đang tổng hợp kết quả"
          message="Đang tính điểm và thống kê theo lớp…"
          steps={['Đang tải danh sách học viên…', 'Đang tính điểm trung bình…', 'Sắp xếp bảng xếp hạng…']}
        />
      )}

      {classId && !loading && error && (
        <StateView
          type="error"
          title="Không tải được dữ liệu"
          message={error}
          action={{ label: 'Thử lại', onClick: fetchResults }}
        />
      )}

      {classId && !loading && !error && results && stats && (
        <>
          <div className="iqcr-stats">
            <div className="iqcr-stat">
              <span className="iqcr-stat__val">{stats.completed_count}/{stats.total_students}</span>
              <span className="iqcr-stat__lbl">Đã nộp bài</span>
              <span className="iqcr-stat__sub">{Math.round(stats.completion_rate || 0)}% hoàn thành</span>
            </div>
            <div className="iqcr-stat">
              <span className="iqcr-stat__val">{Math.round(stats.pass_rate || 0)}%</span>
              <span className="iqcr-stat__lbl">Tỷ lệ đạt</span>
              <span className="iqcr-stat__sub">{stats.pass_count} đạt · {stats.fail_count} chưa đạt</span>
            </div>
            <div className="iqcr-stat">
              <span className="iqcr-stat__val">{Math.round(stats.average_score || 0)}%</span>
              <span className="iqcr-stat__lbl">Điểm trung bình</span>
              <span className="iqcr-stat__sub">
                Cao nhất {Math.round(stats.highest_score || 0)}% · Thấp nhất {Math.round(stats.lowest_score || 0)}%
              </span>
            </div>
          </div>

          {results.student_ranking?.length > 0 ? (
            <section className="iqcr-section">
              <h2 className="iqcr-section-title">Bảng xếp hạng học viên</h2>
              <div className="iqcr-table-wrap">
                <table className="iqcr-table">
                  <thead>
                    <tr>
                      <th>Hạng</th>
                      <th>Học viên</th>
                      <th>Điểm</th>
                      <th>Lần làm</th>
                      <th>Thời gian</th>
                      <th>Kết quả</th>
                    </tr>
                  </thead>
                  <tbody>
                    {results.student_ranking.map((row) => (
                      <tr key={row.user_id}>
                        <td className="iqcr-rank">{row.rank}</td>
                        <td className="iqcr-name">{row.full_name}</td>
                        <td><strong>{Math.round(row.score)}%</strong></td>
                        <td>{row.attempt_count}</td>
                        <td>{row.time_spent != null ? `${row.time_spent} phút` : '—'}</td>
                        <td>
                          <span className={`iqcr-badge iqcr-badge--${row.status}`}>
                            {row.status === 'pass' ? 'Đạt' : 'Chưa đạt'}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>
          ) : (
            <StateView type="empty" message="Chưa có học viên nào làm quiz trong lớp này" />
          )}

          {results.difficult_questions?.length > 0 && (
            <section className="iqcr-section">
              <h2 className="iqcr-section-title">Câu hỏi khó (tỷ lệ đúng thấp)</h2>
              <ul className="iqcr-difficult-list">
                {results.difficult_questions.map((q) => (
                  <li key={q.question_id} className="iqcr-difficult-item">
                    <p className="iqcr-difficult-text">{q.question_text}</p>
                    <span className="iqcr-difficult-rate">{Math.round(q.correct_rate)}% trả lời đúng</span>
                  </li>
                ))}
              </ul>
            </section>
          )}
        </>
      )}

      {classId && !loading && !error && !results && (
        <StateView type="empty" message="Chưa có dữ liệu kết quả cho lớp này" />
      )}

      <div className="iqcr-footer">
        <Button variant="outline" onClick={() => navigate(`/dashboard/quiz/${quizId}`)}>
          Xem trước quiz (học viên)
        </Button>
      </div>
    </motion.div>
  )
}

export default InstructorQuizClassResultsPage
