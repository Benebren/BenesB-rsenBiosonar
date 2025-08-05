from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any
import requests
import pandas as pd
from indicators import compute_indicators
from scoring import evaluate_conditions, score_from_conditions

Twelve_API_KEY = "92f06ae57fa0459086049b49161765e1"
BASE_URL = "https://api.twelvedata.com/time_series"

app = FastAPI()

# CORS-Freigabe für Vercel und allgemein
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*", "https://benes-b-rsen-biosonar-7safv7pvz-benebrens-projects.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

def fetch_history(symbol: str) -> pd.DataFrame:
    params = {
        "symbol": symbol,
        "interval": "1day",
        "outputsize": 300,
        "apikey": Twelve_API_KEY
    }
    response = requests.get(BASE_URL, params=params)
    data = response.json()

    if "values" not in data:
        return pd.DataFrame()

    df = pd.DataFrame(data["values"])
    df = df.rename(columns={
        "datetime": "Date", "open": "Open", "high": "High",
        "low": "Low", "close": "Close", "volume": "Volume"
    })
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values("Date")
    df[["Open", "High", "Low", "Close", "Volume"]] = df[
        ["Open", "High", "Low", "Close", "Volume"]
    ].astype(float)
    return df

def analyze_symbol(symbol: str) -> Dict[str, Any]:
    df = fetch_history(symbol)
    if df is None or df.empty or len(df) < 50:
        return {"symbol": symbol, "error": "not_enough_data", "debug": {"rows": len(df)}}

    df = compute_indicators(df)
    if len(df) < 2:
        return {"symbol": symbol, "error": "not_enough_data", "debug": {"rows": len(df)}}

    prev = df.iloc[-2]
    curr = df.iloc[-1]

    flags = evaluate_conditions(prev, curr)
    score = score_from_conditions(flags)

    return {
        "symbol": symbol,
        "price": float(curr["Close"]),
        "score": score,
        "conditions": flags,
        "debug": {"rows": len(df)}
    }

@app.get("/analyze")
def analyze(symbols: str = Query(..., description="Comma separated tickers, e.g. AAPL,BTC/USD")):
    syms = [s.strip() for s in symbols.split(",") if s.strip()]
    results = [analyze_symbol(s) for s in syms]
    sorted_res = sorted(results, key=lambda x: x.get("score", -1), reverse=True)
    return {"results": sorted_res}
