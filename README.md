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
uvicorn main:app --reload
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

Backend runs on `http://localhost:8000`

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on `http://localhost:3000`

## Project Structure

```
├── backend/
│   ├── main.py              # FastAPI application
│   ├── analytics.py         # Analytics engine
│   ├── ml_models.py         # ML models
│   ├── insights.py          # Insights generation
│   └── requirements.txt
├── frontend/
│   ├── app/                 # Next.js app directory
│   ├── components/          # React components
│   └── package.json
└── README.md
```

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

- Backend uses in-memory storage (for MVP). In production, use a database.
- ML models are trained on-demand when data is uploaded
- Frontend and backend run on separate ports (3000 and 8000)
- CORS is configured to allow frontend-backend communication

