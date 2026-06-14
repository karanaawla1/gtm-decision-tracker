# GTM Decision Tracker — Backend

> ROI Attribution Engine for B2B SaaS GTM teams. Tracks GTM decisions (hires, ad spend, vendors, tools) and scores them as **SCALE**, **MAINTAIN**, **MONITOR**, or **KILL** using time-decay weighted revenue attribution.

**Live API docs:** `https://gtm-decision-tracker-production.up.railway.app/docs`

---

## Tech Stack

- **FastAPI** — REST API framework
- **PostgreSQL** + SQLAlchemy ORM — data storage
- **Redis** — caching layer for ROI analysis
- **Celery** — background batch recalculation
- **Pandas** — CSV ETL pipeline
- **Docker / docker-compose** — local dev environment
- **Railway** — deployment

---

## Quick Start

```bash
git clone https://github.com/karanaawla1/gtm-decision-tracker.git
cd gtm-decision-tracker
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

Create a `.env` file:
```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/gtm_tracker
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=mysecretkey123
DEBUG=True
```

Run the server:
```bash
uvicorn app.main:app --reload
```

API docs available at `http://localhost:8000/docs`

### Run everything with Docker
```bash
docker-compose up
```
Starts: API + PostgreSQL + Redis + Celery worker.

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/decisions/` | Create a decision |
| GET | `/api/decisions/` | List decisions (pagination, filter, search, sort) |
| GET | `/api/decisions/summary` | Dashboard summary stats |
| GET | `/api/decisions/bulk-analysis` | ROI + recommendation for all decisions |
| GET | `/api/decisions/{id}/analysis` | ROI analysis for one decision |
| PATCH | `/api/decisions/{id}` | Update a decision |
| DELETE | `/api/decisions/{id}` | Delete a decision and its outcomes |
| POST | `/api/decisions/upload-csv` | Bulk import decisions via CSV |
| POST | `/api/outcomes/` | Add an outcome for a decision |
| GET | `/api/outcomes/{decision_id}` | Get outcomes for a decision |

### `GET /api/decisions/` query params

| Param | Example | Purpose |
|---|---|---|
| `page` | `?page=2` | Page number |
| `page_size` | `?page_size=10` | Items per page (max 100) |
| `type` | `?type=hire` | Filter by type: hire, ad_spend, vendor, tool |
| `status` | `?status=active` | Filter by status |
| `owner` | `?owner=Sales` | Filter by owner (partial match) |
| `search` | `?search=SDR` | Search owner + description |
| `sort_by` | `?sort_by=cost_amount` | Sort by: date, cost_amount, owner, type |
| `order` | `?order=asc` | asc or desc |

---

## Project Structure

```
app/
├── api/             # Route handlers (decisions, outcomes)
├── models/          # SQLAlchemy models
├── services/        # Attribution engine + Redis cache
├── pipelines/        # CSV ETL pipeline
├── tasks/           # Celery config + background jobs
├── core/            # Settings / config
├── database.py      # DB connection
└── main.py          # App entry point + CORS
```

---

<br>

# 📖 Detailed Documentation

## The Problem This Solves

A company makes several GTM decisions in a quarter — hiring an SDR, running ad campaigns, buying tools — and revenue comes in afterward. But nobody can tell **which decision actually drove that revenue**. This API solves that by letting teams log decisions, log outcomes, and get an automated ROI + recommendation per decision.

## How Recommendations Are Calculated

| Recommendation | Condition | Meaning |
|---|---|---|
| 🚀 SCALE | ROI > 3x AND Confidence > 0.7 | Strong returns, high certainty — invest more |
| 🔴 KILL | ROI < 0.5x AND Confidence > 0.6 | Poor returns, confirmed — cut this spend |
| 👀 MONITOR | Confidence < 0.6 | Not enough data yet |
| ✅ MAINTAIN | Everything else | Performing as expected |
| ⚪ NO_DATA | No outcomes linked | Nothing to analyze yet |

## Attribution Engine

The core logic answers: *if a decision was made in January and revenue came in June, how much credit should that revenue get?*

**Time-decay weighting:**
```
weight = e^(-λ × days_since_decision)
```
Recent outcomes get weight close to 1 (full credit); older outcomes decay exponentially toward 0.

**ROI:**
```
weighted_revenue = Σ (outcome_value × time_decay_weight)
ROI = weighted_revenue / decision_cost
```

**Confidence (0.0–1.0):** based on the number of linked outcomes and how consistent they are with each other. A decision with one outcome can show a huge ROI but low confidence — which is why it gets MONITOR instead of SCALE.

## Database Schema

**`decisions`**

| Column | Type | Description |
|---|---|---|
| id | UUID (PK) | Unique identifier |
| type | String | hire / ad_spend / vendor / tool |
| owner | String | Team or person responsible |
| cost_amount | Float | Amount spent |
| description | String | Free-text notes |
| status | String | active / archived |
| date | DateTime | When the decision was made |

**`outcomes`**

| Column | Type | Description |
|---|---|---|
| id | UUID (PK) | Unique identifier |
| decision_id | UUID (FK) | Links to a decision |
| metric_type | String | revenue / pipeline / churn |
| value | Float | Amount of the outcome |
| source | String | manual / csv / api |
| date | DateTime | When the outcome occurred |

One decision → many outcomes.

## CSV Import Format

```csv
type,date,owner,cost_amount,description
hire,2024-01-10,Sales Team,75000,SDR hire for outbound pipeline
ad_spend,2024-01-15,Marketing,40000,LinkedIn Ads Q1 campaign
```

CSV import only creates decisions (the cost side). Outcomes (revenue side) must be added separately via `POST /api/outcomes/` for ROI to be calculated.

Response shape:
```json
{ "message": "Import done!", "result": { "success": 5, "failed": 0, "errors": [] } }
```

## Caching (Redis)

- `/api/decisions/{id}/analysis` caches its result in Redis after first computation
- Subsequent requests for the same decision return instantly (`from_cache: true`)
- Cache is invalidated automatically on `PATCH` or `DELETE` of a decision

## Background Jobs (Celery)

Celery workers run independently of the API process and handle overnight batch recalculation of ROI/confidence scores across all decisions, refreshing the Redis cache without blocking user requests.

## Pagination, Filtering & Sorting Response Shape

`GET /api/decisions/` returns:
```json
{
  "items": [ /* array of decisions */ ],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total_items": 10,
    "total_pages": 1,
    "has_next": false,
    "has_prev": false
  }
}
```

## Deployment

| Component | Platform |
|---|---|
| API | Railway |
| Database | Railway PostgreSQL (auto-linked via `DATABASE_URL`) |
| CORS | Configured in `app/main.py` to allow the frontend origin |

## Links

- Frontend (live): `https://gtm-frontend-production.up.railway.app`
- API docs (Swagger): `https://gtm-decision-tracker-production.up.railway.app/docs`
- Frontend repo: `https://github.com/karanaawla1/gtm-frontend`
