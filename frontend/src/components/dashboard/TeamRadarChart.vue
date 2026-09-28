<script setup>
import { computed } from 'vue'
import {
  Chart as ChartJS,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend,
} from 'chart.js'
import { Radar } from 'vue-chartjs'

ChartJS.register(
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend,
)

const props = defineProps({
  criteriaLabels: {
    type: Array,
    default: () => [],
  },
  companyRadar: {
    type: Object,
    default: () => ({ label: '전사 평균', scores: [] }),
  },
  selectedTeam: {
    type: Object,
    default: null,
  },
  allTeams: {
    type: Array,
    default: () => [],
  },
})

const chartData = computed(() => {
  const datasets = []

  // 1. Company average dataset
  if (props.companyRadar && props.companyRadar.scores?.length > 0) {
    datasets.push({
      label: props.companyRadar.label || '전사 평균',
      data: props.companyRadar.scores,
      backgroundColor: 'rgba(148, 163, 184, 0.15)',
      borderColor: '#94a3b8',
      borderWidth: 2,
      borderDash: [4, 4],
      pointBackgroundColor: '#94a3b8',
      pointBorderColor: '#ffffff',
      pointHoverBackgroundColor: '#64748b',
      pointRadius: 4,
    })
  }

  // 2. Selected team dataset
  if (props.selectedTeam && props.selectedTeam.scores?.length > 0) {
    datasets.push({
      label: `${props.selectedTeam.team_name} (평균)`,
      data: props.selectedTeam.scores,
      backgroundColor: 'rgba(32, 107, 196, 0.25)',
      borderColor: '#206bc4',
      borderWidth: 2.5,
      pointBackgroundColor: '#206bc4',
      pointBorderColor: '#ffffff',
      pointHoverBackgroundColor: '#1a569d',
      pointRadius: 5,
      pointHoverRadius: 7,
    })
  } else if (props.allTeams?.length > 0) {
    // If no team is selected specifically, show distinct teams
    const colors = [
      { bg: 'rgba(32, 107, 196, 0.2)', border: '#206bc4' },
      { bg: 'rgba(47, 179, 68, 0.2)', border: '#2fb344' },
      { bg: 'rgba(245, 159, 0, 0.2)', border: '#f59f00' },
      { bg: 'rgba(112, 72, 232, 0.2)', border: '#7048e8' },
    ]
    props.allTeams.forEach((t, idx) => {
      const palette = colors[idx % colors.length]
      datasets.push({
        label: t.team_name,
        data: t.scores,
        backgroundColor: palette.bg,
        borderColor: palette.border,
        borderWidth: 2,
        pointBackgroundColor: palette.border,
        pointRadius: 4,
      })
    })
  }

  return {
    labels: props.criteriaLabels.length > 0 ? props.criteriaLabels : ['항목 1', '항목 2', '항목 3'],
    datasets,
  }
})

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  scales: {
    r: {
      angleLines: {
        color: '#e2e8f0',
      },
      grid: {
        color: '#e2e8f0',
      },
      pointLabels: {
        font: {
          size: 12,
          weight: '600',
          family: 'inherit',
        },
        color: '#1e293b',
      },
      suggestedMin: 0,
      suggestedMax: 5,
      ticks: {
        stepSize: 1,
        backdropColor: 'transparent',
        color: '#64748b',
        font: {
          size: 10,
        },
      },
    },
  },
  plugins: {
    legend: {
      position: 'top',
      labels: {
        boxWidth: 14,
        font: {
          size: 12,
          weight: '500',
        },
        color: '#334155',
      },
    },
    tooltip: {
      backgroundColor: '#0f172a',
      titleFont: { size: 12, weight: 'bold' },
      bodyFont: { size: 12 },
      padding: 10,
      cornerRadius: 8,
      callbacks: {
        label: function (context) {
          return ` ${context.dataset.label}: ${Number(context.raw).toFixed(2)} / 5.00점`
        },
      },
    },
  },
}
</script>

<template>
  <div class="team-radar-wrapper">
    <div v-if="criteriaLabels.length === 0" class="empty-radar text-center py-5 text-secondary">
      평가 항목 데이터가 없습니다.
    </div>
    <div v-else class="radar-chart-container" style="position: relative; height: 320px; width: 100%;">
      <Radar :data="chartData" :options="chartOptions" />
    </div>
  </div>
</template>

<style scoped>
.team-radar-wrapper {
  width: 100%;
}
.radar-chart-container {
  margin: 0 auto;
}
</style>

