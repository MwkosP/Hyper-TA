# === External libraries ===
import numpy as np
import pandas as pd

from HyperTA.Indicators.indicators import *
from HyperTA.Indicators.dispatcher import *
from HyperTA.Metrics.derivatives import *

#Fix??
def makeSignals(df, mask) -> pd.DataFrame:
    """
    Build the standard signal table from OHLCV rows where mask is True.

    Returns
    -------
    DataFrame with columns:
      - Date  : datetime (second resolution when the source has it)
      - Price : Close at that bar (exact traded close for the signal candle)
    """
    out = df.loc[mask, ["Date", "Close"]].copy()
    out = out.rename(columns={"Close": "Price"})
    out["Date"] = pd.to_datetime(out["Date"])
    return out.reset_index(drop=True)


def makeSignalsFromDates(df, dates) -> pd.DataFrame:
    """Same schema, keyed by signal dates (aligned back to OHLCV Close)."""
    dates = pd.to_datetime(pd.Series(list(dates)))
    out = df.loc[df["Date"].isin(dates), ["Date", "Close"]].copy()
    out = out.rename(columns={"Close": "Price"})
    out["Date"] = pd.to_datetime(out["Date"])
    return out.drop_duplicates(subset=["Date"]).sort_values("Date").reset_index(drop=True)


def _filterBySpacing(signals: pd.DataFrame, wd: float) -> pd.DataFrame:
    """Drop signals closer than wd days (fractional days ok for intraday)."""
    if wd <= 0 or signals.empty:
        return signals
    out = signals.copy()
    out["diff"] = out["Date"].diff().dt.total_seconds() / 86400.0
    out = out[(out["diff"].isna()) | (out["diff"] > wd)]
    return out.drop(columns="diff").reset_index(drop=True)


#? ==========================================================================================================
#? STATIC THRESHOLDS
#? ==========================================================================================================


def crossLevel(df, type, thr, period, wd=0, sell=False, **kwargs):
    """Indicator crosses a fixed level. Returns Date + Price."""
    ind_df = calculateIndicator(df.copy(), type=type, period=period, plot=False, **kwargs)
    col = [c for c in ind_df.columns if c != "Date"][0]

    prev = ind_df[col].shift(1)
    curr = ind_df[col]

    if not sell:
        cross = (prev < thr) & (curr >= thr)
    else:
        cross = (prev > thr) & (curr <= thr)

    signals = makeSignalsFromDates(df, ind_df.loc[cross, "Date"])
    return _filterBySpacing(signals, wd)


def crossLines(df, type1, period1, type2, period2, wd=1, kwargs1={}, kwargs2={}):
    """Line A crosses above line B. Returns Date + Price."""
    ind1_df = calculateIndicator(df.copy(), type=type1, period=period1, plot=False, **kwargs1)
    ind2_df = calculateIndicator(df.copy(), type=type2, period=period2, plot=False, **kwargs2)

    ind1_df = ind1_df.rename(columns={c: "value" for c in ind1_df.columns if c != "Date"})
    ind2_df = ind2_df.rename(columns={c: "value" for c in ind2_df.columns if c != "Date"})
    merged = pd.merge(ind1_df, ind2_df, on="Date", suffixes=("_1", "_2"))

    cross_up = (merged["value_1"].shift(1) < merged["value_2"].shift(1)) & (
        merged["value_1"] >= merged["value_2"]
    )

    signals = makeSignalsFromDates(df, merged.loc[cross_up, "Date"])
    return _filterBySpacing(signals, wd)


def inRange(df, type, period, lower, upper, kwargs={}):
    """Indicator value inside [lower, upper]. Returns Date + Price."""
    ind = calculateIndicator(df.copy(), type=type, period=period, plot=False, **kwargs)
    col = [c for c in ind.columns if c != "Date"][0]
    ind = ind.rename(columns={col: "value"})
    in_range = (ind["value"] >= lower) & (ind["value"] <= upper)
    return makeSignalsFromDates(df, ind.loc[in_range, "Date"])


def holdLevel(df, type, period, level, direction="above", min_candles=3, wd=0, **kwargs):
    """Indicator held above/below level for N candles. Returns Date + Price."""
    ind = calculateIndicator(df.copy(), type=type, period=period, plot=False, **kwargs)
    col = [c for c in ind.columns if c != "Date"][0]
    ind = ind.rename(columns={col: "value"})

    if direction == "above":
        cond = ind["value"] > level
    elif direction == "below":
        cond = ind["value"] < level
    else:
        raise ValueError("direction must be 'above' or 'below'")

    streak = (cond != cond.shift()).cumsum()
    streak_count = cond.groupby(streak).cumsum()
    valid = streak_count >= min_candles

    if wd > 0:
        for i in range(1, wd + 1):
            valid |= valid.shift(i)
            valid |= valid.shift(-i)

    signals = makeSignalsFromDates(df, ind.loc[valid.fillna(False), "Date"])
    return signals


