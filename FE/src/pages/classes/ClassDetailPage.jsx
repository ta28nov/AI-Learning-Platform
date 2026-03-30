import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import classService from '@services/classService'
import Button from '@components/ui/Button'
import Card, { CardHeader, CardBody } from '@components/ui/Card'
import './ClassDetailPage.css'

/**
 * Trang chi tiết lớp học (Instructor)
 * Route: /dashboard/classes/:classId
 * API: GET /classes/{classId}, GET /classes/{classId}/students
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
          classService.getStudents(classId).catch(() => ({ data: [] }))
        ])
        setClassData(detail)
        setStudents(studentList.data || [])
      } catch (error) {
        toast.error('Không thể tải thông tin lớp học')
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [classId])

  if (loading) return <div className="class-detail-state">Đang tải...</div>
  if (!classData) return <div className="class-detail-state">Không tìm thấy lớp học</div>

  const tabs = [
    { id: 'info', label: 'Thông tin' },
    { id: 'students', label: `Học viên (${students.length})` }
  ]

  return (
    <div className="class-detail-page">
      <div className="class-detail-header">
        <Button variant="ghost" onClick={() => navigate('/dashboard/classes')}>← Quay lại</Button>
        <h1 className="class-detail-header__title">{classData.name}</h1>
      </div>

      {/* Tabs */}
      <div className="class-detail-tabs">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            className={`class-detail-tab ${activeTab === tab.id ? 'class-detail-tab--active' : ''}`}
            onClick={() => setActiveTab(tab.id)}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab: Thông tin */}
      {activeTab === 'info' && (
        <div className="class-detail-info">
          <Card>
            <CardBody>
              <div className="class-detail-info-grid">
                <div className="class-detail-info-item">
                  <strong>Mã mời:</strong>{' '}
                  <code className="class-detail-invite-code">{classData.invite_code}</code>
                </div>
                <div className="class-detail-info-item">
                  <strong>Trạng thái:</strong> {classData.status}
                </div>
                <div className="class-detail-info-item">
                  <strong>Khóa học:</strong> {classData.course?.title}
                </div>
                <div className="class-detail-info-item">
                  {/* student_count la string "25/30" hoac int tuy endpoint */}
                  <strong>Số học viên:</strong> {classData.student_count}
                </div>
                <div className="class-detail-info-item">
                  <strong>Bắt đầu:</strong>{' '}
                  {classData.start_date ? new Date(classData.start_date).toLocaleDateString('vi-VN') : '-'}
                </div>
                <div className="class-detail-info-item">
                  <strong>Kết thúc:</strong>{' '}
                  {classData.end_date ? new Date(classData.end_date).toLocaleDateString('vi-VN') : '-'}
                </div>
              </div>
            </CardBody>
          </Card>

          {classData.class_stats && (
            <Card>
              <CardHeader><h3>Thống kê</h3></CardHeader>
              <CardBody>
                <div className="class-detail-stats">
                  <div>
                    <div className="class-detail-stat__value">{classData.class_stats.total_students}</div>
                    <div className="class-detail-stat__label">Học viên</div>
                  </div>
                  <div>
                    <div className="class-detail-stat__value">{classData.class_stats.lessons_completed || 0}</div>
                    <div className="class-detail-stat__label">Bài hoàn thành</div>
                  </div>
                  <div>
                    <div className="class-detail-stat__value">{classData.class_stats.avg_quiz_score || 0}</div>
                    <div className="class-detail-stat__label">Điểm TB quiz</div>
                  </div>
                </div>
              </CardBody>
            </Card>
          )}
        </div>
      )}

      {/* Tab: Học viên */}
      {activeTab === 'students' && (
        <Card>
          <CardBody>
            {students.length === 0 ? (
              <p className="class-detail-empty">Chưa có học viên nào</p>
            ) : (
              <div className="class-detail-table-wrap">
                <table className="class-detail-table">
                  <thead>
                    <tr>
                      <th>Học viên</th>
                      <th>Email</th>
                      <th>Tiến độ</th>
                      <th>Điểm quiz TB</th>
                    </tr>
                  </thead>
                  <tbody>
                    {students.map((student) => (
                      <tr key={student.student_id}>
                        <td>{student.student_name}</td>
                        <td>{student.email}</td>
                        <td>{student.progress}%</td>
                        <td>{student.quiz_average || '-'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </CardBody>
        </Card>
      )}
    </div>
  )
}

export default ClassDetailPage
