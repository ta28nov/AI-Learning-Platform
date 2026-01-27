import React from 'react'
import Card, { CardHeader, CardBody } from '@components/ui/Card'
import Button from '@components/ui/Button'

/**
 * Component MyCoursesPage - Trang khóa học của tôi
 */
const MyCoursesPage = () => {
  return (
    <div className="my-courses-page">
      <div className="page-header">
        <h1>Khóa học của tôi</h1>
        <p>Quản lý các khóa học bạn đã đăng ký</p>
      </div>

      <div className="my-courses-content">
        <Card>
          <CardHeader>
            <h3>Khóa học đã đăng ký</h3>
          </CardHeader>
          <CardBody>
            <p>Bạn chưa đăng ký khóa học nào</p>
            <Button>Khám phá khóa học</Button>
          </CardBody>
        </Card>

        <Card>
          <CardHeader>
            <h3>Khóa học đã hoàn thành</h3>
          </CardHeader>
          <CardBody>
            <p>Chưa có khóa học nào được hoàn thành</p>
          </CardBody>
        </Card>
      </div>
    </div>
  )
}

export default MyCoursesPage