#? ==========================================================================================================
#? DYNAMIC THRESHOLDS
#? ==========================================================================================================


def stdvBandsThreshold(df, ema_period=10, window=50, sigma=0.8, wd=0):
    """Price outside EMA ± σ bands. Returns (above, below) each as Date + Price."""
    df_temp = df.copy()
    df_temp["ema"] = df_temp["Close"].ewm(span=ema_period, adjust=False).mean()
    df_temp["dist_raw"] = df_temp["Close"] - df_temp["ema"]
    df_temp["rolling_std"] = df_temp["dist_raw"].rolling(window=window).std()
    df_temp["upper_band_price"] = df_temp["ema"] + (sigma * df_temp["rolling_std"])
    df_temp["lower_band_price"] = df_temp["ema"] - (sigma * df_temp["rolling_std"])

    above = df_temp["Close"] >= df_temp["upper_band_price"]
    below = df_temp["Close"] <= df_temp["lower_band_price"]

    s_above = _filterBySpacing(makeSignals(df_temp, above), wd)
    s_below = _filterBySpacing(makeSignals(df_temp, below), wd)
    return s_above, s_below


def kurtosisThreshold(df, window=20, k_range=(-2.0, 1.0), label="trigger_active"):
    """Rolling kurtosis in range. Returns Date + Price."""
    df_temp = df.copy()
    if "Date" not in df_temp.columns:
        df_temp = df_temp.reset_index()

    df_temp["returns"] = np.log(df_temp["Close"] / df_temp["Close"].shift(1))
    df_temp["kurt"] = df_temp["returns"].rolling(window=window).kurt()
    is_in_range = (df_temp["kurt"] >= k_range[0]) & (df_temp["kurt"] <= k_range[1])
    return makeSignals(df_temp, is_in_range.fillna(False))


def skewThreshold(df, window=20, s_range=(-2.0, 1.0), label="trigger_active"):
    """Rolling skew in range. Returns Date + Price."""
    df_temp = df.copy()
    if "Date" not in df_temp.columns:
        df_temp = df_temp.reset_index()

    df_temp["returns"] = np.log(df_temp["Close"] / df_temp["Close"].shift(1))
    df_temp["skew"] = df_temp["returns"].rolling(window=window).skew()
    is_in_range = (df_temp["skew"] >= s_range[0]) & (df_temp["skew"] <= s_range[1])
    return makeSignals(df_temp, is_in_range.fillna(False))


def stdvKurtosisThreshold(df, ema_p=20, window=20, sig=1.5, k_win=50, delta_k=0.5, n=5):
    """Band touch + kurtosis cooling. Returns (buys, sells) as Date + Price."""
    s_above, s_below = stdvBandsThreshold(df, ema_period=ema_p, window=window, sigma=sig)

    k_data = df.copy()
    k_data["returns"] = np.log(k_data["Close"] / k_data["Close"].shift(1))
    k_data["kurt"] = k_data["returns"].rolling(window=k_win).kurt()
    k_data["drop"] = (k_data["kurt"].shift(n) - k_data["kurt"]) > delta_k
    valid_dates = k_data.loc[k_data["drop"].fillna(False), "Date"]

    final_buys = s_below[s_below["Date"].isin(valid_dates)].reset_index(drop=True)
    final_sells = s_above[s_above["Date"].isin(valid_dates)].reset_index(drop=True)
    return final_buys, final_sells


def derivativeThreshold(
    df,
    k=40,
    alpha=1.0,
    derivatives="first",
    lower=-0.001,
    upper=0.001,
    lower2=-0.001,
    upper2=0.001,
    wd=0,
    scale=True,
):
    """Derivative in range. Returns Date + Price."""
    ind_df = rollingDerivative(df=df, k=k, alpha=alpha, scale=scale, derivative=derivatives)
    cols = [c for c in ind_df.columns if c != "Date"]

    if derivatives == "first":
        cond = (ind_df[cols[0]] >= lower) & (ind_df[cols[0]] <= upper)
    elif derivatives == "second":
        cond = (ind_df[cols[0]] >= lower) & (ind_df[cols[0]] <= upper)
    elif derivatives == "both":
        first_col = [c for c in cols if "First" in c][0]
        second_col = [c for c in cols if "Second" in c][0]
        cond = (
            (ind_df[first_col] >= lower)
            & (ind_df[first_col] <= upper)
            & (ind_df[second_col] >= lower2)
            & (ind_df[second_col] <= upper2)
        )
    else:
        raise ValueError("derivative must be 'first', 'second', or 'both'")

    signals = makeSignalsFromDates(df, ind_df.loc[cond.fillna(False), "Date"])
    return _filterBySpacing(signals, wd / 24.0 if wd else 0)  # wd historically hours for this fn
