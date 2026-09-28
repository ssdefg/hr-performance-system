<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import {
  IconDownload,
  IconGift,
  IconUsers,
  IconChartBar,
  IconTargetArrow,
  IconSparkles,
  IconRadar,
  IconScale,
  IconAlertCircle,
  IconCheck,
} from '@tabler/icons-vue'
import client, { getErrorMessage } from '../../api/client'
import TeamRadarChart from '../../components/dashboard/TeamRadarChart.vue'

const kpi = ref(null)
const analytics = ref(null)
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

const selectedTeamRadar = computed(() => {
  if (!analytics.value?.teams_radar || !selectedTeamId.value) return null
  return analytics.value.teams_radar.find((t) => String(t.team_id) === selectedTeamId.value) || null
})

async function loadDashboard() {
  loading.value = true
  error.value = ''
  try {
    const params = selectedTeamId.value ? { team_id: selectedTeamId.value } : {}
    const [kpiResponse, teamsResponse, tableResponse, analyticsResponse] = await Promise.all([
      client.get('/reports/dashboard-kpi/'),
      client.get('/teams/'),
      client.get('/reports/score-table/', { params }),
      client.get('/reports/team-analytics/'),
    ])
    kpi.value = kpiResponse.data
    teams.value = teamsResponse.data
    rows.value = tableResponse.data
    analytics.value = analyticsResponse.data

    if (selectedTeamId.value) {
      const team = teams.value.find((item) => String(item.id) === selectedTeamId.value)
      if (team) bonusScore.value = Number(team.bonus_score) || 0
    } else {
      bonusScore.value = 0
    }
  } catch (requestError) {
    error.value = getErrorMessage(requestError, '점수 관리 데이터를 불러오지 못했습니다.')
  } finally {
    loading.value = false
  }
}

