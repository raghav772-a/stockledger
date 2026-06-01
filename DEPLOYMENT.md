# Deployment Guide — StockLedger

This guide covers **Docker Compose** (local/VPS), **Render** (free public URLs), **Vercel** (frontend alternative), and **GitHub Container Registry** (Docker images).

---

## 1. Docker Compose (full stack)

### Development

```bash
docker compose up --build
```

| Service  | URL |
|----------|-----|
| Web UI   | http://localhost |
| API      | http://localhost:8000 |
| API docs | http://localhost:8000/docs |

Default login (after seed): `admin@example.com` / `Admin123!`

### Production-style (local server)

```bash
# Set secrets first (example)
export SECRET_KEY="$(openssl rand -hex 32)"
export CORS_ORIGINS=https://your-domain.com

docker compose -f docker-compose.yml -f docker-compose.prod.yml up --build -d
```

---

## 2. Render (free hosting — recommended)

Render provides a **free PostgreSQL database**, **Docker API**, and **static frontend** with public HTTPS URLs.

### One-click deploy

1. Push this repo to GitHub: `https://github.com/raghav772-a/stockledger`
2. Open: **[Deploy to Render](https://render.com/deploy?repo=https://github.com/raghav772-a/stockledger)**
3. Sign in to Render and approve the Blueprint (`render.yaml`).
4. Wait for **stockledger-db**, **stockledger-api**, and **stockledger-web** to finish deploying (~10–15 min on free tier).

### Expected public URLs

| Service | URL |
|---------|-----|
| **Live app (UI)** | https://stockledger-web.onrender.com |
| **API** | https://stockledger-api.onrender.com |
| **API docs** | https://stockledger-api.onrender.com/docs |
| **Health** | https://stockledger-api.onrender.com/health |

> Free web services **spin down after ~15 minutes of inactivity**. The first request may take 30–60 seconds to wake up.

### After deploy — update CORS (if UI URL differs)

In Render Dashboard → **stockledger-api** → **Environment**:

- `CORS_ORIGINS` = your exact frontend URL (e.g. `https://stockledger-web.onrender.com`)

Redeploy the API service if you change this.

### Manual Render setup (without Blueprint)

1. Create **PostgreSQL** (free).
2. Create **Web Service** → Docker → root `backend/Dockerfile`, context `backend/`.
3. Set env vars from `backend/.env.example` + link `DATABASE_URL` / `DATABASE_URL_SYNC` from the database.
4. Create **Static Site** → root `frontend`, build `npm install && npm run build`, publish `dist`.
5. Set `VITE_API_URL=https://<your-api-host>/api/v1` on the static site.

---

## 3. Vercel (frontend only)

Use with a hosted API (e.g. Render backend).

1. Import the repo in [Vercel](https://vercel.com).
2. Set **Root Directory** to `frontend`.
3. Environment variable:
   - `VITE_API_URL` = `https://stockledger-api.onrender.com/api/v1`
4. Deploy.

Update backend `CORS_ORIGINS` to include your Vercel URL (e.g. `https://stockledger.vercel.app`).

---

## 4. Docker images (GHCR)

On every push to `main`, GitHub Actions publishes:

| Image | Pull |
|-------|------|
| Backend | `docker pull ghcr.io/raghav772-a/stockledger-backend:latest` |
| Frontend | `docker pull ghcr.io/raghav772-a/stockledger-frontend:latest` |

Package pages (after first successful workflow run):

- https://github.com/raghav772-a/stockledger/pkgs/container/stockledger-backend
- https://github.com/raghav772-a/stockledger/pkgs/container/stockledger-frontend

### Run published images locally

```bash
# Requires a Postgres instance and env vars — prefer docker compose for full stack
docker run --rm -p 8000:8000 \
  -e DATABASE_URL=postgresql+asyncpg://postgres:postgres@host.docker.internal:5432/inventory_db \
  -e DATABASE_URL_SYNC=postgresql+psycopg2://postgres:postgres@host.docker.internal:5432/inventory_db \
  -e SECRET_KEY=your-secret-min-32-chars \
  -e CORS_ORIGINS=http://localhost \
  ghcr.io/raghav772-a/stockledger-backend:latest
```

---

## 5. Environment variables

See `backend/.env.example` and `frontend/.env.example`.

| Variable | Required | Notes |
|----------|----------|--------|
| `DATABASE_URL` | Yes | Async SQLAlchemy URL (`postgresql+asyncpg://...`) |
| `DATABASE_URL_SYNC` | Yes | Alembic (`postgresql+psycopg2://...`) |
| `SECRET_KEY` | Yes | Min 32 random characters in production |
| `API_V1_PREFIX` | Yes | `/api/v1` |
| `CORS_ORIGINS` | Yes | Comma-separated frontend URLs |
| `AUTO_SEED` | No | `true` on first deploy only, then `false` |
| `VITE_API_URL` | Frontend build | Full API base including `/api/v1` |

---

## 6. Troubleshooting

| Issue | Fix |
|-------|-----|
| UI shows $0 / login fails | Check `VITE_API_URL` matches live API; hard-refresh browser |
| CORS error | Add frontend URL to `CORS_ORIGINS` on API |
| API 502 on Render | Check logs; DB must be linked; wait for migrations in entrypoint |
| Cold start slow | Normal on Render free tier — retry after 60s |

---

## 7. Submission checklist

Fill in [SUBMISSION.md](./SUBMISSION.md) with your live URLs after deploying, then push to GitHub.
