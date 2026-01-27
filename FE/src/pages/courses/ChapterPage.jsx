import React from 'react'
import { useParams } from 'react-router-dom'
import Card, { CardHeader, CardBody } from '@components/ui/Card'
import Button from '@components/ui/Button'

/**
 * Component ChapterPage - Trang chương học
 */
const ChapterPage = () => {
  const { courseId, chapterId } = useParams()

  return (
    <div className="chapter-page">
      <div className="page-header">
        <h1>Chương học</h1>
        <p>Khóa học: {courseId} - Chương: {chapterId}</p>
      </div>

      <div className="chapter-content">
        <Card>
          <CardHeader>
            <h3>Nội dung chương</h3>
          </CardHeader>
          <CardBody>
            <p>Nội dung chi tiết của chương học sẽ được hiển thị ở đây</p>
            <div className="chapter-actions">
              <Button variant="outline">Chương trước</Button>
              <Button>Chương tiếp theo</Button>
            </div>
          </CardBody>
        </Card>

        <Card>
          <CardHeader>
            <h3>Bài tập</h3>
          </CardHeader>
          <CardBody>
            <p>Các bài tập của chương này</p>
          </CardBody>
        </Card>
      </div>
    </div>
  )
}

export default ChapterPage