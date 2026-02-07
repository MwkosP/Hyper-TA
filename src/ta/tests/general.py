from src.ta.data.fetch_yfinance import download_underlying_stock
from src.ta.functions.indicators.universal_indicator_dispatcher import calculate_indicator
from src.ta.functions.indicators.threshold_functions import timeThreshold
import pandas as pd
import numpy as np



def timet(title, start, end, tmfrm, indicator_type, plot=False, **kwargs):
    """
    Fetches OHLCV data and calculates a chosen indicator via the universal dispatcher.

    Parameters:
        title (str): Ticker symbol (e.g., 'BTC-USD')
        start (str): Start date
        end (str): End date
        tmfrm (str): Timeframe (e.g., '1d', '1h')
        indicator_type (str): Indicator name ('rsi','ema','macd', etc.)
        plot (bool): Whether to plot
        **kwargs: Extra indicator parameters (period, fast, slow, etc.)

    Returns:
        pd.DataFrame: Indicator dataframe
    """
    df = download_underlying_stock(title=title, start=start, end=end, tmfrm=tmfrm, plot=False)

    result = calculate_indicator(df=df, type=indicator_type, plot=plot, **kwargs)
    print(result.head())

    # 2. Auto-pick column name for threshold check
    col = [c for c in result.columns if c != "Date"][0]

    # 3. Define defaults per indicator (you can expand this dictionary)
    default_levels = {
        "rsi": 40,
        "williams": -50,
        "roc": 0,
        "macd": 0,
        "adx": 20,
        "ema": None,  # price-based → no default
        "ma": None,
        "ema_crossover": None,
        "ema_ribbon": None,
        "ichimoku": None,
        "bbands": None,
        "atr": None,
        "donchian": None,
    }

    level = default_levels.get(indicator_type.lower(), None)
    if level is None:
        print(f"No default threshold for {indicator_type}. Returning raw indicator.")
        return result

    # 4. Call timeThreshold with defaults
    signals = timeThreshold(result, col=col, level=level,
                            direction="below", min_candles=3, wd=0)
    print("Threshold signals:\n", signals)  

    return result




