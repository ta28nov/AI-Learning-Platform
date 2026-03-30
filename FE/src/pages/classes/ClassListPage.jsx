import { useState, useEffect, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import classService from '@services/classService'
import { useAuthStore } from '@stores/authStore'
import Button from '@components/ui/Button'
import Card, { CardBody } from '@components/ui/Card'
import JoinClassModal from '@components/classes/JoinClassModal'
import './ClassListPage.css'

/**
 * Trang danh sách lớp học
 * Instructor: xem danh sach, tao lop moi
 * Student: xem danh sach, tham gia lop bang ma moi (JoinClassModal)
 * API: GET /classes/my-classes
 * student_count tra ve dang string "25/30" (so hien tai/toi da)
 */
const ClassListPage = () => {
  const navigate = useNavigate()
  const { user } = useAuthStore()
  const [classes, setClasses] = useState([])
  const [loading, setLoading] = useState(true)
  const [joinModalOpen, setJoinModalOpen] = useState(false)

  // Lay danh sach lop khi mount
  const fetchClasses = useCallback(async () => {
    try {
      setLoading(true)
      const data = await classService.getMyClasses()
      setClasses(data.classes || data || [])
    } catch (error) {
      toast.error('Không thể tải danh sách lớp học')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchClasses()
  }, [fetchClasses])

  if (loading) return <div className="class-list-loading">Đang tải...</div>

  return (
    <div className="class-list-page">
      <div className="class-list-header">
        <div>
          <h1 className="class-list-header__title">Lớp học của tôi</h1>
          <p className="class-list-header__count">{classes.length} lớp học</p>
        </div>
        <div style={{ display: 'flex', gap: 8 }}>
          {/* Student: tham gia lop bang ma moi */}
          {user?.role === 'student' && (
            <Button variant="outline" onClick={() => setJoinModalOpen(true)}>
              🔑 Tham gia lớp
            </Button>
          )}
          {/* Instructor: tao lop moi */}
          {(user?.role === 'instructor' || user?.role === 'admin') && (
            <Button onClick={() => navigate('/dashboard/classes/create')}>
              + Tạo lớp mới
            </Button>
          )}
        </div>
      </div>

      <div className="class-list">
        {classes.map((cls) => (
          <Card
            key={cls.id}
            hover
            className="class-card"
            onClick={() => navigate(`/dashboard/classes/${cls.id}`)}
          >
            <CardBody>
              <h3 className="class-card__name">{cls.name}</h3>
              <p className="class-card__course">{cls.course_title}</p>
              <div className="class-card__meta">
                {/* student_count la string "25/30" theo BE schema */}
                <span>👥 {cls.student_count} học viên</span>
                <span className={`class-card__status ${cls.status === 'completed' ? 'class-card__status--completed' : cls.status === 'cancelled' ? 'class-card__status--cancelled' : ''}`}>
                  {cls.status === 'active' ? 'Đang hoạt động'
                    : cls.status === 'completed' ? 'Đã kết thúc'
                    : cls.status === 'preparing' ? 'Chuẩn bị'
                    : cls.status || 'Không rõ'}
                </span>
                {cls.start_date && (
                  <span>Bắt đầu: {new Date(cls.start_date).toLocaleDateString('vi-VN')}</span>
                )}
              </div>
              {/* Thanh tiến độ nếu có progress */}
              {cls.progress != null && (
                <div className="class-card__progress-wrap">
                  <div className="class-card__progress-bar">
                    <div
                      className="class-card__progress-fill"
                      style={{ width: `${cls.progress}%` }}
                    />
                  </div>
                </div>
              )}
            </CardBody>
          </Card>
        ))}
        {classes.length === 0 && (
          <div className="class-list-empty">
            {user?.role === 'student'
              ? 'Bạn chưa tham gia lớp học nào. Hãy nhập mã mời để tham gia!'
              : 'Bạn chưa có lớp học nào. Hãy tạo lớp mới!'}
          </div>
        )}
      </div>

      {/* Modal tham gia lớp học bằng mã mời */}
      <JoinClassModal
        isOpen={joinModalOpen}
        onClose={() => setJoinModalOpen(false)}
        onSuccess={() => fetchClasses()}
      />
    </div>
  )
}

export default ClassListPage
