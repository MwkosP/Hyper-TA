"""Internal helpers for Structures (all names start with _)."""

from __future__ import annotations

import re

import numpy as np
import pandas as pd


def _ensureOhlc(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize Date + OHLC columns; sort by Date."""
    out = df.copy()
    if "Date" not in out.columns:
        out = out.reset_index()
        for candidate in ("Date", "date", "Datetime", "datetime"):
            if candidate in out.columns:
                if candidate != "Date":
                    out = out.rename(columns={candidate: "Date"})
                break
    if "Date" not in out.columns:
        raise ValueError("DataFrame must contain a Date column")

    rename = {}
    for src, dst in (
        ("Open", "Open"),
        ("open", "Open"),
        ("High", "High"),
        ("high", "High"),
        ("Low", "Low"),
        ("low", "Low"),
        ("Close", "Close"),
        ("close", "Close"),
        ("Volume", "Volume"),
        ("volume", "Volume"),
    ):
        if src in out.columns and dst not in out.columns:
            rename[src] = dst
    out = out.rename(columns=rename)

    for col in ("High", "Low", "Close"):
        if col not in out.columns:
            raise ValueError(f"DataFrame must contain '{col}'")

    out["Date"] = pd.to_datetime(out["Date"])
    return out.sort_values("Date").reset_index(drop=True)


def _fractalSwings(
    df: pd.DataFrame,
    *,
    left: int = 2,
    right: int = 2,
) -> pd.DataFrame:
    """
    Classic fractal swing highs/lows.

    A swing high at i: High[i] is max of High[i-left : i+right+1]
    A swing low  at i: Low[i]  is min of Low[i-left  : i+right+1]
    """
    if left < 1 or right < 1:
        raise ValueError("left and right must be >= 1")

    highs = df["High"].to_numpy(dtype=float)
    lows = df["Low"].to_numpy(dtype=float)
    n = len(df)
    rows = []

    for i in range(left, n - right):
        window_h = highs[i - left : i + right + 1]
        window_l = lows[i - left : i + right + 1]
        if highs[i] == np.nanmax(window_h) and np.sum(window_h == highs[i]) == 1:
            rows.append(
                {
                    "Date": df.at[i, "Date"],
                    "Price": float(highs[i]),
                    "kind": "high",
                    "index": i,
                }
            )
        if lows[i] == np.nanmin(window_l) and np.sum(window_l == lows[i]) == 1:
            rows.append(
                {
                    "Date": df.at[i, "Date"],
                    "Price": float(lows[i]),
                    "kind": "low",
                    "index": i,
                }
            )

    if not rows:
        return pd.DataFrame(columns=["Date", "Price", "kind", "index"])
    return pd.DataFrame(rows).sort_values("Date").reset_index(drop=True)


def _labelSwingStructure(swings: pd.DataFrame) -> pd.DataFrame:
    """Add structure label: HH / HL / LH / LL relative to previous same-kind swing."""
    out = swings.copy()
    if out.empty:
        out["structure"] = pd.Series(dtype=object)
        return out

    last_high = None
    last_low = None
    labels = []
    for _, row in out.iterrows():
        if row["kind"] == "high":
            if last_high is None:
                labels.append("H")
            else:
                labels.append("HH" if row["Price"] > last_high else "LH")
            last_high = row["Price"]
        else:
            if last_low is None:
                labels.append("L")
            else:
                labels.append("HL" if row["Price"] > last_low else "LL")
            last_low = row["Price"]
    out["structure"] = labels
    return out


def _lastSwingPair(swings: pd.DataFrame) -> tuple[dict, dict] | tuple[None, None]:
    """Most recent swing low + swing high (independent of order)."""
    if swings is None or swings.empty:
        return None, None
    lows = swings[swings["kind"] == "low"]
    highs = swings[swings["kind"] == "high"]
    if lows.empty or highs.empty:
        return None, None
    return lows.iloc[-1].to_dict(), highs.iloc[-1].to_dict()


def _activeSwingPair(
    swings: pd.DataFrame,
    *,
    min_span_pct: float = 0.05,
    search: int = 40,
) -> tuple[dict, dict, str] | tuple[None, None, None]:
    """
    Fib anchors from a completed swing move.

    Among the newest ``search`` swings, pick the opposite-kind pair with the
    largest price span (must be ≥ ``min_span_pct`` of mid-price).
    """
    if swings is None or len(swings) < 2:
        return None, None, None

    start_i = max(1, len(swings) - int(search))
    best = None
    best_span = -1.0
    for i in range(len(swings) - 1, start_i - 1, -1):
        last = swings.iloc[i]
        prior = swings[
            (swings["kind"] != last["kind"]) & (swings["index"] < last["index"])
        ]
        if prior.empty:
            continue
        other = prior.iloc[-1]
        lo_p = float(min(last["Price"], other["Price"]))
        hi_p = float(max(last["Price"], other["Price"]))
        mid = 0.5 * (lo_p + hi_p)
        span = hi_p - lo_p
        span_pct = span / max(mid, 1e-12)
        if span_pct < min_span_pct:
            continue
        if last["kind"] == "high":
            pair = (other.to_dict(), last.to_dict(), "up")
        else:
            pair = (last.to_dict(), other.to_dict(), "down")
        if span > best_span:
            best_span = span
            best = pair
    return best if best is not None else (None, None, None)


def _fitLine(xs: np.ndarray, ys: np.ndarray) -> tuple[float, float]:
    """Least-squares slope/intercept: y = slope * x + intercept."""
    if len(xs) < 2:
        raise ValueError("Need at least 2 points to fit a line")
    slope, intercept = np.polyfit(xs.astype(float), ys.astype(float), 1)
    return float(slope), float(intercept)


def _clusterLevels(
    prices: np.ndarray,
    *,
    tol: float,
) -> list[dict]:
    """
    Greedy 1D clustering of price levels within relative tolerance ``tol``.
    Returns list of {price, touches, lo, hi}.
    """
    if len(prices) == 0:
        return []
    prices = np.sort(prices.astype(float))
    clusters: list[list[float]] = [[prices[0]]]
    for p in prices[1:]:
        center = float(np.mean(clusters[-1]))
        if abs(p - center) <= tol * max(abs(center), 1e-12):
            clusters[-1].append(float(p))
        else:
            clusters.append([float(p)])

    levels = []
    for c in clusters:
        arr = np.asarray(c, dtype=float)
        levels.append(
            {
                "price": float(arr.mean()),
                "touches": int(len(arr)),
                "lo": float(arr.min()),
                "hi": float(arr.max()),
            }
        )
    return levels


def _meltCandlePatterns(
    pattern_df: pd.DataFrame,
    ohlc: pd.DataFrame,
    *,
    min_abs: float = 100.0,
) -> pd.DataFrame:
    """Wide CDL_* frame → long Date/Price/pattern/bias/value rows."""
    empty = pd.DataFrame(columns=["Date", "Price", "pattern", "bias", "value", "family"])
    if pattern_df is None or pattern_df.empty:
        return empty

    work = pattern_df.copy()
    work.index = ohlc.index
    rows = []
    for col in work.columns:
        name = str(col)
        if name.upper().startswith("CDL_"):
            name = name[4:]
        name = name.lower()
        # pandas-ta may emit parameterized names like doji_10_0.1
        if "_" in name:
            head = name.split("_", 1)[0]
            # keep multi-word patterns (3whitesoldiers, darkcloudcover, …)
            if not head[0].isdigit():
                # strip trailing numeric params only
                name = re.sub(r"_\d.*$", "", name)
        series = work[col]
        hits = series[series.abs() >= min_abs]
        for idx, val in hits.items():
            v = float(val)
            rows.append(
                {
                    "Date": ohlc.at[idx, "Date"],
                    "Price": float(ohlc.at[idx, "Close"]),
                    "pattern": name,
                    "bias": "bullish" if v > 0 else "bearish",
                    "value": v,
                    "family": "candle",
                }
            )
    if not rows:
        return empty
    return (
        pd.DataFrame(rows)
        .sort_values(["Date", "pattern"])
        .reset_index(drop=True)
    )


def _indicatorAtDates(
    indicator: pd.DataFrame,
    dates: pd.Series,
    *,
    value_col: str,
    date_col: str = "Date",
) -> pd.Series:
    """Nearest-date lookup of indicator values for swing dates."""
    ind = indicator[[date_col, value_col]].dropna().copy()
    ind[date_col] = pd.to_datetime(ind[date_col])
    ind = ind.sort_values(date_col).reset_index(drop=True)
    values = []
    for ts in pd.to_datetime(dates):
        i = (ind[date_col] - ts).abs().idxmin()
        values.append(float(ind.at[i, value_col]))
    return pd.Series(values, index=dates.index)


def _findDivergences(
    swings: pd.DataFrame,
    ind_values: pd.Series,
    *,
    mode: str = "both",
) -> pd.DataFrame:
    """
    Pair consecutive same-kind swings and classify regular / hidden divergence.
    ``ind_values`` aligned to ``swings`` index.
    """
    empty = pd.DataFrame(
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
    if swings is None or len(swings) < 2:
        return empty

    want_regular = mode in {"regular", "both"}
    want_hidden = mode in {"hidden", "both"}
    rows = []
    work = swings.copy()
    work["ind"] = ind_values.to_numpy()

    for skind in ("low", "high"):
        pts = work[work["kind"] == skind].sort_values("index")
        if len(pts) < 2:
            continue
        for i in range(1, len(pts)):
            a = pts.iloc[i - 1]
            b = pts.iloc[i]
            pa, pb = float(a["Price"]), float(b["Price"])
            ia, ib = float(a["ind"]), float(b["ind"])
            if pa == pb or ia == ib:
                continue

            bias = None
            div_mode = None
            if skind == "low":
                if want_regular and pb < pa and ib > ia:
                    bias, div_mode = "bullish", "regular"
                elif want_hidden and pb > pa and ib < ia:
                    bias, div_mode = "bullish", "hidden"
            else:
                if want_regular and pb > pa and ib < ia:
                    bias, div_mode = "bearish", "regular"
                elif want_hidden and pb < pa and ib > ia:
                    bias, div_mode = "bearish", "hidden"

            if bias is None:
                continue
            rows.append(
                {
                    "start_date": a["Date"],
                    "end_date": b["Date"],
                    "price_start": pa,
                    "price_end": pb,
                    "ind_start": ia,
                    "ind_end": ib,
                    "bias": bias,
                    "mode": div_mode,
                    "swing_kind": skind,
                }
            )

    if not rows:
        return empty
    return pd.DataFrame(rows).sort_values("end_date").reset_index(drop=True)


def _annotateHhLl(swings: pd.DataFrame) -> pd.DataFrame:
    """
    Add running trend + BOS/ChoCH events on labeled swing structure.

    HH in uptrend → bos (bullish continuation)
    LL in downtrend → bos (bearish continuation)
    HH while downtrend → choch (bullish reversal)
    LL while uptrend → choch (bearish reversal)
    """
    empty_cols = ["Date", "Price", "kind", "structure", "trend", "event", "index"]
    if swings is None or swings.empty:
        return pd.DataFrame(columns=empty_cols)

    out = swings.copy()
    if "structure" not in out.columns:
        out = _labelSwingStructure(out)

    trend = "range"
    events: list[str | None] = []
    trends: list[str] = []

    for _, row in out.iterrows():
        label = str(row["structure"])
        event = None

        if label == "HH":
            if trend == "down":
                event = "choch"
            elif trend == "up":
                event = "bos"
            trend = "up"
        elif label == "LL":
            if trend == "up":
                event = "choch"
            elif trend == "down":
                event = "bos"
            trend = "down"
        elif label == "HL":
            # higher low — confirms / starts uptrend context
            if trend != "down":
                trend = "up"
        elif label == "LH":
            if trend != "up":
                trend = "down"
        # bare H/L keep current trend

        trends.append(trend)
        events.append(event)

    out["trend"] = trends
    out["event"] = events
    return out.reset_index(drop=True)


def _mergeOverlappingRanges(ranges: list[dict]) -> list[dict]:
    """Merge overlapping/nearby ranges; keep the wider / longer span."""
    if not ranges:
        return []
    ranges = sorted(ranges, key=lambda r: (r["start_index"], r["end_index"]))
    merged = [ranges[0]]
    for r in ranges[1:]:
        prev = merged[-1]
        # overlap or abut
        if r["start_index"] <= prev["end_index"] + 2:
            prev["end_index"] = max(prev["end_index"], r["end_index"])
            prev["end_date"] = max(prev["end_date"], r["end_date"])
            prev["top"] = max(prev["top"], r["top"])
            prev["bottom"] = min(prev["bottom"], r["bottom"])
            prev["touches_top"] = max(prev["touches_top"], r["touches_top"])
            prev["touches_bottom"] = max(prev["touches_bottom"], r["touches_bottom"])
            mid = 0.5 * (prev["top"] + prev["bottom"])
            prev["mid"] = mid
            prev["width_pct"] = (prev["top"] - prev["bottom"]) / max(abs(mid), 1e-12)
            prev["n_bars"] = int(prev["end_index"] - prev["start_index"] + 1)
        else:
            merged.append(dict(r))
    return merged


def _detectRanges(
    ohlc: pd.DataFrame,
    *,
    window: int = 40,
    max_width_pct: float = 0.12,
    min_touches: int = 2,
    touch_tol: float = 0.008,
    step: int = 5,
) -> pd.DataFrame:
    """
    Sliding-window consolidation boxes.

    A window is a range when (max High − min Low) / mid ≤ max_width_pct and
    both the top and bottom edges are touched at least ``min_touches`` times.
    Tries ``window`` and nearby sizes for robustness.
    """
    empty = pd.DataFrame(
        columns=[
            "start_date",
            "end_date",
            "start_index",
            "end_index",
            "top",
            "bottom",
            "mid",
            "width_pct",
            "touches_top",
            "touches_bottom",
            "n_bars",
        ]
    )
    n = len(ohlc)
    windows = sorted({int(window), max(15, int(window * 0.75)), int(window * 1.25), 30, 50})
    windows = [w for w in windows if w < n]
    if not windows:
        return empty

    highs = ohlc["High"].to_numpy(dtype=float)
    lows = ohlc["Low"].to_numpy(dtype=float)
    dates = ohlc["Date"]
    found: list[dict] = []

    for win in windows:
        for start in range(0, n - win + 1, max(1, int(step))):
            end = start + win - 1
            top = float(np.nanmax(highs[start : end + 1]))
            bottom = float(np.nanmin(lows[start : end + 1]))
            mid = 0.5 * (top + bottom)
            width_pct = (top - bottom) / max(abs(mid), 1e-12)
            if width_pct > max_width_pct or width_pct <= 0:
                continue

            tol = touch_tol * max(abs(mid), 1e-12)
            touches_top = int(np.sum(highs[start : end + 1] >= top - tol))
            touches_bottom = int(np.sum(lows[start : end + 1] <= bottom + tol))
            if touches_top < min_touches or touches_bottom < min_touches:
                continue

            found.append(
                {
                    "start_date": dates.iloc[start],
                    "end_date": dates.iloc[end],
                    "start_index": int(start),
                    "end_index": int(end),
                    "top": top,
                    "bottom": bottom,
                    "mid": mid,
                    "width_pct": float(width_pct),
                    "touches_top": touches_top,
                    "touches_bottom": touches_bottom,
                    "n_bars": int(win),
                }
            )

    merged = _mergeOverlappingRanges(found)
    if not merged:
        return empty
    return (
        pd.DataFrame(merged)
        .sort_values(["n_bars", "width_pct"], ascending=[False, True])
        .reset_index(drop=True)
    )


def _fitPriceChannel(
    ohlc: pd.DataFrame,
    *,
    start: int,
    end: int,
    flat_slope: float = 1e-4,
) -> dict | None:
    """
    Parallel channel over [start, end] (inclusive bar indices).

    Slope from Close regression; upper/lower intercepts from extreme
    High/Low residuals so both rails share the same slope.
    """
    if end - start < 5:
        return None
    seg = ohlc.iloc[start : end + 1]
    xs = np.arange(start, end + 1, dtype=float)
    closes = seg["Close"].to_numpy(dtype=float)
    highs = seg["High"].to_numpy(dtype=float)
    lows = seg["Low"].to_numpy(dtype=float)

    slope, mid_b = _fitLine(xs, closes)
    line = slope * xs + mid_b
    upper_b = mid_b + float(np.nanmax(highs - line))
    lower_b = mid_b + float(np.nanmin(lows - line))
    if upper_b <= lower_b:
        return None

    mid_price = float(np.nanmean(closes))
    width = upper_b - lower_b
    # normalize slope roughly as relative move per bar
    rel_slope = slope / max(abs(mid_price), 1e-12)
    if rel_slope > flat_slope:
        kind = "up"
    elif rel_slope < -flat_slope:
        kind = "down"
    else:
        kind = "flat"

    y_u0 = slope * start + upper_b
    y_u1 = slope * end + upper_b
    y_l0 = slope * start + lower_b
    y_l1 = slope * end + lower_b

    return {
        "kind": kind,
        "slope": float(slope),
        "upper_intercept": float(upper_b),
        "lower_intercept": float(lower_b),
        "start_date": seg["Date"].iloc[0],
        "end_date": seg["Date"].iloc[-1],
        "start_index": int(start),
        "end_index": int(end),
        "upper_start": float(y_u0),
        "upper_end": float(y_u1),
        "lower_start": float(y_l0),
        "lower_end": float(y_l1),
        "width": float(width),
        "width_pct": float(width / max(abs(mid_price), 1e-12)),
        "n_bars": int(end - start + 1),
    }


def _detectChannels(
    ohlc: pd.DataFrame,
    *,
    window: int = 60,
    step: int = 10,
    max_channels: int = 3,
    max_width_pct: float = 0.25,
) -> pd.DataFrame:
    """Slide windows and keep the tightest parallel channels."""
    empty = pd.DataFrame(
        columns=[
            "kind",
            "slope",
            "upper_intercept",
            "lower_intercept",
            "start_date",
            "end_date",
            "start_index",
            "end_index",
            "upper_start",
            "upper_end",
            "lower_start",
            "lower_end",
            "width",
            "width_pct",
            "n_bars",
        ]
    )
    n = len(ohlc)
    if n < window:
        # fall back to full series
        ch = _fitPriceChannel(ohlc, start=0, end=n - 1)
        return pd.DataFrame([ch]) if ch else empty

    cands: list[dict] = []
    for start in range(0, n - window + 1, max(1, int(step))):
        end = start + window - 1
        ch = _fitPriceChannel(ohlc, start=start, end=end)
        if ch is None:
            continue
        if ch["width_pct"] > max_width_pct:
            continue
        cands.append(ch)

    # also include the most recent window and a longer lookback
    for start, end in ((max(0, n - window), n - 1), (max(0, n - 2 * window), n - 1)):
        ch = _fitPriceChannel(ohlc, start=start, end=end)
        if ch is not None and ch["width_pct"] <= max_width_pct:
            cands.append(ch)

    if not cands:
        return empty

    # prefer recent + tighter channels; de-dupe by overlapping start
    cands = sorted(cands, key=lambda c: (c["end_index"], -c["width_pct"]), reverse=True)
    picked: list[dict] = []
    for c in cands:
        if any(
            abs(c["start_index"] - p["start_index"]) < window // 2
            and abs(c["end_index"] - p["end_index"]) < window // 2
            for p in picked
        ):
            continue
        picked.append(c)
        if len(picked) >= max_channels:
            break

    return pd.DataFrame(picked).reset_index(drop=True)


def _atrSeries(ohlc: pd.DataFrame, period: int = 14) -> np.ndarray:
    """Simple rolling ATR from OHLC true range."""
    high = ohlc["High"].to_numpy(dtype=float)
    low = ohlc["Low"].to_numpy(dtype=float)
    close = ohlc["Close"].to_numpy(dtype=float)
    prev_close = np.roll(close, 1)
    prev_close[0] = close[0]
    tr = np.maximum(
        high - low,
        np.maximum(np.abs(high - prev_close), np.abs(low - prev_close)),
    )
    return pd.Series(tr).rolling(period, min_periods=1).mean().to_numpy(dtype=float)


def _zigzagTrendLegs(
    ohlc: pd.DataFrame,
    *,
    sensitivity: float = 0.05,
    mode: str = "pct",
    atr_period: int = 14,
    atr_mult: float | None = None,
) -> pd.DataFrame:
    """
    ZigZag-style up/down trend legs.

    ``sensitivity`` = minimum adverse move to flip the trend:
      - mode=\"pct\": fraction of pivot price (0.02–0.04 = reactive,
        0.10–0.20 = big picture)
      - mode=\"atr\": ATR multiple (``atr_mult`` or ``sensitivity`` as the multiple)
    """
    empty = pd.DataFrame(
        columns=[
            "start_date",
            "end_date",
            "start_index",
            "end_index",
            "direction",
            "start_price",
            "end_price",
            "move_pct",
            "n_bars",
            "sensitivity",
            "mode",
        ]
    )
    n = len(ohlc)
    if n < 3:
        return empty

    highs = ohlc["High"].to_numpy(dtype=float)
    lows = ohlc["Low"].to_numpy(dtype=float)
    dates = ohlc["Date"]
    atr = _atrSeries(ohlc, atr_period) if mode == "atr" else None
    mult = float(atr_mult) if atr_mult is not None else float(sensitivity)

    def _thresh(i: int, price: float) -> float:
        if mode == "atr":
            return max(float(atr[i]) * mult, 1e-12)
        return max(abs(price) * float(sensitivity), 1e-12)

    # Start from first low; rise until reversal
    pivots: list[tuple[int, float]] = [(0, float(lows[0]))]
    trend_dir = 1  # 1 = seeking high, -1 = seeking low
    ext_i = 0
    ext_price = float(lows[0])

    for i in range(1, n):
        h, l = float(highs[i]), float(lows[i])
        thr = _thresh(i, ext_price)

        if trend_dir == 1:
            if h >= ext_price:
                ext_i, ext_price = i, h
            elif ext_price - l >= thr:
                pivots.append((ext_i, ext_price))
                trend_dir = -1
                ext_i, ext_price = i, l
        else:
            if l <= ext_price:
                ext_i, ext_price = i, l
            elif h - ext_price >= thr:
                pivots.append((ext_i, ext_price))
                trend_dir = 1
                ext_i, ext_price = i, h

    if pivots[-1][0] != ext_i:
        pivots.append((ext_i, ext_price))

    cleaned: list[tuple[int, float]] = []
    for idx, price in pivots:
        if cleaned and cleaned[-1][0] == idx:
            cleaned[-1] = (idx, price)
        else:
            cleaned.append((idx, price))
    pivots = cleaned
    if len(pivots) < 2:
        return empty

    sens_out = float(sensitivity if mode == "pct" else mult)
    rows = []
    for (i0, p0), (i1, p1) in zip(pivots[:-1], pivots[1:]):
        if i1 <= i0:
            continue
        direction = "up" if p1 >= p0 else "down"
        mid = 0.5 * (abs(p0) + abs(p1))
        rows.append(
            {
                "start_date": dates.iloc[i0],
                "end_date": dates.iloc[i1],
                "start_index": int(i0),
                "end_index": int(i1),
                "direction": direction,
                "start_price": float(p0),
                "end_price": float(p1),
                "move_pct": float(abs(p1 - p0) / max(mid, 1e-12)),
                "n_bars": int(i1 - i0),
                "sensitivity": sens_out,
                "mode": mode,
            }
        )
    if not rows:
        return empty
    return pd.DataFrame(rows).reset_index(drop=True)


_DEFAULT_CHART_PATTERNS = (
    "double_top",
    "double_bottom",
    "triple_top",
    "triple_bottom",
    "hs_top",
    "hs_bottom",
    "ascending_triangle",
    "descending_triangle",
    "symmetrical_triangle",
    "flag_bull",
    "flag_bear",
    "pennant_bull",
    "pennant_bear",
    "rising_wedge",
    "falling_wedge",
    "cup_with_handle",
)


def _meltChartSignals(
    signals: dict,
    ohlc: pd.DataFrame,
) -> pd.DataFrame:
    """Dict[name -> ±1/0 ndarray] → long Date/Price/pattern/bias/value/family."""
    empty = pd.DataFrame(
        columns=["Date", "Price", "pattern", "bias", "value", "family"]
    )
    if not signals:
        return empty
    rows = []
    for name, arr in signals.items():
        arr = np.asarray(arr).reshape(-1)
        if len(arr) != len(ohlc):
            continue
        nz = np.flatnonzero(arr != 0)
        for i in nz:
            v = float(arr[i])
            rows.append(
                {
                    "Date": ohlc.at[i, "Date"],
                    "Price": float(ohlc.at[i, "Close"]),
                    "pattern": str(name),
                    "bias": "bullish" if v > 0 else "bearish",
                    "value": v,
                    "family": "chart",
                }
            )
    if not rows:
        return empty
    return (
        pd.DataFrame(rows)
        .sort_values(["Date", "pattern"])
        .reset_index(drop=True)
    )


def _scanChartPatterns(
    ohlc: pd.DataFrame,
    *,
    patterns: tuple[str, ...] | list[str] | str,
    mode: str = "confirmed",
    window: int = 100,
    pivot_n: int = 5,
) -> pd.DataFrame:
    """Run selected ta_patterns chart detectors."""
    import ta_patterns.chart_patterns as cp

    if patterns == "all":
        names = list(cp.chart_list_patterns())
    else:
        names = list(patterns)

    o = ohlc["Open"].astype(float).to_numpy()
    h = ohlc["High"].astype(float).to_numpy()
    l = ohlc["Low"].astype(float).to_numpy()
    c = ohlc["Close"].astype(float).to_numpy()
    v = ohlc["Volume"].astype(float).to_numpy() if "Volume" in ohlc.columns else None

    out: dict = {}
    for name in names:
        fn = getattr(cp, name, None)
        if fn is None or not callable(fn):
            continue
        try:
            # most accept o,h,l,c + mode/window/pivot_n; volume patterns need v
            kwargs = {}
            import inspect

            sig = inspect.signature(fn)
            params = sig.parameters
            args = [o, h, l, c]
            if "v" in params and v is not None:
                # positional v after c for some; prefer kw
                pass
            call_kw = {}
            if "mode" in params:
                call_kw["mode"] = mode
            if "window" in params:
                call_kw["window"] = window
            if "pivot_n" in params:
                call_kw["pivot_n"] = pivot_n
            if "v" in params and v is not None:
                call_kw["v"] = v
            arr = fn(*args, **call_kw)
            out[name] = arr
        except TypeError:
            try:
                out[name] = fn(o, h, l, c)
            except Exception:
                continue
        except Exception:
            continue
    return _meltChartSignals(out, ohlc)


def _detectGaps(
    ohlc: pd.DataFrame,
    *,
    min_gap_pct: float = 0.002,
    lookforward: int = 40,
) -> pd.DataFrame:
    """
    OHLC gaps between consecutive bars.

    gap up: Low[i] > High[i-1]
    gap down: High[i] < Low[i-1]
    """
    empty = pd.DataFrame(
        columns=[
            "Date",
            "direction",
            "gap_top",
            "gap_bottom",
            "gap_pct",
            "filled",
            "fill_date",
            "index",
        ]
    )
    n = len(ohlc)
    if n < 2:
        return empty

    highs = ohlc["High"].to_numpy(dtype=float)
    lows = ohlc["Low"].to_numpy(dtype=float)
    dates = ohlc["Date"]
    rows = []
    for i in range(1, n):
        prev_h, prev_l = highs[i - 1], lows[i - 1]
        h, l = highs[i], lows[i]
        mid = 0.5 * (prev_h + prev_l)
        if l > prev_h:
            top, bottom = float(l), float(prev_h)
            direction = "up"
        elif h < prev_l:
            top, bottom = float(prev_l), float(h)
            direction = "down"
        else:
            continue
        gap_pct = (top - bottom) / max(abs(mid), 1e-12)
        if gap_pct < min_gap_pct:
            continue

        filled = False
        fill_date = pd.NaT
        end = min(n, i + max(1, int(lookforward)))
        for j in range(i, end):
            if direction == "up" and lows[j] <= bottom:
                filled = True
                fill_date = dates.iloc[j]
                break
            if direction == "down" and highs[j] >= top:
                filled = True
                fill_date = dates.iloc[j]
                break

        rows.append(
            {
                "Date": dates.iloc[i],
                "direction": direction,
                "gap_top": top,
                "gap_bottom": bottom,
                "gap_pct": float(gap_pct),
                "filled": filled,
                "fill_date": fill_date,
                "index": int(i),
            }
        )
    if not rows:
        return empty
    return pd.DataFrame(rows).reset_index(drop=True)


def _detectWyckoff(
    ohlc: pd.DataFrame,
    *,
    window: int = 40,
    max_width_pct: float = 0.15,
    lookforward: int = 30,
    volume_mult: float = 1.2,
) -> pd.DataFrame:
    """
    Wyckoff-style events around consolidation ranges.

    Events: spring, upthrust, sos (sign of strength), sow (sign of weakness).
    Phase: accumulation / distribution / markup / markdown / ranging.
    """
    empty = pd.DataFrame(
        columns=[
            "Date",
            "event",
            "phase",
            "Price",
            "range_top",
            "range_bottom",
            "range_start",
            "range_end",
            "index",
        ]
    )
    ranges = _detectRanges(
        ohlc, window=window, max_width_pct=max_width_pct, min_touches=2, step=5
    )
    if ranges.empty:
        return empty

    highs = ohlc["High"].to_numpy(dtype=float)
    lows = ohlc["Low"].to_numpy(dtype=float)
    closes = ohlc["Close"].to_numpy(dtype=float)
    dates = ohlc["Date"]
    n = len(ohlc)
    has_vol = "Volume" in ohlc.columns
    vol = ohlc["Volume"].astype(float).to_numpy() if has_vol else None
    vol_ma = (
        pd.Series(vol).rolling(20, min_periods=5).mean().to_numpy()
        if has_vol
        else None
    )

    rows = []
    for _, rg in ranges.iterrows():
        top = float(rg["top"])
        bottom = float(rg["bottom"])
        rs, re = int(rg["start_index"]), int(rg["end_index"])
        # search inside range + short follow-through
        i0 = rs
        i1 = min(n - 1, re + int(lookforward))

        spring_i = upthrust_i = sos_i = sow_i = None
        for i in range(i0, i1 + 1):
            # spring: pierce below then reclaim
            if spring_i is None and lows[i] < bottom and closes[i] > bottom:
                if i >= rs:  # in/near range
                    spring_i = i
            # upthrust: pierce above then reject
            if upthrust_i is None and highs[i] > top and closes[i] < top:
                if i >= rs:
                    upthrust_i = i
            # SOS / SOW: decisive closes outside with optional volume
            vol_ok = True
            if has_vol and vol_ma is not None and not np.isnan(vol_ma[i]):
                vol_ok = vol[i] >= volume_mult * vol_ma[i]
            if sos_i is None and closes[i] > top and vol_ok and i >= re - 2:
                sos_i = i
            if sow_i is None and closes[i] < bottom and vol_ok and i >= re - 2:
                sow_i = i

        # phase from aftermath
        after = closes[min(n - 1, re + 1) : min(n, re + lookforward + 1)]
        if len(after) == 0:
            phase = "ranging"
        else:
            last = float(after[-1])
            if last > top:
                phase = "markup" if spring_i is not None or sos_i is not None else "markup"
            elif last < bottom:
                phase = "markdown"
            else:
                phase = "accumulation" if spring_i is not None else (
                    "distribution" if upthrust_i is not None else "ranging"
                )

        def _add(event, idx):
            if idx is None:
                return
            rows.append(
                {
                    "Date": dates.iloc[idx],
                    "event": event,
                    "phase": phase,
                    "Price": float(closes[idx]),
                    "range_top": top,
                    "range_bottom": bottom,
                    "range_start": rg["start_date"],
                    "range_end": rg["end_date"],
                    "index": int(idx),
                }
            )

        _add("spring", spring_i)
        _add("upthrust", upthrust_i)
        _add("sos", sos_i)
        _add("sow", sow_i)

        # always emit a phase marker at range end if no events
        if spring_i is None and upthrust_i is None and sos_i is None and sow_i is None:
            rows.append(
                {
                    "Date": dates.iloc[re],
                    "event": "range",
                    "phase": phase,
                    "Price": float(closes[re]),
                    "range_top": top,
                    "range_bottom": bottom,
                    "range_start": rg["start_date"],
                    "range_end": rg["end_date"],
                    "index": int(re),
                }
            )

    if not rows:
        return empty
    return (
        pd.DataFrame(rows)
        .drop_duplicates(subset=["Date", "event"], keep="first")
        .sort_values("Date")
        .reset_index(drop=True)
    )
