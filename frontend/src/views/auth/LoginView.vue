<script setup>
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'

const employeeId = ref('')
const password = ref('')
const errorMessage = ref('')
const submitting = ref(false)
const auth = useAuthStore()
const route = useRoute()
const router = useRouter()

async function submitLogin() {
    errorMessage.value = ''
    if (!employeeId.value.trim() || !password.value) {
        errorMessage.value = '사번과 비밀번호를 모두 입력해 주세요.'
        return
    }

    submitting.value = true
    try {
        await auth.login(employeeId.value.trim(), password.value)
        const requestedPath = typeof route.query.redirect === 'string' ? route.query.redirect : ''
        await router.replace(requestedPath || auth.homeRoute())
    } catch (error) {
        errorMessage.value = error.response?.status === 401
            ? '사번 또는 비밀번호를 확인해 주세요.'
            : '로그인할 수 없습니다. 서버 연결을 확인해 주세요.'
    } finally {
        submitting.value = false
    }
}
</script>

<template>
    <main class="login-page">
        <section class="login-panel" aria-labelledby="login-title">
            <div class="login-brand">
                <span class="brand-mark">H</span>
                <span class="fw-bold">People Review</span>
            </div>
            <p class="eyebrow mt-4">2026 · PERFORMANCE CYCLE</p>
            <h1 id="login-title" class="page-title">성과 평가 시스템</h1>
            <p class="text-secondary mb-4">사번으로 로그인해 주세요.</p>

            <div v-if="errorMessage" class="alert alert-danger" role="alert">
                {{ errorMessage }}
            </div>

            <form @submit.prevent="submitLogin">
                <div class="mb-3">
                    <label class="form-label" for="employee-id">사번</label>
                    <input
                        id="employee-id"
                        v-model="employeeId"
                        class="form-control"
                        name="employee_id"
                        autocomplete="username"
                        placeholder="사번을 입력하세요"
                        required
                    />
                </div>
                <div class="mb-4">
                    <label class="form-label" for="password">비밀번호</label>
                    <input
                        id="password"
                        v-model="password"
                        class="form-control"
                        type="password"
                        name="password"
                        autocomplete="current-password"
                        placeholder="비밀번호를 입력하세요"
                        required
                    />
                </div>
                <button class="btn btn-primary w-100" type="submit" :disabled="submitting">
                    {{ submitting ? '로그인 중...' : '로그인' }}
                </button>
            </form>
        </section>
    </main>
</template>