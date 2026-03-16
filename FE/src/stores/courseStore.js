import { create } from 'zustand'
import courseService from '@services/courseService'

/**
 * Zustand store cho quan ly khoa hoc
 * Mapping: courseService (4 endpoints) + UI state
 */
export const useCourseStore = create((set, get) => ({
  // State
  courses: [],
  currentCourse: null,
  isLoading: false,
  error: null,
  
  // Pagination state (MongoDB style: skip/limit)
  pagination: {
    skip: 0,
    limit: 12,
    total: 0
  },
  
  // Filter state
  filters: {
    keyword: '',
    category: '',
    level: '',
    sort_by: 'newest'
  },

  /**
   * Tim kiem khoa hoc
   * API: GET /courses/search
   */
  searchCourses: async (params = {}) => {
    set({ isLoading: true, error: null })
    
    try {
      const mergedParams = {
        ...get().filters,
        ...get().pagination,
        ...params
      }
      const response = await courseService.searchCourses(mergedParams)
      
      set({
        courses: response.courses || [],
        pagination: {
          skip: response.skip || 0,
          limit: response.limit || 12,
          total: response.total || 0
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
   * Lay danh sach khoa hoc cong khai
   * API: GET /courses/public
   */
  getPublicCourses: async (params = {}) => {
    set({ isLoading: true, error: null })
    
    try {
      const response = await courseService.getPublicCourses({
        skip: get().pagination.skip,
        limit: get().pagination.limit,
        ...params
      })
      
      set({
        courses: response.courses || [],
        pagination: {
          skip: response.skip || 0,
          limit: response.limit || 12,
          total: response.total || 0
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
   * Lay chi tiet khoa hoc
   * API: GET /courses/{courseId}
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
   * Cap nhat filters
   */
  setFilters: (newFilters) => {
    set({
      filters: { ...get().filters, ...newFilters },
      pagination: { ...get().pagination, skip: 0 }
    })
  },

  /**
   * Cap nhat pagination (chuyen trang)
   */
  setPage: (skip) => {
    set({
      pagination: { ...get().pagination, skip }
    })
  },

  /**
   * Xoa state hien tai
   */
  clearCurrent: () => {
    set({ currentCourse: null })
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
      isLoading: false,
      error: null,
      pagination: { skip: 0, limit: 12, total: 0 },
      filters: { keyword: '', category: '', level: '', sort_by: 'newest' }
    })
  }
}))

export default useCourseStore