# GTM Decision Tracker 🚀

> ROI Attribution Engine for B2B SaaS GTM teams

Track every GTM decision (hires, ad spend, vendors, tools) and automatically calculate whether to **SCALE**, **KILL**, **MAINTAIN**, or **MONITOR** it — using time-decay weighted attribution.

---

## 🎯 Problem It Solves

GTM teams make dozens of decisions every quarter — hire an SDR, run Facebook ads, buy a tool — but rarely know which ones actually drove revenue. This engine connects decisions to outcomes and scores them with confidence.

---

## 🏗️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11, FastAPI |
| Database | PostgreSQL + SQLAlchemy ORM |
| Cache | Redis (analysis results) |
| Background Jobs | Celery (overnight batch sync) |
| Data Pipeline | Pandas (CSV ingestion) |
| API Docs | Swagger UI (auto-generated) |

---

## ⚙️ Core Features

- ✅ **Time-decay attribution** — recent outcomes weighted higher (`e^(-λt)`)
- ✅ **Confidence scoring** — 0.0 to 1.0 based on data volume + consistency  
- ✅ **SCALE / KILL / MAINTAIN / MONITOR** recommendations
- ✅ **Bulk CSV upload** — ingest historical decisions in one shot
- ✅ **Redis caching** — ~80% faster repeated analysis calls
- ✅ **Celery workers** — overnight batch sync of all decision scores
- ✅ **REST API** — full CRUD + bulk analysis endpoint
- ✅ **Auto Swagger docs** — zero config API documentation

---

## 📊 Attribution Logic

Decision (SDR hire, Jan 1) → Outcomes (revenue in Feb, Mar, Apr)

↓

Time-decay weight = e^(-0.02 * days)

↓

Weighted ROI = Σ(outcome * weight) / cost

↓

Confidence = f(data points, consistency)

| Condition | Recommendation |
|---|---|
| ROI > 3x AND Confidence > 0.7 | 🚀 SCALE |
| ROI < 0.5x AND Confidence > 0.6 | 🔴 KILL |
| Confidence < 0.6 | 👀 MONITOR |
| Otherwise | ✅ MAINTAIN |

---

## 🚀 Quick Start

### 1. Clone & Setup
```bash
git clone https://github.com/YOUR_USERNAME/gtm-decision-tracker.git
cd gtm-decision-tracker
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 2. Environment Variables
```bash
# .env file banao
DATABASE_URL=postgresql://postgres:password@localhost:5432/gtm_tracker
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=mysecretkey123
DEBUG=True
```

### 3. Database Setup
```bash
psql -U postgres -c "CREATE DATABASE gtm_tracker;"
```

### 4. Run Server
```bash
uvicorn app.main:app --reload
```

### 5. API Docs
http://localhost:8000/docs
---

## 📡 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/decisions/` | Create new decision |
| GET | `/api/decisions/` | List all decisions |
| GET | `/api/decisions/summary` | Dashboard stats (counts, avg ROI) |
| GET | `/api/decisions/bulk-analysis` | ROI for all decisions at once |
| GET | `/api/decisions/{id}/analysis` | Single decision ROI analysis |
| PATCH | `/api/decisions/{id}` | Update decision |
| DELETE | `/api/decisions/{id}` | Delete decision |
| POST | `/api/decisions/upload-csv` | Bulk CSV upload |
| POST | `/api/outcomes/` | Add outcome to decision |
| GET | `/api/outcomes/{decision_id}` | Get outcomes for decision |

---

## 📁 Project Structure

gtm-decision-tracker/

├── app/

│   ├── api/

│   │   ├── decisions.py    # CRUD + analysis endpoints

│   │   └── outcomes.py     # Outcome endpoints

│   ├── models/

│   │   ├── decision.py     # SQLAlchemy Decision model

│   │   └── outcome.py      # SQLAlchemy Outcome model

│   ├── services/

│   │   ├── attribution.py  # Time-decay ROI engine

│   │   └── cache.py        # Redis caching layer

│   ├── pipelines/

│   │   └── csv_pipeline.py # ETL pipeline

│   ├── tasks/

│   │   ├── celery_app.py   # Celery configuration

│   │   └── sync_tasks.py   # Background job tasks

│   ├── core/

│   │   └── config.py       # Settings from .env

│   ├── database.py         # DB connection + session

│   └── main.py             # FastAPI app entry point

├── requirements.txt

└── .env

---

## 🎤 Interview Talking Points

- *"Built time-decay weighted correlation engine with 0-1 confidence scoring"*
- *"Designed ETL pipeline ingesting CSV and REST APIs into normalized PostgreSQL schema"*  
- *"Implemented Redis caching layer reducing repeated computation by ~80%"*
- *"Built async Celery workers for overnight batch data sync with failure recovery"*