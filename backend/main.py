from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, List
import requests
import pandas as pd
from indicators import compute_indicators
from scoring import evaluate_conditions, score_from_conditions

TWELVE_API_KEY = "92f06ae57fa0459086049b49161765e1"
BASE_URL = "https://api.twelvedata.com/time_series"

app = FastAPI()

# CORS: erlaubt alle vercel.app-Domains + optional deine eigene Domain
app.add_middleware(
    CORSMiddleware,
    allow_origin=["https://BenesBoersenBiosonar.vercel.app"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

def fetch_history(symbol: str) -> pd.DataFrame:
    """Holt Kursdaten von TwelveData; gibt immer einen DataFrame zurück (ggf. leer)."""
    params = {
        "symbol": symbol,
        "interval": "1day",
        "outputsize": 300,
        "apikey": TWELVE_API_KEY,
        "timezone": "UTC",
        "order": "ASC",  # aufsteigend nach Datum
    }
    try:
        r = requests.get(BASE_URL, params=params, timeout=15)
        r.raise_for_status()
        data = r.json()
    except Exception:
        # Netzwerk-/JSON-Fehler -> leerer DF, damit kein 500 entsteht
        return pd.DataFrame()

    # Fehler vom Provider (Rate-Limit, invalid symbol, …)
    if isinstance(data, dict) and data.get("status") == "error":
        return pd.DataFrame()

    if "values" not in data:
        return pd.DataFrame()

    df = pd.DataFrame(data["values"]).rename(
        columns={
            "datetime": "Date",
            "open": "Open",
            "high": "High",
            "low": "Low",
            "close": "Close",
            "volume": "Volume",
        }
    )
    try:
        df["Date"] = pd.to_datetime(df["Date"], utc=True)
        df = df.sort_values("Date")
        for col in ["Open", "High", "Low", "Close", "Volume"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        df = df.dropna(subset=["Open", "High", "Low", "Close"])
    except Exception:
        return pd.DataFrame()

    return df

def analyze_symbol(symbol: str) -> Dict[str, Any]:
    df = fetch_history(symbol)
    if df.empty or len(df) < 50:
        return {"symbol": symbol, "error": "not_enough_data", "debug": {"rows": int(len(df))}}

    df = compute_indicators(df)
    if len(df) < 2:
        return {"symbol": symbol, "error": "not_enough_data", "debug": {"rows": int(len(df))}}

    prev = df.iloc[-2]
    curr = df.iloc[-1]
    flags = evaluate_conditions(prev, curr)
    score = score_from_conditions(flags)

    return {
        "symbol": symbol,
        "price": float(curr["Close"]),
        "score": int(score),
        "conditions": flags,
        "debug": {"rows": int(len(df))},
    }

@app.get("/analyze")
def analyze(symbols: str = Query(..., description="Comma separated tickers, e.g. AAPL,BTC/USD")):
    syms: List[str] = [s.strip() for s in symbols.split(",") if s.strip()]
    results = [analyze_symbol(s) for s in syms]
    results_sorted = sorted(results, key=lambda x: x.get("score", -1), reverse=True)
    return {"results": results_sorted}
