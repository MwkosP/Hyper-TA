# === External libraries ===
from finta import TA
import pandas as pd
from src.ta.functions.plots.plot_indicators import plot_indicator
import numpy as np

# ============================================================
# RSI
# ============================================================
def calculate_rsi(df: pd.DataFrame, plot: bool = False, period: int = 14) -> pd.DataFrame:
    df['rsi'] = TA.RSI(df, period)
    df['rsi'] = df['rsi'].mask(df.index < period)
    df = df.dropna(subset=['rsi']).copy()

    result = df[['Date', 'rsi']]

    if plot:
        plot_indicator(result, f"RSI ({period})")

    return result


# ============================================================
# StochRSI
# ============================================================
def calculate_stochrsi(
        df: pd.DataFrame,
        rsi_length: int = 14,
        stoch_length: int = 14,
        k: int = 3,
        d: int = 3,
        plot: bool = False
    ) -> pd.DataFrame:

    # --- FIX: Normalize parameters so dispatcher can pass lists ---
    def _ensure_scalar(x):
        if isinstance(x, (list, tuple, set)):
            return list(x)[0]  # or max/min/mean, your preference
        return x

    rsi_length = _ensure_scalar(rsi_length)
    stoch_length = _ensure_scalar(stoch_length)
    k = _ensure_scalar(k)
    d = _ensure_scalar(d)
    # --------------------------------------------------------------

    rsi = TA.RSI(df, rsi_length)

    min_rsi = rsi.rolling(window=stoch_length).min()
    max_rsi = rsi.rolling(window=stoch_length).max()
    stoch_rsi = (rsi - min_rsi) / (max_rsi - min_rsi)

    df['stochrsi_k'] = stoch_rsi.ewm(span=k, adjust=False).mean()
    df['stochrsi_d'] = df['stochrsi_k'].ewm(span=d, adjust=False).mean()

    df = df.dropna(subset=['stochrsi_k', 'stochrsi_d']).copy()

    if plot:
        plot_indicator(df[['Date', 'stochrsi_k', 'stochrsi_d']],
                       f"StochRSI (RSI={rsi_length}, Stoch={stoch_length}, K={k}, D={d})")

    return df[['Date', 'stochrsi_k', 'stochrsi_d']]



# ============================================================
# ROC — Rate of Change
# ============================================================
def calculate_roc(df: pd.DataFrame, plot: bool = False, period: int = 14) -> pd.DataFrame:
    df['roc'] = ((df['close'] - df['close'].shift(period)) / df['close'].shift(period)) * 100
    df = df.dropna(subset=['roc']).copy()

    result = df[['Date', 'roc']]

    if plot:
        plot_indicator(result, f"ROC ({period})")

    return result


# ============================================================
# Williams %R
# ============================================================
def calculate_williams(df: pd.DataFrame, plot: bool = False, period: int = 14) -> pd.DataFrame:
    highest_high = df['high'].rolling(window=period).max()
    lowest_low = df['low'].rolling(window=period).min()

    df['williams'] = -100 * ((highest_high - df['close']) /
                             (highest_high - lowest_low))

    df = df.dropna(subset=['williams']).copy()

    result = df[['Date', 'williams']]

    if plot:
        plot_indicator(result, f"Williams %R ({period})")

    return result
