# StockLedger

Zoho Inventory–style inventory and sales order management: items, customers, sales orders, stock tracking, reports, and a professional SaaS UI. Built with FastAPI, React, PostgreSQL, and Docker.

## Tech Stack

| Layer | Technologies |
|-------|-------------|
| Backend | Python, FastAPI, PostgreSQL, SQLAlchemy, Alembic, JWT, Pydantic |
| Frontend | React, Vite, Tailwind CSS, Redux Toolkit, React Router, Recharts |
| DevOps | Docker, Docker Compose, Nginx, GitHub Actions |

## Project Structure

```
inventory-saas/
├── backend/          # FastAPI API (clean architecture)
├── frontend/         # React SPA
├── nginx/            # Reverse proxy config
├── docker-compose.yml
└── .github/workflows/
```

## Quick Start (Docker)

```bash
cd inventory-saas
docker compose up --build
```

- Frontend: http://localhost (port 80)
- API docs: http://localhost:8000/docs
- Default admin (after seed): `admin@example.com` / `Admin123!`

With unified proxy profile:

```bash
docker compose --profile proxy up --build
# App via http://localhost:8080
```

## Local Development

### Backend

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Start PostgreSQL and update DATABASE_URL in .env
alembic upgrade head
python -m scripts.seed
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

## API Overview

Base URL: `/api/v1`

| Module | Endpoints |
|--------|-----------|
| Auth | `/auth/register`, `/auth/login`, `/auth/refresh`, `/auth/me` |
| Products | CRUD, stock adjust, image upload |
| Customers | CRUD, order history |
| Orders | Create (transactional), status updates |
| Dashboard | Stats, monthly sales, top products, low stock |
| Inventory | Product movement logs |

OpenAPI: `/docs`

## Roles

- **Admin** — Full access, user management
- **Manager** — Products, customers, orders, stock
- **Staff** — View data, create orders

## Deployment

### Frontend (Vercel)

1. Import `frontend/` as project root
2. Set `VITE_API_URL` to your production API (e.g. `https://api.example.com/api/v1`)
3. Deploy

### Backend (Render / Railway / Fly.io)

1. Deploy `backend/` with Dockerfile
2. Set environment variables from `backend/.env.example`
3. Use **Neon** or **Supabase** for PostgreSQL:
   - `DATABASE_URL=postgresql+asyncpg://...`
   - `DATABASE_URL_SYNC=postgresql+psycopg2://...`
4. Run migrations: `alembic upgrade head`
5. Seed: `python -m scripts.seed`

### Environment Variables

See `backend/.env.example` and `frontend/.env.example`. Never commit real secrets.

## Testing

```bash
# Backend
cd backend && pytest

# Frontend
cd frontend && npm test
```

## Security

- Bcrypt password hashing
- JWT access + refresh tokens
- CORS allowlist
- Rate limiting (SlowAPI)
- SQLAlchemy ORM (parameterized queries)
- Soft deletes on core entities

## License

MIT
