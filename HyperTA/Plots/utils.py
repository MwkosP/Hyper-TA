"""Internal plot helpers — all _* helpers for Plots/ modules.

Organized by consumer file. Public plot APIs stay in asset.py / signals.py /
indicators.py / etc.
"""

from __future__ import annotations

import os
import subprocess
import sys
import warnings
from io import BytesIO
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


# =============================================================================
# ## __________ shared (all plot modules) __________
# =============================================================================

_THEMES = {
    "hyperta": {
        "figsize": (14, 6),
        "facecolor": "white",
        "price_color": "#333333",
        "grid_color": "#cccccc",
        "title_size": 12,
        "label_size": 9,
        "dpi": 140,
    },
}


def _theme(name: str = "hyperta") -> dict:
    return _THEMES.get(name, _THEMES["hyperta"]).copy()


def _applyTheme(ax, *, theme: str = "hyperta") -> None:
    cfg = _theme(theme)
    ax.set_facecolor(cfg["facecolor"])
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(True, linestyle=":", linewidth=0.5, color=cfg["grid_color"])
    ax.tick_params(length=3, width=0.5, labelsize=cfg["label_size"])


def _backendInteractive() -> bool:
    name = matplotlib.get_backend().lower()
    non_interactive = {
        "agg",
        "cairo",
        "svg",
        "pdf",
        "ps",
        "template",
        "module://matplotlib.backends.backend_agg",
    }
    return name not in non_interactive and not name.endswith(".backend_agg")


def _ensureShowBackend() -> None:
    """Prefer an interactive GUI backend when the user wants to display plots."""
    if _backendInteractive():
        return
    for backend in ("TkAgg", "QtAgg", "Qt5Agg", "GTK4Agg", "GTK3Agg"):
        try:
            matplotlib.use(backend, force=True)
            if _backendInteractive():
                return
        except Exception:
            continue


