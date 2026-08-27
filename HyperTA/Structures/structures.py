"""Market structure calculators — swings, Fib, S/R, trendlines."""

from __future__ import annotations

import numpy as np
import pandas as pd

from HyperTA.Structures.utils import (
    _DEFAULT_CHART_PATTERNS,
    _activeSwingPair,
    _annotateHhLl,
    _clusterLevels,
    _detectChannels,
    _detectGaps,
    _detectRanges,
    _detectWyckoff,
    _ensureOhlc,
    _findDivergences,
    _fitLine,
    _fractalSwings,
    _indicatorAtDates,
    _labelSwingStructure,
    _meltCandlePatterns,
    _scanChartPatterns,
    _zigzagTrendLegs,
)

# Default Fib ratios (retracement)
_DEFAULT_FIB = (0.0, 0.236, 0.382, 0.5, 0.618, 0.786, 1.0)

# Popular candlestick subset (pass patterns="all" for the full 62)
_DEFAULT_CANDLES = (
    "doji",
    "engulfing",
    "hammer",
    "invertedhammer",
    "hangingman",
    "shootingstar",
    "morningstar",
    "eveningstar",
    "harami",
    "piercing",
    "darkcloudcover",
    "marubozu",
    "3whitesoldiers",
    "3blackcrows",
)


# =============================================================================
# SWINGS
# =============================================================================

def calculateSwingPoints(
    df: pd.DataFrame,
    *,
    left: int = 2,
    right: int = 2,
) -> pd.DataFrame:
    """
    Detect fractal swing highs / lows.

    Returns
    -------
    DataFrame: Date, Price, kind ('high'|'low'), structure (HH/HL/LH/LL/H/L), index
    """
    ohlc = _ensureOhlc(df)
    swings = _fractalSwings(ohlc, left=left, right=right)
    return _labelSwingStructure(swings)


# =============================================================================
# FIBONACCI
# =============================================================================

def calculateFib(
    df: pd.DataFrame,
    *,
    swing_low: float | None = None,
    swing_high: float | None = None,
    levels: tuple[float, ...] = _DEFAULT_FIB,
    left: int = 2,
    right: int = 2,
    direction: str = "auto",
    lookback: int | None = None,
) -> pd.DataFrame:
    """
    Fibonacci retracement / extension levels between two swing anchors.

    If ``swing_low`` / ``swing_high`` are omitted, anchors to the latest
    completed move (last swing + prior opposite swing). Pass ``lookback=N``
    to use min Low / max High of the last N bars instead.

    Parameters
    ----------
    direction : str
        ``"up"`` / ``"down"`` / ``"auto"`` (inferred from the move)

    Returns
    -------
    DataFrame: level, price, swing_low, swing_high, direction,
               start_date, end_date
    """
    ohlc = _ensureOhlc(df)
    start_date = end_date = None

    if swing_low is None or swing_high is None:
        if lookback is not None:
            window = ohlc.iloc[-int(lookback) :]
            swing_low = float(window["Low"].min())
            swing_high = float(window["High"].max())
            start_date = window.loc[window["Low"].idxmin(), "Date"]
            end_date = window.loc[window["High"].idxmax(), "Date"]
            if direction == "auto":
                # later extreme defines end of move
                direction = "up" if end_date >= start_date else "down"
                if direction == "down":
                    start_date, end_date = end_date, start_date
        else:
            swings = calculateSwingPoints(ohlc, left=left, right=right)
            lo, hi, inferred = _activeSwingPair(swings)
            if lo is None or hi is None:
                return pd.DataFrame(
                    columns=[
                        "level",
                        "price",
                        "swing_low",
                        "swing_high",
                        "direction",
                        "start_date",
                        "end_date",
                    ]
                )
            swing_low = float(lo["Price"])
            swing_high = float(hi["Price"])
            if direction == "auto":
                direction = inferred
            if direction == "up":
                start_date, end_date = lo["Date"], hi["Date"]
            else:
                start_date, end_date = hi["Date"], lo["Date"]
    else:
        swing_low = float(swing_low)
        swing_high = float(swing_high)
        if direction == "auto":
            direction = "up"

    if swing_high == swing_low:
        raise ValueError("swing_high and swing_low must differ")

    direction = direction.lower()
    if direction not in {"up", "down"}:
        raise ValueError("direction must be 'up', 'down', or 'auto'")

    span = swing_high - swing_low
    rows = []
    for ratio in levels:
        if direction == "up":
            price = swing_low + span * float(ratio)
        else:
            price = swing_high - span * float(ratio)
        rows.append(
            {
                "level": float(ratio),
                "price": float(price),
                "swing_low": swing_low,
                "swing_high": swing_high,
                "direction": direction,
                "start_date": start_date,
                "end_date": end_date,
            }
        )
    return pd.DataFrame(rows)


