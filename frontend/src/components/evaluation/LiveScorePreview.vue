<script setup>
import { computed } from 'vue'

const props = defineProps({
  criteria: { type: Array, required: true },
  scores: { type: Object, required: true },
  completed: { type: Boolean, default: false },
  saving: { type: Boolean, default: false },
  locked: { type: Boolean, default: false },
})
const emit = defineEmits(['save-draft', 'submit'])
const totalScore = computed(() => props.criteria.reduce((total, item) => {
  const score = props.scores[item.id]
  return total + (score ? Number(score) / 5 * Number(item.weight) : 0)
}, 0))
const answered = computed(() => props.criteria.filter((item) => props.scores[item.id]).length)
const progress = computed(() => props.criteria.length ? Math.round(answered.value / props.criteria.length * 100) : 0)
</script>

<template>
  <aside class="live-score-panel card-enterprise" aria-label="실시간 평가 점수 프리뷰">
    <div class="live-score-header"><span class="eyebrow mb-1">LIVE SCORE PREVIEW</span><span class="badge bg-blue-lt">{{ answered }} / {{ criteria.length }} 완료</span></div>
    <div class="live-score-total"><strong>{{ totalScore.toFixed(2) }}</strong><span>/ 100점</span></div>
    <div class="progress progress-sm mb-3"><div class="progress-bar" :style="{ width: `${progress}%` }" role="progressbar" :aria-valuenow="progress" aria-valuemin="0" aria-valuemax="100"></div></div>
    <div class="live-score-progress-label">{{ answered }} / {{ criteria.length }}개 항목 입력 완료 · {{ progress }}%</div>
    <div class="live-score-breakdown"><div v-for="item in criteria" :key="item.id" class="live-score-row"><span>{{ item.name }} <span class="text-secondary">({{ item.weight }}%)</span></span><strong>{{ scores[item.id] ? `${(scores[item.id] / 5 * item.weight).toFixed(2)}점` : '미입력' }}</strong></div></div>
    <div v-if="locked" class="alert alert-success mb-0 mt-3">최종 제출이 완료되어 평가가 잠겼습니다.</div>
    <div v-else class="live-score-actions"><button class="btn btn-outline-primary" type="button" :disabled="saving" @click="emit('save-draft')">{{ saving ? '저장 중...' : '임시 저장' }}</button><button class="btn btn-primary" type="button" :disabled="saving || !completed" @click="emit('submit')">최종 제출</button></div>
  </aside>
</template>