def _openImage(path: Path) -> None:
    """Open a saved PNG with the OS default viewer."""
    path = Path(path)
    try:
        if os.name == "nt":
            os.startfile(path)  # type: ignore[attr-defined]
        elif sys.platform == "darwin":
            subprocess.Popen(["open", str(path)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            subprocess.Popen(["xdg-open", str(path)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e:
        warnings.warn(f"Could not open image viewer for {path}: {e}", UserWarning, stacklevel=3)


def _maximizeFigure(fig) -> None:
    """Maximize the GUI window so the figure fills the screen."""
    try:
        manager = fig.canvas.manager
        if manager is None:
            return
        window = getattr(manager, "window", None)

        # TkAgg — Linux
        if window is not None and hasattr(window, "attributes"):
            try:
                window.attributes("-zoomed", True)
                return
            except Exception:
                pass

        # TkAgg — Windows
        if window is not None and hasattr(window, "state"):
            try:
                window.state("zoomed")
                return
            except Exception:
                pass

        # QtAgg / Qt5Agg
        if window is not None and hasattr(window, "showMaximized"):
            try:
                window.showMaximized()
                return
            except Exception:
                pass

        # Generic fallback: stretch to reported screen max
        if window is not None and hasattr(window, "maxsize") and hasattr(manager, "resize"):
            try:
                w, h = window.maxsize()
                if w and h:
                    manager.resize(int(w), int(h))
            except Exception:
                pass
    except Exception:
        pass


def _resolveOutputPath(output: str | Path, *, default_name: str = "plot.png") -> Path:
    """File path to write. Directory (or trailing slash) → ``default_name`` inside it."""
    raw = str(output)
    path = Path(output)
    if raw.endswith(("/", "\\")) or path.is_dir():
        path.mkdir(parents=True, exist_ok=True)
        return path / default_name
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def _render(
    fig,
    *,
    output: str | Path | BytesIO | None = None,
    show: bool = True,
    dpi: int | None = None,
    theme: str = "hyperta",
) -> Path | BytesIO | None:
    """
    Display and/or save a figure.

    Never writes a file unless ``output`` is set explicitly.
    No Cache/ default — pass e.g. ``output=\"/path/to/plot.png\"`` or a directory.
    """
    cfg = _theme(theme)
    dpi = dpi or cfg["dpi"]

    saved: Path | BytesIO | None = None
    if output is not None:
        if isinstance(output, BytesIO):
            fig.savefig(output, format="png", dpi=dpi, bbox_inches="tight", facecolor=cfg["facecolor"])
            output.seek(0)
            saved = output
        else:
            path = _resolveOutputPath(output)
            fig.savefig(path, format="png", dpi=dpi, bbox_inches="tight", facecolor=cfg["facecolor"])
            saved = path

    if show:
        if _backendInteractive():
            _maximizeFigure(fig)
            plt.show()
        elif isinstance(saved, Path):
            _openImage(saved)
        else:
            warnings.warn(
                "Could not display plot (no interactive matplotlib backend). "
                "Pass output='path.png' to save, or install a GUI backend (e.g. TkAgg).",
                UserWarning,
                stacklevel=3,
            )

    plt.close(fig)
    return saved


# =============================================================================
# ## __________ asset.py helpers __________
# =============================================================================

_CHART_TYPES = {
    "doji": "hollow_and_filled",
    "candle": "candle",
    "candles": "candle",
    "line": "line",
    "ohlc": "ohlc",
    "bars": "ohlc",
}


def _resolveChartType(chart: str) -> str:
    key = str(chart).strip().lower()
    if key not in _CHART_TYPES:
        raise ValueError(
            f"Unknown chart={chart!r}. Expected one of: {sorted(_CHART_TYPES)}"
        )
    return _CHART_TYPES[key]


def _prepareOhlc(
    df: pd.DataFrame,
    *,
    date_col: str = "Date",
) -> pd.DataFrame:
    """
    Build an OHLC DataFrame indexed by DatetimeIndex for mplfinance.

    Accepts Open/High/Low/Close (any common casing). If only Close exists,
    OHLC are filled from Close so line/candle still render.
    """
    out = df.copy()
    if date_col not in out.columns:
        out = out.reset_index()
        if date_col not in out.columns:
            for candidate in ("Date", "date", "Datetime", "datetime"):
                if candidate in out.columns:
                    date_col = candidate
                    break
    if date_col not in out.columns:
        raise ValueError(f"DataFrame must contain a date column (expected '{date_col}')")

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
        ("Adj Close", "Close"),
        ("Volume", "Volume"),
        ("volume", "Volume"),
    ):
        if src in out.columns and dst not in rename.values():
            rename[src] = dst
    out = out.rename(columns=rename)

    if "Close" not in out.columns:
        raise ValueError("DataFrame must contain a Close column for charting")

    for col in ("Open", "High", "Low"):
        if col not in out.columns:
            out[col] = out["Close"]

    out[date_col] = pd.to_datetime(out[date_col])
    ohlc = (
        out[[date_col, "Open", "High", "Low", "Close"] + (["Volume"] if "Volume" in out.columns else [])]
        .sort_values(date_col)
        .drop_duplicates(subset=[date_col])
        .set_index(date_col)
    )
    ohlc.index.name = "Date"
    return ohlc


def _attachCrosshair(ax, ohlc: pd.DataFrame | None = None) -> None:
    """Hover crosshair: dotted H/V lines + small OHLC price window."""
    import matplotlib.dates as mdates

    hline = ax.axhline(0, color="#555555", lw=0.9, ls=":", visible=False, zorder=10)
    vline = ax.axvline(0, color="#555555", lw=0.9, ls=":", visible=False, zorder=10)
    panel = ax.text(
        0.01,
        0.99,
        "",
        transform=ax.transAxes,
        va="top",
        ha="left",
        fontsize=8,
        family="monospace",
        color="#222222",
        zorder=11,
        bbox={
            "boxstyle": "round,pad=0.45",
            "facecolor": "#fafafa",
            "edgecolor": "#bbbbbb",
            "alpha": 0.95,
        },
    )

    x_nums = None
    if ohlc is not None and len(ohlc) > 0:
        try:
            x_nums = mdates.date2num(pd.to_datetime(ohlc.index).to_pydatetime())
        except Exception:
            x_nums = np.arange(len(ohlc), dtype=float)

    def _barAt(xdata: float):
        if ohlc is None or len(ohlc) == 0:
            return None
        if x_nums is not None and float(xdata) > len(ohlc) + 5:
            i = int(np.argmin(np.abs(x_nums - float(xdata))))
        else:
            i = int(round(float(xdata)))
        i = max(0, min(len(ohlc) - 1, i))
        return i, ohlc.iloc[i]

    def _fmt(v) -> str:
        try:
            return f"{float(v):,.4g}"
        except Exception:
            return str(v)

    def _onMove(event):
        if event.inaxes is not ax or event.xdata is None or event.ydata is None:
            if hline.get_visible():
                hline.set_visible(False)
                vline.set_visible(False)
                panel.set_text("")
                ax.figure.canvas.draw_idle()
            return

        hline.set_ydata([event.ydata, event.ydata])
        vline.set_xdata([event.xdata, event.xdata])
        hline.set_visible(True)
        vline.set_visible(True)

        hit = _barAt(event.xdata)
        if hit is not None:
            _, row = hit
            ts = row.name
            try:
                date_txt = pd.Timestamp(ts).strftime("%Y-%m-%d %H:%M")
                if date_txt.endswith(" 00:00"):
                    date_txt = date_txt[:10]
            except Exception:
                date_txt = str(ts)

            lines = [
                date_txt,
                f"O  {_fmt(row['Open'])}",
                f"H  {_fmt(row['High'])}",
                f"L  {_fmt(row['Low'])}",
                f"C  {_fmt(row['Close'])}",
            ]
            if "Volume" in row.index and pd.notna(row["Volume"]):
                lines.append(f"V  {_fmt(row['Volume'])}")
            lines.append(f"Y  {_fmt(event.ydata)}")
            panel.set_text("\n".join(lines))
        else:
            try:
                x_txt = mdates.num2date(event.xdata).strftime("%Y-%m-%d")
            except Exception:
                x_txt = f"{event.xdata:.4g}"
            panel.set_text(f"{x_txt}\nY  {_fmt(event.ydata)}")

        ax.figure.canvas.draw_idle()

    ax.figure.canvas.mpl_connect("motion_notify_event", _onMove)


# =============================================================================
# ## __________ signals.py helpers __________
# =============================================================================

def _prepareSeries(
    df: pd.DataFrame,
    *,
    date_col: str = "Date",
    value_col: str = "Close",
) -> tuple[pd.DataFrame, str, str]:
    """Normalize date column and return sorted copy."""
    out = df.copy()
    if date_col not in out.columns:
        out = out.reset_index()
        if date_col not in out.columns:
            for candidate in ("Date", "date", "Datetime", "datetime"):
                if candidate in out.columns:
                    date_col = candidate
                    break

    if value_col not in out.columns:
        for candidate in ("Close", "close", "Adj Close", "Price"):
            if candidate in out.columns:
                value_col = candidate
                break

    if date_col not in out.columns:
        raise ValueError(f"DataFrame must contain a date column (expected '{date_col}')")
    if value_col not in out.columns:
        raise ValueError(f"DataFrame must contain a price column (expected '{value_col}')")

    out[date_col] = pd.to_datetime(out[date_col])
    return out.sort_values(date_col), date_col, value_col


def _normalizeSignalDates(signal_dates) -> pd.DatetimeIndex:
    """Accept list/Index/Series/DataFrame(Date) of signal timestamps."""
    if signal_dates is None:
        return pd.DatetimeIndex([])
    if isinstance(signal_dates, pd.DataFrame):
        if "Date" in signal_dates.columns:
            return pd.to_datetime(signal_dates["Date"]).drop_duplicates().sort_values()
        raise ValueError("signal DataFrame must contain a 'Date' column")
    return pd.DatetimeIndex(pd.to_datetime(list(signal_dates))).drop_duplicates().sort_values()


def _drawGlowingSignals(
    ax,
    xs,
    ys,
    *,
    color: str = "#ff2d55",
    label: str = "Signal",
    marker: str = "o",
) -> None:
    """Multi-layer scatter to fake a glow around signal points."""
    if len(xs) == 0:
        return
    # outer glow rings
    for size, alpha in ((280, 0.08), (160, 0.14), (90, 0.28)):
        ax.scatter(xs, ys, s=size, c=color, alpha=alpha, edgecolors="none", zorder=4, marker=marker)
    # core
    ax.scatter(
        xs,
        ys,
        s=42,
        c=color,
        alpha=0.95,
        edgecolors="white",
        linewidths=0.6,
        zorder=5,
        marker=marker,
        label=label,
    )


def _signalRowsOnSeries(
    series_df: pd.DataFrame,
    signal_dates: pd.DatetimeIndex,
    *,
    date_col: str = "Date",
    value_col: str,
) -> pd.DataFrame:
    """Match signal dates to nearest rows on a Date+value series."""
    if series_df.empty or len(signal_dates) == 0 or value_col not in series_df.columns:
        return pd.DataFrame(columns=[date_col, value_col])
    work = series_df[[date_col, value_col]].dropna().copy()
    work[date_col] = pd.to_datetime(work[date_col])
    # exact date matches first
    exact = work[work[date_col].isin(signal_dates)]
    if len(exact) == len(signal_dates):
        return exact
    # nearest-date fallback for timezone / missing bars
    work = work.sort_values(date_col)
    rows = []
    for ts in signal_dates:
        idx = (work[date_col] - ts).abs().idxmin()
        rows.append(work.loc[idx])
    out = pd.DataFrame(rows).drop_duplicates(subset=[date_col])
    return out


def _drawIndicatorOnAxes(
    ax,
    indicator_df: pd.DataFrame,
    *,
    kind: str | None,
    cfg: dict,
    price_df: pd.DataFrame | None = None,
) -> tuple[str, str]:
    """
    Reuse plotIndicator templates on an existing axes.

    Returns (resolved_kind, layout).
    For overlay layouts, pass price_df so bands/cloud sit on price (bbands/ichimoku).
    """
    ind = _normalizeInd(indicator_df)
    resolved = (kind or _detectKind(ind)).lower()
    spec = dict(_INDICATOR_SPECS.get(resolved, {"layout": "panel", "columns": None}))
    layout = spec.get("layout", "panel")

    if layout == "macd":
        _drawMacd(ax, ind, spec, cfg)
    elif layout == "overlay":
        _drawOverlay(ax, ind, spec, cfg, price_df=price_df)
    else:
        _drawPanel(ax, ind, spec, cfg)
    return resolved, layout


def _indicatorSignalYCol(ind: pd.DataFrame, kind: str) -> str | None:
    """Pick a Y series on the indicator for glowing signal markers."""
    prefer = {
        "macd": ["macd"],
        "stochrsi": ["stochrsi_k"],
        "rsi": ["rsi"],
        "atr": ["atr"],
        "adx": ["adx"],
        "roc": ["roc"],
        "williams": ["williams"],
        "bbands": ["bb_mid", "bb_upper", "bb_lower"],
        "donchian": ["donchian_mid"],
        "ichimoku": ["tenkan_sen", "kijun_sen"],
        "ma": ["ma"],
        "ema": ["ema"],
        "ema_crossover": ["ema_fast", "ema_slow"],
    }
    cols = prefer.get(kind, []) + [c for c in ind.columns if c != "Date"]
    return next((c for c in cols if c in ind.columns), None)


def _buildSignalsChart(
    df: pd.DataFrame,
    signal_dates=None,
    *,
    indicator_df: pd.DataFrame | None = None,
    kind: str | None = None,
    showIndicator: bool = False,
    showIndicatorSignals: bool = True,
    showSignalsOnIndicator: bool = False,
    price_col: str = "Close",
    date_col: str = "Date",
    label: str = "Price",
    theme: str = "hyperta",
    dpi: int | None = None,
    signal_color: str = "#ff2d55",
    indicator_signal_color: str = "#ff9f0a",
):
    """
    Shared figure builder for plotSignals.

    Returns (fig, ax_price, ax_ind, meta) where meta has keys:
      resolved, layout, is_overlay, dates, cfg, dpi
    Does not show/save — caller runs _render.
    """
    if showIndicator and indicator_df is None:
        raise ValueError("showIndicator=True requires indicator_df=...")

    data, date_col, price_col = _prepareSeries(df, date_col=date_col, value_col=price_col)
    dates = _normalizeSignalDates(signal_dates)
    cfg = _theme(theme)
    dpi = dpi or cfg["dpi"]

    layout = "none"
    resolved = None
    ind = None
    if showIndicator:
        ind = _normalizeInd(indicator_df)
        resolved = (kind or _detectKind(ind)).lower()
        layout = _INDICATOR_SPECS.get(resolved, {}).get("layout", "panel")

    is_overlay = showIndicator and layout == "overlay"

    if is_overlay:
        fig, ax_price = plt.subplots(figsize=cfg["figsize"], dpi=dpi)
        ax_ind = None
    elif showIndicator:
        fig, (ax_price, ax_ind) = plt.subplots(
            2,
            1,
            sharex=True,
            figsize=(cfg["figsize"][0], cfg["figsize"][1] + 2.5),
            dpi=dpi,
            gridspec_kw={"height_ratios": [1.6, 1.0]},
        )
    else:
        fig, ax_price = plt.subplots(figsize=cfg["figsize"], dpi=dpi)
        ax_ind = None

    if is_overlay:
        _drawIndicatorOnAxes(ax_price, ind, kind=resolved, cfg=cfg, price_df=df)
        ax_price.set_ylabel("Price", fontsize=cfg["label_size"])
    else:
        ax_price.plot(
            data[date_col],
            data[price_col],
            color=cfg["price_color"],
            lw=1.2,
            label=label,
            zorder=2,
        )
        ax_price.set_ylabel("Price", fontsize=cfg["label_size"])

    if showIndicatorSignals and len(dates) > 0:
        marked = _signalRowsOnSeries(data, dates, date_col=date_col, value_col=price_col)
        _drawGlowingSignals(
            ax_price,
            marked[date_col],
            marked[price_col],
            color=signal_color,
            label="Signal",
        )

    if is_overlay and showSignalsOnIndicator and len(dates) > 0 and ind is not None:
        y_col = _indicatorSignalYCol(ind, resolved or "")
        if y_col is not None:
            marked_ind = _signalRowsOnSeries(ind, dates, date_col="Date", value_col=y_col)
            _drawGlowingSignals(
                ax_price,
                marked_ind["Date"],
                marked_ind[y_col],
                color=indicator_signal_color,
                label=f"Signal ({y_col})",
                marker="D",
            )
            for ts in marked_ind["Date"]:
                ax_price.axvline(ts, color=indicator_signal_color, lw=0.7, ls=":", alpha=0.45, zorder=3)

    if showIndicator and not is_overlay and ax_ind is not None:
        _drawIndicatorOnAxes(ax_ind, ind, kind=resolved, cfg=cfg, price_df=None)
        ax_ind.set_ylabel(resolved or "indicator", fontsize=cfg["label_size"])

        if showSignalsOnIndicator and len(dates) > 0 and ind is not None:
            y_col = _indicatorSignalYCol(ind, resolved or "")
            if y_col is not None:
                marked_ind = _signalRowsOnSeries(ind, dates, date_col="Date", value_col=y_col)
                _drawGlowingSignals(
                    ax_ind,
                    marked_ind["Date"],
                    marked_ind[y_col],
                    color=indicator_signal_color,
                    label="Signal",
                    marker="D",
                )
                for ts in marked_ind["Date"]:
                    ax_ind.axvline(ts, color=indicator_signal_color, lw=0.7, ls=":", alpha=0.55, zorder=3)

        ax_ind.legend(loc="upper left", fontsize=cfg["label_size"])
        _applyTheme(ax_ind, theme=theme)

    ax_price.legend(loc="upper left", fontsize=cfg["label_size"])
    _applyTheme(ax_price, theme=theme)

    meta = {
        "resolved": resolved,
        "layout": layout,
        "is_overlay": is_overlay,
        "dates": dates,
        "cfg": cfg,
        "dpi": dpi,
        "ind": ind,
    }
    return fig, ax_price, ax_ind, meta


# =============================================================================
# ## __________ indicators.py helpers __________
# =============================================================================

# layout: "panel" | "macd" | "overlay"
_INDICATOR_SPECS: dict[str, dict] = {
    "rsi": {
        "layout": "panel",
        "columns": ["rsi"],
        "hlines": (30, 70),
        "ylim": (0, 100),
    },
    "atr": {"layout": "panel", "columns": ["atr"]},
    "adx": {"layout": "panel", "columns": ["adx"], "hlines": (20, 40), "ylim": (0, 100)},
    "roc": {"layout": "panel", "columns": ["roc"], "hlines": (0,)},
    "williams": {
        "layout": "panel",
        "columns": ["williams"],
        "hlines": (-80, -20),
        "ylim": (-100, 0),
    },
    "stochrsi": {
        "layout": "panel",
        "columns": ["stochrsi_k", "stochrsi_d"],
        "hlines": (0.2, 0.8),
        "ylim": (0, 1),
    },
    "macd": {
        "layout": "macd",
        "columns": ["macd", "signal"],
        "hist": True,
    },
    "ma": {"layout": "overlay", "columns": ["ma"]},
    "ema": {"layout": "overlay", "columns": ["ema"]},
    "ema_crossover": {"layout": "overlay", "columns": ["ema_fast", "ema_slow"]},
    "ema_ribbon": {"layout": "overlay", "columns": None},
    "bbands": {
        "layout": "overlay",
        "columns": ["bb_mid"],
        "band": ("bb_lower", "bb_upper"),
    },
    "donchian": {
        "layout": "overlay",
        "columns": ["donchian_mid"],
        "band": ("donchian_lower", "donchian_upper"),
    },
    "ichimoku": {
        "layout": "overlay",
        "columns": ["tenkan_sen", "kijun_sen", "chikou_span"],
        "cloud": ("senkou_span_a", "senkou_span_b"),
    },
}

_COLUMN_HINTS: list[tuple[frozenset[str], str]] = [
    (frozenset({"rsi"}), "rsi"),
    (frozenset({"atr"}), "atr"),
    (frozenset({"adx"}), "adx"),
    (frozenset({"roc"}), "roc"),
    (frozenset({"williams"}), "williams"),
    (frozenset({"stochrsi_k", "stochrsi_d"}), "stochrsi"),
    (frozenset({"macd", "signal"}), "macd"),
    (frozenset({"bb_lower", "bb_mid", "bb_upper"}), "bbands"),
    (frozenset({"donchian_lower", "donchian_mid", "donchian_upper"}), "donchian"),
    (frozenset({"tenkan_sen", "kijun_sen", "senkou_span_a", "senkou_span_b"}), "ichimoku"),
    (frozenset({"ema_fast", "ema_slow"}), "ema_crossover"),
    (frozenset({"ma"}), "ma"),
    (frozenset({"ema"}), "ema"),
]


def _detectKind(ind_df: pd.DataFrame) -> str:
    cols = {c for c in ind_df.columns if c != "Date"}
    for needed, kind in _COLUMN_HINTS:
        if needed.issubset(cols):
            return kind
    if any(c.startswith("ema_") for c in cols):
        return "ema_ribbon"
    return "panel"


def _normalizeInd(ind_df: pd.DataFrame) -> pd.DataFrame:
    out = ind_df.copy()
    if "Date" not in out.columns:
        out = out.reset_index()
    out["Date"] = pd.to_datetime(out["Date"])
    return out.sort_values("Date")


def _valueColumns(ind_df: pd.DataFrame, spec: dict) -> list[str]:
    cols = spec.get("columns")
    if cols is None:
        return [c for c in ind_df.columns if c != "Date"]
    return [c for c in cols if c in ind_df.columns]


def _drawHlines(ax, hlines, color="#aaaaaa") -> None:
    for y in hlines or ():
        ax.axhline(y, color=color, lw=0.8, ls="--", alpha=0.8)


def _drawPanel(ax, ind_df: pd.DataFrame, spec: dict, cfg: dict) -> None:
    for col in _valueColumns(ind_df, spec):
        ax.plot(ind_df["Date"], ind_df[col], lw=1.2, label=col)
    _drawHlines(ax, spec.get("hlines"))
    if spec.get("ylim"):
        ax.set_ylim(*spec["ylim"])
    ax.legend(loc="upper left", fontsize=cfg["label_size"])
    _applyTheme(ax)


def _drawMacd(ax, ind_df: pd.DataFrame, spec: dict, cfg: dict) -> None:
    if "macd" in ind_df.columns:
        ax.plot(ind_df["Date"], ind_df["macd"], lw=1.2, label="macd", color="#1f77b4")
    if "signal" in ind_df.columns:
        ax.plot(ind_df["Date"], ind_df["signal"], lw=1.2, label="signal", color="#ff7f0e")
    if spec.get("hist") and {"macd", "signal"}.issubset(ind_df.columns):
        hist = ind_df["macd"] - ind_df["signal"]
        colors = np.where(hist >= 0, "#2ca02c", "#d62728")
        ax.bar(ind_df["Date"], hist, width=0.8, color=colors, alpha=0.45, label="hist")
    ax.axhline(0, color="#aaaaaa", lw=0.8, ls="--")
    ax.legend(loc="upper left", fontsize=cfg["label_size"])
    _applyTheme(ax)


def _drawOverlay(
    ax,
    ind_df: pd.DataFrame,
    spec: dict,
    cfg: dict,
    price_df: pd.DataFrame | None,
) -> None:
    if price_df is not None and "Close" in price_df.columns:
        pdf = price_df.copy()
        if "Date" not in pdf.columns:
            pdf = pdf.reset_index()
        pdf["Date"] = pd.to_datetime(pdf["Date"])
        ax.plot(pdf["Date"], pdf["Close"], color=cfg["price_color"], lw=1.0, label="Close", zorder=2)

    cloud = spec.get("cloud")
    if cloud and all(c in ind_df.columns for c in cloud):
        a, b = cloud
        ax.fill_between(
            ind_df["Date"],
            ind_df[a],
            ind_df[b],
            where=ind_df[a] >= ind_df[b],
            color="#2ca02c",
            alpha=0.2,
            label="cloud+",
        )
        ax.fill_between(
            ind_df["Date"],
            ind_df[a],
            ind_df[b],
            where=ind_df[a] < ind_df[b],
            color="#d62728",
            alpha=0.2,
            label="cloud-",
        )

    band = spec.get("band")
    if band and all(c in ind_df.columns for c in band):
        lo, hi = band
        ax.fill_between(ind_df["Date"], ind_df[lo], ind_df[hi], color="#4a90d9", alpha=0.15, label="band")
        ax.plot(ind_df["Date"], ind_df[lo], lw=0.9, color="#4a90d9", alpha=0.8)
        ax.plot(ind_df["Date"], ind_df[hi], lw=0.9, color="#4a90d9", alpha=0.8)

    for col in _valueColumns(ind_df, spec):
        ax.plot(ind_df["Date"], ind_df[col], lw=1.2, label=col, zorder=3)

    ax.legend(loc="upper left", fontsize=cfg["label_size"])
    _applyTheme(ax)


def _plotIndicator(df, plot_name, **plot_kwargs):
    """Backward-compatible wrapper → plotIndicator."""
    from HyperTA.Plots.indicators import plotIndicator

    return plotIndicator(
        df,
        title=plot_name,
        show=plot_kwargs.pop("show", True),
        output=plot_kwargs.pop("output", plot_kwargs.pop("out", None)),
        kind=plot_kwargs.pop("kind", None),
        price_df=plot_kwargs.pop("price_df", None),
        **{k: v for k, v in plot_kwargs.items() if k in {"theme", "dpi", "with_price"}},
    )


# =============================================================================
# ## __________ signals.py threshold-rule helpers (rule=) __________
# =============================================================================

def _coerceSignalDates(signals) -> pd.DatetimeIndex:
    """Normalize list / Date-Price frame / (above, below) tuple into dates."""
    if signals is None:
        return pd.DatetimeIndex([])
    if isinstance(signals, tuple):
        chunks = [_normalizeSignalDates(part) for part in signals if part is not None]
        if not chunks:
            return pd.DatetimeIndex([])
        return pd.DatetimeIndex(pd.Series(pd.concat([pd.Series(c) for c in chunks])).unique()).sort_values()
    return _normalizeSignalDates(signals)


def _prepareSigmaBands(
    df: pd.DataFrame,
    *,
    ema_period: int = 10,
    window: int = 50,
    sigma: float = 0.8,
) -> pd.DataFrame:
    """EMA ± σ bands for stdvBandsThreshold visualization."""
    out = df.copy()
    if "Date" not in out.columns:
        out = out.reset_index()
    out["Date"] = pd.to_datetime(out["Date"])
    out["ema"] = out["Close"].ewm(span=ema_period, adjust=False).mean()
    dist = out["Close"] - out["ema"]
    rolling_std = dist.rolling(window=window).std()
    out["upper_band"] = out["ema"] + sigma * rolling_std
    out["lower_band"] = out["ema"] - sigma * rolling_std
    return out[["Date", "ema", "upper_band", "lower_band"]].dropna()


def _drawThresholdRule(
    ax_price,
    ax_ind,
    *,
    rule: str,
    thr: float | None = None,
    band: tuple[float, float] | None = None,
    sigma_df: pd.DataFrame | None = None,
    prefer_indicator: bool = True,
) -> None:
    """
    Draw threshold geometry.

    rule:
      - "level"  → horizontal thr (on indicator ax if present, else price)
      - "band"   → shaded [lo, hi] zone
      - "sigma"  → EMA ± σ bands on price
    """
    rule = (rule or "level").lower()
    target = ax_ind if (prefer_indicator and ax_ind is not None) else ax_price
    if target is None:
        target = ax_price

    if rule == "level" and thr is not None:
        target.axhline(float(thr), color="#2ca02c", lw=1.3, ls="--", label=f"thr={thr:g}", zorder=3)

    elif rule == "band" and band is not None:
        lo, hi = float(band[0]), float(band[1])
        target.axhspan(lo, hi, color="#2ca02c", alpha=0.15, label=f"band[{lo:g},{hi:g}]", zorder=1)
        target.axhline(lo, color="#2ca02c", lw=0.9, ls="--", alpha=0.8)
        target.axhline(hi, color="#2ca02c", lw=0.9, ls="--", alpha=0.8)

    elif rule == "sigma" and sigma_df is not None and not sigma_df.empty:
        ax_price.plot(sigma_df["Date"], sigma_df["ema"], color="#1f77b4", lw=1.2, label="EMA", zorder=3)
        ax_price.plot(sigma_df["Date"], sigma_df["upper_band"], color="#d62728", lw=1.0, ls=":", label="+σ", zorder=3)
        ax_price.plot(sigma_df["Date"], sigma_df["lower_band"], color="#2ca02c", lw=1.0, ls=":", label="-σ", zorder=3)
        ax_price.fill_between(
            sigma_df["Date"],
            sigma_df["lower_band"],
            sigma_df["upper_band"],
            color="#4a90d9",
            alpha=0.12,
            zorder=1,
        )

    # refresh legends after rule artists
    ax_price.legend(loc="upper left", fontsize=8)
    if ax_ind is not None:
        ax_ind.legend(loc="upper left", fontsize=8)


# =============================================================================
# ## __________ metrics.py helpers __________
# =============================================================================

# layout: "distribution" | "entropy" | "derivative" | "summary"
_METRIC_SPECS: dict[str, dict] = {
    "distribution": {"layout": "distribution"},
    "hist": {"layout": "distribution"},
    "returns": {"layout": "distribution"},
    "entropy": {
        "layout": "panel",
        "columns": ["entropy", "stdv"],
        "hlines": (),
    },
    "rolling_entropy": {
        "layout": "panel",
        "columns": ["entropy", "stdv"],
    },
    "derivative": {
        "layout": "derivative",
        "columns": ["First_Derivative", "Second_Derivative"],
        "hlines": (0,),
    },
    "derivatives": {
        "layout": "derivative",
        "columns": ["First_Derivative", "Second_Derivative"],
        "hlines": (0,),
    },
    "summary": {"layout": "summary"},
    "stats": {"layout": "summary"},
}

_METRIC_COLUMN_HINTS: list[tuple[frozenset[str], str]] = [
    (frozenset({"entropy", "stdv"}), "entropy"),
    (frozenset({"First_Derivative", "Second_Derivative"}), "derivative"),
    (frozenset({"First_Derivative"}), "derivative"),
    (frozenset({"Second_Derivative"}), "derivative"),
]


def _detectMetricKind(data) -> str:
    if isinstance(data, dict):
        return "summary"
    if not isinstance(data, pd.DataFrame):
        return "distribution"
    cols = {c for c in data.columns if c != "Date"}
    for needed, kind in _METRIC_COLUMN_HINTS:
        if needed.issubset(cols):
            return kind
    # raw OHLCV / price → distribution
    if "Close" in data.columns or "close" in data.columns:
        return "distribution"
    return "distribution"


def _normalizeMetricDf(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    if "Date" not in out.columns:
        out = out.reset_index()
        if "Date" not in out.columns:
            for candidate in ("Date", "date", "Datetime", "datetime"):
                if candidate in out.columns:
                    out = out.rename(columns={candidate: "Date"})
                    break
    if "Date" in out.columns:
        out["Date"] = pd.to_datetime(out["Date"])
        out = out.sort_values("Date")
    return out


def _returnsSeries(df: pd.DataFrame, column: str = "Close") -> pd.Series:
    if column not in df.columns:
        for candidate in ("Close", "close", "Adj Close", "Price"):
            if candidate in df.columns:
                column = candidate
                break
    if column not in df.columns:
        raise ValueError(f"No price column found (expected '{column}')")
    px = pd.to_numeric(df[column], errors="coerce").dropna()
    return np.log(px / px.shift(1)).dropna()


def _drawDistribution(ax, df: pd.DataFrame, cfg: dict, *, column: str = "Close", bins: int = 40) -> dict:
    """Histogram of log-returns + normal overlay; returns summary stats."""
    rets = _returnsSeries(df, column=column)
    mu, sigma = float(rets.mean()), float(rets.std())
    skew = float(rets.skew())
    kurt = float(rets.kurt())  # excess kurtosis (pandas)

    ax.hist(rets, bins=bins, density=True, color="#4a4a4a", alpha=0.75, edgecolor="white", label="returns")
    if sigma > 0 and len(rets) > 2:
        xs = np.linspace(rets.min(), rets.max(), 200)
        pdf = (1.0 / (sigma * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((xs - mu) / sigma) ** 2)
        ax.plot(xs, pdf, color="#d62728", lw=1.4, label="normal")
    ax.axvline(mu, color="#1f77b4", lw=1.0, ls="--", label=f"mean={mu:.4g}")
    ax.set_xlabel("log-return", fontsize=cfg["label_size"])
    ax.set_ylabel("density", fontsize=cfg["label_size"])
    ax.legend(loc="upper left", fontsize=cfg["label_size"])
    _applyTheme(ax)

    stats = {
        "mean": mu,
        "std": sigma,
        "skew": skew,
        "kurtosis": kurt,
        "n": int(len(rets)),
    }
    box = "\n".join(
        [
            f"n={stats['n']}",
            f"mean={mu:.4g}",
            f"std={sigma:.4g}",
            f"skew={skew:.4g}",
            f"kurt={kurt:.4g}",
        ]
    )
    ax.text(
        0.98,
        0.98,
        box,
        transform=ax.transAxes,
        va="top",
        ha="right",
        fontsize=8,
        family="monospace",
        bbox={"boxstyle": "round,pad=0.4", "facecolor": "#fafafa", "edgecolor": "#bbbbbb", "alpha": 0.95},
    )
    return stats


def _drawMetricPanel(ax, met_df: pd.DataFrame, spec: dict, cfg: dict) -> None:
    cols = [c for c in (spec.get("columns") or []) if c in met_df.columns]
    if not cols:
        cols = [c for c in met_df.columns if c != "Date"]
    for col in cols:
        ax.plot(met_df["Date"], met_df[col], lw=1.2, label=col)
    for y in spec.get("hlines") or ():
        ax.axhline(y, color="#aaaaaa", lw=0.8, ls="--", alpha=0.8)
    ax.legend(loc="upper left", fontsize=cfg["label_size"])
    _applyTheme(ax)


def _drawDerivatives(
    fig_axes,
    met_df: pd.DataFrame,
    cfg: dict,
    price_df: pd.DataFrame | None,
) -> None:
    """fig_axes is a list of axes from top to bottom."""
    axes = list(fig_axes)
    idx = 0
    if price_df is not None and "Close" in price_df.columns:
        pdf = _normalizeMetricDf(price_df)
        axes[idx].plot(pdf["Date"], pdf["Close"], color=cfg["price_color"], lw=1.0, label="Close")
        axes[idx].set_ylabel("Price", fontsize=cfg["label_size"])
        axes[idx].legend(loc="upper left", fontsize=cfg["label_size"])
        _applyTheme(axes[idx])
        idx += 1

    for col, color in (
        ("First_Derivative", "#ff7f0e"),
        ("Second_Derivative", "#1f77b4"),
    ):
        if col not in met_df.columns or idx >= len(axes):
            continue
        axes[idx].plot(met_df["Date"], met_df[col], lw=1.1, color=color, label=col)
        axes[idx].axhline(0, color="#aaaaaa", lw=0.8, ls="--")
        axes[idx].set_ylabel(col.replace("_", " "), fontsize=cfg["label_size"])
        axes[idx].legend(loc="upper left", fontsize=cfg["label_size"])
        _applyTheme(axes[idx])
        idx += 1


def _drawSummary(ax_left, ax_right, data: dict, df: pd.DataFrame | None, cfg: dict, *, column: str = "Close") -> None:
    """Left: return distribution (if df). Right: metric bars from calculateMetrics dict."""
    if df is not None:
        _drawDistribution(ax_left, df, cfg, column=column)
        ax_left.set_title("Return distribution", fontsize=cfg["label_size"])
    else:
        ax_left.axis("off")
        ax_left.text(0.5, 0.5, "pass price_df=... for distribution", ha="center", va="center")

    keys = ["variance", "std_dev", "skewness", "kurtosis"]
    vals = [float(data[k]) for k in keys if k in data]
    labels = [k for k in keys if k in data]
    if not labels:
        # plot whatever numeric entries exist
        labels = [k for k, v in data.items() if isinstance(v, (int, float, np.floating))]
        vals = [float(data[k]) for k in labels]

    colors = ["#4a4a4a"] * len(vals)
    ax_right.barh(range(len(labels)), vals, color=colors, height=0.55)
    ax_right.set_yticks(range(len(labels)))
    ax_right.set_yticklabels(labels, fontsize=cfg["label_size"])
    ax_right.set_xlabel("value", fontsize=cfg["label_size"])
    ax_right.set_title("Summary metrics", fontsize=cfg["label_size"])
    _applyTheme(ax_right)


# =============================================================================
# ## __________ structures.py helpers __________
# =============================================================================

_STRUCTURE_KINDS = ("swings", "fib", "sr", "trendlines", "candles", "chart", "divergence", "hhll", "range", "channel", "trend", "gaps", "wyckoff")


def _detectStructureKind(structure: pd.DataFrame) -> str:
    """Infer structure type from calculate* output columns."""
    if structure is None or structure.empty:
        raise ValueError("structure DataFrame is empty")
    cols = {c.lower() for c in structure.columns}
    if "upper_intercept" in cols and "lower_intercept" in cols:
        return "channel"
    if "direction" in cols and "move_pct" in cols and "start_price" in cols:
        return "trend"
    if "top" in cols and "bottom" in cols and "width_pct" in cols:
        return "range"
    if "slope" in cols and "intercept" in cols:
        return "trendlines"
    if "level" in cols and "price" in cols:
        return "fib"
    if "touches" in cols and "price" in cols:
        return "sr"
    if "pattern" in cols and "bias" in cols:
        if "family" in structure.columns:
            fam = str(structure["family"].iloc[0]).lower()
            return "chart" if fam == "chart" else "candles"
        return "candles"
    if "gap_top" in cols and "gap_bottom" in cols:
        return "gaps"
    if "phase" in cols and "event" in cols and "range_top" in cols:
        return "wyckoff"
    if "ind_start" in cols and "ind_end" in cols:
        return "divergence"
    if "trend" in cols and "structure" in cols:
        return "hhll"
    if "price" in cols and ("kind" in cols or "structure" in cols):
        return "swings"
    raise ValueError(
        "Cannot detect structure kind from columns "
        f"{list(structure.columns)}. Pass kind= one of {_STRUCTURE_KINDS}."
    )


def _resolveStructureBundles(
    structure: pd.DataFrame | None,
    *,
    kind: str | None,
    swings,
    fib,
    sr,
    trendlines,
    candles=None,
    divergence=None,
    hhll=None,
    ranges=None,
    channel=None,
    trend=None,
    chart=None,
    gaps=None,
    wyckoff=None,
) -> dict[str, pd.DataFrame]:
    """Collect named structure frames; optionally classify a single ``structure``."""
    bundles: dict[str, pd.DataFrame] = {}
    if swings is not None and not getattr(swings, "empty", False):
        bundles["swings"] = swings
    if fib is not None and not getattr(fib, "empty", False):
        bundles["fib"] = fib
    if sr is not None and not getattr(sr, "empty", False):
        bundles["sr"] = sr
    if trendlines is not None and not getattr(trendlines, "empty", False):
        bundles["trendlines"] = trendlines
    if candles is not None and not getattr(candles, "empty", False):
        bundles["candles"] = candles
    if divergence is not None and not getattr(divergence, "empty", False):
        bundles["divergence"] = divergence
    if hhll is not None and not getattr(hhll, "empty", False):
        bundles["hhll"] = hhll
    if ranges is not None and not getattr(ranges, "empty", False):
        bundles["range"] = ranges
    if channel is not None and not getattr(channel, "empty", False):
        bundles["channel"] = channel
    if trend is not None and not getattr(trend, "empty", False):
        bundles["trend"] = trend
    if chart is not None and not getattr(chart, "empty", False):
        bundles["chart"] = chart
    if gaps is not None and not getattr(gaps, "empty", False):
        bundles["gaps"] = gaps
    if wyckoff is not None and not getattr(wyckoff, "empty", False):
        bundles["wyckoff"] = wyckoff

    if structure is not None and not getattr(structure, "empty", False):
        key = (kind or _detectStructureKind(structure)).lower()
        if key not in _STRUCTURE_KINDS:
            raise ValueError(f"Unknown kind={kind!r}. Expected one of {_STRUCTURE_KINDS}")
        bundles[key] = structure

    if not bundles:
        if structure is not None and getattr(structure, "empty", False):
            raise ValueError("structure DataFrame is empty — nothing to plot")
        raise ValueError(
            "Pass structure=... (+ candles/chart/gaps/wyckoff/trend/ranges/channel/…)"
        )
    return bundles


def _drawStructureSwings(ax, swings: pd.DataFrame, *, cfg: dict) -> None:
    work = swings.copy()
    work["Date"] = pd.to_datetime(work["Date"])
    highs = work[work["kind"].astype(str).str.lower() == "high"]
    lows = work[work["kind"].astype(str).str.lower() == "low"]
    if not highs.empty:
        ax.scatter(
            highs["Date"],
            highs["Price"],
            marker="v",
            s=55,
            c="#e74c3c",
            zorder=6,
            label="Swing high",
            edgecolors="white",
            linewidths=0.4,
        )
    if not lows.empty:
        ax.scatter(
            lows["Date"],
            lows["Price"],
            marker="^",
            s=55,
            c="#27ae60",
            zorder=6,
            label="Swing low",
            edgecolors="white",
            linewidths=0.4,
        )
    # optional HH/HL labels on a subset to avoid clutter
    if "structure" in work.columns and len(work) <= 40:
        for _, row in work.iterrows():
            ax.annotate(
                str(row["structure"]),
                (row["Date"], row["Price"]),
                textcoords="offset points",
                xytext=(0, 8 if row["kind"] == "high" else -12),
                ha="center",
                fontsize=7,
                color="#555555",
            )



def _structureFocusWindow(
    data: pd.DataFrame,
    bundles: dict[str, pd.DataFrame],
    *,
    date_col: str,
    price_col: str,
    pad_frac: float = 0.2,
) -> tuple[pd.Timestamp, pd.Timestamp, float, float]:
    """
    Zoom to the structure's active window so overlays aren't stuck on the
    far-right of a multi-year chart. Falls back to full series for swings/SR-only.
    """
    dates = pd.to_datetime(data[date_col])
    full_x0, full_x1 = dates.iloc[0], dates.iloc[-1]

    starts: list[pd.Timestamp] = []
    ends: list[pd.Timestamp] = []

    if "fib" in bundles and not bundles["fib"].empty:
        fib = bundles["fib"]
        if "start_date" in fib.columns and pd.notna(fib["start_date"].iloc[0]):
            s = pd.Timestamp(fib["start_date"].iloc[0])
            e = (
                pd.Timestamp(fib["end_date"].iloc[0])
                if "end_date" in fib.columns and pd.notna(fib["end_date"].iloc[0])
                else full_x1
            )
            starts.append(min(s, e))
            ends.append(full_x1)

    if "trendlines" in bundles and not bundles["trendlines"].empty:
        tls = bundles["trendlines"]
        starts.append(pd.Timestamp(tls["start_date"].min()))
        ends.append(full_x1)

    if "divergence" in bundles and not bundles["divergence"].empty:
        div = bundles["divergence"]
        starts.append(pd.Timestamp(div["start_date"].min()))
        ends.append(pd.Timestamp(div["end_date"].max()))

    if "range" in bundles and not bundles["range"].empty:
        rg = bundles["range"]
        starts.append(pd.Timestamp(rg["start_date"].min()))
        ends.append(pd.Timestamp(rg["end_date"].max()))

    if "channel" in bundles and not bundles["channel"].empty:
        ch = bundles["channel"]
        starts.append(pd.Timestamp(ch["start_date"].min()))
        ends.append(pd.Timestamp(ch["end_date"].max()))

    if "trend" in bundles and not bundles["trend"].empty:
        tr = bundles["trend"]
        starts.append(pd.Timestamp(tr["start_date"].min()))
        ends.append(pd.Timestamp(tr["end_date"].max()))

    if "gaps" in bundles and not bundles["gaps"].empty:
        gp = bundles["gaps"]
        starts.append(pd.Timestamp(gp["Date"].min()))
        ends.append(pd.Timestamp(gp["Date"].max()))

    if "wyckoff" in bundles and not bundles["wyckoff"].empty:
        wk = bundles["wyckoff"]
        starts.append(pd.Timestamp(wk["range_start"].min()))
        ends.append(pd.Timestamp(wk["Date"].max()))

    if "chart" in bundles and not bundles["chart"].empty and not starts:
        cd = bundles["chart"]
        last = pd.Timestamp(cd["Date"].max())
        starts.append(max(full_x0, last - pd.Timedelta(days=180)))
        ends.append(full_x1)

    if "candles" in bundles and not bundles["candles"].empty and not starts:
        # candles alone → recent window around last hits
        cd = bundles["candles"]
        last = pd.Timestamp(cd["Date"].max())
        first = pd.Timestamp(cd["Date"].min())
        starts.append(max(full_x0, last - (last - first) * 0.35 if last > first else last - pd.Timedelta(days=90)))
        ends.append(full_x1)

    if starts:
        x0 = min(starts)
        x1 = max(ends)
        span = x1 - x0
        if span <= pd.Timedelta(0):
            span = pd.Timedelta(days=30)
        x0 = max(full_x0, x0 - span * pad_frac)
        x1 = min(full_x1, x1 + span * 0.02)
    else:
        x0, x1 = full_x0, full_x1

    mask = (dates >= x0) & (dates <= x1)
    window = data.loc[mask]
    if window.empty:
        window = data

    if "High" in window.columns and "Low" in window.columns:
        y_min = float(np.nanmin(window["Low"].to_numpy(dtype=float)))
        y_max = float(np.nanmax(window["High"].to_numpy(dtype=float)))
    else:
        y_min = float(np.nanmin(window[price_col].to_numpy(dtype=float)))
        y_max = float(np.nanmax(window[price_col].to_numpy(dtype=float)))

    if "fib" in bundles and not bundles["fib"].empty:
        fib = bundles["fib"]
        y_min = min(y_min, float(fib["swing_low"].iloc[0]))
        y_max = max(y_max, float(fib["swing_high"].iloc[0]))

    pad = 0.06 * (y_max - y_min or 1.0)
    return x0, x1, y_min - pad, y_max + pad


def _drawStructureFib(ax, fib: pd.DataFrame, *, x0, x1, y_lo, y_hi, cfg: dict) -> None:
    if fib.empty:
        return
    start = fib["start_date"].iloc[0] if "start_date" in fib.columns else None
    end = fib["end_date"].iloc[0] if "end_date" in fib.columns else None
    x_left = pd.Timestamp(start) if pd.notna(start) else pd.Timestamp(x0)
    x_right = pd.Timestamp(x1)

    lo = float(fib["swing_low"].iloc[0])
    hi = float(fib["swing_high"].iloc[0])
    if pd.notna(start) and pd.notna(end):
        direction = str(fib["direction"].iloc[0])
        if direction == "up":
            ax.scatter([start], [lo], marker="^", s=70, c="#27ae60", zorder=7, label="Fib low")
            ax.scatter([end], [hi], marker="v", s=70, c="#e74c3c", zorder=7, label="Fib high")
        else:
            ax.scatter([start], [hi], marker="v", s=70, c="#e74c3c", zorder=7, label="Fib high")
            ax.scatter([end], [lo], marker="^", s=70, c="#27ae60", zorder=7, label="Fib low")

    emphasize = {0.382, 0.5, 0.618, 0.786}
    for _, row in fib.iterrows():
        level = float(row["level"])
        price = float(row["price"])
        if price < y_lo or price > y_hi:
            continue
        strong = level in emphasize or level in {0.0, 1.0}
        color = "#c0392b" if strong else "#e67e22"
        lw = 1.35 if strong else 0.75
        ax.hlines(
            price,
            x_left,
            x_right,
            colors=color,
            linestyles="--",
            linewidths=lw,
            alpha=0.9 if strong else 0.55,
            zorder=3,
        )
        ax.annotate(
            f"{level:.3f}",
            xy=(x_right, price),
            xytext=(-4, 0),
            textcoords="offset points",
            va="center",
            ha="right",
            fontsize=7,
            color=color,
            bbox=dict(boxstyle="round,pad=0.12", fc="white", ec="none", alpha=0.8),
            zorder=5,
            clip_on=True,
        )


def _drawStructureSR(ax, sr: pd.DataFrame, *, x0, x1, y_lo, y_hi, cfg: dict) -> None:
    if sr.empty:
        return
    color_map = {
        "support": "#27ae60",
        "resistance": "#e74c3c",
        "both": "#8e44ad",
    }
    seen = set()
    work = sr.sort_values("touches", ascending=True)
    max_touches = max(int(work["touches"].max()), 1)
    x_left, x_right = pd.Timestamp(x0), pd.Timestamp(x1)
    for _, row in work.iterrows():
        kind = str(row.get("kind", "both")).lower()
        color = color_map.get(kind, "#7f8c8d")
        price = float(row["price"])
        if price < y_lo or price > y_hi:
            continue
        touches = int(row.get("touches", 0))
        alpha = 0.35 + 0.55 * (touches / max_touches)
        ax.hlines(
            price,
            x_left,
            x_right,
            colors=color,
            linestyles="-",
            linewidths=1.0 + 0.2 * max(touches - 2, 0),
            alpha=min(alpha, 0.95),
            zorder=3,
            label=kind.capitalize() if kind not in seen else None,
        )
        seen.add(kind)
        ax.annotate(
            f"{kind[:3].upper()} {touches}",
            xy=(x_right, price),
            xytext=(-4, 0),
            textcoords="offset points",
            va="center",
            ha="right",
            fontsize=7,
            color=color,
            bbox=dict(boxstyle="round,pad=0.12", fc="white", ec="none", alpha=0.8),
            zorder=5,
            clip_on=True,
        )


def _drawStructureTrendlines(
    ax,
    tls: pd.DataFrame,
    price_df: pd.DataFrame,
    *,
    date_col: str,
    y_lo: float,
    y_hi: float,
    cfg: dict,
) -> None:
    """Draw trendline from first pivot → view end, clipped to y window."""
    if tls.empty:
        return
    dates = pd.to_datetime(price_df[date_col]).reset_index(drop=True)
    n = len(dates)
    if n == 0:
        return

    def _date_index(ts) -> int:
        ts = pd.Timestamp(ts)
        delta = (dates - ts).abs()
        return int(delta.idxmin())

    color_map = {"support": "#27ae60", "resistance": "#e74c3c"}
    seen = set()
    for _, row in tls.iterrows():
        kind = str(row.get("kind", "support")).lower()
        color = color_map.get(kind, "#7f8c8d")
        slope = float(row["slope"])
        intercept = float(row["intercept"])

        if "start_index" in row and pd.notna(row["start_index"]):
            i0 = int(row["start_index"])
            i1 = int(row["end_index"])
        else:
            i0 = _date_index(row["start_date"])
            i1 = max(_date_index(row["end_date"]), i0 + 1)
        i0 = max(0, min(i0, n - 1))
        i1 = max(0, min(i1, n - 1))

        i_end = i1
        for i in range(i1, n):
            y = slope * i + intercept
            if y < y_lo or y > y_hi:
                break
            i_end = i

        xs_i = np.array([i0, i1, i_end], dtype=float)
        ys = slope * xs_i + intercept
        xs = [dates.iloc[i0], dates.iloc[i1], dates.iloc[i_end]]
        ax.plot(
            xs,
            ys,
            color=color,
            lw=1.8,
            ls="-.",
            alpha=0.95,
            zorder=4,
            label=f"TL {kind}" if kind not in seen else None,
        )
        ax.scatter(
            [dates.iloc[i0], dates.iloc[i1]],
            [ys[0], ys[1]],
            s=28,
            c=color,
            zorder=5,
            edgecolors="white",
            linewidths=0.4,
        )
        seen.add(kind)





def _drawStructureRange(ax, ranges: pd.DataFrame, *, cfg: dict) -> None:
    if ranges is None or ranges.empty:
        return
    labeled = False
    for _, row in ranges.iterrows():
        x0 = pd.Timestamp(row["start_date"])
        x1 = pd.Timestamp(row["end_date"])
        top = float(row["top"])
        bottom = float(row["bottom"])
        ax.fill_between(
            [x0, x1],
            [bottom, bottom],
            [top, top],
            color="#3498db",
            alpha=0.15,
            zorder=1,
            label="Range" if not labeled else None,
        )
        labeled = True
        ax.hlines([top, bottom], x0, x1, colors="#2980b9", linestyles="-", linewidths=1.2, zorder=3)
        ax.hlines([float(row["mid"])], x0, x1, colors="#2980b9", linestyles=":", linewidths=0.8, alpha=0.7, zorder=3)



def _drawStructureTrend(ax, trend: pd.DataFrame, *, cfg: dict) -> None:
    """Draw ZigZag up/down legs as thick colored segments."""
    if trend is None or trend.empty:
        return
    color_map = {"up": "#27ae60", "down": "#e74c3c"}
    # line width scales mildly with average leg size (bigger trends → thicker)
    avg_bars = float(trend["n_bars"].mean()) if "n_bars" in trend.columns else 20.0
    lw = float(np.clip(1.2 + np.log1p(avg_bars) * 0.35, 1.5, 4.0))
    seen = set()
    for _, row in trend.iterrows():
        direction = str(row.get("direction", "")).lower()
        color = color_map.get(direction, "#7f8c8d")
        label = f"Trend {direction}" if direction not in seen else None
        seen.add(direction)
        ax.plot(
            [row["start_date"], row["end_date"]],
            [row["start_price"], row["end_price"]],
            color=color,
            lw=lw,
            solid_capstyle="round",
            alpha=0.95,
            zorder=5,
            label=label,
        )
        ax.scatter(
            [row["start_date"], row["end_date"]],
            [row["start_price"], row["end_price"]],
            s=28,
            c=color,
            zorder=6,
            edgecolors="white",
            linewidths=0.4,
        )


def _drawStructureChannel(ax, channels: pd.DataFrame, *, cfg: dict) -> None:
    if channels is None or channels.empty:
        return
    color_map = {"up": "#27ae60", "down": "#e74c3c", "flat": "#8e44ad"}
    seen = set()
    for _, row in channels.iterrows():
        kind = str(row.get("kind", "flat")).lower()
        color = color_map.get(kind, "#7f8c8d")
        x0 = pd.Timestamp(row["start_date"])
        x1 = pd.Timestamp(row["end_date"])
        label = f"Channel {kind}" if kind not in seen else None
        seen.add(kind)
        ax.plot(
            [x0, x1],
            [row["upper_start"], row["upper_end"]],
            color=color,
            lw=1.5,
            ls="-",
            zorder=4,
            label=label,
        )
        ax.plot(
            [x0, x1],
            [row["lower_start"], row["lower_end"]],
            color=color,
            lw=1.5,
            ls="-",
            zorder=4,
        )
        ax.fill_between(
            [x0, x1],
            [row["lower_start"], row["lower_end"]],
            [row["upper_start"], row["upper_end"]],
            color=color,
            alpha=0.08,
            zorder=1,
        )

def _drawStructureHhLl(ax, hhll: pd.DataFrame, *, cfg: dict) -> None:
    if hhll is None or hhll.empty:
        return
    work = hhll.copy()
    work["Date"] = pd.to_datetime(work["Date"])

    # connect consecutive swings
    ax.plot(
        work["Date"],
        work["Price"],
        color="#7f8c8d",
        lw=0.9,
        ls=":",
        alpha=0.55,
        zorder=3,
        label="Structure path",
    )

    color_struct = {
        "HH": "#e74c3c",
        "LH": "#e67e22",
        "HL": "#27ae60",
        "LL": "#2980b9",
        "H": "#c0392b",
        "L": "#16a085",
    }
    for label, color in color_struct.items():
        sub = work[work["structure"].astype(str) == label]
        if sub.empty:
            continue
        marker = "v" if label in {"HH", "LH", "H"} else "^"
        ax.scatter(
            sub["Date"],
            sub["Price"],
            marker=marker,
            s=55,
            c=color,
            zorder=6,
            edgecolors="white",
            linewidths=0.4,
            label=label,
        )

    for _, row in work.iterrows():
        ax.annotate(
            str(row["structure"]),
            (row["Date"], row["Price"]),
            textcoords="offset points",
            xytext=(0, 9 if row["kind"] == "high" else -11),
            ha="center",
            fontsize=7,
            color=color_struct.get(str(row["structure"]), "#555555"),
            fontweight="bold",
        )

    # highlight BOS / ChoCH
    events = work[work["event"].notna()] if "event" in work.columns else work.iloc[0:0]
    for _, row in events.iterrows():
        ev = str(row["event"]).lower()
        color = "#8e44ad" if ev == "choch" else "#2c3e50"
        ax.scatter(
            [row["Date"]],
            [row["Price"]],
            s=120,
            facecolors="none",
            edgecolors=color,
            linewidths=1.6,
            zorder=7,
            label=ev.upper() if ev not in getattr(_drawStructureHhLl, "_seen", set()) else None,
        )
        _drawStructureHhLl._seen = getattr(_drawStructureHhLl, "_seen", set()) | {ev}
        ax.annotate(
            ev.upper(),
            (row["Date"], row["Price"]),
            textcoords="offset points",
            xytext=(8, 0),
            ha="left",
            fontsize=7,
            color=color,
            fontweight="bold",
        )


def _drawStructureCandles(ax, candles: pd.DataFrame, *, cfg: dict) -> None:
    if candles is None or candles.empty:
        return
    work = candles.copy()
    work["Date"] = pd.to_datetime(work["Date"])
    fam = "Chart"
    if "family" in work.columns and len(work):
        fam = "Chart" if str(work["family"].iloc[0]).lower() == "chart" else "Candle"
    color_map = {"bullish": "#27ae60", "bearish": "#e74c3c"}
    for bias, marker in (("bullish", "^"), ("bearish", "v")):
        sub = work[work["bias"].astype(str).str.lower() == bias]
        if sub.empty:
            continue
        ax.scatter(
            sub["Date"],
            sub["Price"],
            marker=marker,
            s=48,
            c=color_map[bias],
            zorder=6,
            edgecolors="white",
            linewidths=0.35,
            label=f"{fam} {bias}",
            alpha=0.9,
        )
    # annotate a light subset to avoid clutter
    if len(work) <= 25:
        for _, row in work.iterrows():
            ax.annotate(
                str(row["pattern"]),
                (row["Date"], row["Price"]),
                textcoords="offset points",
                xytext=(0, 10 if row["bias"] == "bullish" else -12),
                ha="center",
                fontsize=6,
                color=color_map.get(str(row["bias"]).lower(), "#555555"),
            )



def _drawStructureChartPatterns(ax, chart: pd.DataFrame, *, cfg: dict) -> None:
    """Markers for classic chart patterns (reuse candle-style markers)."""
    _drawStructureCandles(ax, chart, cfg=cfg)


def _drawStructureGaps(ax, gaps: pd.DataFrame, *, cfg: dict) -> None:
    if gaps is None or gaps.empty:
        return
    color_map = {"up": "#27ae60", "down": "#e74c3c"}
    seen = set()
    for _, row in gaps.iterrows():
        direction = str(row["direction"]).lower()
        color = color_map.get(direction, "#7f8c8d")
        x = pd.Timestamp(row["Date"])
        top, bottom = float(row["gap_top"]), float(row["gap_bottom"])
        label = f"Gap {direction}" if direction not in seen else None
        seen.add(direction)
        ax.vlines(x, bottom, top, colors=color, linewidths=2.2, alpha=0.85, zorder=4, label=label)
        ax.scatter([x], [(top + bottom) / 2], s=20, c=color, zorder=5)
        if bool(row.get("filled", False)) and pd.notna(row.get("fill_date", None)):
            ax.annotate(
                "filled",
                (x, (top + bottom) / 2),
                textcoords="offset points",
                xytext=(6, 0),
                fontsize=6,
                color=color,
                alpha=0.8,
            )


def _drawStructureWyckoff(ax, wk: pd.DataFrame, *, cfg: dict) -> None:
    if wk is None or wk.empty:
        return
    # draw unique ranges as boxes
    seen_ranges = set()
    for _, row in wk.iterrows():
        key = (str(row["range_start"]), str(row["range_end"]), float(row["range_top"]))
        if key in seen_ranges:
            continue
        seen_ranges.add(key)
        x0, x1 = pd.Timestamp(row["range_start"]), pd.Timestamp(row["range_end"])
        top, bottom = float(row["range_top"]), float(row["range_bottom"])
        ax.fill_between(
            [x0, x1], [bottom, bottom], [top, top],
            color="#9b59b6", alpha=0.12, zorder=1,
            label="Wyckoff range" if len(seen_ranges) == 1 else None,
        )
        ax.hlines([top, bottom], x0, x1, colors="#8e44ad", linewidths=1.0, zorder=3)

    color_map = {
        "spring": "#27ae60",
        "upthrust": "#e74c3c",
        "sos": "#2ecc71",
        "sow": "#c0392b",
        "range": "#8e44ad",
    }
    seen_ev = set()
    for _, row in wk.iterrows():
        ev = str(row["event"]).lower()
        color = color_map.get(ev, "#7f8c8d")
        label = ev.upper() if ev not in seen_ev else None
        seen_ev.add(ev)
        ax.scatter(
            [row["Date"]], [row["Price"]],
            s=70, c=color, marker="D", zorder=6,
            edgecolors="white", linewidths=0.4, label=label,
        )
        ax.annotate(
            f"{ev}\n{row['phase']}",
            (row["Date"], row["Price"]),
            textcoords="offset points",
            xytext=(0, 10),
            ha="center",
            fontsize=6,
            color=color,
        )


def _drawStructureDivergence(ax, divs: pd.DataFrame, *, cfg: dict) -> None:
    if divs is None or divs.empty:
        return
    color_map = {"bullish": "#27ae60", "bearish": "#e74c3c"}
    seen = set()
    for _, row in divs.iterrows():
        bias = str(row.get("bias", "")).lower()
        color = color_map.get(bias, "#7f8c8d")
        mode = str(row.get("mode", "regular"))
        ls = "-" if mode == "regular" else ":"
        label = f"{bias} {mode}" if f"{bias}-{mode}" not in seen else None
        seen.add(f"{bias}-{mode}")
        ax.plot(
            [row["start_date"], row["end_date"]],
            [row["price_start"], row["price_end"]],
            color=color,
            lw=1.6,
            ls=ls,
            alpha=0.9,
            zorder=5,
            label=label,
        )
        ax.scatter(
            [row["start_date"], row["end_date"]],
            [row["price_start"], row["price_end"]],
            s=32,
            c=color,
            zorder=6,
            edgecolors="white",
            linewidths=0.4,
        )


def _buildStructureChart(
    df: pd.DataFrame,
    bundles: dict[str, pd.DataFrame],
    *,
    price_col: str = "Close",
    date_col: str = "Date",
    label: str = "Price",
    theme: str = "hyperta",
    dpi: int | None = None,
    zoom: bool = True,
):
    """Price line + structure overlays. Returns (fig, ax, meta)."""
    data, date_col, price_col = _prepareSeries(df, date_col=date_col, value_col=price_col)
    cfg = _theme(theme)
    dpi = dpi or cfg["dpi"]

    if zoom:
        x0, x1, y_lo, y_hi = _structureFocusWindow(
            data, bundles, date_col=date_col, price_col=price_col
        )
    else:
        x0, x1 = data[date_col].iloc[0], data[date_col].iloc[-1]
        if "High" in data.columns and "Low" in data.columns:
            y_min = float(np.nanmin(data["Low"].to_numpy(dtype=float)))
            y_max = float(np.nanmax(data["High"].to_numpy(dtype=float)))
        else:
            y_min = float(np.nanmin(data[price_col].to_numpy(dtype=float)))
            y_max = float(np.nanmax(data[price_col].to_numpy(dtype=float)))
        pad = 0.04 * (y_max - y_min or 1.0)
        y_lo, y_hi = y_min - pad, y_max + pad

    dates = pd.to_datetime(data[date_col])
    view = data.loc[(dates >= x0) & (dates <= x1)].copy()
    if view.empty:
        view = data

    fig, ax = plt.subplots(figsize=cfg["figsize"], dpi=dpi)
    ax.plot(
        view[date_col],
        view[price_col],
        color=cfg["price_color"],
        lw=1.25,
        label=label,
        zorder=2,
    )

    vx0, vx1 = view[date_col].iloc[0], view[date_col].iloc[-1]
    if "swings" in bundles:
        sw = bundles["swings"]
        if "Date" in sw.columns and not sw.empty:
            sw = sw[
                (pd.to_datetime(sw["Date"]) >= vx0) & (pd.to_datetime(sw["Date"]) <= vx1)
            ]
        _drawStructureSwings(ax, sw, cfg=cfg)
    if "fib" in bundles:
        _drawStructureFib(ax, bundles["fib"], x0=vx0, x1=vx1, y_lo=y_lo, y_hi=y_hi, cfg=cfg)
    if "sr" in bundles:
        _drawStructureSR(ax, bundles["sr"], x0=vx0, x1=vx1, y_lo=y_lo, y_hi=y_hi, cfg=cfg)
    if "trendlines" in bundles:
        _drawStructureTrendlines(
            ax,
            bundles["trendlines"],
            data,
            date_col=date_col,
            y_lo=y_lo,
            y_hi=y_hi,
            cfg=cfg,
        )
    if "range" in bundles:
        rg = bundles["range"]
        if not rg.empty:
            rg = rg[
                (pd.to_datetime(rg["end_date"]) >= vx0)
                & (pd.to_datetime(rg["start_date"]) <= vx1)
            ]
        _drawStructureRange(ax, rg, cfg=cfg)
    if "channel" in bundles:
        ch = bundles["channel"]
        if not ch.empty:
            ch = ch[
                (pd.to_datetime(ch["end_date"]) >= vx0)
                & (pd.to_datetime(ch["start_date"]) <= vx1)
            ]
        _drawStructureChannel(ax, ch, cfg=cfg)
    if "trend" in bundles:
        tr = bundles["trend"]
        if not tr.empty:
            tr = tr[
                (pd.to_datetime(tr["end_date"]) >= vx0)
                & (pd.to_datetime(tr["start_date"]) <= vx1)
            ]
        _drawStructureTrend(ax, tr, cfg=cfg)
    if "hhll" in bundles:
        hh = bundles["hhll"]
        if "Date" in hh.columns and not hh.empty:
            hh = hh[
                (pd.to_datetime(hh["Date"]) >= vx0) & (pd.to_datetime(hh["Date"]) <= vx1)
            ]
        # reset event-legend helper state per chart
        if hasattr(_drawStructureHhLl, "_seen"):
            delattr(_drawStructureHhLl, "_seen")
        _drawStructureHhLl(ax, hh, cfg=cfg)
    if "candles" in bundles:
        cd = bundles["candles"]
        if "Date" in cd.columns and not cd.empty:
            cd = cd[
                (pd.to_datetime(cd["Date"]) >= vx0) & (pd.to_datetime(cd["Date"]) <= vx1)
            ]
        _drawStructureCandles(ax, cd, cfg=cfg)
    if "chart" in bundles:
        cp = bundles["chart"]
        if "Date" in cp.columns and not cp.empty:
            cp = cp[
                (pd.to_datetime(cp["Date"]) >= vx0) & (pd.to_datetime(cp["Date"]) <= vx1)
            ]
        _drawStructureChartPatterns(ax, cp, cfg=cfg)
    if "gaps" in bundles:
        gp = bundles["gaps"]
        if not gp.empty:
            gp = gp[
                (pd.to_datetime(gp["Date"]) >= vx0) & (pd.to_datetime(gp["Date"]) <= vx1)
            ]
        _drawStructureGaps(ax, gp, cfg=cfg)
    if "wyckoff" in bundles:
        wk = bundles["wyckoff"]
        if not wk.empty:
            wk = wk[
                (pd.to_datetime(wk["Date"]) >= vx0)
                & (pd.to_datetime(wk["range_start"]) <= vx1)
            ]
        _drawStructureWyckoff(ax, wk, cfg=cfg)
    if "divergence" in bundles:
        dv = bundles["divergence"]
        if not dv.empty:
            dv = dv[
                (pd.to_datetime(dv["end_date"]) >= vx0)
                & (pd.to_datetime(dv["start_date"]) <= vx1)
            ]
        _drawStructureDivergence(ax, dv, cfg=cfg)

    ax.set_xlim(pd.Timestamp(vx0), pd.Timestamp(vx1))
    ax.set_ylim(y_lo, y_hi)
    ax.margins(x=0.02)
    ax.set_ylabel("Price", fontsize=cfg["label_size"])
    ax.ticklabel_format(axis="y", style="plain", useOffset=False)
    _applyTheme(ax)
    handles, labels_ = ax.get_legend_handles_labels()
    if handles:
        seen = set()
        uniq = []
        for h, lab in zip(handles, labels_):
            if lab in seen:
                continue
            seen.add(lab)
            uniq.append((h, lab))
        ax.legend(*zip(*uniq), loc="upper left", fontsize=8, frameon=False)

    meta = {"cfg": cfg, "dpi": dpi, "kinds": tuple(bundles.keys()), "zoom": zoom}
    return fig, ax, meta
