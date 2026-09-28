<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { IconDownload, IconGift, IconUsers, IconChartBar, IconTargetArrow, IconSparkles } from '@tabler/icons-vue'
import client from '../../api/client'

const kpi = ref(null)
const teams = ref([])
const rows = ref([])
const selectedTeamId = ref('')
const bonusScore = ref(0)
const loading = ref(true)
const applying = ref(false)
const downloading = ref(false)
const error = ref('')
const notice = ref('')
const hasSelectedTeam = computed(() => Boolean(selectedTeamId.value))

async function loadDashboard() {
  loading.value = true
  error.value = ''
  try {
    const params = selectedTeamId.value ? { team_id: selectedTeamId.value } : {}
    const [kpiResponse, teamsResponse, tableResponse] = await Promise.all([
      client.get('/reports/dashboard-kpi/'),
      client.get('/teams/'),
      client.get('/reports/score-table/', { params }),
    ])
    kpi.value = kpiResponse.data
    teams.value = teamsResponse.data
    rows.value = tableResponse.data
    if (selectedTeamId.value) {
      const team = teams.value.find((item) => String(item.id) === selectedTeamId.value)
      if (team) bonusScore.value = Number(team.bonus_score)
    }
  } catch (requestError) {
    error.value = requestError.response?.data?.detail || '점수 관리 데이터를 불러오지 못했습니다.'
  } finally {
    loading.value = false
  }
}

watch(selectedTeamId, () => {
  notice.value = ''
  loadDashboard()
})

async function applyBonus() {
  if (!selectedTeamId.value) return
  const team = teams.value.find((item) => String(item.id) === selectedTeamId.value)
  const accepted = window.confirm(`${team?.name} 팀 전체에 +${Number(bonusScore.value).toFixed(1)}점을 적용하고 제출된 점수를 다시 계산할까요?`)
  if (!accepted) return
  applying.value = true
  error.value = ''
  notice.value = ''
  try {
    const { data } = await client.post(`/teams/${selectedTeamId.value}/bonus/`, { bonus_score: Number(bonusScore.value) })
    notice.value = `${data.team_name} ${data.updated_reviews}건의 제출 점수를 업데이트했습니다.`
    await loadDashboard()
  } catch (requestError) {
    error.value = requestError.response?.data?.bonus_score?.[0] || requestError.response?.data?.detail || '팀 보너스를 적용하지 못했습니다.'
  } finally {
    applying.value = false
  }
}

async function downloadCsv() {
  downloading.value = true
  error.value = ''
  try {
    const params = selectedTeamId.value ? { team_id: selectedTeamId.value } : {}
    const response = await client.get('/reports/export-csv/', { params, responseType: 'blob' })
    const blob = new Blob([response.data], { type: 'text/csv;charset=utf-8-sig' })
    const url = URL.createObjectURL(blob)
    const anchor = document.createElement('a')
    anchor.href = url
    anchor.download = response.headers['content-disposition']?.match(/filename="?([^";]+)"?/)?.[1] || 'HR_Performance_Review.csv'
    anchor.click()
    URL.revokeObjectURL(url)
  } catch {
    error.value = 'CSV 파일을 다운로드하지 못했습니다.'
  } finally {
    downloading.value = false
  }
}

function statusLabel(status) {
  return { NOT_STARTED: '평가 대기', DRAFT: '임시 저장', SUBMITTED: '제출 완료' }[status] || status
}
function statusClass(status) {
  return { NOT_STARTED: 'bg-secondary-lt', DRAFT: 'bg-yellow-lt', SUBMITTED: 'bg-green-lt' }[status]
}

onMounted(loadDashboard)
</script>

