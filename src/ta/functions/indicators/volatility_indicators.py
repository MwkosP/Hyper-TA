# === External libraries ===
from finta import TA
import pandas as pd
from src.ta.functions.plots.plot_indicators import plot_indicator


# ============================================================
# Bollinger Bands
# ============================================================
def calculate_bbands(df: pd.DataFrame, plot: bool = False, period: int = 20, std: float = 2.0) -> pd.DataFrame:
    ma = df['close'].rolling(window=period).mean()
    std_dev = df['close'].rolling(window=period).std()

    df['bb_mid'] = ma
    df['bb_upper'] = ma + std * std_dev
    df['bb_lower'] = ma - std * std_dev

    df = df.dropna(subset=['bb_mid', 'bb_upper', 'bb_lower']).copy()

    result = df[['Date', 'bb_lower', 'bb_mid', 'bb_upper']]

    if plot:
        plot_indicator(result, f"Bollinger Bands (Period={period}, Std={std})")

    return result


# ============================================================
# ATR — Average True Range
# ============================================================
def calculate_atr(df: pd.DataFrame, plot: bool = False, period: int = 14) -> pd.DataFrame:
    df['atr'] = TA.ATR(df, period)
    df['atr'] = df['atr'].mask(df.index < period)
    df = df.dropna(subset=['atr']).copy()

    result = df[['Date', 'atr']]

    if plot:
        plot_indicator(result, f"ATR ({period})")

    return result


# ============================================================
# Donchian Channel
# ============================================================
def calculate_donchian(df: pd.DataFrame, plot: bool = False, period: int = 20) -> pd.DataFrame:
    df['donchian_upper'] = df['high'].rolling(window=period).max()
    df['donchian_lower'] = df['low'].rolling(window=period).min()
    df['donchian_mid'] = (df['donchian_upper'] + df['donchian_lower']) / 2

    df = df.dropna(subset=['donchian_upper']).copy()

    result = df[['Date', 'donchian_lower', 'donchian_mid', 'donchian_upper']]

    if plot:
        plot_indicator(result, f"Donchian Channel ({period})")

    return result
