<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import SegmentButtonGroup from '../../components/evaluation/SegmentButtonGroup.vue'
import LiveScorePreview from '../../components/evaluation/LiveScorePreview.vue'
import client from '../../api/client'

const route = useRoute()
const employeeId = computed(() => decodeURIComponent(route.params.employeeId))
const review = ref(null)
const criteria = ref([])
const scores = ref({})
const loading = ref(true)
const saving = ref(false)
const error = ref('')
const notice = ref('')
const complete = computed(() => criteria.value.length > 0 && criteria.value.every((item) => scores.value[item.id]))
const locked = computed(() => review.value?.status === 'SUBMITTED')
const weightTotal = computed(() => criteria.value.reduce((total, item) => total + item.weight, 0))

async function loadReview() {
  loading.value = true
  error.value = ''
  try {
    const [criteriaResponse, reviewResponse] = await Promise.all([
      client.get('/evaluations/criteria/'),
      client.get(`/evaluations/reviews/${encodeURIComponent(employeeId.value)}/`),
    ])
    criteria.value = criteriaResponse.data.filter((item) => item.is_active)
    review.value = reviewResponse.data
    scores.value = Object.fromEntries(review.value.scores.map((item) => [item.criteria_id, item.score]))
    if (weightTotal.value !== 100) error.value = '가중치 합계가 100이 아니므로 평가를 진행할 수 없습니다.'
  } catch (requestError) {
    error.value = requestError.response?.data?.detail || '평가 정보를 불러오지 못했습니다.'
  } finally {
    loading.value = false
  }
}

function scorePayload() {
  return { scores: criteria.value.filter((item) => scores.value[item.id]).map((item) => ({ criteria_id: item.id, score: scores.value[item.id] })) }
}

async function saveDraft() {
  saving.value = true
  error.value = ''
  notice.value = ''
  try {
    review.value = (await client.post(`/evaluations/reviews/${encodeURIComponent(employeeId.value)}/draft/`, scorePayload())).data
    scores.value = Object.fromEntries(review.value.scores.map((item) => [item.criteria_id, item.score]))
    notice.value = '임시 저장되었습니다.'
  } catch (requestError) {
    error.value = requestError.response?.data?.weight?.[0] || requestError.response?.data?.detail || '평가를 저장하지 못했습니다.'
  } finally {
    saving.value = false
  }
}

async function submitReview() {
  if (!complete.value || locked.value) return
  if (!window.confirm('제출 후에는 평가 점수를 수정할 수 없습니다. 계속하시겠습니까?')) return
  saving.value = true
  error.value = ''
  notice.value = ''
  try {
    review.value = (await client.post(`/evaluations/reviews/${encodeURIComponent(employeeId.value)}/submit/`, scorePayload())).data
    scores.value = Object.fromEntries(review.value.scores.map((item) => [item.criteria_id, item.score]))
    notice.value = '평가 제출이 완료되었습니다. 수정이 잠겼습니다.'
  } catch (requestError) {
    error.value = requestError.response?.data?.scores?.[0] || requestError.response?.data?.weight?.[0] || requestError.response?.data?.detail || '평가를 제출하지 못했습니다.'
  } finally {
    saving.value = false
  }
}

onMounted(loadReview)
</script>

<template>
  <div class="admin-page-heading"><div><p class="eyebrow">TEAM REVIEW</p><h2 class="page-title">팀원 평가 작성</h2><p v-if="review" class="text-secondary mb-0">{{ review.employee_name }} · {{ review.employee_id }} · {{ review.team_name }}</p></div><RouterLink to="/manager" class="btn btn-outline-secondary">팀원 목록</RouterLink></div>
  <div v-if="loading" class="placeholder placeholder-glow w-100" style="height: 180px"></div>
  <template v-else-if="review">
    <div v-if="error" class="alert alert-danger" role="alert">{{ error }}</div><div v-if="notice" class="alert alert-success" role="status">{{ notice }}</div><div v-if="locked" class="alert alert-warning" role="status">제출 완료된 평가는 수정할 수 없습니다.</div>
    <div class="evaluation-layout"><section class="criteria-list"><article v-for="(item, index) in criteria" :key="item.id" class="criteria-review-card card-enterprise">
      <div class="criteria-review-heading"><div><span class="eyebrow">CRITERION {{ String(index + 1).padStart(2, '0') }}</span><h3>{{ item.name }}</h3></div><span class="badge bg-blue-lt">가중치 {{ item.weight }}%</span></div><p class="text-secondary">{{ item.description || '이 항목에 대한 평가를 선택해 주세요.' }}</p><SegmentButtonGroup v-model="scores[item.id]" :disabled="locked || weightTotal !== 100" />
    </article><div v-if="!criteria.length && !error" class="alert alert-warning">활성 평가 항목이 없습니다.</div></section>
      <LiveScorePreview :criteria="criteria" :scores="scores" :completed="complete && weightTotal === 100" :saving="saving" :locked="locked" @save-draft="saveDraft" @submit="submitReview" />
    </div>
  </template>
  <div v-else-if="error" class="alert alert-danger" role="alert">{{ error }}</div>
</template>