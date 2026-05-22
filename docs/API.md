# Qafied API

Base URL: `http://localhost:8000`

Interactive Swagger docs are available at `/docs`.

All protected endpoints require a `Bearer <token>` header. Public widget endpoints authenticate via a `script_key` query parameter.

## Authentication

### `POST /auth/register`

Body:
```json
{ "email": "alice@example.com", "password": "secret123", "full_name": "Alice" }
```
Returns the created `User` (no token).

### `POST /auth/login`

Body:
```json
{ "email": "alice@example.com", "password": "secret123" }
```
Returns `{ "access_token": "...", "token_type": "bearer" }`. Tokens expire after `ACCESS_TOKEN_EXPIRE_MINUTES` (default 30).

### `GET /auth/me`

Returns the current authenticated user.

## Workspaces

### `POST /workspaces/`
Creates a workspace and adds the caller as `OWNER`. Body: `WorkspaceCreate`.

### `GET /workspaces/`
Lists all workspaces the caller is a member of.

### `GET /workspaces/{workspace_id}`
Returns the workspace plus its members (joined with user info).

### `POST /workspaces/{workspace_id}/invite`
Adds an existing user (by email) as a member. Enforces `max_members`. Body:
```json
{ "email": "bob@example.com", "role": "member" }
```

## Websites

All website endpoints require workspace membership.

### `POST /websites/?workspace_id={id}`
Creates a website. Body: `WebsiteCreate`. The server generates a `script_key`.

### `GET /websites/?workspace_id={id}`
Lists active websites in the workspace.

### `GET /websites/{website_id}`
Returns the website.

### `PATCH /websites/{website_id}`
Partial update (name, url, is_active, show_feedback_by_default).

### `DELETE /websites/{website_id}`
Soft-delete (`is_active=false`).

### `GET /websites/{website_id}/script`
Returns the `<script>` tag to embed.

## Feedback (admin)

All require workspace membership for the website.

### `GET /feedback/?website_id={id}&page_url=...&status=...`
List feedback (newest first), optionally filtered by page URL and status.

### `GET /feedback/grouped?website_id={id}`
Returns feedback grouped by `page_url`:
```json
[{ "page_url": "...", "count": 3, "items": [...] }]
```

### `PATCH /feedback/{feedback_id}/status?status=resolved`
Update status (`new` | `in_progress` | `resolved` | `closed`).

### `POST /feedback/{feedback_id}/response`
Body:
```json
{ "admin_response": "Fixed in v1.2" }
```

## Widget (public)

These endpoints authenticate via `script_key`, NOT a JWT.

### `GET /widget/config?key={script_key}`
Returns:
```json
{ "website_id": 1, "show_by_default": true, "enabled": true }
```

### `POST /widget/feedback?key={script_key}`
Submit a new comment. Body: `FeedbackCreate`. Important fields:

- `page_url` — full URL where the comment was placed
- `content` — comment text
- `feedback_type` — `change`|`remove`|`replace`|`bug`|`suggestion`|`other`
- `x_position`, `y_position`, `element_selector` — placement on the page
- `browser_info`, `os_info`, viewport/screen dims — auto-collected by the widget
- `include_screenshot` + `screenshot_data` — base64 PNG (data: URL also accepted)
- `commenter_name`, `commenter_email` — optional; absence makes the comment anonymous

Returns `{ "success": true, "feedback_id": 42 }`.

## Schema reference

Pydantic models live in `backend/app/schemas/`. The `FeedbackType` and `FeedbackStatus` enums plus `WorkspaceRole` map to TypeScript types in `frontend/src/types/index.ts`.
