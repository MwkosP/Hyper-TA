"""Signal charts — price/indicator + glowing signals + optional threshold rules."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path

import pandas as pd

from HyperTA.Plots.utils import (
    _buildSignalsChart,
    _coerceSignalDates,
    _drawThresholdRule,
    _ensureShowBackend,
    _prepareSigmaBands,
    _render,
)


def plotSignals(
    df: pd.DataFrame,
    signal_dates=None,
    *,
    indicator_df: pd.DataFrame | None = None,
    kind: str | None = None,
    showIndicator: bool = False,
    showIndicatorSignals: bool = True,
    showSignalsOnIndicator: bool = False,
    # threshold rule overlays (optional)
    rule: str | None = None,
    thr: float | None = None,
    band: tuple[float, float] | None = None,
    ema_period: int = 10,
    window: int = 50,
    sigma: float = 0.8,
    sigma_df: pd.DataFrame | None = None,
    title: str = "Signals",
    price_col: str = "Close",
    date_col: str = "Date",
    label: str = "Price",
    theme: str = "hyperta",
    output: str | Path | BytesIO | None = None,
    show: bool = True,
    dpi: int | None = None,
) -> Path | BytesIO | None:
    """
    plotIndicator-style chart + glowing signals, optional threshold geometry.

    Indicator layouts
    -----------------
    - overlay (bbands, ichimoku, …): on price
    - panel / macd (rsi, atr, …): under price

    Threshold rules (set ``rule=``)
    -------------------------------
    - ``"level"`` — horizontal ``thr`` (crossLevel / holdLevel)
    - ``"band"``  — shaded ``band=(lo, hi)`` (inRange / skew-kurt zones)
    - ``"sigma"`` — EMA ± σ on price (stdvBandsThreshold); signals may be
      a ``(above, below)`` tuple

    ``signal_dates`` accepts list / Date-Price frame / (above, below) tuple.
    """
    if show:
        _ensureShowBackend()

    rule_key = (rule or "").lower() or None
    dates = _coerceSignalDates(signal_dates) if rule_key else signal_dates

    # sigma lives on price — don't require an indicator panel
    show_ind = showIndicator
    if rule_key == "sigma" and show_ind and indicator_df is None:
        show_ind = False

    fig, ax_price, ax_ind, meta = _buildSignalsChart(
        df,
        dates,
        indicator_df=indicator_df,
        kind=kind,
        showIndicator=show_ind,
        showIndicatorSignals=showIndicatorSignals,
        showSignalsOnIndicator=showSignalsOnIndicator,
        price_col=price_col,
        date_col=date_col,
        label=label,
        theme=theme,
        dpi=dpi,
    )

    if rule_key is not None:
        bands = sigma_df
        if rule_key == "sigma" and bands is None:
            bands = _prepareSigmaBands(df, ema_period=ema_period, window=window, sigma=sigma)
        _drawThresholdRule(
            ax_price,
            ax_ind,
            rule=rule_key,
            thr=thr,
            band=band,
            sigma_df=bands,
            prefer_indicator=(rule_key in {"level", "band"}),
        )

    fig.suptitle(title, fontsize=meta["cfg"]["title_size"])
    fig.autofmt_xdate(rotation=25)
    fig.tight_layout()
    return _render(fig, output=output, show=show, dpi=meta["dpi"], theme=theme)
