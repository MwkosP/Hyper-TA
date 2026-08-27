"""Asset price charts — base layer for price-only and combined plots."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path

import mplfinance as mpf

from HyperTA.Plots.utils import (
    _attachCrosshair,
    _ensureShowBackend,
    _prepareOhlc,
    _render,
    _resolveChartType,
    _theme,
)


def plotChart(
    df,
    *,
    chart: str = "doji",
    date_col: str = "Date",
    title: str | None = None,
    label: str = "Price",
    volume: bool = False,
    theme: str = "hyperta",
    output: str | Path | BytesIO | None = None,
    show: bool = True,
    dpi: int | None = None,
) -> Path | BytesIO | None:
    """
    Plot asset price as doji/hollow candles, candles, line, or OHLC bars.

    By default only displays (no file written). Pass ``output=`` to save a PNG.
    When shown in a GUI window, hover draws a dotted crosshair with date/price.
    """
    if show:
        _ensureShowBackend()

    ohlc = _prepareOhlc(df, date_col=date_col)
    mpf_type = _resolveChartType(chart)
    cfg = _theme(theme)
    dpi = dpi or cfg["dpi"]

    has_volume = volume and "Volume" in ohlc.columns
    style = mpf.make_mpf_style(
        base_mpf_style="yahoo",
        facecolor=cfg["facecolor"],
        gridstyle=":",
        gridcolor=cfg["grid_color"],
        y_on_right=False,
    )

    fig, axes = mpf.plot(
        ohlc,
        type=mpf_type,
        style=style,
        title=title or f"{label} — {chart}",
        ylabel="Price",
        volume=has_volume,
        figsize=cfg["figsize"],
        returnfig=True,
        tight_layout=True,
    )
    fig.set_dpi(dpi)

    # price panel is always the first axes from mplfinance
    price_ax = axes[0] if isinstance(axes, (list, tuple)) else axes
    if show:
        _attachCrosshair(price_ax, ohlc=ohlc)

    return _render(fig, output=output, show=show, dpi=dpi, theme=theme)
