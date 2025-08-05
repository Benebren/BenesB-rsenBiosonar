import os
from typing import List, Dict, Any
import pandas as pd
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf

from indicators import compute_indicators
from scoring import evaluate_buy_conditions

app = FastAPI(title="BenesBörsenBiosonar API", version="0.1.0")

# Allow simple local dev & Vercel frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DEFAULT_SYMBOLS = os.getenv("ANALYZE_DEFAULT_SYMBOLS", "AAPL,MSFT,NVDA,TSLA,SPY,BTC-USD,ETH-USD,SOL-USD")

@app.get("/health")
def health():
    return {"status": "ok"}

def download_history(symbol: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
    df = yf.download(symbol, period=period, interval=interval, auto_adjust=True, progress=False)
    if df is None or df.empty:
        raise ValueError(f"Empty data for {symbol}")
    return df

@app.get("/analyze")
def analyze(symbols: str = Query(DEFAULT_SYMBOLS), period: str = "1y", interval: str = "1d") -> Dict[str, Any]:
    sym_list = [s.strip() for s in symbols.split(",") if s.strip()]
    results = []
    for sym in sym_list:
        try:
            raw = download_history(sym, period=period, interval=interval)
            df = compute_indicators(raw)
            if df.empty:
                raise ValueError(f"Insufficient data after indicators for {sym}")
            eval_res = evaluate_buy_conditions(df)
            last = df.iloc[-1]
            results.append({
                "symbol": sym,
                "close": float(last['Close']),
                "score": eval_res["score"],
                "conditions": eval_res["conditions"],
                "as_of": str(last.name)
            })
        except Exception as e:
            results.append({
                "symbol": sym,
                "error": str(e)
            })

    # Ranking by score desc, then by recent momentum (close vs ema50) as tie-breaker if available
    def momentum_key(item):
        # Use a simple proxy if available by recomputing quickly
        try:
            return float(item.get("close", 0.0))
        except Exception:
            return 0.0

    ranked = sorted(results, key=lambda x: (x.get("score", -1), momentum_key(x)), reverse=True)
    return {"period": period, "interval": interval, "results": ranked}