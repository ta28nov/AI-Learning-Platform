import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import classService from '@services/classService'
import Button from '@components/ui/Button'
import Card, { CardBody } from '@components/ui/Card'

/**
 * Trang danh sach lop hoc (Instructor)
 * Route: /dashboard/classes
 * API: GET /classes/my-classes
 */
const ClassListPage = () => {
  const navigate = useNavigate()
  const [classes, setClasses] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchClasses = async () => {
      try {
        setLoading(true)
        const data = await classService.getMyClasses()
        setClasses(data.classes || data || [])
      } catch (error) {
        toast.error('Khong the tai danh sach lop hoc')
      } finally {
        setLoading(false)
      }
    }
    fetchClasses()
  }, [])

  if (loading) return <div style={{ padding: 24, textAlign: 'center' }}>Dang tai...</div>

  return (
    <div style={{ padding: 16 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
        <div>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 700 }}>Lop hoc cua toi</h1>
          <p style={{ color: '#6b7280', fontSize: '0.85rem' }}>{classes.length} lop hoc</p>
        </div>
        <Button onClick={() => navigate('/dashboard/classes/create')}>
          + Tao lop moi
        </Button>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
        {classes.map((cls) => (
          <Card
            key={cls.id}
            hover
            onClick={() => navigate(`/dashboard/classes/${cls.id}`)}
          >
            <CardBody>
              <h3 style={{ fontWeight: 600, marginBottom: 4 }}>{cls.name}</h3>
              <p style={{ fontSize: '0.8rem', color: '#6b7280', marginBottom: 8 }}>
                {cls.course_title}
              </p>
              <div style={{ display: 'flex', gap: 12, fontSize: '0.75rem', color: '#6b7280' }}>
                <span>{cls.student_count}</span>
                <span>{cls.status}</span>
              </div>
            </CardBody>
          </Card>
        ))}
        {classes.length === 0 && (
          <div style={{ textAlign: 'center', padding: 40, color: '#6b7280' }}>
            Ban chua co lop hoc nao. Hay tao lop moi!
          </div>
        )}
      </div>
    </div>
  )
}

export default ClassListPage
