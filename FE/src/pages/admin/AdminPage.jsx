import { useState, useEffect, useCallback } from 'react'
import { Routes, Route, Link, useNavigate, useLocation } from 'react-router-dom'
import { motion } from 'framer-motion'
import toast from 'react-hot-toast'
import adminService from '@services/adminService'
import analyticsService from '@services/analyticsService'
import Button from '@components/ui/Button'
import './AdminPage.css'

/**
 * AdminPage — Trang quản trị hệ thống (route: /dashboard/admin/*)
 * Docs: BE_TO_FE_MAPPING.md line 570-597
 * Sub-routes nội bộ:
 *   /dashboard/admin         → Overview (mặc định)
 *   /dashboard/admin/users   → Quản lý người dùng
 *   /dashboard/admin/courses → Quản lý khóa học
 *   /dashboard/admin/classes → Quản lý lớp học
 *   /dashboard/admin/analytics → Analytics dashboard
 */
const AdminPage = () => {
  const location = useLocation()

  // Xác định tab hiện tại từ URL
  const getActiveTab = () => {
    const path = location.pathname.replace('/dashboard/admin', '')
    if (path.startsWith('/users')) return 'users'
    if (path.startsWith('/courses')) return 'courses'
    if (path.startsWith('/classes')) return 'classes'
    if (path.startsWith('/analytics')) return 'analytics'
    return 'overview'
  }

  const tabs = [
    { key: 'overview', label: 'Tổng quan', path: '/dashboard/admin' },
    { key: 'users', label: 'Người dùng', path: '/dashboard/admin/users' },
    { key: 'courses', label: 'Khóa học', path: '/dashboard/admin/courses' },
    { key: 'classes', label: 'Lớp học', path: '/dashboard/admin/classes' },
    { key: 'analytics', label: 'Analytics', path: '/dashboard/admin/analytics' }
  ]

  return (
    <div className="admin-page">
      <div className="admin-header">
        <h1 className="admin-header__title">Quản trị hệ thống</h1>
        <p className="admin-header__sub">Quản lý toàn bộ người dùng, khóa học và hệ thống</p>
      </div>

      {/* Navigation tabs */}
      <nav className="admin-nav">
        {tabs.map(tab => (
          <Link
            key={tab.key}
            to={tab.path}
            className={`admin-nav__tab ${getActiveTab() === tab.key ? 'admin-nav__tab--active' : ''}`}
          >
            {tab.label}
          </Link>
        ))}
      </nav>

      {/* Sub-routes */}
      <Routes>
        <Route index element={<AdminOverview />} />
        <Route path="users" element={<AdminUsers />} />
        <Route path="courses" element={<AdminCourses />} />
        <Route path="classes" element={<AdminClasses />} />
        <Route path="analytics" element={<AdminAnalytics />} />
      </Routes>
    </div>
  )
}

/* ========== OVERVIEW ========== */
const AdminOverview = () => {
  const navigate = useNavigate()
  const cards = [
    { icon: '👥', title: 'Người dùng', desc: 'Quản lý tài khoản, vai trò, mật khẩu', path: '/dashboard/admin/users' },
    { icon: '📚', title: 'Khóa học', desc: 'Quản lý nội dung, tác giả, trạng thái', path: '/dashboard/admin/courses' },
    { icon: '🏫', title: 'Lớp học', desc: 'Giám sát lớp học, tiến độ', path: '/dashboard/admin/classes' },
    { icon: '📊', title: 'Analytics', desc: 'Thống kê, tăng trưởng, sức khỏe hệ thống', path: '/dashboard/admin/analytics' }
  ]

  return (
    <motion.div className="admin-overview" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
      <div className="admin-grid">
        {cards.map(card => (
          <div key={card.title} className="admin-card" onClick={() => navigate(card.path)}>
            <span className="admin-card__icon">{card.icon}</span>
            <h3 className="admin-card__title">{card.title}</h3>
            <p className="admin-card__desc">{card.desc}</p>
          </div>
        ))}
      </div>
    </motion.div>
  )
}

/* ========== USERS MANAGEMENT ========== */
/**
 * API: GET /admin/users (list), POST /admin/users (create),
 *      PUT /admin/users/{id} (update), DELETE /admin/users/{id},
 *      PUT /admin/users/{id}/role, POST /admin/users/{id}/reset-password
 * Docs: data[] + summary{total_users, active_users, new_users_this_month}
 */
