import axios from 'axios'

const client = axios.create({
    baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
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

export function getErrorMessage(error, fallback = '오류가 발생했습니다.') {
    if (!error) return ''
    const data = error.response?.data
    if (!data) return error.message || fallback
    if (typeof data === 'string') return data
    if (data.detail && typeof data.detail === 'string') return data.detail
    if (data.message && typeof data.message === 'string') return data.message
    if (data.non_field_errors) {
        return Array.isArray(data.non_field_errors) ? data.non_field_errors[0] : String(data.non_field_errors)
    }
    if (typeof data === 'object') {
        for (const key of Object.keys(data)) {
            const val = data[key]
            if (Array.isArray(val) && val.length > 0) {
                return typeof val[0] === 'string' ? val[0] : JSON.stringify(val[0])
            }
            if (typeof val === 'string' && val.trim().length > 0) {
                return val
            }
        }
    }
    return fallback
}

export default client