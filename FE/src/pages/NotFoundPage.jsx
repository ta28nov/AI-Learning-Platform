import React from 'react'
import { Link } from 'react-router-dom'
import Button from '@components/ui/Button'
import './ErrorPages.css'

/**
 * Component NotFoundPage - Trang 404
 */
const NotFoundPage = () => {
  return (
    <div className="error-page">
      <div className="error-container">
        <div className="error-content">
          <div className="error-illustration">
            <div className="error-code">404</div>
          </div>
          
          <h1 className="error-title">
            Trang không tồn tại
          </h1>
          
          <p className="error-description">
            Xin lỗi, trang bạn đang tìm kiếm không tồn tại hoặc đã được di chuyển.
          </p>
          
          <div className="error-actions">
            <Link to="/">
              <Button variant="primary" size="lg">
                Về trang chủ
              </Button>
            </Link>
            <Link to="/dashboard">
              <Button variant="outline" size="lg">
                Về dashboard
              </Button>
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}

export default NotFoundPage