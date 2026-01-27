import axios from 'axios'

/**
 * Cau hinh axios instance cho viec goi API
 */
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

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
 * Response interceptor - Xu ly loi va refresh token
 */
api.interceptors.response.use(
  (response) => {
    return response
  },
  async (error) => {
    const originalRequest = error.config
    
    // Neu loi 401 va chua thu refresh token
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      
      try {
        // Lay refresh token
        const refreshToken = localStorage.getItem('refresh_token')
        
        if (refreshToken) {
          // Goi API refresh token
          const response = await axios.post(
            `${api.defaults.baseURL}/auth/refresh`,
            { refresh_token: refreshToken }
          )
          
          const { access_token } = response.data
          
          // Luu token moi
          localStorage.setItem('access_token', access_token)
          
          // Retry request ban dau voi token moi
          originalRequest.headers.Authorization = `Bearer ${access_token}`
          return api(originalRequest)
        }
      } catch (refreshError) {
        // Neu refresh token het han, xoa token va chuyen ve login
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        window.location.href = '/auth/login'
        return Promise.reject(refreshError)
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

export const handleApiError = (error) => {
  if (error.response) {
    // Server tra ve response voi status code loi
    const message = error.response.data?.message || 
                   error.response.data?.detail || 
                   'Co loi xay ra tu server'
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