# =============================================================================
# SUPPORT / RESISTANCE
# =============================================================================

def calculateSR(
    df: pd.DataFrame,
    *,
    left: int = 2,
    right: int = 2,
    tol: float = 0.015,
    min_touches: int = 3,
    max_levels: int = 8,
) -> pd.DataFrame:
    """
    Support / resistance from clustered swing prices.

    Parameters
    ----------
    tol : float
        Relative price tolerance for clustering (0.015 = 1.5%).
    min_touches : int
        Minimum swings that must land in a cluster.
    max_levels : int
        Keep the strongest N levels (by touch count).

    Returns
    -------
    DataFrame: price, touches, lo, hi, kind ('support'|'resistance'|'both')
    """
    ohlc = _ensureOhlc(df)
    swings = calculateSwingPoints(ohlc, left=left, right=right)
    if swings.empty:
        return pd.DataFrame(columns=["price", "touches", "lo", "hi", "kind"])

    levels = _clusterLevels(swings["Price"].to_numpy(), tol=tol)
    mid = float(ohlc["Close"].iloc[-1])
    rows = []
    for lvl in levels:
        if lvl["touches"] < min_touches:
            continue
        highs_n = int(
            (
                (swings["kind"] == "high")
                & (swings["Price"].between(lvl["lo"], lvl["hi"]))
            ).sum()
        )
        lows_n = int(
            (
                (swings["kind"] == "low")
                & (swings["Price"].between(lvl["lo"], lvl["hi"]))
            ).sum()
        )
        if highs_n > 0 and lows_n > 0:
            kind = "both"
        elif lvl["price"] >= mid:
            kind = "resistance"
        else:
            kind = "support"
        rows.append({**lvl, "kind": kind})

    if not rows:
        return pd.DataFrame(columns=["price", "touches", "lo", "hi", "kind"])
    out = (
        pd.DataFrame(rows)
        .sort_values(["touches", "price"], ascending=[False, True])
        .reset_index(drop=True)
    )
    if max_levels is not None and max_levels > 0:
        out = out.head(int(max_levels)).reset_index(drop=True)
    return out


# =============================================================================
# TRENDLINES
# =============================================================================

def calculateTrendlines(
    df: pd.DataFrame,
    *,
    left: int = 5,
    right: int = 5,
    min_points: int = 3,
    max_lines: int = 1,
) -> pd.DataFrame:
    """
    Fit trendlines through recent swing highs (resistance) and lows (support).

    Default: one support + one resistance from the last ``min_points`` swings
    of each kind (wider fractal window so pivots are more significant).

    Returns
    -------
    DataFrame: kind, slope, intercept, start_date, end_date,
               start_price, end_price, start_index, end_index, n_points
    """
    if min_points < 2:
        raise ValueError("min_points must be >= 2")

    ohlc = _ensureOhlc(df)
    swings = calculateSwingPoints(ohlc, left=left, right=right)
    empty_cols = [
        "kind",
        "slope",
        "intercept",
        "start_date",
        "end_date",
        "start_price",
        "end_price",
        "start_index",
        "end_index",
        "n_points",
    ]
    if swings.empty:
        return pd.DataFrame(columns=empty_cols)

    rows = []
    for kind, label in (("low", "support"), ("high", "resistance")):
        pts = swings[swings["kind"] == kind].copy()
        if len(pts) < min_points:
            continue

        # newest window first; optionally a few older non-overlapping ones
        n_windows = max(1, int(max_lines))
        for w in range(n_windows):
            end = len(pts) - w * min_points
            start = end - min_points
            if start < 0:
                break
            window = pts.iloc[start:end]
            xs = window["index"].to_numpy(dtype=float)
            ys = window["Price"].to_numpy(dtype=float)
            slope, intercept = _fitLine(xs, ys)
            rows.append(
                {
                    "kind": label,
                    "slope": slope,
                    "intercept": intercept,
                    "start_date": window["Date"].iloc[0],
                    "end_date": window["Date"].iloc[-1],
                    "start_price": float(ys[0]),
                    "end_price": float(ys[-1]),
                    "start_index": int(xs[0]),
                    "end_index": int(xs[-1]),
                    "n_points": int(len(window)),
                }
            )

    if not rows:
        return pd.DataFrame(columns=empty_cols)
    return pd.DataFrame(rows).reset_index(drop=True)


