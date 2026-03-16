import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import toast from 'react-hot-toast'
import classService from '@services/classService'
import Button from '@components/ui/Button'
import Card, { CardHeader, CardBody } from '@components/ui/Card'

/**
 * Trang tao lop hoc moi (Instructor)
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
      toast.success(`Tao lop thanh cong! Ma moi: ${response.invite_code}`)
      navigate(`/dashboard/classes/${response.class_id}`)
    } catch (error) {
      toast.error(error.message || 'Khong the tao lop')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div style={{ padding: 16, maxWidth: 700, margin: '0 auto' }}>
      <h1 style={{ fontSize: '1.5rem', fontWeight: 700, marginBottom: 20 }}>Tao lop hoc moi</h1>

      <form onSubmit={handleSubmit(onSubmit)}>
        <Card>
          <CardHeader><h3>Thong tin lop hoc</h3></CardHeader>
          <CardBody>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
              <div className="form-group">
                <label>Ten lop</label>
                <input
                  {...register('name', { required: 'Vui long nhap ten lop' })}
                  className="form-select"
                  placeholder="VD: Lop Python co ban - K1"
                />
                {errors.name && <span className="form-error">{errors.name.message}</span>}
              </div>

              <div className="form-group">
                <label>Mo ta</label>
                <textarea
                  {...register('description')}
                  className="form-select"
                  rows={3}
                  placeholder="Mo ta ngan ve lop hoc"
                />
              </div>

              <div className="form-group">
                <label>ID khoa hoc</label>
                <input
                  {...register('course_id', { required: 'Vui long nhap ID khoa hoc' })}
                  className="form-select"
                  placeholder="UUID khoa hoc"
                />
                {errors.course_id && <span className="form-error">{errors.course_id.message}</span>}
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
                <div className="form-group">
                  <label>Ngay bat dau</label>
                  <input type="date" {...register('start_date')} className="form-select" />
                </div>
                <div className="form-group">
                  <label>Ngay ket thuc</label>
                  <input type="date" {...register('end_date')} className="form-select" />
                </div>
              </div>

              <div className="form-group">
                <label>So hoc vien toi da</label>
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

        <div style={{ display: 'flex', gap: 10, marginTop: 16, justifyContent: 'flex-end' }}>
          <Button variant="outline" type="button" onClick={() => navigate(-1)}>Huy</Button>
          <Button type="submit" loading={isLoading}>Tao lop hoc</Button>
        </div>
      </form>
    </div>
  )
}

export default ClassCreatePage
