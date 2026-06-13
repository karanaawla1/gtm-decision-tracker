# GTM Decision Tracker — Backend 

> ROI Attribution Engine for B2B SaaS GTM teams — track decisions, link outcomes, and get automatic SCALE/KILL/MAINTAIN/MONITOR recommendations based on time-decay weighted ROI.

---

## 🎯 Problem It Solves

GTM teams make dozens of decisions every quarter — hire an SDR, run Facebook ads, buy a tool — but rarely know which ones actually drove revenue. This engine connects decisions to outcomes and scores each one with a confidence-weighted ROI.

---

## 🏗️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11+, FastAPI |
| Database | PostgreSQL + SQLAlchemy ORM |
| Migrations | Alembic |
| Cache | Redis |
| Background Jobs | Celery |
| Data Pipeline | Pandas (CSV ingestion) |
| API Docs | Swagger UI (auto-generated) |
| Containerization | Docker + docker-compose |

---

## ⚙️ Core Features

- ✅ **Time-decay attribution** — recent outcomes weighted higher (`e^(-λt)`)
- ✅ **Confidence scoring** — 0.0 to 1.0 based on data volume + consistency
- ✅ **SCALE / KILL / MAINTAIN / MONITOR** recommendations
- ✅ **Bulk CSV upload** — ingest historical decisions in one shot
- ✅ **Redis caching** — ~80% faster repeated analysis calls, with cache invalidation on updates
- ✅ **Celery workers** — overnight batch sync of all decision scores
- ✅ **Full REST API** — CRUD + bulk analysis + dashboard summary
- ✅ **Auto Swagger docs** — zero-config interactive API documentation
- ✅ **CORS configured** — ready to connect with any frontend

---

## 📊 Attribution Logic

```
Decision (e.g. SDR hire, Jan 1)
        │
        ▼
Outcomes (revenue in Feb, Mar, Apr)
        │
        ▼
Time-decay weight = e^(-λ × days_since_decision)
        │
        ▼
Weighted ROI = Σ(outcome_value × weight) / cost_amount
        │
        ▼
Confidence = f(number of data points, consistency)
```

| Condition | Recommendation |
|---|---|
| ROI > 3x AND Confidence > 0.7 | 🚀 SCALE |
| ROI < 0.5x AND Confidence > 0.6 | 🔴 KILL |
| Confidence < 0.6 | 👀 MONITOR |
| Otherwise | ✅ MAINTAIN |

---

## 🚀 Quick Start (Local)

### 1. Clone & Setup
```bash
git clone https://github.com/karanaawla1/gtm-decision-tracker.git
cd gtm-decision-tracker
python -m venv venv
venv\Scripts\activate   # Windows
# source venv/bin/activate   # Mac/Linux
pip install -r requirements.txt
```

### 2. Environment Variables
Create a `.env` file in the project root:
```dotenv
DATABASE_URL=postgresql://postgres:password@localhost:5432/gtm_tracker
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key
DEBUG=True
```

### 3. Database Setup
```bash
psql -U postgres -c "CREATE DATABASE gtm_tracker;"
```

### 4. Run the Server
```bash
uvicorn app.main:app --reload
```

### 5. API Docs
Visit: **http://localhost:8000/docs**

### 6. (Optional) Run Redis + Celery
```bash
# Redis (separate terminal)
redis-server

# Celery worker (separate terminal)
celery -A app.tasks.celery_app worker --loglevel=info --pool=solo
```

---

## 🐳 Run with Docker (One Command)

```bash
docker-compose up
```

This starts PostgreSQL, Redis, the FastAPI API, and a Celery worker together.

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/decisions/` | Create a new decision |
| GET | `/api/decisions/` | List all decisions |
| GET | `/api/decisions/summary` | Dashboard stats (counts, avg ROI, recommendation breakdown) |
| GET | `/api/decisions/bulk-analysis` | ROI + recommendation for all decisions at once |
| GET | `/api/decisions/{id}/analysis` | Single decision ROI analysis |
| PATCH | `/api/decisions/{id}` | Update a decision |
| DELETE | `/api/decisions/{id}` | Delete a decision (and its outcomes) |
| POST | `/api/decisions/upload-csv` | Bulk CSV upload |
| POST | `/api/outcomes/` | Add an outcome to a decision |
| GET | `/api/outcomes/{decision_id}` | Get outcomes for a decision |

---

## 📁 Project Structure

```
gtm-decision-tracker/
├── app/
│   ├── api/
│   │   ├── decisions.py       # CRUD + analysis endpoints
│   │   └── outcomes.py        # Outcome endpoints
│   ├── models/
│   │   ├── decision.py         # SQLAlchemy Decision model
│   │   └── outcome.py          # SQLAlchemy Outcome model
│   ├── services/
│   │   ├── attribution.py      # Time-decay ROI engine
│   │   └── cache.py             # Redis caching layer
│   ├── pipelines/
│   │   └── csv_pipeline.py      # ETL pipeline
│   ├── tasks/
│   │   ├── celery_app.py        # Celery configuration
│   │   └── sync_tasks.py        # Background job tasks
│   ├── core/
│   │   └── config.py            # Settings from .env
│   ├── database.py               # DB connection + session
│   └── main.py                   # FastAPI app entry point
├── alembic/                       # Database migrations
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── .env
```

---

## 🌐 Live Demo

- **Frontend:** [GTM Tracker Dashboard](https://gtm-frontend-production.up.railway.app)
- **Backend API Docs:** (link to be added once deployed on Render)

---

## 📄 CSV Upload Format

```csv
type, date, owner, cost_amount, description
hire, 2024-01-15, Sales Team, 8000, SDR hire Q1
ad_spend, 2024-01-20, Marketing, 5000, Google Ads January campaign
tool, 2024-02-01, Engineering, 500, GitHub Copilot subscription
```

---

## 🔗 Related Repository

Frontend: [gtm-frontend](https://github.com/karanaawla1/gtm-frontend) — Next.js + TypeScript + Tailwind CSS dashboard
