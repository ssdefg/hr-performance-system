<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { IconSparkles, IconThumbUp, IconBulb, IconMessageDots, IconCheck } from '@tabler/icons-vue'
import SegmentButtonGroup from '../../components/evaluation/SegmentButtonGroup.vue'
import LiveScorePreview from '../../components/evaluation/LiveScorePreview.vue'
import client, { getErrorMessage } from '../../api/client'

const route = useRoute()
const employeeId = computed(() => decodeURIComponent(route.params.employeeId))
const review = ref(null)
const criteria = ref([])
const scores = ref({})
const selectedStrengths = ref([])
const selectedImprovements = ref([])
const managerComment = ref('')

const loading = ref(true)
const saving = ref(false)
const error = ref('')
const notice = ref('')

const strengthOptions = [
  '높은 책임감',
  '문제 해결력',
  '적극적인 소통',
  '빠른 일정 준수',
  '도전 정신',
  '탁월한 전문성',
  '유연한 팀워크',
  '철저한 품질 관리',
]

const improvementOptions = [
  '문서화 보완',
  '협업 확대',
  '주도적 의견 개진',
  '일정 예측도 개선',
  '도메인 지식 확장',
  '공유 및 피드백 전파',
  '우선순위 조율',
]

const complete = computed(() => criteria.value.length > 0 && criteria.value.every((item) => scores.value[item.id]))
const isSubmitted = computed(() => review.value?.status === 'SUBMITTED')
const weightTotal = computed(() => criteria.value.reduce((total, item) => total + item.weight, 0))

function toggleStrength(tag) {
  if (selectedStrengths.value.includes(tag)) {
    selectedStrengths.value = selectedStrengths.value.filter((t) => t !== tag)
  } else {
    selectedStrengths.value.push(tag)
  }
}

function toggleImprovement(tag) {
  if (selectedImprovements.value.includes(tag)) {
    selectedImprovements.value = selectedImprovements.value.filter((t) => t !== tag)
  } else {
    selectedImprovements.value.push(tag)
  }
}

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
    selectedStrengths.value = Array.isArray(review.value.strengths) ? [...review.value.strengths] : []
    selectedImprovements.value = Array.isArray(review.value.improvements) ? [...review.value.improvements] : []
    managerComment.value = review.value.comment || ''

    if (weightTotal.value !== 100) error.value = '가중치 합계가 100이 아니므로 평가를 진행할 수 없습니다.'
  } catch (requestError) {
    error.value = getErrorMessage(requestError, '평가 정보를 불러오지 못했습니다.')
  } finally {
    loading.value = false
  }
}

function scorePayload() {
  return {
    scores: criteria.value.filter((item) => scores.value[item.id]).map((item) => ({ criteria_id: item.id, score: scores.value[item.id] })),
    strengths: selectedStrengths.value,
    improvements: selectedImprovements.value,
    comment: managerComment.value,
  }
}

async function submitOrUpdateReview() {
  if (!complete.value) return
  saving.value = true
  error.value = ''
  notice.value = ''
  const isEditing = isSubmitted.value
  try {
    review.value = (await client.post(`/evaluations/reviews/${encodeURIComponent(employeeId.value)}/submit/`, scorePayload())).data
    scores.value = Object.fromEntries(review.value.scores.map((item) => [item.criteria_id, item.score]))
    selectedStrengths.value = Array.isArray(review.value.strengths) ? [...review.value.strengths] : []
    selectedImprovements.value = Array.isArray(review.value.improvements) ? [...review.value.improvements] : []
    managerComment.value = review.value.comment || ''
    notice.value = isEditing ? '평가 점수 및 피드백이 성공적으로 수정되었습니다.' : '평가 제출이 완료되었습니다.'
  } catch (requestError) {
    error.value = getErrorMessage(requestError, '평가를 저장하지 못했습니다.')
  } finally {
    saving.value = false
  }
}

onMounted(loadReview)
</script>

