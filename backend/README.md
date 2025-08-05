# Backend (FastAPI)

## Start local
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

## Environment
- `ANALYZE_DEFAULT_SYMBOLS` (optional): comma-separated list of symbols to analyze by default.
- For Crypto use Yahoo-style tickers like `BTC-USD`, `ETH-USD`, `SOL-USD`.

## Endpoints
- `GET /health` → health check
- `GET /analyze?symbols=AAPL,BTC-USD` → returns ranking + indicator details