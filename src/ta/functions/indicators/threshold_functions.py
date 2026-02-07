# === External libraries ===
import pandas as pd

from src.ta.functions.indicators.trend_indicators import *
from src.ta.functions.indicators.momentum_indicators import *
from src.ta.functions.indicators.volatility_indicators  import *
from src.ta.functions.indicators.universal_indicator_dispatcher import *




#? ==========================================================================================================
#? STATIC THRESHOLDS
#? ==========================================================================================================


#----------------
#crossUpThresehold   1 indicator static level
#----------------
def crossUpThreshold(df, type, thr, period, wd=0, sell=False, **kwargs):
    """
    Detect cross-up or cross-down of indicator vs static threshold.
    Handles arbitrary indicator parameters via **kwargs.
    """

    # compute indicator with user-provided params
    ind_df = calculate_indicator(df.copy(), type=type, period=period, plot=False, **kwargs)

    # find the indicator column (everything except Date)
    col = [c for c in ind_df.columns if c != 'Date'][0]

    prev = ind_df[col].shift(1)
    curr = ind_df[col]

    # BUY: cross up through threshold
    if not sell:
        cross = (prev < thr) & (curr >= thr)

    # SELL: cross down through threshold
    else:
        cross = (prev > thr) & (curr <= thr)

    # Create signal column
    ind_df["signal"] = df["close"].where(cross, "")

    # Filter only signal rows
    signals = ind_df[ind_df["signal"] != ""][["Date", "signal"]].copy()

    # cluster filtering: remove signals too close to each other
    signals["diff"] = signals["Date"].diff().dt.days
    signals = signals[(signals["diff"].isna()) | (signals["diff"] > wd)]

    return signals.drop(columns="diff")





#----------------
#crossUpLineThresehold  2 indicators - line vs line
#----------------
def crossUpLineThreshold(df,type1, period1,type2, period2,wd=1,kwargs1={},kwargs2={}):
    """
    Detects clean cross-up events between two indicators (line-to-line crossover).
    Filters out duplicate consecutive signals so each cluster is represented once.

    Parameters:
        df (pd.DataFrame): Must contain full OHLCV + 'Date'
        type1 (str): First indicator type (e.g., 'ema')
        period1 (int): Period for indicator 1
        type2 (str): Second indicator type
        period2 (int): Period for indicator 2
        wd (int): Minimum gap (in days) between valid signals
        kwargs1 (dict): Extra arguments for indicator 1
        kwargs2 (dict): Extra arguments for indicator 2

    Returns:
        pd.DataFrame: ['Date', 'signal'] with clean cross-up entries
    """

    # === 1. Calculate both indicators
    ind1_df = calculate_indicator(df.copy(), type=type1, period=period1, plot=False, **kwargs1)
    ind2_df = calculate_indicator(df.copy(), type=type2, period=period2, plot=False, **kwargs2)

    # === 2. Standardize column names to 'value'
    ind1_df = ind1_df.rename(columns={col: 'value' for col in ind1_df.columns if col != 'Date'})
    ind2_df = ind2_df.rename(columns={col: 'value' for col in ind2_df.columns if col != 'Date'})

    # === 3. Merge with suffixes
    merged = pd.merge(ind1_df, ind2_df, on='Date', suffixes=('_1', '_2'))

    # === 4. Detect upward cross (value_1 crosses above value_2)
    cross_up = (merged['value_1'].shift(1) < merged['value_2'].shift(1)) & \
               (merged['value_1'] >= merged['value_2'])

    # === 5. Mark only exact crossing points
    merged['signal'] = cross_up.apply(lambda x: 'entry' if x else '')

    # === 6. Keep only rows with signals
    signals = merged[merged['signal'] != ''][['Date', 'signal']].copy()

    # === 7. Filter clusters: keep only first signal if multiple are close
    signals['diff'] = signals['Date'].diff().dt.days
    signals = signals[(signals['diff'].isna()) | (signals['diff'] > wd)]
    signals = signals.drop(columns='diff')

    return signals






