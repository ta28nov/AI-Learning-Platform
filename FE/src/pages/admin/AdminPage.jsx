import React from 'react'
import Card, { CardHeader, CardBody } from '@components/ui/Card'
import Button from '@components/ui/Button'

/**
 * Component AdminPage - Trang quản trị
 */
const AdminPage = () => {
  return (
    <div className="admin-page">
      <div className="page-header">
        <h1>Quản trị hệ thống</h1>
        <p>Quản lý toàn bộ hệ thống</p>
      </div>

      <div className="admin-content">
        <div className="admin-grid">
          <Card>
            <CardHeader>
              <h3>Quản lý người dùng</h3>
            </CardHeader>
            <CardBody>
              <p>Quản lý tài khoản người dùng</p>
              <Button>Xem chi tiết</Button>
            </CardBody>
          </Card>

          <Card>
            <CardHeader>
              <h3>Quản lý khóa học</h3>
            </CardHeader>
            <CardBody>
              <p>Quản lý tất cả khóa học</p>
              <Button>Xem chi tiết</Button>
            </CardBody>
          </Card>

          <Card>
            <CardHeader>
              <h3>Thống kê hệ thống</h3>
            </CardHeader>
            <CardBody>
              <p>Xem thống kê và báo cáo</p>
              <Button>Xem chi tiết</Button>
            </CardBody>
          </Card>

          <Card>
            <CardHeader>
              <h3>Cài đặt hệ thống</h3>
            </CardHeader>
            <CardBody>
              <p>Cấu hình hệ thống</p>
              <Button>Cài đặt</Button>
            </CardBody>
          </Card>
        </div>
      </div>
    </div>
  )
}

export default AdminPage