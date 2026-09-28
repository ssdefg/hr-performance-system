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
  chartData: {
    type: Object,
    default: () => ({ labels: [], datasets: [] }),
  },
  selectedTeam: {
    type: String,
    default: null,
  },
})

const emit = defineEmits(['select-team'])

const data = computed(() => {
  const labels = props.chartData?.labels || []
  const rawDatasets = props.chartData?.datasets || []

  // If a team is selected, emphasize that dataset line
  const datasets = rawDatasets.map((ds) => {
    if (props.selectedTeam) {
      if (ds.label === props.selectedTeam) {
        return {
          ...ds,
          borderWidth: 3,
          pointRadius: 5,
        }
      } else if (ds.label !== '전사 평균') {
        return {
          ...ds,
          borderWidth: 1,
          pointRadius: 2,
        }
      }
    }
    return ds
  })

  return {
    labels,
    datasets,
  }
})

const options = {
  responsive: true,
  maintainAspectRatio: false,
  onClick: (event, elements, chart) => {
    if (elements && elements.length > 0) {
      const datasetIndex = elements[0].datasetIndex
      const teamName = chart.data.datasets[datasetIndex]?.label
      if (teamName && teamName !== '전사 평균') {
        emit('select-team', teamName)
      } else {
        emit('select-team', null)
      }
    } else {
      emit('select-team', null)
    }
  },
  onHover: (event, elements) => {
    if (event?.native?.target) {
      event.native.target.style.cursor = elements && elements.length > 0 ? 'pointer' : 'default'
    }
  },
  scales: {
    r: {
      angleLines: { color: '#e2e8f0' },
      grid: { color: '#e2e8f0' },
      pointLabels: {
        font: { size: 11, weight: '600' },
        color: '#1e293b',
      },
      suggestedMin: 0,
      suggestedMax: 5,
      ticks: {
        stepSize: 1,
        backdropColor: 'transparent',
        color: '#64748b',
        font: { size: 10 },
      },
    },
  },
  plugins: {
    legend: {
      position: 'top',
      onClick: (e, legendItem, legend) => {
        const teamName = legendItem.text
        if (teamName && teamName !== '전사 평균') {
          emit('select-team', teamName)
        } else {
          emit('select-team', null)
        }
      },
      labels: {
        boxWidth: 12,
        font: { size: 11, weight: '500' },
        color: '#334155',
      },
    },
    tooltip: {
      backgroundColor: '#0f172a',
      padding: 10,
      cornerRadius: 8,
      callbacks: {
        label: (context) => ` ${context.dataset.label}: ${Number(context.raw).toFixed(2)}점 (클릭 시 필터)`,
      },
    },
  },
}
</script>

<template>
  <div class="chart-container" style="position: relative; height: 260px; width: 100%;">
    <div v-if="!chartData?.labels?.length" class="text-center py-5 text-secondary">
      역량 평가 데이터가 없습니다.
    </div>
    <Radar v-else :data="data" :options="options" />
  </div>
</template>

