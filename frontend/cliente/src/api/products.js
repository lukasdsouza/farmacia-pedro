import api from './client'

export const getProducts = (params) => api.get('/products', { params })
export const getProduct = (sku) => api.get(`/products/${sku}`)
export const getCategories = () => api.get('/products/categories')
