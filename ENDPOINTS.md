# Mapping Endpoints từ CHUCNANG.md -> Routers
> Ngày cập nhật: 05/11/2025

---

## Auth Router (`auth_router.py`)
**Section:** 2.1.1-2.1.3  
**Endpoints:** 3 API

| Endpoint | Method | Section | Controller | Schema |
|----------|--------|---------|-----------|--------|
| `/api/v1/auth/register` | POST | 2.1.1 | handle_register | RegisterRequest/Response |
| `/api/v1/auth/login` | POST | 2.1.2 | handle_login | LoginRequest/Response |
| `/api/v1/auth/logout` | POST | 2.1.3 | handle_logout | LogoutResponse |

---

## User Router (`users_router.py`)
**Section:** 2.1.4-2.1.5  
**Endpoints:** 2 API

| Endpoint | Method | Section | Controller | Schema |
|----------|--------|---------|-----------|--------|
| `/api/v1/users/me` | GET | 2.1.4 | handle_get_profile | UserProfileResponse |
| `/api/v1/users/me` | PATCH | 2.1.5 | handle_update_profile | UserProfileUpdateRequest/Response |

---

## Course Router (`courses_router.py`)
**Section:** 2.3.1-2.3.3, 2.3.7  
**Endpoints:** 4 API

| Endpoint | Method | Section | Controller | Schema |
|----------|--------|---------|-----------|--------|
| `/api/v1/courses/search` | GET | 2.3.1 | handle_search_courses | CourseSearchRequest/Response |
| `/api/v1/courses/public` | GET | 2.3.2 | handle_list_public_courses | CourseListResponse |
| `/api/v1/courses/{course_id}` | GET | 2.3.3 | handle_get_course_detail | CourseDetailResponse |
| `/api/v1/courses/{course_id}/enrollment-status` | GET | 2.3.7 | handle_check_course_enrollment_status | CourseEnrollmentStatusResponse |

---

## Learning Router (`learning_router.py`)
**Section:** 2.4.1-2.4.2  
**Endpoints:** 6 API

| Endpoint | Method | Section | Controller | Schema |
|----------|--------|---------|-----------|--------|
| `/api/v1/courses/{course_id}/modules/{module_id}` | GET | 2.4.1 | handle_get_module_detail | ModuleDetailResponse |
| `/api/v1/courses/{course_id}/lessons/{lesson_id}` | GET | 2.4.2 | handle_get_lesson_content | LessonContentResponse |
| `/api/v1/courses/{course_id}/modules` | GET | Notes | handle_get_course_modules | CourseModulesResponse |
| `/api/v1/courses/{course_id}/modules/{module_id}/outcomes` | GET | Notes | handle_get_module_outcomes | ModuleOutcomesResponse |
| `/api/v1/courses/{course_id}/modules/{module_id}/resources` | GET | Notes | handle_get_module_resources | ModuleResourcesResponse |
| `/api/v1/courses/{course_id}/modules/{module_id}/assessments/generate` | POST | Notes | handle_generate_module_assessment | ModuleAssessmentGenerateRequest/Response |

---

## Personal Course Router (`personal_courses_router.py`)
**Section:** 2.5.1-2.5.5  
**Endpoints:** 5 API

| Endpoint | Method | Section | Controller | Schema |
|----------|--------|---------|-----------|--------|
| `/api/v1/courses/from-prompt` | POST | 2.5.1 | handle_create_course_from_prompt | CourseFromPromptRequest/Response |
| `/api/v1/courses/personal` | POST | 2.5.2 | handle_create_personal_course | PersonalCourseCreateRequest/Response |
| `/api/v1/courses/my-personal` | GET | 2.5.3 | handle_list_my_personal_courses | PersonalCourseListResponse |
| `/api/v1/courses/personal/{course_id}` | PUT | 2.5.4 | handle_update_personal_course | PersonalCourseUpdateRequest/Response |
| `/api/v1/courses/personal/{course_id}` | DELETE | 2.5.5 | handle_delete_personal_course | PersonalCourseDeleteResponse |

---

## Enrollment Router (`enrollments_router.py`)
**Section:** 2.3.4-2.3.6, 2.3.8  
**Endpoints:** 4 API

