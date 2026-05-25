import api from './client'

export const registerCustomer = (data) => api.post('/customers/register', data)
export const loginCustomer = (email, senha) => api.post('/customers/login', { email, senha })
export const getMyProfile = (token) => api.get('/customers/me', {
  headers: { Authorization: `Bearer ${token}` }
})
export const updateMyProfile = (token, data) => api.put('/customers/me', data, {
  headers: { Authorization: `Bearer ${token}` }
})
