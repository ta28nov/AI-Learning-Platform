import { useState, useEffect, useCallback } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import toast from 'react-hot-toast'
import classService from '@services/classService'
import { useAuthStore } from '@stores/authStore'
import Button from '@components/ui/Button'
import Input from '@components/ui/Input'
import Modal, { ModalFooter } from '@components/ui/Modal'
import StateView from '@components/ui/StateView'
import AILoadingState from '@components/ui/AILoadingState'
import { navigateToCourseLearning } from '@utils/classLearningContext'
import './ClassDetailPage.css'

const CopyIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
  </svg>
)

/**
 * ClassDetailPage — Chi tiết lớp học (instructor + student)
 * Routes: /dashboard/instructor/classes/:classId | /dashboard/classes/:classId
 * API: GET /classes/{classId}; instructor thêm students/progress CRUD
 */
const ClassDetailPage = () => {
  const { classId } = useParams()
  const navigate = useNavigate()
  const { user } = useAuthStore()
  const role = user?.role || 'student'
  const isInstructor = role === 'instructor' || role === 'admin'
  const listPath = isInstructor ? '/dashboard/instructor/classes' : '/dashboard/classes'

  const [classData, setClassData] = useState(null)
  const [students, setStudents] = useState([])
  const [classProgress, setClassProgress] = useState(null)
  const [activeTab, setActiveTab] = useState('info')
  const [loading, setLoading] = useState(true)
  const [editOpen, setEditOpen] = useState(false)
  const [editForm, setEditForm] = useState({ name: '', description: '', max_students: 30 })
  const [saving, setSaving] = useState(false)
  const [deleting, setDeleting] = useState(false)
  const [studentDetailOpen, setStudentDetailOpen] = useState(false)
  const [studentDetail, setStudentDetail] = useState(null)
  const [studentDetailLoading, setStudentDetailLoading] = useState(false)
  const [myProgress, setMyProgress] = useState(null)
  const [myProgressLoading, setMyProgressLoading] = useState(false)

  const fetchData = useCallback(async () => {
    try {
      setLoading(true)
      const detail = await classService.getClassDetail(classId)
      setClassData(detail)

      if (isInstructor) {
        const [studentList, progress] = await Promise.all([
          classService.getStudents(classId).catch(() => ({ data: [] })),
          classService.getClassProgress(classId).catch(() => null),
        ])
        setStudents(studentList.data || [])
        setClassProgress(progress)
      } else {
        setStudents([])
        setClassProgress(null)
      }
    } catch {
      toast.error('Không thể tải thông tin lớp học')
      setClassData(null)
    } finally {
      setLoading(false)
    }
  }, [classId, isInstructor])

  useEffect(() => { fetchData() }, [fetchData])

  const loadMyProgress = useCallback(async () => {
    if (isInstructor) return
    setMyProgressLoading(true)
    try {
      const data = await classService.getMyProgress(classId)
      setMyProgress(data)
    } catch {
      setMyProgress(null)
    } finally {
      setMyProgressLoading(false)
    }
  }, [classId, isInstructor])

  useEffect(() => {
    if (!isInstructor && activeTab === 'my-progress') {
      loadMyProgress()
    }
  }, [activeTab, isInstructor, loadMyProgress])

  const copyInviteCode = () => {
    navigator.clipboard.writeText(classData?.invite_code || '')
    toast.success('Đã sao chép mã mời')
  }

  const openEdit = () => {
    setEditForm({
      name: classData?.name || '',
      description: classData?.description || '',
      max_students: classData?.max_students || 30,
    })
    setEditOpen(true)
  }

  const handleSaveEdit = async () => {
    setSaving(true)
    try {
      await classService.updateClass(classId, {
        name: editForm.name.trim(),
        description: editForm.description.trim(),
        max_students: Number(editForm.max_students),
      })
      toast.success('Đã cập nhật lớp học')
      setEditOpen(false)
      await fetchData()
    } catch (error) {
      toast.error(error.message || 'Không thể cập nhật')
    } finally {
      setSaving(false)
    }
  }

  const handleDelete = async () => {
    if (!window.confirm('Xóa lớp học này? Hành động không thể hoàn tác.')) return
    setDeleting(true)
    try {
      await classService.deleteClass(classId)
      toast.success('Đã xóa lớp học')
      navigate(listPath)
    } catch (error) {
      toast.error(error.message || 'Không thể xóa lớp')
    } finally {
      setDeleting(false)
    }
  }

  const handleRemoveStudent = async (studentId) => {
    if (!window.confirm('Gỡ học viên khỏi lớp?')) return
    try {
      await classService.removeStudent(classId, studentId)
      toast.success('Đã gỡ học viên')
      await fetchData()
    } catch (error) {
      toast.error(error.message || 'Không thể gỡ học viên')
    }
  }

  const openStudentDetail = async (studentId, studentName) => {
    setStudentDetailOpen(true)
    setStudentDetail(null)
    setStudentDetailLoading(true)
    try {
      const detail = await classService.getStudentDetail(classId, studentId)
      setStudentDetail({ ...detail, student_name: detail.student_name || studentName })
    } catch (error) {
      toast.error(error.message || 'Không thể tải hồ sơ học viên')
      setStudentDetailOpen(false)
    } finally {
      setStudentDetailLoading(false)
    }
  }

  const closeStudentDetail = () => {
    setStudentDetailOpen(false)
    setStudentDetail(null)
  }

  if (loading) {
    return (
      <div className="cld-page">
        <AILoadingState
          title="AI đang tải thông tin lớp học"
          message="Đang đồng bộ chi tiết lớp và danh sách học viên."
          steps={[
            'Đang tải thông tin lớp học...',
            'Đang tải danh sách học viên...',
            'Đang sắp xếp dữ liệu hiển thị...',
          ]}
        />
      </div>
    )
  }
  if (!classData) return (
    <div className="cld-page">
      <StateView type="empty" message="Không tìm thấy lớp học" action={{ label: 'Quay lại', onClick: () => navigate(listPath) }} />
    </div>
  )

  const courseId = classData?.course?.id || classData?.course_id

  const goToCourseLearning = (resume = false) => {
    if (!courseId) return
    navigateToCourseLearning(navigate, {
      courseId,
      classId,
      className: classData.name,
      instructorName: classData.instructor_name,
      nextLesson: classData.next_lesson,
      resume,
    })
  }

  const tabs = isInstructor
    ? [
        { id: 'info', label: 'Thông tin' },
        { id: 'students', label: `Học viên (${students.length})` },
        { id: 'progress', label: 'Tiến độ lớp' },
      ]
    : [
        { id: 'info', label: 'Thông tin' },
        { id: 'my-progress', label: 'Tiến độ của tôi' },
      ]

  const statusLabel = { active: 'Đang hoạt động', completed: 'Đã kết thúc', preparing: 'Chuẩn bị', cancelled: 'Đã hủy' }
  const statusClass = { active: 'cld-status--active', completed: 'cld-status--completed', cancelled: 'cld-status--cancelled', preparing: 'cld-status--preparing' }

  return (
    <div className="cld-page">
      {/* Header */}
      <motion.div className="cld-header" initial={{ opacity: 0, y: 24 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5, ease: [0.65, 0, 0.35, 1] }}>
        <button type="button" className="cld-back" onClick={() => navigate(listPath)}>
          <svg viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.5">
            <path d="M15 10H5m0 0 5-5M5 10l5 5" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
          Danh sách lớp
        </button>
        <div className="cld-header__row">
          <h1 className="cld-title">{classData.name}</h1>
          <span className={`cld-status ${statusClass[classData.status] || ''}`}>
            {statusLabel[classData.status] ?? classData.status}
          </span>
        </div>
        {classData.course?.title && <p className="cld-subtitle">Khóa học: {classData.course.title}</p>}
        {!isInstructor && classData.instructor_name && (
          <p className="cld-subtitle">Giảng viên: {classData.instructor_name}</p>
        )}
        {isInstructor && (
          <motion.div className="cld-header__actions">
            <Button variant="outline" size="sm" onClick={openEdit}>Chỉnh sửa</Button>
            <Button variant="outline" size="sm" loading={deleting} onClick={handleDelete}>Xóa lớp</Button>
          </motion.div>
        )}
      </motion.div>

      {/* Tabs */}
      <div className="cld-tabs">
        {tabs.map(tab => (
          <button
            key={tab.id}
            className={`cld-tab ${activeTab === tab.id ? 'cld-tab--active' : ''}`}
            onClick={() => setActiveTab(tab.id)}
          >
            {tab.label}
          </button>
        ))}
      </div>

      <AnimatePresence mode="wait">
        {activeTab === 'info' && (
          <motion.div
            key="info"
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            transition={{ duration: 0.3 }}
          >
            {isInstructor && classData.invite_code && (
              <div className="cld-invite">
                <span className="cld-invite__label">Mã mời lớp</span>
                <div className="cld-invite__row">
                  <code className="cld-invite__code">{classData.invite_code}</code>
                  <button type="button" className="cld-invite__copy" onClick={copyInviteCode} title="Sao chép">
                    <CopyIcon />
                  </button>
                </div>
              </div>
            )}

            {classData.description && <p className="cld-desc">{classData.description}</p>}

            <div className="cld-info-grid">
              {[
                { label: 'Học viên', value: classData.student_count ?? students.length },
                { label: 'Bắt đầu', value: classData.start_date ? new Date(classData.start_date).toLocaleDateString('vi-VN') : '—' },
                { label: 'Kết thúc', value: classData.end_date ? new Date(classData.end_date).toLocaleDateString('vi-VN') : '—' },
                ...(!isInstructor && classData.my_progress != null
                  ? [{ label: 'Tiến độ của bạn', value: `${Math.round(classData.my_progress)}%` }]
                  : []),
              ].map(({ label, value }) => (
                <div key={label} className="cld-info-card">
                  <span className="cld-info-card__label">{label}</span>
                  <span className="cld-info-card__value">{value}</span>
                </div>
              ))}
            </div>

            {!isInstructor && (
              <div className="cld-student-learn">
                <h2 className="cld-section-title">Cách học trong lớp này</h2>
                <ol className="cld-learn-steps">
                  <li className="cld-learn-step cld-learn-step--done">
                    <span className="cld-learn-step__num">1</span>
                    <div>
                      <strong>Tham gia lớp</strong>
                      <p>Bạn đã vào lớp «{classData.name}» — khóa «{classData.course?.title || '—'}».</p>
                    </div>
                  </li>
                  <li className="cld-learn-step">
                    <span className="cld-learn-step__num">2</span>
                    <div>
                      <strong>Học theo module → bài học</strong>
                      <p>Mở nội dung khóa, chọn module, đọc/xem bài và đánh dấu hoàn thành. AI trợ giảng luôn sẵn sàng ở góc màn hình.</p>
                    </div>
                  </li>
                  <li className="cld-learn-step">
                    <span className="cld-learn-step__num">3</span>
                    <div>
                      <strong>Quiz & theo dõi tiến độ</strong>
                      <p>Làm quiz sau mỗi module; tiến độ cập nhật trên trang lớp và «Khóa học của tôi».</p>
                    </div>
                  </li>
                </ol>
              </div>
            )}

            {courseId && (
              <div className="cld-course-cta">
                <Button onClick={() => goToCourseLearning(true)}>
                  {(classData.my_progress ?? 0) > 0 ? 'Tiếp tục học' : 'Bắt đầu học'}
                </Button>
                {classData.next_lesson?.lesson_title && (
                  <p className="cld-next-lesson">
                    Bài tiếp theo: {classData.next_lesson.module_title ? `${classData.next_lesson.module_title} · ` : ''}
                    {classData.next_lesson.lesson_title}
                  </p>
                )}
                <Button variant="outline" onClick={() => goToCourseLearning(false)}>
                  Xem tất cả module
                </Button>
                <Button variant="outline" onClick={() => navigate(`/dashboard/courses/${courseId}`)}>
                  Tổng quan khóa
                </Button>
              </div>
            )}

            {classData.class_stats && isInstructor && (
              <div className="cld-stats">
                <h2 className="cld-section-title">Thống kê</h2>
                <div className="cld-stats-grid">
                  <div className="cld-stat"><span className="cld-stat__value">{classData.class_stats.total_students}</span><span className="cld-stat__label">Học viên</span></div>
                  <div className="cld-stat"><span className="cld-stat__value">{classData.class_stats.lessons_completed || 0}</span><span className="cld-stat__label">Bài hoàn thành</span></div>
                  <div className="cld-stat"><span className="cld-stat__value">{classData.class_stats.avg_quiz_score || 0}</span><span className="cld-stat__label">Điểm TB quiz</span></div>
                </div>
              </div>
            )}
          </motion.div>
        )}

        {activeTab === 'students' && isInstructor && (
          <motion.div
            key="students"
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            transition={{ duration: 0.3 }}
          >
            {students.length === 0 ? (
              <StateView type="empty" message="Chưa có học viên nào trong lớp" />
            ) : (
              <div className="cld-table-wrap">
                <table className="cld-table">
                  <thead>
                    <tr>
                      <th>Học viên</th>
                      <th>Email</th>
                      <th>Tiến độ</th>
                      <th>Quiz TB</th>
                      <th />
                    </tr>
                  </thead>
                  <tbody>
                    {students.map((s) => {
                      const sid = s.student_id || s.id
                      const pct = Math.round(s.progress || 0)
                      return (
                      <tr key={sid}>
                        <td className="cld-table__name">
                          <button type="button" className="cld-student-link" onClick={() => openStudentDetail(sid, s.student_name)}>
                            {s.student_name}
                          </button>
                        </td>
                        <td>{s.email}</td>
                        <td>
                          <div className="cld-progress-cell">
                            <div className="cld-progress-bar">
                              <div className="cld-progress-fill" style={{ width: `${pct}%` }} />
                            </div>
                            <span>{pct}%</span>
                          </div>
                        </td>
                        <td>{s.quiz_average != null ? `${Math.round(s.quiz_average)}%` : '—'}</td>
                        <td>
                          <Button variant="outline" size="sm" onClick={() => handleRemoveStudent(sid)}>
                            Gỡ
                          </Button>
                        </td>
                      </tr>
                    )})}
                  </tbody>
                </table>
              </div>
            )}
          </motion.div>
        )}

        {activeTab === 'progress' && isInstructor && (
          <motion.div
            key="progress"
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            transition={{ duration: 0.3 }}
          >
            {!classProgress ? (
              <StateView type="empty" message="Chưa có dữ liệu tiến độ" />
            ) : (
              <div className="cld-info-grid">
                <div className="cld-info-card">
                  <span className="cld-info-card__label">Tiến độ TB</span>
                  <span className="cld-info-card__value">{Math.round(classProgress.average_progress || 0)}%</span>
                </div>
                <div className="cld-info-card">
                  <span className="cld-info-card__label">Tỷ lệ hoàn thành</span>
                  <span className="cld-info-card__value">{Math.round(classProgress.completion_rate || 0)}%</span>
                </div>
                <div className="cld-info-card">
                  <span className="cld-info-card__label">Điểm quiz TB</span>
                  <span className="cld-info-card__value">{Math.round(classProgress.average_quiz_score || 0)}%</span>
                </div>
              </div>
            )}
          </motion.div>
        )}

        {activeTab === 'my-progress' && !isInstructor && (
          <motion.div
            key="my-progress"
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            transition={{ duration: 0.3 }}
          >
            {myProgressLoading && <StateView type="loading" message="Đang tải tiến độ của bạn…" />}
            {!myProgressLoading && !myProgress && (
              <StateView type="empty" message="Chưa có dữ liệu tiến độ" />
            )}
            {!myProgressLoading && myProgress && (
              <>
                <div className="cld-info-grid">
                  <div className="cld-info-card">
                    <span className="cld-info-card__label">Tổng tiến độ</span>
                    <span className="cld-info-card__value">{Math.round(myProgress.progress?.overall_progress || 0)}%</span>
                  </div>
                  <div className="cld-info-card">
                    <span className="cld-info-card__label">Module hoàn thành</span>
                    <span className="cld-info-card__value">
                      {myProgress.progress?.completed_modules ?? 0}/{myProgress.progress?.total_modules ?? 0}
                    </span>
                  </div>
                  <div className="cld-info-card">
                    <span className="cld-info-card__label">Thời gian học</span>
                    <span className="cld-info-card__value">{Number(myProgress.progress?.total_study_time || 0).toFixed(1)}h</span>
                  </div>
                </div>

                {myProgress.modules_detail?.length > 0 && (
                  <div className="cld-student-detail__section">
                    <h2 className="cld-section-title">Tiến độ theo module</h2>
                    <ul className="cld-module-list">
                      {myProgress.modules_detail.map((mod) => (
                        <li key={mod.module_id} className="cld-module-list__item">
                          <span className="cld-module-list__title">{mod.module_title}</span>
                          <span className="cld-module-list__meta">
                            {mod.completed_lessons} bài · {Math.round(mod.progress || 0)}%
                          </span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {myProgress.quiz_scores?.length > 0 && (
                  <div className="cld-student-detail__section">
                    <h2 className="cld-section-title">Kết quả quiz</h2>
                    <ul className="cld-quiz-list">
                      {myProgress.quiz_scores.map((q) => (
                        <li key={`${q.quiz_id}-${q.attempt_date}`} className="cld-quiz-list__item">
                          <span>{q.quiz_title}</span>
                          <span className="cld-quiz-list__score">{Math.round(q.score || 0)}%</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                <div className="cld-course-cta">
                  <Button onClick={() => goToCourseLearning(true)}>Tiếp tục học</Button>
                </div>
              </>
            )}
          </motion.div>
        )}
      </AnimatePresence>

      <Modal isOpen={editOpen} onClose={() => setEditOpen(false)} title="Chỉnh sửa lớp học">
        <div className="cld-edit-form">
          <Input label="Tên lớp" value={editForm.name} onChange={(e) => setEditForm((f) => ({ ...f, name: e.target.value }))} />
          <label className="cld-edit-label">
            Mô tả
            <textarea
              className="cld-edit-textarea"
              rows={3}
              value={editForm.description}
              onChange={(e) => setEditForm((f) => ({ ...f, description: e.target.value }))}
            />
          </label>
          <Input
            type="number"
            label="Số học viên tối đa"
            value={editForm.max_students}
            onChange={(e) => setEditForm((f) => ({ ...f, max_students: e.target.value }))}
          />
        </div>
        <ModalFooter>
          <Button variant="outline" onClick={() => setEditOpen(false)}>Hủy</Button>
          <Button loading={saving} onClick={handleSaveEdit}>Lưu</Button>
        </ModalFooter>
      </Modal>

      <Modal
        isOpen={studentDetailOpen}
        onClose={closeStudentDetail}
        title={studentDetail?.student_name ? `Hồ sơ: ${studentDetail.student_name}` : 'Hồ sơ học viên'}
      >
        {studentDetailLoading ? (
          <StateView type="loading" message="Đang tải hồ sơ học viên…" />
        ) : studentDetail ? (
          <div className="cld-student-detail">
            <p className="cld-student-detail__email">{studentDetail.email}</p>
            <div className="cld-info-grid cld-student-detail__stats">
              <div className="cld-info-card">
                <span className="cld-info-card__label">Tiến độ</span>
                <span className="cld-info-card__value">{Math.round(studentDetail.progress?.overall_progress || 0)}%</span>
              </div>
              <div className="cld-info-card">
                <span className="cld-info-card__label">Modules</span>
                <span className="cld-info-card__value">
                  {studentDetail.progress?.completed_modules || 0}/{studentDetail.progress?.total_modules || 0}
                </span>
              </div>
              <div className="cld-info-card">
                <span className="cld-info-card__label">Giờ học</span>
                <span className="cld-info-card__value">{Math.round(studentDetail.progress?.total_study_time || 0)}h</span>
              </div>
            </div>

            {(studentDetail.modules_detail || []).length > 0 && (
              <div className="cld-student-detail__section">
                <h3 className="cld-section-title">Tiến độ theo module</h3>
                <ul className="cld-module-list">
                  {studentDetail.modules_detail.map((m) => (
                    <li key={m.module_id} className="cld-module-list__item">
                      <span className="cld-module-list__title">{m.module_title}</span>
                      <span className="cld-module-list__meta">
                        {m.completed_lessons ?? 0} bài · {Math.round(m.progress || 0)}%
                      </span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {(studentDetail.quiz_scores || []).length > 0 && (
              <div className="cld-student-detail__section">
                <h3 className="cld-section-title">Điểm quiz</h3>
                <ul className="cld-quiz-list">
                  {studentDetail.quiz_scores.slice(0, 8).map((q) => (
                    <li key={`${q.quiz_id}-${q.attempt_date}`} className="cld-quiz-list__item">
                      <span>{q.quiz_title}</span>
                      <span className="cld-quiz-list__score">{Math.round(q.score || 0)}%</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        ) : (
          <StateView type="empty" message="Không có dữ liệu học viên" />
        )}
        <ModalFooter>
          <Button variant="outline" onClick={closeStudentDetail}>Đóng</Button>
        </ModalFooter>
      </Modal>
    </div>
  )
}

export default ClassDetailPage
