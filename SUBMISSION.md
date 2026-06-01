# StockLedger — Project Submission

**Inventory & Order Management SaaS** (FastAPI · React · PostgreSQL · Docker)

---

## Repository

| Item | Link |
|------|------|
| **GitHub Repository** | https://github.com/raghav772-a/stockledger |

---

## Docker Images

Published to **GitHub Container Registry (GHCR)** on each push to `main`:

| Component | Image | Package page |
|-----------|--------|----------------|
| **Backend API** | `ghcr.io/raghav772-a/stockledger-backend:latest` | https://github.com/raghav772-a/stockledger/pkgs/container/stockledger-backend |
| **Frontend (Nginx)** | `ghcr.io/raghav772-a/stockledger-frontend:latest` | https://github.com/raghav772-a/stockledger/pkgs/container/stockledger-frontend |

Pull commands:

```bash
docker pull ghcr.io/raghav772-a/stockledger-backend:latest
docker pull ghcr.io/raghav772-a/stockledger-frontend:latest
```

> Images appear after the [Publish Docker images](https://github.com/raghav772-a/stockledger/actions/workflows/docker-publish.yml) workflow runs successfully.

---

## Live Application (Render — free tier)

Deploy using the [Render Blueprint](./render.yaml) or **[Deploy to Render](https://render.com/deploy?repo=https://github.com/raghav772-a/stockledger)**.

| Item | URL |
|------|-----|
| **Live Web Application** | https://stockledger-web.onrender.com |
| **Backend API** | https://stockledger-api.onrender.com |
| **API Documentation (Swagger)** | https://stockledger-api.onrender.com/docs |
| **Health Check** | https://stockledger-api.onrender.com/health |

**Demo credentials** (seeded on first deploy when `AUTO_SEED=true`):

- Email: `admin@example.com`
- Password: `Admin123!`

> If URLs are not live yet, complete deployment per [DEPLOYMENT.md](./DEPLOYMENT.md) and update this table with your actual Render service URLs.

---

## Docker Compose (local / demonstration)

```bash
git clone https://github.com/raghav772-a/stockledger.git
cd stockledger
docker compose up --build
```

- **UI:** http://localhost  
- **API:** http://localhost:8000/docs  

---

## Tech Stack Summary

| Layer | Technologies |
|-------|----------------|
| Backend | Python, FastAPI, PostgreSQL, SQLAlchemy, Alembic, JWT |
| Frontend | React, Vite, Tailwind CSS, Axios, Recharts |
| DevOps | Docker, Docker Compose, Nginx, GitHub Actions, Render |

---

## Features Delivered

- JWT authentication and role-based access  
- Products, customers, sales orders with stock validation  
- Automatic inventory deduction and cancellation restock  
- Inventory movement audit log  
- Live dashboard and analytics from PostgreSQL  
- Containerized deployment with public hosting support  

---

*Last updated: June 2026*
