from fastapi import FastAPI, Query
from typing import List, Dict, Any
import yfinance as yf
import pandas as pd
from indicators import compute_indicators
from scoring import evaluate_conditions, score_from_conditions

app = FastAPI()
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # oder explizit ["https://deine-vercel-url.vercel.app"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

def analyze_symbol(symbol: str) -> Dict[str, Any]:
    hist = yf.download(symbol, period="6mo", interval="1d", progress=False)
    if hist is None or hist.empty or len(hist) < 220:
        return {"symbol": symbol, "error": "not_enough_data"}

    df = hist.rename(columns=str.title)  # Ensure 'Open','High','Low','Close','Volume'
    df = compute_indicators(df)
    if len(df) < 2:
        return {"symbol": symbol, "error": "not_enough_data"}

    prev = df.iloc[-2]
    curr = df.iloc[-1]

    flags = evaluate_conditions(prev, curr)
    score = score_from_conditions(flags)

    return {
        "symbol": symbol,
        "price": float(curr["Close"]),
        "score": score,
        "conditions": flags,
    }

@app.get("/analyze")
def analyze(symbols: str = Query(..., description="Comma separated tickers, e.g. AAPL,BTC-USD")):
    syms = [s.strip() for s in symbols.split(",") if s.strip()]
    results = [analyze_symbol(s) for s in syms]
    sorted_res = sorted(results, key=lambda x: x.get("score", -1), reverse=True)
    return {"results": sorted_res}
