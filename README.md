# Qafied

Visual feedback tool for web developers. Drop a script tag onto any website, and visitors can place comments directly on specific elements. Manage incoming feedback from a workspace-based dashboard.

## Features

- User authentication with JWT
- Multi-workspace support with roles (owner, admin, member)
- 3-member tier limit per workspace
- Add any website by URL — get a unique embed script
- Visitors click anywhere on a page to leave feedback
- Optional screenshots, captured client-side via `html2canvas`
- Automatic browser/OS/viewport detection
- Anonymous comments allowed (name/email optional)
- Show widget by default OR gate behind `?feedback=on`

## Architecture

- **Backend** — FastAPI + SQLAlchemy 2.0 + PostgreSQL 15 (JWT auth)
- **Frontend** — Vite + React 18 + TypeScript + Tailwind CSS + shadcn-style UI
- **Widget** — Vanilla TypeScript IIFE built with Rollup, html2canvas for screenshots
- **Deployment** — Docker Compose

## Quick start

```bash
cp .env.example .env
docker-compose up -d
```

Then open:

- Frontend dashboard: http://localhost (port 80)
- Backend API + Swagger UI: http://localhost:8000/docs
- Widget JS: http://localhost:8080/widget.js
- Postgres: localhost:5432

## Embedding the widget

After creating a website in the dashboard, copy the generated tag into the `<head>` of your site:

```html
<script src="http://localhost:8080/widget.js" data-key="YOUR_SCRIPT_KEY"></script>
```

If you set the website's `show_feedback_by_default` to false, the widget stays hidden unless you append `?feedback=on` to the URL.

## Documentation

- `docs/API.md` — REST endpoints
- `docs/MEMORY.md` — implementation decisions and per-task notes
- `PLAN.md` — original implementation plan with progress checklist

## License

MIT