watch(selectedTeamId, () => {
  notice.value = ''
  error.value = ''
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
    error.value = getErrorMessage(requestError, '팀 보너스를 적용하지 못했습니다.')
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
  } catch (requestError) {
    error.value = getErrorMessage(requestError, 'CSV 파일을 다운로드하지 못했습니다.')
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

function gradeBadgeClass(grade) {
  switch (grade) {
    case 'S':
      return 'badge bg-purple-lt text-purple'
    case 'A':
      return 'badge bg-blue-lt text-blue'
    case 'B':
      return 'badge bg-green-lt text-green'
    case 'C':
      return 'badge bg-orange-lt text-orange'
    case 'D':
      return 'badge bg-red-lt text-red'
    default:
      return 'badge bg-secondary-lt text-secondary'
  }
}

function distributionStatusBadge(status) {
  switch (status) {
    case 'OVER':
      return 'badge bg-danger-lt text-danger'
    case 'UNDER':
      return 'badge bg-warning-lt text-warning'
    default:
      return 'badge bg-success-lt text-success'
  }
}

onMounted(loadDashboard)
</script>

<template>
  <div class="admin-page-heading">
    <div>
      <p class="eyebrow">COMPENSATION & REPORTING</p>
      <h2 class="page-title">점수 및 보너스 관리</h2>
      <p class="text-secondary mb-0">제출 점수, 등급 배분 및 팀 역량 분석을 확인하고 팀 보너스를 반영합니다.</p>
    </div>
  </div>

  <div v-if="error && error.trim()" class="alert alert-danger d-flex align-items-center justify-content-between mb-3" role="alert">
    <div class="d-flex align-items-center gap-2">
      <IconAlertCircle :size="18" />
      <span>{{ error }}</span>
    </div>
    <button type="button" class="btn-close" aria-label="닫기" @click="error = ''"></button>
  </div>
  <div v-if="notice && notice.trim()" class="alert alert-success d-flex align-items-center justify-content-between mb-3" role="status">
    <div class="d-flex align-items-center gap-2">
      <IconCheck :size="18" />
      <span>{{ notice }}</span>
    </div>
    <button type="button" class="btn-close" aria-label="닫기" @click="notice = ''"></button>
  </div>

  <!-- 상단 4열 KPI 카드 -->
  <section v-if="loading && !kpi" class="metric-grid" aria-label="KPI 불러오는 중">
    <div v-for="index in 4" :key="index" class="metric-panel">
      <div class="placeholder placeholder-glow w-50"></div>
      <div class="placeholder placeholder-glow w-75 mt-3"></div>
    </div>
  </section>
  <section v-else-if="kpi" class="score-kpi-grid" aria-label="평가 주요 지표">
    <article class="score-kpi-card card-enterprise">
      <div class="score-kpi-icon bg-azure-lt"><IconUsers :size="18" /></div>
      <div class="metric-label">전체 평가 대상</div>
      <div class="metric-value">{{ kpi.total_employees }}<span class="metric-suffix">명</span></div>
      <div class="metric-note">활성 직원 계정</div>
    </article>
    <article class="score-kpi-card card-enterprise">
      <div class="score-kpi-icon bg-green-lt"><IconChartBar :size="18" /></div>
      <div class="metric-label">평가 완료율</div>
      <div class="metric-value">{{ Number(kpi.completion_rate).toFixed(1) }}<span class="metric-suffix">%</span></div>
      <div class="progress progress-sm mt-2">
        <div class="progress-bar bg-green" :style="{ width: `${Math.min(kpi.completion_rate, 100)}%` }"></div>
      </div>
      <div class="metric-note mt-1">{{ kpi.completed_reviews }}명 제출 완료</div>
    </article>
    <article class="score-kpi-card card-enterprise">
      <div class="score-kpi-icon bg-orange-lt"><IconTargetArrow :size="18" /></div>
      <div class="metric-label">전사 평균 점수</div>
      <div class="metric-value">{{ Number(kpi.company_average_score).toFixed(2) }}<span class="metric-suffix">점</span></div>
      <div class="metric-note">제출 완료 평가 기준</div>
    </article>
    <article class="score-kpi-card card-enterprise">
      <div class="score-kpi-icon bg-purple-lt"><IconGift :size="18" /></div>
      <div class="metric-label">팀 보너스 적용</div>
      <div class="metric-value">{{ kpi.bonus_summary.teams_with_bonus }}<span class="metric-suffix"> / {{ kpi.bonus_summary.total_teams }}팀</span></div>
      <div class="metric-note">보너스가 설정된 팀</div>
    </article>
  </section>

  <!-- 고급 시각화 섹션 (레이더 차트 & 상대평가 배분 현황) -->
  <section v-if="analytics" class="analytics-grid mt-4">
    <div class="row g-3">
      <!-- 1. 팀별 역량 레이더 차트 -->
      <div class="col-lg-6">
        <div class="card card-enterprise h-100">
          <div class="card-header d-flex align-items-center justify-content-between py-3">
            <div class="d-flex align-items-center gap-2">
              <span class="score-kpi-icon bg-azure-lt p-1 rounded-2"><IconRadar :size="18" /></span>
              <h3 class="card-title mb-0">팀별 역량 레이더 분석</h3>
            </div>
            <span v-if="selectedTeamRadar" class="badge bg-blue-lt">
              {{ selectedTeamRadar.team_name }} (제출: {{ selectedTeamRadar.submitted_count }}건)
            </span>
            <span v-else class="badge bg-secondary-lt">전체 팀 비교</span>
          </div>
          <div class="card-body">
            <TeamRadarChart
              :criteria-labels="analytics.criteria_labels"
              :company-radar="analytics.company_radar"
              :selected-team="selectedTeamRadar"
              :all-teams="analytics.teams_radar"
            />
          </div>
          <div class="card-footer bg-transparent py-2 border-top">
            <div class="d-flex align-items-center justify-content-between text-secondary small">
              <span>* 각 항목 5.0점 척도 기준 매니저 채점 평균</span>
              <span>점선: 전사 평균 비교</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 2. 상대평가 등급 배분율 체크 위젯 -->
      <div class="col-lg-6">
        <div class="card card-enterprise h-100">
          <div class="card-header d-flex align-items-center justify-content-between py-3">
            <div class="d-flex align-items-center gap-2">
              <span class="score-kpi-icon bg-purple-lt p-1 rounded-2"><IconScale :size="18" /></span>
              <h3 class="card-title mb-0">상대평가 등급 배분 현황</h3>
            </div>
            <span class="badge bg-purple-lt">
              제출 인원: {{ analytics.distribution.total_submitted }}명
            </span>
          </div>
          <div class="card-body">
            <div class="distribution-bars mb-3">
              <div v-for="item in analytics.distribution.grades" :key="item.grade" class="distribution-item mb-2 pb-2 border-bottom">
                <div class="d-flex align-items-center justify-content-between mb-1">
                  <div class="d-flex align-items-center gap-2">
                    <span :class="gradeBadgeClass(item.grade)" class="fw-bold px-2">{{ item.grade }}등급</span>
                    <span class="small text-secondary">({{ item.count }}명 / {{ item.percentage }}%)</span>
                  </div>
                  <div class="d-flex align-items-center gap-2">
                    <span class="small text-muted">권장: {{ item.recommended_percentage }}%</span>
                    <span :class="distributionStatusBadge(item.status)" class="badge">
                      {{ item.status === 'OVER' ? `초과 (+${item.diff_percentage}%p)` : (item.status === 'UNDER' ? `미달 (${item.diff_percentage}%p)` : '적정') }}
                    </span>
                  </div>
                </div>
                <div class="progress progress-sm" style="height: 6px;">
                  <div
                    class="progress-bar"
                    :class="{
                      'bg-purple': item.grade === 'S',
                      'bg-blue': item.grade === 'A',
                      'bg-green': item.grade === 'B',
                      'bg-orange': item.grade === 'C',
                      'bg-red': item.grade === 'D'
                    }"
                    :style="{ width: `${Math.min(item.percentage, 100)}%` }"
                  ></div>
                </div>
              </div>
            </div>

            <!-- 인라인 요약 칩 영역 -->
            <div class="distribution-summary-chips">
              <div class="small fw-semibold text-secondary mb-2">배분율 가이드라인 점검:</div>
              <div class="d-flex flex-wrap gap-2">
                <span
                  v-for="chip in analytics.distribution.summary_chips"
                  :key="chip.grade"
                  class="badge border d-flex align-items-center gap-1 py-1 px-2"
                  :class="chip.status === 'OVER' ? 'border-danger text-danger bg-danger-subtle' : (chip.status === 'UNDER' ? 'border-secondary text-secondary bg-light' : 'border-success text-success bg-success-subtle')"
                >
                  <IconAlertCircle v-if="chip.status !== 'NORMAL'" :size="14" />
                  <IconCheck v-else :size="14" />
                  {{ chip.message }}
                </span>
              </div>
            </div>
          </div>
          <div class="card-footer bg-transparent py-2 border-top">
            <span class="text-secondary small">
              * 가이드라인: S(10%), A(25%), B(50%), C/D(15%) 배분 권장
            </span>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- 툴바 섹션 -->
  <section class="score-toolbar mt-4" aria-label="점수 관리 작업">
    <div class="score-toolbar-control">
      <label class="form-label" for="score-team-filter">팀 선택</label>
      <select id="score-team-filter" v-model="selectedTeamId" class="form-select">
        <option value="">전체 팀</option>
        <option v-for="team in teams" :key="team.id" :value="String(team.id)">{{ team.name }}</option>
      </select>
    </div>
    <div class="score-toolbar-control score-bonus-input">
      <label class="form-label" for="bonus-score">팀 보너스</label>
      <div class="input-group">
        <input
          id="bonus-score"
          v-model.number="bonusScore"
          class="form-control"
          type="number"
          min="0"
          max="10"
          step="0.5"
          :disabled="!hasSelectedTeam"
        />
        <span class="input-group-text">점</span>
      </div>
    </div>
    <button class="btn btn-primary" type="button" :disabled="!hasSelectedTeam || applying" @click="applyBonus">
      <IconSparkles :size="17" />{{ applying ? '반영 중...' : '팀 전체 일괄 적용' }}
    </button>
    <button class="btn btn-outline-secondary ms-auto" type="button" :disabled="downloading" @click="downloadCsv">
      <IconDownload :size="17" />{{ downloading ? '준비 중...' : 'CSV 다운로드' }}
    </button>
  </section>
  <p v-if="!hasSelectedTeam" class="text-secondary small score-toolbar-hint">
    팀 보너스를 입력하려면 먼저 팀을 선택하세요. CSV는 현재 조회 범위를 다운로드합니다.
  </p>

  <!-- 점수 및 등급 관리 테이블 -->
  <section class="card card-enterprise score-table-card mt-3">
    <div class="table-responsive">
      <table class="table table-vcenter card-table">
        <thead>
          <tr>
            <th>사원 정보</th>
            <th>소속 팀</th>
            <th>평가 상태</th>
            <th class="text-end">개인 점수</th>
            <th>팀 보너스</th>
            <th class="text-end">최종 점수</th>
            <th class="text-center">등급</th>
          </tr>
        </thead>
        <tbody v-if="!loading && rows.length">
          <tr v-for="row in rows" :key="row.id">
            <td>
              <div class="user-name-cell">
                <span class="avatar avatar-sm bg-blue-lt">{{ row.name.slice(0, 1) }}</span>
                <span>
                  <strong class="d-block">{{ row.name }}</strong>
                  <small class="text-secondary">{{ row.employee_id }}</small>
                </span>
              </div>
            </td>
            <td>{{ row.team_name || '미배정' }}</td>
            <td>
              <span class="badge" :class="statusClass(row.review_status)">{{ statusLabel(row.review_status) }}</span>
            </td>
            <td class="text-end">{{ row.raw_score === null ? '—' : `${Number(row.raw_score).toFixed(2)}점` }}</td>
            <td>
              <span class="badge bg-success-lt text-success rounded-pill">+{{ Number(row.bonus_score).toFixed(1) }}점</span>
            </td>
            <td class="text-end">
              <strong>{{ row.final_score === null ? '—' : `${Number(row.final_score).toFixed(2)}점` }}</strong>
              <span v-if="row.is_capped" class="badge bg-indigo-lt text-indigo ms-2">(상한)</span>
            </td>
            <td class="text-center">
              <span v-if="row.grade" :class="gradeBadgeClass(row.grade)" class="fw-bold px-2 py-1">
                {{ row.grade }}
              </span>
              <span v-else class="text-secondary">—</span>
            </td>
          </tr>
        </tbody>
        <tbody v-else-if="loading">
          <tr>
            <td colspan="7"><div class="placeholder placeholder-glow w-100"></div></td>
          </tr>
        </tbody>
        <tbody v-else>
          <tr>
            <td colspan="7" class="text-center text-secondary py-5">조회 조건에 맞는 직원이 없습니다.</td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>

<style scoped>
.analytics-grid {
  margin-bottom: 1.5rem;
}
</style>