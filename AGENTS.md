# AGENTS.md - HR Performance Review System

이 문서는 **바이브 코딩(Vibe Coding)** 기반의 HR 인사평가 시스템 개발을 위한 아키텍처 원칙, 프로젝트 규칙, 코딩 컨벤션, UI/UX 디자인 시스템 및 10개 명세서 간 상호참조 가이드라인입니다. 모든 AI 에이전트와 개발자는 본 문서의 규칙을 준수해야 합니다.

---

## 1. 프로젝트 개요 및 핵심 목표

- **시스템 명칭**: HR Performance Review System (B2B SaaS 인사평가 플랫폼)
- **주요 목적**: 사번 기반 인증, 권한별(관리자/매니저/직원) 분기, 가중치 기반 다면 평가, 팀 보너스 합산 및 100점 상한 규칙을 갖춘 엔터프라이즈급 인사평가 솔루션 구축
- **개발 철학**: 
  - 불필요한 기능(오버엔지니어링) 배제, 핵심 기능의 완성도 및 무결성 극대화
  - 프론트엔드와 백엔드의 명확한 분리(RESTful API)
  - Tabler 기반의 직관적이고 세련된 B2B SaaS UI/UX 제공 (`#f8fafc` 배경, `rounded-3`, `shadow-sm`)

---

## 2. 기술 스택 & 시스템 아키텍처

```
hr-system/
├── backend/                  # Django REST Framework 백엔드
│   ├── config/               # 프로젝트 설정 (settings, urls, wsgi)
│   ├── apps/
│   │   ├── authentication/   # 사용자, 사번 인증, 역할 관리
│   │   ├── organizations/    # 팀(부서) 관리
│   │   ├── evaluations/      # 평가 항목, 매니저 평가서, 점수/보너스 로직
│   │   └── reports/          # 통계 대시보드, CSV 내보내기
│   ├── manage.py
│   └── requirements.txt
├── frontend/                 # Vue.js 3 SPA 프론트엔드
│   ├── src/
│   │   ├── api/              # Axios 기반 REST API 클라이언트
│   │   ├── assets/           # Tabler 테마 및 커스텀 스타일
│   │   ├── components/       # 공통 UI 컴포넌트 (KPI 카드, 세그먼트 버튼그룹, 툴바 등)
│   │   ├── views/            # 페이지 뷰 (Admin, Manager, Employee 대시보드)
│   │   ├── router/           # Vue Router (인증/권한 가드 포함)
│   │   ├── stores/           # Pinia 상태 관리 (Auth, Review 등)
│   │   ├── App.vue
│   │   └── main.js
│   ├── package.json
│   └── vite.config.js
├── specs/                    # 시스템 상세 명세서 (10개 모듈)
│   ├── 01-architecture.md    # 시스템 아키텍처 및 기술 스택
│   ├── 02-database.md        # DB 스키마 및 ERD
│   ├── 03-auth.md            # 사번 인증 및 RBAC
│   ├── 04-organizations.md   # 조직(팀) 및 사원 관리
│   ├── 05-evaluations.md     # 평가 항목 및 제출 프로세스
│   ├── 06-reports.md         # 대시보드 통계 및 CSV 내보내기
│   ├── 07-scoring.md         # 점수 계산 공식, 상한 규칙 및 엣지 케이스
│   ├── 08-ui.md              # Tabler B2B SaaS 디자인 시스템 및 컴포넌트
│   ├── 09-roadmap.md         # 5단계 로드맵 및 강화된 완료 정의(DoD)
│   └── 10-api-reference.md   # RESTful API 엔드포인트 전체 규격
└── AGENTS.md                 # 본 프로젝트 전역 규칙 및 가이드 문서
```

### 2.1 기술 스택 정의
- **Frontend**: Vue.js 3 (Composition API `<script setup>`), Vite, Pinia, Vue Router, Axios
- **UI Framework**: Tabler (Bootstrap 5 기반 모던 B2B SaaS 디자인) + Tabler Icons
- **Backend**: Python 3.11+, Django 5.x, Django REST Framework (DRF), SimpleJWT (사번 기반 JWT 토큰 인증)
- **Database**: PostgreSQL (Django ORM 활용)
- **데이터 교환**: JSON RESTful API (UTF-8 with BOM CSV)

---

## 3. 핵심 비즈니스 로직 및 계산 공식 (Scoring Engine)

상세 내용은 [`specs/07-scoring.md`](./specs/07-scoring.md)를 준수합니다.

1. **평가 항목 가중치 규칙**:
   - 시스템 내 활성화된 평가 항목들의 `weight` 합은 반드시 **100**이어야 함.
   - 가중치 합계가 100이 아닐 경우 매니저 평가 작성 차단 및 관리자 경고 인디케이터 상시 노출.
2. **개인 평가 점수 (Individual Raw Score)**:
   $$S_{\text{raw}} = \sum_{i=1}^{N} \left( \frac{\text{부여 점수}_i}{5} \times \text{항목 가중치}_i \right)$$
   *(각 항목의 척도는 1~5점 정수, 소수점 둘째 자리까지 반올림)*
3. **최종 산출 점수 (Final Score) & 상한 규칙 (Cap Rule)**:
   $$S_{\text{final}} = \min(100.00, \max(0.00, S_{\text{raw}} + B_{\text{team}}))$$
   - 팀 보너스 점수($B_{\text{team}}$)는 0.0~10.0점 범위.
   - 개인 점수와 팀 보너스 합계가 100점을 초과할 경우 **100.00점으로 상한 제한(Cap)** 적용 및 UI에 `(상한)` 배지 표시.
   - *예: 개인점수 100점 + 보너스 5점 = 105점이 아닌 100점 확정.*

