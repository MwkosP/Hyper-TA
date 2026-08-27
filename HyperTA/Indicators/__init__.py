from .indicators import *
from .dispatcher import *

# Name -> calculator registry (internal convenience; prefer calculateIndicator())
INDICATOR_MAP = {
    "rsi": calculateRsi,
    "williams": calculateWilliams,
    "roc": calculateRoc,
    "stochrsi": calculateStochrsi,
    "ma": calculateMa,
    "ema": calculateEma,
    "ema_ribbon": calculateEmaRibbon,
    "ema_crossover": calculateEmaCrossover,
    "macd": calculateMacd,
    "adx": calculateAdx,
    "bbands": calculateBbands,
    "atr": calculateAtr,
    "donchian": calculateDonchian,
}
