# CLAUDE.md - HR Performance Review System

This workspace contains the specifications, backend (Django REST Framework), and frontend (Vue.js 3 + Tabler) for the HR Performance Review System.

## Documentation Index
- `AGENTS.md`: Master architectural rules, design system, and coding conventions.
- `specs/01-architecture.md`: System Architecture & Tech Stack
- `specs/02-database.md`: Database Schema & ERD
- `specs/03-auth.md`: Authentication & RBAC (Employee ID login)
- `specs/04-organizations.md`: Organizations (Team) & User Management
- `specs/05-evaluations.md`: Evaluation Criteria & Review Submission
- `specs/06-reports.md`: Dashboard KPI & CSV Export
- `specs/07-scoring.md`: Scoring Engine, Cap Rules (100 pts) & Edge Cases
- `specs/08-ui.md`: Tabler B2B SaaS Design System & UI Components
- `specs/09-roadmap.md`: 5-Phase Development Roadmap & Enhanced Definition of Done (DoD)
- `specs/10-api-reference.md`: RESTful API Endpoints & Contracts

## Core Rules & Commands
- **Backend**: Python 3.11+, Django 5.x, Django REST Framework, SimpleJWT, PostgreSQL
  - Run server: `python backend/manage.py runserver`
  - Migrate: `python backend/manage.py migrate`
- **Frontend**: Vue.js 3 (`<script setup>`), Vite, Pinia, Vue Router, Tabler
  - Run dev server: `cd frontend && npm run dev`
  - Build: `cd frontend && npm run build`
- **Key Calculation**:
  - Raw Score: $\sum (\text{score}_i / 5 \times \text{weight}_i)$
  - Final Score: $\min(100.0, \max(0.0, \text{raw\_score} + \text{bonus}))$
  - Cap Rule: Capped at 100 with badge if sum > 100.

