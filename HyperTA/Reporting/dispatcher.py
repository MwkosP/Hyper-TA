"""User-facing reporting entrypoints.

buildReport(type, states, ...) produces a full multi-page PDF for the
chosen analysis template. Page layouts live in pages.py; templates in reporting.py.
"""
from __future__ import annotations

from HyperTA.Reporting.reporting import analysisReport, compareReport
from HyperTA.Reporting.utils import _defaultOutPath


_REPORT_MAP = {
    "analysis": analysisReport,
    "compare": compareReport,
}


def buildReport(type, states, format="pdf", out=None, **kwargs):
    """
    Build a multi-page analysis PDF from search states (saved under Cache/ by default).

    Args:
        type: report template — "analysis" | "compare"
        states: search output (list of states or dict of named state lists)
        format: output format (default "pdf")
        out: optional path; default Cache/{type}_report.pdf
        **kwargs: template options (top_n, max_state_pages, ...)

    Returns:
        dict with {"type", "path", "n_pages", ...}
    """
    report_type = str(type).lower()
    if report_type not in _REPORT_MAP:
        raise ValueError(
            f"Unknown report type: {type!r}. "
            f"Expected one of: {sorted(_REPORT_MAP)}"
        )

    if format != "pdf":
        raise ValueError(f"Unsupported format: {format!r}. Only 'pdf' is implemented.")

    out_path = out if out is not None else _defaultOutPath(report_type, format=format)
    return _REPORT_MAP[report_type](states, out_path=out_path, **kwargs)
