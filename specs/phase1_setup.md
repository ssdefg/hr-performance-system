# Phase 1: 프로젝트 구성 및 기본 환경 설정 (Setup & Environment)

## 1. 개요 및 목적
백엔드(Django REST Framework)와 프론트엔드(Vue.js 3 + Tabler)의 프로젝트 구조를 구축하고, PostgreSQL 데이터베이스 연결 및 CORS, 기본 에셋 설정을 완료한다.

---

## 2. 작업 상세 요구사항

### 2.1 Backend (Django REST Framework)
1. **프로젝트 & 앱 디렉터리 구성**:
   - `backend/` 폴더 내에 Django 프로젝트(`config`) 및 4개 핵심 앱 생성:
     - `apps.authentication`: 계정, 사번 인증, 권한 관리
     - `apps.organizations`: 팀/부서 관리
     - `apps.evaluations`: 평가 항목, 평가서 제출 및 점수 계산
     - `apps.reports`: 통계 및 CSV 데이터 내보내기
2. **패키지 의존성 설정 (`requirements.txt`)**:
   - `Django>=5.0`
   - `djangorestframework>=3.14.0`
   - `djangorestframework-simplejwt>=5.3.0`
   - `django-cors-headers>=4.3.0`
   - `psycopg2-binary>=2.9.9` (PostgreSQL 연동)
   - `python-dotenv>=1.0.0`
3. **`config/settings.py` 구성**:
   - `INSTALLED_APPS`에 DRF, CORS, SimpleJWT, 로컬 앱 등록
   - `DATABASES` 설정 (PostgreSQL 환경 변수 연동)
   - `AUTH_USER_MODEL = 'authentication.User'` 지정
   - `REST_FRAMEWORK` 설정: JWT 인증을 기본 인증 클래스로 설정
   - `CORS_ALLOWED_ORIGINS` 설정 (프론트엔드 Vite 개발 서버 `http://localhost:5173` 허용)

### 2.2 Frontend (Vue 3 + Vite + Tabler)
1. **Vite 프로젝트 스캐폴딩**:
   - Vue 3 + Single Page Application (SPA) 구성
   - Pinia (상태 관리), Vue Router, Axios 설치
2. **Tabler UI Framework & 테마 구성**:
   - `@tabler/core` 및 `@tabler/icons-vue` 설치 및 글로벌 스타일 임포트
   - 뉴트럴 라이트 쿨그레이(`#f8fafc`) 배경 및 엔터프라이즈 카드 디자인 템플릿 기본 레이아웃 구성 (`AppLayout.vue`)
3. **Axios 인터셉터 기본 설정 (`src/api/client.js`)**:
   - Base URL 설정 (`http://localhost:8000/api`)
   - Request 인터셉터: 로컬 스토리지의 JWT Access Token 자동 첨부
   - Response 인터셉터: 401 Unauthorized 발생 시 자동 로그아웃 및 로그인 페이지 리다이렉트

---

## 3. 검증 기준 (Definition of Done)
1. 백엔드 `python manage.py runserver` 실행 시 오류 없이 구동되고 PostgreSQL 데이터베이스에 정상 연결됨.
2. 프론트엔드 `npm run dev` 실행 시 Tabler 스타일이 적용된 기본 레이아웃 셸이 브라우저에 렌더링됨.
3. 프론트엔드에서 백엔드 기본 헬스체크 API 호출 시 200 OK 응답 및 CORS 정상 작동 확인.

