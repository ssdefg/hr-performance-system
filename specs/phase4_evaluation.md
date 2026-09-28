# Phase 4: 매니저 평가 인터페이스 및 실시간 프리뷰 (Evaluation Interface & Realtime Logic)

## 1. 개요 및 목적
매니저(Manager)가 소속 팀원에 대한 다면 평가를 직관적으로 수행할 수 있는 인터페이스를 구축한다. 1~5점 척도의 세그먼트 버튼, 점수 선택에 따른 실시간 점수 환산 프리뷰, 임시 저장(Draft) 및 최종 제출(Lock)을 통한 어뷰징 방지 로직을 구현하며, 직원의 본인 평가 조회 화면과 관리자의 모니터링 뷰를 제공한다.

---

## 2. 작업 상세 요구사항

### 2.1 Backend Models & Business Logic

1. **평가 데이터 모델 (`apps/evaluations`)**:
   - Model `EvaluationReview`:
     - `employee` (ForeignKey to `User`, 피평가자 - `role='EMPLOYEE'`)
     - `evaluator` (ForeignKey to `User`, 평가자 매니저)
     - `status` (CharField, choices: `DRAFT`, `SUBMITTED`, default=`DRAFT`)
     - `submitted_at` (DateTimeField, null=True, blank=True)
     - `raw_score` (FloatField, default=0.0, 개인 평가 환산 점수)
     - Unique constraint: `(employee, evaluator)` - 동일 평가 주기 중복 방지
   - Model `EvaluationItemScore`:
     - `review` (ForeignKey to `EvaluationReview`, related_name='scores')
     - `criteria` (ForeignKey to `EvaluationCriteria`)
     - `score` (PositiveSmallIntegerField, 1~5점)
     - Unique constraint: `(review, criteria)`

2. **접근 제어 및 검증 로직**:
   - **소속 팀 제한**: 매니저는 자신이 담당하는 팀의 소속 직원만 평가 목록에서 조회 및 작성 가능.
   - **수정 불가(Lock) 규칙**: `status == 'SUBMITTED'`인 경우 수정(`PUT`/`PATCH`) 요청 시 `403 Forbidden` 또는 `400 Bad Request` 반환.
   - **점수 계산 로직**:
     $$\text{raw\_score} = \sum \left( \frac{\text{score}}{5} \times \text{criteria.weight} \right)$$

3. **Endpoints (`/api/evaluations/`)**:
   - `GET /api/evaluations/team-members/`: 매니저 전용 - 소속 팀원 목록 및 각 팀원별 평가 진행 상태(`DRAFT`, `SUBMITTED`, `NOT_STARTED`) 조회
   - `GET /api/evaluations/reviews/{employee_id}/`: 특정 직원에 대한 평가서 조회 (임시저장본 포함)
   - `POST /api/evaluations/reviews/{employee_id}/draft/`: 평가서 임시 저장
   - `POST /api/evaluations/reviews/{employee_id}/submit/`: 평가서 최종 제출 (락 처리)
   - `GET /api/evaluations/my-review/`: 직원(Employee) 전용 - 본인의 평가 상세 결과 및 최종 점수 조회
   - `GET /api/evaluations/admin-monitoring/`: 관리자(Admin) 전용 - 매니저별/팀별 제출율 및 미제출자 실시간 현황

### 2.2 Frontend UI & UX 구현

1. **매니저 평가 대시보드 & 팀원 목록 (`src/views/manager/ManagerDashboardView.vue`)**:
   - 담당 팀 명칭 및 팀원 카드/리스트
   - 진행 상태 배지 (`작성 전: secondary`, `임시저장: warning`, `제출완료: success`)
   - 진행률 인디케이터 (예: 4명 중 3명 제출 완료)

2. **인터랙티브 평가 작성 폼 (`src/views/manager/EvaluationFormView.vue`)**:
   - **1~5점 척도 세그먼트 버튼 그룹 (`btn-group`)**:
     - 각 항목마다 [1 매우미흡] [2 미흡] [3 보통] [4 우수] [5 매우우수] 형태의 클릭형 버튼 제공
     - 선택 시 즉시 활성화 하이라이트 스타일 적용
   - **실시간 반응형 점수 프리뷰 (Live Score Preview)**:
     - 우측 고정 사이드바(또는 하단 플로팅 바)에 항목별 환산 기여 점수 표시
     - 총 개인 평가 환산 점수(100점 만점 기준) 실시간 계산 출력
   - **액션 버튼**:
     - [임시 저장]: 모든 항목을 채우지 않아도 현재까지 입력값 저장
     - [최종 제출]: 모든 항목(1~5점)이 채워진 경우에만 활성화되며, 확인 모달(제출 후 수정 불가 안내) 노출 후 제출

3. **직원 전용 내 평가 조회 뷰 (`src/views/employee/MyEvaluationView.vue`)**:
   - 본인의 평가가 제출 완료된 경우에만 열람 가능 (미제출 시 '평가 진행 중' 안내)
   - 항목별 가중치, 매니저 부여 점수, 개인 환산 점수, 팀 보너스 및 최종 점수 내역 카드 표시

---

## 3. 검증 기준 (Definition of Done)
1. 매니저는 타 팀의 직원에 대한 평가를 조회하거나 제출할 수 없음.
2. 1~5점 세그먼트 버튼 클릭 시 새로고침 없이 즉시 실시간 환산 점수가 계산되어 화면에 반영됨.
3. 임시 저장 후 재접속 시 이전 입력값이 복원되어야 함.
4. 최종 제출 이후에는 매니저가 점수를 수정할 수 없으며(Lock), 읽기 전용 모드로 전환됨.
5. 직원은 본인 계정으로 본인 점수만 조회 가능해야 함.

