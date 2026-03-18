# 🇮🇳 Trade Opportunities API

AI-powered FastAPI service that analyzes market data and provides structured
trade opportunity insights for sectors in India. Built with Gemini AI + live web search.

---

## Quick Start

```bash
# 1. Create virtual environment
py -3.14 -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Mac/Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start the server
python run.py
```

Then open **http://localhost:8000/app** in your browser.

---

## Usage

| URL | What it does |
|-----|-------------|
| `http://localhost:8000/app` | Full UI — login, select sector, get report |
| `http://localhost:8000/docs` | Interactive API documentation |
| `http://localhost:8000/health` | Server health check |

---

## Demo Credentials

| Username | Password |
|----------|----------|
| `admin` | `password123` |
| `analyst` | `trade2024!` |
| `guest` | `guest123` |

---

## Supported Sectors

pharmaceuticals, technology, agriculture, textiles, automotive,
renewable_energy, chemicals, electronics, food_processing, gems_and_jewellery,
steel, defence, aerospace, fintech, healthcare, education, logistics,
real_estate, retail, telecommunications

---

## Project Structure

```
trade_api/
├── app.html              ← Frontend UI
├── run.py                ← Server entry point
├── requirements.txt
├── .env                  ← API keys (do not commit)
└── app/
    ├── main.py
    ├── routers/
    │   ├── auth.py       ← POST /auth/token
    │   └── analyze.py    ← GET  /analyze/{sector}
    ├── services/
    │   ├── session_store.py
    │   ├── web_search.py
    │   ├── ai_analysis.py
    │   └── cache.py
    ├── models/schemas.py
    └── middleware/rate_limiter.py
```

---

## Security Features

- Bearer token authentication (1-hour TTL)
- Sliding-window rate limiting (5 req/min on analyze endpoints)
- Input validation with sector allowlist
- In-memory session management with auto-expiry
- Global error handling — no stack traces exposed

---

## API Flow

1. `POST /auth/token` with credentials → get Bearer token
2. `GET /analyze/{sector}` with `Authorization: Bearer <token>` → get markdown report

Reports are cached for 5 minutes. Add `?refresh=true` to bypass cache.


"Note: Hosted on Render free tier — first load may take ~60 seconds to wake up."
