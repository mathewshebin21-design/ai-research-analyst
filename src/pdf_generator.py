import io
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from src.analysis import StrategicAnalysis

def generate_pdf_report(analysis: StrategicAnalysis, query: str) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    
    # Custom Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#0F172A'),
        spaceAfter=10
    )
    
    sub_title_style = ParagraphStyle(
        'SubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#64748B'),
        spaceAfter=15
    )

    heading_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=17,
        textColor=colors.HexColor('#1E293B'),
        spaceBefore=12,
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#334155'),
        spaceAfter=6
    )

    bullet_style = ParagraphStyle(
        'BulletCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#334155'),
        leftIndent=15,
        spaceAfter=4
    )

    story = []

    # Title & Metadata
    story.append(Paragraph("Strategic Market Intelligence Assessment", title_style))
    story.append(Paragraph(f"<b>Query:</b> {query}", sub_title_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#CBD5E1'), spaceAfter=15))

    # Executive Summary Box
    rec = analysis.recommendation.upper()
    rec_color = colors.HexColor('#16A34A') if 'ENTER' in rec and 'NOT' not in rec else (colors.HexColor('#DC2626') if 'NOT' in rec else colors.HexColor('#D97706'))

    rec_table_data = [
        [Paragraph(f"<b>RECOMMENDATION:</b> <font color='{rec_color.hexval()}'><b>{rec}</b></font>", body_style)],
        [Paragraph(f"<b>Executive Summary:</b> {analysis.executive_summary}", body_style)]
    ]
    rec_table = Table(rec_table_data, colWidths=[540])
    rec_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#E2E8F0')),
        ('PADDING', (0,0), (-1,-1), 10),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(rec_table)
    story.append(Spacer(1, 15))

    # Key Market Drivers
    story.append(Paragraph("Key Market Drivers", heading_style))
    for driver in analysis.market_drivers:
        story.append(Paragraph(f"• {driver}", bullet_style))
    story.append(Spacer(1, 10))

    # Key Risks & Challenges
    story.append(Paragraph("Key Risks & Strategic Challenges", heading_style))
    for risk in analysis.key_risks:
        story.append(Paragraph(f"• {risk}", bullet_style))
    story.append(Spacer(1, 10))

    # Strategic Action Plan
    story.append(Paragraph("Recommended Action Plan", heading_style))
    for action in analysis.action_plan:
        story.append(Paragraph(f"• {action}", bullet_style))

    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()