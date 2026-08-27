"""Indicator charts — public plotIndicator API."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from HyperTA.Plots.utils import (
    _INDICATOR_SPECS,
    _applyTheme,
    _detectKind,
    _drawMacd,
    _drawOverlay,
    _drawPanel,
    _ensureShowBackend,
    _normalizeInd,
    _render,
    _theme,
)


def plotIndicator(
    ind_df: pd.DataFrame,
    *,
    kind: str | None = None,
    price_df: pd.DataFrame | None = None,
    title: str | None = None,
    with_price: bool | None = None,
    theme: str = "hyperta",
    output: str | Path | BytesIO | None = None,
    show: bool = True,
    dpi: int | None = None,
) -> Path | BytesIO | None:
    """
    Templated indicator plot.

    Layouts (auto-detected from columns, or set via ``kind``):
      - panel   — RSI, ATR, StochRSI, Williams, ROC, ADX
      - macd    — MACD + signal + histogram
      - overlay — MA/EMA/BB/Donchian/Ichimoku on price

    Parameters
    ----------
    ind_df : DataFrame
        Output of calculate* (Date + indicator columns).
    kind : str, optional
        Force a registry key (``"rsi"``, ``"macd"``, ``"ichimoku"``, …).
    price_df : DataFrame, optional
        OHLCV used for overlays / stacked price panel.
    with_price : bool, optional
        For panel/macd: stack Close above the indicator when price_df is set.
        Defaults to True for overlay.
    output / show :
        Show by default; save only if ``output=`` is set (no Cache default).
    """
    if show:
        _ensureShowBackend()

    ind_df = _normalizeInd(ind_df)
    kind = (kind or _detectKind(ind_df)).lower()
    spec = dict(_INDICATOR_SPECS.get(kind, {"layout": "panel", "columns": None}))
    layout = spec.get("layout", "panel")
    cfg = _theme(theme)
    dpi = dpi or cfg["dpi"]

    if with_price is None:
        with_price = layout == "overlay"

    needs_price_panel = with_price and price_df is not None and layout in {"panel", "macd"}

    if needs_price_panel:
        fig, (ax_price, ax_ind) = plt.subplots(
            2,
            1,
            sharex=True,
            figsize=(cfg["figsize"][0], cfg["figsize"][1] + 2),
            dpi=dpi,
            gridspec_kw={"height_ratios": [1.4, 1.0]},
        )
        pdf = price_df.copy()
        if "Date" not in pdf.columns:
            pdf = pdf.reset_index()
        pdf["Date"] = pd.to_datetime(pdf["Date"])
        ax_price.plot(pdf["Date"], pdf["Close"], color=cfg["price_color"], lw=1.0, label="Close")
        ax_price.set_ylabel("Price", fontsize=cfg["label_size"])
        ax_price.legend(loc="upper left", fontsize=cfg["label_size"])
        _applyTheme(ax_price)
        draw_ax = ax_ind
    else:
        fig, draw_ax = plt.subplots(figsize=cfg["figsize"], dpi=dpi)

    if layout == "macd":
        _drawMacd(draw_ax, ind_df, spec, cfg)
    elif layout == "overlay":
        _drawOverlay(draw_ax, ind_df, spec, cfg, price_df if with_price else None)
    else:
        _drawPanel(draw_ax, ind_df, spec, cfg)

    draw_ax.set_ylabel(kind, fontsize=cfg["label_size"])
    fig.suptitle(title or kind.upper(), fontsize=cfg["title_size"])
    fig.autofmt_xdate(rotation=25)
    fig.tight_layout()

    return _render(fig, output=output, show=show, dpi=dpi, theme=theme)
