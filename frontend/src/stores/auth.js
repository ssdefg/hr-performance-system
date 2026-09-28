import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import client from '../api/client'

const roleRoutes = {
    ADMIN: '/admin',
    MANAGER: '/manager',
    EMPLOYEE: '/employee',
}

export const useAuthStore = defineStore('auth', () => {
    const token = ref(localStorage.getItem('access_token') || '')
    const refreshToken = ref(localStorage.getItem('refresh_token') || '')
    const user = ref(JSON.parse(localStorage.getItem('auth_user') || 'null'))
    const isAuthenticated = computed(() => Boolean(token.value && user.value))
    const initialized = ref(false)

    function persistSession(access, refresh, profile) {
        token.value = access
        refreshToken.value = refresh
        user.value = profile
        localStorage.setItem('access_token', access)
        localStorage.setItem('refresh_token', refresh)
        localStorage.setItem('auth_user', JSON.stringify(profile))
    }

    function logout() {
        token.value = ''
        refreshToken.value = ''
        user.value = null
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        localStorage.removeItem('auth_user')
    }

    async function login(employeeId, password) {
        const { data } = await client.post('/auth/login/', {
            employee_id: employeeId,
            password,
        })
        persistSession(data.access, data.refresh, data.user)
        return data.user
    }

    async function fetchCurrentUser() {
        if (!token.value) return null
        const { data } = await client.get('/auth/me/')
        user.value = data
        localStorage.setItem('auth_user', JSON.stringify(data))
        return data
    }

    async function initialize() {
        if (initialized.value) return
        try {
            if (token.value) await fetchCurrentUser()
        } catch {
            logout()
        } finally {
            initialized.value = true
        }
    }

    function homeRoute() {
        return roleRoutes[user.value?.role] || '/login'
    }

    return {
        token,
        refreshToken,
        user,
        isAuthenticated,
        initialize,
        login,
        logout,
        fetchCurrentUser,
        homeRoute,
    }
})