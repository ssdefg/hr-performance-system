<script setup>
import { IconChartBar, IconClipboardCheck, IconLogout, IconScale, IconUsers, IconUsersGroup, IconTrophy } from '@tabler/icons-vue'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()

function logout() {
  auth.logout()
  window.location.assign('/login')
}
</script>

<template>
  <div class="app-shell">
    <aside class="navbar navbar-vertical navbar-expand-lg app-sidebar">
      <div class="container-fluid">
        <h1 class="navbar-brand navbar-brand-autodark">
          <RouterLink to="/" class="brand-lockup">
            <span class="brand-mark">H</span>
            <span>People Review</span>
          </RouterLink>
        </h1>
        <div class="navbar-nav pt-lg-3">
          <RouterLink :to="auth.homeRoute()" class="nav-link" active-class="active">
            <span class="nav-link-icon"><IconChartBar :size="20" /></span>
            <span class="nav-link-title">대시보드</span>
          </RouterLink>
          <RouterLink v-if="auth.user?.role === 'ADMIN'" to="/admin/teams" class="nav-link" active-class="active">
            <span class="nav-link-icon"><IconUsersGroup :size="20" /></span>
            <span class="nav-link-title">팀 관리</span>
          </RouterLink>
          <RouterLink v-if="auth.user?.role === 'ADMIN'" to="/admin/users" class="nav-link" active-class="active">
            <span class="nav-link-icon"><IconUsers :size="20" /></span>
            <span class="nav-link-title">사원 관리</span>
          </RouterLink>
          <RouterLink v-if="auth.user?.role === 'ADMIN'" to="/admin/criteria" class="nav-link" active-class="active">
            <span class="nav-link-icon"><IconScale :size="20" /></span>
            <span class="nav-link-title">평가 항목</span>
          </RouterLink>
          <RouterLink v-if="auth.user?.role === 'ADMIN'" to="/admin/scores" class="nav-link" active-class="active">
            <span class="nav-link-icon"><IconTrophy :size="20" /></span>
            <span class="nav-link-title">점수 및 보너스</span>
          </RouterLink>
          <RouterLink v-if="auth.user?.role === 'MANAGER'" to="/manager" class="nav-link" active-class="active">
            <span class="nav-link-icon"><IconUsersGroup :size="20" /></span>
            <span class="nav-link-title">팀원 평가</span>
          </RouterLink>
          <RouterLink v-if="auth.user?.role === 'EMPLOYEE'" to="/employee" class="nav-link" active-class="active">
            <span class="nav-link-icon"><IconClipboardCheck :size="20" /></span>
            <span class="nav-link-title">내 평가 결과</span>
          </RouterLink>
        </div>
      </div>
      <div class="sidebar-footer">
        <span class="avatar avatar-sm">HR</span>
        <div>
          <div class="fw-semibold">{{ auth.user?.name }}</div>
          <div class="text-secondary small">{{ auth.user?.employee_id }} · {{ auth.user?.role }}</div>
        </div>
        <button class="btn btn-ghost-secondary btn-icon ms-auto" type="button" aria-label="로그아웃" title="로그아웃" @click="logout">
          <IconLogout :size="18" />
        </button>
      </div>
    </aside>

    <div class="app-main">
      <header class="navbar navbar-expand-md d-print-none app-header">
        <div class="container-fluid">
          <div class="header-context">
            <span class="text-secondary small">인사 관리</span>
            <span class="text-secondary">/</span>
            <span class="fw-semibold">성과 평가</span>
          </div>
          <span class="badge bg-blue-lt">2026 상반기</span>
        </div>
      </header>
      <main class="page-wrapper">
        <div class="page-body">
          <div class="container-fluid">
            <RouterView />
          </div>
        </div>
      </main>
    </div>
  </div>
</template>