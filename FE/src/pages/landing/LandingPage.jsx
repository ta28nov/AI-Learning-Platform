import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import Button from '@components/ui/Button'
import './LandingPage.css'

/**
 * LandingPage - Trang chu gioi thieu he thong hoc tap AI
 * Route: /
 * Premium design voi glassmorphism, gradient, animations
 */
const LandingPage = () => {
  const [scrolled, setScrolled] = useState(false)

  // Theo doi scroll de doi style header
  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 50)
    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  // Animation variants cho framer-motion
  const fadeUp = {
    hidden: { opacity: 0, y: 30 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.6 } }
  }

  const stagger = {
    visible: { transition: { staggerChildren: 0.15 } }
  }

  return (
    <div className="landing">
      {/* ========== HEADER ========== */}
      <header className={`landing-header ${scrolled ? 'landing-header--scrolled' : ''}`}>
        <div className="landing-container">
          <div className="landing-header__inner">
            <Link to="/" className="landing-logo">
              <div className="landing-logo__icon">AI</div>
              <span className="landing-logo__text">LearnAI</span>
            </Link>
            <nav className="landing-nav">
              <a href="#features" className="landing-nav__link">Tinh nang</a>
              <a href="#stats" className="landing-nav__link">Thanh tuu</a>
              <a href="#how-it-works" className="landing-nav__link">Cach hoat dong</a>
              <Link to="/auth/login" className="landing-nav__link">Dang nhap</Link>
              <Link to="/auth/register">
                <Button variant="primary" size="sm">Bat dau mien phi</Button>
              </Link>
            </nav>
          </div>
        </div>
      </header>

      {/* ========== HERO ========== */}
      <section className="hero">
        <div className="hero__bg">
          <div className="hero__orb hero__orb--1" />
          <div className="hero__orb hero__orb--2" />
          <div className="hero__orb hero__orb--3" />
        </div>
        <div className="landing-container">
          <motion.div
            className="hero__content"
            initial="hidden"
            animate="visible"
            variants={stagger}
          >
            <motion.div className="hero__badge" variants={fadeUp}>
               Nen tang hoc tap the he moi
            </motion.div>
            <motion.h1 className="hero__title" variants={fadeUp}>
              Hoc tap thong minh hon<br />
              voi <span className="hero__title--gradient">Tri tue nhan tao</span>
            </motion.h1>
            <motion.p className="hero__desc" variants={fadeUp}>
              AI phan tich trinh do cua ban, tao lo trinh ca nhan hoa, 
              va dong hanh suot qua trinh hoc tap. Hieu qua gap 3 lan phuong phap truyen thong.
            </motion.p>
            <motion.div className="hero__actions" variants={fadeUp}>
              <Link to="/auth/register">
                <Button variant="primary" size="lg">Bat dau hoc tap →</Button>
              </Link>
              <Link to="/auth/login">
                <Button variant="outline" size="lg">Dang nhap</Button>
              </Link>
            </motion.div>
            <motion.div className="hero__metrics" variants={fadeUp}>
              <div className="hero__metric">
                <span className="hero__metric-value">10K+</span>
                <span className="hero__metric-label">Hoc vien</span>
              </div>
              <div className="hero__metric-divider" />
              <div className="hero__metric">
                <span className="hero__metric-value">500+</span>
                <span className="hero__metric-label">Khoa hoc</span>
              </div>
              <div className="hero__metric-divider" />
              <div className="hero__metric">
                <span className="hero__metric-value">95%</span>
                <span className="hero__metric-label">Hai long</span>
              </div>
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* ========== FEATURES ========== */}
      <section className="features" id="features">
        <div className="landing-container">
          <motion.div
            className="section-header"
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, margin: '-100px' }}
            variants={fadeUp}
          >
            <span className="section-label">Tinh nang</span>
            <h2 className="section-title">Moi thu ban can de hoc tap hieu qua</h2>
            <p className="section-desc">
              He thong tich hop AI tien tien, giup ban hoc dung cach va nhanh hon
            </p>
          </motion.div>

          <motion.div
            className="features__grid"
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, margin: '-50px' }}
            variants={stagger}
          >
            {features.map((f, i) => (
              <motion.div key={i} className="feature-card" variants={fadeUp}>
                <div className={`feature-card__icon feature-card__icon--${f.color}`}>
                  {f.emoji}
                </div>
                <h3 className="feature-card__title">{f.title}</h3>
                <p className="feature-card__desc">{f.desc}</p>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* ========== HOW IT WORKS ========== */}
      <section className="how-it-works" id="how-it-works">
        <div className="landing-container">
          <motion.div
            className="section-header"
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            variants={fadeUp}
          >
            <span className="section-label">Quy trinh</span>
            <h2 className="section-title">3 buoc bat dau hanh trinh</h2>
          </motion.div>

          <motion.div
            className="steps"
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            variants={stagger}
          >
            {steps.map((s, i) => (
              <motion.div key={i} className="step" variants={fadeUp}>
                <div className="step__number">{i + 1}</div>
                <div className="step__line" />
                <h3 className="step__title">{s.title}</h3>
                <p className="step__desc">{s.desc}</p>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* ========== STATS ========== */}
      <section className="stats" id="stats">
        <div className="landing-container">
          <motion.div
            className="stats__grid"
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            variants={stagger}
          >
            {stats.map((s, i) => (
              <motion.div key={i} className="stat-card" variants={fadeUp}>
                <span className="stat-card__value">{s.value}</span>
                <span className="stat-card__label">{s.label}</span>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* ========== CTA ========== */}
      <section className="cta">
        <div className="cta__bg">
          <div className="cta__orb cta__orb--1" />
          <div className="cta__orb cta__orb--2" />
        </div>
        <div className="landing-container">
          <motion.div
            className="cta__content"
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            variants={fadeUp}
          >
            <h2 className="cta__title">San sang thay doi cach hoc tap?</h2>
            <p className="cta__desc">
              Tham gia cung hang nghin hoc vien da tin tuong nen tang cua chung toi.
              Bat dau mien phi, khong can the tin dung.
            </p>
            <Link to="/auth/register">
              <Button variant="primary" size="lg">Dang ky mien phi →</Button>
            </Link>
          </motion.div>
        </div>
      </section>

      {/* ========== FOOTER ========== */}
      <footer className="landing-footer">
        <div className="landing-container">
          <div className="landing-footer__grid">
            <div className="landing-footer__brand">
              <div className="landing-logo">
                <div className="landing-logo__icon">AI</div>
                <span className="landing-logo__text">LearnAI</span>
              </div>
              <p className="landing-footer__tagline">
                Nen tang hoc tap thong minh cho tuong lai
              </p>
            </div>
            <div className="landing-footer__links">
              <div className="landing-footer__col">
                <h4>San pham</h4>
                <Link to="/dashboard/courses">Khoa hoc</Link>
                <Link to="/dashboard/assessment">Danh gia nang luc</Link>
                <Link to="/dashboard/chat">AI Chat</Link>
              </div>
              <div className="landing-footer__col">
                <h4>Ho tro</h4>
                <a href="#">Huong dan</a>
                <a href="#">Cau hoi thuong gap</a>
                <a href="#">Lien he</a>
              </div>
            </div>
          </div>
          <div className="landing-footer__bottom">
            <p>&copy; 2025 LearnAI. Bao luu moi quyen.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}

// Du lieu tinh
const features = [
  { emoji: '🧠', color: 'purple', title: 'Danh gia nang luc AI', desc: 'He thong AI tu dong danh gia trinh do va de xuat lo trinh hoc tap phu hop nhat voi ban.' },
  { emoji: '📚', color: 'blue', title: 'Khoa hoc ca nhan hoa', desc: 'Noi dung duoc AI tu dieu chinh theo toc do va phong cach hoc cua tung hoc vien.' },
  { emoji: '💬', color: 'green', title: 'Tro ly AI 24/7', desc: 'Tro ly ao thong minh giai dap thac mac bat cu luc nao, nhu co gia su rieng.' },
  { emoji: '📊', color: 'orange', title: 'Phan tich chi tiet', desc: 'Theo doi tien do, diem manh, diem yeu voi bieu do va bao cao truc quan.' },
  { emoji: '🎯', color: 'red', title: 'Quiz thong minh', desc: 'Bai tap va quiz tu dong sinh boi AI, phu hop voi trinh do hien tai cua ban.' },
  { emoji: '🏆', color: 'yellow', title: 'Chung chi hoan thanh', desc: 'Nhan chung chi sau khi hoan thanh khoa hoc, chia se tren ho so chuyen nghiep.' }
]

const steps = [
  { title: 'Dang ky tai khoan', desc: 'Tao tai khoan mien phi chi trong 30 giay voi email cua ban.' },
  { title: 'Lam bai danh gia', desc: 'AI se phan tich trinh do va tao lo trinh hoc tap rieng cho ban.' },
  { title: 'Bat dau hoc tap', desc: 'Truy cap khoa hoc, lam quiz, va chat voi AI de nang cao ky nang.' }
]

const stats = [
  { value: '10,000+', label: 'Hoc vien dang hoat dong' },
  { value: '500+', label: 'Khoa hoc chat luong' },
  { value: '95%', label: 'Ty le hai long' },
  { value: '3x', label: 'Hieu qua hoc tap' }
]

export default LandingPage