const AdminUsers = () => {
  const [users, setUsers] = useState([])
  const [summary, setSummary] = useState(null)
  const [loading, setLoading] = useState(true)
  const [filters, setFilters] = useState({ role: '', status: '', search: '' })
  const [pagination, setPagination] = useState({ skip: 0, limit: 20, total: 0 })

  // Lấy danh sách users
  const fetchUsers = useCallback(async () => {
    try {
      setLoading(true)
      const params = { ...filters, skip: pagination.skip, limit: pagination.limit }
      // Xóa params rỗng
      Object.keys(params).forEach(k => { if (!params[k] && params[k] !== 0) delete params[k] })
      const data = await adminService.getUsers(params)
      setUsers(data?.data || [])
      if (data?.summary) setSummary(data.summary)
      setPagination(prev => ({ ...prev, total: data?.summary?.total_users || 0 }))
    } catch (error) {
      toast.error('Không thể tải danh sách người dùng')
    } finally {
      setLoading(false)
    }
  }, [filters, pagination.skip, pagination.limit])

  useEffect(() => { fetchUsers() }, [fetchUsers])

  // Xóa người dùng
  const handleDelete = async (userId, name) => {
    if (!window.confirm(`Xóa người dùng "${name}"?`)) return
    try {
      await adminService.deleteUser(userId)
      toast.success('Đã xóa người dùng')
      fetchUsers()
    } catch (error) {
      toast.error(error?.message || 'Không thể xóa')
    }
  }

  // Đổi vai trò
  const handleChangeRole = async (userId, currentRole) => {
    const newRole = prompt(`Nhập vai trò mới (student/instructor/admin).\nHiện tại: ${currentRole}`)
    if (!newRole || !['student', 'instructor', 'admin'].includes(newRole)) return
    try {
      const result = await adminService.changeUserRole(userId, newRole)
      toast.success(`Đã đổi vai trò thành ${newRole}`)
      if (result?.impact?.description) {
        toast(result.impact.description, { duration: 5000 })
      }
      fetchUsers()
    } catch (error) {
      toast.error(error?.message || 'Không thể đổi vai trò')
    }
  }

  // Reset mật khẩu
  const handleResetPassword = async (userId, name) => {
    const newPassword = prompt(`Nhập mật khẩu mới cho "${name}" (tối thiểu 8 ký tự):`)
    if (!newPassword || newPassword.length < 8) {
      if (newPassword) toast.error('Mật khẩu phải có ít nhất 8 ký tự')
      return
    }
    try {
      const result = await adminService.resetUserPassword(userId, newPassword)
      toast.success('Đã reset mật khẩu')
      if (result?.note) toast(result.note, { duration: 4000 })
    } catch (error) {
      toast.error(error?.message || 'Không thể reset mật khẩu')
    }
  }

  const fadeUp = { hidden: { opacity: 0, y: 20 }, visible: { opacity: 1, y: 0 } }

  return (
    <motion.div initial="hidden" animate="visible" variants={fadeUp}>
      {/* Summary stats */}
      {summary && (
        <div className="admin-summary">
          <div className="admin-summary__item">
            <span className="admin-summary__value">{summary.total_users || 0}</span>
            <span className="admin-summary__label">Tổng người dùng</span>
          </div>
          <div className="admin-summary__item">
            <span className="admin-summary__value">{summary.active_users || 0}</span>
            <span className="admin-summary__label">Đang hoạt động</span>
          </div>
          <div className="admin-summary__item">
            <span className="admin-summary__value">{summary.new_users_this_month || 0}</span>
            <span className="admin-summary__label">Mới tháng này</span>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="admin-filters">
        <input
          type="text"
          className="admin-filters__search"
          placeholder="Tìm kiếm theo tên, email..."
          value={filters.search}
          onChange={(e) => setFilters(prev => ({ ...prev, search: e.target.value }))}
        />
        <select
          className="admin-filters__select"
          value={filters.role}
          onChange={(e) => setFilters(prev => ({ ...prev, role: e.target.value }))}
        >
          <option value="">Tất cả vai trò</option>
          <option value="student">Học viên</option>
          <option value="instructor">Giảng viên</option>
          <option value="admin">Quản trị</option>
        </select>
        <select
          className="admin-filters__select"
          value={filters.status}
          onChange={(e) => setFilters(prev => ({ ...prev, status: e.target.value }))}
        >
          <option value="">Tất cả trạng thái</option>
          <option value="active">Hoạt động</option>
          <option value="inactive">Bị khóa</option>
        </select>
      </div>

      {/* Bảng users */}
      {loading ? (
        <div className="admin-table-skeleton">{[1,2,3,4,5].map(i => <div key={i} className="admin-skeleton-row" />)}</div>
      ) : (
        <div className="admin-table-wrap">
          <table className="admin-table">
            <thead>
              <tr>
                <th>Họ tên</th>
                <th>Email</th>
                <th>Vai trò</th>
                <th>Trạng thái</th>
                <th>Hành động</th>
              </tr>
            </thead>
            <tbody>
              {users.length > 0 ? users.map(user => (
                <tr key={user.id || user.user_id}>
                  <td className="admin-table__name">
                    {(user.avatar || user.avatar_url) && <img src={user.avatar || user.avatar_url} alt="" className="admin-table__avatar" />}
                    {user.full_name}
                  </td>
                  <td>{user.email}</td>
                  <td>
                    <span className={`admin-badge admin-badge--${user.role}`}>
                      {user.role === 'admin' ? 'Quản trị' : user.role === 'instructor' ? 'Giảng viên' : 'Học viên'}
                    </span>
                  </td>
                  <td>
                    <span className={`admin-badge admin-badge--${user.status || 'active'}`}>
                      {user.status === 'inactive' ? 'Bị khóa' : 'Hoạt động'}
                    </span>
                  </td>
                  <td className="admin-table__actions">
                    <button className="admin-action-btn" onClick={() => handleChangeRole(user.id || user.user_id, user.role)} title="Đổi vai trò">
                      Vai trò
                    </button>
                    <button className="admin-action-btn" onClick={() => handleResetPassword(user.id || user.user_id, user.full_name)} title="Reset mật khẩu">
                      Reset MK
                    </button>
                    <button className="admin-action-btn admin-action-btn--danger" onClick={() => handleDelete(user.id || user.user_id, user.full_name)} title="Xóa">
                      Xóa
                    </button>
                  </td>
                </tr>
              )) : (
                <tr><td colSpan="5" className="admin-table__empty">Không tìm thấy người dùng</td></tr>
              )}
            </tbody>
          </table>
        </div>
      )}
    </motion.div>
  )
}

/* ========== COURSES MANAGEMENT ========== */
/**
 * API: GET /admin/courses (list), DELETE /admin/courses/{id}
 * Docs: data[]{course_id, title, author{}, course_type, enrollment_count, status, category, level}
 */
const AdminCourses = () => {
  const [courses, setCourses] = useState([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')

  const fetchCourses = useCallback(async () => {
    try {
      setLoading(true)
      const params = {}
      if (search) params.search = search
      const data = await adminService.getCourses(params)
      setCourses(data?.data || [])
    } catch (error) {
      toast.error('Không thể tải danh sách khóa học')
    } finally {
      setLoading(false)
    }
  }, [search])

  useEffect(() => { fetchCourses() }, [fetchCourses])

  const handleDelete = async (courseId, title) => {
    if (!window.confirm(`Xóa khóa học "${title}"? Hành động này không thể hoàn tác.`)) return
    try {
      const result = await adminService.deleteCourse(courseId)
      toast.success('Đã xóa khóa học')
      if (result?.impact?.warning) toast(result.impact.warning, { duration: 5000 })
      fetchCourses()
    } catch (error) {
      toast.error(error?.message || 'Không thể xóa')
    }
  }

  const fadeUp = { hidden: { opacity: 0, y: 20 }, visible: { opacity: 1, y: 0 } }

  return (
    <motion.div initial="hidden" animate="visible" variants={fadeUp}>
      <div className="admin-filters">
        <input
          type="text"
          className="admin-filters__search"
          placeholder="Tìm kiếm khóa học..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      {loading ? (
        <div className="admin-table-skeleton">{[1,2,3,4].map(i => <div key={i} className="admin-skeleton-row" />)}</div>
      ) : (
        <div className="admin-table-wrap">
          <table className="admin-table">
            <thead>
              <tr>
                <th>Tên khóa học</th>
                <th>Tác giả</th>
                <th>Loại</th>
                <th>Học viên</th>
                <th>Trạng thái</th>
                <th>Hành động</th>
              </tr>
            </thead>
            <tbody>
              {courses.length > 0 ? courses.map(course => (
                <tr key={course.course_id}>
                  <td>
                    <div>
                      <span className="admin-table__name">{course.title}</span>
                      {course.category && <span className="admin-table__sub">{course.category} · {course.level}</span>}
                    </div>
                  </td>
                  <td>{course.author?.full_name || '—'}</td>
                  <td>
                    <span className={`admin-badge admin-badge--${course.course_type}`}>
                      {course.course_type === 'personal' ? 'Cá nhân' : 'Công khai'}
                    </span>
                  </td>
                  <td>{course.enrollment_count || 0}</td>
                  <td>
                    <span className={`admin-badge admin-badge--${course.status}`}>
                      {course.status === 'published' ? 'Xuất bản' : course.status === 'draft' ? 'Nháp' : course.status}
                    </span>
                  </td>
                  <td>
                    <button className="admin-action-btn admin-action-btn--danger" onClick={() => handleDelete(course.course_id, course.title)}>
                      Xóa
                    </button>
                  </td>
                </tr>
              )) : (
                <tr><td colSpan="6" className="admin-table__empty">Không tìm thấy khóa học</td></tr>
              )}
            </tbody>
          </table>
        </div>
      )}
    </motion.div>
  )
}

/* ========== CLASSES MANAGEMENT ========== */
/**
 * API: GET /admin/classes
 * Docs: data[]{class_id, class_name, course_title, instructor_name, student_count, status, created_at}
 */
const AdminClasses = () => {
  const [classes, setClasses] = useState([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')

  const fetchClasses = useCallback(async () => {
    try {
      setLoading(true)
      const params = {}
      if (search) params.search = search
      const data = await adminService.getClasses(params)
      setClasses(data?.data || [])
    } catch (error) {
      toast.error('Không thể tải danh sách lớp học')
    } finally {
      setLoading(false)
    }
  }, [search])

  useEffect(() => { fetchClasses() }, [fetchClasses])

  const fadeUp = { hidden: { opacity: 0, y: 20 }, visible: { opacity: 1, y: 0 } }

  return (
    <motion.div initial="hidden" animate="visible" variants={fadeUp}>
      <div className="admin-filters">
        <input
          type="text"
          className="admin-filters__search"
          placeholder="Tìm kiếm lớp học..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      {loading ? (
        <div className="admin-table-skeleton">{[1,2,3].map(i => <div key={i} className="admin-skeleton-row" />)}</div>
      ) : (
        <div className="admin-table-wrap">
          <table className="admin-table">
            <thead>
              <tr>
                <th>Tên lớp</th>
                <th>Khóa học</th>
                <th>Giảng viên</th>
                <th>Học viên</th>
                <th>Trạng thái</th>
                <th>Ngày tạo</th>
              </tr>
            </thead>
            <tbody>
              {classes.length > 0 ? classes.map(cls => (
                <tr key={cls.class_id}>
                  <td className="admin-table__name">{cls.class_name}</td>
                  <td>{cls.course_title || '—'}</td>
                  <td>{cls.instructor_name || '—'}</td>
                  <td>{cls.student_count || 0}</td>
                  <td>
                    <span className={`admin-badge admin-badge--${cls.status}`}>
                      {cls.status === 'active' ? 'Hoạt động' : cls.status === 'completed' ? 'Kết thúc' : cls.status}
                    </span>
                  </td>
                  <td>{cls.created_at ? new Date(cls.created_at).toLocaleDateString('vi-VN') : '—'}</td>
                </tr>
              )) : (
                <tr><td colSpan="6" className="admin-table__empty">Không tìm thấy lớp học</td></tr>
              )}
            </tbody>
          </table>
        </div>
      )}
    </motion.div>
  )
}

/* ========== ANALYTICS ========== */
/**
 * API (analyticsService):
 *   GET /admin/analytics/users-growth -> chart_data[], statistics{}
 *   GET /admin/analytics/courses -> top_courses[], overall_completion_rate
 *   GET /admin/analytics/system-health -> status, metrics{}, alerts[]
 */
const AdminAnalytics = () => {
  const [usersGrowth, setUsersGrowth] = useState(null)
  const [courseAnalytics, setCourseAnalytics] = useState(null)
  const [systemHealth, setSystemHealth] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchAll = async () => {
      try {
        setLoading(true)
        const [growth, courses, health] = await Promise.allSettled([
          analyticsService.getUsersGrowth({ time_range: '30d' }),
          analyticsService.getCourseAnalytics(),
          analyticsService.getSystemHealth()
        ])
        if (growth.status === 'fulfilled') setUsersGrowth(growth.value)
        if (courses.status === 'fulfilled') setCourseAnalytics(courses.value)
        if (health.status === 'fulfilled') setSystemHealth(health.value)
      } catch (error) {
        toast.error('Không thể tải analytics')
      } finally {
        setLoading(false)
      }
    }
    fetchAll()
  }, [])

  const fadeUp = { hidden: { opacity: 0, y: 20 }, visible: { opacity: 1, y: 0 } }

  if (loading) {
    return (
      <div className="admin-table-skeleton">
        {[1,2,3].map(i => <div key={i} className="admin-skeleton-row admin-skeleton-row--tall" />)}
      </div>
    )
  }

  return (
    <motion.div initial="hidden" animate="visible" variants={fadeUp}>
      {/* System Health */}
      {systemHealth && (
        <div className="admin-analytics-section">
          <h3 className="admin-analytics__title">Sức khỏe hệ thống</h3>
          <div className="admin-health">
            <span className={`admin-health__status admin-health__status--${systemHealth.status}`}>
              {systemHealth.status === 'healthy' ? '✅ Bình thường'
                : systemHealth.status === 'warning' ? '⚠️ Cảnh báo'
                : '🔴 Nghiêm trọng'}
            </span>
            {systemHealth.uptime_hours != null && (
              <span className="admin-health__uptime">Uptime: {Math.round(systemHealth.uptime_hours)}h</span>
            )}
          </div>
          {systemHealth.metrics && (
            <div className="admin-metrics">
              <MetricCard label="API Response" value={`${systemHealth.metrics.api_response_time_ms || 0}ms`} />
              <MetricCard label="Error Rate" value={`${systemHealth.metrics.error_rate_percentage || 0}%`} />
              <MetricCard label="DB Query" value={`${systemHealth.metrics.database_query_time_ms || 0}ms`} />
              <MetricCard label="Storage" value={`${systemHealth.metrics.storage_usage_percentage || 0}%`} />
              <MetricCard label="Memory" value={`${systemHealth.metrics.memory_usage_percentage || 0}%`} />
              <MetricCard label="Sessions" value={systemHealth.metrics.active_sessions || 0} />
            </div>
          )}
          {/* Alerts */}
          {systemHealth.alerts?.length > 0 && (
            <div className="admin-alerts">
              {systemHealth.alerts.map((alert, i) => (
                <div key={i} className={`admin-alert admin-alert--${alert.alert_type}`}>
                  <span>{alert.message}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Users Growth */}
      {usersGrowth?.statistics && (
        <div className="admin-analytics-section">
          <h3 className="admin-analytics__title">Tăng trưởng người dùng (30 ngày)</h3>
          <div className="admin-metrics">
            <MetricCard label="Tỉ lệ tăng trưởng" value={`${usersGrowth.statistics.total_growth_rate || 0}%`} />
            <MetricCard label="Tăng trưởng học viên" value={`${usersGrowth.statistics.student_growth_rate || 0}%`} />
            <MetricCard label="Tỉ lệ giữ chân" value={`${usersGrowth.statistics.user_retention_rate || 0}%`} />
            <MetricCard label="TB mới/ngày" value={usersGrowth.statistics.avg_daily_new_users || 0} />
          </div>
        </div>
      )}

      {/* Course Analytics */}
      {courseAnalytics && (
        <div className="admin-analytics-section">
          <h3 className="admin-analytics__title">Phân tích khóa học</h3>
          <div className="admin-summary" style={{ marginBottom: 16 }}>
            <div className="admin-summary__item">
              <span className="admin-summary__value">{courseAnalytics.total_enrollments || 0}</span>
              <span className="admin-summary__label">Tổng đăng ký</span>
            </div>
            <div className="admin-summary__item">
              <span className="admin-summary__value">{courseAnalytics.overall_completion_rate || 0}%</span>
              <span className="admin-summary__label">Tỉ lệ hoàn thành</span>
            </div>
          </div>

          {/* Top courses */}
          {courseAnalytics.top_courses?.length > 0 && (
            <div className="admin-table-wrap">
              <table className="admin-table">
                <thead>
                  <tr>
                    <th>Khóa học</th>
                    <th>Đăng ký</th>
                    <th>Hoàn thành</th>
                    <th>Quiz TB</th>
                    <th>Giảng viên</th>
                  </tr>
                </thead>
                <tbody>
                  {courseAnalytics.top_courses.map((c, i) => (
                    <tr key={i}>
                      <td className="admin-table__name">{c.title}</td>
                      <td>{c.enrollments || 0}</td>
                      <td>{c.completion_rate || 0}%</td>
                      <td>{c.avg_quiz_score || 0}</td>
                      <td>{c.instructor_name || '—'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
    </motion.div>
  )
}

// Metric card nhỏ dùng trong analytics
const MetricCard = ({ label, value }) => (
  <div className="admin-metric-card">
    <span className="admin-metric-card__value">{value}</span>
    <span className="admin-metric-card__label">{label}</span>
  </div>
)

export default AdminPage