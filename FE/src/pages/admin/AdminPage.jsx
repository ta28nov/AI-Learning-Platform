import { useState, useEffect, useCallback } from 'react'
import { Routes, Route, Link, useNavigate, useLocation } from 'react-router-dom'
import { motion, useReducedMotion } from 'framer-motion'
import toast from 'react-hot-toast'
import adminService from '@services/adminService'
import analyticsService from '@services/analyticsService'
import dashboardService from '@services/dashboardService'
import Button from '@components/ui/Button'
import StateView from '@components/ui/StateView'
import appLogger from '@utils/logger'
import './AdminPage.css'

/* ─── SVG Icon Library ─────────────────────────── */
const UsersIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
    <circle cx="9" cy="7" r="4"/>
    <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
    <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
  </svg>
)

const CoursesIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/>
    <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/>
  </svg>
)

const ClassesIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
    <polyline points="9 22 9 12 15 12 15 22"/>
  </svg>
)

const AnalyticsIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <line x1="18" y1="20" x2="18" y2="10"/>
    <line x1="12" y1="20" x2="12" y2="4"/>
    <line x1="6"  y1="20" x2="6"  y2="14"/>
  </svg>
)

const CheckIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="20 6 9 17 4 12"/>
  </svg>
)

const WarnIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
    <line x1="12" y1="9" x2="12" y2="13"/>
    <line x1="12" y1="17" x2="12.01" y2="17"/>
  </svg>
)

const ErrorIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="10"/>
    <line x1="15" y1="9" x2="9" y2="15"/>
    <line x1="9" y1="9" x2="15" y2="15"/>
  </svg>
)

const SearchIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="11" cy="11" r="8"/>
    <line x1="21" y1="21" x2="16.65" y2="16.65"/>
  </svg>
)

const RoleIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
  </svg>
)

const KeyIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <path d="M21 2l-2 2m-7.61 7.61a5.5 5.5 0 1 1-7.778 7.778 5.5 5.5 0 0 1 7.777-7.777zm0 0L15.5 7.5m0 0 3 3L22 7l-3-3m-3.5 3.5L19 4"/>
  </svg>
)

const DeleteIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="3 6 5 6 21 6"/>
    <path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/>
    <path d="M10 11v6"/>
    <path d="M14 11v6"/>
  </svg>
)

/**
 * AdminPage — Trang quản trị hệ thống
 * Route: /dashboard/admin/*
 * Sub-routes: /dashboard/admin → /users → /courses → /classes → /analytics
 */
const AdminPage = () => {
  const location = useLocation()

  const getActiveTab = () => {
    const path = location.pathname.replace('/dashboard/admin', '')
    if (path.startsWith('/users'))     return 'users'
    if (path.startsWith('/courses'))   return 'courses'
    if (path.startsWith('/classes'))   return 'classes'
    if (path.startsWith('/analytics')) return 'analytics'
    return 'overview'
  }

  const tabs = [
    { key: 'overview',   label: 'Tổng quan',     path: '/dashboard/admin',           Icon: AnalyticsIcon },
    { key: 'users',      label: 'Người dùng',    path: '/dashboard/admin/users',     Icon: UsersIcon },
    { key: 'courses',    label: 'Khóa học',      path: '/dashboard/admin/courses',   Icon: CoursesIcon },
    { key: 'classes',    label: 'Lớp học',       path: '/dashboard/admin/classes',   Icon: ClassesIcon },
    { key: 'analytics',  label: 'Analytics',     path: '/dashboard/admin/analytics', Icon: AnalyticsIcon },
  ]

  const active = getActiveTab()

  return (
    <div className="adm-page">
      <div className="adm-header">
        <div className="adm-header__eyebrow">Hệ thống quản trị</div>
        <h1 className="adm-header__title">Admin Console</h1>
        <p className="adm-header__sub">Quản lý toàn bộ người dùng, khóa học và hệ thống</p>
      </div>

      <nav className="adm-nav" aria-label="Admin navigation">
        {tabs.map(({ key, label, path, Icon }) => (
          <Link
            key={key}
            to={path}
            className={`adm-nav__tab ${active === key ? 'adm-nav__tab--active' : ''}`}
            aria-current={active === key ? 'page' : undefined}
          >
            <span className="adm-nav__icon"><Icon /></span>
            {label}
          </Link>
        ))}
      </nav>

      <div className="adm-content">
        <Routes>
          <Route index element={<AdminOverview />} />
          <Route path="users"     element={<AdminUsers />} />
          <Route path="courses"   element={<AdminCourses />} />
          <Route path="classes"   element={<AdminClasses />} />
          <Route path="analytics" element={<AdminAnalytics />} />
        </Routes>
      </div>
    </div>
  )
}

