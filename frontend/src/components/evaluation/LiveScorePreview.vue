<script setup>
import { computed } from 'vue'

const props = defineProps({
  criteria: { type: Array, required: true },
  scores: { type: Object, required: true },
  completed: { type: Boolean, default: false },
  saving: { type: Boolean, default: false },
  isSubmitted: { type: Boolean, default: false },
})
const emit = defineEmits(['submit'])
const totalScore = computed(() => props.criteria.reduce((total, item) => {
  const score = props.scores[item.id]
  return total + (score ? Number(score) / 5 * Number(item.weight) : 0)
}, 0))
const answered = computed(() => props.criteria.filter((item) => props.scores[item.id]).length)
const progress = computed(() => props.criteria.length ? Math.round(answered.value / props.criteria.length * 100) : 0)
</script>

<template>
  <aside class="live-score-panel card-enterprise" aria-label="실시간 평가 점수 프리뷰">
    <div class="live-score-header">
      <span class="eyebrow mb-1">LIVE SCORE PREVIEW</span>
      <span class="badge bg-blue-lt">{{ answered }} / {{ criteria.length }} 완료</span>
    </div>
    <div class="live-score-total">
      <strong>{{ totalScore.toFixed(2) }}</strong><span>/ 100점</span>
    </div>
    <div class="progress progress-sm mb-3">
      <div class="progress-bar" :style="{ width: `${progress}%` }" role="progressbar" :aria-valuenow="progress" aria-valuemin="0" aria-valuemax="100"></div>
    </div>
    <div class="live-score-progress-label">{{ answered }} / {{ criteria.length }}개 항목 입력 완료 · {{ progress }}%</div>
    <div class="live-score-breakdown">
      <div v-for="item in criteria" :key="item.id" class="live-score-row">
        <span>{{ item.name }} <span class="text-secondary">({{ item.weight }}%)</span></span>
        <strong>{{ scores[item.id] ? `${(scores[item.id] / 5 * item.weight).toFixed(2)}점` : '미입력' }}</strong>
      </div>
    </div>
    <div class="live-score-actions mt-3">
      <button
        class="btn w-100"
        :class="isSubmitted ? 'btn-success' : 'btn-primary'"
        type="button"
        :disabled="saving || !completed"
        @click="emit('submit')"
      >
        <span v-if="saving">{{ isSubmitted ? '수정 저장 중...' : '저장 중...' }}</span>
        <span v-else>{{ isSubmitted ? '✏️ 평가 수정 저장' : '평가 제출' }}</span>
      </button>
    </div>
    <div v-if="isSubmitted" class="text-secondary small text-center mt-2">
      💡 제출된 평가는 점수를 변경한 후 언제든지 다시 수정 저장할 수 있습니다.
    </div>
  </aside>
</template>