# Phase 3: 팀, 사용자 및 평가 항목 관리 (Core Management CRUD)

## 1. 개요 및 목적
관리자(Admin)가 인사평가 시스템 운영에 필수적인 조직(팀), 사용자 계정(매니저/직원 배정), 그리고 평가 척도의 기준이 되는 평가 항목 및 가중치(합계 100 검증)를 관리할 수 있는 CRUD 기능과 직관적인 UI를 구현한다.

---

## 2. 작업 상세 요구사항

### 2.1 Backend Models & Endpoints

1. **팀(부서) 관리 (`apps/organizations`)**:
   - Model `Team`:
     - `name` (CharField, unique=True, 팀 이름)
     - `manager` (ForeignKey to `User`, null=True, blank=True, `limit_choices_to={'role': 'MANAGER'}`)
     - `bonus_score` (FloatField, default=0.0, 0~10점 범위)
   - Endpoints (`/api/teams/`):
     - `GET /api/teams/`: 팀 목록 및 담당 매니저 정보 조회
     - `POST /api/teams/`: 팀 생성 및 매니저 지정
     - `PUT/PATCH /api/teams/{id}/`: 팀 정보 수정
     - `DELETE /api/teams/{id}/`: 팀 삭제

2. **사용자 관리 (`apps/authentication`)**:
   - Endpoints (`/api/users/`):
     - `GET /api/users/`: 전체 사원 목록 필터링/조회 (사번, 이름, 역할, 소속팀)
     - `POST /api/users/`: 신규 사원 등록 (사번, 이름, 비밀번호, 역할, 소속팀 지정)
     - `PUT/PATCH /api/users/{id}/`: 사원 정보 및 소속/역할 변경
     - `DELETE /api/users/{id}/`: 사원 삭제

3. **평가 항목 및 가중치 관리 (`apps/evaluations`)**:
   - Model `EvaluationCriteria`:
     - `name` (CharField, 항목명, 예: 직무 역량, 협업 및 커뮤니케이션)
     - `description` (TextField, 항목 세부 평가 기준 안내)
     - `weight` (PositiveIntegerField, 1~100 가중치)
     - `order` (PositiveIntegerField, 표시 순서)
   - **가중치 합계 검증 로직**:
     - Serializer 및 서비스 레이어에서 평가 항목의 가중치 합계를 검증하는 엔드포인트 제공
     - `GET /api/evaluations/criteria/summary/`: 현재 등록된 항목 수 및 가중치 합계(`total_weight`) 반환 (100점 여부 플래그 포함)
     - 활성 평가 항목 가중치 총합이 100이 아닐 경우 경고 플래그 전달

### 2.2 Frontend Admin Management UI

1. **팀 관리 페이지 (`src/views/admin/TeamManagementView.vue`)**:
   - Tabler 모던 테이블 레이아웃
   - 팀명, 담당 매니저명, 소속 팀원 수, 팀 보너스 점수 표시
   - 모달을 통한 팀 등록/수정 (매니저 선택 드롭다운 연동)
2. **사원 관리 페이지 (`src/views/admin/UserManagementView.vue`)**:
   - 사번, 아바타 칩 + 성명, 역할(Admin/Manager/Employee 배지), 소속 팀 컬럼
   - 역할별/팀별 필터 툴바
   - 사원 등록/수정 모달 폼
3. **평가 항목 관리 페이지 (`src/views/admin/CriteriaManagementView.vue`)**:
   - 상단에 **가중치 합계 상태 인디케이터 바** 제공:
     - 합계 = 100: `100 / 100 (완료 - 정상)` 녹색 배지
     - 합계 != 100: `현재 X / 100 (가중치 합계가 100이어야 평가가 활성화됩니다)` 적색 경고
   - 항목명, 설명, 가중치(%) 입력 및 순서 정렬 기능

---

## 3. 검증 기준 (Definition of Done)
1. 팀 추가 시 `MANAGER` 역할을 가진 유저만 매니저로 지정 가능해야 함.
2. 사원 등록 시 사번 중복 체크가 정상 작동하고, 소속 팀 배정이 올바르게 반영됨.
3. 평가 항목 생성/수정/삭제 시 가중치 합계가 실시간으로 계산되고, 합계가 100이 아닌 경우 명확한 시각적 알림이 표시됨.

