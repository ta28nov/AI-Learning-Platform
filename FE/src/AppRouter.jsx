import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import DashboardLayout from '@components/layout/DashboardLayout'
import ProtectedRoute, { AdminRoute, InstructorRoute } from '@components/layout/ProtectedRoute'

// Auth pages
import LoginPage from '@pages/auth/LoginPage'
import RegisterPage from '@pages/auth/RegisterPage'
import ForgotPasswordPage from '@pages/auth/ForgotPasswordPage'
import ResetPasswordPage from '@pages/auth/ResetPasswordPage'
import VerifyEmailPage from '@pages/auth/VerifyEmailPage'

// Main pages
import LandingPage from '@pages/LandingPage'
import DashboardPage from '@pages/DashboardPage'
import ProfilePage from '@pages/ProfilePage'
import ProgressPage from '@pages/ProgressPage'

// Course pages
import CoursesPage from '@pages/courses/CoursesPage'
import CourseDetailPage from '@pages/courses/CourseDetailPage'
import ChapterPage from '@pages/courses/ChapterPage'

// Enrollment pages
import MyCoursesPage from '@pages/enrollment/MyCoursesPage'
import StudentEnrollmentPage from '@pages/enrollment/StudentEnrollmentPage'
import InstructorDashboardPage from '@pages/enrollment/InstructorDashboardPage'

// Quiz pages
import QuizPage from '@pages/quiz/QuizPage'
import QuizDetailPage from '@pages/quiz/QuizDetailPage'

// Chat pages
import ChatPage from '@pages/chat/ChatPage'

// Admin pages
import AdminPage from '@pages/admin/AdminPage'

// Other pages
import NotFoundPage from '@pages/NotFoundPage'
import UnauthorizedPage from '@pages/UnauthorizedPage'

/**
 * Component AppRouter - Quan ly routing cho toan bo ung dung
 */
const AppRouter = () => {
  return (
    <Routes>
      {/* Public routes */}
      <Route path="/" element={<LandingPage />} />
      
      {/* Auth routes */}
      <Route path="/auth/login" element={<LoginPage />} />
      <Route path="/auth/register" element={<RegisterPage />} />
      <Route path="/auth/forgot-password" element={<ForgotPasswordPage />} />
      <Route path="/auth/reset-password" element={<ResetPasswordPage />} />
      <Route path="/auth/verify-email" element={<VerifyEmailPage />} />

      {/* Protected routes with dashboard layout */}
      <Route 
        path="/dashboard" 
        element={
          <ProtectedRoute>
            <DashboardLayout />
          </ProtectedRoute>
        }
      >
        {/* Dashboard home */}
        <Route index element={<DashboardPage />} />
        
        {/* Profile */}
        <Route path="profile" element={<ProfilePage />} />
        <Route path="progress" element={<ProgressPage />} />
        
        {/* Courses */}
        <Route path="courses" element={<CoursesPage />} />
        <Route path="courses/:courseId" element={<CourseDetailPage />} />
        <Route path="courses/:courseId/chapters/:chapterId" element={<ChapterPage />} />
        
        {/* My Courses */}
        <Route path="my-courses" element={<MyCoursesPage />} />
        <Route path="enrollment/:enrollmentId" element={<StudentEnrollmentPage />} />
        
        {/* Quiz */}
        <Route path="quiz" element={<QuizPage />} />
        <Route path="quiz/:quizId" element={<QuizDetailPage />} />
        
        {/* Chat */}
        <Route path="chat" element={<ChatPage />} />
        
        {/* Instructor routes */}
        <Route path="instructor" element={
          <InstructorRoute>
            <InstructorDashboardPage />
          </InstructorRoute>
        } />
        
        {/* Admin routes */}
        <Route path="admin/*" element={
          <AdminRoute>
            <AdminPage />
          </AdminRoute>
        } />
      </Route>

      {/* Direct protected routes (without dashboard layout) */}
      <Route 
        path="/courses" 
        element={
          <ProtectedRoute>
            <CoursesPage />
          </ProtectedRoute>
        }
      />
      
      <Route 
        path="/my-courses" 
        element={
          <ProtectedRoute>
            <MyCoursesPage />
          </ProtectedRoute>
        }
      />

      {/* Error pages */}
      <Route path="/unauthorized" element={<UnauthorizedPage />} />
      <Route path="/404" element={<NotFoundPage />} />
      
      {/* Catch all - redirect to 404 */}
      <Route path="*" element={<Navigate to="/404" replace />} />
    </Routes>
  )
}

export default AppRouter