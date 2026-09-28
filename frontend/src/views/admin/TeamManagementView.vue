<script setup>
import { computed, onMounted, ref } from 'vue'
import { IconPlus, IconPencil, IconTrash } from '@tabler/icons-vue'
import client, { getErrorMessage } from '../../api/client'

const teams = ref([])
const managers = ref([])
const loading = ref(true)
const error = ref('')
const modalOpen = ref(false)
const saving = ref(false)
const editingId = ref(null)
const form = ref({ name: '', manager_id: null, bonus_score: 0 })
const availableManagers = computed(() => managers.value.filter((manager) => !manager.team_id || manager.team_id === editingId.value || manager.id === form.value.manager_id))

async function loadData() {
  loading.value = true
  error.value = ''
  try {
    const [teamResponse, userResponse] = await Promise.all([
      client.get('/teams/'),
      client.get('/users/', { params: { role: 'MANAGER' } }),
    ])
    teams.value = teamResponse.data
    managers.value = userResponse.data
  } catch (requestError) {
    error.value = getErrorMessage(requestError, '팀 정보를 불러오지 못했습니다.')
  } finally {
    loading.value = false
  }
}

function openCreate() {
  editingId.value = null
  form.value = { name: '', manager_id: null, bonus_score: 0 }
  modalOpen.value = true
}

function openEdit(team) {
  editingId.value = team.id
  form.value = { name: team.name, manager_id: team.manager_id, bonus_score: team.bonus_score }
  modalOpen.value = true
}

async function saveTeam() {
  saving.value = true
  error.value = ''
  try {
    const payload = { ...form.value, manager_id: form.value.manager_id || null }
    if (editingId.value) await client.patch(`/teams/${editingId.value}/`, payload)
    else await client.post('/teams/', payload)
    modalOpen.value = false
    await loadData()
  } catch (requestError) {
    error.value = getErrorMessage(requestError, '팀을 저장하지 못했습니다.')
  } finally {
    saving.value = false
  }
}

async function deleteTeam(team) {
  if (!window.confirm(`${team.name}을(를) 삭제할까요?`)) return
  try {
    await client.delete(`/teams/${team.id}/`)
    await loadData()
  } catch {
    error.value = '팀을 삭제하지 못했습니다.'
  }
}

onMounted(loadData)
</script>

<template>
  <div class="admin-page-heading">
    <div>
      <p class="eyebrow">ORGANIZATION</p>
      <h2 class="page-title">팀 관리</h2>
      <p class="text-secondary mb-0">팀과 담당 매니저 배정을 관리합니다.</p>
    </div>
    <button class="btn btn-primary" type="button" @click="openCreate"><IconPlus :size="18" /> 팀 추가</button>
  </div>

  <div v-if="error" class="alert alert-danger" role="alert">{{ error }}</div>
  <section class="card card-enterprise">
    <div class="table-responsive">
      <table class="table table-vcenter card-table">
        <thead><tr><th>팀명</th><th>담당 매니저</th><th>소속 인원</th><th>팀 보너스</th><th class="w-1">관리</th></tr></thead>
        <tbody v-if="!loading && teams.length">
          <tr v-for="team in teams" :key="team.id">
            <td class="fw-semibold">{{ team.name }}</td>
            <td>{{ team.manager_name || '미배정' }}</td>
            <td>{{ team.member_count }}명</td>
            <td><span class="badge bg-green-lt">+{{ Number(team.bonus_score).toFixed(1) }}점</span></td>
            <td><div class="table-actions"><button class="btn btn-icon btn-ghost-secondary" :aria-label="`${team.name} 수정`" @click="openEdit(team)"><IconPencil :size="17" /></button><button class="btn btn-icon btn-ghost-danger" :aria-label="`${team.name} 삭제`" @click="deleteTeam(team)"><IconTrash :size="17" /></button></div></td>
          </tr>
        </tbody>
        <tbody v-else-if="loading"><tr><td colspan="5"><div class="placeholder placeholder-glow w-100"></div></td></tr></tbody>
        <tbody v-else><tr><td colspan="5" class="text-center text-secondary py-5">등록된 팀이 없습니다.</td></tr></tbody>
      </table>
    </div>
  </section>

  <div v-if="modalOpen" class="modal-backdrop-enterprise" @click.self="modalOpen = false">
    <section class="modal-panel" role="dialog" aria-modal="true" aria-labelledby="team-modal-title">
      <header class="modal-panel-header"><h3 id="team-modal-title">{{ editingId ? '팀 수정' : '팀 추가' }}</h3><button class="btn-close" aria-label="닫기" @click="modalOpen = false"></button></header>
      <form @submit.prevent="saveTeam">
        <div class="modal-panel-body">
          <label class="form-label" for="team-name">팀명</label><input id="team-name" v-model.trim="form.name" class="form-control mb-3" required maxlength="100" />
          <label class="form-label" for="team-manager">담당 매니저</label><select id="team-manager" v-model="form.manager_id" class="form-select mb-3"><option :value="null">미배정</option><option v-for="manager in availableManagers" :key="manager.id" :value="manager.id">{{ manager.name }} · {{ manager.employee_id }}</option></select>
          <label class="form-label" for="team-bonus">팀 보너스 점수</label><input id="team-bonus" v-model.number="form.bonus_score" type="number" min="0" max="10" step="0.5" class="form-control" />
          <div v-if="error" class="alert alert-danger mt-3 mb-0">{{ error }}</div>
        </div>
        <footer class="modal-panel-footer"><button class="btn btn-outline-secondary" type="button" @click="modalOpen = false">취소</button><button class="btn btn-primary" type="submit" :disabled="saving">{{ saving ? '저장 중...' : '저장' }}</button></footer>
      </form>
    </section>
  </div>
</template>