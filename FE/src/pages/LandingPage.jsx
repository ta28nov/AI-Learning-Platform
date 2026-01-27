import React from 'react'
import { Link } from 'react-router-dom'
import Button from '@components/ui/Button'
import Card from '@components/ui/Card'
import './LandingPage.css'

/**
 * Component LandingPage - Trang chu gioi thieu he thong
 */
const LandingPage = () => {
  return (
    <div className="landing-page">
      {/* Header */}
      <header className="landing-header">
        <div className="container">
          <div className="header-content">
            <div className="logo">
              <h2>AI Learning Platform</h2>
            </div>
            <nav className="header-nav">
              <Link to="/auth/login" className="nav-link">Dang nhap</Link>
              <Link to="/auth/register">
                <Button variant="primary">Dang ky</Button>
              </Link>
            </nav>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="hero-section">
        <div className="container">
          <div className="hero-content">
            <h1 className="hero-title">
              Nen tang hoc tap AI thong minh
            </h1>
            <p className="hero-description">
              Khám phá và nâng cao kỹ năng của bạn với các khóa học được cá nhân hóa 
              bởi trí tuệ nhân tạo. Học tập hiệu quả hơn với lộ trình được thiết kế riêng cho bạn.
            </p>
            <div className="hero-actions">
              <Link to="/auth/register">
                <Button variant="primary" size="lg">
                  Bat dau hoc tap
                </Button>
              </Link>
              <Link to="/courses">
                <Button variant="outline" size="lg">
                  Khám phá khóa hoc
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="features-section">
        <div className="container">
          <h2 className="section-title">Tính năng noi bat</h2>
          <div className="features-grid">
            <Card className="feature-card" hover shadow>
              <div className="feature-icon">
                <AIIcon />
              </div>
              <h3>Đánh giá năng lực AI</h3>
              <p>
                Hệ thống AI tự động đánh giá năng lực của bạn và đề xuất 
                lộ trình học tập phù hợp nhất.
              </p>
            </Card>

            <Card className="feature-card" hover shadow>
              <div className="feature-icon">
                <PersonalizedIcon />
              </div>
              <h3>Học tập cá nhân hóa</h3>
              <p>
                Nội dung khóa học được điều chỉnh theo trình độ và mục tiêu 
                của từng học viên.
              </p>
            </Card>

            <Card className="feature-card" hover shadow>
              <div className="feature-icon">
                <ProgressIcon />
              </div>
              <h3>Theo dõi tiến độ</h3>
              <p>
                Giám sát tiến độ học tập chi tiết với báo cáo và 
                phân tích hiệu suất học tập.
              </p>
            </Card>

            <Card className="feature-card" hover shadow>
              <div className="feature-icon">
                <ChatIcon />
              </div>
              <h3>AI Chat hỗ trợ</h3>
              <p>
                Trợ lý AI luôn sẵn sàng giải đáp thắc mắc và hướng dẫn 
                trong quá trình học tập.
              </p>
            </Card>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="cta-section">
        <div className="container">
          <div className="cta-content">
            <h2>Sẵn sàng bắt đầu hành trình học tập?</h2>
            <p>
              Tham gia cùng hàng nghìn học viên đã tin tưởng nền tảng của chúng tôi.
            </p>
            <Link to="/auth/register">
              <Button variant="primary" size="lg">
                Đăng ký miễn phí
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="landing-footer">
        <div className="container">
          <div className="footer-content">
            <div className="footer-brand">
              <h3>AI Learning Platform</h3>
              <p>Nền tảng học tập thông minh cho tương lai</p>
            </div>
            <div className="footer-links">
              <div className="footer-section">
                <h4>Sản phẩm</h4>
                <ul>
                  <li><Link to="/courses">Khóa học</Link></li>
                  <li><Link to="/about">Giới thiệu</Link></li>
                  <li><Link to="/contact">Liên hệ</Link></li>
                </ul>
              </div>
              <div className="footer-section">
                <h4>Hỗ trợ</h4>
                <ul>
                  <li><Link to="/help">Trợ giúp</Link></li>
                  <li><Link to="/faq">FAQ</Link></li>
                  <li><Link to="/contact">Liên hệ</Link></li>
                </ul>
              </div>
            </div>
          </div>
          <div className="footer-bottom">
            <p>&copy; 2025 AI Learning Platform. Bảo lưu mọi quyền.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}

// Simple SVG Icons
const AIIcon = () => (
  <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <circle cx="12" cy="12" r="10"></circle>
    <path d="M8 14s1.5 2 4 2 4-2 4-2"></path>
    <line x1="9" y1="9" x2="9.01" y2="9"></line>
    <line x1="15" y1="9" x2="15.01" y2="9"></line>
  </svg>
)

const PersonalizedIcon = () => (
  <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
    <circle cx="12" cy="7" r="4"></circle>
  </svg>
)

const ProgressIcon = () => (
  <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="M22 12h-4l-3 9L9 3l-3 9H2"></path>
  </svg>
)

const ChatIcon = () => (
  <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
  </svg>
)

export default LandingPage