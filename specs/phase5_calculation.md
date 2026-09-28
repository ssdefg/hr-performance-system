# Phase 5: 점수 산출, 팀 보너스, 집계 대시보드 및 내보내기 (Calculation, Bonus & Reporting)

## 1. 개요 및 목적
개인 평가 점수와 팀 보너스(0~10점)를 결합하여 최종 점수를 산출하고, 100점 상한(Cap) 규칙을 적용한다. 관리자가 팀 보너스를 일괄 입력하고 전사 평가 현황을 모니터링할 수 있는 4개 KPI 요약 카드 및 점수 관리 테이블을 제공하며, 최종 집계 데이터를 CSV로 다운로드하는 기능을 구현한다.

---

## 2. 작업 상세 요구사항

### 2.1 Backend Calculation & Bonus Logic

1. **최종 점수 및 상한(Cap) 계산 로직 (`apps/evaluations/services.py`)**:
   - 개인 점수: $\text{raw\_score} = \sum (\text{score} / 5 \times \text{weight})$
   - 팀 보너스: $B_{\text{team}} \in [0, 10]$
   - 최종 점수 계산식:
     $$\text{final\_score} = \min(100.0, \max(0.0, \text{raw\_score} + B_{\text{team}}))$$
   - `is_capped` 플래그: $(\text{raw\_score} + B_{\text{team}}) > 100.0$ 인 경우 `True`

2. **팀 보너스 일괄 적용 API (`apps/organizations/views.py` or `apps/evaluations/views.py`)**:
   - `POST /api/teams/{team_id}/bonus/`:
     - Request: `{ "bonus_score": 5.0 }` (0.0 ~ 10.0 범위 유효성 검사)
     - 처리: 해당 팀의 `bonus_score`를 업데이트하고, 해당 팀 소속 사원들의 최종 점수 및 상한 여부를 일괄 갱신

3. **전사 통계 및 대시보드 API (`apps/reports/views.py`)**:
   - `GET /api/reports/dashboard-kpi/`:
     - `total_employees`: 전체 평가 대상 인원수
     - `completion_rate`: 평가 완료율 (제출된 평가서 수 / 전체 대상자 수 * 100, %)
     - `company_average_score`: 제출 완료된 사원들의 최종 점수 전사 평균
     - `bonus_summary`: 보너스가 부여된 팀 수 / 전체 팀 수
   - `GET /api/reports/score-table/`:
     - 팀별 필터 지원 (`?team_id=...`)
     - 사원별 상세 데이터 목록:
       - 사번, 성명, 소속팀, 매니저명, 평가 제출상태, 개인 평가 점수, 팀 보너스 점수, 최종 점수, 상한 적용 여부(`is_capped`)

4. **CSV 데이터 내보내기 API (`apps/reports/views.py`)**:
   - `GET /api/reports/export-csv/`:
     - `Content-Type: text/csv; charset=utf-8-sig` (Excel 한글 깨짐 방지 UTF-8 BOM 포함)
     - 파일명: `HR_Performance_Review_YYYYMMDD.csv`
     - 컬럼 구성:
       `사번, 성명, 역할, 소속팀, 평가진행상태, 개인평가점수, 팀보너스, 최종점수, 상한적용여부`

### 2.2 Frontend UI & B2B SaaS Dashboard

1. **대시보드 KPI 카드 (`src/components/KpiCard.vue` 및 `AdminDashboardView.vue`)**:
   - 상단 그리드에 4개 요약 통계 카드 배치:
     1. **전체 인원수**: `N명` (사원 아이콘)
     2. **평가 완료율**: `X.X%` (프로그레스 바 및 퍼센트)
     3. **전사 평균 점수**: `Y.Y점` (차트/점수 아이콘)
     4. **보너스 부여 현황**: `M / Total 팀 적용됨` (선물/별 아이콘)

2. **점수 및 보너스 관리 테이블 & 인라인 툴바**:
   - **인라인 툴바 구성**:
     - `[팀 선택 드롭다운]` (전체 또는 특정 팀 선택)
     - `[보너스 점수 입력]` (+0.0 ~ 10.0)
     - `['팀 전체 적용' 액션 버튼]` (클릭 시 확인 컨펌 후 즉시 반영 및 토스트 알림)
     - `[CSV 다운로드 버튼]` (클릭 시 즉시 브라우저 다운로드)
   - **테이블 컬럼 및 스타일**:
     - **사원 프로필**: 이니셜 원형 아바타 + 성명 (사번은 서브 텍스트)
     - **소속 팀**: 텍스트 및 부서명
     - **팀 보너스**: 캡슐형 배지 (`badge bg-success-subtle text-success`, 예: `+5.0점`)
     - **개인 점수**: 기본 평가 원점수
     - **최종 점수**: 볼드 강조 텍스트 (예: `87.0점`)
     - **상한 표시**: 100점 초과 시 `badge bg-azure text-white` 형태의 `(상한)` 라벨 노출

---

## 3. 검증 기준 (Definition of Done)
1. 개인 점수 82점에 팀 보너스 +5점 적용 시 최종 점수 87점이 정확히 산출되어야 함.
2. 개인 점수 98점에 팀 보너스 +5점 적용 시 최종 점수는 100점으로 상한 처리되고 `(상한)` 라벨이 표시되어야 함.
3. 특정 팀에 보너스 점수 입력 후 '팀 전체 적용' 실행 시 해당 팀원 전원의 테이블에 즉시 보너스 및 재계산된 점수가 반영되어야 함.
4. CSV 다운로드 실행 시 UTF-8 BOM 인코딩으로 한글 깨짐 없이 정상적인 CSV 파일이 저장되어야 함.

