# === External libraries ===
from finta import TA
import pandas as pd
from src.ta.functions.plots.plot_indicators import plot_indicator


# ============================================================
# ADX
# ============================================================
def calculate_adx(df: pd.DataFrame, plot: bool = False, period: int = 14) -> pd.DataFrame:
    df['adx'] = TA.ADX(df, period)
    df['adx'] = df['adx'].mask(df.index < period)
    df = df.dropna(subset=['adx']).copy()

    result = df[['Date', 'adx']]

    if plot:
        plot_indicator(result, f"ADX ({period})")

    return result


# ============================================================
# MACD
# ============================================================
def calculate_macd(df: pd.DataFrame, plot: bool = False, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
    df['ema_fast'] = df['close'].ewm(span=fast, adjust=False).mean()
    df['ema_slow'] = df['close'].ewm(span=slow, adjust=False).mean()
    df['macd'] = df['ema_fast'] - df['ema_slow']
    df['signal'] = df['macd'].ewm(span=signal, adjust=False).mean()

    result = df[['Date', 'macd', 'signal', 'ema_fast', 'ema_slow']]

    if plot:
        plot_indicator(result, f"MACD ({fast}-{slow}-{signal})")

    return result


# ============================================================
# MA
# ============================================================
def calculate_ma(df: pd.DataFrame, plot: bool = False, period: int = 14) -> pd.DataFrame:
    df['ma'] = df['close'].rolling(window=period).mean()
    df['ma'] = df['ma'].mask(df.index < period)
    df = df.dropna(subset=['ma']).copy()

    result = df[['Date', 'ma']]

    if plot:
        plot_indicator(result, f"MA ({period})")

    return result


# ============================================================
# EMA
# ============================================================
def calculate_ema(df: pd.DataFrame, plot: bool = False, period: int = 14) -> pd.DataFrame:
    df['ema'] = df['close'].ewm(span=period, adjust=False).mean()
    df['ema'] = df['ema'].mask(df.index < period)
    df = df.dropna(subset=['ema']).copy()

    result = df[['Date', 'ema']]

    if plot:
        plot_indicator(result, f"EMA ({period})")

    return result


# ============================================================
# EMA Ribbon
# ============================================================
def calculate_ema_ribbon(df: pd.DataFrame, plot: bool = False, periods: list = [8, 13, 21, 34, 55, 89, 144, 233]) -> pd.DataFrame:
    for p in periods:
        df[f'ema_{p}'] = df['close'].ewm(span=p, adjust=False).mean()

    df = df.dropna(subset=[f'ema_{max(periods)}']).copy()

    result = df[['Date'] + [f'ema_{p}' for p in periods]]

    if plot:
        plot_indicator(result, f"EMA Ribbon {periods}")

    return result


# ============================================================
# EMA Crossover
# ============================================================
def calculate_ema_crossover(df: pd.DataFrame, plot: bool = False, fast: int = 9, slow: int = 21) -> pd.DataFrame:
    df['ema_fast'] = df['close'].ewm(span=fast, adjust=False).mean()
    df['ema_slow'] = df['close'].ewm(span=slow, adjust=False).mean()

    df['ema_signal'] = 0
    df.loc[df['ema_fast'] > df['ema_slow'], 'ema_signal'] = 1
    df.loc[df['ema_fast'] < df['ema_slow'], 'ema_signal'] = -1

    df = df.dropna(subset=['ema_fast', 'ema_slow']).copy()

    result = df[['Date', 'ema_fast', 'ema_slow', 'ema_signal']]

    if plot:
        plot_indicator(result, f"EMA Crossover ({fast}-{slow})")

    return result


# ============================================================
# Ichimoku Cloud
# ============================================================
def calculate_ichimoku(df: pd.DataFrame, plot: bool = False, tenkan: int = 9, kijun: int = 26, senkou: int = 52) -> pd.DataFrame:

    high = df['high']
    low = df['low']
    close = df['close']

    df['tenkan_sen'] = (high.rolling(tenkan).max() + low.rolling(tenkan).min()) / 2
    df['kijun_sen'] = (high.rolling(kijun).max() + low.rolling(kijun).min()) / 2
    df['senkou_span_a'] = ((df['tenkan_sen'] + df['kijun_sen']) / 2).shift(kijun)
    df['senkou_span_b'] = ((high.rolling(senkou).max() + low.rolling(senkou).min()) / 2).shift(kijun)
    df['chikou_span'] = close.shift(-kijun)

    df = df.dropna(subset=['tenkan_sen', 'kijun_sen', 'senkou_span_a', 'senkou_span_b']).copy()

    result = df[['Date', 'tenkan_sen', 'kijun_sen',
                 'senkou_span_a', 'senkou_span_b', 'chikou_span']]

    if plot:
        plot_indicator(result, f"Ichimoku ({tenkan}-{kijun}-{senkou})")

    return result
