<script setup>
import { computed, onMounted, ref } from 'vue'
import { IconArrowRight, IconEdit, IconPencil } from '@tabler/icons-vue'
import client from '../../api/client'

const data = ref(null)
const loading = ref(true)
const error = ref('')
const progress = computed(() => data.value?.member_count ? Math.round(data.value.submitted_count / data.value.member_count * 100) : 0)

onMounted(async () => {
  try {
    data.value = (await client.get('/evaluations/team-members/')).data
  } catch (requestError) {
    error.value = requestError.response?.data?.detail || '담당 팀원 목록을 불러오지 못했습니다.'
  } finally {
    loading.value = false
  }
})

function statusLabel(status) {
  return { NOT_STARTED: '작성 전', DRAFT: '작성 중', SUBMITTED: '평가 완료' }[status] || status
}
function statusClass(status) {
  return { NOT_STARTED: 'bg-secondary-lt', DRAFT: 'bg-yellow-lt', SUBMITTED: 'bg-green-lt' }[status]
}
</script>

<template>
  <div class="admin-page-heading">
    <div>
      <p class="eyebrow">MANAGER WORKSPACE</p>
      <h2 class="page-title">팀원 성과 평가</h2>
      <p class="text-secondary mb-0">담당 팀 구성원에 대한 역량 평가를 작성하고 필요 시 언제든지 수정할 수 있습니다.</p>
    </div>
  </div>
  <div v-if="error" class="alert alert-danger" role="alert">{{ error }}</div>
  <div v-if="loading" class="placeholder placeholder-glow w-100" style="height: 120px"></div>
  <template v-else-if="data">
    <section class="team-progress-panel card-enterprise">
      <div>
        <span class="eyebrow">MY TEAM</span>
        <h3>{{ data.team_name }}</h3>
        <p class="text-secondary mb-0">{{ data.submitted_count }}명 완료 · 전체 {{ data.member_count }}명</p>
      </div>
      <div class="team-progress-meter">
        <strong>{{ progress }}%</strong>
        <div class="progress progress-sm">
          <div class="progress-bar" :style="{ width: `${progress}%` }"></div>
        </div>
      </div>
    </section>
    <section class="member-list-section">
      <div class="section-heading">
        <div>
          <h3 class="section-title">평가 대상자 목록</h3>
          <p class="text-secondary mb-0">제출 완료된 평가는 언제든지 다시 열어 수정할 수 있습니다.</p>
        </div>
        <span class="badge bg-blue-lt">{{ data.member_count }}명</span>
      </div>
      <div class="card card-enterprise">
        <div class="table-responsive">
          <table class="table table-vcenter card-table">
            <thead>
              <tr>
                <th>사원</th>
                <th>사번</th>
                <th>평가 상태</th>
                <th>평가 원점수</th>
                <th class="text-end">작업</th>
              </tr>
            </thead>
            <tbody v-if="data.members.length">
              <tr v-for="member in data.members" :key="member.employee_id">
                <td>
                  <span class="member-avatar">{{ member.name.slice(0, 1) }}</span>
                  <span class="fw-semibold ms-2">{{ member.name }}</span>
                </td>
                <td class="text-secondary">{{ member.employee_id }}</td>
                <td>
                  <span class="badge" :class="statusClass(member.review_status)">{{ statusLabel(member.review_status) }}</span>
                </td>
                <td>
                  <strong>{{ member.raw_score === null ? '—' : `${Number(member.raw_score).toFixed(2)}점` }}</strong>
                </td>
                <td class="text-end">
                  <RouterLink
                    class="btn btn-sm"
                    :class="member.review_status === 'SUBMITTED' ? 'btn-outline-success' : 'btn-primary'"
                    :to="`/manager/evaluations/${encodeURIComponent(member.employee_id)}`"
                  >
                    <span v-if="member.review_status === 'SUBMITTED'" class="d-inline-flex align-items-center gap-1">
                      <IconPencil :size="14" /> 평가 수정
                    </span>
                    <span v-else class="d-inline-flex align-items-center gap-1">
                      <IconEdit :size="14" /> 평가 작성
                    </span>
                  </RouterLink>
                </td>
              </tr>
            </tbody>
            <tbody v-else>
              <tr>
                <td colspan="5" class="text-center text-secondary py-5">담당 팀에 평가 대상 직원이 없습니다.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </section>
  </template>
</template>