<template>
  <div class="admin-page-heading"><div><p class="eyebrow">COMPENSATION & REPORTING</p><h2 class="page-title">점수 및 보너스 관리</h2><p class="text-secondary mb-0">제출 점수와 팀 보너스를 확인하고 일괄 반영합니다.</p></div></div>
  <div v-if="error" class="alert alert-danger" role="alert">{{ error }}</div>
  <div v-if="notice" class="alert alert-success" role="status">{{ notice }}</div>

  <section v-if="loading && !kpi" class="metric-grid" aria-label="KPI 불러오는 중"><div v-for="index in 4" :key="index" class="metric-panel"><div class="placeholder placeholder-glow w-50"></div><div class="placeholder placeholder-glow w-75 mt-3"></div></div></section>
  <section v-else-if="kpi" class="score-kpi-grid" aria-label="평가 주요 지표">
    <article class="score-kpi-card card-enterprise"><div class="score-kpi-icon bg-azure-lt"><IconUsers :size="18" /></div><div class="metric-label">전체 평가 대상</div><div class="metric-value">{{ kpi.total_employees }}<span class="metric-suffix">명</span></div><div class="metric-note">활성 직원 계정</div></article>
    <article class="score-kpi-card card-enterprise"><div class="score-kpi-icon bg-green-lt"><IconChartBar :size="18" /></div><div class="metric-label">평가 완료율</div><div class="metric-value">{{ Number(kpi.completion_rate).toFixed(1) }}<span class="metric-suffix">%</span></div><div class="progress progress-sm mt-2"><div class="progress-bar bg-green" :style="{ width: `${Math.min(kpi.completion_rate, 100)}%` }"></div></div><div class="metric-note mt-1">{{ kpi.completed_reviews }}명 제출 완료</div></article>
    <article class="score-kpi-card card-enterprise"><div class="score-kpi-icon bg-orange-lt"><IconTargetArrow :size="18" /></div><div class="metric-label">전사 평균 점수</div><div class="metric-value">{{ Number(kpi.company_average_score).toFixed(2) }}<span class="metric-suffix">점</span></div><div class="metric-note">제출 완료 평가 기준</div></article>
    <article class="score-kpi-card card-enterprise"><div class="score-kpi-icon bg-purple-lt"><IconGift :size="18" /></div><div class="metric-label">팀 보너스 적용</div><div class="metric-value">{{ kpi.bonus_summary.teams_with_bonus }}<span class="metric-suffix"> / {{ kpi.bonus_summary.total_teams }}팀</span></div><div class="metric-note">보너스가 설정된 팀</div></article>
  </section>

  <section class="score-toolbar" aria-label="점수 관리 작업">
    <div class="score-toolbar-control"><label class="form-label" for="score-team-filter">팀 선택</label><select id="score-team-filter" v-model="selectedTeamId" class="form-select"><option value="">전체 팀</option><option v-for="team in teams" :key="team.id" :value="String(team.id)">{{ team.name }}</option></select></div>
    <div class="score-toolbar-control score-bonus-input"><label class="form-label" for="bonus-score">팀 보너스</label><div class="input-group"><input id="bonus-score" v-model.number="bonusScore" class="form-control" type="number" min="0" max="10" step="0.5" :disabled="!hasSelectedTeam" /><span class="input-group-text">점</span></div></div>
    <button class="btn btn-primary" type="button" :disabled="!hasSelectedTeam || applying" @click="applyBonus"><IconSparkles :size="17" />{{ applying ? '반영 중...' : '팀 전체 일괄 적용' }}</button>
    <button class="btn btn-outline-secondary ms-auto" type="button" :disabled="downloading" @click="downloadCsv"><IconDownload :size="17" />{{ downloading ? '준비 중...' : 'CSV 다운로드' }}</button>
  </section>
  <p v-if="!hasSelectedTeam" class="text-secondary small score-toolbar-hint">팀 보너스를 입력하려면 먼저 팀을 선택하세요. CSV는 현재 조회 범위를 다운로드합니다.</p>

  <section class="card card-enterprise score-table-card"><div class="table-responsive"><table class="table table-vcenter card-table">
    <thead><tr><th>사원 정보</th><th>소속 팀</th><th>평가 상태</th><th class="text-end">개인 점수</th><th>팀 보너스</th><th class="text-end">최종 점수</th></tr></thead>
    <tbody v-if="!loading && rows.length"><tr v-for="row in rows" :key="row.id">
      <td><div class="user-name-cell"><span class="avatar avatar-sm bg-blue-lt">{{ row.name.slice(0, 1) }}</span><span><strong class="d-block">{{ row.name }}</strong><small class="text-secondary">{{ row.employee_id }}</small></span></div></td>
      <td>{{ row.team_name || '미배정' }}</td><td><span class="badge" :class="statusClass(row.review_status)">{{ statusLabel(row.review_status) }}</span></td>
      <td class="text-end">{{ row.raw_score === null ? '—' : `${Number(row.raw_score).toFixed(2)}점` }}</td><td><span class="badge bg-success-lt text-success rounded-pill">+{{ Number(row.bonus_score).toFixed(1) }}점</span></td>
      <td class="text-end"><strong>{{ row.final_score === null ? '—' : `${Number(row.final_score).toFixed(2)}점` }}</strong><span v-if="row.is_capped" class="badge bg-indigo-lt text-indigo ms-2">(상한)</span></td>
    </tr></tbody>
    <tbody v-else-if="loading"><tr><td colspan="6"><div class="placeholder placeholder-glow w-100"></div></td></tr></tbody><tbody v-else><tr><td colspan="6" class="text-center text-secondary py-5">조회 조건에 맞는 직원이 없습니다.</td></tr></tbody>
  </table></div></section>
</template>