import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import '../auth/AuthPages.css'
import './LegalPage.css'

const TERMS_SECTIONS = [
  {
    id: 'accept',
    title: '1. Chấp nhận điều khoản',
    body: 'Bằng việc đăng ký và sử dụng nền tảng, bạn đồng ý tuân thủ quy tắc học tập, không chia sẻ tài khoản, và sử dụng nội dung khóa học cho mục đích cá nhân hoặc học tập được phép.',
  },
  {
    id: 'content',
    title: '2. Nội dung và trách nhiệm',
    body: 'Giảng viên chịu trách nhiệm về nội dung quiz và khóa học do mình tạo. Học viên không được sao chép, phát tán hoặc bán lại tài liệu khóa học khi chưa có sự cho phép.',
  },
  {
    id: 'conduct',
    title: '3. Hành vi bị cấm',
    body: 'Gian lận trong quiz, spam, quấy rối người dùng khác, hoặc cố gắng truy cập trái phép hệ thống đều bị cấm và có thể dẫn đến khóa tài khoản.',
  },
  {
    id: 'admin',
    title: '4. Quyền quản trị',
    body: 'Quản trị viên có quyền khóa tài khoản vi phạm, gỡ nội dung không phù hợp, và tạm ngưng dịch vụ để bảo trì mà không cần báo trước trong trường hợp khẩn cấp.',
  },
]

const PRIVACY_SECTIONS = [
  {
    id: 'collect',
    title: '1. Dữ liệu thu thập',
    body: 'Chúng tôi thu thập email, họ tên, vai trò (học viên/giảng viên) và dữ liệu tiến độ học (bài học đã xem, điểm quiz) để vận hành dịch vụ.',
  },
  {
    id: 'security',
    title: '2. Bảo mật',
    body: 'Mật khẩu được băm; không lưu plain text. Phiên đăng nhập được bảo vệ bằng token; bạn nên đăng xuất trên thiết bị dùng chung.',
  },
  {
    id: 'sharing',
    title: '3. Chia sẻ với bên thứ ba',
    body: 'Dữ liệu không được bán cho bên thứ ba. Chúng tôi chỉ chia sẻ khi pháp luật yêu cầu hoặc để bảo vệ quyền lợi người dùng khác.',
  },
  {
    id: 'rights',
    title: '4. Quyền của bạn',
    body: 'Bạn có thể yêu cầu xem, chỉnh sửa hoặc xóa tài khoản qua quản trị viên. Dữ liệu tiến độ có thể được giữ tạm để tuân thủ báo cáo học tập theo yêu cầu tổ chức.',
  },
]

/**
 * Trang pháp lý tĩnh — /terms, /privacy
 */
const LegalPage = ({ type = 'terms' }) => {
  const isTerms = type === 'terms'
  const title = isTerms ? 'Điều khoản sử dụng' : 'Chính sách bảo mật'
  const sections = isTerms ? TERMS_SECTIONS : PRIVACY_SECTIONS

  return (
    <motion.div
      className="legal-page"
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
    >
      <article className="legal-card auth-stub-card">
        <p className="auth-stub-eyebrow">AI Learning Platform</p>
        <h1 className="auth-stub-title">{title}</h1>
        <p className="legal-intro">
          {isTerms
            ? 'Vui lòng đọc kỹ trước khi đăng ký. Điều khoản áp dụng cho mọi người dùng trên nền tảng.'
            : 'Chúng tôi tôn trọng quyền riêng tư của bạn. Tài liệu này mô tả cách xử lý dữ liệu cá nhân.'}
        </p>

        <nav className="legal-toc" aria-label="Mục lục">
          <span className="legal-toc__label">Mục lục</span>
          <ul>
            {sections.map((s) => (
              <li key={s.id}>
                <a href={`#${s.id}`}>{s.title}</a>
              </li>
            ))}
          </ul>
        </nav>

        <motion.div className="legal-body">
          {sections.map((s) => (
            <section key={s.id} id={s.id} className="legal-section">
              <h2 className="legal-section__title">{s.title}</h2>
              <p>{s.body}</p>
            </section>
          ))}
          <p className="legal-updated">Cập nhật: tháng 5/2026 · Phiên bản demo nội bộ.</p>
        </motion.div>

        <div className="legal-actions">
          <Link to="/auth/register" className="auth-stub-back">← Quay lại đăng ký</Link>
          <Link to="/" className="auth-stub-back legal-home">Trang chủ</Link>
        </div>
      </article>
    </motion.div>
  )
}

export default LegalPage
