"""ReportLab page/section builders (flowables).

Each function returns a list of Platypus flowables for one logical section.
Text wraps inside margins — no overflow.
"""
from __future__ import annotations

from datetime import datetime

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    HRFlowable,
    Image,
    KeepTogether,
    PageBreak,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

from HyperTA.Reporting.utils import (
    _LIGHT,
    _MUTED,
    _RULE,
    _bestState,
    _chartCompareBars,
    _chartPriceWithSignals,
    _chartSignalBars,
    _chartSignalTimeline,
    _dummySignalImagePaths,
    _escape,
    _logoPath,
    _paramsText,
    _styles,
    _typeImagePath,
)


def _rule():
    return HRFlowable(width="100%", thickness=0.7, color=_RULE, spaceBefore=2, spaceAfter=4)


def _thinRule():
    return HRFlowable(width="100%", thickness=0.4, color=colors.HexColor("#bbbbbb"), spaceBefore=2, spaceAfter=8)


def _coverLogo():
    path = _logoPath()
    if not path.is_file():
        return Paragraph("Hyper-TA", _styles()["title"])
    return Image(str(path), width=5.8 * inch, height=1.36 * inch)


def _coverTypeArt(analysis_type: str):
    """Right column: bold analysis-type label over the type picture."""
    s = _styles()
    path = _typeImagePath(analysis_type)

    label = Paragraph(
        f"<b>{_escape(analysis_type)}</b>",
        ParagraphStyle(
            "typeLabel",
            parent=s["meta"],
            fontName="Times-Bold",
            fontSize=11,
            leading=13,
            alignment=TA_CENTER,
            spaceAfter=6,
        ),
    )

    if path.is_file():
        max_w = 2.9 * inch
        try:
            from PIL import Image as PILImage

            with PILImage.open(path) as im:
                w_px, h_px = im.size
            height = max_w * (h_px / float(w_px))
        except Exception:
            height = 1.2 * inch
        art = Image(str(path), width=max_w, height=height)
    else:
        art = Paragraph(_escape(analysis_type), s["caption"])

    col = Table([[label], [Spacer(1, 0.08 * inch)], [art]], colWidths=[2.9 * inch])
    col.setStyle(
        TableStyle(
            [
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ]
        )
    )
    return col


def _coverStatsBlock(meta: dict):
    """Left-column stats: same labels for every report type."""
    s = _styles()
    lines = []
    for k, v in meta.items():
        lines.append(
            Paragraph(
                f"<b>{_escape(str(k))}:</b>&nbsp;&nbsp;{_escape(str(v))}",
                s["meta"],
            )
        )
    # stack as a single-column table so it valigns next to the image
    return Table([[line] for line in lines], colWidths=[2.9 * inch])


def pageCover(
    title: str,
    subtitle: str = "",
    analysis_type: str = "Hyperparameter Search",
    meta: dict | None = None,
):
    """
    Shared first page for every PDF report type.
    Only title / subtitle / analysis_type / meta values change.
    Layout: header → title → logo → thin rule → [stats | type art] → footer notes.
    """
    s = _styles()
    generated = f"Generated  {_escape(datetime.now().strftime('%Y-%m-%d  %H:%M'))}"
    header = Table(
        [[Paragraph("HyperTA", s["brand"]), Paragraph(generated, s["footer_right"])]],
        colWidths=[3.0 * inch, 3.0 * inch],
    )
    header.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ]
        )
    )

    stats = {"Analysis type": analysis_type}
    if meta:
        for k, v in meta.items():
            if str(k).lower() == "analysis type":
                continue
            stats[k] = v

    stats_flow = _coverStatsBlock(stats)
    art_flow = _coverTypeArt(analysis_type)
    stats_row = Table(
        [[stats_flow, art_flow]],
        colWidths=[3.0 * inch, 3.0 * inch],
    )
    stats_row.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (0, 0), "TOP"),
                ("VALIGN", (1, 0), (1, 0), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (0, 0), 0),
                ("TOPPADDING", (1, 0), (1, 0), 14),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                ("ALIGN", (1, 0), (1, 0), "RIGHT"),
            ]
        )
    )

    story = [
        header,
        Spacer(1, 0.04 * inch),
        _rule(),
        Paragraph(_escape(title), s["title"]),
    ]
    if subtitle:
        story.append(Paragraph(_escape(subtitle), s["subtitle"]))

    story.append(Spacer(1, 0.15 * inch))
    story.append(_coverLogo())
    story.append(Spacer(1, 0.15 * inch))
    story.append(_thinRule())
    story.append(Spacer(1, 0.10 * inch))
    story.append(stats_row)
    story.append(PageBreak())
    return story


