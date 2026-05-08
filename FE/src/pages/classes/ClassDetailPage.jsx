import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import toast from 'react-hot-toast'
import classService from '@services/classService'
import Button from '@components/ui/Button'
import StateView from '@components/ui/StateView'
import AILoadingState from '@components/ui/AILoadingState'
import './ClassDetailPage.css'

const CopyIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
  </svg>
)

/**
 * ClassDetailPage — Chi tiết lớp học (Instructor)
 * Route: /dashboard/instructor/classes/:classId (InstructorRoute)
 * API: GET /classes/{classId}, GET /classes/{classId}/students via classService — unchanged
 */
const ClassDetailPage = () => {
  const { classId } = useParams()
  const navigate = useNavigate()
  const [classData, setClassData] = useState(null)
  const [students, setStudents] = useState([])
  const [activeTab, setActiveTab] = useState('info')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true)
        const [detail, studentList] = await Promise.all([
          classService.getClassDetail(classId),
          classService.getStudents(classId).catch(() => ({ data: [] })),
        ])
        setClassData(detail)
        setStudents(studentList.data || [])
      } catch {
        toast.error('Không thể tải thông tin lớp học')
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [classId])

  const copyInviteCode = () => {
    navigator.clipboard.writeText(classData?.invite_code || '')
    toast.success('Đã sao chép mã mời')
  }

  if (loading) {
    return (
      <div className="cld-page">
        <AILoadingState
          title="AI đang tải thông tin lớp học"
          message="Đang đồng bộ chi tiết lớp và danh sách học viên."
          steps={[
            'Đang tải thông tin lớp học...',
            'Đang tải danh sách học viên...',
            'Đang sắp xếp dữ liệu hiển thị...',
          ]}
        />
      </div>
    )
  }
  if (!classData) return (
    <div className="cld-page">
      <StateView type="empty" message="Không tìm thấy lớp học" action={{ label: 'Quay lại', onClick: () => navigate('/dashboard/instructor/classes') }} />
    </div>
  )

  const tabs = [
    { id: 'info', label: 'Thông tin' },
    { id: 'students', label: `Học viên (${students.length})` },
  ]

  const statusLabel = { active: 'Đang hoạt động', completed: 'Đã kết thúc', preparing: 'Chuẩn bị', cancelled: 'Đã hủy' }
  const statusClass = { active: 'cld-status--active', completed: 'cld-status--completed', cancelled: 'cld-status--cancelled', preparing: 'cld-status--preparing' }

  return (
    <div className="cld-page">
      {/* Header */}
      <motion.div className="cld-header" initial={{ opacity: 0, y: 24 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5, ease: [0.65, 0, 0.35, 1] }}>
        <button className="cld-back" onClick={() => navigate('/dashboard/instructor/classes')}>
          <svg viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.5">
            <path d="M15 10H5m0 0 5-5M5 10l5 5" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
          Danh sách lớp
        </button>
        <div className="cld-header__row">
          <h1 className="cld-title">{classData.name}</h1>
          <span className={`cld-status ${statusClass[classData.status] || ''}`}>
            {statusLabel[classData.status] ?? classData.status}
          </span>
        </div>
        {classData.course?.title && <p className="cld-subtitle">Khóa học: {classData.course.title}</p>}
      </motion.div>

      {/* Tabs */}
      <div className="cld-tabs">
        {tabs.map(tab => (
          <button
            key={tab.id}
            className={`cld-tab ${activeTab === tab.id ? 'cld-tab--active' : ''}`}
            onClick={() => setActiveTab(tab.id)}
          >
            {tab.label}
          </button>
        ))}
      </div>

      <AnimatePresence mode="wait">
        {activeTab === 'info' && (
          <motion.div
            key="info"
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            transition={{ duration: 0.3 }}
          >
            {/* Invite code */}
            <div className="cld-invite">
              <span className="cld-invite__label">Mã mời lớp</span>
              <div className="cld-invite__row">
                <code className="cld-invite__code">{classData.invite_code}</code>
                <button className="cld-invite__copy" onClick={copyInviteCode} title="Sao chép">
                  <CopyIcon />
                </button>
              </div>
            </div>

            {/* Info grid */}
            <div className="cld-info-grid">
              {[
                { label: 'Học viên', value: classData.student_count ?? students.length },
                { label: 'Bắt đầu', value: classData.start_date ? new Date(classData.start_date).toLocaleDateString('vi-VN') : '—' },
                { label: 'Kết thúc', value: classData.end_date ? new Date(classData.end_date).toLocaleDateString('vi-VN') : '—' },
              ].map(({ label, value }) => (
                <div key={label} className="cld-info-card">
                  <span className="cld-info-card__label">{label}</span>
                  <span className="cld-info-card__value">{value}</span>
                </div>
              ))}
            </div>

            {/* Stats */}
            {classData.class_stats && (
              <div className="cld-stats">
                <h2 className="cld-section-title">Thống kê</h2>
                <div className="cld-stats-grid">
                  <div className="cld-stat"><span className="cld-stat__value">{classData.class_stats.total_students}</span><span className="cld-stat__label">Học viên</span></div>
                  <div className="cld-stat"><span className="cld-stat__value">{classData.class_stats.lessons_completed || 0}</span><span className="cld-stat__label">Bài hoàn thành</span></div>
                  <div className="cld-stat"><span className="cld-stat__value">{classData.class_stats.avg_quiz_score || 0}</span><span className="cld-stat__label">Điểm TB quiz</span></div>
                </div>
              </div>
            )}
          </motion.div>
        )}

        {activeTab === 'students' && (
          <motion.div
            key="students"
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            transition={{ duration: 0.3 }}
          >
            {students.length === 0 ? (
              <StateView type="empty" message="Chưa có học viên nào trong lớp" />
            ) : (
              <div className="cld-table-wrap">
                <table className="cld-table">
                  <thead>
                    <tr>
                      <th>Học viên</th>
                      <th>Email</th>
                      <th>Tiến độ</th>
                      <th>Quiz TB</th>
                    </tr>
                  </thead>
                  <tbody>
                    {students.map((s) => (
                      <tr key={s.student_id}>
                        <td className="cld-table__name">{s.student_name}</td>
                        <td>{s.email}</td>
                        <td>
                          <div className="cld-progress-cell">
                            <div className="cld-progress-bar">
                              <div className="cld-progress-fill" style={{ width: `${s.progress || 0}%` }} />
                            </div>
                            <span>{s.progress || 0}%</span>
                          </div>
                        </td>
                        <td>{s.quiz_average != null ? `${Math.round(s.quiz_average)}%` : '—'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

export default ClassDetailPage
