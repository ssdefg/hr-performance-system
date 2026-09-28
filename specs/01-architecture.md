# 01. 시스템 아키텍처 및 기술 스택 명세 (System Architecture)

## 1. 시스템 아키텍처 개요
HR 인사평가 시스템은 B2B SaaS 환경을 타겟으로 한 Single Page Application(SPA) 프론트엔드와 RESTful API 백엔드로 구성됩니다.

```
+--------------------------------------------------------------------+
|                         Client Browser                             |
|       Vue.js 3 SPA (Vite + Pinia + Vue Router + Tabler UI)         |
+--------------------------------------------------------------------+
                                  |
                           JSON REST API
                                  |
+--------------------------------------------------------------------+
|                         Backend Server                             |
|     Django 5.x + Django REST Framework (DRF) + SimpleJWT           |
|                                                                    |
|  [authentication]  [organizations]  [evaluations]  [reports]       |
+--------------------------------------------------------------------+
                                  |
                              Django ORM
                                  |
+--------------------------------------------------------------------+
|                       Database (PostgreSQL)                        |
+--------------------------------------------------------------------+
```

## 2. 기술 스택 상세
- **Frontend**: Vue.js 3 (Composition API `<script setup>`), Vite, Pinia, Vue Router 4, Axios
- **UI Framework**: Tabler (Bootstrap 5 기반), Tabler Icons Vue
- **Backend**: Python 3.11+, Django 5.x, Django REST Framework, djangorestframework-simplejwt
- **Database**: PostgreSQL (개발 시 SQLite 호환 가능)
- **보안 & 인증**: 사번 기반 JWT 인증 (Access + Refresh Token), Role-Based Access Control (RBAC)

## 3. 디렉터리 구조 규칙
- 백엔드는 단일 책임 원칙에 따라 4개 앱(`authentication`, `organizations`, `evaluations`, `reports`)으로 분리.
- 프론트엔드는 도메인별 API 모듈(`src/api/`), 상태 스토어(`src/stores/`), 재사용 UI 컴포넌트(`src/components/`), 역할별 뷰(`src/views/`)로 모듈화.

