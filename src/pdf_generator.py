import io
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
)
from src.analysis import StrategicAnalysis

def generate_pdf_report(analysis: StrategicAnalysis, query: str) -> bytes:
    buffer = io.BytesIO()
    
    # Page setup with compact executive margins
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Executive Color Palette
    COLOR_PRIMARY = colors.HexColor('#0F172A')   # Slate 900
    COLOR_ACCENT = colors.HexColor('#2563EB')    # Royal Blue 600
    COLOR_TEXT = colors.HexColor('#1E293B')      # Slate 800
    COLOR_MUTED = colors.HexColor('#64748B')     # Slate 500
    COLOR_BG = colors.HexColor('#F8FAFC')        # Soft Light Grey
    COLOR_BORDER = colors.HexColor('#E2E8F0')    # Light Border

    # Dynamic status tag colors
    rec_str = analysis.recommendation.upper()
    if 'ENTER' in rec_str and 'NOT' not in rec_str:
        REC_BG = colors.HexColor('#DCFCE7')
        REC_TEXT = colors.HexColor('#15803D')
    elif 'NOT' in rec_str:
        REC_BG = colors.HexColor('#FEE2E2')
        REC_TEXT = colors.HexColor('#B91C1C')
    else:
        REC_BG = colors.HexColor('#FEF3C7')
        REC_TEXT = colors.HexColor('#B45309')

    # Styles Definition
    header_tag_style = ParagraphStyle(
        'HeaderTag',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=11,
        textColor=COLOR_ACCENT,
        spaceAfter=4
    )

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=COLOR_PRIMARY,
        spaceAfter=12
    )

    query_style = ParagraphStyle(
        'QueryText',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=9.5,
        leading=13,
        textColor=COLOR_MUTED,
        spaceAfter=14
    )

    section_heading = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=COLOR_PRIMARY,
        spaceBefore=10,
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        'BodyCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=14,
        textColor=COLOR_TEXT
    )

    bullet_style = ParagraphStyle(
        'BulletCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=COLOR_TEXT,
        leftIndent=10,
        spaceAfter=4
    )

    story = []

    # 1. Header Banner & Branding
    story.append(Paragraph("AI RESEARCH ANALYST • STRATEGIC ASSESSMENT", header_tag_style))
    story.append(Paragraph("Market Intelligence Assessment", title_style))
    story.append(Paragraph(f"<b>Strategic Inquiry:</b> {query}", query_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=COLOR_ACCENT, spaceAfter=14))

    # 2. Executive Recommendation Callout Card
    rec_label = Paragraph(f"<b><font color='{REC_TEXT.hexval()}'>{rec_str}</font></b>", 
                          ParagraphStyle('RecL', parent=body_style, fontName='Helvetica-Bold', fontSize=13, leading=16))
    
    exec_summary_text = Paragraph(f"<b>Executive Summary:</b> {analysis.executive_summary}", body_style)

    rec_box_data = [
        [Paragraph("<b>STRATEGIC RECOMMENDATION</b>", ParagraphStyle('H', parent=body_style, fontSize=8, textColor=COLOR_MUTED)), ""],
        [rec_label, ""],
        [exec_summary_text, ""]
    ]

    rec_table = Table(rec_box_data, colWidths=[520, 20])
    rec_table.setStyle(TableStyle([
        ('SPAN', (0, 0), (1, 0)),
        ('SPAN', (0, 1), (1, 1)),
        ('SPAN', (0, 2), (1, 2)),
        ('BACKGROUND', (0, 0), (-1, -1), COLOR_BG),
        ('BOX', (0, 0), (-1, -1), 1, COLOR_BORDER),
        ('LINELEFT', (0, 0), (0, -1), 4, REC_TEXT),
        ('PADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(rec_table)
    story.append(Spacer(1, 12))

    # 3. Market Drivers Section
    drivers = getattr(analysis, 'key_drivers', getattr(analysis, 'market_drivers', []))
    story.append(Paragraph("KEY MARKET DRIVERS", section_heading))
    story.append(HRFlowable(width="100%", thickness=0.5, color=COLOR_BORDER, spaceAfter=8))
    for d in drivers:
        story.append(Paragraph(f"• {d}", bullet_style))
    story.append(Spacer(1, 10))

    # 4. Key Risks Section
    risks = getattr(analysis, 'key_risks', getattr(analysis, 'risks', []))
    story.append(Paragraph("KEY RISKS & CHALLENGES", section_heading))
    story.append(HRFlowable(width="100%", thickness=0.5, color=COLOR_BORDER, spaceAfter=8))
    for r in risks:
        story.append(Paragraph(f"• {r}", bullet_style))
    story.append(Spacer(1, 10))

    # 5. Action Plan Section
    actions = getattr(analysis, 'action_plan', getattr(analysis, 'opportunities', []))
    story.append(Paragraph("RECOMMENDED ACTION PLAN", section_heading))
    story.append(HRFlowable(width="100%", thickness=0.5, color=COLOR_BORDER, spaceAfter=8))
    for a in actions:
        story.append(Paragraph(f"• {a}", bullet_style))

    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()