| Endpoint | Method | Section | Controller | Schema |
|----------|--------|---------|-----------|--------|
| `/api/v1/enrollments` | POST | 2.3.4 | handle_enroll_course | EnrollmentCreateRequest/Response |
| `/api/v1/enrollments/my-courses` | GET | 2.3.5 | handle_list_my_enrollments | EnrollmentListResponse |
| `/api/v1/enrollments/{enrollment_id}` | GET | 2.3.6 | handle_get_enrollment_detail | EnrollmentDetailResponse |
| `/api/v1/enrollments/{enrollment_id}` | DELETE | 2.3.8 | handle_unenroll_course | EnrollmentCancelResponse |

---

## Assessment Router (`assessments_router.py`)
**Section:** 2.2.1-2.2.4  
**Endpoints:** 3 API

| Endpoint | Method | Section | Controller | Schema |
|----------|--------|---------|-----------|--------|
| `/api/v1/assessments/generate` | POST | 2.2.1 | handle_generate_assessment | AssessmentGenerateRequest/Response |
| `/api/v1/assessments/{session_id}/submit` | POST | 2.2.2 | handle_submit_assessment | AssessmentSubmitRequest/Response |
| `/api/v1/assessments/{session_id}/results` | GET | 2.2.3 | handle_get_assessment_results | AssessmentResultsResponse |

---

## Quiz Router (`quiz_router.py`)
**Section:** 2.4.3-2.4.7 (Student) + 3.3 (Instructor)  
**Endpoints:** 10 API

| Endpoint | Method | Section | Controller | Schema |
|----------|--------|---------|-----------|--------|
| `/api/v1/quizzes/{quiz_id}` | GET | 2.4.3 | handle_get_quiz_detail | QuizDetailResponse |
| `/api/v1/quizzes/{quiz_id}/attempt` | POST | 2.4.4 | handle_attempt_quiz | QuizAttemptRequest/Response |
| `/api/v1/quizzes/{quiz_id}/results` | GET | 2.4.5 | handle_get_quiz_results | QuizResultsResponse |
| `/api/v1/quizzes/{quiz_id}/retake` | POST | 2.4.6 | handle_retake_quiz | QuizRetakeResponse |
| `/api/v1/ai/generate-practice` | POST | 2.4.7 | handle_generate_practice_exercises | PracticeExercisesRequest/Response |
| `/api/v1/lessons/{lesson_id}/quizzes` | POST | 3.3.1 | handle_create_quiz | QuizCreateRequest/Response |
| `/api/v1/quizzes?role=instructor` | GET | 3.3.2 | handle_list_quizzes_with_filters | QuizListResponse |
| `/api/v1/quizzes/{quiz_id}` | PUT | 3.3.3 | handle_update_quiz | QuizUpdateRequest/Response |
| `/api/v1/quizzes/{quiz_id}` | DELETE | 3.3.4 | handle_delete_quiz | QuizDeleteResponse |
| `/api/v1/quizzes/{quiz_id}/class-results` | GET | 3.3.5 | handle_get_class_quiz_results | QuizClassResultsResponse |

---

## Progress Router (`progress_router.py`)
**Section:** 2.4.9  
**Endpoints:** 1 API

| Endpoint | Method | Section | Controller | Schema |
|----------|--------|---------|-----------|--------|
| `/api/v1/progress/course/{course_id}` | GET | 2.4.9 | handle_get_course_progress | ProgressCourseResponse |

**Note:** Section 2.4.8 (Hoàn thành bài học tự động) không cần endpoint riêng - được xử lý tự động khi pass quiz.

---

## Chat Router (`chat_router.py`)
**Section:** 2.6.1-2.6.5  
**Endpoints:** 5 API

| Endpoint | Method | Section | Controller | Schema |
|----------|--------|---------|-----------|--------|
| `/api/v1/chat/course/{course_id}` | POST | 2.6.1 | handle_send_chat_message | ChatMessageRequest/Response |
| `/api/v1/chat/history` | GET | 2.6.2 | handle_get_chat_history | ChatHistoryListResponse |
| `/api/v1/chat/conversations/{conversation_id}` | GET | 2.6.3 | handle_get_conversation_detail | ConversationDetailResponse |
| `/api/v1/chat/conversations` | DELETE | 2.6.4 | handle_delete_all_conversations | ChatDeleteAllResponse |
| `/api/v1/chat/history/{conversation_id}` | DELETE | 2.6.5 | handle_delete_conversation | ChatDeleteResponse |

