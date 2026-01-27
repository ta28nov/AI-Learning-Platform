import React from 'react'
import Card, { CardHeader, CardBody } from '@components/ui/Card'
import Button from '@components/ui/Button'

/**
 * Component ProfilePage - Trang thông tin cá nhân
 */
const ProfilePage = () => {
  return (
    <div className="profile-page">
      <div className="page-header">
        <h1>Thông tin cá nhân</h1>
        <p>Quản lý thông tin tài khoản của bạn</p>
      </div>

      <div className="profile-content">
        <Card>
          <CardHeader>
            <h3>Thông tin tài khoản</h3>
          </CardHeader>
          <CardBody>
            <div className="profile-info">
              <div className="info-item">
                <label>Họ và tên:</label>
                <span>Người dùng</span>
              </div>
              <div className="info-item">
                <label>Email:</label>
                <span>user@example.com</span>
              </div>
              <div className="info-item">
                <label>Vai trò:</label>
                <span>Học viên</span>
              </div>
            </div>
            <div className="profile-actions">
              <Button variant="outline">Chỉnh sửa thông tin</Button>
              <Button variant="outline">Đổi mật khẩu</Button>
            </div>
          </CardBody>
        </Card>
      </div>
    </div>
  )
}

export default ProfilePage