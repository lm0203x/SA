# Repository Guidelines

## Project Structure & Modules
- `app/`: Flask API, WebSocket handlers, services, SQLAlchemy models; entry `run.py`; config `config.py`; bootstrap scripts in repo root (`create_ai_config_table.py`, `create_ai_analysis_table.py`, `create_system_config_table.py`, `init_alert_records_db.py`).
- `web/`: React 18 + Vite frontend; UI in `web/src/components`, API helpers in `web/src/services/api.js`, WebSocket client in `web/src/services/websocket.js`.
- `docs/`: design/API notes; update when routes, schema, or flows change.
- `logs/`: runtime logs; keep out of commits.

## Build, Run, Develop
- Backend setup: `pip install -r requirements_minimal.txt`; set DB creds in `config.py` or env; start API+WebSocket with `python run.py` (port 5000).
- DB init (first run or schema reset): run the bootstrap scripts above in order as needed; verify tables created in MySQL.
- Frontend: `cd web && pnpm install && pnpm dev` for local dev; `pnpm build` for production bundle; `pnpm lint` for ESLint checks.

## Coding Style & Naming
- Python: PEP8, 4-space indent, type hints preferred; functions snake_case, classes PascalCase; no bare `except`; return JSON via unified schema; keep DB logic in `services/` or `models/`, not directly in routes.
- Concurrency/IO: wrap outbound calls with timeouts; close sessions; avoid shared mutable globals without locks.
- React: functional components + hooks; files/components PascalCase (e.g., `AlertRules.jsx`); shared helpers in `src/lib`; use `src/services/api.js` for HTTP wrappers; Tailwind for styling.

## Testing
- Integration smoke: `python test_alert_records.py` (requires backend on :5000 and seeded DB); add new scripts as `test_*.py` alongside backend.
- Frontend: manual UI check plus `pnpm lint`; add Jest/Vitest later if you introduce complex logic.

## Commit & PR
- Commits: short verb + scope in Chinese (e.g., "实现webhook后端接口"); present tense; avoid WIP.
- PRs: include change summary, risk/rollback, test evidence (command output or UI screenshot), linked issue; call out schema changes explicitly.

## Security & Config
- Never commit `.env`, DB creds, or Tushare tokens; `.gitignore` already covers them.
- MySQL: ensure indexes match query patterns in models; keep transactions short to avoid lock contention.
- WebSocket: validate payloads server-side and cap subscriptions per client to avoid broadcast abuse.

## Context & Improvement (background/design/risks/optimizations)
- Background: real-time stock anomaly monitoring with alerting; frontend consumes REST + WebSocket; MySQL stores market and alert data.
- Design: React + Vite + Tailwind UI; Flask + Socket.IO + SQLAlchemy on backend; cache helpers in `app/utils/cache.py` for hot data.
- Risks/Tradeoffs: Tushare rate limits, alert tables becoming hot and slowing queries, WebSocket broadcast load, manual tests only.
- Optimization: add Redis cache with cache-aside + TTL for hot reads, introduce pytest + CI, run WebSocket load tests, consider alert table partitioning by date when volume grows.
