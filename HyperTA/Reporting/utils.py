"""Internal helpers for ReportLab PDF reporting."""
from __future__ import annotations

import json
from io import BytesIO
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate


def _useAgg():
    """Force non-interactive backend for PDF chart embeds (headless-safe)."""
    try:
        matplotlib.use("Agg", force=True)
    except Exception:
        pass


# Letter + generous margins (no edge bleed)
_PAGE = letter
_MARGIN = 0.85 * inch

_INK = colors.HexColor("#222222")
_MUTED = colors.HexColor("#555555")
_RULE = colors.HexColor("#222222")
_LIGHT = colors.HexColor("#f2f2f2")
_GRID = colors.HexColor("#cccccc")


def _projectRoot() -> Path:
    return Path(__file__).resolve().parents[2]


def _cacheDir() -> Path:
    path = _projectRoot() / "Cache"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _defaultOutPath(report_type: str, format: str = "pdf") -> Path:
    return _cacheDir() / f"{report_type}_report.{format}"


def _logoPath() -> Path:
    """Official Hyper-TA banner used on report cover pages."""
    return _projectRoot() / "Assets" / "img" / "hypertalogo.png"


def _typeImagePath(analysis_type: str) -> Path:
    """
    Cover art for the analysis type (shown right of cover stats).
    """
    key = str(analysis_type).strip().lower()
    img_dir = _projectRoot() / "Assets" / "img"
    mapping = {
        "hyperparameter search": img_dir / "dummy_rsi14_crossLevel30.png",
        "search analysis": img_dir / "dummy_rsi14_crossLevel30.png",
        "state comparison": img_dir / "dummy_williams_crossLevel_m20.png",
        "compare": img_dir / "dummy_williams_crossLevel_m20.png",
        "comparison": img_dir / "dummy_williams_crossLevel_m20.png",
    }
    path = mapping.get(key, img_dir / "dummy_rsi14_crossLevel30.png")
    return path


def _dummySignalImagePaths(analysis_type: str = "Hyperparameter Search") -> list[tuple[str, Path]]:
    """Static demo signal plots shipped under Assets/img/dummy_*.png."""
    img_dir = _projectRoot() / "Assets" / "img"
    key = str(analysis_type).strip().lower()
    if key in {"state comparison", "compare", "comparison"}:
        return [
            ("Williams %R(14) × crossLevel(-20)", img_dir / "dummy_williams_crossLevel_m20.png"),
            ("ATR(14) × crossLevel (dummy)", img_dir / "dummy_atr_crossLevel.png"),
        ]
    return [
        ("RSI(14) × crossLevel(30)", img_dir / "dummy_rsi14_crossLevel30.png"),
        ("RSI(20) × crossLevel(30)", img_dir / "dummy_rsi20_crossLevel30.png"),
        ("RSI periods 14–20 × crossLevel(30)", img_dir / "dummy_rsi14_20_crossLevel30.png"),
        ("ATR(14) × crossLevel (dummy)", img_dir / "dummy_atr_crossLevel.png"),
    ]


def _signalCount(signals) -> int:
    if signals is None:
        return 0
    if isinstance(signals, pd.DataFrame):
        return len(signals)
    if isinstance(signals, (list, tuple)):
        return len(signals)
    return 0


def _flattenStates(states) -> list[dict]:
    flat = []

    if states is None:
        return flat

    if isinstance(states, dict) and "params" in states:
        states = [states]

    if isinstance(states, list):
        for i, s in enumerate(states):
            flat.append(_normalizeOne(s, name=s.get("name", f"state_{i}")))
        return flat

    if isinstance(states, dict):
        for name, value in states.items():
            if isinstance(value, list):
                for i, s in enumerate(value):
                    flat.append(_normalizeOne(s, name=s.get("name", f"{name}_{i}")))
            else:
                flat.append(
                    _normalizeOne(
                        value,
                        name=value.get("name", name) if isinstance(value, dict) else name,
                    )
                )
        return flat

    raise TypeError(f"Unsupported states type: {type(states)}")


def _normalizeOne(state, name: str) -> dict:
    if not isinstance(state, dict):
        raise TypeError(f"Each state must be a dict, got {type(state)}")
    params = state.get("params", {})
    signals = state.get("signals")
    return {
        "name": name,
        "params": params,
        "signals": signals,
        "signal_count": int(state.get("signal_count", _signalCount(signals))),
    }


def _paramsText(params, max_len: int = 120) -> str:
    try:
        text = json.dumps(params, sort_keys=True, default=str)
    except Exception:
        text = str(params)
    if len(text) > max_len:
        return text[: max_len - 3] + "..."
    return text


