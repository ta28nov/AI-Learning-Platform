import { useState, useEffect, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import toast from 'react-hot-toast'
import analyticsService from '@services/analyticsService'
import StateView from '@components/ui/StateView'
import AILoadingState from '@components/ui/AILoadingState'
import Button from '@components/ui/Button'
import './InstructorAnalyticsPage.css'

const InstructorAnalyticsPage = () => {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [classStats, setClassStats] = useState(null)
  const [chart, setChart] = useState(null)
  const [quizPerf, setQuizPerf] = useState(null)
  const [timeRange, setTimeRange] = useState('week')

  const load = useCallback(async () => {
    try {
      setLoading(true)
      setError('')
      const [classes, progressChart, quizzes] = await Promise.all([
        analyticsService.getInstructorClassStats(),
        analyticsService.getInstructorProgressChart({ time_range: timeRange }),
        analyticsService.getInstructorQuizPerformance(),
      ])
      setClassStats(classes)
      setChart(progressChart)
      setQuizPerf(quizzes)
    } catch (err) {
      setError(err?.message || 'Không thể tải analytics')
      toast.error('Không thể tải analytics')
    } finally {
      setLoading(false)
    }
  }, [timeRange])

  useEffect(() => { load() }, [load])

  const chartData = chart?.chart_data || []

  if (loading) {
    return (
      <div className="ia-page">
        <AILoadingState
          title="Đang tải analytics"
          message="Tổng hợp dữ liệu lớp học và quiz…"
          steps={['Thống kê lớp…', 'Biểu đồ tiến độ…', 'Hiệu quả quiz…']}
        />
      </div>
    )
  }

  if (error) {
    return (
      <div className="ia-page">
        <PageHeader onBack={() => navigate('/dashboard/instructor')} />
        <StateView type="error" title="Lỗi tải dữ liệu" message={error} action={{ label: 'Thử lại', onClick: load }} />
      </div>
    )
  }

  return (
    <motion.div className="ia-page" initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}>
      <PageHeader onBack={() => navigate('/dashboard/instructor')} />

      <div className="ia-stats">
        <div className="ia-stat">
          <span className="ia-stat__val">{classStats?.total_classes ?? 0}</span>
          <span className="ia-stat__lbl">Lớp học</span>
        </div>
        <div className="ia-stat">
          <span className="ia-stat__val">{classStats?.total_students ?? 0}</span>
          <span className="ia-stat__lbl">Học viên</span>
        </div>
        <div className="ia-stat">
          <span className="ia-stat__val">{Math.round(classStats?.avg_completion || 0)}%</span>
          <span className="ia-stat__lbl">Hoàn thành TB</span>
        </div>
        <div className="ia-stat">
          <span className="ia-stat__val">{Math.round(quizPerf?.overall_pass_rate || 0)}%</span>
          <span className="ia-stat__lbl">Pass quiz TB</span>
        </div>
      </div>

      <div className="ia-toolbar">
        <div className="ia-toolbar__field">
          <label className="ia-label" htmlFor="ia-range">Khoảng thời gian</label>
          <select id="ia-range" className="ia-select" value={timeRange} onChange={(e) => setTimeRange(e.target.value)}>
            <option value="day">Theo ngày</option>
            <option value="week">Theo tuần</option>
            <option value="month">Theo tháng</option>
          </select>
        </div>
        <Button variant="outline" size="sm" onClick={() => navigate('/dashboard/instructor/quizzes')}>
          Quản lý quiz
        </Button>
        <Button variant="outline" size="sm" onClick={() => navigate('/dashboard/instructor/classes')}>
          Quản lý lớp
        </Button>
      </div>

      {chartData.length > 0 ? (
        <section className="ia-chart">
          <h2 className="ia-section">Tiến độ học viên</h2>
          <p className="ia-chart-hint">Số bài học và quiz hoàn thành theo thời gian</p>
          <ResponsiveContainer width="100%" height={280}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border-subtle)" />
              <XAxis dataKey="date" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} allowDecimals={false} />
              <Tooltip />
              <Line type="monotone" dataKey="lessons_completed" stroke="var(--gold-500)" name="Bài học" strokeWidth={2} />
              <Line type="monotone" dataKey="quizzes_completed" stroke="#b87333" name="Quiz" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </section>
      ) : (
        <StateView type="empty" message="Chưa có dữ liệu biểu đồ cho khoảng thời gian này" />
      )}

      {classStats?.classes?.length > 0 ? (
        <section className="ia-classes">
          <h2 className="ia-section">Theo lớp</h2>
          <div className="ia-class-list">
            {classStats.classes.map((c) => (
              <div key={c.class_id} className="ia-class-row">
                <span className="ia-class-row__name">{c.class_name}</span>
                <span className="ia-class-row__meta">
                  {c.student_count} HV · {Math.round(c.avg_progress || 0)}% tiến độ
                </span>
              </div>
            ))}
          </div>
        </section>
      ) : (
        <StateView type="empty" message="Chưa có lớp học để hiển thị" />
      )}

      {quizPerf?.quizzes?.length > 0 ? (
        <section className="ia-quizzes">
          <h2 className="ia-section">Hiệu quả quiz ({quizPerf.total_quizzes} bài)</h2>
          <div className="ia-table-wrap">
            <table className="ia-table">
              <thead>
                <tr>
                  <th>Quiz</th>
                  <th>Khóa học</th>
                  <th>Pass rate</th>
                  <th>Điểm TB</th>
                  <th>Lượt làm</th>
                </tr>
              </thead>
              <tbody>
                {quizPerf.quizzes.slice(0, 15).map((q) => (
                  <tr key={q.quiz_id}>
                    <td className="ia-table__title">{q.quiz_title}</td>
                    <td>{q.course_title}</td>
                    <td>{Math.round(q.pass_rate)}%</td>
                    <td>{Math.round(q.avg_score)}%</td>
                    <td>{q.total_attempts}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      ) : (
        <StateView type="empty" message="Chưa có quiz nào để phân tích" action={{ label: 'Tạo quiz', onClick: () => navigate('/dashboard/instructor/quizzes/create') }} />
      )}
    </motion.div>
  )
}

function PageHeader({ onBack }) {
  return (
    <header className="ia-header">
      <button type="button" className="ia-back" onClick={onBack}>
        <svg viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.5" aria-hidden>
          <path d="M15 10H5m0 0 5-5M5 10l5 5" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
        Dashboard giảng viên
      </button>
      <svg className="ia-ornament" viewBox="0 0 48 12" fill="none" aria-hidden>
        <line x1="0" y1="6" x2="16" y2="6" stroke="var(--gold-500)" strokeWidth="1" />
        <circle cx="24" cy="6" r="4" stroke="var(--gold-500)" strokeWidth="1" />
        <line x1="32" y1="6" x2="48" y2="6" stroke="var(--gold-500)" strokeWidth="1" />
      </svg>
      <h1 className="ia-title">Analytics giảng viên</h1>
      <p className="ia-subtitle">Theo dõi tiến độ lớp, hoạt động học viên và hiệu quả quiz</p>
    </header>
  )
}

export default InstructorAnalyticsPage
