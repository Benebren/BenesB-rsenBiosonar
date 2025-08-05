import pandas as pd
import pandas_ta as ta

def compute_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    # Basic sanity
    if df.isna().all().any():
        df = df.dropna()
    # EMAs
    df['ema50'] = ta.ema(df['Close'], length=50)
    df['ema200'] = ta.ema(df['Close'], length=200)
    # RSI
    df['rsi14'] = ta.rsi(df['Close'], length=14)
    # MACD
    macd = ta.macd(df['Close'], fast=12, slow=26, signal=9)
    df['macd'] = macd['MACD_12_26_9']
    df['macd_signal'] = macd['MACDs_12_26_9']
    # Bollinger Bands
    bb = ta.bbands(df['Close'], length=20, std=2)
    df['bb_upper'] = bb['BBU_20_2.0']
    df['bb_middle'] = bb['BBM_20_2.0']
    df['bb_lower'] = bb['BBL_20_2.0']
    # ADX
    adx = ta.adx(df['High'], df['Low'], df['Close'], length=14)
    df['adx14'] = adx['ADX_14']
    # OBV
    df['obv'] = ta.obv(df['Close'], df['Volume'])
    # Stochastic
    stoch = ta.stoch(df['High'], df['Low'], df['Close'], k=14, d=3, smooth_k=3)
    df['stoch_k'] = stoch['STOCHk_14_3_3']
    df['stoch_d'] = stoch['STOCHd_14_3_3']
    return df.dropna()