#----------------
#In Range Threshold
# TODO: add wd!
#----------------
def inRangeThreshold(df,type,period,lower,upper,kwargs={}):
    """
    Detects when an indicator's value is inside a specified threshold range.
    Returns a signal for every candle that is inside the range.

    Parameters:
        df (pd.DataFrame): Input OHLCV with 'Date'
        type (str): Indicator type (e.g., 'rsi', 'williams', etc.)
        period (int): Indicator period
        lower (float): Lower threshold
        upper (float): Upper threshold
        kwargs (dict): Extra kwargs for the indicator

    Returns:
        pd.DataFrame: ['Date', 'signal'] rows where value is inside range
    """

    # === 1. Calculate indicator
    ind = calculate_indicator(df.copy(), type=type, period=period, plot=False, **kwargs)
    col = [c for c in ind.columns if c != 'Date'][0]
    ind = ind.rename(columns={col: 'value'})

    # === 2. Check if inside range
    in_range = (ind['value'] >= lower) & (ind['value'] <= upper)

    # === 3. Mark signals for every in-range candle
    ind['signal'] = in_range.apply(lambda x: 'entry' if x else '')

    # === 4. Return only signal rows
    result = ind[ind['signal'] != ''][['Date', 'signal']].copy()
    return result




#----------------
# Time Threshold (generalized)
#----------------
def timeThreshold(df,type,period,level,direction="above",min_candles=3,wd=0,**kwargs):  # "above" or "below"
    """
    Detects when an indicator has stayed above/below a threshold
    for at least N consecutive candles.

    Parameters:
        df (pd.DataFrame): OHLCV DataFrame
        type (str): Indicator type (e.g. 'rsi', 'ema', 'williams')
        period (int): Indicator period
        level (float): Threshold value
        direction (str): "above" or "below"
        min_candles (int): Required streak length
        wd (int): Expand signals ±wd candles
        kwargs (dict): Extra params for the indicator

    Returns:
        pd.DataFrame: ['Date', 'signal']
    """

    # === 1. Calculate indicator
    ind = calculate_indicator(df.copy(), type=type, period=period, plot=False, **kwargs)
    col = [c for c in ind.columns if c != "Date"][0]
    ind = ind.rename(columns={col: "value"})

    # === 2. Boolean mask above/below threshold
    if direction == "above":
        cond = ind["value"] > level
    elif direction == "below":
        cond = ind["value"] < level
    else:
        raise ValueError("direction must be 'above' or 'below'")

    # === 3. Count consecutive streaks
    streak = (cond != cond.shift()).cumsum()
    streak_count = cond.groupby(streak).cumsum()

    # === 4. Valid if streak length ≥ min_candles
    valid = streak_count >= min_candles

    # === 5. Expand by window if needed
    if wd > 0:
        for i in range(1, wd + 1):
            valid |= valid.shift(i)
            valid |= valid.shift(-i)

    # === 6. Build result
    signals = ind.loc[valid, ["Date"]].copy()
    signals["signal"] = "entry"

    return signals








#? ==========================================================================================================
#? DYNAMIC THRESHOLDS
#? ==========================================================================================================


