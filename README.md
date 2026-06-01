# StockLedger

Zoho Inventory–style inventory and sales order management: items, customers, sales orders, stock tracking, reports, and a professional SaaS UI. Built with FastAPI, React, PostgreSQL, and Docker.

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/raghav772-a/stockledger)

## Submission & live URLs

See **[SUBMISSION.md](./SUBMISSION.md)** for:

- GitHub repository link  
- Docker image links (GHCR)  
- Live application URLs (Render)  

See **[DEPLOYMENT.md](./DEPLOYMENT.md)** for full deployment instructions.

## Tech Stack

| Layer | Technologies |
|-------|-------------|
| Backend | Python, FastAPI, PostgreSQL, SQLAlchemy, Alembic, JWT, Pydantic |
| Frontend | React, Vite, Tailwind CSS, Redux Toolkit, React Router, Recharts |
| DevOps | Docker, Docker Compose, Nginx, GitHub Actions, Render, GHCR |

## Project Structure

```
stockledger/
├── backend/              # FastAPI API
├── frontend/             # React SPA
├── docker-compose.yml    # Local full stack
├── docker-compose.prod.yml
├── render.yaml           # Render Blueprint (free cloud deploy)
├── DEPLOYMENT.md
├── SUBMISSION.md
└── .github/workflows/
```

## Quick Start (Docker)

```bash
git clone https://github.com/raghav772-a/stockledger.git
cd stockledger
docker compose up --build
```

| Service | URL |
|---------|-----|
| **Web UI** | http://localhost |
| **API docs** | http://localhost:8000/docs |
| **Login** | `admin@example.com` / `Admin123!` |

Production-style compose:

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up --build -d
```

## Cloud deployment (free)

1. Push to GitHub (or use the repo above).  
2. Click **Deploy to Render** (button at top) or open [this link](https://render.com/deploy?repo=https://github.com/raghav772-a/stockledger).  
3. Wait for services to build; use URLs from [SUBMISSION.md](./SUBMISSION.md).

Docker images are built automatically on `main` and published to:

- `ghcr.io/raghav772-a/stockledger-backend:latest`  
- `ghcr.io/raghav772-a/stockledger-frontend:latest`  

## Local Development

### Backend

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
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
| Inventory | Movement logs |

OpenAPI: `/docs`

## Testing

```bash
cd backend && pytest -q
cd frontend && npm test
```

## License

MIT
