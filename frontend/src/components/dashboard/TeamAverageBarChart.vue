<script setup>
import { computed } from 'vue'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js'
import { Bar } from 'vue-chartjs'

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
)

const props = defineProps({
  chartData: {
    type: Object,
    default: () => ({ labels: [], data: [] }),
  },
  selectedTeam: {
    type: String,
    default: null,
  },
})

const emit = defineEmits(['select-team'])

const data = computed(() => {
  return {
    labels: props.chartData?.labels || [],
    datasets: [
      {
        label: '팀 평균 최종 점수',
        data: props.chartData?.data || [],
        backgroundColor: (props.chartData?.labels || []).map((label, idx) => {
          if (props.selectedTeam && props.selectedTeam !== label) {
            return 'rgba(203, 213, 225, 0.4)'
          }
          const colors = [
            'rgba(32, 107, 196, 0.85)',
            'rgba(47, 179, 68, 0.85)',
            'rgba(245, 159, 0, 0.85)',
            'rgba(112, 72, 232, 0.85)',
            'rgba(214, 57, 57, 0.85)',
          ]
          return colors[idx % colors.length]
        }),
        borderColor: (props.chartData?.labels || []).map((label, idx) => {
          if (props.selectedTeam && props.selectedTeam !== label) {
            return '#cbd5e1'
          }
          const borders = [
            '#206bc4',
            '#2fb344',
            '#f59f00',
            '#7048e8',
            '#d63939',
          ]
          return borders[idx % borders.length]
        }),
        borderWidth: (props.chartData?.labels || []).map((label) =>
          props.selectedTeam === label ? 3 : 1.5
        ),
        borderRadius: 6,
        barThickness: 32,
      },
    ],
  }
})

const options = {
  responsive: true,
  maintainAspectRatio: false,
  onClick: (event, elements, chart) => {
    if (elements && elements.length > 0) {
      const index = elements[0].index
      const teamName = chart.data.labels[index]
      emit('select-team', teamName)
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
    y: {
      beginAtZero: true,
      suggestedMax: 100,
      grid: {
        color: '#f1f5f9',
      },
      ticks: {
        stepSize: 20,
        color: '#64748b',
        callback: (val) => `${val}점`,
      },
    },
    x: {
      grid: {
        display: false,
      },
      ticks: {
        color: '#334155',
        font: {
          weight: '600',
        },
      },
    },
  },
  plugins: {
    legend: {
      display: false,
    },
    tooltip: {
      backgroundColor: '#0f172a',
      padding: 10,
      cornerRadius: 8,
      callbacks: {
        label: (context) => ` 평균 점수: ${Number(context.raw).toFixed(2)}점 (클릭 시 드릴다운 필터)`,
      },
    },
  },
}
</script>

<template>
  <div class="chart-container" style="position: relative; height: 260px; width: 100%;">
    <div v-if="!chartData?.labels?.length" class="text-center py-5 text-secondary">
      팀 점수 데이터가 없습니다.
    </div>
    <Bar v-else :data="data" :options="options" />
  </div>
</template>

