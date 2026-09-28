# 10. RESTful API 엔드포인트 참조 규격 (API Reference)

## 1. 인증 API (`/api/auth/`)
| Method | Endpoint | Description | Auth | Request Body / Query |
| :--- | :--- | :--- | :---: | :--- |
| `POST` | `/api/auth/login/` | 사번/비밀번호 로그인 및 JWT 발급 | Public | `{ "employee_id": "ADMIN", "password": "..." }` |
| `POST` | `/api/auth/refresh/` | JWT Access Token 갱신 | Public | `{ "refresh": "..." }` |
| `GET` | `/api/auth/me/` | 현재 로그인 유저 프로필 조회 | Bearer | - |

## 2. 조직/팀 API (`/api/teams/`)
| Method | Endpoint | Description | Auth | Request Body / Query |
| :--- | :--- | :--- | :---: | :--- |
| `GET` | `/api/teams/` | 팀 목록 조회 | Bearer | - |
| `POST` | `/api/teams/` | 신규 팀 생성 | Admin | `{ "name": "개발팀", "manager_id": 2 }` |
| `PUT/PATCH`| `/api/teams/{id}/` | 팀 수정 및 매니저 지정 | Admin | `{ "name": "...", "manager_id": 3 }` |
| `DELETE` | `/api/teams/{id}/` | 팀 삭제 | Admin | - |
| `POST` | `/api/teams/{id}/bonus/`| 팀 보너스 일괄 입력 및 점수 갱신 | Admin | `{ "bonus_score": 5.0 }` |

## 3. 사용자 관리 API (`/api/users/`)
| Method | Endpoint | Description | Auth | Request Body / Query |
| :--- | :--- | :--- | :---: | :--- |
| `GET` | `/api/users/` | 사원 목록 조회 (팀/역할 필터) | Admin | `?team_id=&role=` |
| `POST` | `/api/users/` | 신규 사원 등록 | Admin | `{ "employee_id": "EMP001", "name": "홍길동", "password": "...", "role": "EMPLOYEE", "team_id": 1 }` |
| `PUT/PATCH`| `/api/users/{id}/` | 사원 정보 수정 | Admin | `{ "name": "...", "team_id": 2, "role": "MANAGER" }` |
| `DELETE` | `/api/users/{id}/` | 사원 삭제 | Admin | - |

## 4. 평가 관리 API (`/api/evaluations/`)
| Method | Endpoint | Description | Auth | Request Body / Query |
| :--- | :--- | :--- | :---: | :--- |
| `GET` | `/api/evaluations/criteria/` | 평가 항목 목록 조회 | Bearer | - |
| `POST` | `/api/evaluations/criteria/` | 평가 항목 생성 | Admin | `{ "name": "직무역량", "weight": 40, "order": 1 }` |
| `PUT/PATCH`| `/api/evaluations/criteria/{id}/` | 평가 항목 및 가중치 수정 | Admin | `{ "weight": 50 }` |
| `DELETE` | `/api/evaluations/criteria/{id}/` | 평가 항목 삭제 | Admin | - |
| `GET` | `/api/evaluations/criteria/summary/` | 가중치 합계 및 유효성 확인 | Bearer | Returns `{ "total_weight": 100, "is_valid": true }` |
| `GET` | `/api/evaluations/team-members/` | 매니저 담당 팀원 목록 및 작성상태 | Manager | - |
| `GET` | `/api/evaluations/reviews/{employee_id}/` | 특정 직원의 평가서 조회 | Manager | - |
| `POST` | `/api/evaluations/reviews/{employee_id}/draft/` | 평가서 임시 저장 | Manager | `{ "scores": [{ "criteria_id": 1, "score": 4 }] }` |
| `POST` | `/api/evaluations/reviews/{employee_id}/submit/`| 평가서 최종 제출 (잠금) | Manager | `{ "scores": [{ "criteria_id": 1, "score": 4 }] }` |
| `GET` | `/api/evaluations/my-review/` | 본인 평가 결과 조회 | Employee | - |

## 5. 리포트 & 대시보드 API (`/api/reports/`)
| Method | Endpoint | Description | Auth | Request Body / Query |
| :--- | :--- | :--- | :---: | :--- |
| `GET` | `/api/reports/dashboard-kpi/` | 4대 요약 KPI 지표 | Admin | - |
| `GET` | `/api/reports/score-table/` | 전사 점수 관리 테이블 데이터 | Admin | `?team_id=` |
| `GET` | `/api/reports/export-csv/` | UTF-8 BOM CSV 파일 다운로드 | Admin | `?team_id=` |

