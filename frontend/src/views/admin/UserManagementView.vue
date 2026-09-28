<script setup>
import { computed, onMounted, ref } from 'vue'
import { IconPlus, IconPencil, IconTrash } from '@tabler/icons-vue'
import client, { getErrorMessage } from '../../api/client'

const users = ref([])
const teams = ref([])
const loading = ref(true)
const error = ref('')
const modalOpen = ref(false)
const saving = ref(false)
const editingId = ref(null)
const roleFilter = ref('')
const teamFilter = ref('')
const form = ref({ employee_id: '', name: '', password: '', role: 'EMPLOYEE', team_id: null, is_active: true })
const visibleUsers = computed(() => users.value)

async function loadData() {
  loading.value = true
  error.value = ''
  try {
    const params = {}
    if (roleFilter.value) params.role = roleFilter.value
    if (teamFilter.value) params.team_id = teamFilter.value
    const [userResponse, teamResponse] = await Promise.all([client.get('/users/', { params }), client.get('/teams/')])
    users.value = userResponse.data
    teams.value = teamResponse.data
  } catch (requestError) {
    error.value = getErrorMessage(requestError, '사원 정보를 불러오지 못했습니다.')
  } finally {
    loading.value = false
  }
}

function openCreate() {
  editingId.value = null
  form.value = { employee_id: '', name: '', password: '', role: 'EMPLOYEE', team_id: null, is_active: true }
  modalOpen.value = true
}

function openEdit(user) {
  editingId.value = user.id
  form.value = { employee_id: user.employee_id, name: user.name, password: '', role: user.role, team_id: user.team_id, is_active: user.is_active }
  modalOpen.value = true
}

async function saveUser() {
  saving.value = true
  error.value = ''
  try {
    const payload = { ...form.value, team_id: form.value.team_id || null }
    if (!payload.password) delete payload.password
    if (editingId.value) await client.patch(`/users/${editingId.value}/`, payload)
    else await client.post('/users/', payload)
    modalOpen.value = false
    await loadData()
  } catch (requestError) {
    error.value = getErrorMessage(requestError, '사원 정보를 저장하지 못했습니다.')
  } finally {
    saving.value = false
  }
}

async function deleteUser(user) {
  if (!window.confirm(`${user.name} (${user.employee_id}) 계정을 삭제할까요?`)) return
  try {
    await client.delete(`/users/${user.id}/`)
    await loadData()
  } catch {
    error.value = '사원 계정을 삭제하지 못했습니다.'
  }
}

function roleLabel(role) {
  return { ADMIN: '관리자', MANAGER: '매니저', EMPLOYEE: '직원' }[role] || role
}

onMounted(loadData)
</script>

