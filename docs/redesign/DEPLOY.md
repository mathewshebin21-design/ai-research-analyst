# Deploying

Target: web app on Vercel, API and worker in one container on Render (or Fly.io), Postgres and auth on Supabase. The Streamlit app keeps deploying from `main` and is untouched until you switch links over.

## 1. Supabase

1. Create a project in an **EU or UK region** (the privacy notice and subprocessor list assume this).
2. Authentication → Providers: enable Email. Decide whether to require email confirmation.
3. Note: Project URL, anon key, database connection string (use the pooled `postgresql+psycopg://` form), and, if the project uses the legacy HS256 JWT secret, that secret.
4. Database → Backups: keep retention at 35 days or less.

## 2. API (Render web service from `backend/Dockerfile`)

| Variable | Value |
| --- | --- |
| `ENVIRONMENT` | `production` |
| `DATABASE_URL` | Supabase connection string |
| `AUTH_MODE` | `supabase` |
| `SUPABASE_URL` | Project URL |
| `SUPABASE_JWT_SECRET` | Only for HS256 projects; asymmetric projects use JWKS automatically |
| `CORS_ORIGINS` | `["https://<your-vercel-domain>"]` |
| `TAVILY_API_KEY`, `GEMINI_API_KEY` | Your keys (Gemini **paid** tier) |
| `STORAGE_DIR` | `/data/storage` on a persistent disk |
| `WORKER_IN_PROCESS` | `true` for one instance; `false` plus a separate worker service running `python -m intel.worker` to scale |

Health check path: `/ready` (fails until the database and both keys are configured). Migrations run on start (`alembic upgrade head`). The container refuses to start with `AUTH_MODE=dev` in production.

## 3. Web app (Vercel, root directory `frontend`)

| Variable | Value |
| --- | --- |
| `NEXT_PUBLIC_API_URL` | The API's public URL |
| `NEXT_PUBLIC_AUTH_MODE` | `supabase` |
| `NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_ANON_KEY` | From Supabase |

## 4. Before inviting users

- Work through `frontend/content/legal/LAUNCH_CHECKLIST.md` (company details, ICO fee, regions, paid Gemini tier, solicitor review).
- Record a real acceptance run and the verifier evaluation (see `evidence/2026-10-21-build-test-results.md`).
- Set log retention on Render and Vercel to 30 days.
- Replace the sample report with the recorded real run: `python -m intel.export_sample RUN_ID "A real run recorded on <date>. Not advice."`, then commit `frontend/public/sample-run.json`.

## Rollback

- The Streamlit app is still live from `main`; its last pre-redesign commit is `00e6826`. Tag it from your machine with `git tag v1-streamlit 00e6826 && git push origin v1-streamlit` (tag pushes were blocked from the build environment).
- New services run on separate URLs, so rolling back means pointing your link back at Streamlit.
- Database changes are Alembic migrations with downgrades (`alembic downgrade -1`); the Streamlit app does not read these tables.
