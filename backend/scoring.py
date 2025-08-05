from typing import Dict

def evaluate_conditions(row_prev, row_curr) -> Dict[str, bool]:
    cond_trend = row_curr["ema50"] > row_curr["ema200"]
    cond_rsi = row_curr["rsi14"] < 30
    cond_macd_cross = (row_prev["macd"] <= row_prev["macd_signal"]) and (row_curr["macd"] > row_curr["macd_signal"])
    cond_bb_breakout = row_curr["Close"] > row_curr["bb_upper"]
    cond_adx = row_curr["adx14"] > 25
    cond_obv_up = (row_curr["obv"] > row_prev["obv"])
    cond_stoch_cross = (row_prev["stoch_k"] <= row_prev["stoch_d"]) and (row_curr["stoch_k"] > row_curr["stoch_d"]) and (row_curr["stoch_k"] < 25 or row_curr["stoch_d"] < 25)
    return {
        "trend_ema50_gt_ema200": cond_trend,
        "rsi14_lt_30": cond_rsi,
        "macd_crossover_up": cond_macd_cross,
        "close_gt_bb_upper": cond_bb_breakout,
        "adx14_gt_25": cond_adx,
        "obv_up": cond_obv_up,
        "stoch_crossover_up_20": cond_stoch_cross,
    }

def score_from_conditions(flags: Dict[str, bool]) -> int:
    return sum(1 for v in flags.values() if v)
