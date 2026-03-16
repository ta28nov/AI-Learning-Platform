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
import LandingPage from '@pages/landing/LandingPage'
import DashboardPage from '@pages/dashboard/DashboardPage'
import ProfilePage from '@pages/profile/ProfilePage'
import ProgressPage from '@pages/progress/ProgressPage'

// Course pages
import CoursesPage from '@pages/courses/CoursesPage'
import CourseDetailPage from '@pages/courses/CourseDetailPage'

// Enrollment pages
import MyCoursesPage from '@pages/enrollment/MyCoursesPage'
import StudentEnrollmentPage from '@pages/enrollment/StudentEnrollmentPage'
import InstructorDashboardPage from '@pages/enrollment/InstructorDashboardPage'

// Assessment pages
import AssessmentSetupPage from '@pages/assessment/AssessmentSetupPage'
import AssessmentQuizPage from '@pages/assessment/AssessmentQuizPage'
import AssessmentResultsPage from '@pages/assessment/AssessmentResultsPage'

// Learning pages
import ModuleListPage from '@pages/learning/ModuleListPage'
import ModuleDetailPage from '@pages/learning/ModuleDetailPage'
import LessonPage from '@pages/learning/LessonPage'

// Quiz pages
import QuizPage from '@pages/quiz/QuizPage'
import QuizDetailPage from '@pages/quiz/QuizDetailPage'
import QuizAttemptPage from '@pages/quiz/QuizAttemptPage'
import QuizResultsPage from '@pages/quiz/QuizResultsPage'

// Chat pages
import ChatPage from '@pages/chat/ChatPage'

// Personal courses
import PersonalCoursesPage from '@pages/personal-courses/PersonalCoursesPage'

// Classes pages
import ClassListPage from '@pages/classes/ClassListPage'
import ClassCreatePage from '@pages/classes/ClassCreatePage'
import ClassDetailPage from '@pages/classes/ClassDetailPage'

// Search & Recommendations
import SearchResultsPage from '@pages/search/SearchResultsPage'
import RecommendationsPage from '@pages/recommendations/RecommendationsPage'

// Admin pages
import AdminPage from '@pages/admin/AdminPage'

// Error pages
import NotFoundPage from '@pages/error/NotFoundPage'
import UnauthorizedPage from '@pages/error/UnauthorizedPage'

/**
 * Component AppRouter - Quan ly routing cho toan bo ung dung
 * Tat ca protected routes nam trong /dashboard/* voi DashboardLayout
 */
const AppRouter = () => {
  return (
    <Routes>
      {/* Public routes */}
      <Route path="/" element={<LandingPage />} />
      
      {/* Auth routes - khong can dang nhap */}
      <Route path="/auth/login" element={<LoginPage />} />
      <Route path="/auth/register" element={<RegisterPage />} />
      <Route path="/auth/forgot-password" element={<ForgotPasswordPage />} />
      <Route path="/auth/reset-password" element={<ResetPasswordPage />} />
      <Route path="/auth/verify-email" element={<VerifyEmailPage />} />

      {/* Protected routes - can dang nhap, dung DashboardLayout */}
      <Route 
        path="/dashboard" 
        element={
          <ProtectedRoute>
            <DashboardLayout />
          </ProtectedRoute>
        }
      >
        {/* Dashboard home - render theo role */}
        <Route index element={<DashboardPage />} />
        
        {/* Profile & Progress */}
        <Route path="profile" element={<ProfilePage />} />
        <Route path="progress" element={<ProgressPage />} />
        
        {/* Courses - tim kiem va chi tiet */}
        <Route path="courses" element={<CoursesPage />} />
        <Route path="courses/:courseId" element={<CourseDetailPage />} />

        {/* Learning - modules va lessons */}
        <Route path="courses/:courseId/modules" element={<ModuleListPage />} />
        <Route path="courses/:courseId/modules/:moduleId" element={<ModuleDetailPage />} />
        <Route path="courses/:courseId/lessons/:lessonId" element={<LessonPage />} />
        
        {/* My Courses (Enrollments) */}
        <Route path="my-courses" element={<MyCoursesPage />} />
        <Route path="enrollment/:enrollmentId" element={<StudentEnrollmentPage />} />

        {/* Assessment - danh gia nang luc AI */}
        <Route path="assessment" element={<AssessmentSetupPage />} />
        <Route path="assessment/:sessionId" element={<AssessmentQuizPage />} />
        <Route path="assessment/:sessionId/results" element={<AssessmentResultsPage />} />
        
        {/* Quiz */}
        <Route path="quiz" element={<QuizPage />} />
        <Route path="quiz/:quizId" element={<QuizDetailPage />} />
        <Route path="quiz/:quizId/attempt" element={<QuizAttemptPage />} />
        <Route path="quiz/:quizId/results" element={<QuizResultsPage />} />
        
        {/* Chat AI */}
        <Route path="chat" element={<ChatPage />} />

        {/* Personal Courses - khoa hoc ca nhan */}
        <Route path="personal-courses" element={<PersonalCoursesPage />} />

        {/* Search */}
        <Route path="search" element={<SearchResultsPage />} />

        {/* Recommendations */}
        <Route path="recommendations" element={<RecommendationsPage />} />
        
        {/* Instructor routes */}
        <Route path="instructor" element={
          <InstructorRoute>
            <InstructorDashboardPage />
          </InstructorRoute>
        } />
        
        {/* Classes (Instructor) */}
        <Route path="classes" element={
          <InstructorRoute><ClassListPage /></InstructorRoute>
        } />
        <Route path="classes/create" element={
          <InstructorRoute><ClassCreatePage /></InstructorRoute>
        } />
        <Route path="classes/:classId" element={
          <InstructorRoute><ClassDetailPage /></InstructorRoute>
        } />
        
        {/* Admin routes */}
        <Route path="admin/*" element={
          <AdminRoute>
            <AdminPage />
          </AdminRoute>
        } />
      </Route>

      {/* Error pages */}
      <Route path="/unauthorized" element={<UnauthorizedPage />} />
      <Route path="/404" element={<NotFoundPage />} />
      
      {/* Catch all */}
      <Route path="*" element={<Navigate to="/404" replace />} />
    </Routes>
  )
}

export default AppRouter