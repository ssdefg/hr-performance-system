# 06. 대시보드 통계 및 데이터 내보내기 명세 (Dashboard & Reporting)

## 1. 전사 통계 대시보드 (KPI Cards)
- **전체 평가 대상자 수**: `COUNT(User WHERE role='EMPLOYEE')`
- **평가 완료율 (%)**: `COUNT(EvaluationReview WHERE status='SUBMITTED') / 전체 대상자 수 * 100`
- **전사 평균 점수**: 제출 완료된 사원들의 `final_score` 산술 평균
- **팀 보너스 부여 현황**: `COUNT(Team WHERE bonus_score > 0) / 전체 팀 수`

## 2. 점수 및 보너스 관리 테이블
- 팀별 필터링, 검색 지원
- 팀 보너스 일괄 입력 및 즉시 재계산 반영
- 개인 점수, 팀 보너스 배지, 최종 점수 및 `(상한)` 배지 표시

## 3. CSV 데이터 내보내기
- 엑셀 호환을 위해 UTF-8 with BOM (`utf-8-sig`) 인코딩 적용.
- 파일명 형식: `HR_Performance_Review_YYYYMMDD.csv`
- 컬럼 구성:
  1. 사번 (`employee_id`)
  2. 성명 (`name`)
  3. 역할 (`role`)
  4. 소속 팀 (`team_name`)
  5. 평가 상태 (`status`)
  6. 개인 평가 점수 (`raw_score`)
  7. 팀 보너스 (`bonus_score`)
  8. 최종 점수 (`final_score`)
  9. 상한 적용 여부 (`is_capped`)

