import React from 'react'
import { Link } from 'react-router-dom'
import './Footer.css'

/**
 * Footer — thin editorial footer.
 * Rendered only on public routes (outside /dashboard/*).
 * App.jsx uses useLocation to conditionally render this.
 */
const Footer = () => {
  const year = new Date().getFullYear()

  return (
    <footer className="site-footer" role="contentinfo">
      <div className="site-footer__inner">
        <div className="site-footer__brand">
          <span className="site-footer__mark" aria-hidden="true">◆</span>
          <span className="site-footer__name">AI Learning</span>
        </div>

        <nav className="site-footer__links" aria-label="Footer navigation">
          <Link to="/" className="site-footer__link">Trang chủ</Link>
          <Link to="/auth/login" className="site-footer__link">Đăng nhập</Link>
          <Link to="/auth/register" className="site-footer__link">Đăng ký</Link>
        </nav>

        <p className="site-footer__copy">
          © {year} AI Learning Platform
        </p>
      </div>
    </footer>
  )
}

export default Footer
