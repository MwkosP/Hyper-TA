# === External libraries ===
import pandas as pd

from .trend_indicators import *
from .momentum_indicators import *
from .volatility_indicators import *


#df here is from corresponding indicator. eg: df = Date, adx 
def calculate_indicator(df: pd.DataFrame, type: str, plot: bool = False, **kwargs) -> pd.DataFrame:
    type = type.lower()

    if type == 'rsi':
        return calculate_rsi(df, plot=plot, period=kwargs.get('period', 14))

    elif type == 'williams':
        return calculate_williams(df, plot=plot, period=kwargs.get('period', 14))

    elif type == 'ma':
        return calculate_ma(df, plot=plot, period=kwargs.get('period', 14))

    elif type == 'ema':
        return calculate_ema(df, plot=plot, period=kwargs.get('period', 14))

    elif type == 'ema_ribbon':
        return calculate_ema_ribbon(df,plot=plot,periods=kwargs.get('periods', [8, 13, 21, 34, 55, 89, 144, 233]))

    elif type == 'ema_crossover':
        return calculate_ema_crossover(df,plot=plot,fast=kwargs.get('fast', 9),slow=kwargs.get('slow', 21))

    elif type == 'macd':
        return calculate_macd(df,plot=plot,fast=kwargs.get('fast', 12),slow=kwargs.get('slow', 26),signal=kwargs.get('signal', 9))

    elif type == 'roc':
        return calculate_roc(df, plot=plot, period=kwargs.get('period', 14))
    
    #why result = .... ????
    elif type == 'stochrsi':
        result = calculate_stochrsi(df,plot=plot,rsi_length=kwargs.get('rsi_length', 14),stoch_length=kwargs.get('stoch_length', 14),k=kwargs.get('k', 3),d=kwargs.get('d', 3))
        line = kwargs.get('line', 'stochrsi_k')  # 'stochrsi_k' or 'stochrsi_d'
        return result[['Date', line]]

    elif type == 'adx':
        result = calculate_adx(df, plot=plot, period=kwargs.get('period', 14))
        return result[['Date', 'adx']]

    elif type == 'ichimoku':
        return calculate_ichimoku(df,plot=plot,tenkan=kwargs.get('tenkan', 9),kijun=kwargs.get('kijun', 26),senkou=kwargs.get('senkou', 52))

    elif type == 'bbands':
        return calculate_bbands(df,plot=plot,period=kwargs.get('period', 20),std=kwargs.get('std_dev', 2))

    elif type == 'atr':
        return calculate_atr(df, plot=plot, period=kwargs.get('period', 14))

    elif type == 'donchian':
        return calculate_donchian(df, plot=plot, period=kwargs.get('period', 20))

    else:
        raise ValueError(f"Unsupported indicator type: {type}")