---

## 4. UI/UX 디자인 시스템 가이드 (Enterprise Tabler UI)

상세 내용은 [`specs/08-ui.md`](./specs/08-ui.md)를 준수합니다.

1. **컬러 & 레이아웃**:
   - 배경: `#f8fafc` (Slate 50 / Soft Cool Gray)
   - 메인 카드/컨테이너: `bg-white`, 테두리 `border: 1px solid #e2e8f0`, 모서리 `border-radius: 12px` (`rounded-3`), `shadow-sm`
   - 사이드바: 좌측 240px 슬림 고정 네비게이션 + 상단 글로벌 헤더 (브레드크럼, 주기 배지, 유저 아바타)
2. **대시보드 KPI 카드**:
   - 상단 4열 그리드: [전체 대상자 수] [평가 완료율(%)] [전사 평균 점수] [팀 보너스 부여 현황]
3. **매니저 평가 입력 컴포넌트**:
   - 1~5점 척도 선택은 단순 셀렉트박스가 아닌 **인터랙티브 세그먼트 버튼 그룹(`btn-group`)** 사용
   - 점수 클릭 시 즉시 우측/하단 프리뷰 패널에 항목별 환산 점수 및 실시간 총점 반응형 반영
4. **점수 및 보너스 관리 테이블**:
   - 인라인 툴바: 단일 행에 `[팀 선택 드롭다운] + [보너스 입력폼 (+0~10)] + [팀 전체 적용 버튼] + [CSV 다운로드 버튼]` 정렬
   - 테이블 행: 이니셜 원형 아바타 칩 + 성명/사번 + 소속 팀 + 캡슐형 팀 보너스 배지(`badge bg-success-subtle text-success`) + 볼드 최종 점수 + `(상한)` 라벨

---

## 5. 역할 및 권한 체계 (RBAC)

| 역할 (Role) | 주요 권한 및 접근 범위 |
| :--- | :--- |
| **Admin (관리자)** | - 팀(부서) CRUD 및 매니저 1명 지정<br>- 사용자(사번/성명/역할/팀) CRUD<br>- 평가 항목 및 가중치(합계 100 검증) CRUD<br>- 매니저별 제출 현황 실시간 모니터링<br>- 팀별 보너스(0~10점) 일괄 반영<br>- 최종 평가 데이터 CSV 다운로드 (UTF-8 BOM) |
| **Manager (매니저)** | - 본인 담당 팀에 소속된 직원 목록만 조회<br>- 소속 팀원 대상 1~5점 세그먼트 버튼 평가 입력<br>- 임시 저장(Draft) 및 실시간 점수 환산 프리뷰<br>- 최종 제출(Submit) 후 수정 불가(Lock) 어뷰징 차단 |
| **Employee (직원)** | - 본인 계정의 평가 세부 항목별 점수, 팀 보너스, 최종 점수만 읽기 전용 조회 |

---

## 6. 개발 로드맵 및 단계별 구현 가이드

상세 내용은 [`specs/09-roadmap.md`](./specs/09-roadmap.md)를 준수합니다.

- **Phase 1: Project Setup & Environment** (`specs/phase1_setup.md` / `specs/01-architecture.md`)
- **Phase 2: Authentication & Admin Seed** (`specs/phase2_auth.md` / `specs/03-auth.md`)
- **Phase 3: Core Management CRUD** (`specs/phase3_management.md` / `specs/04-organizations.md`)
- **Phase 4: Evaluation Interface & Realtime Logic** (`specs/phase4_evaluation.md` / `specs/05-evaluations.md` / `specs/08-ui.md`)
- **Phase 5: Calculation, Bonus & Reporting** (`specs/phase5_calculation.md` / `specs/06-reports.md` / `specs/07-scoring.md`)

---

## 7. 명세서 간 상호참조 가이드 (Specs Cross-Reference)

| 명세서 파일 | 핵심 주제 | 상호 연관 문서 |
| :--- | :--- | :--- |
| `specs/01-architecture.md` | 아키텍처 및 스택 | `AGENTS.md`, `specs/09-roadmap.md` |
| `specs/02-database.md` | ERD 및 모델 스키마 | `specs/03-auth.md`, `specs/04-organizations.md`, `specs/05-evaluations.md` |
| `specs/03-auth.md` | 사번 JWT 및 RBAC | `specs/02-database.md`, `specs/10-api-reference.md` |
| `specs/04-organizations.md` | 팀/유저 관리 | `specs/02-database.md`, `specs/07-scoring.md` |
| `specs/05-evaluations.md` | 다면 평가 및 잠금 | `specs/07-scoring.md`, `specs/08-ui.md`, `specs/10-api-reference.md` |
| `specs/06-reports.md` | 대시보드 및 CSV | `specs/07-scoring.md`, `specs/08-ui.md`, `specs/10-api-reference.md` |
| `specs/07-scoring.md` | 연산 엔진 및 엣지케이스 | `specs/05-evaluations.md`, `specs/06-reports.md`, `specs/08-ui.md` |
| `specs/08-ui.md` | UI/UX 컴포넌트 디자인 | `specs/05-evaluations.md`, `specs/06-reports.md`, `specs/09-roadmap.md` |
| `specs/09-roadmap.md` | 5단계 로드맵 & 강화된 DoD | `specs/08-ui.md`, `specs/phase1_setup.md` ~ `phase5_calculation.md` |
| `specs/10-api-reference.md` | REST API 규격 | `specs/03-auth.md` ~ `specs/07-scoring.md` |