/* ═══════════════════════════════════════════════
   OVERVIEW
═══════════════════════════════════════════════ */
const AdminOverview = () => {
  const navigate = useNavigate()
  const shouldReduce = useReducedMotion()
  const [dashboard, setDashboard] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        setLoading(true)
        setError('')
        const data = await dashboardService.getAdminDashboard()
        setDashboard(data)
      } catch (err) {
        setError('Không thể tải dữ liệu tổng quan quản trị.')
        appLogger.error(err, { feature: 'AdminOverview' })
      } finally {
        setLoading(false)
      }
    }
    fetchDashboard()
  }, [])

  const cards = [
    { Icon: UsersIcon,   title: 'Người dùng',  desc: 'Quản lý tài khoản, vai trò, mật khẩu', path: '/dashboard/admin/users',     stat: dashboard?.total_users },
    { Icon: CoursesIcon, title: 'Khóa học',    desc: 'Quản lý nội dung, tác giả, trạng thái', path: '/dashboard/admin/courses',   stat: dashboard?.total_courses },
    { Icon: ClassesIcon, title: 'Lớp học',     desc: 'Giám sát lớp học, tiến độ học viên',    path: '/dashboard/admin/classes',   stat: dashboard?.total_classes },
    { Icon: AnalyticsIcon, title: 'Analytics', desc: 'Thống kê, tăng trưởng, sức khỏe hệ thống', path: '/dashboard/admin/analytics' },
  ]

  const stagger = { visible: { transition: { staggerChildren: shouldReduce ? 0 : 0.07 } } }
  const fadeUp  = { hidden: { opacity: 0, y: 16 }, visible: { opacity: 1, y: 0 } }

  return (
    <motion.div initial="hidden" animate="visible" variants={stagger}>
      {error && <StateView type="error" title="Lỗi tải tổng quan" message={error} />}

      {/* Summary strip */}
      {dashboard && !loading && (
        <motion.div className="adm-summary" variants={fadeUp}>
          <div className="adm-summary__item">
            <span className="adm-summary__value">{dashboard.total_users || 0}</span>
            <span className="adm-summary__label">Người dùng</span>
          </div>
          <div className="adm-summary__item">
            <span className="adm-summary__value">{dashboard.total_courses || 0}</span>
            <span className="adm-summary__label">Khóa học</span>
          </div>
          <div className="adm-summary__item">
            <span className="adm-summary__value">{dashboard.total_classes || 0}</span>
            <span className="adm-summary__label">Lớp học</span>
          </div>
          {dashboard.activity_stats && (
            <div className="adm-summary__item">
              <span className="adm-summary__value">{dashboard.activity_stats.active_users_today || 0}</span>
              <span className="adm-summary__label">Hoạt động hôm nay</span>
            </div>
          )}
        </motion.div>
      )}

      <div className="adm-grid">
        {cards.map(({ Icon, title, desc, path, stat }) => (
          <motion.div
            key={title}
            className="adm-card"
            variants={fadeUp}
            transition={{ duration: 0.4 }}
            onClick={() => navigate(path)}
            role="button"
            tabIndex={0}
            onKeyDown={(e) => e.key === 'Enter' && navigate(path)}
          >
            <div className="adm-card__icon-wrap">
              <Icon />
            </div>
            <h3 className="adm-card__title">{title}</h3>
            <p className="adm-card__desc">{desc}</p>
            {stat != null && <span className="adm-card__stat">{stat.toLocaleString()}</span>}
          </motion.div>
        ))}
      </div>
    </motion.div>
  )
}