<template>
  <div class="admin-page-heading">
    <div>
      <p class="eyebrow">TEAM REVIEW</p>
      <h2 class="page-title">{{ isSubmitted ? '팀원 평가 수정' : '팀원 평가 작성' }}</h2>
      <p v-if="review" class="text-secondary mb-0">{{ review.employee_name }} · {{ review.employee_id }} · {{ review.team_name }}</p>
    </div>
    <RouterLink to="/manager" class="btn btn-outline-secondary">팀원 목록</RouterLink>
  </div>
  <div v-if="loading" class="placeholder placeholder-glow w-100" style="height: 180px"></div>
  <template v-else-if="review">
    <div v-if="error" class="alert alert-danger" role="alert">{{ error }}</div>
    <div v-if="notice" class="alert alert-success" role="status">{{ notice }}</div>
    <div v-if="isSubmitted" class="alert alert-info d-flex align-items-center justify-content-between" role="status">
      <div>
        <strong>📌 평가 완료 상태</strong>: 점수 및 피드백을 변경한 후 우측 하단의 <strong>[평가 수정 저장]</strong> 버튼을 누르면 언제든지 점수가 갱신됩니다.
      </div>
      <span class="badge bg-green text-white">제출 완료됨</span>
    </div>

    <div class="evaluation-layout">
      <!-- 좌측: 정량 점수 + 정성 피드백 폼 -->
      <section class="criteria-list">
        <!-- 1. 정량 역량 평가 항목들 -->
        <article v-for="(item, index) in criteria" :key="item.id" class="criteria-review-card card-enterprise mb-3">
          <div class="criteria-review-heading">
            <div>
              <span class="eyebrow">CRITERION {{ String(index + 1).padStart(2, '0') }}</span>
              <h3>{{ item.name }}</h3>
            </div>
            <span class="badge bg-blue-lt">가중치 {{ item.weight }}%</span>
          </div>
          <p class="text-secondary">{{ item.description || '이 항목에 대한 평가를 선택해 주세요.' }}</p>
          <SegmentButtonGroup v-model="scores[item.id]" :disabled="weightTotal !== 100" />
        </article>
        <div v-if="!criteria.length && !error" class="alert alert-warning">활성 평가 항목이 없습니다.</div>

        <!-- 2. 정성 피드백 섹션 (선택형 태그 & 총평) -->
        <article class="feedback-card card card-enterprise p-4 mt-4">
          <div class="d-flex align-items-center gap-2 mb-3">
            <span class="score-kpi-icon bg-azure-lt p-1 rounded-2"><IconSparkles :size="18" /></span>
            <div>
              <h3 class="card-title mb-0 fs-3">정성 피드백 및 코멘트</h3>
              <p class="text-secondary small mb-0">팀원의 성장을 위한 주요 강점, 개선 제언 및 총평을 남겨주세요. (선택 사항)</p>
            </div>
          </div>

          <!-- 주요 강점 선택 태그 칩 -->
          <div class="feedback-group mb-4">
            <label class="form-label fw-bold d-flex align-items-center gap-1">
              <IconThumbUp :size="16" class="text-primary" /> 주요 강점 (복수 선택 가능)
            </label>
            <div class="d-flex flex-wrap gap-2 mt-1">
              <button
                v-for="tag in strengthOptions"
                :key="tag"
                type="button"
                class="btn btn-sm tag-chip-btn"
                :class="selectedStrengths.includes(tag) ? 'btn-primary shadow-sm' : 'btn-outline-secondary'"
                @click="toggleStrength(tag)"
              >
                <IconCheck v-if="selectedStrengths.includes(tag)" :size="14" class="me-1" />
                {{ tag }}
              </button>
            </div>
          </div>

          <!-- 개선 제언 선택 태그 칩 -->
          <div class="feedback-group mb-4">
            <label class="form-label fw-bold d-flex align-items-center gap-1">
              <IconBulb :size="16" class="text-warning" /> 개선 및 개발 제언 (복수 선택 가능)
            </label>
            <div class="d-flex flex-wrap gap-2 mt-1">
              <button
                v-for="tag in improvementOptions"
                :key="tag"
                type="button"
                class="btn btn-sm tag-chip-btn"
                :class="selectedImprovements.includes(tag) ? 'btn-warning text-dark shadow-sm' : 'btn-outline-secondary'"
                @click="toggleImprovement(tag)"
              >
                <IconCheck v-if="selectedImprovements.includes(tag)" :size="14" class="me-1" />
                {{ tag }}
              </button>
            </div>
          </div>

          <!-- 매니저 총평 텍스트에어리어 -->
          <div class="feedback-group mb-2">
            <label class="form-label fw-bold d-flex align-items-center gap-1" for="manager-comment">
              <IconMessageDots :size="16" class="text-success" /> 매니저 총평 및 격려의 말
            </label>
            <textarea
              id="manager-comment"
              v-model.trim="managerComment"
              class="form-control"
              rows="4"
              placeholder="이번 평가 기간 동안 수고한 팀원에게 따뜻한 격려와 향후 성장을 위한 조언을 자유롭게 작성해 주세요."
            ></textarea>
          </div>
        </article>
      </section>

      <!-- 우측: 실시간 점수 프리뷰 -->
      <LiveScorePreview
        :criteria="criteria"
        :scores="scores"
        :completed="complete && weightTotal === 100"
        :saving="saving"
        :is-submitted="isSubmitted"
        @submit="submitOrUpdateReview"
      />
    </div>
  </template>
  <div v-else-if="error" class="alert alert-danger" role="alert">{{ error }}</div>
</template>

<style scoped>
.tag-chip-btn {
  border-radius: 20px;
  padding: 0.35rem 0.85rem;
  font-size: 0.8125rem;
  transition: all 0.15s ease-in-out;
}
</style>