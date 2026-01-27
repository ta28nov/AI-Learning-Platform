import React from 'react'
import Card, { CardHeader, CardBody } from '@components/ui/Card'

/**
 * Component DashboardPage - Trang dashboard chính
 */
const DashboardPage = () => {
  return (
    <div className="dashboard-page">
      <div className="page-header">
        <h1>Dashboard</h1>
        <p>Chào mừng bạn đến với trang quản lý</p>
      </div>

      <div className="dashboard-content">
        <div className="dashboard-grid">
          <Card>
            <CardHeader>
              <h3>Khóa học của tôi</h3>
            </CardHeader>
            <CardBody>
              <p>Quản lý các khóa học bạn đã đăng ký</p>
            </CardBody>
          </Card>

          <Card>
            <CardHeader>
              <h3>Tiến độ học tập</h3>
            </CardHeader>
            <CardBody>
              <p>Theo dõi tiến độ học tập của bạn</p>
            </CardBody>
          </Card>

          <Card>
            <CardHeader>
              <h3>Bài quiz</h3>
            </CardHeader>
            <CardBody>
              <p>Thực hành với các bài quiz</p>
            </CardBody>
          </Card>

          <Card>
            <CardHeader>
              <h3>Trò chuyện</h3>
            </CardHeader>
            <CardBody>
              <p>Tương tác với AI và cộng đồng</p>
            </CardBody>
          </Card>
        </div>
      </div>
    </div>
  )
}

export default DashboardPage