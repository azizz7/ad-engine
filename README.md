# Ad Performance Intelligence Engine

A web-based AI-powered analytics platform that analyzes digital advertising data and generates actionable insights for marketers.

## Features

- **Data Ingestion**: Upload CSV files with ad performance data
- **Analytics Engine**: Compute key metrics (CTR, CPC, CPA, ROAS)
- **Machine Learning**: Predict future performance, detect trends, cluster ads
- **Insights Layer**: Generate business-focused, plain-English insights

## Tech Stack

- **Frontend**: Next.js, React, Recharts
- **Backend**: Python, FastAPI, Pandas, Scikit-learn

## Getting Started

### Backend Setup

**Note:** This project works best with Python 3.11 or 3.12. Python 3.13 may have compatibility issues with some packages.

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env   # then set SECRET_KEY (see comment in the file)
uvicorn app.main:app --reload
```

If you encounter build errors with Python 3.13, consider using Python 3.11 or 3.12:
```bash
# Using pyenv (recommended)
pyenv install 3.12.7
pyenv local 3.12.7
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Backend runs on `http://localhost:8000`. On first login with no users in the
database, the credentials below bootstrap a default admin account:

```
email: admin@example.com
password: admin
```

To (re)create/reset that admin account directly:
```bash
python -m scripts.reset_admin
```

Run the test suite:
```bash
pytest
```

### Frontend Setup

```bash
cd frontend
npm install
cp .env.local.example .env.local   # set NEXT_PUBLIC_API_URL if not localhost:8000
npm run dev
```

Frontend runs on `http://localhost:3000`

## Project Structure

```
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app factory, middleware, router registration
│   │   ├── core/                # Config, security (JWT/hashing), logging, rate limiting
│   │   ├── db/                  # SQLAlchemy session/engine + data-access (crud) functions
│   │   ├── models/               # SQLAlchemy ORM models (User, Dataset, ...)
│   │   ├── schemas/              # Pydantic request/response models
│   │   ├── services/             # Business logic: analytics, ML, insights, ingestion,
│   │   │                         #   ad-platform integrations (all framework-agnostic)
│   │   └── api/routes/           # FastAPI routers (auth, datasets, integrations, health)
│   ├── scripts/                  # One-off operational scripts (e.g. reset_admin)
│   ├── tests/                    # pytest suite (unit + API integration tests)
│   └── requirements.txt
├── frontend/
│   ├── app/                 # Next.js app directory (pages)
│   ├── components/          # React components
│   ├── context/             # AuthContext (session state, axios auth wiring)
│   ├── lib/                 # Shared API client (axios instance, base URL)
│   └── package.json
└── README.md
```

### Backend architecture notes

- **`app/api/routes`** only handles HTTP concerns (request parsing, status
  codes, response shaping) and delegates everything else.
- **`app/services`** holds all business logic (metrics computation, ML
  training/prediction, insight generation, dataset ingestion) with no
  FastAPI or SQLAlchemy imports, so it can be unit-tested in isolation.
- **`app/db/crud.py`** is the only place that talks to the ORM for
  datasets; every read/write is scoped by `user_id` so one account can
  never see or delete another account's data.
- **`app/core/config.py`** centralizes all environment variables behind a
  single `Settings` object — no other module reads `os.environ` directly.

## API Endpoints

- `POST /api/upload` - Upload CSV file
- `GET /api/analytics` - Get computed analytics
- `GET /api/insights` - Get generated insights
- `GET /api/predictions` - Get ML predictions

## Sample Data Format

CSV files should include columns:
- `date` (required) - Date in YYYY-MM-DD format
- `impressions` (required) - Number of impressions
- `clicks` (required) - Number of clicks
- `spend` (required) - Amount spent in dollars
- `platform` (optional) - Advertising platform name
- `conversions` (optional) - Number of conversions
- `revenue` (optional) - Revenue generated in dollars
- `campaign_name` or `ad_name` (optional) - Campaign or ad identifier

A sample CSV file (`sample_data.csv`) is included in the root directory for testing.

## Features in Detail

### Analytics Engine
- Computes key performance metrics (CTR, CPC, CPA, ROAS)
- Identifies top and bottom performing ads
- Detects spend inefficiencies
- Analyzes performance trends over time

### Machine Learning
- **Predictions**: Random Forest regression model to forecast future revenue and conversions
- **Trend Detection**: Statistical analysis to identify performance trends
- **Clustering**: K-means clustering to group ads by performance behavior

### Insights Generation
- Business-focused, plain-English insights
- Actionable recommendations
- Priority-based insight categorization
- Budget allocation suggestions

## Development Notes

- Backend persists to SQLite (`backend/ad_engine.db`, gitignored) via SQLAlchemy;
  swap `DATABASE_URL` for a Postgres/MySQL URL to move to a real database.
- Datasets are scoped per-user (`Dataset.user_id`) — one account can never see
  or delete another account's uploads.
- Trained ML models are cached to disk per-dataset (`backend/models_cache/`,
  gitignored) and retrained on-demand if the cache is missing or invalid.
- Frontend and backend run on separate ports (3000 and 8000); the frontend's
  API base URL is configurable via `NEXT_PUBLIC_API_URL`.
- CORS is configured (via `CORS_ORIGINS`) to allow frontend-backend communication.
- Uploads without `revenue`/`conversions` columns are fully supported — those
  metrics report `null` (shown as "N/A" in the UI) rather than erroring.
- A minimal in-memory rate limiter protects `/token` against brute-force
  login attempts; replace with a shared store (e.g. Redis) for a
  multi-process deployment.

