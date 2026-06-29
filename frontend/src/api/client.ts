import axios from 'axios'

const api = axios.create({
  baseURL: '/api/v1',
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('lh_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  const clientId = localStorage.getItem('lh_client_id')
  if (clientId) {
    config.params = { ...config.params, client_id: clientId }
  }
  return config
})

export default api
