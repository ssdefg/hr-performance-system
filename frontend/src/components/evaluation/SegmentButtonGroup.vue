<script setup>
const props = defineProps({
  modelValue: { type: Number, default: null },
  disabled: { type: Boolean, default: false },
})
const emit = defineEmits(['update:modelValue'])
const choices = [
  { score: 1, label: '매우 미흡' },
  { score: 2, label: '미흡' },
  { score: 3, label: '보통' },
  { score: 4, label: '우수' },
  { score: 5, label: '매우 우수' },
]
</script>

<template>
  <div class="score-segments" role="group" aria-label="1점부터 5점까지 평가 선택">
    <button
      v-for="choice in choices"
      :key="choice.score"
      class="score-segment"
      :class="modelValue === choice.score ? 'score-segment-selected' : ''"
      type="button"
      :disabled="disabled"
      :aria-pressed="modelValue === choice.score"
      :aria-label="`${choice.score}점 ${choice.label}`"
      @click="emit('update:modelValue', choice.score)"
    >
      <span class="score-segment-number">{{ choice.score }}</span>
      <span class="score-segment-label">{{ choice.label }}</span>
    </button>
  </div>
</template>