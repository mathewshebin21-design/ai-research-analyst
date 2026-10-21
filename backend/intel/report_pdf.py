"""Boardroom PDF export. Every figure in the report is a claim, an assumption or a model output.

Styling continues the navy/ivory/gold direction approved for the product (design A) and builds
on the ReportLab layout in the original src/pdf_generator.py.
"""

import io
from datetime import UTC, datetime
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from intel.finance import ASSUMPTION_SPEC

NAVY = colors.HexColor("#0B1628")
INK = colors.HexColor("#1B2333")
MUTED = colors.HexColor("#5E6675")
GOLD = colors.HexColor("#A88A45")
RULE = colors.HexColor("#D9D4C7")
STATUS_COLOR = {
    "supported": colors.HexColor("#2C6E4F"),
    "partial": colors.HexColor("#8A5A00"),
    "contradicted": colors.HexColor("#A3392B"),
    "unsupported": colors.HexColor("#A3392B"),
    "missing": MUTED,
}
STATUS_LABEL = {
    "supported": "Supported",
    "partial": "Partially supported",
    "contradicted": "Contradicted",
    "unsupported": "Unsupported",
    "missing": "Missing data",
}

DISCLAIMER = (
    "This report was produced with automated research and language-model analysis. It is provided for information "
    "and to support, not replace, professional judgement. It is not financial, investment, legal or tax advice. "
    "Claims are labelled with how well retrieved sources support them; check the cited extracts before relying on "
    "any figure. Financial projections are deterministic calculations from the stated assumptions, several of "
    "which are estimates."
)


def _styles() -> dict[str, ParagraphStyle]:
    base = dict(fontName="Helvetica", textColor=INK, alignment=TA_LEFT)
    return {
        "eyebrow": ParagraphStyle(
            "eyebrow", fontSize=7.5, leading=10, textColor=GOLD, fontName="Helvetica-Bold", spaceAfter=4
        ),
        "title": ParagraphStyle(
            "title", fontName="Times-Roman", fontSize=24, leading=29, textColor=NAVY, spaceAfter=10
        ),
        "h1": ParagraphStyle(
            "h1", fontName="Times-Roman", fontSize=16, leading=20, textColor=NAVY, spaceBefore=14, spaceAfter=8
        ),
        "h2": ParagraphStyle(
            "h2", fontName="Helvetica-Bold", fontSize=8, leading=11, textColor=MUTED, spaceBefore=8, spaceAfter=4
        ),
        "body": ParagraphStyle("body", fontSize=9.5, leading=14, **base),
        "small": ParagraphStyle("small", fontSize=8, leading=11, textColor=MUTED, fontName="Helvetica"),
        "quote": ParagraphStyle("quote", fontName="Times-Italic", fontSize=10, leading=14, textColor=INK, leftIndent=8),
        "verdict": ParagraphStyle(
            "verdict", fontName="Times-Roman", fontSize=19, leading=24, textColor=NAVY, spaceAfter=6
        ),
        "cell": ParagraphStyle("cell", fontSize=8.5, leading=11.5, **base),
    }


def _p(text: str, style: ParagraphStyle) -> Paragraph:
    return Paragraph(escape(str(text)), style)


def _eur(v: float) -> str:
    sign = "−" if v < 0 else ""
    v = abs(v)
    return f"{sign}€{v / 1_000_000:.2f}m" if v >= 1_000_000 else f"{sign}€{round(v / 1000):,}k"


