# 09. 개발 로드맵 및 완료 기준 (Roadmap & Enhanced DoD)

## 1. 개요
본 문서는 HR 인사평가 시스템의 5단계(Phase 1~5) 개발 로드맵과 각 단계별 세부 작업 및 **강화된 완료 정의(Definition of Done, DoD)**를 규정합니다. 특히 Phase 3, 4, 5의 프론트엔드 작업에서는 [`08-ui.md`](./08-ui.md)에 명시된 Tabler 기반 B2B SaaS 엔터프라이즈 컴포넌트 준수 여부를 필수적으로 검증합니다.

---

## 2. 단계별 세부 로드맵 & DoD

```
Phase 1: Setup & Env  -->  Phase 2: Auth & Seed  -->  Phase 3: Core CRUD  -->  Phase 4: Evaluation UI  -->  Phase 5: Calculation & Report
[Django/Vue3/Tabler]      [사번 JWT/관리자 시드]      [팀/유저/가중치 CRUD]     [세그먼트 폼/실시간]        [보너스/상한/KPI/CSV]
```

### 2.1 Phase 1: 프로젝트 구성 및 기본 환경 설정 (Setup & Environment)
- **주요 작업**:
  - Django 프로젝트 및 4개 핵심 앱 분리 (`authentication`, `organizations`, `evaluations`, `reports`)
  - PostgreSQL 연동 및 기본 `requirements.txt` 설치
  - Vue.js 3 + Vite + Pinia + Vue Router + Tabler 테마 세팅
  - Axios 클라이언트 기본 URL 및 인터셉터 설정
- **DoD (완료 기준)**:
  - [x] `manage.py runserver` 및 `npm run dev` 구동 확인
  - [x] 프론트엔드-백엔드 간 CORS 통신 테스트 통과
  - [x] Tabler 글로벌 스타일(`#f8fafc` 배경 등) 적용 확인

### 2.2 Phase 2: 사번 기반 인증 및 기본 관리자 시드 (Authentication & Admin Seed)
- **주요 작업**:
  - `AbstractUser` 상속 `User` 모델 (`employee_id` 기반)
  - `post_migrate` 기반 기본 관리자(`ADMIN` / `ADMIN` / `admin1234!`) 자동 생성
  - SimpleJWT 로그인 API 구현 및 Pinia Auth Store 연동
  - 로그인 뷰 및 역할별(Admin/Manager/Employee) Vue Router 가드
- **DoD (완료 기준)**:
  - [x] 최초 마이그레이션 시 `ADMIN` 관리자 계정 자동 생성 확인
  - [x] JWT 발급 및 사번/비밀번호 로그인 정상 동작
  - [x] 비인가 접근 차단 및 역할에 따른 올바른 대시보드 리다이렉트 확인

### 2.3 Phase 3: 조직, 사용자 및 가중치 평가 항목 관리 (Core Management CRUD)
- **주요 작업**:
  - 팀 CRUD API 및 매니저 1명 배정 제한 로직
  - 사원 CRUD API (사번 중복 검증, 역할 배정, 팀 배정)
  - 평가 항목 CRUD API 및 가중치 합 100 검증 API
  - 관리자용 관리 화면 UI 개발
- **DoD (UI 디자인 시스템 검증 포함)**:
  - [x] **Tabler UI 준수**: `specs/08-ui.md`의 `.card-enterprise` 컨테이너 및 둥근 코너(`rounded-3`, `shadow-sm`) 적용
  - [x] **아바타 칩 & 배지**: 사원 목록에 이니셜 원형 아바타 칩 및 역할별 컬러 배지 적용
  - [x] **가중치 인디케이터**: 가중치 합계가 100일 때 녹색 인디케이터(`100/100 정상`), 100이 아닐 때 적색 경고 인디케이터 실시간 렌더링
  - [x] **유효성 검증**: 매니저 역할만 팀장으로 배정 가능하며, 사번 중복 등록이 차단됨

### 2.4 Phase 4: 매니저 평가 인터페이스 및 실시간 프리뷰 (Evaluation Interface & Realtime Logic)
- **주요 작업**:
  - `EvaluationReview` 및 `EvaluationItemScore` 모델 구현
  - 매니저 전용 팀원 목록 및 상태 조회 API
  - 1~5점 척도 인터랙티브 세그먼트 버튼 그룹 컴포넌트
  - 실시간 환산 점수 반응형 프리뷰 패널
  - 임시저장(Draft) 및 최종제출 잠금(Lock) 어뷰징 방지
  - 직원 전용 본인 평가 결과 조회 뷰
- **DoD (UI 디자인 시스템 검증 포함)**:
  - [x] **세그먼트 버튼 그룹**: 단순 드롭다운이 아닌 클릭형 1~5점 세그먼트 버튼(`btn-group`) 적용 및 활성 하이라이트
  - [x] **실시간 프리뷰**: 세그먼트 버튼 클릭 즉시 우측/하단 사이드 패널에 항목별 환산 점수 및 총점 실시간 반응
  - [x] **상태 배지 & 진행률**: 팀원 목록에 진행 상태 배지(작성전, 임시저장, 제출완료) 및 진행률 프로그레스 바 표시
  - [x] **잠금(Lock) 확인 모달**: 최종 제출 시 확인 모달 팝업 및 제출 후 수정 불가(읽기 전용) 전환 확인
  - [x] **가중치 불일치 차단**: 가중치 합계가 100이 아닐 때 평가 진입 차단 안내 메시지 출력

### 2.5 Phase 5: 점수 산출, 팀 보너스, 대시보드 및 내보내기 (Calculation, Bonus & Reporting)
- **주요 작업**:
  - 팀 보너스 일괄 입력 및 전사 사원 점수 일괄 재계산 로직
  - 100점 상한(Cap) 규칙 적용 및 `is_capped` 플래그 관리
  - 4개 KPI 요약 카드 (`specs/08-ui.md` 레이아웃)
  - 점수 및 보너스 관리 테이블 (인라인 툴바 포함)
  - UTF-8 BOM 지원 CSV 데이터 내보내기 API 및 프론트엔드 트리거
- **DoD (UI 디자인 시스템 검증 포함)**:
  - [x] **4열 KPI 카드**: [전체 인원 / 완료율(%) / 전사 평균 / 보너스 현황] Tabler KPI 카드 그리드 완성
  - [x] **인라인 툴바**: `[팀 선택 드롭다운] + [보너스 입력폼(+0~10)] + [팀 전체 적용 버튼] + [CSV 다운로드 버튼]`이 단일 Flex Row로 정렬
  - [x] **테이블 렌더링**: 캡슐형 팀 보너스 배지(`badge bg-success-subtle text-success`), 100점 초과 시 `(상한)` 라벨 노출
  - [x] **계산 및 상한 검증**: 82점 + 5점 = 87점, 98점 + 5점 = 100점(상한) 정상 작동
  - [x] **CSV 내보내기**: 엑셀에서 한글 깨짐 없는 CSV 파일 다운로드 확인

