# === External libraries ===
from finta import TA
import pandas as pd

from HyperTA.Indicators.utils import _transformForFinta


# =============================================================================
# MOMENTUM
# =============================================================================

def calculateRsi(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
    rsi = TA.RSI(_transformForFinta(df), period)
    return pd.DataFrame({"Date": df["Date"], "rsi": rsi})


def calculateStochrsi(df: pd.DataFrame, rsi_length: int = 14, stoch_length: int = 14, k: int = 3, d: int = 3) -> pd.DataFrame:
    rsi = TA.RSI(_transformForFinta(df), rsi_length)
    min_rsi = rsi.rolling(window=stoch_length).min()
    max_rsi = rsi.rolling(window=stoch_length).max()
    stoch_rsi = (rsi - min_rsi) / (max_rsi - min_rsi)
    k_line = stoch_rsi.ewm(span=k, adjust=False).mean()
    d_line = k_line.ewm(span=d, adjust=False).mean()
    return pd.DataFrame({"Date": df["Date"], "stochrsi_k": k_line, "stochrsi_d": d_line})


def calculateRoc(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
    close = df["Close"]
    roc = ((close - close.shift(period)) / close.shift(period)) * 100
    return pd.DataFrame({"Date": df["Date"], "roc": roc})


def calculateWilliams(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
    highest_high = df["High"].rolling(window=period).max()
    lowest_low = df["Low"].rolling(window=period).min()
    williams = -100 * ((highest_high - df["Close"]) / (highest_high - lowest_low))
    return pd.DataFrame({"Date": df["Date"], "williams": williams})


# =============================================================================
# TREND
# =============================================================================

def calculateAdx(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
    adx = TA.ADX(_transformForFinta(df), period)
    return pd.DataFrame({"Date": df["Date"], "adx": adx})


def calculateMacd(df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
    ema_fast = df["Close"].ewm(span=fast, adjust=False).mean()
    ema_slow = df["Close"].ewm(span=slow, adjust=False).mean()
    macd = ema_fast - ema_slow
    signal_line = macd.ewm(span=signal, adjust=False).mean()
    return pd.DataFrame({
        "Date": df["Date"],
        "macd": macd,
        "signal": signal_line,
        "ema_fast": ema_fast,
        "ema_slow": ema_slow,
    })


def calculateMa(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
    ma = df["Close"].rolling(window=period).mean()
    return pd.DataFrame({"Date": df["Date"], "ma": ma})


def calculateEma(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
    ema = df["Close"].ewm(span=period, adjust=False).mean()
    return pd.DataFrame({"Date": df["Date"], "ema": ema})


def calculateEmaRibbon(df: pd.DataFrame, periods: list = [8, 13, 21, 34, 55, 89, 144, 233]) -> pd.DataFrame:
    data = {"Date": df["Date"]}
    for p in periods:
        data[f"ema_{p}"] = df["Close"].ewm(span=p, adjust=False).mean()
    return pd.DataFrame(data)


def calculateEmaCrossover(df: pd.DataFrame, fast: int = 9, slow: int = 21) -> pd.DataFrame:
    ema_fast = df["Close"].ewm(span=fast, adjust=False).mean()
    ema_slow = df["Close"].ewm(span=slow, adjust=False).mean()
    ema_signal = (ema_fast > ema_slow).astype(int) - (ema_fast < ema_slow).astype(int)
    return pd.DataFrame({
        "Date": df["Date"],
        "ema_fast": ema_fast,
        "ema_slow": ema_slow,
        "ema_signal": ema_signal,
    })


def calculateIchimoku(df: pd.DataFrame, tenkan: int = 9, kijun: int = 26, senkou: int = 52) -> pd.DataFrame:
    high, low, close = df["High"], df["Low"], df["Close"]
    tenkan_sen = (high.rolling(tenkan).max() + low.rolling(tenkan).min()) / 2
    kijun_sen = (high.rolling(kijun).max() + low.rolling(kijun).min()) / 2
    senkou_span_a = ((tenkan_sen + kijun_sen) / 2).shift(kijun)
    senkou_span_b = ((high.rolling(senkou).max() + low.rolling(senkou).min()) / 2).shift(kijun)
    chikou_span = close.shift(-kijun)
    return pd.DataFrame({
        "Date": df["Date"],
        "tenkan_sen": tenkan_sen,
        "kijun_sen": kijun_sen,
        "senkou_span_a": senkou_span_a,
        "senkou_span_b": senkou_span_b,
        "chikou_span": chikou_span,
    })


# =============================================================================
# VOLATILITY
# =============================================================================

def calculateBbands(df: pd.DataFrame, period: int = 20, std: float = 2.0) -> pd.DataFrame:
    ma = df["Close"].rolling(window=period).mean()
    std_dev = df["Close"].rolling(window=period).std()
    return pd.DataFrame({
        "Date": df["Date"],
        "bb_lower": ma - std * std_dev,
        "bb_mid": ma,
        "bb_upper": ma + std * std_dev,
    })


def calculateAtr(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
    atr = TA.ATR(_transformForFinta(df), period)
    return pd.DataFrame({"Date": df["Date"], "atr": atr})


def calculateDonchian(df: pd.DataFrame, period: int = 20) -> pd.DataFrame:
    upper = df["High"].rolling(window=period).max()
    lower = df["Low"].rolling(window=period).min()
    return pd.DataFrame({
        "Date": df["Date"],
        "donchian_lower": lower,
        "donchian_mid": (upper + lower) / 2,
        "donchian_upper": upper,
    })


# =============================================================================
# VOLUME
# =============================================================================
# (no volume indicators yet)
