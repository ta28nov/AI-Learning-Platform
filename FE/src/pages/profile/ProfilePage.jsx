import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { useForm } from 'react-hook-form'
import toast from 'react-hot-toast'
import { useAuthStore } from '@stores/authStore'
import userService from '@services/userService'
import Button from '@components/ui/Button'
import './ProfilePage.css'

/**
 * ProfilePage - Trang thông tin cá nhân, kết nối userService
 * Route: /dashboard/profile
 * API: GET /users/me -> UserProfileResponse
 *      PATCH /users/me -> UserProfileUpdateRequest
 * Docs: BE_TO_FE_MAPPING.md line 65-96
 * Fields từ docs:
 *   - full_name, email, role, avatar_url, bio (max 500),
 *   - contact_info (str|null), learning_preferences (List[str]),
 *   - created_at, updated_at
 * Update fields: full_name, avatar_url, bio, contact_info, learning_preferences
 */
const ProfilePage = () => {
  const { user } = useAuthStore()
  const [loading, setLoading] = useState(true)
  const [editing, setEditing] = useState(false)
  const [saving, setSaving] = useState(false)
  const [profile, setProfile] = useState(null)

  const { register, handleSubmit, reset, formState: { errors } } = useForm()

  // Lấy thông tin profile khi mount
  useEffect(() => {
    const fetchProfile = async () => {
      try {
        setLoading(true)
        const data = await userService.getProfile()
        setProfile(data)
        // Reset form với data từ API (theo docs schema)
        reset({
          full_name: data?.full_name || '',
          bio: data?.bio || '',
          contact_info: data?.contact_info || '',
          avatar_url: data?.avatar_url || '',
          learning_preferences: (data?.learning_preferences || []).join(', ')
        })
      } catch (error) {
        toast.error('Không thể tải thông tin cá nhân')
      } finally {
        setLoading(false)
      }
    }
    fetchProfile()
  }, [reset])

  // Xử lý lưu thông tin — gửi đúng schema UserProfileUpdateRequest
  const onSubmit = async (formData) => {
    try {
      setSaving(true)
      // Chuyển learning_preferences từ chuỗi thành mảng
      const prefsArray = formData.learning_preferences
        ? formData.learning_preferences.split(',').map(s => s.trim()).filter(Boolean)
        : null

      const updateData = {
        full_name: formData.full_name || null,
        avatar_url: formData.avatar_url || null,
        bio: formData.bio || null,
        contact_info: formData.contact_info || null,
        learning_preferences: prefsArray
      }
      const result = await userService.updateProfile(updateData)
      // API trả về user_id, message, updated_at — fetch lại profile mới
      await userService.getProfile().then(setProfile)
      setEditing(false)
      toast.success(result?.message || 'Cập nhật thành công!')
    } catch (error) {
      toast.error(error?.message || 'Không thể cập nhật')
    } finally {
      setSaving(false)
    }
  }

  // Animation
  const fadeUp = { hidden: { opacity: 0, y: 20 }, visible: { opacity: 1, y: 0 } }

  if (loading) {
    return (
      <div className="profile-page">
        <div className="profile-skeleton__header" />
        <div className="profile-skeleton__body" />
      </div>
    )
  }

  const displayData = profile || user

  return (
    <div className="profile-page">
      {/* Header với avatar */}
      <motion.div
        className="profile-header"
        initial="hidden"
        animate="visible"
        variants={fadeUp}
        transition={{ duration: 0.4 }}
      >
        <div className="profile-header__bg" />
        <div className="profile-header__content">
          <div className="profile-avatar">
            {displayData?.avatar_url ? (
              <img src={displayData.avatar_url} alt="Avatar" className="profile-avatar__img" />
            ) : (
              <div className="profile-avatar__placeholder">
                {(displayData?.full_name || 'U').charAt(0).toUpperCase()}
              </div>
            )}
          </div>
          <div className="profile-header__info">
            <h1 className="profile-header__name">{displayData?.full_name || 'Người dùng'}</h1>
            <span className="profile-header__email">{displayData?.email}</span>
            <span className={`profile-header__role profile-header__role--${displayData?.role}`}>
              {displayData?.role === 'admin' ? 'Quản trị viên'
                : displayData?.role === 'instructor' ? 'Giảng viên'
                : 'Học viên'}
            </span>
          </div>
          <div className="profile-header__actions">
            {!editing ? (
              <Button variant="outline" size="sm" onClick={() => setEditing(true)}>Chỉnh sửa</Button>
            ) : (
              <Button variant="outline" size="sm" onClick={() => { setEditing(false); reset(); }}>Hủy</Button>
            )}
          </div>
        </div>
      </motion.div>

      {/* Nội dung chính */}
      <motion.div
        className="profile-body"
        initial="hidden"
        animate="visible"
        variants={fadeUp}
        transition={{ duration: 0.4, delay: 0.1 }}
      >
        {!editing ? (
          /* ===== CHẾ ĐỘ XEM ===== */
          <div className="profile-sections">
            <div className="profile-section">
              <h3 className="profile-section__title">Thông tin cá nhân</h3>
              <div className="profile-fields">
                <ProfileField label="Họ và tên" value={displayData?.full_name} />
                <ProfileField label="Email" value={displayData?.email} />
                <ProfileField
                  label="Vai trò"
                  value={displayData?.role === 'admin' ? 'Quản trị viên'
                    : displayData?.role === 'instructor' ? 'Giảng viên'
                    : 'Học viên'}
                />
                <ProfileField
                  label="Tiểu sử"
                  value={displayData?.bio || 'Chưa có tiểu sử'}
                  muted={!displayData?.bio}
                />
              </div>
            </div>

            {/* Liên hệ — contact_info là str|null theo docs */}
            <div className="profile-section">
              <h3 className="profile-section__title">Liên hệ</h3>
              <div className="profile-fields">
                <ProfileField
                  label="Thông tin liên hệ"
                  value={displayData?.contact_info || 'Chưa cập nhật'}
                  muted={!displayData?.contact_info}
                />
              </div>
            </div>

            {/* Learning preferences — Tags array (docs line 78) */}
            <div className="profile-section">
              <h3 className="profile-section__title">Sở thích học tập</h3>
              <div className="profile-fields">
                {displayData?.learning_preferences?.length > 0 ? (
                  <div className="profile-tags">
                    {displayData.learning_preferences.map((pref, i) => (
                      <span key={i} className="profile-tag">{pref}</span>
                    ))}
                  </div>
                ) : (
                  <ProfileField label="" value="Chưa thiết lập sở thích học tập" muted />
                )}
              </div>
            </div>

            {/* Tài khoản */}
            <div className="profile-section">
              <h3 className="profile-section__title">Tài khoản</h3>
              <div className="profile-fields">
                <ProfileField
                  label="Ngày tạo"
                  value={displayData?.created_at
                    ? new Date(displayData.created_at).toLocaleDateString('vi-VN')
                    : '—'}
                />
                <ProfileField
                  label="Cập nhật lần cuối"
                  value={displayData?.updated_at
                    ? new Date(displayData.updated_at).toLocaleDateString('vi-VN')
                    : '—'}
                />
              </div>
            </div>
          </div>
        ) : (
          /* ===== CHẾ ĐỘ CHỈNH SỬA ===== */
          <form className="profile-form" onSubmit={handleSubmit(onSubmit)}>
            <div className="profile-section">
              <h3 className="profile-section__title">Chỉnh sửa thông tin</h3>
              <div className="profile-form__grid">
                {/* Họ và tên — min 3, max 100 */}
                <div className="profile-form__field">
                  <label>Họ và tên</label>
                  <input
                    type="text"
                    {...register('full_name', {
                      required: 'Vui lòng nhập họ tên',
                      minLength: { value: 3, message: 'Tối thiểu 3 ký tự' },
                      maxLength: { value: 100, message: 'Tối đa 100 ký tự' }
                    })}
                    className={errors.full_name ? 'input--error' : ''}
                  />
                  {errors.full_name && <span className="field-error">{errors.full_name.message}</span>}
                </div>

                {/* Avatar URL */}
                <div className="profile-form__field">
                  <label>Avatar URL</label>
                  <input
                    type="url"
                    {...register('avatar_url')}
                    placeholder="https://example.com/avatar.jpg"
                  />
                </div>

                {/* Tiểu sử — max 500 */}
                <div className="profile-form__field profile-form__field--full">
                  <label>Tiểu sử</label>
                  <textarea
                    {...register('bio', {
                      maxLength: { value: 500, message: 'Tối đa 500 ký tự' }
                    })}
                    rows={3}
                    placeholder="Giới thiệu ngắn gọn về bản thân..."
                  />
                  {errors.bio && <span className="field-error">{errors.bio.message}</span>}
                </div>

                {/* Thông tin liên hệ — max 200 */}
                <div className="profile-form__field profile-form__field--full">
                  <label>Thông tin liên hệ</label>
                  <input
                    type="text"
                    {...register('contact_info', {
                      maxLength: { value: 200, message: 'Tối đa 200 ký tự' }
                    })}
                    placeholder="Số điện thoại, địa chỉ, hoặc link liên hệ..."
                  />
                  {errors.contact_info && <span className="field-error">{errors.contact_info.message}</span>}
                </div>

                {/* Learning preferences — Tags nhập bằng dấu phẩy */}
                <div className="profile-form__field profile-form__field--full">
                  <label>Sở thích học tập (cách nhau bằng dấu phẩy)</label>
                  <input
                    type="text"
                    {...register('learning_preferences')}
                    placeholder="Programming, Data Science, AI, Math..."
                  />
                </div>
              </div>

              <div className="profile-form__actions">
                <Button variant="primary" type="submit" loading={saving} disabled={saving}>
                  Lưu thay đổi
                </Button>
                <Button variant="outline" type="button" onClick={() => { setEditing(false); reset(); }}>
                  Hủy bỏ
                </Button>
              </div>
            </div>
          </form>
        )}
      </motion.div>
    </div>
  )
}

// Sub-component: hiển thị 1 field thông tin
const ProfileField = ({ label, value, muted, badge }) => (
  <div className="profile-field">
    {label && <span className="profile-field__label">{label}</span>}
    <div className="profile-field__value-wrap">
      <span className={`profile-field__value ${muted ? 'profile-field__value--muted' : ''}`}>{value}</span>
      {badge && (
        <span className={`profile-field__badge profile-field__badge--${badge}`}>
          {badge === 'active' ? 'Hoạt động' : 'Đã khóa'}
        </span>
      )}
    </div>
  </div>
)

export default ProfilePage
