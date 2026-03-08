import axios, { AxiosRequestConfig } from 'axios'

// Axios instance used everywhere — auth headers + 401 redirect handled here.
// baseURL is '' so Orval-generated paths (/api/designs, /api/auth/...) resolve
// through Vite's proxy to the backend without double-prefixing.
const axiosInstance = axios.create({ baseURL: '' })

axiosInstance.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

axiosInstance.interceptors.response.use(
  (r) => r,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('username')
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

// Orval mutator — generated hooks call this instead of raw fetch.
// Returns response.data so callers get the typed payload directly.
export const apiClient = <T>(config: AxiosRequestConfig): Promise<T> => {
  return axiosInstance(config).then((r) => r.data)
}

export default axiosInstance
