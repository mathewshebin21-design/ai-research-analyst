from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
import io

class PDFExporter:
    @staticmethod
    def generate_report_pdf(title: str, content_data: list):
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []

        # Title
        story.append(Paragraph(title, styles['Title']))
        story.append(Spacer(1, 12))

        # Content
        for section in content_data:
            story.append(Paragraph(section['header'], styles['Heading2']))
            story.append(Spacer(1, 6))
            story.append(Paragraph(section['body'], styles['Normal']))
            story.append(Spacer(1, 12))

        doc.build(story)
        buffer.seek(0)
        return buffer
