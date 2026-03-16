import api, { handleApiResponse, handleApiError } from './api'

/**
 * Service xu ly hoc tap - modules va lessons
 * Endpoints: GET modules list, GET module detail, GET lesson content,
 *            GET outcomes, GET resources, POST generate assessment
 */
export const learningService = {
  /**
   * Lay danh sach modules trong khoa hoc
   * @param {string} courseId - UUID khoa hoc
   * @returns {Promise} CourseModulesResponse
   */
  async getCourseModules(courseId) {
    try {
      const response = await api.get(`/courses/${courseId}/modules`)
      return handleApiResponse(response)
    } catch (error) {
      handleApiError(error)
    }
  },

  /**
   * Lay chi tiet module (lessons, outcomes, resources)
   * @param {string} courseId - UUID khoa hoc
   * @param {string} moduleId - UUID module
   * @returns {Promise} ModuleDetailResponse
   */
  async getModuleDetail(courseId, moduleId) {
    try {
      const response = await api.get(`/courses/${courseId}/modules/${moduleId}`)
      return handleApiResponse(response)
    } catch (error) {
      handleApiError(error)
    }
  },

  /**
   * Lay noi dung bai hoc (text, video, navigation, quiz info)
   * @param {string} courseId - UUID khoa hoc
   * @param {string} lessonId - UUID bai hoc
   * @returns {Promise} LessonContentResponse
   */
  async getLessonContent(courseId, lessonId) {
    try {
      const response = await api.get(`/courses/${courseId}/lessons/${lessonId}`)
      return handleApiResponse(response)
    } catch (error) {
      handleApiError(error)
    }
  },

  /**
   * Lay learning outcomes cua module
   * @param {string} courseId - UUID khoa hoc
   * @param {string} moduleId - UUID module
   * @returns {Promise} ModuleOutcomesResponse
   */
  async getModuleOutcomes(courseId, moduleId) {
    try {
      const response = await api.get(`/courses/${courseId}/modules/${moduleId}/outcomes`)
      return handleApiResponse(response)
    } catch (error) {
      handleApiError(error)
    }
  },

  /**
   * Lay tai nguyen hoc tap cua module
   * @param {string} courseId - UUID khoa hoc
   * @param {string} moduleId - UUID module
   * @returns {Promise} ModuleResourcesResponse
   */
  async getModuleResources(courseId, moduleId) {
    try {
      const response = await api.get(`/courses/${courseId}/modules/${moduleId}/resources`)
      return handleApiResponse(response)
    } catch (error) {
      handleApiError(error)
    }
  },

  /**
   * Sinh quiz danh gia tu dong cho module bang AI
   * @param {string} courseId - UUID khoa hoc
   * @param {string} moduleId - UUID module
   * @param {Object} data - { assessment_type, question_count, difficulty_preference, focus_topics[], time_limit_minutes }
   * @returns {Promise} ModuleAssessmentGenerateResponse
   */
  async generateModuleAssessment(courseId, moduleId, data) {
    try {
      const response = await api.post(
        `/courses/${courseId}/modules/${moduleId}/assessments/generate`,
        data
      )
      return handleApiResponse(response)
    } catch (error) {
      handleApiError(error)
    }
  }
}

export default learningService