def pageOverview(rows: list[dict]):
    s = _styles()
    n = len(rows)
    total = sum(r["signal_count"] for r in rows)
    avg = (total / n) if n else 0.0
    mx = max((r["signal_count"] for r in rows), default=0)
    mn = min((r["signal_count"] for r in rows), default=0)
    nonempty = sum(1 for r in rows if r["signal_count"] > 0)

    data = [
        [
            Paragraph("States", s["tablecell"]),
            Paragraph(str(n), s["tablecell"]),
            Paragraph("Max signals", s["tablecell"]),
            Paragraph(str(mx), s["tablecell"]),
        ],
        [
            Paragraph("Total signals", s["tablecell"]),
            Paragraph(str(total), s["tablecell"]),
            Paragraph("Min signals", s["tablecell"]),
            Paragraph(str(mn), s["tablecell"]),
        ],
        [
            Paragraph("Mean signals / state", s["tablecell"]),
            Paragraph(f"{avg:.2f}", s["tablecell"]),
            Paragraph("Non-empty states", s["tablecell"]),
            Paragraph(str(nonempty), s["tablecell"]),
        ],
    ]
    table = Table(data, colWidths=[1.7 * inch, 0.9 * inch, 1.7 * inch, 0.9 * inch])
    table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 2),
                ("RIGHTPADDING", (0, 0), (-1, -1), 2),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("TEXTCOLOR", (0, 0), (0, -1), _MUTED),
                ("TEXTCOLOR", (2, 0), (2, -1), _MUTED),
            ]
        )
    )

    note = (
        "This report summarizes the enumerated hyperparameter states from a HyperTA "
        "search run. Subsequent pages list configurations, compare signal yield, and "
        "inspect individual state timelines where signal series are available."
    )

    story = [
        Paragraph("1.  Overview", s["h1"]),
        _rule(),
        Paragraph("Summary statistics", s["h2"]),
        _thinRule(),
        table,
        Spacer(1, 0.2 * inch),
        Paragraph("Notes", s["h2"]),
        Paragraph(note, s["body"]),
        PageBreak(),
    ]
    return story


def pageStatesTable(rows: list[dict], title: str = "States", section: str = "2."):
    s = _styles()
    story = [
        Paragraph(f"{section}  {_escape(title)}", s["h1"]),
        _rule(),
    ]

    if not rows:
        story.append(Paragraph("No states.", s["center"]))
        story.append(PageBreak())
        return story

    shown = rows[:22]
    header = [
        Paragraph("State", s["tableheader"]),
        Paragraph("Signals", s["tableheader"]),
        Paragraph("Parameters", s["tableheader"]),
    ]
    body = [header]
    for r in shown:
        body.append(
            [
                Paragraph(_escape(r["name"][:40]), s["tablecell"]),
                Paragraph(str(r["signal_count"]), s["tablecell"]),
                Paragraph(_escape(_paramsText(r["params"], 70)), s["tablecell"]),
            ]
        )

    table = Table(body, colWidths=[1.5 * inch, 0.7 * inch, 4.0 * inch])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), _LIGHT),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#cccccc")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    story.append(table)

    if len(rows) > len(shown):
        story.append(
            Paragraph(
                f"Showing {len(shown)} of {len(rows)} states.",
                s["caption"],
            )
        )

    story.append(PageBreak())
    return story


def pageSignalDistribution(rows: list[dict], section: str = "3."):
    s = _styles()
    story = [
        Paragraph(f"{section}  Signal distribution", s["h1"]),
        _rule(),
    ]

    if not rows:
        story.append(Paragraph("No states.", s["center"]))
        story.append(PageBreak())
        return story

    buf = _chartSignalBars(rows)
    img = Image(buf, width=5.8 * inch, height=3.2 * inch)
    story.append(Spacer(1, 0.15 * inch))
    story.append(img)
    story.append(
        Paragraph(
            "Figure 1.  Signal counts by searched state (sorted descending).",
            s["caption"],
        )
    )
    story.append(PageBreak())
    return story


def pageTopStatesDetail(rows: list[dict], top_n: int = 5, section: str = "4."):
    s = _styles()
    top = sorted(rows, key=lambda r: r["signal_count"], reverse=True)[:top_n]

    story = [
        Paragraph(f"{section}  Top-{len(top)} states", s["h1"]),
        _rule(),
    ]

    if not top:
        story.append(Paragraph("No states.", s["center"]))
        story.append(PageBreak())
        return story

    blocks = []
    for i, r in enumerate(top, 1):
        block = [
            Paragraph(f"{i}.  {_escape(r['name'])}", s["h2"]),
            Paragraph(f"signals = {r['signal_count']}", s["meta"]),
            Paragraph(_escape(_paramsText(r["params"], 110)), s["mono"]),
            Spacer(1, 0.08 * inch),
        ]
        blocks.append(KeepTogether(block))

    story.extend(blocks)
    story.append(PageBreak())
    return story


def pageCompareRanking(rows: list[dict], top_n: int = 5, section: str = "2."):
    s = _styles()
    top = sorted(rows, key=lambda r: r["signal_count"], reverse=True)[:top_n]

    story = [
        Paragraph(f"{section}  Comparison", s["h1"]),
        _rule(),
    ]

    if not top:
        story.append(Paragraph("No states.", s["center"]))
        story.append(PageBreak())
        return story

    buf = _chartCompareBars(rows, top_n=top_n)
    story.append(Image(buf, width=5.8 * inch, height=3.0 * inch))
    story.append(
        Paragraph(
            f"Figure 1.  Top-{len(top)} states by signal count.",
            s["caption"],
        )
    )

    for i, r in enumerate(top, 1):
        story.append(Paragraph(f"{i}.  {_escape(r['name'])}  (n = {r['signal_count']})", s["meta"]))
        story.append(Paragraph(_escape(_paramsText(r["params"], 100)), s["mono"]))

    story.append(PageBreak())
    return story


