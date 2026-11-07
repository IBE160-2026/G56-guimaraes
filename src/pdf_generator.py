import io
from typing import Optional, List, Dict, Any
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


def _fmt_nok_pdf(value: float, decimals: int = 0) -> str:
    val = float(value or 0.0)
    if decimals == 0:
        formatted = f"{val:,.0f}".replace(",", " ")
    else:
        formatted = f"{val:,.{decimals}f}".replace(",", " ").replace(".", ",")
    return f"{formatted} NOK"


def generate_management_pdf(
    company_name: str,
    ai_report,
    ns4102_summary: dict = None,
    recon_result: dict = None,
    recommendations: Optional[List[Dict[str, Any]]] = None,
) -> io.BytesIO:
    """
    TOP 10% TYPOGRAPHY PATTERN (v2.0 CFO-pakke):
    Genererer en formell, profesjonell styrepakke (PDF) direkte in-memory.
    Rendrer deterministisk nøkkeltallstabell (inkl. Soliditet, LG2, TKR og EKR),
    avstemmingsstatus/avvikstabell, deterministiske lønnsomhetsråd og dype CFO-analyser.
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
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#cbd5e1"), spaceBefore=2, spaceAfter=8))

    # 2. Hovedkonklusjon (Callout box med fargeindikator)
    has_warning = "ADVARSEL" in ai_report.hovedkonklusjon.upper() or "feil" in ai_report.revisors_avstemmingsnotat.lower()
    box_bg = colors.HexColor("#fef2f2") if has_warning else colors.HexColor("#eff6ff")
    box_border = colors.HexColor("#ef4444") if has_warning else colors.HexColor("#3b82f6")
    stamp_text = "<b>[REVISJONSSTATUS: AVVIK OPPDAGET I HOVEDBOK]</b><br/>" if has_warning else "<b>[REVISJONSSTATUS: 100% GODKJENT OG AVSTEMT]</b><br/>"

    callout_data = [[Paragraph(f"{stamp_text}<b>Hovedkonklusjon til Styret:</b><br/>{ai_report.hovedkonklusjon}", callout_style)]]
    callout_table = Table(callout_data, colWidths=[515])
    callout_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), box_bg),
        ('BOX', (0, 0), (-1, -1), 1.5, box_border),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    elements.append(callout_table)
    elements.append(Spacer(1, 10))

    # 2b. Nøkkeltallstabell (Utvidet CFO-pakke)
    if ns4102_summary and isinstance(ns4102_summary, dict):
        elements.append(Paragraph("Finansielle Nøkkeltall (Deterministisk beregnet etter NS 4102)", section_heading))
        kpi_data = [
            [
                Paragraph("<b>Driftsinntekter</b>", body_style),
                Paragraph(_fmt_nok_pdf(ns4102_summary.get("driftsinntekter", 0.0)), body_style),
                Paragraph("<b>Bruttofortjeneste</b>", body_style),
                Paragraph(_fmt_nok_pdf(ns4102_summary.get("bruttofortjeneste", 0.0)), body_style),
            ],
            [
                Paragraph("<b>Driftskostnader</b>", body_style),
                Paragraph(_fmt_nok_pdf(ns4102_summary.get("samlede_driftskostnader", 0.0)), body_style),
                Paragraph("<b>Bruttomargin</b>", body_style),
                Paragraph(f"{float(ns4102_summary.get('bruttomargin', 0.0)):.1f} %".replace(".", ","), body_style),
            ],
            [
                Paragraph("<b>Driftsresultat (EBIT)</b>", body_style),
                Paragraph(_fmt_nok_pdf(ns4102_summary.get("ebit", 0.0)), body_style),
                Paragraph("<b>Arbeidskapital</b>", body_style),
                Paragraph(_fmt_nok_pdf(ns4102_summary.get("arbeidskapital", 0.0)), body_style),
            ],
            [
                Paragraph("<b>Driftsmargin</b>", body_style),
                Paragraph(f"{float(ns4102_summary.get('driftsmargin', 0.0)):.1f} %".replace(".", ","), body_style),
                Paragraph("<b>Likviditetsgrad 1 / 2</b>", body_style),
                Paragraph(
                    f"{float(ns4102_summary.get('likviditetsgrad_1', 0.0)):.2f} / {float(ns4102_summary.get('likviditetsgrad_2', 0.0)):.2f}".replace(".", ","),
                    body_style,
                ),
            ],
            [
                Paragraph("<b>Egenkapitalandel (Soliditet)</b>", body_style),
                Paragraph(f"{float(ns4102_summary.get('egenkapitalandel', 0.0)):.1f} %".replace(".", ","), body_style),
                Paragraph("<b>Gjeldsgrad</b>", body_style),
                Paragraph(f"{float(ns4102_summary.get('gjeldsgrad', 0.0)):.2f}".replace(".", ","), body_style),
            ],
            [
                Paragraph("<b>Totalkapitalrentabilitet (TKR)</b>", body_style),
                Paragraph(f"{float(ns4102_summary.get('totalkapitalrentabilitet', 0.0)):.1f} %".replace(".", ","), body_style),
                Paragraph("<b>Egenkapitalrentabilitet (EKR)</b>", body_style),
                Paragraph(f"{float(ns4102_summary.get('egenkapitalrentabilitet', 0.0)):.1f} %".replace(".", ","), body_style),
            ],
        ]
        kpi_table = Table(kpi_data, colWidths=[135, 122, 135, 123])
        kpi_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor("#f8fafc")),
            ('BACKGROUND', (2, 0), (2, -1), colors.HexColor("#f8fafc")),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(kpi_table)
        elements.append(Spacer(1, 8))

    # 2c. Avvikstabell dersom kryssavstemming har avdekket feil
    if recon_result and not recon_result.get("is_reconciled", True):
        disc_df = recon_result.get("discrepancies")
        if disc_df is not None and not disc_df.empty:
            elements.append(Paragraph("Avvikstabell: Kryssavstemming Hovedbok mot Saldobalanse", section_heading))
            disc_rows = [[
                Paragraph("<b>Konto</b>", body_style),
                Paragraph("<b>Kontonavn</b>", body_style),
                Paragraph("<b>IB</b>", body_style),
                Paragraph("<b>Netto HB</b>", body_style),
                Paragraph("<b>Beregnet UB</b>", body_style),
                Paragraph("<b>UB (SB)</b>", body_style),
                Paragraph("<b>Avvik</b>", body_style),
            ]]
            for _, row in disc_df.iterrows():
                disc_rows.append([
                    Paragraph(str(row.get("Konto", "")), body_style),
                    Paragraph(str(row.get("Kontonavn", "")), body_style),
                    Paragraph(_fmt_nok_pdf(row.get("IB", 0.0), 2), body_style),
                    Paragraph(_fmt_nok_pdf(row.get("Netto_HB", 0.0), 2), body_style),
                    Paragraph(_fmt_nok_pdf(row.get("Beregnet_UB", 0.0), 2), body_style),
                    Paragraph(_fmt_nok_pdf(row.get("UB", 0.0), 2), body_style),
                    Paragraph(f"<font color='#b91c1c'><b>{_fmt_nok_pdf(row.get('Avvik', 0.0), 2)}</b></font>", body_style),
                ])
            disc_table = Table(disc_rows, colWidths=[45, 95, 75, 75, 75, 75, 75])
            disc_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#fef2f2")),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ]))
            elements.append(disc_table)
            elements.append(Spacer(1, 8))

    # 3. Lønnsomhet & Marginer
    elements.append(Paragraph("1. Lønnsomhets- og Marginanalyse", section_heading))
    elements.append(Paragraph(ai_report.lonnsomhet_og_marginer, body_style))
    elements.append(Spacer(1, 8))

    # 4. Likviditet og Arbeidskapital
    elements.append(Paragraph("2. Likviditetsvurdering og Arbeidskapital", section_heading))
    elements.append(Paragraph(ai_report.likviditet_og_arbeidskapital, body_style))
    elements.append(Spacer(1, 8))

    # 5. Soliditet og Kapitalavkastning (TKR/EKR)
    soliditet_txt = getattr(ai_report, "soliditet_og_rentabilitet", "")
    if soliditet_txt:
        elements.append(Paragraph("3. Soliditet og Kapitalavkastning (TKR / EKR)", section_heading))
        elements.append(Paragraph(soliditet_txt, body_style))
        elements.append(Spacer(1, 8))

    # 6. Revisors Avstemmingsnotat
    elements.append(Paragraph("4. Revisors Avstemmingsnotat (Internkontroll)", section_heading))
    elements.append(Paragraph(ai_report.revisors_avstemmingsnotat, body_style))
    elements.append(Spacer(1, 8))

    # 7. Deterministisk Lønnsomhetspotensial (dersom oppgitt fra Python-motoren)
    if recommendations:
        elements.append(Paragraph("5. Deterministisk Lønnsomhetspotensial (Beregnet i Python)", section_heading))
        rec_rows = [[
            Paragraph("<b>Kategori</b>", body_style),
            Paragraph("<b>Tiltak / Mål-KPI</b>", body_style),
            Paragraph("<b>Beregnet Effekt</b>", body_style),
        ]]
        for r in recommendations:
            rec_rows.append([
                Paragraph(str(r.get("kategori", "")), body_style),
                Paragraph(f"<b>{r.get('tittel', '')}</b><br/>{r.get('anbefaling', '')}", body_style),
                Paragraph(str(r.get("effekt_beskrivelse", "")), body_style),
            ])
        rec_table = Table(rec_rows, colWidths=[115, 240, 160])
        rec_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#eff6ff")),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        elements.append(rec_table)
        elements.append(Spacer(1, 8))

    # 8. Faresignaler og Potensielle Avvik
    elements.append(Paragraph("6. Identifiserte Faresignaler & Avvik", section_heading))
    for avvik in ai_report.potensielle_avvik:
        elements.append(Paragraph(f"• <font color='#b91c1c'>{avvik}</font>", body_style))
    elements.append(Spacer(1, 10))

    # 9. Strategisk Tiltaksliste
    elements.append(Paragraph("7. Strategisk Tiltaksliste for Ledelsen (KI-CFO)", section_heading))

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

    doc.build(elements)
    buffer.seek(0)
    return buffer