/* ═══════════════════════════════════════════════
   USERS MANAGEMENT
   API: GET /admin/users (list) + PUT role + POST reset-password + DELETE
═══════════════════════════════════════════════ */
const AdminUsers = () => {
  const [users, setUsers]             = useState([])
  const [loading, setLoading]         = useState(true)
  const [filters, setFilters]         = useState({ role: '', status: '', search: '' })
  const [pagination, setPagination]   = useState({ skip: 0, limit: 20, total: 0 })
  const [error, setError]             = useState('')

  const fetchUsers = useCallback(async () => {
    try {
      setLoading(true)
      setError('')
      const params = { ...filters, skip: pagination.skip, limit: pagination.limit }
      Object.keys(params).forEach(k => { if (!params[k] && params[k] !== 0) delete params[k] })
      const data = await adminService.getUsers(params)
      setUsers(data?.data || [])
      setPagination(prev => ({ ...prev, total: data?.total || 0 }))
    } catch (err) {
      setError('Không thể tải danh sách người dùng.')
      appLogger.error(err, { feature: 'AdminUsers' })
      toast.error('Không thể tải danh sách người dùng')
    } finally {
      setLoading(false)
    }
  }, [filters, pagination.skip, pagination.limit])

  useEffect(() => { fetchUsers() }, [fetchUsers])

  const handleDelete = async (userId, name) => {
    if (!window.confirm(`Xóa người dùng "${name}"?`)) return
    try {
      await adminService.deleteUser(userId)
      toast.success('Đã xóa người dùng')
      fetchUsers()
    } catch (err) {
      toast.error(err?.message || 'Không thể xóa')
    }
  }

  const handleChangeRole = async (userId, currentRole) => {
    const newRole = window.prompt(`Nhập vai trò mới (student/instructor/admin).\nHiện tại: ${currentRole}`)
    if (!newRole || !['student', 'instructor', 'admin'].includes(newRole)) return
    try {
      const result = await adminService.changeUserRole(userId, newRole)
      toast.success(`Đã đổi vai trò thành ${newRole}`)
      if (result?.impact?.description) toast(result.impact.description, { duration: 5000 })
      fetchUsers()
    } catch (err) {
      toast.error(err?.message || 'Không thể đổi vai trò')
    }
  }

  const handleResetPassword = async (userId, name) => {
    const newPassword = window.prompt(`Nhập mật khẩu mới cho "${name}" (tối thiểu 8 ký tự):`)
    if (!newPassword || newPassword.length < 8) {
      if (newPassword) toast.error('Mật khẩu phải có ít nhất 8 ký tự')
      return
    }
    try {
      const result = await adminService.resetUserPassword(userId, newPassword)
      toast.success('Đã reset mật khẩu')
      if (result?.note) toast(result.note, { duration: 4000 })
    } catch (err) {
      toast.error(err?.message || 'Không thể reset mật khẩu')
    }
  }

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
      <div className="adm-stat-strip">
        <div className="adm-stat-item">
          <span className="adm-stat-item__val">{pagination.total}</span>
          <span className="adm-stat-item__lbl">Tổng người dùng</span>
        </div>
        <div className="adm-stat-item">
          <span className="adm-stat-item__val">{users.length}</span>
          <span className="adm-stat-item__lbl">Đang hiển thị</span>
        </div>
      </div>

      <div className="adm-filters">
        <div className="adm-filters__search-wrap">
          <span className="adm-filters__search-icon"><SearchIcon /></span>
          <input
            type="text"
            className="adm-input adm-input--search"
            placeholder="Tìm theo tên, email…"
            value={filters.search}
            onChange={(e) => setFilters(prev => ({ ...prev, search: e.target.value }))}
          />
        </div>
        <select className="adm-select" value={filters.role} onChange={(e) => setFilters(prev => ({ ...prev, role: e.target.value }))}>
          <option value="">Tất cả vai trò</option>
          <option value="student">Học viên</option>
          <option value="instructor">Giảng viên</option>
          <option value="admin">Quản trị</option>
        </select>
        <select className="adm-select" value={filters.status} onChange={(e) => setFilters(prev => ({ ...prev, status: e.target.value }))}>
          <option value="">Tất cả trạng thái</option>
          <option value="active">Hoạt động</option>
          <option value="inactive">Bị khóa</option>
        </select>
      </div>

      {loading ? (
        <Skeleton rows={5} />
      ) : error ? (
        <StateView type="error" title="Lỗi tải người dùng" message={error} actionLabel="Tải lại" onAction={fetchUsers} />
      ) : (
        <div className="adm-table-wrap">
          <table className="adm-table">
            <thead>
              <tr>
                <th>Họ tên</th><th>Email</th><th>Vai trò</th><th>Trạng thái</th><th>Hành động</th>
              </tr>
            </thead>
            <tbody>
              {users.length > 0 ? users.map(user => (
                <tr key={user.id || user.user_id}>
                  <td>
                    <div className="adm-cell-name">
                      {(user.avatar || user.avatar_url) && <img src={user.avatar || user.avatar_url} alt="" className="adm-avatar" />}
                      <span className="adm-cell-name__text">{user.full_name}</span>
                    </div>
                  </td>
                  <td className="adm-cell-muted">{user.email}</td>
                  <td><span className={`adm-badge adm-badge--${user.role}`}>{user.role === 'admin' ? 'Quản trị' : user.role === 'instructor' ? 'Giảng viên' : 'Học viên'}</span></td>
                  <td><span className={`adm-badge adm-badge--${user.status || 'active'}`}>{user.status === 'inactive' ? 'Bị khóa' : 'Hoạt động'}</span></td>
                  <td>
                    <div className="adm-actions">
                      <button className="adm-btn" title="Đổi vai trò" onClick={() => handleChangeRole(user.id || user.user_id, user.role)}>
                        <RoleIcon /> Vai trò
                      </button>
                      <button className="adm-btn" title="Reset mật khẩu" onClick={() => handleResetPassword(user.id || user.user_id, user.full_name)}>
                        <KeyIcon /> Reset
                      </button>
                      <button className="adm-btn adm-btn--danger" title="Xóa" onClick={() => handleDelete(user.id || user.user_id, user.full_name)}>
                        <DeleteIcon /> Xóa
                      </button>
                    </div>
                  </td>
                </tr>
              )) : (
                <tr><td colSpan="5" className="adm-table__empty">Không tìm thấy người dùng</td></tr>
              )}
            </tbody>
          </table>
        </div>
      )}
    </motion.div>
  )
}

