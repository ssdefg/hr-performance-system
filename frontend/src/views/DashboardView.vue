<script setup>
import { onMounted, ref } from 'vue'
import client from '../api/client'

const apiStatus = ref('확인 중')
const apiAvailable = ref(false)

onMounted(async () => {
  try {
    await client.get('/health/')
    apiStatus.value = 'API 연결됨'
    apiAvailable.value = true
  } catch {
    apiStatus.value = 'API 연결 대기'
  }
})

const metrics = [
  { label: '전체 대상자', value: '248', note: '전사 구성원', color: 'blue' },
  { label: '평가 완료율', value: '72%', note: '179명 제출 완료', color: 'green' },
  { label: '전사 평균 점수', value: '84.6', note: '100점 기준', color: 'orange' },
  { label: '팀 보너스 부여', value: '12팀', note: '전체 16개 팀', color: 'purple' },
]
</script>

<template>
  <div class="dashboard-heading">
    <div>
      <p class="eyebrow">PERFORMANCE CYCLE · 2026 H1</p>
      <h2 class="page-title">성과 평가 현황</h2>
      <p class="text-secondary mb-0">조직 전체의 평가 진행 상황을 확인합니다.</p>
    </div>
    <button class="btn btn-primary" type="button" disabled>평가 데이터 준비 중</button>
  </div>

  <section class="metric-grid" aria-label="평가 주요 지표">
    <article v-for="metric in metrics" :key="metric.label" class="metric-panel">
      <div class="metric-label">{{ metric.label }}</div>
      <div class="metric-value" :class="`text-${metric.color}`">{{ metric.value }}</div>
      <div class="metric-note">{{ metric.note }}</div>
    </article>
  </section>

  <section class="overview-section">
    <div class="section-heading">
      <div>
        <h3 class="section-title">평가 진행</h3>
        <p class="text-secondary mb-0">매니저 제출 현황</p>
      </div>
      <span class="badge" :class="apiAvailable ? 'bg-green-lt' : 'bg-secondary-lt'">{{ apiStatus }}</span>
    </div>
    <div class="empty-state">
      <div class="empty-state-mark">01</div>
      <div>
        <div class="fw-semibold">평가 데이터가 연결되면 진행 현황이 표시됩니다.</div>
        <div class="text-secondary small">백엔드 API 연결은 다음 개발 단계에서 구성합니다.</div>
      </div>
    </div>
  </section>
</template>