def projectTrendline(line: pd.Series | dict, bar_index: int | float) -> float:
    """Evaluate y = slope * bar_index + intercept for a calculateTrendlines row."""
    if isinstance(line, pd.Series):
        line = line.to_dict()
    return float(line["slope"]) * float(bar_index) + float(line["intercept"])


# =============================================================================
# TREND (ZigZag up / down legs)
# =============================================================================

def calculateTrend(
    df: pd.DataFrame,
    *,
    sensitivity: float = 0.05,
    mode: str = "pct",
    atr_period: int = 14,
    atr_mult: float | None = None,
) -> pd.DataFrame:
    """
    Segment price into up / down trend legs (ZigZag).

    Hyperparameter ``sensitivity`` controls how reactive the legs are:

    - **Small** (e.g. ``0.02``–``0.04``): many short legs — catches spikes / swings
    - **Large** (e.g. ``0.10``–``0.20``): few long legs — big-picture trend only

    Parameters
    ----------
    sensitivity : float
        In ``mode=\"pct\"``: minimum % reversal of the pivot price to flip.
        In ``mode=\"atr\"``: used as ATR multiple unless ``atr_mult`` is set.
    mode : str
        ``\"pct\"`` (default) or ``\"atr\"``.
    atr_mult : float | None
        ATR multiple when ``mode=\"atr\"`` (overrides ``sensitivity`` as mult).

    Returns
    -------
    DataFrame: start_date, end_date, start_index, end_index, direction
               ('up'|'down'), start_price, end_price, move_pct, n_bars,
               sensitivity, mode
    """
    mode = str(mode).lower()
    if mode not in {"pct", "atr"}:
        raise ValueError("mode must be 'pct' or 'atr'")
    if sensitivity <= 0:
        raise ValueError("sensitivity must be > 0")

    ohlc = _ensureOhlc(df)
    return _zigzagTrendLegs(
        ohlc,
        sensitivity=sensitivity,
        mode=mode,
        atr_period=atr_period,
        atr_mult=atr_mult,
    )


# =============================================================================
# RANGE (horizontal box)
# =============================================================================

def calculateRange(
    df: pd.DataFrame,
    *,
    window: int = 40,
    max_width_pct: float = 0.12,
    min_touches: int = 2,
    touch_tol: float = 0.008,
    step: int = 5,
    max_ranges: int = 5,
) -> pd.DataFrame:
    """
    Detect consolidation ranges as horizontal price boxes.

    A sliding window is kept when its High−Low band is ≤ ``max_width_pct`` of
    mid-price and both the top and bottom edges are touched enough times.

    Returns
    -------
    DataFrame: start_date, end_date, start_index, end_index,
               top, bottom, mid, width_pct, touches_top, touches_bottom, n_bars
    """
    ohlc = _ensureOhlc(df)
    out = _detectRanges(
        ohlc,
        window=window,
        max_width_pct=max_width_pct,
        min_touches=min_touches,
        touch_tol=touch_tol,
        step=step,
    )
    if out.empty or max_ranges is None:
        return out
    return out.head(int(max_ranges)).reset_index(drop=True)


# =============================================================================
# CHANNEL (parallel rails)
# =============================================================================

def calculateChannel(
    df: pd.DataFrame,
    *,
    window: int = 60,
    step: int = 10,
    max_channels: int = 3,
    max_width_pct: float = 0.25,
) -> pd.DataFrame:
    """
    Fit parallel price channels (up / down / flat).

    Slope comes from a Close regression; upper and lower rails share that
    slope and bound the High/Low extremes in the window.

    Returns
    -------
    DataFrame: kind ('up'|'down'|'flat'), slope, upper_intercept, lower_intercept,
               start_date, end_date, start_index, end_index,
               upper_start, upper_end, lower_start, lower_end,
               width, width_pct, n_bars
    """
    ohlc = _ensureOhlc(df)
    return _detectChannels(
        ohlc,
        window=window,
        step=step,
        max_channels=max_channels,
        max_width_pct=max_width_pct,
    )