def _table(rows: list[list], widths: list[float], header: bool = True) -> Table:
    t = Table(rows, colWidths=widths, repeatRows=1 if header else 0)
    style = [
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LINEBELOW", (0, 0), (-1, -1), 0.4, RULE),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 2),
    ]
    if header:
        style += [("LINEBELOW", (0, 0), (-1, 0), 0.8, NAVY), ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold")]
    t.setStyle(TableStyle(style))
    return t


def _footer(canvas, doc, title: str) -> None:
    canvas.saveState()
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(MUTED)
    canvas.drawString(
        18 * mm, 10 * mm, f"{title[:90]}  ·  Generated {datetime.now(UTC):%d %b %Y}  ·  Not financial advice"
    )
    canvas.drawRightString(A4[0] - 18 * mm, 10 * mm, f"Page {doc.page}")
    canvas.restoreState()


def build_report(data: dict) -> bytes:
    """`data` is the run read model from intel.api.runs.run_detail plus the chosen scenario."""
    s = _styles()
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
        title="Market entry assessment",
        author=data.get("workspace_name", ""),
    )
    width = A4[0] - 36 * mm
    story: list = []
    rec = data.get("recommendation") or {}
    claims = data.get("claims", [])

    # Cover and recommendation.
    story += [
        _p("STRATEGIC INTELLIGENCE HUB · MARKET ENTRY ASSESSMENT", s["eyebrow"]),
        _p(data["question"], s["title"]),
        _p(f"{data.get('workspace_name', '')} · run completed {data.get('finished_at', '')[:10]}", s["small"]),
        Spacer(1, 10),
    ]
    if rec:
        box = [
            [_p(f"RECOMMENDATION · {rec.get('verdict', '').upper()}", s["eyebrow"])],
            [_p(rec.get("headline", ""), s["verdict"])],
            [_p(rec.get("summary", ""), s["body"])],
            [
                _p(
                    f"Confidence {rec.get('confidence_label')} ({rec.get('confidence', 0):.2f}). "
                    f"{rec.get('confidence_method', '')}. "
                    f"Verdict rule: {rec.get('rule', '')}",
                    s["small"],
                )
            ],
        ]
        t = Table(box, colWidths=[width])
        t.setStyle(
            TableStyle(
                [
                    ("LINEBEFORE", (0, 0), (0, -1), 2.5, GOLD),
                    ("LEFTPADDING", (0, 0), (-1, -1), 10),
                    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F7F5EF")),
                ]
            )
        )
        story += [t, Spacer(1, 8)]
        cols = []
        for title, items in (
            ("PROCEED ONLY IF", rec.get("conditions", [])),
            ("WHAT WOULD CHANGE THIS", rec.get("would_change", [])),
        ):
            cols.append([_p(title, s["h2"])] + [_p(f"– {i}", s["body"]) for i in items])
        story.append(
            Table([[cols[0], cols[1]]], colWidths=[width / 2, width / 2], style=[("VALIGN", (0, 0), (-1, -1), "TOP")])
        )

    # Scores.
    factors = data.get("factors", [])
    if factors:
        story.append(_p("How the score is built", s["h1"]))
        rows = [["Factor", "Weight", "Score", "Evidence", "Basis"]]
        for f in factors:
            rows.append(
                [
                    _p(f["label"], s["cell"]),
                    f"{f['weight'] * 100:.0f}%",
                    str(f["score"]),
                    f"{f['coverage'] * 100:.0f}%",
                    _p(f"{f['rationale']} ({', '.join(f['claims']) or 'no claims cited'})", s["cell"]),
                ]
            )
        story.append(_table(rows, [38 * mm, 15 * mm, 13 * mm, 17 * mm, width - 83 * mm]))
        story.append(
            _p(f"Weighted score {rec.get('overall', '')} / 100. Factors without evidence are held at 50.", s["small"])
        )

    # Financials.
    scenario = data.get("scenario")
    if scenario:
        story.append(_p("Financial scenarios", s["h1"]))
        res = scenario["results"]["scenarios"]
        rows = [["", "Conservative", "Base", "Optimistic"]]
        for label, key, fmt in (
            ("Break-even month", "break_even_month", lambda v: f"Month {v}" if v else "Not within 36 months"),
            ("Payback month", "payback_month", lambda v: f"Month {v}" if v else "Not within 36 months"),
            ("Peak funding need", "peak_funding", lambda v: _eur(-v)),
            ("Revenue, 36 months", "revenue_36", _eur),
            ("Cash at month 36", "cash_36", _eur),
        ):
            rows.append([label] + [fmt(res[n][key]) for n in ("conservative", "base", "optimistic")])
        story.append(_table(rows, [50 * mm] + [(width - 50 * mm) / 3] * 3))
        story.append(_p("Assumptions", s["h2"]))
        arows = [["Assumption", "Value", "Origin"]]
        for k, v in scenario["assumptions"].items():
            origin = {
                "evidence": f"Evidence {v.get('claim')}",
                "estimate": "Model estimate",
                "user": "Entered by user",
            }.get(v.get("origin"), v.get("origin"))
            spec = ASSUMPTION_SPEC.get(k, {"label": k, "unit": ""})
            value = f"{v['value'] * 100:.0f}%" if spec["unit"] == "share" else f"€{v['value']:,.0f}"
            arows.append([spec["label"], value, origin])
        story.append(_table(arows, [60 * mm, 40 * mm, width - 100 * mm]))
        sens = scenario["results"].get("sensitivity", [])[:4]
        if sens:
            story.append(
                _p(
                    "Most sensitive inputs (change in month-36 cash for a ±20% move): "
                    + "; ".join(f"{r['label']} {_eur(r['low'])} / {_eur(r['high'])}" for r in sens),
                    s["small"],
                )
            )

    # Frameworks.
    story.append(PageBreak())
    story.append(_p("Market and competitors", s["h1"]))
    comps = data.get("competitors", [])
    if comps:
        rows = [["Competitor", "Positioning", "Price", "Evidence"]]
        for c in comps:
            rows.append(
                [
                    _p(c["name"], s["cell"]),
                    _p(c["positioning"], s["cell"]),
                    _p(c.get("price_note") or "—", s["cell"]),
                    ", ".join(c["claims"]),
                ]
            )
        story.append(_table(rows, [35 * mm, width - 95 * mm, 35 * mm, 25 * mm]))
    else:
        story.append(_p("No competitor was named in the evidence.", s["small"]))

    swot = data.get("swot")
    if swot:
        story.append(_p("SWOT", s["h1"]))
        cells = []
        for k in ("strengths", "weaknesses", "opportunities", "threats"):
            cells.append(
                [_p(k.upper(), s["h2"])]
                + [_p(f"– {i['text']} ({', '.join(i['claims']) or 'no evidence'})", s["cell"]) for i in swot.get(k, [])]
            )
        story.append(
            Table(
                [[cells[0], cells[1]], [cells[2], cells[3]]],
                colWidths=[width / 2] * 2,
                style=[("VALIGN", (0, 0), (-1, -1), "TOP"), ("GRID", (0, 0), (-1, -1), 0.4, RULE)],
            )
        )
    pestle = data.get("pestle", [])
    if pestle:
        story.append(_p("PESTLE", s["h1"]))
        rows = [["Factor", "Impact", "Note", "Evidence"]] + [
            [p["factor"], f"{p['rating']}/5", _p(p["note"], s["cell"]), ", ".join(p["claims"]) or "—"] for p in pestle
        ]
        story.append(_table(rows, [30 * mm, 15 * mm, width - 70 * mm, 25 * mm]))
    porter = data.get("porter", [])
    if porter:
        story.append(_p("Five Forces", s["h1"]))
        rows = [["Force", "Intensity", "Rationale", "Evidence"]] + [
            [f["force"], f"{f['level']}/5", _p(f["rationale"], s["cell"]), ", ".join(f["claims"]) or "—"]
            for f in porter
        ]
        story.append(_table(rows, [30 * mm, 18 * mm, width - 73 * mm, 25 * mm]))

    # Risks and gaps.
    story.append(_p("Critique and missing data", s["h1"]))
    for f in data.get("findings", []):
        story.append(_p(f"[{f['severity'].upper()}] {f['text']}", s["body"]))
    for m in data.get("missing", []):
        story.append(_p(f"Missing ({m['impact']}): {m['item']}. Plan: {m['plan']}", s["body"]))

    # Evidence appendix.
    story.append(PageBreak())
    story.append(_p("Evidence appendix", s["h1"]))
    story.append(
        _p(
            "Each claim with its status and the extracts the verifier relied on. Relevance shows how closely a "
            "passage matched the search; only the support score decides the status.",
            s["small"],
        )
    )
    sources = {src["id"]: src for src in data.get("sources", [])}
    for c in claims:
        block = [
            Spacer(1, 6),
            Paragraph(
                f"<b>{escape(c['key'])}</b> · <font color='{STATUS_COLOR[c['status']].hexval()}'>"
                f"{STATUS_LABEL[c['status']]}</font> · {escape(c['text'])}",
                s["body"],
            ),
            _p(c["status_reason"], s["small"]),
        ]
        for e in c.get("evidence", [])[:3]:
            src = sources.get(e["source_id"], {})
            cite = f"{src.get('key', '')} {src.get('publisher', '')}" + (f", p. {e['page']}" if e.get("page") else "")
            if src.get("url"):
                cite += f" · {src['url']}"
            text = e.get("quote") or e["passage"][:400]
            block += [
                _p(f"“{text}”", s["quote"]),
                _p(
                    f"{cite} · {e['relation']} · support {e['entailment']:.2f} · relevance {e['relevance']:.2f}",
                    s["small"],
                ),
            ]
        story.append(KeepTogether(block))

    story.append(_p("Sources", s["h1"]))
    rows = [["Key", "Publisher", "Tier", "Title / location", "Retrieved"]]
    for src in data.get("sources", []):
        rows.append(
            [
                src["key"],
                _p(src["publisher"], s["cell"]),
                src["tier"],
                _p(f"{src['title']} {src.get('url') or ''}", s["cell"]),
                src.get("retrieved_at", "")[:10],
            ]
        )
    story.append(_table(rows, [12 * mm, 40 * mm, 10 * mm, width - 87 * mm, 25 * mm]))

    story.append(_p("Important notice", s["h1"]))
    story.append(_p(DISCLAIMER, s["small"]))

    doc.build(
        story,
        onFirstPage=lambda c, d: _footer(c, d, data["question"]),
        onLaterPages=lambda c, d: _footer(c, d, data["question"]),
    )
    return buf.getvalue()
