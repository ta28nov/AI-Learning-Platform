import React from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { useAuthStore } from '@stores/authStore'

/**
 * Component ProtectedRoute de bao ve cac trang can xac thuc
 * Chi cho phep truy cap neu nguoi dung da dang nhap
 * @param {Object} props - Cac thuoc tinh cua component
 * @param {React.ReactNode} props.children - Noi dung can bao ve
 * @param {Array} props.allowedRoles - Cac vai tro duoc phep truy cap
 * @param {string} props.redirectTo - Duong dan chuyen huong neu khong co quyen
 */
const ProtectedRoute = ({ 
  children, 
  allowedRoles = [], 
  redirectTo = '/auth/login' 
}) => {
  const { user, isAuthenticated } = useAuthStore()
  const location = useLocation()

  // Neu chua dang nhap, chuyen den trang login
  if (!isAuthenticated) {
    return (
      <Navigate 
        to={redirectTo} 
        state={{ from: location.pathname }} 
        replace 
      />
    )
  }

  // Neu co gioi han vai tro va nguoi dung khong co quyen
  if (allowedRoles.length > 0 && !allowedRoles.includes(user?.role)) {
    return (
      <Navigate 
        to="/unauthorized" 
        replace 
      />
    )
  }

  // Neu moi thu hop le, hien thi noi dung
  return children
}

/**
 * Component AdminRoute - Chi danh cho admin
 */
export const AdminRoute = ({ children }) => {
  return (
    <ProtectedRoute allowedRoles={['admin']}>
      {children}
    </ProtectedRoute>
  )
}

/**
 * Component InstructorRoute - Danh cho giang vien va admin
 */
export const InstructorRoute = ({ children }) => {
  return (
    <ProtectedRoute allowedRoles={['instructor', 'admin']}>
      {children}
    </ProtectedRoute>
  )
}

/**
 * Component StudentRoute - Danh cho hoc vien (tat ca cac vai tro)
 */
export const StudentRoute = ({ children }) => {
  return (
    <ProtectedRoute>
      {children}
    </ProtectedRoute>
  )
}

export default ProtectedRoute