def projectChannel(
    channel: pd.Series | dict,
    bar_index: int | float,
    *,
    rail: str = "mid",
) -> float:
    """Evaluate a channel rail at ``bar_index`` (``upper`` / ``lower`` / ``mid``)."""
    if isinstance(channel, pd.Series):
        channel = channel.to_dict()
    slope = float(channel["slope"])
    if rail == "upper":
        b = float(channel["upper_intercept"])
    elif rail == "lower":
        b = float(channel["lower_intercept"])
    else:
        b = 0.5 * (float(channel["upper_intercept"]) + float(channel["lower_intercept"]))
    return slope * float(bar_index) + b


# =============================================================================
# CANDLESTICK PATTERNS (pandas-ta-classic)
# =============================================================================

def calculateCandleFormations(
    df: pd.DataFrame,
    *,
    patterns: str | tuple[str, ...] | list[str] = _DEFAULT_CANDLES,
    min_abs: float = 100.0,
) -> pd.DataFrame:
    """
    Detect candlestick formations via ``pandas-ta-classic`` (62 native CDL patterns).

    Parameters
    ----------
    patterns : str | sequence
        ``"all"`` for every pattern, or a list/tuple of names
        (e.g. ``"engulfing"``, ``"hammer"``, ``"morningstar"``).
    min_abs : float
        Keep hits with ``abs(value) >= min_abs`` (TA-Lib-style signals are ±100).

    Returns
    -------
    DataFrame: Date, Price, pattern, bias ('bullish'|'bearish'), value
    """
    import pandas_ta_classic as ta

    ohlc = _ensureOhlc(df)
    if "Open" not in ohlc.columns:
        raise ValueError("calculateCandleFormations requires an Open column")

    name = patterns
    if isinstance(patterns, (list, tuple)):
        name = list(patterns)

    wide = ta.cdl_pattern(
        ohlc["Open"].astype(float),
        ohlc["High"].astype(float),
        ohlc["Low"].astype(float),
        ohlc["Close"].astype(float),
        name=name,
    )
    if wide is None or wide.empty:
        return pd.DataFrame(columns=["Date", "Price", "pattern", "bias", "value", "family"])

    return _meltCandlePatterns(wide, ohlc, min_abs=min_abs)


# =============================================================================
# CHART PATTERNS (ta-patterns)
# =============================================================================

def calculateChartPatterns(
    df: pd.DataFrame,
    *,
    patterns: str | tuple[str, ...] | list[str] = _DEFAULT_CHART_PATTERNS,
    mode: str = "confirmed",
    window: int = 100,
    pivot_n: int = 5,
) -> pd.DataFrame:
    """
    Classic chart patterns via ``ta-patterns`` (double top/bottom, H&S,
    triangles, flags, pennants, wedges, cup-with-handle, …).

    Parameters
    ----------
    patterns : str | sequence
        ``"all"`` for every chart detector, or a subset of names.
    mode : str
        ``"confirmed"`` (default) or ``"forming"``.
    window, pivot_n : int
        Pivot sensitivity — smaller ``pivot_n`` / ``window`` → more hits.

    Returns
    -------
    DataFrame: Date, Price, pattern, bias, value, family ('chart')
    """
    ohlc = _ensureOhlc(df)
    if "Open" not in ohlc.columns:
        raise ValueError("calculateChartPatterns requires an Open column")
    return _scanChartPatterns(
        ohlc,
        patterns=patterns if patterns == "all" else tuple(patterns),
        mode=mode,
        window=window,
        pivot_n=pivot_n,
    )


def calculateDoubleTopBottom(
    df: pd.DataFrame,
    *,
    mode: str = "confirmed",
    window: int = 60,
    pivot_n: int = 5,
) -> pd.DataFrame:
    """Convenience wrapper: double tops + double bottoms only."""
    return calculateChartPatterns(
        df,
        patterns=("double_top", "double_bottom"),
        mode=mode,
        window=window,
        pivot_n=pivot_n,
    )


# =============================================================================
# GAPS
# =============================================================================

def calculateGaps(
    df: pd.DataFrame,
    *,
    min_gap_pct: float = 0.002,
    lookforward: int = 40,
) -> pd.DataFrame:
    """
    Detect price gaps between consecutive bars and whether they fill.

    Returns
    -------
    DataFrame: Date, direction ('up'|'down'), gap_top, gap_bottom, gap_pct,
               filled, fill_date, index
    """
    ohlc = _ensureOhlc(df)
    return _detectGaps(ohlc, min_gap_pct=min_gap_pct, lookforward=lookforward)


