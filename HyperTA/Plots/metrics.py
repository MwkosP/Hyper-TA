"""Metric charts — distribution, entropy, derivatives, summary stats."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from HyperTA.Plots.utils import (
    _METRIC_SPECS,
    _applyTheme,
    _detectMetricKind,
    _drawDerivatives,
    _drawDistribution,
    _drawMetricPanel,
    _drawSummary,
    _ensureShowBackend,
    _normalizeMetricDf,
    _render,
    _theme,
)


def plotMetrics(
    data,
    *,
    kind: str | None = None,
    price_df: pd.DataFrame | None = None,
    column: str = "Close",
    bins: int = 40,
    title: str | None = None,
    with_price: bool | None = None,
    theme: str = "hyperta",
    output: str | Path | BytesIO | None = None,
    show: bool = True,
    dpi: int | None = None,
) -> Path | BytesIO | None:
    """
    Templated metrics plot.

    Layouts (auto-detected, or set via ``kind``):
      - distribution — log-return histogram (+ normal overlay, skew/kurt box)
      - entropy      — rolling entropy / stdv panel (from calculateRollingEntropy)
      - derivative   — first/second derivative panels (from rollingDerivative)
      - summary      — calculateMetrics dict bars + optional return distribution

    Parameters
    ----------
    data : DataFrame | dict
        Metric series, price OHLCV (for distribution), or calculateMetrics dict.
    kind : str, optional
        ``"distribution"``, ``"entropy"``, ``"derivative"``, ``"summary"``.
    price_df : DataFrame, optional
        Price for stacked panels / summary distribution side.
    column : str
        Price column for distribution (default Close).
    bins : int
        Histogram bins for distribution.
    output / show :
        Show by default; save only if ``output=`` is set (no Cache default).
    """
    if show:
        _ensureShowBackend()

    kind = (kind or _detectMetricKind(data)).lower()
    spec = dict(_METRIC_SPECS.get(kind, {"layout": "distribution"}))
    layout = spec.get("layout", "distribution")
    cfg = _theme(theme)
    dpi = dpi or cfg["dpi"]

    if with_price is None:
        with_price = layout in {"panel", "derivative"} and price_df is not None

    # ---- distribution ----
    if layout == "distribution":
        if not isinstance(data, pd.DataFrame):
            raise TypeError("distribution layout expects a price DataFrame")
        fig, ax = plt.subplots(figsize=cfg["figsize"], dpi=dpi)
        _drawDistribution(ax, data, cfg, column=column, bins=bins)
        fig.suptitle(title or "Return distribution", fontsize=cfg["title_size"])
        fig.tight_layout()
        return _render(fig, output=output, show=show, dpi=dpi, theme=theme)

    # ---- summary (dict from calculateMetrics) ----
    if layout == "summary":
        if not isinstance(data, dict):
            raise TypeError("summary layout expects a dict from calculateMetrics")
        fig, (ax_l, ax_r) = plt.subplots(
            1,
            2,
            figsize=(cfg["figsize"][0], cfg["figsize"][1]),
            dpi=dpi,
            gridspec_kw={"width_ratios": [1.4, 1.0]},
        )
        src = price_df if price_df is not None else None
        _drawSummary(ax_l, ax_r, data, src, cfg, column=column)
        fig.suptitle(title or "Metrics summary", fontsize=cfg["title_size"])
        fig.tight_layout()
        return _render(fig, output=output, show=show, dpi=dpi, theme=theme)

    if not isinstance(data, pd.DataFrame):
        raise TypeError(f"{layout} layout expects a metrics DataFrame")

    met_df = _normalizeMetricDf(data)

    # ---- rolling entropy panel ----
    if layout == "panel":
        if with_price and price_df is not None:
            fig, (ax_price, ax_m) = plt.subplots(
                2,
                1,
                sharex=True,
                figsize=(cfg["figsize"][0], cfg["figsize"][1] + 2),
                dpi=dpi,
                gridspec_kw={"height_ratios": [1.3, 1.0]},
            )
            pdf = _normalizeMetricDf(price_df)
            ax_price.plot(pdf["Date"], pdf["Close"], color=cfg["price_color"], lw=1.0, label="Close")
            ax_price.set_ylabel("Price", fontsize=cfg["label_size"])
            ax_price.legend(loc="upper left", fontsize=cfg["label_size"])
            _applyTheme(ax_price)
            draw_ax = ax_m
        else:
            fig, draw_ax = plt.subplots(figsize=cfg["figsize"], dpi=dpi)

        _drawMetricPanel(draw_ax, met_df, spec, cfg)
        draw_ax.set_ylabel(kind, fontsize=cfg["label_size"])
        fig.suptitle(title or kind.upper(), fontsize=cfg["title_size"])
        fig.autofmt_xdate(rotation=25)
        fig.tight_layout()
        return _render(fig, output=output, show=show, dpi=dpi, theme=theme)

    # ---- derivatives ----
    if layout == "derivative":
        has_first = "First_Derivative" in met_df.columns
        has_second = "Second_Derivative" in met_df.columns
        n_ind = int(has_first) + int(has_second)
        n_rows = n_ind + (1 if with_price and price_df is not None else 0)
        n_rows = max(n_rows, 1)
        height = cfg["figsize"][1] + 1.5 * max(0, n_rows - 1)
        ratios = ([1.4] if with_price and price_df is not None else []) + [1.0] * n_ind
        if not ratios:
            ratios = [1.0]
        fig, axes = plt.subplots(
            n_rows,
            1,
            sharex=True,
            figsize=(cfg["figsize"][0], height),
            dpi=dpi,
            gridspec_kw={"height_ratios": ratios},
        )
        if n_rows == 1:
            axes = [axes]
        _drawDerivatives(axes, met_df, cfg, price_df if with_price else None)
        fig.suptitle(title or "Derivatives", fontsize=cfg["title_size"])
        fig.autofmt_xdate(rotation=25)
        fig.tight_layout()
        return _render(fig, output=output, show=show, dpi=dpi, theme=theme)

    raise ValueError(f"Unknown metrics layout: {layout!r}")
