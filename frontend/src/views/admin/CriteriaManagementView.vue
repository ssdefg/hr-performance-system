<script setup>
import { computed, onMounted, ref } from 'vue'
import { IconPlus, IconPencil, IconTrash } from '@tabler/icons-vue'
import client, { getErrorMessage } from '../../api/client'

const criteria = ref([])
const loading = ref(true)
const error = ref('')
const modalOpen = ref(false)
const saving = ref(false)
const editingId = ref(null)
const form = ref({ name: '', description: '', weight: 1, order: 1, is_active: true })
const totalWeight = computed(() => criteria.value.filter((item) => item.is_active).reduce((total, item) => total + Number(item.weight || 0), 0))
const isValid = computed(() => totalWeight.value === 100)

async function loadCriteria() {
  loading.value = true
  error.value = ''
  try {
    const { data } = await client.get('/evaluations/criteria/')
    criteria.value = data
  } catch (requestError) {
    error.value = getErrorMessage(requestError, '평가 항목을 불러오지 못했습니다.')
  } finally {
    loading.value = false
  }
}

function openCreate() {
  editingId.value = null
  form.value = { name: '', description: '', weight: 1, order: criteria.value.length + 1, is_active: true }
  modalOpen.value = true
}

function openEdit(item) {
  editingId.value = item.id
  form.value = { name: item.name, description: item.description, weight: item.weight, order: item.order, is_active: item.is_active }
  modalOpen.value = true
}

async function saveCriteria() {
  saving.value = true
  error.value = ''
  try {
    if (editingId.value) await client.patch(`/evaluations/criteria/${editingId.value}/`, form.value)
    else await client.post('/evaluations/criteria/', form.value)
    modalOpen.value = false
    await loadCriteria()
  } catch (requestError) {
    error.value = getErrorMessage(requestError, '평가 항목을 저장하지 못했습니다.')
  } finally {
    saving.value = false
  }
}

async function deleteCriteria(item) {
  if (!window.confirm(`'${item.name}' 평가 항목을 삭제할까요?`)) return
  try {
    await client.delete(`/evaluations/criteria/${item.id}/`)
    await loadCriteria()
  } catch {
    error.value = '평가 항목을 삭제하지 못했습니다.'
  }
}

async function move(item, offset) {
  const sorted = [...criteria.value].sort((first, second) => first.order - second.order)
  const index = sorted.findIndex((entry) => entry.id === item.id)
  const target = sorted[index + offset]
  if (!target) return
  try {
    await Promise.all([
      client.patch(`/evaluations/criteria/${item.id}/`, { order: target.order }),
      client.patch(`/evaluations/criteria/${target.id}/`, { order: item.order }),
    ])
    await loadCriteria()
  } catch {
    error.value = '평가 항목 순서를 변경하지 못했습니다.'
  }
}

onMounted(loadCriteria)
</script>

<template>
  <div class="admin-page-heading"><div><p class="eyebrow">SCORING FRAMEWORK</p><h2 class="page-title">평가 항목 관리</h2><p class="text-secondary mb-0">평가 기준과 항목별 가중치를 구성합니다.</p></div><button class="btn btn-primary" type="button" @click="openCreate"><IconPlus :size="18" /> 항목 추가</button></div>

  <section class="weight-status" :class="isValid ? 'weight-status-valid' : 'weight-status-invalid'" role="status" aria-live="polite">
    <div><div class="weight-status-title">가중치 합계 <strong>{{ totalWeight }} / 100</strong></div><div class="small">{{ isValid ? '완료 · 정상, 평가를 활성화할 수 있습니다.' : '가중치 합계가 100이어야 평가가 활성화됩니다.' }}</div></div>
    <span class="badge" :class="isValid ? 'bg-green-lt' : 'bg-red-lt'">{{ isValid ? '정상' : totalWeight < 100 ? '미달' : '초과' }}</span>
  </section>

  <div v-if="error" class="alert alert-danger" role="alert">{{ error }}</div>
  <section class="card card-enterprise"><div class="table-responsive"><table class="table table-vcenter card-table">
    <thead><tr><th class="w-1">순서</th><th>평가 항목</th><th>설명</th><th>가중치</th><th>상태</th><th class="w-1">관리</th></tr></thead>
    <tbody v-if="!loading && criteria.length"><tr v-for="item in [...criteria].sort((first, second) => first.order - second.order)" :key="item.id">
      <td><div class="order-controls"><button class="btn btn-icon btn-sm btn-ghost-secondary" :aria-label="`${item.name} 위로`" @click="move(item, -1)">↑</button><span>{{ item.order }}</span><button class="btn btn-icon btn-sm btn-ghost-secondary" :aria-label="`${item.name} 아래로`" @click="move(item, 1)">↓</button></div></td>
      <td class="fw-semibold">{{ item.name }}</td><td class="text-secondary criteria-description">{{ item.description || '설명 없음' }}</td><td><span class="badge bg-blue-lt">{{ item.weight }}%</span></td><td><span class="badge" :class="item.is_active ? 'bg-green-lt' : 'bg-secondary-lt'">{{ item.is_active ? '활성' : '비활성' }}</span></td>
      <td><div class="table-actions"><button class="btn btn-icon btn-ghost-secondary" :aria-label="`${item.name} 수정`" @click="openEdit(item)"><IconPencil :size="17" /></button><button class="btn btn-icon btn-ghost-danger" :aria-label="`${item.name} 삭제`" @click="deleteCriteria(item)"><IconTrash :size="17" /></button></div></td>
    </tr></tbody>
    <tbody v-else-if="loading"><tr><td colspan="6"><div class="placeholder placeholder-glow w-100"></div></td></tr></tbody><tbody v-else><tr><td colspan="6" class="text-center text-secondary py-5">등록된 평가 항목이 없습니다.</td></tr></tbody>
  </table></div></section>

  <div v-if="modalOpen" class="modal-backdrop-enterprise" @click.self="modalOpen = false"><section class="modal-panel" role="dialog" aria-modal="true" aria-labelledby="criteria-modal-title">
    <header class="modal-panel-header"><h3 id="criteria-modal-title">{{ editingId ? '평가 항목 수정' : '평가 항목 추가' }}</h3><button class="btn-close" aria-label="닫기" @click="modalOpen = false"></button></header>
    <form @submit.prevent="saveCriteria"><div class="modal-panel-body"><label class="form-label" for="criteria-name">항목명</label><input id="criteria-name" v-model.trim="form.name" class="form-control mb-3" required maxlength="150" />
      <label class="form-label" for="criteria-description">평가 기준 설명</label><textarea id="criteria-description" v-model.trim="form.description" class="form-control mb-3" rows="3"></textarea>
      <div class="criteria-form-grid"><div><label class="form-label" for="criteria-weight">가중치 (%)</label><input id="criteria-weight" v-model.number="form.weight" type="number" min="1" max="100" class="form-control" required /></div><div><label class="form-label" for="criteria-order">표시 순서</label><input id="criteria-order" v-model.number="form.order" type="number" min="1" class="form-control" required /></div></div>
      <label class="form-check mt-3"><input v-model="form.is_active" type="checkbox" class="form-check-input" /><span class="form-check-label">평가에 사용</span></label><div v-if="error" class="alert alert-danger mt-3 mb-0">{{ error }}</div>
    </div><footer class="modal-panel-footer"><button class="btn btn-outline-secondary" type="button" @click="modalOpen = false">취소</button><button class="btn btn-primary" type="submit" :disabled="saving">{{ saving ? '저장 중...' : '저장' }}</button></footer></form>
  </section></div>
</template>