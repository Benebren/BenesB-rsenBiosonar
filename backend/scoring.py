import numpy as np
import pandas as pd

def macd_cross_up(macd: pd.Series, signal: pd.Series) -> bool:
    if len(macd) < 2:
        return False
    prev = macd.iloc[-2] - signal.iloc[-2]
    curr = macd.iloc[-1] - signal.iloc[-1]
    return prev <= 0 and curr > 0

def stoch_cross_up_low(k: pd.Series, d: pd.Series, threshold: float = 20) -> bool:
    if len(k) < 2:
        return False
    prev_cross = k.iloc[-2] - d.iloc[-2]
    curr_cross = k.iloc[-1] - d.iloc[-1]
    # Below threshold recently and bullish cross now
    below = (k.iloc[-2] < threshold) and (d.iloc[-2] < threshold)
    return below and (prev_cross <= 0 and curr_cross > 0)

def obv_trending_up(obv: pd.Series, lookback: int = 5) -> bool:
    if len(obv) < lookback + 1:
        return False
    return obv.iloc[-1] > obv.iloc[-1 - lookback]

def evaluate_buy_conditions(df: pd.DataFrame) -> dict:
    row = df.iloc[-1]
    # Individual conditions
    cond_trend = bool(row['ema50'] > row['ema200'])
    cond_rsi = bool(row['rsi14'] < 30)
    cond_macd = macd_cross_up(df['macd'], df['macd_signal'])
    cond_bb = bool(row['Close'] > row['bb_upper'])
    cond_adx = bool(row['adx14'] > 25)
    cond_obv = obv_trending_up(df['obv'], lookback=5)
    cond_stoch = stoch_cross_up_low(df['stoch_k'], df['stoch_d'], threshold=20)

    conditions = {
        "trend_EMA50_gt_EMA200": cond_trend,
        "rsi14_lt_30": cond_rsi,
        "macd_cross_up": cond_macd,
        "close_gt_bb_upper": cond_bb,
        "adx14_gt_25": cond_adx,
        "obv_up": cond_obv,
        "stoch_cross_up_low": cond_stoch
    }

    score = int(sum(1 for v in conditions.values() if v))
    return {
        "score": score,
        "conditions": conditions
    }