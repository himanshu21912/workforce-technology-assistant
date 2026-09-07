# Workforce Assistant — Frontend

Next.js App Router interface for the AI-Powered Workforce and Technology
Recommendation Assistant. It talks only to the FastAPI backend; there is no
direct access to PostgreSQL, Redis, Ollama, the MCP server, or GitHub.

## Requirements

- Node.js 20+ (developed on Node 26)
- A running backend on `NEXT_PUBLIC_API_BASE_URL` (default `http://localhost:8000`)

## Environment

Copy `.env.example` to `.env.local`:

```bash
cp .env.example .env.local
```

| Variable                   | Purpose                                  |
| -------------------------- | ---------------------------------------- |
| `NEXT_PUBLIC_API_BASE_URL` | Base URL of the FastAPI backend (public) |

Never put secrets in `NEXT_PUBLIC_*` variables: they are inlined into the
browser bundle.

## Commands

```bash
npm install      # install dependencies
npm run dev      # development server on http://localhost:3000
npm run build    # production build (also type-checks)
npm start        # serve the production build
npm run lint     # ESLint
npm test         # Vitest unit and integration tests
```

## Structure

```
src/
├── app/                 route entry, global styles, loading and error UI
├── components/
│   ├── layout/          app shell and off-canvas drawer
│   └── ui/              shared primitives (button, badge, dialog, toast…)
├── features/
│   ├── chat/            ask API, chat hooks, message rendering, composer
│   ├── sessions/        session API, session hooks, sidebar
│   ├── system-status/   health polling and status card
│   ├── project-info/    static project description panel
│   └── workspace/       screen that composes the three regions
├── hooks/               cross-feature hooks
├── lib/                 API client, endpoints, errors, formatting
└── test/                test helpers (fetch mock, fixtures)
```

Each feature owns its own `api/`, `schemas/`, `types/`, `hooks/`, and
`components/`. Backend responses are validated with Zod at the edge, so the
rest of the app works with fully typed data.

## Backend endpoints used

| Method | Path                        |
| ------ | --------------------------- |
| GET    | `/api/v1/health`            |
| GET    | `/api/v1/sessions`          |
| POST   | `/api/v1/sessions`          |
| GET    | `/api/v1/sessions/{id}`     |
| PATCH  | `/api/v1/sessions/{id}`     |
| DELETE | `/api/v1/sessions/{id}`     |
| POST   | `/api/v1/ask`               |
