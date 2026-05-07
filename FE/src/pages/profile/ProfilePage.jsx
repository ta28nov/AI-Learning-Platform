import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useForm } from 'react-hook-form'
import toast from 'react-hot-toast'
import { useAuthStore } from '@stores/authStore'
import userService from '@services/userService'
import Button from '@components/ui/Button'
import StateView from '@components/ui/StateView'
import './ProfilePage.css'

const EditIcon = () => (
  <svg viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <path d="M14.5 2.5a2.121 2.121 0 0 1 3 3L6 17l-4 1 1-4L14.5 2.5z"/>
  </svg>
)

/**
 * ProfilePage — Trang thông tin cá nhân
 * Route: /dashboard/profile
 * API: GET /users/me → userService.getProfile — unchanged
 *      PATCH /users/me → userService.updateProfile — unchanged
 */
const ProfilePage = () => {
  const { user } = useAuthStore()
  const [loading, setLoading] = useState(true)
  const [editing, setEditing] = useState(false)
  const [saving, setSaving] = useState(false)
  const [profile, setProfile] = useState(null)

  const { register, handleSubmit, reset, formState: { errors } } = useForm()

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        setLoading(true)
        const data = await userService.getProfile()
        setProfile(data)
        reset({
          full_name: data?.full_name || '',
          bio: data?.bio || '',
          contact_info: data?.contact_info || '',
          avatar_url: data?.avatar_url || '',
          learning_preferences: (data?.learning_preferences || []).join(', '),
        })
      } catch {
        toast.error('Không thể tải thông tin cá nhân')
      } finally {
        setLoading(false)
      }
    }
    fetchProfile()
  }, [reset])

  const onSubmit = async (formData) => {
    try {
      setSaving(true)
      const prefsArray = formData.learning_preferences
        ? formData.learning_preferences.split(',').map(s => s.trim()).filter(Boolean)
        : null
      const updateData = {
        full_name: formData.full_name || null,
        avatar_url: formData.avatar_url || null,
        bio: formData.bio || null,
        contact_info: formData.contact_info || null,
        learning_preferences: prefsArray,
      }
      const result = await userService.updateProfile(updateData)
      await userService.getProfile().then(setProfile)
      setEditing(false)
      toast.success(result?.message || 'Cập nhật thành công!')
    } catch (error) {
      toast.error(error?.message || 'Không thể cập nhật')
    } finally {
      setSaving(false)
    }
  }

  if (loading) return <div className="pf-page"><StateView type="loading" message="Đang tải hồ sơ…" /></div>

  const data = profile || user
  const roleName = { admin: 'Quản trị viên', instructor: 'Giảng viên', student: 'Học viên' }
  const initial = (data?.full_name || 'U').charAt(0).toUpperCase()

  return (
    <div className="pf-page">
      {/* Cover hero */}
      <motion.div
        className="pf-hero"
        initial={{ opacity: 0, y: 24 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, ease: [0.65, 0, 0.35, 1] }}
      >
        <div className="pf-hero__cover" />
        <div className="pf-hero__content">
          <div className="pf-avatar">
            {data?.avatar_url ? (
              <img src={data.avatar_url} alt="Avatar" className="pf-avatar__img" />
            ) : (
              <div className="pf-avatar__initial">{initial}</div>
            )}
          </div>
          <div className="pf-hero__info">
            <h1 className="pf-hero__name">{data?.full_name || 'Người dùng'}</h1>
            <p className="pf-hero__email">{data?.email}</p>
            <span className={`pf-role pf-role--${data?.role}`}>{roleName[data?.role] ?? data?.role}</span>
          </div>
          <div className="pf-hero__edit">
            {!editing ? (
              <Button variant="outline" size="sm" onClick={() => setEditing(true)}>
                <EditIcon /> Chỉnh sửa
              </Button>
            ) : (
              <Button variant="outline" size="sm" onClick={() => { setEditing(false); reset() }}>
                Hủy
              </Button>
            )}
          </div>
        </div>
      </motion.div>

      {/* Body */}
      <AnimatePresence mode="wait">
        {!editing ? (
          <motion.div
            key="view"
            className="pf-body"
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            transition={{ duration: 0.35 }}
          >
            <Section title="Thông tin cá nhân">
              <Field label="Họ và tên" value={data?.full_name} />
              <Field label="Email" value={data?.email} />
              <Field label="Vai trò" value={roleName[data?.role] ?? data?.role} />
              <Field label="Tiểu sử" value={data?.bio || 'Chưa có tiểu sử'} muted={!data?.bio} />
            </Section>

            <Section title="Liên hệ">
              <Field label="Thông tin liên hệ" value={data?.contact_info || 'Chưa cập nhật'} muted={!data?.contact_info} />
            </Section>

            <Section title="Sở thích học tập">
              {data?.learning_preferences?.length > 0 ? (
                <div className="pf-tags">
                  {data.learning_preferences.map((pref, i) => (
                    <span key={i} className="pf-tag">{pref}</span>
                  ))}
                </div>
              ) : (
                <Field label="" value="Chưa thiết lập sở thích học tập" muted />
              )}
            </Section>

            <Section title="Tài khoản">
              <Field label="Ngày tạo" value={data?.created_at ? new Date(data.created_at).toLocaleDateString('vi-VN') : '—'} />
              <Field label="Cập nhật" value={data?.updated_at ? new Date(data.updated_at).toLocaleDateString('vi-VN') : '—'} />
            </Section>
          </motion.div>
        ) : (
          <motion.form
            key="edit"
            className="pf-body pf-form"
            onSubmit={handleSubmit(onSubmit)}
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            transition={{ duration: 0.35 }}
          >
            <Section title="Chỉnh sửa thông tin">
              <div className="pf-form__grid">
                <div className="pf-form__field">
                  <label className="pf-form__label">Họ và tên <span className="pf-required">*</span></label>
                  <input
                    {...register('full_name', {
                      required: 'Vui lòng nhập họ tên',
                      maxLength: { value: 100, message: 'Tối đa 100 ký tự' },
                      validate: (v) => {
                        const words = v.trim().split(/\s+/).filter(Boolean)
                        if (words.length < 2) return 'Vui lòng nhập đầy đủ họ và tên (ít nhất 2 từ)'
                        return true
                      },
                    })}
                    className={`pf-input ${errors.full_name ? 'pf-input--error' : ''}`}
                  />
                  {errors.full_name && <p className="pf-error">{errors.full_name.message}</p>}
                </div>

                <div className="pf-form__field">
                  <label className="pf-form__label">Avatar URL</label>
                  <input type="url" {...register('avatar_url')} className="pf-input" placeholder="https://example.com/avatar.jpg" />
                </div>

                <div className="pf-form__field pf-form__field--full">
                  <label className="pf-form__label">Tiểu sử</label>
                  <textarea
                    {...register('bio', { maxLength: { value: 500, message: 'Tối đa 500 ký tự' } })}
                    className="pf-input pf-textarea"
                    rows={3}
                    placeholder="Giới thiệu ngắn gọn về bản thân…"
                  />
                  {errors.bio && <p className="pf-error">{errors.bio.message}</p>}
                </div>

                <div className="pf-form__field pf-form__field--full">
                  <label className="pf-form__label">Thông tin liên hệ</label>
                  <input
                    {...register('contact_info', { maxLength: { value: 200, message: 'Tối đa 200 ký tự' } })}
                    className="pf-input"
                    placeholder="Số điện thoại, địa chỉ, hoặc link liên hệ…"
                  />
                  {errors.contact_info && <p className="pf-error">{errors.contact_info.message}</p>}
                </div>

                <div className="pf-form__field pf-form__field--full">
                  <label className="pf-form__label">Sở thích học tập <span className="pf-hint">(cách nhau bằng dấu phẩy)</span></label>
                  <input
                    {...register('learning_preferences')}
                    className="pf-input"
                    placeholder="Programming, Data Science, AI, Math…"
                  />
                </div>
              </div>

              <div className="pf-form__actions">
                <Button variant="primary" type="submit" loading={saving} disabled={saving}>Lưu thay đổi</Button>
                <Button variant="outline" type="button" onClick={() => { setEditing(false); reset() }}>Hủy bỏ</Button>
              </div>
            </Section>
          </motion.form>
        )}
      </AnimatePresence>
    </div>
  )
}

const Section = ({ title, children }) => (
  <div className="pf-section">
    <h3 className="pf-section__title">{title}</h3>
    <div className="pf-section__body">{children}</div>
  </div>
)

const Field = ({ label, value, muted }) => (
  <div className="pf-field">
    {label && <span className="pf-field__label">{label}</span>}
    <span className={`pf-field__value ${muted ? 'pf-field__value--muted' : ''}`}>{value}</span>
  </div>
)

export default ProfilePage
