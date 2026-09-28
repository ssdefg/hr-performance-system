import { createRouter, createWebHistory } from 'vue-router'
import AppLayout from '../components/AppLayout.vue'
import LoginView from '../views/auth/LoginView.vue'
import { useAuthStore } from '../stores/auth'

const rolePaths = {
    ADMIN: '/admin',
    MANAGER: '/manager',
    EMPLOYEE: '/employee',
}

const routes = [
    {
        path: '/',
        redirect: () => useAuthStore().homeRoute(),
    },
    {
        path: '/login',
        name: 'login',
        component: LoginView,
        meta: { guestOnly: true },
    },
    ...Object.entries(rolePaths).map(([role, path]) => ({
        path,
        component: AppLayout,
        meta: { requiresAuth: true, role },
        children: [
            ...(role === 'ADMIN' ? [
                { path: 'teams', name: 'admin-teams', component: () => import('../views/admin/TeamManagementView.vue') },
                { path: 'users', name: 'admin-users', component: () => import('../views/admin/UserManagementView.vue') },
                { path: 'criteria', name: 'admin-criteria', component: () => import('../views/admin/CriteriaManagementView.vue') },
                { path: 'scores', name: 'admin-scores', component: () => import('../views/admin/ScoreManagementView.vue') },
            ] : []),
            ...(role === 'MANAGER' ? [
                { path: 'evaluations/:employeeId', name: 'manager-evaluation-form', component: () => import('../views/manager/EvaluationFormView.vue') },
            ] : []),
            {
                path: '',
                name: `${role.toLowerCase()}-dashboard`,
                component: role === 'MANAGER'
                    ? () => import('../views/manager/ManagerDashboardView.vue')
                    : role === 'EMPLOYEE'
                        ? () => import('../views/employee/MyEvaluationView.vue')
                        : () => import('../views/DashboardView.vue'),
            },
        ],
    })),
    {
        path: '/:pathMatch(.*)*',
        redirect: '/',
    },
]

const router = createRouter({
    history: createWebHistory(),
    routes,
})

router.beforeEach(async (to) => {
    const auth = useAuthStore()
    await auth.initialize()

    if (to.meta.guestOnly && auth.isAuthenticated) {
        return auth.homeRoute()
    }

    const requiresAuth = to.matched.some((record) => record.meta.requiresAuth)
    const requiredRole = to.matched.find((record) => record.meta.role)?.meta.role

    if (requiresAuth && !auth.isAuthenticated) {
        return { name: 'login', query: { redirect: to.fullPath } }
    }

    if (requiredRole && auth.user?.role !== requiredRole) {
        return auth.homeRoute()
    }

    return true
})

export default router