def _escape(text: str) -> str:
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def _styles():
    base = getSampleStyleSheet()
    styles = {
        "brand": ParagraphStyle(
            "brand",
            parent=base["Normal"],
            fontName="Times-Italic",
            fontSize=10,
            textColor=_MUTED,
            spaceAfter=0,
        ),
        "title": ParagraphStyle(
            "title",
            parent=base["Normal"],
            fontName="Times-Bold",
            fontSize=20,
            leading=24,
            textColor=_INK,
            spaceBefore=2,
            spaceAfter=8,
        ),
        "subtitle": ParagraphStyle(
            "subtitle",
            parent=base["Normal"],
            fontName="Times-Roman",
            fontSize=11,
            leading=14,
            textColor=_MUTED,
            spaceAfter=14,
        ),
        "h1": ParagraphStyle(
            "h1",
            parent=base["Normal"],
            fontName="Times-Bold",
            fontSize=14,
            leading=18,
            textColor=_INK,
            spaceBefore=4,
            spaceAfter=8,
        ),
        "h2": ParagraphStyle(
            "h2",
            parent=base["Normal"],
            fontName="Times-Bold",
            fontSize=11,
            leading=14,
            textColor=_INK,
            spaceBefore=10,
            spaceAfter=6,
        ),
        "body": ParagraphStyle(
            "body",
            parent=base["Normal"],
            fontName="Times-Roman",
            fontSize=10,
            leading=14,
            textColor=_INK,
            alignment=TA_JUSTIFY,
            spaceAfter=8,
        ),
        "meta": ParagraphStyle(
            "meta",
            parent=base["Normal"],
            fontName="Times-Roman",
            fontSize=10,
            leading=14,
            textColor=_INK,
            spaceAfter=3,
        ),
        "caption": ParagraphStyle(
            "caption",
            parent=base["Normal"],
            fontName="Times-Italic",
            fontSize=9,
            leading=11,
            textColor=_MUTED,
            spaceBefore=6,
            spaceAfter=10,
        ),
        "mono": ParagraphStyle(
            "mono",
            parent=base["Normal"],
            fontName="Courier",
            fontSize=8,
            leading=11,
            textColor=_INK,
            spaceAfter=4,
        ),
        "tablecell": ParagraphStyle(
            "tablecell",
            parent=base["Normal"],
            fontName="Times-Roman",
            fontSize=8,
            leading=10,
            textColor=_INK,
        ),
        "tableheader": ParagraphStyle(
            "tableheader",
            parent=base["Normal"],
            fontName="Times-Bold",
            fontSize=8,
            leading=10,
            textColor=_INK,
        ),
        "footer": ParagraphStyle(
            "footer",
            parent=base["Normal"],
            fontName="Times-Italic",
            fontSize=8,
            textColor=_MUTED,
            alignment=TA_LEFT,
        ),
        "footer_right": ParagraphStyle(
            "footer_right",
            parent=base["Normal"],
            fontName="Times-Italic",
            fontSize=10,
            textColor=_MUTED,
            alignment=TA_RIGHT,
            spaceAfter=0,
        ),
        "center": ParagraphStyle(
            "center",
            parent=base["Normal"],
            fontName="Times-Italic",
            fontSize=10,
            alignment=TA_CENTER,
            textColor=_MUTED,
        ),
    }
    return styles


def _drawCoverFooterNotes(canvas):
    """Cover page only — pinned above the bottom rule."""
    canvas.saveState()
    canvas.setFont("Times-Italic", 9)
    canvas.setFillColor(_MUTED)
    x = _MARGIN
    canvas.drawString(x, 1.15 * inch, "Technical report — hyperparameter search analysis")
    canvas.drawString(
        x,
        1.0 * inch,
        "Made using the Hyper-TA Python library (https://github.com/MwkosP/Hyper-TA).",
    )
    canvas.restoreState()


