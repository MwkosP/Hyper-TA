from .trend_indicators import *
from .momentum_indicators import *
from .volatility_indicators import *
from .universal_indicator_dispatcher import *


# 📌 Indicator mapping for API access
INDICATOR_MAP = {
    # --- Momentum ---
    "rsi": calculate_rsi,
    "williams": calculate_williams,
    "roc": calculate_roc,
    "stochrsi": calculate_stochrsi,

    # --- Trend ---
    "ma": calculate_ma,
    "ema": calculate_ema,
    "ema_ribbon": calculate_ema_ribbon,
    "ema_crossover": calculate_ema_crossover,
    "macd": calculate_macd,
    "adx": calculate_adx,

    # --- Volatility ---
    "bbands": calculate_bbands,
    "atr": calculate_atr,
    "donchian": calculate_donchian,
}



