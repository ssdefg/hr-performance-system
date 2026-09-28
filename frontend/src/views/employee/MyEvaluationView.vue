<script setup>
import { computed, onMounted, ref } from 'vue'
import {
  IconPrinter,
  IconDownload,
  IconThumbUp,
  IconBulb,
  IconMessageDots,
  IconTarget,
  IconTrophy,
  IconSparkles,
} from '@tabler/icons-vue'
import client, { getErrorMessage } from '../../api/client'

const result = ref(null)
const loading = ref(true)
const error = ref('')
const teamBonus = computed(() => Number(result.value?.team_bonus || 0))

const roadmap = computed(() => {
  return result.value?.roadmap || null
})

const roadmapProgress = computed(() => {
  if (!roadmap.value || !result.value) return 100
  if (roadmap.value.current_grade === 'S') return 100
  const min = roadmap.value.current_tier_min || 0
  const max = roadmap.value.next_grade_score || 100
  const score = result.value.final_score || 0
  const span = max - min
  if (span <= 0) return 100
  const prog = ((score - min) / span) * 100
  return Math.min(100, Math.max(0, Math.round(prog)))
})

function gradeBadgeClass(grade) {
  switch (grade) {
    case 'S':
      return 'badge bg-purple text-white'
    case 'A':
      return 'badge bg-blue text-white'
    case 'B':
      return 'badge bg-green text-white'
    case 'C':
      return 'badge bg-orange text-white'
    case 'D':
      return 'badge bg-red text-white'
    default:
      return 'badge bg-secondary text-white'
  }
}

function printReport() {
  window.print()
}

