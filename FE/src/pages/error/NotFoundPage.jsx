import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import Button from '@components/ui/Button'
import './ErrorPages.css'

/**
 * NotFoundPage - Trang 404 voi thiet ke premium
 * Route: * (catch-all)
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
        transition={{ duration: 0.5 }}
      >
        <div className="error-code">
          <span className="error-code__digit">4</span>
          <span className="error-code__circle">
            <span className="error-code__emoji">🔍</span>
          </span>
          <span className="error-code__digit">4</span>
        </div>
        <h1 className="error-title">Trang khong ton tai</h1>
        <p className="error-desc">
          Xin loi, trang ban dang tim kiem khong ton tai hoac da duoc di chuyen.
          Hay quay lai trang chinh de tiep tuc.
        </p>
        <div className="error-actions">
          <Link to="/">
            <Button variant="primary" size="lg">Ve trang chu</Button>
          </Link>
          <Link to="/dashboard">
            <Button variant="outline" size="lg">Ve Dashboard</Button>
          </Link>
        </div>
      </motion.div>
    </div>
  )
}

export default NotFoundPage
