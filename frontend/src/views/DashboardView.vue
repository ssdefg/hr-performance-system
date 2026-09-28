<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import {
  IconUsers,
  IconChartBar,
  IconTargetArrow,
  IconGift,
  IconChevronRight,
  IconRefresh,
  IconChartPie,
  IconRadar,
  IconTable,
  IconFilter,
  IconX,
} from '@tabler/icons-vue'
import client from '../api/client'
import TeamAverageBarChart from '../components/dashboard/TeamAverageBarChart.vue'
import TeamGradeBarChart from '../components/dashboard/TeamGradeBarChart.vue'
import CompetencyRadarChart from '../components/dashboard/CompetencyRadarChart.vue'

const router = useRouter()
const loading = ref(true)
const error = ref('')
const stats = ref(null)
const selectedTeamFilter = ref(null)

async function loadDashboardStats() {
  loading.value = true
  error.value = ''
  try {
    const res = await client.get('/admin/dashboard-stats/')
    stats.value = res.data
  } catch (requestError) {
    error.value = requestError.response?.data?.detail || '대시보드 통계 데이터를 불러오지 못했습니다.'
  } finally {
    loading.value = false
  }
}

function handleSelectTeam(teamName) {
  if (selectedTeamFilter.value === teamName) {
    selectedTeamFilter.value = null
  } else {
    selectedTeamFilter.value = teamName
  }
}

function clearTeamFilter() {
  selectedTeamFilter.value = null
}

const filteredEmployees = computed(() => {
  const list = stats.value?.score_table || []
  if (!selectedTeamFilter.value) {
    return list
  }
  return list.filter((item) => item.team_name === selectedTeamFilter.value)
})

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

onMounted(loadDashboardStats)
</script>

