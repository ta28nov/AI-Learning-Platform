import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import classService from '@services/classService'
import Button from '@components/ui/Button'
import Modal from '@components/ui/Modal'
import './JoinClassModal.css'

/**
 * JoinClassModal - Modal tham gia lớp học bằng mã mời
 * Sử dụng: <JoinClassModal isOpen={...} onClose={...} onSuccess={...} />
 * API: POST /classes/join { invite_code } -> ClassJoinResponse
 * Response: { class_id, class_name, course_title, instructor_name, enrollment_id, course_id }
 */
const JoinClassModal = ({ isOpen, onClose, onSuccess }) => {
  const navigate = useNavigate()
  const [inviteCode, setInviteCode] = useState('')
  const [loading, setLoading] = useState(false)
  const [preview, setPreview] = useState(null) // Thông tin lớp sau khi join

  // Xử lý input mã mời (chỉ chữ và số, viết hoa)
  const handleCodeChange = (e) => {
    const val = e.target.value.toUpperCase().replace(/[^A-Z0-9]/g, '').slice(0, 10)
    setInviteCode(val)
    setPreview(null) // Xóa preview khi nhập lại
  }

  // Xử lý tham gia lớp
  const handleJoin = async () => {
    const code = inviteCode.trim()
    if (!code) {
      toast.error('Vui lòng nhập mã mời lớp học')
      return
    }
    if (code.length < 6) {
      toast.error('Mã mời phải có ít nhất 6 ký tự')
      return
    }

    setLoading(true)
    try {
      const data = await classService.joinClass(code)
      setPreview(data)
      toast.success(`Đã tham gia lớp "${data.class_name}" thành công!`)

      // Callback cho parent component (reload danh sach, ...)
      if (onSuccess) onSuccess(data)

      // Sau 1.5s tự chuyển đến khóa học nếu có
      if (data.course_id) {
        setTimeout(() => {
          handleClose()
          navigate(`/dashboard/courses/${data.course_id}`)
        }, 1500)
      }
    } catch (error) {
      toast.error(error?.message || 'Mã mời không hợp lệ hoặc đã hết hạn')
    } finally {
      setLoading(false)
    }
  }

  // Đóng modal và reset state
  const handleClose = () => {
    setInviteCode('')
    setPreview(null)
    onClose()
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !loading) handleJoin()
  }

  return (
    <Modal isOpen={isOpen} onClose={handleClose} title="Tham gia lớp học">
      {!preview ? (
        <div className="join-class-form">
          <p className="join-class-form__desc">
            Nhập mã mời do giảng viên cung cấp để tham gia lớp học:
          </p>

          <div className="join-class-form__input-wrap">
            <input
              className="join-class-form__input"
              type="text"
              value={inviteCode}
              onChange={handleCodeChange}
              onKeyDown={handleKeyDown}
              placeholder="Ví dụ: ABC123"
              autoFocus
              disabled={loading}
              maxLength={10}
            />
            <span className="join-class-form__hint">
              {inviteCode.length}/10 ký tự
            </span>
          </div>

          <p className="join-class-form__note">
            💡 Mã mời gồm 6–10 ký tự chữ và số, không phân biệt hoa thường
          </p>

          <div className="join-class-form__actions">
            <Button variant="outline" onClick={handleClose} disabled={loading}>
              Hủy
            </Button>
            <Button
              variant="primary"
              onClick={handleJoin}
              loading={loading}
              disabled={loading || inviteCode.length < 6}
            >
              Tham gia lớp học
            </Button>
          </div>
        </div>
      ) : (
        /* Màn hình thành công */
        <div className="join-class-success">
          <div className="join-class-success__icon">🎉</div>
          <h3 className="join-class-success__title">Tham gia thành công!</h3>

          <div className="join-class-success__info">
            <div className="join-class-success__row">
              <span className="join-class-success__label">Lớp học:</span>
              <span className="join-class-success__value">{preview.class_name}</span>
            </div>
            {preview.course_title && (
              <div className="join-class-success__row">
                <span className="join-class-success__label">Khóa học:</span>
                <span className="join-class-success__value">{preview.course_title}</span>
              </div>
            )}
            {preview.instructor_name && (
              <div className="join-class-success__row">
                <span className="join-class-success__label">Giảng viên:</span>
                <span className="join-class-success__value">{preview.instructor_name}</span>
              </div>
            )}
          </div>

          <p className="join-class-success__redirect">
            Đang chuyển đến khóa học...
          </p>

          <div className="join-class-success__actions">
            {preview.course_id && (
              <Button
                variant="primary"
                onClick={() => {
                  handleClose()
                  navigate(`/dashboard/courses/${preview.course_id}`)
                }}
              >
                Xem khóa học ngay
              </Button>
            )}
            <Button variant="outline" onClick={handleClose}>
              Đóng
            </Button>
          </div>
        </div>
      )}
    </Modal>
  )
}

export default JoinClassModal