def _footerCanvas(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(_GRID)
    canvas.setLineWidth(0.4)
    y = 0.55 * inch
    canvas.line(_MARGIN, y, _PAGE[0] - _MARGIN, y)
    canvas.setFont("Times-Italic", 8)
    canvas.setFillColor(_MUTED)
    canvas.drawString(_MARGIN, 0.35 * inch, "HyperTA")
    canvas.setFillColor(colors.HexColor("#999999"))
    canvas.drawRightString(_PAGE[0] - _MARGIN, 0.35 * inch, f"{doc.page}")
    canvas.restoreState()
    if doc.page == 1:
        _drawCoverFooterNotes(canvas)


def _buildPdf(story, out_path: Path) -> tuple[Path, int]:
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    page_count = {"n": 0}

    def _on_page(canvas, doc):
        _footerCanvas(canvas, doc)
        page_count["n"] = doc.page

    doc = SimpleDocTemplate(
        str(out_path),
        pagesize=_PAGE,
        leftMargin=_MARGIN,
        rightMargin=_MARGIN,
        topMargin=_MARGIN,
        bottomMargin=0.85 * inch,
        title="HyperTA Report",
        author="HyperTA",
    )
    doc.build(story, onFirstPage=_on_page, onLaterPages=_on_page)
    return out_path, page_count["n"]


def _chartSignalBars(rows: list[dict], width: float = 5.8 * inch, height: float = 3.2 * inch) -> BytesIO:
    """Render a simple academic bar chart to PNG bytes for ReportLab Image."""
    _useAgg()
    ordered = sorted(rows, key=lambda r: r["signal_count"], reverse=True)
    names = [r["name"] for r in ordered]
    counts = [r["signal_count"] for r in ordered]

    fig, ax = plt.subplots(figsize=(width / inch, height / inch), dpi=140)
    ax.bar(range(len(names)), counts, color="#4a4a4a", width=0.72, edgecolor="none")
    ax.set_xticks(range(len(names)))
    ax.set_xticklabels(names, rotation=30, ha="right", fontsize=8)
    ax.set_ylabel("Signal count", fontsize=9)
    ax.set_xlabel("State", fontsize=9)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", linestyle=":", linewidth=0.5, color="#cccccc")
    ax.tick_params(length=3, width=0.5)
    fig.tight_layout()

    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=140, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    buf.seek(0)
    return buf


def _chartSignalTimeline(row: dict, width: float = 5.8 * inch, height: float = 2.8 * inch) -> BytesIO | None:
    _useAgg()
    signals = row.get("signals")
    if not isinstance(signals, pd.DataFrame) or signals.empty or "Date" not in signals.columns:
        return None

    y = signals["Price"] if "Price" in signals.columns else pd.Series(range(len(signals)))
    fig, ax = plt.subplots(figsize=(width / inch, height / inch), dpi=140)
    ax.plot(signals["Date"], y, color="#888888", lw=0.9, alpha=0.8)
    ax.scatter(signals["Date"], y, s=18, c="#333333", zorder=3, edgecolors="none")
    ax.set_ylabel("Price" if "Price" in signals.columns else "index", fontsize=9)
    ax.set_xlabel("Date", fontsize=9)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(True, linestyle=":", linewidth=0.5, color="#cccccc")
    fig.autofmt_xdate(rotation=25)
    fig.tight_layout()

    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=140, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    buf.seek(0)
    return buf


def _chartCompareBars(rows: list[dict], top_n: int = 5, width: float = 5.8 * inch, height: float = 3.0 * inch) -> BytesIO:
    _useAgg()
    top = sorted(rows, key=lambda r: r["signal_count"], reverse=True)[:top_n]
    names = [r["name"] for r in top][::-1]
    counts = [r["signal_count"] for r in top][::-1]

    fig, ax = plt.subplots(figsize=(width / inch, height / inch), dpi=140)
    ax.barh(range(len(names)), counts, color="#4a4a4a", height=0.55, edgecolor="none")
    ax.set_yticks(range(len(names)))
    ax.set_yticklabels(names, fontsize=8)
    ax.set_xlabel("Signal count", fontsize=9)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="x", linestyle=":", linewidth=0.5, color="#cccccc")
    fig.tight_layout()

    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=140, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    buf.seek(0)
    return buf


def _bestState(rows: list[dict]) -> dict | None:
    if not rows:
        return None
    return max(rows, key=lambda r: r.get("signal_count", 0))


def _chartPriceWithSignals(
    price_df: pd.DataFrame,
    signals: pd.DataFrame,
    title: str = "",
    width: float = 5.8 * inch,
    height: float = 3.0 * inch,
    max_markers: int = 40,
) -> BytesIO | None:
    """Price series with signal markers (live OHLCV + Date/Price signals)."""
    _useAgg()
    if price_df is None or not isinstance(price_df, pd.DataFrame) or price_df.empty:
        return None
    if "Date" not in price_df.columns or "Close" not in price_df.columns:
        return None

    plot_df = price_df.copy()
    plot_df["Date"] = pd.to_datetime(plot_df["Date"])
    # downsample long series for readable PDF charts
    step = max(1, len(plot_df) // 1200)
    plot_df = plot_df.iloc[::step]

    fig, ax = plt.subplots(figsize=(width / inch, height / inch), dpi=140)
    ax.plot(plot_df["Date"], plot_df["Close"], color="#333333", lw=0.8, label="Close")

    if isinstance(signals, pd.DataFrame) and not signals.empty and "Date" in signals.columns:
        sig = signals.copy()
        sig["Date"] = pd.to_datetime(sig["Date"])
        if len(sig) > max_markers:
            # keep evenly spaced sample of markers for clutter control
            idx = np.linspace(0, len(sig) - 1, max_markers).astype(int)
            sig = sig.iloc[idx]
        y = sig["Price"] if "Price" in sig.columns else None
        if y is None:
            merged = pd.merge(sig[["Date"]], price_df[["Date", "Close"]], on="Date", how="left")
            y = merged["Close"]
            sig = merged
        ax.scatter(sig["Date"], y, s=22, c="#b00020", zorder=4, label="Signal", edgecolors="none")

    if title:
        ax.set_title(title, fontsize=9, loc="left", pad=6)
    ax.set_ylabel("Price", fontsize=9)
    ax.set_xlabel("Date", fontsize=9)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(True, linestyle=":", linewidth=0.5, color="#cccccc")
    ax.legend(frameon=False, fontsize=7, loc="upper left")
    fig.autofmt_xdate(rotation=25)
    fig.tight_layout()

    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=140, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    buf.seek(0)
    return buf