/* ═══════════════════════════════════════════════
   COURSES MANAGEMENT
   API: GET /admin/courses, DELETE /admin/courses/{id}
═══════════════════════════════════════════════ */
const AdminCourses = () => {
  const [courses, setCourses] = useState([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch]   = useState('')
  const [error, setError]     = useState('')

  const fetchCourses = useCallback(async () => {
    try {
      setLoading(true)
      setError('')
      const params = {}
      if (search) params.keyword = search
      const data = await adminService.getCourses(params)
      setCourses(data?.data || [])
    } catch (err) {
      setError('Không thể tải danh sách khóa học.')
      appLogger.error(err, { feature: 'AdminCourses' })
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
    } catch (err) {
      toast.error(err?.message || 'Không thể xóa')
    }
  }

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
      <div className="adm-filters">
        <div className="adm-filters__search-wrap">
          <span className="adm-filters__search-icon"><SearchIcon /></span>
          <input
            type="text"
            className="adm-input adm-input--search"
            placeholder="Tìm kiếm khóa học…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
      </div>

      {loading ? <Skeleton rows={4} /> : error ? (
        <StateView type="error" title="Lỗi tải khóa học" message={error} actionLabel="Tải lại" onAction={fetchCourses} />
      ) : (
        <div className="adm-table-wrap">
          <table className="adm-table">
            <thead><tr><th>Tên khóa học</th><th>Tác giả</th><th>Loại</th><th>Học viên</th><th>Trạng thái</th><th>Hành động</th></tr></thead>
            <tbody>
              {courses.length > 0 ? courses.map(course => (
                <tr key={course.course_id}>
                  <td>
                    <div className="adm-cell-stack">
                      <span className="adm-cell-primary">{course.title}</span>
                      {course.category && <span className="adm-cell-secondary">{course.category} · {course.level}</span>}
                    </div>
                  </td>
                  <td className="adm-cell-muted">{course.author?.full_name || '—'}</td>
                  <td><span className={`adm-badge adm-badge--${course.course_type}`}>{course.course_type === 'personal' ? 'Cá nhân' : 'Công khai'}</span></td>
                  <td className="adm-cell-muted">{course.enrollment_count || 0}</td>
                  <td><span className={`adm-badge adm-badge--${course.status}`}>{course.status === 'published' ? 'Xuất bản' : course.status === 'draft' ? 'Nháp' : course.status}</span></td>
                  <td>
                    <div className="adm-actions">
                      <button className="adm-btn adm-btn--danger" onClick={() => handleDelete(course.course_id, course.title)}>
                        <DeleteIcon /> Xóa
                      </button>
                    </div>
                  </td>
                </tr>
              )) : (
                <tr><td colSpan="6" className="adm-table__empty">Không tìm thấy khóa học</td></tr>
              )}
            </tbody>
          </table>
        </div>
      )}
    </motion.div>
  )
}

/* ═══════════════════════════════════════════════
   CLASSES MONITORING
   API: GET /admin/classes
═══════════════════════════════════════════════ */
const AdminClasses = () => {
  const [classes, setClasses] = useState([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch]   = useState('')
  const [error, setError]     = useState('')

  const fetchClasses = useCallback(async () => {
    try {
      setLoading(true)
      setError('')
      const params = {}
      if (search) params.search = search
      const data = await adminService.getClasses(params)
      setClasses(data?.data || [])
    } catch (err) {
      setError('Không thể tải danh sách lớp học.')
      appLogger.error(err, { feature: 'AdminClasses' })
      toast.error('Không thể tải danh sách lớp học')
    } finally {
      setLoading(false)
    }
  }, [search])

  useEffect(() => { fetchClasses() }, [fetchClasses])

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
      <div className="adm-filters">
        <div className="adm-filters__search-wrap">
          <span className="adm-filters__search-icon"><SearchIcon /></span>
          <input
            type="text"
            className="adm-input adm-input--search"
            placeholder="Tìm kiếm lớp học…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
      </div>

      {loading ? <Skeleton rows={3} /> : error ? (
        <StateView type="error" title="Lỗi tải lớp học" message={error} actionLabel="Tải lại" onAction={fetchClasses} />
      ) : (
        <div className="adm-table-wrap">
          <table className="adm-table">
            <thead><tr><th>Tên lớp</th><th>Khóa học</th><th>Giảng viên</th><th>Học viên</th><th>Trạng thái</th><th>Ngày tạo</th></tr></thead>
            <tbody>
              {classes.length > 0 ? classes.map(cls => (
                <tr key={cls.class_id}>
                  <td className="adm-cell-primary">{cls.class_name || cls.name || '—'}</td>
                  <td className="adm-cell-muted">{cls.course_title || '—'}</td>
                  <td className="adm-cell-muted">{cls.instructor_name || '—'}</td>
                  <td className="adm-cell-muted">{cls.student_count || 0}</td>
                  <td><span className={`adm-badge adm-badge--${cls.status}`}>{cls.status === 'active' ? 'Hoạt động' : cls.status === 'completed' ? 'Kết thúc' : cls.status}</span></td>
                  <td className="adm-cell-muted">{cls.created_at ? new Date(cls.created_at).toLocaleDateString('vi-VN') : '—'}</td>
                </tr>
              )) : (
                <tr><td colSpan="6" className="adm-table__empty">Không tìm thấy lớp học</td></tr>
              )}
            </tbody>
          </table>
        </div>
      )}
    </motion.div>
  )
}

/* ═══════════════════════════════════════════════
   ANALYTICS
   API (analyticsService):
     GET /admin/analytics/users-growth → chart_data[], statistics{}
     GET /admin/analytics/courses → top_courses[], overall_completion_rate
     GET /admin/analytics/system-health → status, metrics{}, alerts[]
═══════════════════════════════════════════════ */
const AdminAnalytics = () => {
  const [usersGrowth, setUsersGrowth]       = useState(null)
  const [courseAnalytics, setCourseAnalytics] = useState(null)
  const [systemHealth, setSystemHealth]     = useState(null)
  const [loading, setLoading]               = useState(true)

  useEffect(() => {
    const fetchAll = async () => {
      try {
        setLoading(true)
        const [growth, courses, health] = await Promise.allSettled([
          analyticsService.getUsersGrowth({ time_range: '30d' }),
          analyticsService.getCourseAnalytics(),
          analyticsService.getSystemHealth(),
        ])
        if (growth.status   === 'fulfilled') setUsersGrowth(growth.value)
        if (courses.status  === 'fulfilled') setCourseAnalytics(courses.value)
        if (health.status   === 'fulfilled') setSystemHealth(health.value)
      } catch {
        toast.error('Không thể tải analytics')
      } finally {
        setLoading(false)
      }
    }
    fetchAll()
  }, [])

  if (loading) return <Skeleton rows={4} tall />

  const healthMeta = {
    healthy:  { Icon: CheckIcon, cls: 'adm-health--healthy', label: 'Hệ thống bình thường' },
    warning:  { Icon: WarnIcon,  cls: 'adm-health--warning', label: 'Cảnh báo' },
    critical: { Icon: ErrorIcon, cls: 'adm-health--critical', label: 'Nghiêm trọng' },
  }

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
      {/* ── System Health ── */}
      {systemHealth && (
        <div className="adm-analytics-block">
          <h3 className="adm-analytics-block__title">Sức khỏe hệ thống</h3>
          {(() => {
            const meta = healthMeta[systemHealth.status] || healthMeta.warning
            const { Icon } = meta
            return (
              <div className={`adm-health ${meta.cls}`}>
                <span className="adm-health__icon"><Icon /></span>
                <span className="adm-health__label">{meta.label}</span>
                {systemHealth.uptime_hours != null && (
                  <span className="adm-health__uptime">Uptime: {Math.round(systemHealth.uptime_hours)}h</span>
                )}
              </div>
            )
          })()}

          {systemHealth.metrics && (
            <div className="adm-metrics">
              <MetricCard label="API Response"   value={`${systemHealth.metrics.api_response_time_ms || 0}ms`} />
              <MetricCard label="Error Rate"     value={`${systemHealth.metrics.error_rate_percentage || 0}%`} />
              <MetricCard label="DB Query"       value={`${systemHealth.metrics.database_query_time_ms || 0}ms`} />
              <MetricCard label="Storage"        value={`${systemHealth.metrics.storage_usage_percentage || 0}%`} />
              <MetricCard label="Memory"         value={`${systemHealth.metrics.memory_usage_percentage || 0}%`} />
              <MetricCard label="Sessions"       value={systemHealth.metrics.active_sessions || 0} />
            </div>
          )}

          {systemHealth.alerts?.length > 0 && (
            <div className="adm-alerts">
              {systemHealth.alerts.map((alert, i) => (
                <div key={i} className={`adm-alert adm-alert--${alert.alert_type}`}>{alert.message}</div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* ── Users Growth ── */}
      {usersGrowth?.statistics && (
        <div className="adm-analytics-block">
          <h3 className="adm-analytics-block__title">Tăng trưởng người dùng (30 ngày)</h3>
          <div className="adm-metrics">
            <MetricCard label="Tỉ lệ tăng trưởng"    value={`${usersGrowth.statistics.total_growth_rate || 0}%`} />
            <MetricCard label="Tăng trưởng học viên"  value={`${usersGrowth.statistics.student_growth_rate || 0}%`} />
            <MetricCard label="Tỉ lệ giữ chân"        value={`${usersGrowth.statistics.user_retention_rate || 0}%`} />
            <MetricCard label="TB mới/ngày"            value={usersGrowth.statistics.avg_daily_new_users || 0} />
          </div>
        </div>
      )}

      {/* ── Course Analytics ── */}
      {courseAnalytics && (
        <div className="adm-analytics-block">
          <h3 className="adm-analytics-block__title">Phân tích khóa học</h3>
          <div className="adm-stat-strip" style={{ marginBottom: 16 }}>
            <div className="adm-stat-item">
              <span className="adm-stat-item__val">{courseAnalytics.total_enrollments || 0}</span>
              <span className="adm-stat-item__lbl">Tổng đăng ký</span>
            </div>
            <div className="adm-stat-item">
              <span className="adm-stat-item__val">{courseAnalytics.overall_completion_rate || 0}%</span>
              <span className="adm-stat-item__lbl">Tỉ lệ hoàn thành</span>
            </div>
          </div>

          {courseAnalytics.top_courses?.length > 0 && (
            <div className="adm-table-wrap">
              <table className="adm-table">
                <thead><tr><th>Khóa học</th><th>Đăng ký</th><th>Hoàn thành</th><th>Quiz TB</th><th>Giảng viên</th></tr></thead>
                <tbody>
                  {courseAnalytics.top_courses.map((c, i) => (
                    <tr key={i}>
                      <td className="adm-cell-primary">{c.title}</td>
                      <td className="adm-cell-muted">{c.enrollments || 0}</td>
                      <td className="adm-cell-muted">{c.completion_rate || 0}%</td>
                      <td className="adm-cell-muted">{c.avg_quiz_score || 0}</td>
                      <td className="adm-cell-muted">{c.instructor_name || '—'}</td>
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

/* ─── Shared sub-components ─────────────────── */
const MetricCard = ({ label, value }) => (
  <div className="adm-metric-card">
    <span className="adm-metric-card__val">{value}</span>
    <span className="adm-metric-card__lbl">{label}</span>
  </div>
)

const Skeleton = ({ rows = 4, tall = false }) => (
  <div className="adm-skeleton-list">
    {Array.from({ length: rows }, (_, i) => (
      <div key={i} className={`adm-skeleton-row ${tall ? 'adm-skeleton-row--tall' : ''}`} />
    ))}
  </div>
)

export default AdminPage
