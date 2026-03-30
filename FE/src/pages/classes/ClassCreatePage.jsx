import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import toast from 'react-hot-toast'
import classService from '@services/classService'
import Button from '@components/ui/Button'
import Card, { CardHeader, CardBody } from '@components/ui/Card'
import './ClassCreatePage.css'

/**
 * Trang tạo lớp học mới (Instructor)
 * Route: /dashboard/classes/create
 * API: POST /classes
 */
const ClassCreatePage = () => {
  const navigate = useNavigate()
  const [isLoading, setIsLoading] = useState(false)
  const { register, handleSubmit, formState: { errors } } = useForm()

  const onSubmit = async (data) => {
    setIsLoading(true)
    try {
      const response = await classService.createClass(data)
      toast.success(`Tạo lớp thành công! Mã mời: ${response.invite_code}`)
      navigate(`/dashboard/classes/${response.class_id}`)
    } catch (error) {
      toast.error(error.message || 'Không thể tạo lớp học')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="class-create-page">
      <h1 className="class-create-page__title">Tạo lớp học mới</h1>

      <form onSubmit={handleSubmit(onSubmit)}>
        <Card>
          <CardHeader><h3>Thông tin lớp học</h3></CardHeader>
          <CardBody>
            <div className="class-create-form">
              <div className="form-group">
                <label>Tên lớp</label>
                <input
                  {...register('name', { required: 'Vui lòng nhập tên lớp' })}
                  className="form-select"
                  placeholder="VD: Lớp Python cơ bản - K1"
                />
                {errors.name && <span className="form-error">{errors.name.message}</span>}
              </div>

              <div className="form-group">
                <label>Mô tả</label>
                <textarea
                  {...register('description')}
                  className="form-select"
                  rows={3}
                  placeholder="Mô tả ngắn về lớp học"
                />
              </div>

              <div className="form-group">
                <label>ID khóa học</label>
                <input
                  {...register('course_id', { required: 'Vui lòng nhập ID khóa học' })}
                  className="form-select"
                  placeholder="UUID khóa học"
                />
                {errors.course_id && <span className="form-error">{errors.course_id.message}</span>}
              </div>

              <div className="class-create-row">
                <div className="form-group">
                  <label>Ngày bắt đầu</label>
                  <input type="date" {...register('start_date')} className="form-select" />
                </div>
                <div className="form-group">
                  <label>Ngày kết thúc</label>
                  <input type="date" {...register('end_date')} className="form-select" />
                </div>
              </div>

              <div className="form-group">
                <label>Số học viên tối đa</label>
                <input
                  type="number"
                  {...register('max_students', { min: 1 })}
                  className="form-select"
                  placeholder="VD: 30"
                />
              </div>
            </div>
          </CardBody>
        </Card>

        <div className="class-create-actions">
          <Button variant="outline" type="button" onClick={() => navigate(-1)}>Hủy</Button>
          <Button type="submit" loading={isLoading}>Tạo lớp học</Button>
        </div>
      </form>
    </div>
  )
}

export default ClassCreatePage
