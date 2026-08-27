"""Full multi-page PDF report templates (ReportLab)."""
from __future__ import annotations

from pathlib import Path

from reportlab.platypus import PageBreak

from HyperTA.Reporting.pages import (
    pageCompareRanking,
    pageCover,
    pageDummySignalGallery,
    pageOverview,
    pageSignalDistribution,
    pageStateSignals,
    pageStatesTable,
    pageTopSignals,
    pageTopStatesDetail,
)
from HyperTA.Reporting.utils import _bestState, _buildPdf, _flattenStates


def _dropTrailingPageBreak(story):
    if story and isinstance(story[-1], PageBreak):
        return story[:-1]
    return story


def _standardCoverMeta(rows: list[dict]) -> dict:
    """Same cover variables for every report type (values change)."""
    n_states = len(rows)
    n_signals = sum(r["signal_count"] for r in rows)
    avg = (n_signals / n_states) if n_states else 0.0
    return {
        "States searched": n_states,
        "Total signals": n_signals,
        "Mean signals / state": f"{avg:.2f}",
    }


def analysisReport(
    states,
    out_path,
    top_n: int = 5,
    max_state_pages: int = 5,
    price_df=None,
    top_signals_n: int = 20,
    **kwargs,
):
    """
    Full search-analysis PDF:
      1. Cover (shared layout + top-signals preview)
      2. Overview
      3. States table
      4. Signal distribution
      5. Top-N detail
      6. Top signals (live chart + table)
      7.. Per-state signal pages (top states)
    """
    rows = _flattenStates(states)
    best = _bestState(rows)
    best_signals = best.get("signals") if best else None
    best_name = best.get("name", "") if best else ""

    story = []
    story += pageCover(
        "HyperTA Search Analysis",
        subtitle="Multi-page analysis of hyperparameter search states",
        analysis_type="Hyperparameter Search",
        meta=_standardCoverMeta(rows),
    )
    story += pageOverview(rows)
    story += pageStatesTable(rows)
    story += pageSignalDistribution(rows)
    story += pageTopStatesDetail(rows, top_n=top_n)
    story += pageDummySignalGallery("Hyperparameter Search", section="5.")

    if price_df is not None and best_signals is not None:
        story += pageTopSignals(
            price_df,
            best_signals,
            state_name=best_name,
            top_n=top_signals_n,
            section="6.",
        )

    top = sorted(rows, key=lambda r: r["signal_count"], reverse=True)[:max_state_pages]
    for i, row in enumerate(top, 1):
        story += pageStateSignals(row, section=f"A.{i}", price_df=price_df)

    story = _dropTrailingPageBreak(story)
    path, n_pages = _buildPdf(story, Path(out_path))
    return {
        "type": "analysis",
        "path": str(path),
        "n_states": len(rows),
        "n_pages": n_pages,
    }


def compareReport(
    states,
    out_path,
    top_n: int = 5,
    price_df=None,
    top_signals_n: int = 20,
    **kwargs,
):
    """
    Comparison-focused PDF:
      1. Cover (shared layout + top-signals preview)
      2. Compare ranking layout
      3. States table (top only)
      4. Top signals chart/table
      5. Per-state pages for compared states
    """
    rows = _flattenStates(states)
    top = sorted(rows, key=lambda r: r["signal_count"], reverse=True)[:top_n]
    best = _bestState(top) or _bestState(rows)
    best_signals = best.get("signals") if best else None
    best_name = best.get("name", "") if best else ""

    story = []
    story += pageCover(
        "HyperTA Compare Report",
        subtitle=f"Side-by-side comparison of top {len(top)} states",
        analysis_type="State Comparison",
        meta=_standardCoverMeta(top),
    )
    story += pageCompareRanking(rows, top_n=top_n)
    story += pageStatesTable(top, title=f"Compared States (Top {len(top)})", section="3.")
    story += pageDummySignalGallery("State Comparison", section="4.")

    if price_df is not None and best_signals is not None:
        story += pageTopSignals(
            price_df,
            best_signals,
            state_name=best_name,
            top_n=top_signals_n,
            section="5.",
        )

    for i, row in enumerate(top, 1):
        story += pageStateSignals(row, section=f"A.{i}", price_df=price_df)

    story = _dropTrailingPageBreak(story)
    path, n_pages = _buildPdf(story, Path(out_path))
    return {
        "type": "compare",
        "path": str(path),
        "n_states": len(rows),
        "n_pages": n_pages,
    }
