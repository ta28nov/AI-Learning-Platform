import { create } from 'zustand'
import courseService from '@services/courseService'

/**
 * Zustand store cho quan ly khoa hoc
 */
export const useCourseStore = create((set, get) => ({
  // State
  courses: [],
  currentCourse: null,
  currentModule: null,
  currentLesson: null,
  isLoading: false,
  error: null,
  
  // Pagination state
  pagination: {
    page: 1,
    limit: 12,
    total: 0,
    totalPages: 0
  },
  
  // Filter state
  filters: {
    search: '',
    category: '',
    level: '',
    sortBy: 'newest'
  },

  /**
   * Lay danh sach khoa hoc cong khai
   * @param {Object} params - Parameters tim kiem va filter
   */
  getCourses: async (params = {}) => {
    set({ isLoading: true, error: null })
    
    try {
      const response = await courseService.getPublicCourses({
        ...get().filters,
        ...get().pagination,
        ...params
      })
      
      set({
        courses: response.courses || response.data || [],
        pagination: {
          page: response.page || 1,
          limit: response.limit || 12,
          total: response.total || 0,
          totalPages: response.totalPages || Math.ceil((response.total || 0) / (response.limit || 12))
        },
        isLoading: false,
        error: null
      })
      
      return response
    } catch (error) {
      set({
        courses: [],
        isLoading: false,
        error: error.message
      })
      throw error
    }
  },

  /**
   * Tim kiem khoa hoc
   * @param {string} searchTerm - Tu khoa tim kiem
   */
  searchCourses: async (searchTerm = '') => {
    set({ 
      isLoading: true, 
      error: null,
      filters: { ...get().filters, search: searchTerm }
    })
    
    try {
      const response = await courseService.searchCourses({
        search: searchTerm,
        ...get().filters
      })
      
      set({
        courses: response.courses || response.data || [],
        isLoading: false,
        error: null
      })
      
      return response
    } catch (error) {
      set({
        courses: [],
        isLoading: false,
        error: error.message
      })
      throw error
    }
  },

  /**
   * Lay thong tin chi tiet khoa hoc
   * @param {string} courseId - ID khoa hoc
   */
  getCourseDetail: async (courseId) => {
    set({ isLoading: true, error: null })
    
    try {
      const course = await courseService.getCourseDetail(courseId)
      
      set({
        currentCourse: course,
        isLoading: false,
        error: null
      })
      
      return course
    } catch (error) {
      set({
        currentCourse: null,
        isLoading: false,
        error: error.message
      })
      throw error
    }
  },

  /**
   * Lay thong tin module
   * @param {string} courseId - ID khoa hoc
   * @param {string} moduleId - ID module
   */
  getModule: async (courseId, moduleId) => {
    set({ isLoading: true, error: null })
    
    try {
      const module = await courseService.getModule(courseId, moduleId)
      
      set({
        currentModule: module,
        isLoading: false,
        error: null
      })
      
      return module
    } catch (error) {
      set({
        currentModule: null,
        isLoading: false,
        error: error.message
      })
      throw error
    }
  },

  /**
   * Lay noi dung bai hoc
   * @param {string} courseId - ID khoa hoc
   * @param {string} lessonId - ID bai hoc
   */
  getLesson: async (courseId, lessonId) => {
    set({ isLoading: true, error: null })
    
    try {
      const lesson = await courseService.getLesson(courseId, lessonId)
      
      set({
        currentLesson: lesson,
        isLoading: false,
        error: null
      })
      
      return lesson
    } catch (error) {
      set({
        currentLesson: null,
        isLoading: false,
        error: error.message
      })
      throw error
    }
  },

  /**
   * Danh dau bai hoc da hoan thanh
   * @param {string} courseId - ID khoa hoc
   * @param {string} lessonId - ID bai hoc
   */
  markLessonComplete: async (courseId, lessonId) => {
    try {
      await courseService.markLessonComplete(courseId, lessonId)
      
      // Cap nhat trang thai local
      const currentLesson = get().currentLesson
      if (currentLesson && currentLesson.id === lessonId) {
        set({
          currentLesson: {
            ...currentLesson,
            completed: true,
            completedAt: new Date().toISOString()
          }
        })
      }
      
      return true
    } catch (error) {
      set({ error: error.message })
      throw error
    }
  },

  /**
   * Cap nhat filters
   * @param {Object} newFilters - Filters moi
   */
  setFilters: (newFilters) => {
    set({
      filters: { ...get().filters, ...newFilters },
      pagination: { ...get().pagination, page: 1 } // Reset ve trang 1
    })
  },

  /**
   * Cap nhat pagination
   * @param {Object} newPagination - Pagination moi
   */
  setPagination: (newPagination) => {
    set({
      pagination: { ...get().pagination, ...newPagination }
    })
  },

  /**
   * Xoa state hien tai
   */
  clearCurrent: () => {
    set({
      currentCourse: null,
      currentModule: null,
      currentLesson: null
    })
  },

  /**
   * Xoa loi
   */
  clearError: () => {
    set({ error: null })
  },

  /**
   * Reset store
   */
  reset: () => {
    set({
      courses: [],
      currentCourse: null,
      currentModule: null,
      currentLesson: null,
      isLoading: false,
      error: null,
      pagination: {
        page: 1,
        limit: 12,
        total: 0,
        totalPages: 0
      },
      filters: {
        search: '',
        category: '',
        level: '',
        sortBy: 'newest'
      }
    })
  }
}))