# =============================================================================
# WYCKOFF
# =============================================================================

def calculateWyckoff(
    df: pd.DataFrame,
    *,
    window: int = 40,
    max_width_pct: float = 0.15,
    lookforward: int = 30,
    volume_mult: float = 1.2,
) -> pd.DataFrame:
    """
    Wyckoff-style events around consolidation ranges.

    Detects **spring** / **upthrust** (false breaks) and **sos** / **sow**
    (strength / weakness breaks), and labels a rough **phase**
    (accumulation / distribution / markup / markdown / ranging).

    Returns
    -------
    DataFrame: Date, event, phase, Price, range_top, range_bottom,
               range_start, range_end, index
    """
    ohlc = _ensureOhlc(df)
    return _detectWyckoff(
        ohlc,
        window=window,
        max_width_pct=max_width_pct,
        lookforward=lookforward,
        volume_mult=volume_mult,
    )


# =============================================================================
# HH / HL / LH / LL MARKET STRUCTURE
# =============================================================================

def calculateHhLl(
    df: pd.DataFrame,
    *,
    left: int = 5,
    right: int = 5,
) -> pd.DataFrame:
    """
    Higher-high / higher-low / lower-high / lower-low market structure.

    Builds on fractal swings, labels each as HH/HL/LH/LL, tracks the running
    trend (up / down / range), and flags BOS / ChoCH events:

    - **bos**   — break of structure in the direction of the trend (HH in uptrend,
      LL in downtrend)
    - **choch** — change of character against the prior trend (HH while downtrend,
      LL while uptrend)

    Returns
    -------
    DataFrame: Date, Price, kind, structure, trend, event, index
    """
    ohlc = _ensureOhlc(df)
    swings = calculateSwingPoints(ohlc, left=left, right=right)
    return _annotateHhLl(swings)


# =============================================================================
# DIVERGENCE (price vs indicator)
# =============================================================================

def calculateDivergence(
    df: pd.DataFrame,
    *,
    indicator_df: pd.DataFrame | None = None,
    indicator_col: str | None = None,
    period: int = 14,
    left: int = 5,
    right: int = 5,
    mode: str = "both",
) -> pd.DataFrame:
    """
    Regular / hidden divergence between price swings and an oscillator.

    Default oscillator is RSI(``period``) from ``HyperTA.Indicators``.
    Pass ``indicator_df`` (e.g. from ``calculateRsi`` / ``calculateMacd``) to
    override; set ``indicator_col`` if the value column isn't auto-detected.

    Parameters
    ----------
    mode : str
        ``"regular"`` | ``"hidden"`` | ``"both"``

    Returns
    -------
    DataFrame: start_date, end_date, price_start, price_end,
               ind_start, ind_end, bias, mode, swing_kind
    """
    mode = str(mode).lower()
    if mode not in {"regular", "hidden", "both"}:
        raise ValueError("mode must be 'regular', 'hidden', or 'both'")

    ohlc = _ensureOhlc(df)
    swings = calculateSwingPoints(ohlc, left=left, right=right)
    if swings.empty:
        return pd.DataFrame(
            columns=[
                "start_date",
                "end_date",
                "price_start",
                "price_end",
                "ind_start",
                "ind_end",
                "bias",
                "mode",
                "swing_kind",
            ]
        )

    if indicator_df is None:
        from HyperTA.Indicators import calculateRsi

        indicator_df = calculateRsi(ohlc, period=period)
        indicator_col = indicator_col or "rsi"
    else:
        indicator_df = indicator_df.copy()
        if "Date" not in indicator_df.columns:
            indicator_df = indicator_df.reset_index()
        if indicator_col is None:
            prefer = ("rsi", "macd", "stochrsi_k", "williams", "roc", "adx")
            cols = [c for c in indicator_df.columns if c != "Date"]
            indicator_col = next((c for c in prefer if c in cols), cols[0] if cols else None)
        if indicator_col is None or indicator_col not in indicator_df.columns:
            raise ValueError("Could not resolve indicator_col for divergence")

    ind_vals = _indicatorAtDates(
        indicator_df, swings["Date"], value_col=indicator_col
    )
    return _findDivergences(swings, ind_vals, mode=mode)
