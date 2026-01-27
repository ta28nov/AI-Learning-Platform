import React from 'react'
import Card, { CardHeader, CardBody } from '@components/ui/Card'
import Button from '@components/ui/Button'

/**
 * Component CoursesPage - Trang danh sách khóa học
 */
const CoursesPage = () => {
  return (
    <div className="courses-page">
      <div className="page-header">
        <h1>Khóa học</h1>
        <p>Khám phá các khóa học có sẵn</p>
      </div>

      <div className="courses-content">
        <div className="courses-grid">
          <Card>
            <CardHeader>
              <h3>Khóa học mẫu 1</h3>
            </CardHeader>
            <CardBody>
              <p>Mô tả khóa học mẫu</p>
              <Button>Xem chi tiết</Button>
            </CardBody>
          </Card>

          <Card>
            <CardHeader>
              <h3>Khóa học mẫu 2</h3>
            </CardHeader>
            <CardBody>
              <p>Mô tả khóa học mẫu</p>
              <Button>Xem chi tiết</Button>
            </CardBody>
          </Card>
        </div>
      </div>
    </div>
  )
}

export default CoursesPage