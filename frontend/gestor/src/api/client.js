import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.response.use(
  r => r,
  err => {
    if (err.response?.status === 401) {
      localStorage.removeItem('farmacia_user')
      localStorage.removeItem('farmacia_token')
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

export default api