---

## Classes Router (`classes_router.py`)
**Section:** 3.1-3.2  
**Endpoints:** 10 API

| Endpoint | Method | Section | Controller | Schema |
|----------|--------|---------|-----------|--------|
| `/api/v1/classes` | POST | 3.1.1 | handle_create_class | ClassCreateRequest/Response |
| `/api/v1/classes/my-classes` | GET | 3.1.2 | handle_list_my_classes | ClassListResponse |
| `/api/v1/classes/{class_id}` | GET | 3.1.3 | handle_get_class_detail | ClassDetailResponse |
| `/api/v1/classes/{class_id}` | PUT | 3.1.4 | handle_update_class | ClassUpdateRequest/Response |
| `/api/v1/classes/{class_id}` | DELETE | 3.1.5 | handle_delete_class | ClassDeleteResponse |
| `/api/v1/classes/join` | POST | 3.2.1 | handle_join_class_with_code | ClassJoinRequest/Response |
| `/api/v1/classes/{class_id}/students` | GET | 3.2.2 | handle_get_class_students | ClassStudentListResponse |
| `/api/v1/classes/{class_id}/students/{student_id}` | GET | 3.2.3 | handle_get_student_detail | ClassStudentDetailResponse |
| `/api/v1/classes/{class_id}/students/{student_id}` | DELETE | 3.2.4 | handle_remove_student | ClassStudentRemoveResponse |
| `/api/v1/classes/{class_id}/progress` | GET | 3.2.5 | handle_get_class_progress | ClassProgressResponse |

**Note:** Mã mời được tự động tạo khi tạo lớp học (3.1.1), không cần endpoint riêng để generate invite code.

---

## Recommendation Router (`recommendation_router.py`)
**Section:** 2.2.4, 2.7.4  
**Endpoints:** 2 API

| Endpoint | Method | Section | Controller | Schema |
|----------|--------|---------|-----------|--------|
| `/api/v1/recommendations/from-assessment` | GET | 2.2.4 | handle_get_assessment_recommendations | AssessmentRecommendationResponse |
| `/api/v1/recommendations` | GET | 2.7.4 | handle_get_recommendations | RecommendationResponse |

---

## Search Router (`search_router.py`)
**Section:** 5.1.1  
**Endpoints:** 1 API

| Endpoint | Method | Section | Controller | Schema |
|----------|--------|---------|-----------|--------|
| `/api/v1/search` | GET | 5.1.1 | handle_global_search | SearchResponse |

**Note:** Advanced filter được tích hợp vào endpoint search chính thông qua query parameters.

---

## Analytics Router (`analytics_router.py`)
**Section:** 2.7.2-2.7.3, 3.4.2-3.4.4  
**Endpoints:** 5 API (Admin analytics đã chuyển sang admin_router)

| Endpoint | Method | Section | Controller | Schema |
|----------|--------|---------|-----------|--------|
| `/api/v1/analytics/learning-stats` | GET | 2.7.2 | handle_get_learning_stats | LearningStatsResponse |
| `/api/v1/analytics/progress-chart` | GET | 2.7.3 | handle_get_progress_chart | ProgressChartResponse |
| `/api/v1/analytics/instructor/classes` | GET | 3.4.2 | handle_get_instructor_class_stats | InstructorClassStatsResponse |
| `/api/v1/analytics/instructor/progress-chart` | GET | 3.4.3 | handle_get_instructor_progress_chart | InstructorProgressChartResponse |
| `/api/v1/analytics/instructor/quiz-performance` | GET | 3.4.4 | handle_get_instructor_quiz_performance | InstructorQuizPerformanceResponse |

---

## Dashboard Router (`dashboard_router.py`)
**Section:** 2.7.1, 3.4.1, 4.4.1  
**Endpoints:** 3 API

| Endpoint | Method | Section | Controller | Schema |
|----------|--------|---------|-----------|--------|
| `/api/v1/dashboard/student` | GET | 2.7.1 | handle_get_student_dashboard | StudentDashboardResponse |
| `/api/v1/dashboard/instructor` | GET | 3.4.1 | handle_get_instructor_dashboard | InstructorDashboardResponse |
| `/api/v1/admin/dashboard` | GET | 4.4.1 | handle_get_admin_dashboard | AdminSystemDashboardResponse |