<template>
  <div class="admin-page-heading">
    <div><p class="eyebrow">PEOPLE DIRECTORY</p><h2 class="page-title">사원 관리</h2><p class="text-secondary mb-0">사원 계정과 조직 배정을 관리합니다.</p></div>
    <button class="btn btn-primary" type="button" @click="openCreate"><IconPlus :size="18" /> 사원 추가</button>
  </div>

  <section class="admin-toolbar">
    <div class="filter-group"><label class="form-label mb-0" for="role-filter">역할</label><select id="role-filter" v-model="roleFilter" class="form-select" @change="loadData"><option value="">전체</option><option value="ADMIN">관리자</option><option value="MANAGER">매니저</option><option value="EMPLOYEE">직원</option></select></div>
    <div class="filter-group"><label class="form-label mb-0" for="team-filter">팀</label><select id="team-filter" v-model="teamFilter" class="form-select" @change="loadData"><option value="">전체 팀</option><option v-for="team in teams" :key="team.id" :value="String(team.id)">{{ team.name }}</option></select></div>
  </section>
  <div v-if="error" class="alert alert-danger" role="alert">{{ error }}</div>
  <section class="card card-enterprise"><div class="table-responsive"><table class="table table-vcenter card-table">
    <thead><tr><th>사번</th><th>성명</th><th>역할</th><th>소속 팀</th><th>상태</th><th class="w-1">관리</th></tr></thead>
    <tbody v-if="!loading && visibleUsers.length"><tr v-for="user in visibleUsers" :key="user.id">
      <td class="text-secondary">{{ user.employee_id }}</td><td><div class="user-name-cell"><span class="avatar avatar-sm bg-blue-lt">{{ user.name.slice(0, 1) }}</span><span class="fw-semibold">{{ user.name }}</span></div></td>
      <td><span class="badge" :class="{ 'bg-purple-lt': user.role === 'ADMIN', 'bg-azure-lt': user.role === 'MANAGER', 'bg-secondary-lt': user.role === 'EMPLOYEE' }">{{ roleLabel(user.role) }}</span></td><td>{{ user.team_name || '미배정' }}</td><td><span class="badge" :class="user.is_active ? 'bg-green-lt' : 'bg-secondary-lt'">{{ user.is_active ? '활성' : '비활성' }}</span></td>
      <td><div class="table-actions"><button class="btn btn-icon btn-ghost-secondary" :aria-label="`${user.name} 수정`" @click="openEdit(user)"><IconPencil :size="17" /></button><button class="btn btn-icon btn-ghost-danger" :aria-label="`${user.name} 삭제`" @click="deleteUser(user)"><IconTrash :size="17" /></button></div></td>
    </tr></tbody>
    <tbody v-else-if="loading"><tr><td colspan="6"><div class="placeholder placeholder-glow w-100"></div></td></tr></tbody><tbody v-else><tr><td colspan="6" class="text-center text-secondary py-5">조건에 맞는 사원이 없습니다.</td></tr></tbody>
  </table></div></section>

  <div v-if="modalOpen" class="modal-backdrop-enterprise" @click.self="modalOpen = false"><section class="modal-panel" role="dialog" aria-modal="true" aria-labelledby="user-modal-title">
    <header class="modal-panel-header"><h3 id="user-modal-title">{{ editingId ? '사원 정보 수정' : '사원 등록' }}</h3><button class="btn-close" aria-label="닫기" @click="modalOpen = false"></button></header>
    <form @submit.prevent="saveUser"><div class="modal-panel-body">
      <label class="form-label" for="employee-id">사번</label><input id="employee-id" v-model.trim="form.employee_id" class="form-control mb-3" required :disabled="Boolean(editingId)" maxlength="50" />
      <label class="form-label" for="employee-name">성명</label><input id="employee-name" v-model.trim="form.name" class="form-control mb-3" required maxlength="100" />
      <label class="form-label" for="employee-password">{{ editingId ? '새 비밀번호 (변경 시 입력)' : '초기 비밀번호' }}</label><input id="employee-password" v-model="form.password" type="password" class="form-control mb-3" :required="!editingId" minlength="4" autocomplete="new-password" />
      <label class="form-label" for="employee-role">역할</label><select id="employee-role" v-model="form.role" class="form-select mb-3"><option value="ADMIN">관리자</option><option value="MANAGER">매니저</option><option value="EMPLOYEE">직원</option></select>
      <label class="form-label" for="employee-team">소속 팀</label><select id="employee-team" v-model="form.team_id" class="form-select mb-3"><option :value="null">미배정</option><option v-for="team in teams" :key="team.id" :value="team.id">{{ team.name }}</option></select>
      <label v-if="editingId" class="form-check"><input v-model="form.is_active" type="checkbox" class="form-check-input" /><span class="form-check-label">계정 활성화</span></label>
      <div v-if="error" class="alert alert-danger mt-3 mb-0">{{ error }}</div>
    </div><footer class="modal-panel-footer"><button class="btn btn-outline-secondary" type="button" @click="modalOpen = false">취소</button><button class="btn btn-primary" type="submit" :disabled="saving">{{ saving ? '저장 중...' : '저장' }}</button></footer></form>
  </section></div>
</template>