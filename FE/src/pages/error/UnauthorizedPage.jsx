import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import Button from '@components/ui/Button'
import './ErrorPages.css'

/**
 * UnauthorizedPage - Trang 403 khong co quyen
 * Route: /unauthorized
 */
const UnauthorizedPage = () => {
  return (
    <div className="error-page error-page--403">
      <div className="error-page__bg">
        <div className="error-orb error-orb--1" />
        <div className="error-orb error-orb--2" />
      </div>
      <motion.div
        className="error-content"
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <div className="error-code">
          <span className="error-code__digit">4</span>
          <span className="error-code__circle error-code__circle--red">
            <span className="error-code__emoji">🔒</span>
          </span>
          <span className="error-code__digit">3</span>
        </div>
        <h1 className="error-title">Khong co quyen truy cap</h1>
        <p className="error-desc">
          Xin loi, ban khong co quyen truy cap vao trang nay.
          Vui long lien he quan tri vien neu ban nghi day la loi.
        </p>
        <div className="error-actions">
          <Link to="/dashboard">
            <Button variant="primary" size="lg">Ve Dashboard</Button>
          </Link>
          <Link to="/">
            <Button variant="outline" size="lg">Ve trang chu</Button>
          </Link>
        </div>
      </motion.div>
    </div>
  )
}

export default UnauthorizedPage
