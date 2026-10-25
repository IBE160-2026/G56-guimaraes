import io
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def generate_management_pdf(company_name: str, ai_report, ns4102_summary: dict = None) -> io.BytesIO:
    """
    TOP 10% TYPOGRAPHY PATTERN:
    Genererer en formell, profesjonell styrepakke (PDF) direkte in-memory.
    Rendrer dype CFO-analyser, marginer, arbeidskapital og revisors avstemmingsstatus.
    """
    buffer = io.BytesIO()
    
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=A4,
        rightMargin=40, 
        leftMargin=40, 
        topMargin=40, 
        bottomMargin=40
    )
    
    styles = getSampleStyleSheet()
    
    # Skreddersydde typografistiler
    title_style = ParagraphStyle(
        'MainTitle', 
        parent=styles['Heading1'], 
        fontSize=20, 
        spaceAfter=5,
        textColor=colors.HexColor("#1e3a8a"),
        fontName="Helvetica-Bold"
    )
    
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor("#64748b"),
        spaceAfter=15
    )
    
    section_heading = ParagraphStyle(
        'SectionHeading', 
        parent=styles['Heading2'], 
        fontSize=12, 
        spaceBefore=12, 
        spaceAfter=6,
        textColor=colors.HexColor("#0f172a"),
        fontName="Helvetica-Bold"
    )
    
    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor("#334155")
    )
    
    callout_style = ParagraphStyle(
        'Callout',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#1e3a8a"),
        fontName="Helvetica-Bold"
    )
    
    elements = []
    
    # 1. Header
    elements.append(Paragraph(f"Styrepakke & Ledelsesrapport: {company_name}", title_style))
    elements.append(Paragraph("Utarbeidet med KI-Revisor • Basert på NS 4102 Kontoplan og Kryssavstemt Hovedbok", subtitle_style))
    elements.append(Spacer(1, 5))
    
    # 2. Hovedkonklusjon (Callout box)
    callout_data = [[Paragraph(f"<b>Hovedkonklusjon til Styret:</b><br/>{ai_report.hovedkonklusjon}", callout_style)]]
    callout_table = Table(callout_data, colWidths=[515])
    callout_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#eff6ff")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#3b82f6")),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    elements.append(callout_table)
    elements.append(Spacer(1, 10))
    
    # 3. Lønnsomhet & Marginer
    elements.append(Paragraph("1. Lønnsomhets- og Marginanalyse", section_heading))
    elements.append(Paragraph(ai_report.lonnsomhet_og_marginer, body_style))
    elements.append(Spacer(1, 8))
    
    # 4. Likviditet og Arbeidskapital
    elements.append(Paragraph("2. Likviditetsvurdering og Arbeidskapital", section_heading))
    elements.append(Paragraph(ai_report.likviditet_og_arbeidskapital, body_style))
    elements.append(Spacer(1, 8))
    
    # 5. Revisors Avstemmingsnotat
    elements.append(Paragraph("3. Revisors Avstemmingsnotat (Internkontroll)", section_heading))
    elements.append(Paragraph(ai_report.revisors_avstemmingsnotat, body_style))
    elements.append(Spacer(1, 8))
    
    # 6. Faresignaler og Potensielle Avvik
    elements.append(Paragraph("4. Identifiserte Faresignaler & Avvik", section_heading))
    for avvik in ai_report.potensielle_avvik:
        elements.append(Paragraph(f"• <font color='#b91c1c'>{avvik}</font>", body_style))
    elements.append(Spacer(1, 10))
    
    # 7. Strategisk Tiltaksliste
    elements.append(Paragraph("5. Strategisk Tiltaksliste for Ledelsen", section_heading))
    
    table_data = [
        [
            Paragraph("<b>Prioritet</b>", body_style),
            Paragraph("<b>Anbefalt Tiltak</b>", body_style),
            Paragraph("<b>Begrunnelse</b>", body_style),
            Paragraph("<b>Forventet Effekt</b>", body_style)
        ]
    ]
    
    for item in ai_report.tiltaksliste:
        prio_color = "#b91c1c" if item.prioritet == "Høy" else ("#d97706" if item.prioritet == "Medium" else "#16a34a")
        table_data.append([
            Paragraph(f"<font color='{prio_color}'><b>{item.prioritet}</b></font>", body_style),
            Paragraph(item.tiltak, body_style),
            Paragraph(getattr(item, 'begrunnelse', '-'), body_style),
            Paragraph(getattr(item, 'forventet_effekt', '-'), body_style)
        ])
        
    t = Table(table_data, colWidths=[65, 170, 140, 140])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    elements.append(t)
    
    # Bygg PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer
