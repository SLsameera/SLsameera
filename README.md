# Pivisuma Full-Stack App

A full‑stack web application for global tree‑planting records with GIS mapping, rewards, and eco‑commerce.

## Stack
- Frontend: Next.js (App Router) + TypeScript + Tailwind CSS + Leaflet
- Backend: FastAPI + SQLAlchemy + GeoAlchemy2
- Database: PostgreSQL + PostGIS
- Auth: JWT + OAuth (Google/Apple/Facebook via Authlib)
- Storage: S3/Cloudinary (configurable)
- Hosting: Vercel (frontend), Render/AWS (backend), Supabase/AWS RDS (DB)

## Quickstart (Docker)

1) Copy env files
```bash
cp .env.example .env
cp frontend/.env.example frontend/.env.local
cp backend/.env.example backend/.env
```

2) Build and start
```bash
docker compose up --build
```

- Frontend: http://localhost:3000
- Backend: http://localhost:8000/docs
- Postgres: localhost:5432

## Local Dev (no Docker)

Frontend
```bash
cd frontend
npm install
npm run dev
```

Backend
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Database
- Default dev DB runs in Docker with PostGIS.
- To apply migrations (later):
```bash
cd backend
alembic upgrade head
```

## Monorepo Structure
```
frontend/   # Next.js + Tailwind + Leaflet
backend/    # FastAPI + SQLAlchemy + GeoAlchemy2
.github/    # CI workflows
```

## License
MIT