def pageStateSignals(row: dict, section: str = "A.", price_df=None):
    s = _styles()
    story = [
        Paragraph(f"{section}  State · {_escape(row['name'])}", s["h1"]),
        _rule(),
        Paragraph(f"signals = {row['signal_count']}", s["meta"]),
        Paragraph(_escape(_paramsText(row["params"], 120)), s["mono"]),
        Spacer(1, 0.15 * inch),
    ]

    signals = row.get("signals")
    buf = None
    if price_df is not None and isinstance(signals, pd.DataFrame):
        buf = _chartPriceWithSignals(
            price_df,
            signals,
            title=f"{row['name']} — price with signals",
        )
    if buf is None:
        buf = _chartSignalTimeline(row)

    if buf is not None:
        story.append(Image(buf, width=5.8 * inch, height=2.8 * inch))
        story.append(
            Paragraph(
                "Figure.  Live price with signal markers for this configuration.",
                s["caption"],
            )
        )
    else:
        story.append(Paragraph("No signal series available for this state.", s["center"]))

    story.append(PageBreak())
    return story


def pageTopSignals(
    price_df,
    signals: pd.DataFrame,
    state_name: str = "",
    top_n: int = 20,
    section: str = "5.",
):
    """Full-page Top-N signals: price chart + table of first top_n events."""
    s = _styles()
    label = f" ({_escape(state_name)})" if state_name else ""
    story = [
        Paragraph(f"{section}  Top {top_n} signals{label}", s["h1"]),
        _rule(),
    ]

    if not isinstance(signals, pd.DataFrame) or signals.empty:
        story.append(Paragraph("No signals available.", s["center"]))
        story.append(PageBreak())
        return story

    shown = signals.head(top_n).copy()
    buf = _chartPriceWithSignals(
        price_df,
        signals,
        title=f"Price with signals — showing markers (table lists first {len(shown)})",
        height=2.6 * inch,
        max_markers=min(60, len(signals)),
    )
    if buf is not None:
        story.append(Image(buf, width=5.8 * inch, height=2.6 * inch))
        story.append(
            Paragraph(
                f"Figure.  Close price with {len(signals)} signal markers "
                f"(leading state{label}).",
                s["caption"],
            )
        )

    story.append(Paragraph(f"First {len(shown)} signals", s["h2"]))
    header_row = [
        Paragraph("#", s["tableheader"]),
        Paragraph("Date", s["tableheader"]),
        Paragraph("Price", s["tableheader"]),
    ]
    body = [header_row]
    for i, (_, r) in enumerate(shown.iterrows(), 1):
        date_s = pd.to_datetime(r["Date"]).strftime("%Y-%m-%d")
        price_s = f"{float(r['Price']):,.2f}" if "Price" in r and pd.notna(r["Price"]) else "—"
        body.append(
            [
                Paragraph(str(i), s["tablecell"]),
                Paragraph(_escape(date_s), s["tablecell"]),
                Paragraph(price_s, s["tablecell"]),
            ]
        )

    table = Table(body, colWidths=[0.5 * inch, 2.2 * inch, 2.0 * inch])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), _LIGHT),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#cccccc")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )
    story.append(table)
    if len(signals) > len(shown):
        story.append(
            Paragraph(
                f"Showing {len(shown)} of {len(signals)} total signals.",
                s["caption"],
            )
        )
    story.append(PageBreak())
    return story


def pageDummySignalGallery(analysis_type: str = "Hyperparameter Search", section: str = "5."):
    """Embed pre-rendered dummy live-signal plots from Assets/img/."""
    s = _styles()
    story = [
        Paragraph(f"{section}  Example signal plots", s["h1"]),
        _rule(),
        Paragraph(
            "Dummy charts from a manual BTC-USD run (indicator × crossLevel). "
            "These illustrate how live search signals will look in the report.",
            s["body"],
        ),
    ]

    for caption, path in _dummySignalImagePaths(analysis_type):
        if not path.is_file():
            continue
        story.append(Paragraph(_escape(caption), s["h2"]))
        try:
            from PIL import Image as PILImage

            with PILImage.open(path) as im:
                w_px, h_px = im.size
            max_w = 5.8 * inch
            height = max_w * (h_px / float(w_px))
            if height > 7.2 * inch:
                height = 7.2 * inch
                max_w = height * (w_px / float(h_px))
        except Exception:
            max_w, height = 5.8 * inch, 3.0 * inch

        story.append(Image(str(path), width=max_w, height=height))
        story.append(Paragraph(f"Figure.  {_escape(caption)}.", s["caption"]))
        story.append(Spacer(1, 0.12 * inch))

    story.append(PageBreak())
    return story
