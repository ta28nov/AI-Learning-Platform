import React from 'react'
import { useParams } from 'react-router-dom'
import Card, { CardHeader, CardBody } from '@components/ui/Card'
import Button from '@components/ui/Button'

/**
 * Component StudentEnrollmentPage - Trang đăng ký khóa học của học viên
 */
const StudentEnrollmentPage = () => {
  const { enrollmentId } = useParams()

  return (
    <div className="student-enrollment-page">
      <div className="page-header">
        <h1>Chi tiết đăng ký</h1>
        <p>Mã đăng ký: {enrollmentId}</p>
      </div>

      <div className="enrollment-content">
        <Card>
          <CardHeader>
            <h3>Thông tin đăng ký</h3>
          </CardHeader>
          <CardBody>
            <div className="enrollment-info">
              <div className="info-item">
                <label>Khóa học:</label>
                <span>Đang tải...</span>
              </div>
              <div className="info-item">
                <label>Ngày đăng ký:</label>
                <span>Đang tải...</span>
              </div>
              <div className="info-item">
                <label>Trạng thái:</label>
                <span>Đang học</span>
              </div>
            </div>
            <div className="enrollment-actions">
              <Button>Tiếp tục học</Button>
              <Button variant="outline">Xem tiến độ</Button>
            </div>
          </CardBody>
        </Card>
      </div>
    </div>
  )
}

export default StudentEnrollmentPage