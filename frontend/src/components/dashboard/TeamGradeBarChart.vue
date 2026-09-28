<script setup>
import { computed, ref, watch } from 'vue'
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
  Title,
} from 'chart.js'
import { Doughnut } from 'vue-chartjs'

ChartJS.register(
  ArcElement,
  Tooltip,
  Legend,
  Title,
)

const props = defineProps({
  chartData: {
    type: Object,
    default: () => ({ labels: [], teams_detail: [], company_detail: null }),
  },
  selectedTeam: {
    type: String,
    default: null,
  },
})

const emit = defineEmits(['select-team'])

// Internal active tab (null for company-wide / '전체', or specific team name)
const activeTab = ref(props.selectedTeam || null)

watch(
  () => props.selectedTeam,
  (newVal) => {
    activeTab.value = newVal || null
  },
)

function setTab(teamName) {
  activeTab.value = teamName
  emit('select-team', teamName)
}

const gradeColorMap = {
  S: { bg: '#7048e8', border: '#5f3dc4', text: 'text-purple', badge: 'bg-purple-lt text-purple' },
  A: { bg: '#206bc4', border: '#185499', text: 'text-blue', badge: 'bg-blue-lt text-blue' },
  B: { bg: '#2fb344', border: '#248c35', text: 'text-green', badge: 'bg-green-lt text-green' },
  C: { bg: '#f59f00', border: '#cc8500', text: 'text-orange', badge: 'bg-orange-lt text-orange' },
  D: { bg: '#d63939', border: '#ae2e2e', text: 'text-red', badge: 'bg-red-lt text-red' },
}

// Get active team detail or company detail
const currentDetail = computed(() => {
  if (!props.chartData) return null
  if (activeTab.value && props.chartData.teams_detail) {
    const found = props.chartData.teams_detail.find((t) => t.team_name === activeTab.value)
    if (found) return found
  }
  return props.chartData.company_detail || null
})

// Active grades with count > 0
const activeGrades = computed(() => {
  if (!currentDetail.value?.grades) return []
  const result = []
  for (const grade of ['S', 'A', 'B', 'C', 'D']) {
    const gInfo = currentDetail.value.grades[grade]
    if (gInfo && gInfo.count > 0) {
      result.push({
        grade,
        count: gInfo.count,
        names: gInfo.names || [],
        color: gradeColorMap[grade],
      })
    }
  }
  return result
})

const totalSubmitted = computed(() => {
  return currentDetail.value?.submitted_count ?? currentDetail.value?.total_submitted ?? 0
})

const totalMembers = computed(() => {
  return currentDetail.value?.total_members ?? 0
})

const doughnutData = computed(() => {
  if (activeGrades.value.length === 0) {
    return { labels: [], datasets: [] }
  }

  return {
    labels: activeGrades.value.map((item) => `${item.grade}등급`),
    datasets: [
      {
        data: activeGrades.value.map((item) => item.count),
        backgroundColor: activeGrades.value.map((item) => item.color.bg),
        borderColor: activeGrades.value.map((item) => item.color.border),
        borderWidth: 2,
        hoverOffset: 6,
      },
    ],
  }
})

const doughnutOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  cutout: '68%',
  plugins: {
    legend: {
      position: 'bottom',
      labels: {
        boxWidth: 12,
        padding: 12,
        font: { size: 11, weight: '600' },
        color: '#334155',
      },
    },
    tooltip: {
      backgroundColor: '#0f172a',
      padding: 10,
      cornerRadius: 8,
      callbacks: {
        label: (context) => {
          const gradeItem = activeGrades.value[context.dataIndex]
          if (!gradeItem) return ''
          const teamLabel = activeTab.value ? activeTab.value : '전사'
          const nameStr = gradeItem.names.length > 0 ? gradeItem.names.join(', ') : '인원'
          return ` ${teamLabel} ${gradeItem.grade}등급: ${nameStr} (${gradeItem.count}명)`
        },
      },
    },
  },
}))
</script>

<template>
  <div class="grade-distribution-container">
    <!-- 팀 선택 탭 네비게이션 -->
    <div class="team-tabs-bar mb-2 d-flex align-items-center gap-1 overflow-auto pb-1">
      <button
        type="button"
        class="btn btn-sm"
        :class="activeTab === null ? 'btn-primary shadow-sm' : 'btn-outline-secondary'"
        @click="setTab(null)"
      >
        전체
      </button>
      <button
        v-for="teamName in chartData?.labels || []"
        :key="teamName"
        type="button"
        class="btn btn-sm"
        :class="activeTab === teamName ? 'btn-primary shadow-sm' : 'btn-outline-secondary'"
        @click="setTab(teamName)"
      >
        {{ teamName }}
      </button>
    </div>

    <!-- 차트 및 중앙 인원수 표시 영역 -->
    <div class="doughnut-chart-wrapper" style="position: relative; height: 190px; width: 100%;">
      <div v-if="totalSubmitted === 0" class="empty-grade-state d-flex flex-column align-items-center justify-content-center h-100 text-center py-4">
        <span class="avatar avatar-md bg-secondary-lt text-secondary mb-2">0명</span>
        <div class="text-secondary small fw-medium">제출 완료된 평가가 없습니다.</div>
        <div class="text-muted" style="font-size: 0.75rem;">(총 {{ totalMembers }}명 중 0명 완료)</div>
      </div>
      <template v-else>
        <Doughnut :data="doughnutData" :options="doughnutOptions" />
        <div class="doughnut-center-text">
          <div class="center-count fw-bold">{{ totalSubmitted }}<span class="fs-6 fw-normal">명</span></div>
          <div class="center-label text-secondary">완료 / 총 {{ totalMembers }}명</div>
        </div>
      </template>
    </div>

    <!-- 하단 등급별 인원 및 사원명 칩 -->
    <div v-if="activeGrades.length > 0" class="grade-chips-list mt-2 d-flex flex-wrap gap-1 justify-content-center">
      <span
        v-for="item in activeGrades"
        :key="item.grade"
        class="badge border py-1 px-2 d-inline-flex align-items-center gap-1"
        :class="item.color.badge"
        :title="item.names.join(', ')"
      >
        <strong>{{ item.grade }}등급</strong>
        <span>{{ item.count }}명</span>
        <small v-if="item.names.length" class="text-secondary opacity-75">({{ item.names.join(', ') }})</small>
      </span>
    </div>
  </div>
</template>

<style scoped>
.grade-distribution-container {
  display: flex;
  flex-direction: column;
  height: 100%;
}
.team-tabs-bar {
  scrollbar-width: thin;
}
.doughnut-chart-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
}
.doughnut-center-text {
  position: absolute;
  top: 42%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
  pointer-events: none;
}
.center-count {
  font-size: 1.35rem;
  color: #0f172a;
  line-height: 1.1;
}
.center-label {
  font-size: 0.6875rem;
  line-height: 1;
  margin-top: 2px;
}
.empty-grade-state {
  background: #f8fafc;
  border-radius: 8px;
  border: 1px dashed #e2e8f0;
}
</style>

