import io
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def generate_management_pdf(company_name: str, ai_report, ns4102_summary: dict = None) -> io.BytesIO:
    """
    TOP 10% TYPOGRAPHY PATTERN:
    Genererer en piksel-perfekt PDF-rapport utelukkende in-memory (CISO krav).
    Mottar strukturerte Pydantic-objekter fra LLM-integrasjonen.
    """
    buffer = io.BytesIO()
    
    # Sett opp PDF-dokument
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=A4,
        rightMargin=50, 
        leftMargin=50, 
        topMargin=50, 
        bottomMargin=50
    )
    
    # Hent standardstiler
    styles = getSampleStyleSheet()
    
    # Skreddersydde stiler for styrepakken
    title_style = ParagraphStyle(
        'TitleStyle', 
        parent=styles['Heading1'], 
        fontSize=24, 
        spaceAfter=20,
        textColor=colors.HexColor("#1e3a8a") # Mørk blå for profesjonelt utseende
    )
    
    heading_style = ParagraphStyle(
        'HeadingStyle', 
        parent=styles['Heading2'], 
        fontSize=14, 
        spaceBefore=20, 
        spaceAfter=10,
        textColor=colors.HexColor("#334155")
    )
    
    normal_style = styles['Normal']
    normal_style.fontSize = 11
    normal_style.leading = 14
    
    elements = []
    
    # 1. Tittel og Header
    elements.append(Paragraph(f"Ledelsesrapport: {company_name}", title_style))
    elements.append(Paragraph("Autogenerert av KI-Revisor Plattform", styles['Italic']))
    elements.append(Spacer(1, 20))
    
    # 2. Økonomisk Sammendrag
    elements.append(Paragraph("Økonomisk Sammendrag", heading_style))
    elements.append(Paragraph(ai_report.okonomisk_sammendrag, normal_style))
    elements.append(Spacer(1, 15))
    
    # 3. Potensielle Avvik (Faresignaler)
    elements.append(Paragraph("Faresignaler og Potensielle Avvik", heading_style))
    for avvik in ai_report.potensielle_avvik:
        bullet_text = f"• <font color='red'>{avvik}</font>"
        elements.append(Paragraph(bullet_text, normal_style))
    elements.append(Spacer(1, 15))
    
    # 4. Strategisk Tiltaksliste (Tabell)
    elements.append(Paragraph("Strategisk Tiltaksliste", heading_style))
    
    table_data = [["Prioritet", "Anbefalt Tiltak"]]
    for tiltak in ai_report.tiltaksliste:
        table_data.append([tiltak.prioritet, tiltak.tiltak])
        
    t = Table(table_data, colWidths=[80, 400])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor("#0f172a")),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1"))
    ]))
    
    elements.append(t)
    
    # Bygg PDF-en i minnet
    doc.build(elements)
    
    # Resett pekeren i bufferet
    buffer.seek(0)
    return buffer
