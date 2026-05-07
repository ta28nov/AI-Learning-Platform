import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import Button from '@components/ui/Button'
import './ErrorPages.css'

const CompassIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="10"/>
    <polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76"/>
  </svg>
)

/**
 * NotFoundPage — Trang 404
 * Route: /404 + catch-all *
 */
const NotFoundPage = () => {
  return (
    <div className="error-page">
      <div className="error-page__bg">
        <div className="error-orb error-orb--1" />
        <div className="error-orb error-orb--2" />
      </div>
      <motion.div
        className="error-content"
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, ease: [0.65, 0, 0.35, 1] }}
      >
        <div className="error-code">
          <span className="error-code__digit">4</span>
          <span className="error-code__circle">
            <CompassIcon />
          </span>
          <span className="error-code__digit">4</span>
        </div>
        <h1 className="error-title">Trang không tồn tại</h1>
        <p className="error-desc">
          Xin lỗi, trang bạn đang tìm kiếm không tồn tại hoặc đã được di chuyển.
          Hãy quay lại trang chính để tiếp tục.
        </p>
        <div className="error-actions">
          <Link to="/">
            <Button variant="primary" size="lg">Về trang chủ</Button>
          </Link>
          <Link to="/dashboard">
            <Button variant="outline" size="lg">Về Dashboard</Button>
          </Link>
        </div>
      </motion.div>
    </div>
  )
}

export default NotFoundPage