#-----------------------
# Stdv Threshold EMA
#-----------------------
import numpy as np
import pandas as pd
def stdvThresholdEMA(df, ema_period=10, window=50, sigma=0.8, wd=0):
    df_temp = df.copy()
    
    # 1. Calculate the Baseline (EMA)
    df_temp['ema'] = df_temp['close'].ewm(span=ema_period, adjust=False).mean()
    print(df_temp['ema'])
    # 2. Calculate RAW distance (not absolute) for the std() calculation
    # We use raw distance so the standard deviation captures the true variance
    df_temp['dist_raw'] = df_temp['close'] - df_temp['ema']
    
    # 3. Calculate Rolling Standard Deviation of the distance
    # This represents the "volatility unit"
    df_temp['rolling_std'] = df_temp['dist_raw'].rolling(window=window).std()
    
    # 4. Create Symmetrical Bands centered on the EMA
    # Distance from EMA = (sigma * std)
    # No rolling_mean is added here to ensure perfect symmetry
    df_temp['upper_band_price'] = df_temp['ema'] + (sigma * df_temp['rolling_std'])
    df_temp['lower_band_price'] = df_temp['ema'] - (sigma * df_temp['rolling_std'])
    
    # 5. Signal Detection
    # Logic: Is the current close price touching or outside the bands?
    above = (df_temp['close'] >= df_temp['upper_band_price'])
    below = (df_temp['close'] <= df_temp['lower_band_price'])
    
    s_above = df_temp.loc[above, ["Date", "close"]].copy()
    s_below = df_temp.loc[below, ["Date", "close"]].copy()

    # 6. Clustering (Filter consecutive signals)
    if wd > 0:
        for sig_df in [s_above, s_below]:
            if not sig_df.empty:
                sig_df['idx'] = range(len(sig_df))
                # Remove signals within 'wd' bars of each other
                sig_df.drop(sig_df[sig_df['idx'].diff() <= wd].index, inplace=True)

    return s_above, s_below





#Kurtosis Threshold
def kurtosisThreshold(df, window=20, k_range=(-2.0, 1.0), label="trigger_active"):
    """
    Calculates kurtosis for each day individually using a rolling window 
    and returns dates falling within the specified range.
    """
    # 1. Prepare the data
    df_temp = df.copy()
    # Handle the capitalization inconsistency often found in yfinance
    if 'Close' in df_temp.columns:
        df_temp['close'] = df_temp['Close']
    
    # 2. Calculation Logic (Individual daily calculation)
    # This generates a unique value for every row
    df_temp['returns'] = df_temp['close'].pct_change()
    df_temp['kurt'] = df_temp['returns'].rolling(window=window).kurt()
    
    # 3. Apply the Range Filter
    # This captures the 'Thin-Tailed' (-2) to 'Normal' (1) regime you requested
    is_in_range = (df_temp['kurt'] >= k_range[0]) & (df_temp['kurt'] <= k_range[1])
    
    # 4. Extract results
    # We ensure "Date" is available (resetting index if necessary)
    if 'Date' not in df_temp.columns:
        df_temp = df_temp.reset_index()
        
    signals = df_temp.loc[is_in_range, ["Date", "close", "kurt"]].copy()
    signals["signal"] = label
    
    return signals





def run_kurtosis_delta_strategy(df, ema_p=20, sig=1.5, k_win=50, delta_k=0.5,n=5):
    # 1. Use your existing stdvThresholdEMA for the bands
    # This gives us the price 'stretches'
    s_above, s_below = stdvThresholdEMA(df, ema_period=ema_p, window=50, sigma=sig)

    # 2. Use your existing kurtosisThreshold for the raw kurtosis data
    # We set a wide range so we get all the data points for calculation
    k_data = kurtosisThreshold(df, window=k_win, k_range=(-10, 10))

    # 3. Apply the Image Logic (Delta K)
    # K(t) < K(t-1)
    k_data['cooling'] = k_data['kurt'] < k_data['kurt'].shift(1)
    
    # K(t-n) - K(t) > ΔK (using n=5)
    k_data['drop'] = (k_data['kurt'].shift(n) - k_data['kurt']) > delta_k

    # 4. Filter the Sigma signals by these new Delta conditions
    valid_kurt_dates = k_data[k_data['cooling'] & k_data['drop']]['Date']
    
    final_buys = s_below[s_below['Date'].isin(valid_kurt_dates)]
    final_sells = s_above[s_above['Date'].isin(valid_kurt_dates)]

    return final_buys, final_sells