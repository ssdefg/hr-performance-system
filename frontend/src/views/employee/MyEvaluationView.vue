<script setup>
import { computed, onMounted, ref } from 'vue'
import client from '../../api/client'

const result = ref(null)
const loading = ref(true)
const error = ref('')
const teamBonus = computed(() => Number(result.value?.team_bonus || 0))

onMounted(async () => {
  try {
    result.value = (await client.get('/evaluations/my-review/')).data
  } catch (requestError) {
    error.value = requestError.response?.data?.detail || '평가 결과를 불러오지 못했습니다.'
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="admin-page-heading"><div><p class="eyebrow">MY PERFORMANCE</p><h2 class="page-title">내 평가 결과</h2><p class="text-secondary mb-0">제출이 완료된 본인 평가만 조회할 수 있습니다.</p></div></div>
  <div v-if="error" class="alert alert-danger" role="alert">{{ error }}</div>
  <div v-else-if="loading" class="placeholder placeholder-glow w-100" style="height: 180px"></div>
  <section v-else-if="result?.status === 'IN_PROGRESS'" class="review-pending-panel card-enterprise" role="status"><span class="review-pending-mark">…</span><div><h3>평가 진행 중</h3><p class="text-secondary mb-0">{{ result.message }}</p></div></section>
  <template v-else-if="result">
    <section class="final-score-panel card-enterprise"><div><span class="eyebrow">FINAL SCORE</span><div class="final-score-number">{{ Number(result.final_score).toFixed(2) }}<span>점</span></div><div class="score-equation"><span>개인 평가 {{ Number(result.raw_score).toFixed(2) }}점</span><span>+</span><span>팀 보너스 +{{ teamBonus.toFixed(1) }}점</span></div></div><div class="final-score-status"><span class="badge bg-green-lt">제출 완료</span><span v-if="result.is_capped" class="badge bg-indigo-lt">상한 적용</span><div class="text-secondary small mt-2">평가자 {{ result.evaluator_name }}</div></div></section>
    <section class="member-list-section"><div class="section-heading"><div><h3 class="section-title">항목별 평가 내역</h3><p class="text-secondary mb-0">항목 점수와 가중치 반영 결과</p></div><span class="badge bg-blue-lt">{{ result.scores.length }}개 항목</span></div>
      <div class="card card-enterprise"><div class="table-responsive"><table class="table table-vcenter card-table"><thead><tr><th>평가 항목</th><th>기준 설명</th><th>가중치</th><th>부여 점수</th><th>환산 점수</th></tr></thead><tbody><tr v-for="item in result.scores" :key="item.criteria_id"><td class="fw-semibold">{{ item.name }}</td><td class="text-secondary">{{ item.description || '—' }}</td><td>{{ item.weight }}%</td><td>{{ item.score }} / 5점</td><td class="fw-bold">{{ Number(item.earned_score).toFixed(2) }}점</td></tr></tbody></table></div></div>
    </section>
  </template>
</template>