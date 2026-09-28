import axios from 'axios'

const client = axios.create({
    baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api',
})

client.interceptors.request.use((config) => {
    const accessToken = localStorage.getItem('access_token')
    if (accessToken) {
        config.headers.Authorization = `Bearer ${accessToken}`
    }
    return config
})

client.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401 && window.location.pathname !== '/login') {
            localStorage.removeItem('access_token')
            localStorage.removeItem('refresh_token')
            localStorage.removeItem('auth_user')
            window.location.assign('/login')
        }
        return Promise.reject(error)
    },
)

export default client