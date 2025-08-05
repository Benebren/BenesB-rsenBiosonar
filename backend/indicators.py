import numpy as np
import pandas as pd

def ema(series: pd.Series, span: int) -> pd.Series:
    return series.ewm(span=span, adjust=False).mean()

def rsi(series: pd.Series, window: int = 14) -> pd.Series:
    delta = series.diff()
    gain = np.where(delta > 0, delta, 0.0)
    loss = np.where(delta < 0, -delta, 0.0)
    roll_up = pd.Series(gain, index=series.index).rolling(window=window).mean()
    roll_down = pd.Series(loss, index=series.index).rolling(window=window).mean()
    rs = roll_up / (roll_down.replace(0, np.nan))
    rsi = 100 - (100 / (1 + rs))
    return rsi

def macd(series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
    macd_line = ema(series, fast) - ema(series, slow)
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    hist = macd_line - signal_line
    return macd_line, signal_line, hist

def bollinger_bands(series: pd.Series, window: int = 20, num_std: float = 2.0):
    mavg = series.rolling(window).mean()
    mstd = series.rolling(window).std(ddof=0)
    upper = mavg + num_std * mstd
    lower = mavg - num_std * mstd
    return upper, mavg, lower

def adx(high: pd.Series, low: pd.Series, close: pd.Series, window: int = 14) -> pd.Series:
    prev_close = close.shift(1)
    tr = pd.concat([high - low, (high - prev_close).abs(), (low - prev_close).abs()], axis=1).max(axis=1)
    plus_dm = high.diff()
    minus_dm = -low.diff()
    plus_dm = np.where((plus_dm > minus_dm) & (plus_dm > 0), plus_dm, 0.0)
    minus_dm = np.where((minus_dm > plus_dm) & (minus_dm > 0), minus_dm, 0.0)
    atr = pd.Series(tr).rolling(window).mean()
    plus_di = 100 * (pd.Series(plus_dm, index=high.index).rolling(window).sum() / atr)
    minus_di = 100 * (pd.Series(minus_dm, index=low.index).rolling(window).sum() / atr)
    dx = ((plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, np.nan)) * 100
    adx = dx.rolling(window).mean()
    return adx

def obv(close: pd.Series, volume: pd.Series) -> pd.Series:
    direction = np.sign(close.diff().fillna(0))
    return (direction * volume).fillna(0).cumsum()

def stochastic_oscillator(high: pd.Series, low: pd.Series, close: pd.Series, k_window: int = 14, d_window: int = 3):
    lowest_low = low.rolling(k_window).min()
    highest_high = high.rolling(k_window).max()
    k = 100 * (close - lowest_low) / (highest_high - lowest_low).replace(0, np.nan)
    d = k.rolling(d_window).mean()
    return k, d

def compute_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["ema50"] = ema(df["Close"], 50)
    df["ema200"] = ema(df["Close"], 200)
    df["rsi14"] = rsi(df["Close"], 14)
    macd_line, signal_line, _ = macd(df["Close"], 12, 26, 9)
    df["macd"] = macd_line
    df["macd_signal"] = signal_line
    bb_upper, bb_mid, bb_lower = bollinger_bands(df["Close"], 20, 2.0)
    df["bb_upper"] = bb_upper
    df["bb_mid"] = bb_mid
    df["bb_lower"] = bb_lower
    df["adx14"] = adx(df["High"], df["Low"], df["Close"], 14)
    df["obv"] = obv(df["Close"], df["Volume"])
    k, d = stochastic_oscillator(df["High"], df["Low"], df["Close"], 14, 3)
    df["stoch_k"] = k
    df["stoch_d"] = d
    return df.dropna()
