# pixforge

Backend for an AI image/video generation app. Python 3.12+, stdlib + sqlite3 only.

## Layout

- `pixforge/` — application code
  - `features/` — user-facing operations (generate an image, start a video)
  - `webhooks/` — inbound webhooks from partners
  - `billing.py`, `pricing.py`, `quota.py` — credits, prices, plan limits
  - `jobs.py` — job records and their status transitions
  - `sweeper.py` — periodic cleanup of stuck jobs
  - `i18n.py` + `locales/` — user-facing strings
  - `db.py` + `migrations/` — SQLite connection and schema migrations
- `lumen_sdk/` — vendored client SDK of Lumen, our generation provider (do not modify)
- `docs/lumen_api.md` — Lumen API reference (copied from their docs site)
- `tests/`

## Tests

```sh
python3 -m pytest
```
