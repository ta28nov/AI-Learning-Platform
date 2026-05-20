import axios from 'axios'

/**
 * Cau hinh axios instance cho viec goi API
 * BaseURL tu .env da bao gom /api/v1
 */
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

/**
 * Timeout cho cac AI endpoints (Gemini API co the mat 20-120 giay)
 * Su dung: api.post('/assessments/generate', data, { timeout: AI_TIMEOUT })
 */
export const AI_TIMEOUT = 120000 // 2 phut

/** POST /assessments/:id/submit chạy sinh + chấm AI trên server — thường > 30s */
export const ASSESSMENT_SUBMIT_TIMEOUT = 180000 // 3 phut

/**
 * Loai bo query params rong/deprecated truoc khi goi API
 */
export const buildQueryParams = (params = {}) => {
  return Object.fromEntries(
    Object.entries(params).filter(([, value]) => value !== undefined && value !== null && value !== '')
  )
}

/**
 * Request interceptor - Them token vao header
 */
api.interceptors.request.use(
  (config) => {
    // Lay token tu localStorage
    const token = localStorage.getItem('access_token')
    
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

/**
 * Response interceptor - Xu ly loi 401 voi refresh token queue
 * 
 * Co che:
 * 1. Khi nhan 401, kiem tra co dang refresh khong
 * 2. Neu dang refresh → dua request vao hang doi (failedQueue)
 * 3. Neu chua refresh → bat dau refresh, sau do retry tat ca queue
 * 4. Neu refresh that bai → force logout + toast thong bao
 */
let isRefreshing = false
let failedQueue = []

const processQueue = (error, token = null) => {
  failedQueue.forEach(({ resolve, reject }) => {
    if (error) {
      reject(error)
    } else {
      resolve(token)
    }
  })
  failedQueue = []
}

api.interceptors.response.use(
  (response) => {
    return response
  },
  async (error) => {
    const originalRequest = error.config
    
    // Chi xu ly 401 va chua thu retry
    if (error.response?.status === 401 && !originalRequest._retry) {
      // Neu dang trong qua trinh refresh → dua vao queue cho
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject })
        }).then((token) => {
          originalRequest.headers.Authorization = `Bearer ${token}`
          return api(originalRequest)
        }).catch((err) => {
          return Promise.reject(err)
        })
      }
      
      originalRequest._retry = true
      isRefreshing = true
      
      try {
        // Lay refresh token tu localStorage
        const refreshToken = localStorage.getItem('refresh_token')
        
        if (!refreshToken) {
          throw new Error('Khong co refresh token')
        }
        
        // Goi API refresh token (dung axios goc, khong dung api instance de tranh loop)
        const response = await axios.post(
          `${api.defaults.baseURL}/auth/refresh`,
          { refresh_token: refreshToken }
        )
        
        const { access_token } = response.data
        
        // Luu token moi vao localStorage
        localStorage.setItem('access_token', access_token)
        
        // Retry tat ca request trong queue
        processQueue(null, access_token)
        
        // Retry request ban dau voi token moi
        originalRequest.headers.Authorization = `Bearer ${access_token}`
        return api(originalRequest)
      } catch (refreshError) {
        // Refresh that bai → force logout
        processQueue(refreshError, null)
        
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        localStorage.removeItem('token_type')
        
        // Dispatch event de UI co the hien thi toast
        window.dispatchEvent(new CustomEvent('auth:session-expired'))
        
        window.location.href = '/auth/login'
        return Promise.reject(refreshError)
      } finally {
        isRefreshing = false
      }
    }
    
    return Promise.reject(error)
  }
)

/**
 * Helper functions de xu ly API response
 */
export const handleApiResponse = (response) => {
  return response.data
}

/**
 * Helper xu ly API error - ho tro ca 422 Pydantic validation array
 */
export const handleApiError = (error) => {
  if (error.response) {
    const detail = error.response.data?.detail
    
    // 422 Pydantic validation error: detail thuong la array of objects
    let message
    if (Array.isArray(detail)) {
      message = detail.map(d => d.msg || d.message || JSON.stringify(d)).join('. ')
    } else if (detail && typeof detail === 'object') {
      message = detail.message || JSON.stringify(detail)
    } else {
      message = detail || error.response.data?.message || 'Co loi xay ra tu server'
    }
    
    throw new Error(message)
  } else if (error.request) {
    // Request duoc gui nhung khong nhan duoc response
    throw new Error('Khong the ket noi den server')
  } else {
    // Loi khac
    throw new Error(error.message || 'Co loi khong xac dinh')
  }
}

export default api