import React from 'react'
import { useParams } from 'react-router-dom'
import Card, { CardHeader, CardBody } from '@components/ui/Card'
import Button from '@components/ui/Button'

/**
 * Component CourseDetailPage - Trang chi tiết khóa học
 */
const CourseDetailPage = () => {
  const { courseId } = useParams()

  return (
    <div className="course-detail-page">
      <div className="page-header">
        <h1>Chi tiết khóa học</h1>
        <p>Khóa học ID: {courseId}</p>
      </div>

      <div className="course-detail-content">
        <Card>
          <CardHeader>
            <h3>Thông tin khóa học</h3>
          </CardHeader>
          <CardBody>
            <p>Nội dung chi tiết của khóa học sẽ được hiển thị ở đây</p>
            <div className="course-actions">
              <Button>Đăng ký khóa học</Button>
              <Button variant="outline">Xem trước</Button>
            </div>
          </CardBody>
        </Card>

        <Card>
          <CardHeader>
            <h3>Chương trình học</h3>
          </CardHeader>
          <CardBody>
            <p>Danh sách các chương trong khóa học</p>
          </CardBody>
        </Card>
      </div>
    </div>
  )
}

export default CourseDetailPage