---

## Admin Router (`admin_router.py`)
**Section:** 4.1-4.4  
**Endpoints:** 17 API

| Endpoint | Method | Section | Controller | Schema |
|----------|--------|---------|-----------|--------|
| `/api/v1/admin/users` | GET | 4.1.1 | handle_list_users_admin | AdminUserListResponse |
| `/api/v1/admin/users/{user_id}` | GET | 4.1.2 | handle_get_user_detail_admin | AdminUserDetailResponse |
| `/api/v1/admin/users` | POST | 4.1.3 | handle_create_user_admin | AdminCreateUserRequest/Response |
| `/api/v1/admin/users/{user_id}` | PUT | 4.1.4 | handle_update_user_admin | AdminUpdateUserRequest/Response |
| `/api/v1/admin/users/{user_id}` | DELETE | 4.1.5 | handle_delete_user_admin | AdminDeleteUserResponse |
| `/api/v1/admin/users/{user_id}/role` | PUT | 4.1.6 | handle_change_user_role_admin | AdminChangeUserRoleRequest/Response |
| `/api/v1/admin/users/{user_id}/reset-password` | POST | 4.1.7 | handle_reset_user_password_admin | AdminResetPasswordRequest/Response |
| `/api/v1/admin/courses` | GET | 4.2.1 | handle_list_courses_admin | AdminCourseListResponse |
| `/api/v1/admin/courses/{course_id}` | GET | 4.2.2 | handle_get_course_detail_admin | AdminCourseDetailResponse |
| `/api/v1/admin/courses` | POST | 4.2.3 | handle_create_course_admin | AdminCourseCreateRequest/Response |
| `/api/v1/admin/courses/{course_id}` | PUT | 4.2.4 | handle_update_course_admin | AdminCourseUpdateRequest/Response |
| `/api/v1/admin/courses/{course_id}` | DELETE | 4.2.5 | handle_delete_course_admin | AdminDeleteCourseResponse |
| `/api/v1/admin/classes` | GET | 4.3.1 | handle_list_classes_admin | AdminClassListResponse |
| `/api/v1/admin/classes/{class_id}` | GET | 4.3.2 | handle_get_class_detail_admin | AdminClassDetailResponse |
| `/api/v1/admin/analytics/users-growth` | GET | 4.4.2 | handle_get_users_growth_analytics | AdminUsersGrowthResponse |
| `/api/v1/admin/analytics/courses` | GET | 4.4.3 | handle_get_course_analytics | AdminCourseAnalyticsResponse |
| `/api/v1/admin/analytics/system-health` | GET | 4.4.4 | handle_get_system_health | AdminSystemHealthResponse |

**Note:** Admin dashboard endpoints đã được chuyển sang Dashboard Router.

---

## Summary

**Tổng cộng: 16 Routers, 84 API Endpoints**

| Router | Endpoints | Section |
|--------|-----------|---------|
| auth_router | 3 | 2.1.1-2.1.3 |
| users_router | 2 | 2.1.4-2.1.5 |
| courses_router | 4 | 2.3.1-2.3.3, 2.3.7 |
| learning_router | 6 | 2.4.1-2.4.2 |
| personal_courses_router | 5 | 2.5.1-2.5.5 |
| enrollments_router | 4 | 2.3.4-2.3.6, 2.3.8 |
| assessments_router | 3 | 2.2.1-2.2.3 |
| quiz_router | 10 | 2.4.3-2.4.7, 3.3 |
| progress_router | 1 | 2.4.9 |
| chat_router | 5 | 2.6.1-2.6.5 |
| classes_router | 10 | 3.1-3.2 |
| recommendation_router | 2 | 2.2.4, 2.7.4 |
| search_router | 1 | 5.1.1 |
| analytics_router | 5 | 2.7.2-2.7.3, 3.4.2-3.4.4 |
| dashboard_router | 3 | 2.7.1, 3.4.1, 4.4.1 |
| admin_router | 17 | 4.1-4.4 |

---

**Ngày cập nhật:** 07/12/2025  

