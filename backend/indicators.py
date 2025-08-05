import pandas as pd
from ta.trend import EMAIndicator, ADXIndicator, MACD
from ta.momentum import RSIIndicator, StochasticOscillator
from ta.volatility import BollingerBands
from ta.volume import OnBalanceVolumeIndicator

def compute_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy().dropna()

    # EMAs
    df["ema50"] = EMAIndicator(close=df["Close"], window=50).ema_indicator()
    df["ema200"] = EMAIndicator(close=df["Close"], window=200).ema_indicator()

    # RSI
    df["rsi14"] = RSIIndicator(close=df["Close"], window=14).rsi()

    # MACD
    macd = MACD(close=df["Close"], window_slow=26, window_fast=12, window_sign=9)
    df["macd"] = macd.macd()
    df["macd_signal"] = macd.macd_signal()

    # Bollinger
    bb = BollingerBands(close=df["Close"], window=20, window_dev=2)
    df["bb_upper"] = bb.bollinger_hband()
    df["bb_middle"] = bb.bollinger_mavg()
    df["bb_lower"] = bb.bollinger_lband()

    # ADX
    adx = ADXIndicator(high=df["High"], low=df["Low"], close=df["Close"], window=14)
    df["adx14"] = adx.adx()

    # OBV
    df["obv"] = OnBalanceVolumeIndicator(close=df["Close"], volume=df["Volume"]).on_balance_volume()

    # Stochastic
    st = StochasticOscillator(high=df["High"], low=df["Low"], close=df["Close"], window=14, smooth_window=3)
    df["stoch_k"] = st.stoch()
    df["stoch_d"] = st.stoch_signal()

    return df.dropna()
