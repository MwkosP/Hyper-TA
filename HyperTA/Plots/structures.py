"""Structure overlays on price."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path

import pandas as pd

from HyperTA.Plots.utils import (
    _attachCrosshair,
    _buildStructureChart,
    _ensureShowBackend,
    _prepareOhlc,
    _render,
    _resolveStructureBundles,
)


def plotStructure(
    df: pd.DataFrame,
    structure: pd.DataFrame | None = None,
    *,
    kind: str | None = None,
    swings: pd.DataFrame | None = None,
    fib: pd.DataFrame | None = None,
    sr: pd.DataFrame | None = None,
    trendlines: pd.DataFrame | None = None,
    candles: pd.DataFrame | None = None,
    chart: pd.DataFrame | None = None,
    divergence: pd.DataFrame | None = None,
    hhll: pd.DataFrame | None = None,
    ranges: pd.DataFrame | None = None,
    channel: pd.DataFrame | None = None,
    trend: pd.DataFrame | None = None,
    gaps: pd.DataFrame | None = None,
    wyckoff: pd.DataFrame | None = None,
    title: str | None = None,
    price_col: str = "Close",
    date_col: str = "Date",
    label: str = "Price",
    zoom: bool = True,
    theme: str = "hyperta",
    output: str | Path | BytesIO | None = None,
    show: bool = True,
    dpi: int | None = None,
) -> Path | BytesIO | None:
    """
    Plot price with one or more market-structure overlays.

        plotStructure(df, chart=patterns)
        plotStructure(df, gaps=gp, wyckoff=wk)
    """
    if show:
        _ensureShowBackend()

    bundles = _resolveStructureBundles(
        structure,
        kind=kind,
        swings=swings,
        fib=fib,
        sr=sr,
        trendlines=trendlines,
        candles=candles,
        chart=chart,
        divergence=divergence,
        hhll=hhll,
        ranges=ranges,
        channel=channel,
        trend=trend,
        gaps=gaps,
        wyckoff=wyckoff,
    )

    fig, ax, meta = _buildStructureChart(
        df,
        bundles,
        price_col=price_col,
        date_col=date_col,
        label=label,
        theme=theme,
        dpi=dpi,
        zoom=zoom,
    )

    kinds = "+".join(meta["kinds"])
    fig.suptitle(title or f"Structure — {kinds}", fontsize=meta["cfg"]["title_size"])
    fig.autofmt_xdate(rotation=25)
    fig.tight_layout()

    if show:
        try:
            ohlc = _prepareOhlc(df, date_col=date_col)
            _attachCrosshair(ax, ohlc=ohlc)
        except Exception:
            pass

    return _render(fig, output=output, show=show, dpi=meta["dpi"], theme=theme)
