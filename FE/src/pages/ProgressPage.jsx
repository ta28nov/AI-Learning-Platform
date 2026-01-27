import React from 'react'
import Card, { CardHeader, CardBody } from '@components/ui/Card'

/**
 * Component ProgressPage - Trang tiến độ học tập
 */
const ProgressPage = () => {
  return (
    <div className="progress-page">
      <div className="page-header">
        <h1>Tiến độ học tập</h1>
        <p>Theo dõi quá trình học tập của bạn</p>
      </div>

      <div className="progress-content">
        <Card>
          <CardHeader>
            <h3>Tổng quan tiến độ</h3>
          </CardHeader>
          <CardBody>
            <div className="progress-stats">
              <div className="stat-item">
                <div className="stat-number">0</div>
                <div className="stat-label">Khóa học đã hoàn thành</div>
              </div>
              <div className="stat-item">
                <div className="stat-number">0</div>
                <div className="stat-label">Bài quiz đã làm</div>
              </div>
              <div className="stat-item">
                <div className="stat-number">0%</div>
                <div className="stat-label">Tiến độ tổng thể</div>
              </div>
            </div>
          </CardBody>
        </Card>

        <Card>
          <CardHeader>
            <h3>Khóa học đang học</h3>
          </CardHeader>
          <CardBody>
            <p>Bạn chưa đăng ký khóa học nào</p>
          </CardBody>
        </Card>
      </div>
    </div>
  )
}

export default ProgressPage