<template>
  <div class="admin-page-heading d-flex align-items-center justify-content-between flex-wrap gap-2">
    <div>
      <p class="eyebrow">PERFORMANCE DASHBOARD</p>
      <h2 class="page-title">통계 대시보드 및 결과 분석</h2>
      <p class="text-secondary mb-0">실시간 성과 평가 현황, 팀별 역량 통계 및 등급 분포를 확인합니다.</p>
    </div>
    <div class="d-flex align-items-center gap-2">
      <button class="btn btn-outline-secondary" type="button" :disabled="loading" @click="loadDashboardStats">
        <IconRefresh :size="16" /> 새로고침
      </button>
      <button class="btn btn-primary" type="button" @click="router.push('/admin/scores')">
        점수 및 보너스 관리 <IconChevronRight :size="16" />
      </button>
    </div>
  </div>

  <div v-if="error" class="alert alert-danger" role="alert">{{ error }}</div>

  <!-- 1. 상단 4열 실제 KPI 카드 -->
  <section v-if="loading && !stats" class="metric-grid" aria-label="KPI 로딩 중">
    <div v-for="index in 4" :key="index" class="metric-panel">
      <div class="placeholder placeholder-glow w-50"></div>
      <div class="placeholder placeholder-glow w-75 mt-3"></div>
    </div>
  </section>
  <section v-else-if="stats?.kpi" class="score-kpi-grid" aria-label="평가 주요 지표">
    <article class="score-kpi-card card-enterprise">
      <div class="score-kpi-icon bg-azure-lt"><IconUsers :size="18" /></div>
      <div class="metric-label">전체 평가 대상</div>
      <div class="metric-value">{{ stats.kpi.total_employees }}<span class="metric-suffix">명</span></div>
      <div class="metric-note">활성 피평가 직원 수</div>
    </article>
    <article class="score-kpi-card card-enterprise">
      <div class="score-kpi-icon bg-green-lt"><IconChartBar :size="18" /></div>
      <div class="metric-label">평가 완료율</div>
      <div class="metric-value">{{ Number(stats.kpi.submission_rate).toFixed(1) }}<span class="metric-suffix">%</span></div>
      <div class="progress progress-sm mt-2">
        <div class="progress-bar bg-green" :style="{ width: `${Math.min(stats.kpi.submission_rate, 100)}%` }"></div>
      </div>
      <div class="metric-note mt-1">{{ stats.kpi.completed_reviews }}명 제출 완료</div>
    </article>
    <article class="score-kpi-card card-enterprise">
      <div class="score-kpi-icon bg-orange-lt"><IconTargetArrow :size="18" /></div>
      <div class="metric-label">전사 평균 점수</div>
      <div class="metric-value">{{ Number(stats.kpi.overall_average).toFixed(2) }}<span class="metric-suffix">점</span></div>
      <div class="metric-note">제출 완료자 최종 점수</div>
    </article>
    <article class="score-kpi-card card-enterprise">
      <div class="score-kpi-icon bg-purple-lt"><IconGift :size="18" /></div>
      <div class="metric-label">팀 보너스 현황</div>
      <div class="metric-value">{{ stats.kpi.bonus_applied_teams }}</div>
      <div class="metric-note">보너스가 설정된 부서</div>
    </article>
  </section>

  <!-- 2. 3대 핵심 시각화 차트 그리드 (막대 1 + 막대 2 + 레이더) -->
  <section v-if="stats" class="charts-grid-section mt-4">
    <div class="d-flex align-items-center justify-content-between mb-2">
      <div class="text-secondary small">
        💡 차트의 <strong>막대</strong> 또는 <strong>범례</strong>를 클릭하면 하단 테이블이 해당 팀으로 즉시 드릴다운 필터링됩니다.
      </div>
      <span v-if="selectedTeamFilter" class="badge bg-primary-lt text-primary px-2 py-1">
        선택된 팀: {{ selectedTeamFilter }}
      </span>
    </div>
    <div class="row g-3">
      <!-- 차트 1: 팀별 평균 점수 비교 -->
      <div class="col-lg-4">
        <div class="card card-enterprise h-100" :class="{ 'border-primary': selectedTeamFilter }">
          <div class="card-header py-3 d-flex align-items-center justify-content-between">
            <div class="d-flex align-items-center gap-2">
              <span class="score-kpi-icon bg-azure-lt p-1 rounded-2 mb-0"><IconChartBar :size="16" /></span>
              <h3 class="card-title mb-0 fs-4">팀별 평균 점수</h3>
            </div>
            <span class="badge bg-secondary-lt text-secondary">클릭 필터링</span>
          </div>
          <div class="card-body">
            <TeamAverageBarChart
              :chart-data="stats.team_averages"
              :selected-team="selectedTeamFilter"
              @select-team="handleSelectTeam"
            />
          </div>
          <div class="card-footer bg-transparent py-2 border-top text-secondary small">
            부서별 최종 환산 점수 평균치 (100점 기준)
          </div>
        </div>
      </div>

      <!-- 차트 2: 팀별 등급 분포 -->
      <div class="col-lg-4">
        <div class="card card-enterprise h-100" :class="{ 'border-primary': selectedTeamFilter }">
          <div class="card-header py-3 d-flex align-items-center justify-content-between">
            <div class="d-flex align-items-center gap-2">
              <span class="score-kpi-icon bg-purple-lt p-1 rounded-2 mb-0"><IconChartPie :size="16" /></span>
              <h3 class="card-title mb-0 fs-4">팀별 등급 분포</h3>
            </div>
            <span class="badge bg-secondary-lt text-secondary">클릭 필터링</span>
          </div>
          <div class="card-body">
            <TeamGradeBarChart
              :chart-data="stats.team_grade_distribution"
              :selected-team="selectedTeamFilter"
              @select-team="handleSelectTeam"
            />
          </div>
          <div class="card-footer bg-transparent py-2 border-top text-secondary small">
            S / A / B / C / D 등급별 인원 수 누적 분포
          </div>
        </div>
      </div>

      <!-- 차트 3: 평가 항목별 팀 역량 레이더 차트 -->
      <div class="col-lg-4">
        <div class="card card-enterprise h-100" :class="{ 'border-primary': selectedTeamFilter }">
          <div class="card-header py-3 d-flex align-items-center justify-content-between">
            <div class="d-flex align-items-center gap-2">
              <span class="score-kpi-icon bg-green-lt p-1 rounded-2 mb-0"><IconRadar :size="16" /></span>
              <h3 class="card-title mb-0 fs-4">평가 항목별 팀 역량</h3>
            </div>
            <span class="badge bg-secondary-lt text-secondary">클릭 필터링</span>
          </div>
          <div class="card-body">
            <CompetencyRadarChart
              :chart-data="stats.criteria_team_radar"
              :selected-team="selectedTeamFilter"
              @select-team="handleSelectTeam"
            />
          </div>
          <div class="card-footer bg-transparent py-2 border-top text-secondary small">
            항목별 5.0점 척도 기준 부서별 역량 다각형
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- 3. 사원별 최종 결과 테이블 -->
  <section v-if="stats?.score_table" class="score-table-section mt-4">
    <div class="section-heading d-flex align-items-center justify-content-between flex-wrap gap-2 mb-3">
      <div class="d-flex align-items-center gap-2">
        <span class="score-kpi-icon bg-azure-lt p-1 rounded-2 mb-0"><IconTable :size="18" /></span>
        <div>
          <h3 class="section-title mb-0">사원별 최종 평가 결과 목록</h3>
          <p class="text-secondary small mb-0">전사 직원의 개인 원점수, 팀 보너스 및 최종 산출 등급</p>
        </div>
      </div>

      <!-- 필터 상태 태그 & 초기화 버튼 -->
      <div v-if="selectedTeamFilter" class="d-flex align-items-center gap-2">
        <span class="badge bg-azure-lt text-azure p-2 fs-6 d-flex align-items-center gap-1">
          <IconFilter :size="15" />
          필터 적용 중: <strong>{{ selectedTeamFilter }}</strong> (총 {{ filteredEmployees.length }}명)
        </span>
        <button class="btn btn-sm btn-outline-danger d-flex align-items-center gap-1" type="button" @click="clearTeamFilter">
          <IconX :size="14" /> 전체 보기 (초기화)
        </button>
      </div>
      <div v-else class="text-secondary small">
        전체 사원 (총 {{ stats.score_table.length }}명)
      </div>
    </div>

    <!-- 활성 필터 알림 배너 (필터 시 강조) -->
    <div v-if="selectedTeamFilter" class="alert alert-info d-flex align-items-center justify-content-between py-2 px-3 mb-3 border-0 bg-azure-lt rounded-3 shadow-none">
      <div class="d-flex align-items-center gap-2">
        <span class="badge bg-primary text-white">📌 필터 적용 중</span>
        <span>
          현재 <strong>{{ selectedTeamFilter }}</strong> 소속 사원만 조회하고 있습니다. (해당 팀원: {{ filteredEmployees.length }}명)
        </span>
      </div>
      <button class="btn btn-sm btn-primary d-flex align-items-center gap-1" type="button" @click="clearTeamFilter">
        <IconX :size="14" /> 필터 해제
      </button>
    </div>

    <div class="card card-enterprise">
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
          <tbody>
            <tr v-if="filteredEmployees.length === 0">
              <td colspan="7" class="text-center py-4 text-secondary">
                선택된 팀(<strong>{{ selectedTeamFilter }}</strong>)에 해당하는 사원이 없습니다.
              </td>
            </tr>
            <tr v-for="row in filteredEmployees" :key="row.id">
              <td>
                <div class="user-name-cell">
                  <span class="avatar avatar-sm bg-blue-lt">{{ row.name.slice(0, 1) }}</span>
                  <span>
                    <strong class="d-block">{{ row.name }}</strong>
                    <small class="text-secondary">{{ row.employee_id }}</small>
                  </span>
                </div>
              </td>
              <td>
                <span class="badge bg-secondary-lt text-dark">{{ row.team_name || '미배정' }}</span>
              </td>
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
                  {{ row.grade }}등급
                </span>
                <span v-else class="text-secondary">—</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </section>
</template>

<style scoped>
.score-kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1rem;
}
.score-kpi-card {
  padding: 1.25rem;
}
.score-kpi-icon {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  margin-bottom: 0.75rem;
}
.metric-label {
  font-size: 0.8125rem;
  color: #64748b;
  font-weight: 500;
}
.metric-value {
  font-size: 1.625rem;
  font-weight: 700;
  color: #0f172a;
  line-height: 1.2;
  margin: 0.25rem 0;
}
.metric-suffix {
  font-size: 0.875rem;
  font-weight: 500;
  color: #64748b;
  margin-left: 0.25rem;
}
.metric-note {
  font-size: 0.75rem;
  color: #94a3b8;
}
</style>