onMounted(async () => {
  try {
    result.value = (await client.get('/evaluations/my-review/')).data
  } catch (requestError) {
    error.value = getErrorMessage(requestError, '평가 결과를 불러오지 못했습니다.')
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="print-container">
    <div class="admin-page-heading d-flex align-items-center justify-content-between flex-wrap gap-2 no-print">
      <div>
        <p class="eyebrow">MY PERFORMANCE</p>
        <h2 class="page-title">내 평가 결과 및 피드백</h2>
        <p class="text-secondary mb-0">최종 산출 등급, 항목별 평가 내역 및 매니저 정성 피드백을 확인합니다.</p>
      </div>
      <div v-if="result && result.status !== 'IN_PROGRESS'">
        <button class="btn btn-primary d-inline-flex align-items-center gap-2" type="button" @click="printReport">
          <IconPrinter :size="17" />
          <span>평가 결과표 (PDF) 다운로드 / 인쇄</span>
        </button>
      </div>
    </div>

    <!-- 인쇄용 전용 헤더 -->
    <div class="print-only-header d-none">
      <div class="d-flex justify-content-between align-items-center border-bottom pb-3 mb-4">
        <div>
          <h1 class="h2 mb-1 fw-bold text-dark">HR 인사 성과 평가 결과표</h1>
          <p class="text-muted small mb-0">공식 성과 평가 리포트</p>
        </div>
        <div class="text-end small text-muted">
          <div>피평가자: <strong>{{ result?.employee_name }}</strong> ({{ result?.employee_id }})</div>
          <div>소속: {{ result?.team_name || '미배정' }} · 평가자: {{ result?.evaluator_name }}</div>
        </div>
      </div>
    </div>

    <div v-if="error" class="alert alert-danger" role="alert">{{ error }}</div>
    <div v-else-if="loading" class="placeholder placeholder-glow w-100" style="height: 180px"></div>
    <section v-else-if="result?.status === 'IN_PROGRESS'" class="review-pending-panel card-enterprise" role="status">
      <span class="review-pending-mark">…</span>
      <div>
        <h3>평가 진행 중</h3>
        <p class="text-secondary mb-0">{{ result.message }}</p>
      </div>
    </section>

    <template v-else-if="result">
      <!-- 1. 최종 점수 및 등급 패널 -->
      <section class="final-score-panel card-enterprise mb-3">
        <div>
          <span class="eyebrow">FINAL SCORE & GRADE</span>
          <div class="d-flex align-items-baseline gap-3">
            <div class="final-score-number">{{ Number(result.final_score).toFixed(2) }}<span>점</span></div>
            <span v-if="result.grade" :class="gradeBadgeClass(result.grade)" class="fs-2 px-3 py-1 fw-bold rounded-2">
              {{ result.grade }}등급
            </span>
          </div>
          <div class="score-equation mt-2">
            <span>개인 평가 {{ Number(result.raw_score).toFixed(2) }}점</span>
            <span>+</span>
            <span>팀 보너스 +{{ teamBonus.toFixed(1) }}점</span>
          </div>
        </div>
        <div class="final-score-status text-end">
          <span class="badge bg-green-lt">제출 완료</span>
          <span v-if="result.is_capped" class="badge bg-indigo-lt ms-1">상한 적용</span>
          <div class="text-secondary small mt-2">소속 팀: {{ result.team_name || '미배정' }}</div>
          <div class="text-secondary small">평가 매니저: {{ result.evaluator_name }}</div>
        </div>
      </section>

      <!-- 2. 등급 달성 로드맵 & 갭(Gap) 바 -->
      <section v-if="roadmap" class="roadmap-card card card-enterprise p-3 mb-3">
        <div class="d-flex align-items-center justify-content-between mb-2">
          <div class="d-flex align-items-center gap-2">
            <span class="score-kpi-icon bg-azure-lt p-1 rounded-2 mb-0"><IconTarget :size="18" /></span>
            <div>
              <h4 class="card-title mb-0 fs-4">등급 달성 로드맵</h4>
              <p class="text-secondary small mb-0">상위 등급 달성을 위한 점수 현황 및 목표</p>
            </div>
          </div>
          <div>
            <span v-if="roadmap.next_grade" class="badge bg-blue-lt px-2 py-1">
              다음 목표: <strong>{{ roadmap.next_grade }}등급 ({{ roadmap.next_grade_score }}점)</strong>
            </span>
            <span v-else class="badge bg-purple-lt px-2 py-1 d-inline-flex align-items-center gap-1">
              <IconTrophy :size="14" /> <strong>최고 등급 달성</strong>
            </span>
          </div>
        </div>

        <div class="roadmap-message alert alert-info py-2 px-3 mb-2 rounded-3 border-0 bg-azure-lt">
          <div v-if="roadmap.next_grade" class="d-flex align-items-center gap-2">
            <IconSparkles :size="16" class="text-primary" />
            <span>
              현재 <strong>{{ Number(result.final_score).toFixed(2) }}점({{ roadmap.current_grade }}등급)</strong>입니다.
              다음 <strong>{{ roadmap.next_grade }}등급({{ roadmap.next_grade_score }}점)</strong>까지
              <strong class="text-primary">+{{ Number(roadmap.points_to_next).toFixed(2) }}점</strong> 남았습니다!
            </span>
          </div>
          <div v-else class="d-flex align-items-center gap-2 text-purple">
            <IconTrophy :size="18" />
            <span>축하합니다! 최고 등급인 <strong>S등급</strong>을 달성했습니다! 🏆</span>
          </div>
        </div>

        <div v-if="roadmap.next_grade" class="roadmap-progress-wrap mt-2">
          <div class="d-flex justify-content-between small text-secondary mb-1">
            <span>{{ roadmap.current_grade }}등급 기준 ({{ roadmap.current_tier_min }}점)</span>
            <span>달성율 {{ roadmapProgress }}%</span>
            <span>{{ roadmap.next_grade }}등급 목표 ({{ roadmap.next_grade_score }}점)</span>
          </div>
          <div class="progress progress-sm" style="height: 8px;">
            <div class="progress-bar bg-primary" :style="{ width: `${roadmapProgress}%` }"></div>
          </div>
        </div>
      </section>

      <!-- 3. 매니저 정성 피드백 & 총평 카드 -->
      <section class="feedback-result-card card card-enterprise p-4 mb-3">
        <div class="d-flex align-items-center gap-2 mb-3">
          <span class="score-kpi-icon bg-green-lt p-1 rounded-2 mb-0"><IconSparkles :size="18" /></span>
          <div>
            <h4 class="card-title mb-0 fs-3">매니저 정성 피드백</h4>
            <p class="text-secondary small mb-0">평가 매니저가 전달하는 성장 피드백 및 조언</p>
          </div>
        </div>

        <div class="row g-3">
          <!-- 주요 강점 -->
          <div class="col-md-6">
            <div class="p-3 bg-light rounded-3 h-100 border border-slate-100">
              <div class="fw-bold d-flex align-items-center gap-1 text-primary mb-2">
                <IconThumbUp :size="16" /> 주요 강점
              </div>
              <div v-if="result.strengths && result.strengths.length" class="d-flex flex-wrap gap-2">
                <span
                  v-for="s in result.strengths"
                  :key="s"
                  class="badge bg-blue-lt text-blue px-2 py-1 fs-6 rounded-pill"
                >
                  ✓ {{ s }}
                </span>
              </div>
              <div v-else class="text-secondary small">등록된 주요 강점 태그가 없습니다.</div>
            </div>
          </div>

          <!-- 개선 제언 -->
          <div class="col-md-6">
            <div class="p-3 bg-light rounded-3 h-100 border border-slate-100">
              <div class="fw-bold d-flex align-items-center gap-1 text-orange mb-2">
                <IconBulb :size="16" /> 개선 및 개발 제언
              </div>
              <div v-if="result.improvements && result.improvements.length" class="d-flex flex-wrap gap-2">
                <span
                  v-for="imp in result.improvements"
                  :key="imp"
                  class="badge bg-orange-lt text-orange px-2 py-1 fs-6 rounded-pill"
                >
                  ⚡ {{ imp }}
                </span>
              </div>
              <div v-else class="text-secondary small">등록된 개선 제언 태그가 없습니다.</div>
            </div>
          </div>
        </div>

        <!-- 매니저 총평 코멘트 -->
        <div class="manager-comment-box mt-3 p-3 bg-azure-lt rounded-3 border-0">
          <div class="fw-bold d-flex align-items-center gap-1 text-dark mb-2">
            <IconMessageDots :size="16" class="text-primary" /> 매니저 총평 및 격려
          </div>
          <p class="mb-0 text-dark" style="white-space: pre-line; line-height: 1.6;">
            {{ result.comment || '등록된 매니저 총평이 없습니다.' }}
          </p>
        </div>
      </section>

      <!-- 4. 항목별 평가 상세 내역 테이블 -->
      <section class="member-list-section mt-3">
        <div class="section-heading mb-2">
          <div>
            <h3 class="section-title">항목별 평가 세부 내역</h3>
            <p class="text-secondary small mb-0">평가 항목별 가중치 및 최종 환산 점수</p>
          </div>
          <span class="badge bg-blue-lt">{{ result.scores.length }}개 항목</span>
        </div>
        <div class="card card-enterprise">
          <div class="table-responsive">
            <table class="table table-vcenter card-table">
              <thead>
                <tr>
                  <th>평가 항목</th>
                  <th>기준 설명</th>
                  <th class="text-center">가중치</th>
                  <th class="text-center">부여 점수</th>
                  <th class="text-end">환산 점수</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in result.scores" :key="item.criteria_id">
                  <td class="fw-semibold">{{ item.name }}</td>
                  <td class="text-secondary">{{ item.description || '—' }}</td>
                  <td class="text-center">{{ item.weight }}%</td>
                  <td class="text-center">
                    <span class="badge bg-secondary-lt fw-bold">{{ item.score }} / 5점</span>
                  </td>
                  <td class="text-end fw-bold">{{ Number(item.earned_score).toFixed(2) }}점</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </section>
    </template>
  </div>
</template>

<style scoped>
@media print {
  .no-print {
    display: none !important;
  }
  .print-only-header {
    display: block !important;
  }
  .print-container {
    padding: 0 !important;
    background: white !important;
  }
  .card-enterprise {
    box-shadow: none !important;
    border: 1px solid #ddd !important;
    break-inside: avoid;
    margin-bottom: 1rem !important;
  }
}
</style>