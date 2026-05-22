# Qafied Project Memory

## Project Overview
Qafied is a visual feedback tool for websites. Users add a script tag to their site,
and visitors can place comments on specific areas. Admins manage feedback through a dashboard.

## Architecture
- **Backend**: FastAPI + SQLAlchemy 2.0 + PostgreSQL 15
- **Frontend**: Vite + React 18 + TypeScript + Tailwind CSS + shadcn/ui
- **Widget**: Vanilla TypeScript + html2canvas
- **Auth**: JWT-based (HS256)
- **Deployment**: Docker + docker-compose

## Implementation Progress

### Phase 1: Backend Foundation
- [x] **Task 1: Project Setup & Dependencies** — completed
  - `backend/requirements.txt` — FastAPI 0.109, SQLAlchemy 2.0.25, psycopg2-binary, python-jose, passlib, pydantic 2.5
  - `backend/app/__init__.py` — empty package marker
  - `backend/app/main.py` — FastAPI app with CORS (allow_origins=*) and `/health` endpoint
  - `backend/Dockerfile` — python:3.11-slim, installs gcc + libpq-dev for psycopg2, runs uvicorn on port 8000
  - `.env.example` — DATABASE_URL, SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES, FRONTEND_URL, WIDGET_URL
  - `.gitignore` — Python (__pycache__, .env, venv), Node (node_modules, dist), DB, IDE, OS
- [ ] Task 2: Database Models
- [ ] Task 3: Pydantic Schemas
- [ ] Task 4: Authentication System

### Phase 2: Core API Routers
- [ ] Task 5: Workspace Router
- [ ] Task 6: Website Router
- [ ] Task 7: Feedback Router

### Phase 3: Frontend
- [ ] Task 8: Frontend Setup
- [ ] Task 9: Frontend Core Components

### Phase 4: Widget
- [ ] Task 10: Feedback Widget

### Phase 5: Docker & Documentation
- [ ] Task 11: Docker Configuration
- [ ] Task 12: Documentation

## Key Decisions
1. Multi-workspace support with role-based access (owner / admin / member)
2. 3-member limit per workspace (current tier)
3. Feedback widget can be shown by default OR hidden behind `?feedback=on` URL param
4. Screenshots are optional (enabled by default, can be disabled per submission)
5. Anonymous commenting allowed; commenter_name/email optional
6. CORS is wide open (`*`) for now — tighten before production

## Database Schema (planned)
- `users`: id, email (unique), hashed_password, full_name, is_active, is_superuser, timestamps
- `workspaces`: id, name, slug (unique), owner_id, max_members (default 3), is_active, timestamps
- `workspace_members`: id, workspace_id, user_id, role (owner/admin/member), invited_by, joined_at
- `websites`: id, workspace_id, name, url, script_key (unique, token_urlsafe(32)), is_active, show_feedback_by_default
- `feedback`: id, website_id, page_url, commenter info, session_id, content, feedback_type, status, position (x/y/selector), browser/OS/viewport info, screenshot_path, admin_response, timestamps

## API Endpoints (planned)
See `docs/API.md` (TBD) for full documentation.

## Development
1. `cp .env.example .env`
2. `docker-compose up -d`
3. Backend: http://localhost:8000 (docs at /docs)
4. Frontend: http://localhost:80
5. Widget: http://localhost:8080/widget.js
