# Phase 2: 사번 기반 인증 및 기본 관리자 시드 (Authentication & Admin Seed)

## 1. 개요 및 목적
사번(Employee ID)과 비밀번호를 이용한 사용자 인증 체계를 구축하고, 앱 구동 시 기본 관리자 계정을 자동으로 생성(시딩)하며, 역할(Admin, Manager, Employee)에 따른 프론트엔드 라우팅 및 접근 제어를 구현한다.

---

## 2. 작업 상세 요구사항

### 2.1 Backend Data Model & Logic
1. **Custom User Model (`apps/authentication/models.py`)**:
   - Django의 `AbstractUser` 상속
   - 필드 정의:
     - `employee_id` (CharField, unique=True, 사번 - 로그인 식별자)
     - `name` (CharField, 성명)
     - `role` (CharField, choices: `ADMIN`, `MANAGER`, `EMPLOYEE`, 기본값: `EMPLOYEE`)
     - `team` (ForeignKey to `organizations.Team`, null=True, blank=True, on_delete=SET_NULL)
   - `USERNAME_FIELD = 'employee_id'`
   - `REQUIRED_FIELDS = ['name']`
2. **Default Admin Seeding**:
   - `apps/authentication/signals.py` 또는 `post_migrate` 핸들러 구현
   - 시스템 최초 구동(마이그레이션) 시 아래 기본 관리자 계정 자동 생성:
     - **사번 (employee_id)**: `ADMIN`
     - **성명 (name)**: `ADMIN`
     - **비밀번호**: `admin1234!`
     - **역할 (role)**: `ADMIN`
     - **슈퍼유저 플래그**: `is_staff=True`, `is_superuser=True`
3. **Authentication Endpoints**:
   - `POST /api/auth/login/`:
     - Request: `{ "employee_id": "...", "password": "..." }`
     - Response: `{ "access": "...", "refresh": "...", "user": { "employee_id": "...", "name": "...", "role": "...", "team_id": "...", "team_name": "..." } }`
   - `GET /api/auth/me/`: 현재 로그인 사용자 정보 반환 (Token 검증용)

### 2.2 Frontend UI & State Management
1. **Auth Store (`src/stores/auth.js`)**:
   - 상태: `token`, `user` (`employee_id`, `name`, `role`, `team`)
   - 액션: `login(employeeId, password)`, `logout()`, `fetchCurrentUser()`
2. **로그인 화면 (`src/views/auth/LoginView.vue`)**:
   - Tabler 기반의 정돈된 단일 로그인 카드 UI
   - 입력 필드: 사번(Employee ID), 비밀번호
   - 입력 유효성 검사 및 에러 메시지(Alert) 처리
3. **Vue Router 가드 (`src/router/index.js`)**:
   - 인증되지 않은 접근 시 `/login`으로 리다이렉트
   - 역할 기반 라우트 보호:
     - `/admin/*` : `ADMIN` 전용
     - `/manager/*` : `MANAGER` 전용
     - `/employee/*` : `EMPLOYEE` 전용
   - 로그인 성공 시 각 역할별 기본 대시보드로 자동 이동

---

## 3. 검증 기준 (Definition of Done)
1. 마이그레이션 실행 후 `ADMIN` / `admin1234!` 계정으로 로그인 시 JWT 토큰과 함께 관리자 정보가 정상 반환됨.
2. 프론트엔드 로그인 페이지에서 유효하지 않은 사번/비밀번호 입력 시 적절한 경고 메시지가 출력됨.
3. 로그인한 사용자의 역할에 따라 올바른 전용 대시보드로 이동하며, 타 역할의 라우트 진입 시 접근이 차단됨.

