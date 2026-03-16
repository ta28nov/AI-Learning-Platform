import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import classService from '@services/classService'
import Button from '@components/ui/Button'
import Card, { CardHeader, CardBody } from '@components/ui/Card'

/**
 * Trang chi tiet lop hoc (Instructor)
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
        toast.error('Khong the tai thong tin lop hoc')
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [classId])

  if (loading) return <div style={{ padding: 24, textAlign: 'center' }}>Dang tai...</div>
  if (!classData) return <div style={{ padding: 24, textAlign: 'center' }}>Khong tim thay lop hoc</div>

  const tabs = [
    { id: 'info', label: 'Thong tin' },
    { id: 'students', label: `Hoc vien (${students.length})` },
  ]

  return (
    <div style={{ padding: 16 }}>
      <div style={{ marginBottom: 20 }}>
        <Button variant="ghost" onClick={() => navigate('/dashboard/classes')}>← Quay lai</Button>
        <h1 style={{ fontSize: '1.5rem', fontWeight: 700, marginTop: 8 }}>{classData.name}</h1>
      </div>

      {/* Tabs */}
      <div style={{ display: 'flex', gap: 4, marginBottom: 16, borderBottom: '1px solid #e5e7eb' }}>
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            style={{
              padding: '10px 16px', border: 'none', background: 'none', cursor: 'pointer',
              fontWeight: activeTab === tab.id ? 600 : 400,
              borderBottom: activeTab === tab.id ? '2px solid #6366f1' : '2px solid transparent',
              color: activeTab === tab.id ? '#6366f1' : '#6b7280', fontSize: '0.85rem'
            }}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab: Thong tin */}
      {activeTab === 'info' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          <Card>
            <CardBody>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, fontSize: '0.85rem' }}>
                <div><strong>Ma moi:</strong> <code style={{ background: '#f3f4f6', padding: '2px 8px', borderRadius: 4, fontWeight: 600 }}>{classData.invite_code}</code></div>
                <div><strong>Trang thai:</strong> {classData.status}</div>
                <div><strong>Khoa hoc:</strong> {classData.course?.title}</div>
                <div><strong>So hoc vien:</strong> {classData.student_count}</div>
                <div><strong>Bat dau:</strong> {classData.start_date ? new Date(classData.start_date).toLocaleDateString('vi') : '-'}</div>
                <div><strong>Ket thuc:</strong> {classData.end_date ? new Date(classData.end_date).toLocaleDateString('vi') : '-'}</div>
              </div>
            </CardBody>
          </Card>

          {classData.class_stats && (
            <Card>
              <CardHeader><h3>Thong ke</h3></CardHeader>
              <CardBody>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 12, textAlign: 'center' }}>
                  <div>
                    <div style={{ fontSize: '1.5rem', fontWeight: 700 }}>{classData.class_stats.total_students}</div>
                    <div style={{ fontSize: '0.75rem', color: '#6b7280' }}>Hoc vien</div>
                  </div>
                  <div>
                    <div style={{ fontSize: '1.5rem', fontWeight: 700 }}>{classData.class_stats.lessons_completed || 0}</div>
                    <div style={{ fontSize: '0.75rem', color: '#6b7280' }}>Bai hoan thanh</div>
                  </div>
                  <div>
                    <div style={{ fontSize: '1.5rem', fontWeight: 700 }}>{classData.class_stats.avg_quiz_score || 0}</div>
                    <div style={{ fontSize: '0.75rem', color: '#6b7280' }}>Diem TB quiz</div>
                  </div>
                </div>
              </CardBody>
            </Card>
          )}
        </div>
      )}

      {/* Tab: Hoc vien */}
      {activeTab === 'students' && (
        <Card>
          <CardBody>
            {students.length === 0 ? (
              <p style={{ textAlign: 'center', color: '#6b7280', padding: 20 }}>Chua co hoc vien nao</p>
            ) : (
              <div style={{ overflowX: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
                  <thead>
                    <tr style={{ borderBottom: '1px solid #e5e7eb' }}>
                      <th style={{ textAlign: 'left', padding: '8px 12px', fontWeight: 600 }}>Hoc vien</th>
                      <th style={{ textAlign: 'left', padding: '8px 12px', fontWeight: 600 }}>Email</th>
                      <th style={{ textAlign: 'right', padding: '8px 12px', fontWeight: 600 }}>Tien do</th>
                      <th style={{ textAlign: 'right', padding: '8px 12px', fontWeight: 600 }}>Diem quiz TB</th>
                    </tr>
                  </thead>
                  <tbody>
                    {students.map((student) => (
                      <tr key={student.student_id} style={{ borderBottom: '1px solid #f3f4f6' }}>
                        <td style={{ padding: '10px 12px' }}>{student.student_name}</td>
                        <td style={{ padding: '10px 12px', color: '#6b7280' }}>{student.email}</td>
                        <td style={{ padding: '10px 12px', textAlign: 'right' }}>{student.progress}%</td>
                        <td style={{ padding: '10px 12px', textAlign: 'right' }}>{student.quiz_average || '-'}</td>
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
