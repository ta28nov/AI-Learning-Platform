import React from 'react'
import Card, { CardHeader, CardBody } from '@components/ui/Card'
import Button from '@components/ui/Button'

/**
 * Component InstructorDashboardPage - Trang dashboard giảng viên
 */
const InstructorDashboardPage = () => {
  return (
    <div className="instructor-dashboard-page">
      <div className="page-header">
        <h1>Dashboard Giảng viên</h1>
        <p>Quản lý khóa học và học viên</p>
      </div>

      <div className="instructor-content">
        <div className="dashboard-grid">
          <Card>
            <CardHeader>
              <h3>Khóa học của tôi</h3>
            </CardHeader>
            <CardBody>
              <p>Quản lý các khóa học bạn đang giảng dạy</p>
              <Button>Xem tất cả</Button>
            </CardBody>
          </Card>

          <Card>
            <CardHeader>
              <h3>Học viên</h3>
            </CardHeader>
            <CardBody>
              <p>Theo dõi tiến độ học viên</p>
              <Button>Xem chi tiết</Button>
            </CardBody>
          </Card>

          <Card>
            <CardHeader>
              <h3>Tạo khóa học mới</h3>
            </CardHeader>
            <CardBody>
              <p>Tạo khóa học mới</p>
              <Button>Tạo mới</Button>
            </CardBody>
          </Card>
        </div>
      </div>
    </div>
  )
}

export default InstructorDashboardPage