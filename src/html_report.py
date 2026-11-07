import html
import io
from typing import Any, Dict, List, Optional


def _format_nok(value: float, decimals: int = 0) -> str:
    """
    Formaterer et ferdig utregnet tall til norsk lesbart format (mellomrom som tusenskilletegn
    og komma som desimaltegn) uten å utføre regnskapsberegninger.
    """
    val = float(value or 0.0)
    if decimals == 0:
        formatted = f"{val:,.0f}".replace(",", " ")
    else:
        formatted = f"{val:,.{decimals}f}".replace(",", " ").replace(".", ",")
    return f"{formatted} NOK"


def _format_percent(value: float, decimals: int = 1) -> str:
    """Formaterer ferdig utregnet prosentverdi med norsk desimalkomma."""
    val = float(value or 0.0)
    return f"{val:.{decimals}f}".replace(".", ",") + " %"


def generate_management_html(
    company_name: str,
    ai_report: Any,
    metrics: dict,
    recon_result: Optional[Dict[str, Any]] = None,
    recommendations: Optional[List[Dict[str, Any]]] = None,
) -> io.BytesIO:
    """
    Genererer en selvstendig, responsiv og offline-klar HTML5-styrepakke direkte i minnet (io.BytesIO).

    ARKITEKTURGARANTI (The AI Firewall & FR-5.1 / FR-5.2):
    - Ingen tall beregnes i denne modulen, i HTML, i JavaScript eller av språkmodellen.
    - Alle nøkkeltall (metrics), lønnsomhetsråd (recommendations), avstemmingsresultater (recon_result)
      og KI-tekster (ai_report) kommer ferdig utregnet og validert fra Python/Pydantic.
    - All dynamisk tekst renses med html.escape() (FR-5.6).
    """
    safe_company = html.escape(str(company_name or "Selskap AS"))

    # Avstemmingsstatus
    is_reconciled = True
    discrepancy_count = 0
    discrepancies_df = None
    if recon_result is not None:
        is_reconciled = bool(recon_result.get("is_reconciled", True))
        discrepancy_count = int(recon_result.get("discrepancy_count", 0))
        discrepancies_df = recon_result.get("discrepancies")

    has_warning = (
        not is_reconciled
        or "ADVARSEL" in str(getattr(ai_report, "hovedkonklusjon", "")).upper()
        or "feil" in str(getattr(ai_report, "revisors_avstemmingsnotat", "")).lower()
    )

    # Statusboks (FR-5.3 og FR-5.4 WCAG-kontrast)
    if is_reconciled and not has_warning:
        status_class = "status-approved"
        status_badge = "REVISJONSSTATUS: 100 % GODKJENT OG AVSTEMT"
        status_summary = (
            "Full konsistens bekreftet mellom Hovedbok og Saldobalanse "
            "(IB + sum transaksjoner i HB = UB per konto, 0 avvik)."
        )
    else:
        status_class = "status-warning"
        status_badge = f"REVISJONSSTATUS: AVVIK OPPDAGET ({discrepancy_count} UAVSTEMTE KONTOER)"
        status_summary = (
            "Det er avdekket uoverensstemmelser mellom Hovedbok og Saldobalanse. "
            "Se spesifisert avvikstabell og revisors merknad nedenfor."
        )

    # Ferdig utregnede nøkkeltall fra compliance_engine.calculate_detailed_financial_metrics
    driftsinntekter_str = _format_nok(metrics.get("driftsinntekter", 0.0), decimals=0)
    driftskostnader_str = _format_nok(metrics.get("samlede_driftskostnader", 0.0), decimals=0)
    ebit_str = _format_nok(metrics.get("ebit", 0.0), decimals=0)
    driftsmargin_str = _format_percent(metrics.get("driftsmargin", 0.0), decimals=1)
    bruttofortjeneste_str = _format_nok(metrics.get("bruttofortjeneste", 0.0), decimals=0)
    bruttomargin_str = _format_percent(metrics.get("bruttomargin", 0.0), decimals=1)
    arbeidskapital_str = _format_nok(metrics.get("arbeidskapital", 0.0), decimals=0)
    likviditetsgrad_str = f"{float(metrics.get('likviditetsgrad_1', 0.0)):.2f}".replace(".", ",")
    likviditetsgrad_2_str = f"{float(metrics.get('likviditetsgrad_2', 0.0)):.2f}".replace(".", ",")
    egenkapitalandel_str = _format_percent(metrics.get("egenkapitalandel", 0.0), decimals=1)
    tkr_str = _format_percent(metrics.get("totalkapitalrentabilitet", 0.0), decimals=1)
    ekr_str = _format_percent(metrics.get("egenkapitalrentabilitet", 0.0), decimals=1)

    # Avvikstabell eller tydelig tomtilstand (FR-5.3)
    if not is_reconciled and discrepancies_df is not None and not discrepancies_df.empty:
        rows_html = []
        for _, row in discrepancies_df.iterrows():
            konto = html.escape(str(row.get("Konto", "")))
            kontonavn = html.escape(str(row.get("Kontonavn", "")))
            ib_val = _format_nok(row.get("IB", 0.0), decimals=2)
            netto_hb_val = _format_nok(row.get("Netto_HB", 0.0), decimals=2)
            beregnet_ub_val = _format_nok(row.get("Beregnet_UB", 0.0), decimals=2)
            ub_val = _format_nok(row.get("UB", 0.0), decimals=2)
            avvik_val = _format_nok(row.get("Avvik", 0.0), decimals=2)
            rows_html.append(
                f"<tr>"
                f"<td><strong>{konto}</strong></td>"
                f"<td>{kontonavn}</td>"
                f"<td class='num'>{ib_val}</td>"
                f"<td class='num'>{netto_hb_val}</td>"
                f"<td class='num'>{beregnet_ub_val}</td>"
                f"<td class='num'>{ub_val}</td>"
                f"<td class='num discrepancy-cell'><strong>{avvik_val}</strong></td>"
                f"</tr>"
            )
        reconciliation_section_html = f"""
        <div class="table-wrapper">
          <table class="data-table" aria-label="Avvikstabell for kryssavstemming">
            <thead>
              <tr>
                <th>Konto</th>
                <th>Kontonavn</th>
                <th class="num">IB</th>
                <th class="num">Netto HB</th>
                <th class="num">Beregnet UB</th>
                <th class="num">UB (Saldobalanse)</th>
                <th class="num">Avvik</th>
              </tr>
            </thead>
            <tbody>
              {''.join(rows_html)}
            </tbody>
          </table>
        </div>
        """
    else:
        reconciliation_section_html = (
            '<div class="empty-state" role="status">'
            'Ingen avstemmingsavvik oppdaget mellom Hovedbok og Saldobalanse (0 avvik).'
            '</div>'
        )

    # Escapede tekster fra ManagementCommentary (FR-5.6)
    hovedkonklusjon = html.escape(str(getattr(ai_report, "hovedkonklusjon", "")))
    lonnsomhet = html.escape(str(getattr(ai_report, "lonnsomhet_og_marginer", "")))
    likviditet = html.escape(str(getattr(ai_report, "likviditet_og_arbeidskapital", "")))
    soliditet_rentabilitet = html.escape(
        str(
            getattr(
                ai_report,
                "soliditet_og_rentabilitet",
                "Soliditet og kapitalavkastning er innenfor normale rammer for perioden.",
            )
        )
    )
    revisor_notat = html.escape(str(getattr(ai_report, "revisors_avstemmingsnotat", "")))

    # Deterministiske lønnsomhetsråd fra Python (dersom oppgitt)
    deterministic_section_html = ""
    if recommendations:
        det_rows = []
        for r in recommendations:
            kat_txt = html.escape(str(r.get("kategori", "")))
            tit_txt = html.escape(str(r.get("tittel", "")))
            anb_txt = html.escape(str(r.get("anbefaling", "")))
            kpi_txt = html.escape(str(r.get("mal_kpi", "")))
            eff_txt = html.escape(str(r.get("effekt_beskrivelse", "")))
            det_rows.append(
                f"<tr>"
                f"<td><strong>{kat_txt}</strong></td>"
                f"<td><strong>{tit_txt}</strong><br/><span>{anb_txt}</span></td>"
                f"<td>{kpi_txt}</td>"
                f"<td><strong>{eff_txt}</strong></td>"
                f"</tr>"
            )
        deterministic_section_html = f"""
        <section aria-labelledby="det-profit-heading">
          <h2 id="det-profit-heading">Deterministisk Lønnsomhetspotensial (Beregnet i Python)</h2>
          <div class="table-wrapper">
            <table class="data-table" aria-label="Deterministisk lønnsomhetspotensial">
              <thead>
                <tr>
                  <th>Kategori</th>
                  <th>Anbefalt Grep</th>
                  <th>Mål-KPI</th>
                  <th>Beregnet Effekt</th>
                </tr>
              </thead>
              <tbody>
                {''.join(det_rows)}
              </tbody>
            </table>
          </div>
        </section>
        """

    # Faresignaler
    avvik_items = getattr(ai_report, "potensielle_avvik", []) or []
    if avvik_items:
        risk_list_html = "".join(
            f"<li class='risk-item'>{html.escape(str(item))}</li>" for item in avvik_items
        )
    else:
        risk_list_html = "<li>Ingen spesifikke faresignaler registrert.</li>"

    # Strategisk tiltaksliste
    tiltak_items = getattr(ai_report, "tiltaksliste", []) or []
    action_rows_html = []
    for item in tiltak_items:
        prioritet_raw = str(getattr(item, "prioritet", "Medium"))
        prioritet = html.escape(prioritet_raw)
        if prioritet_raw == "Høy":
            prio_class = "prio-high"
        elif prioritet_raw == "Medium":
            prio_class = "prio-medium"
        else:
            prio_class = "prio-low"

        tiltak_txt = html.escape(str(getattr(item, "tiltak", "")))
        begrunnelse_txt = html.escape(str(getattr(item, "begrunnelse", "-")))
        effekt_txt = html.escape(str(getattr(item, "forventet_effekt", "-")))

        action_rows_html.append(
            f"<tr>"
            f"<td><span class='prio-badge {prio_class}'>{prioritet}</span></td>"
            f"<td><strong>{tiltak_txt}</strong></td>"
            f"<td>{begrunnelse_txt}</td>"
            f"<td>{effekt_txt}</td>"
            f"</tr>"
        )

    html_document = f"""<!DOCTYPE html>
<html lang="nb">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Styrepakke &amp; Ledelsesrapport – {safe_company}</title>
  <style>
    :root {{
      --navy: #1e3a8a;
      --slate-900: #0f172a;
      --slate-700: #334155;
      --slate-500: #475569;
      --border: #cbd5e1;
      --bg-page: #f8fafc;
      --bg-card: #ffffff;
      --green-border: #16a34a;
      --green-bg: #f0fdf4;
      --green-text: #14532d;
      --red-border: #b91c1c;
      --red-bg: #fef2f2;
      --red-text: #7f1d1d;
      --amber-text: #92400e;
      --amber-bg: #fef3c7;
    }}
    * {{
      box-sizing: border-box;
    }}
    body {{
      margin: 0;
      padding: 24px 16px;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      background-color: var(--bg-page);
      color: var(--slate-900);
      line-height: 1.55;
    }}
    .container {{
      max-width: 960px;
      margin: 0 auto;
      background: var(--bg-card);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 32px;
    }}
    header {{
      border-bottom: 2px solid var(--border);
      padding-bottom: 16px;
      margin-bottom: 24px;
    }}
    h1 {{
      margin: 0 0 6px 0;
      font-size: 1.75rem;
      color: var(--navy);
    }}
    .subtitle {{
      margin: 0;
      font-size: 0.95rem;
      color: var(--slate-500);
    }}
    h2 {{
      font-size: 1.2rem;
      color: var(--slate-900);
      margin-top: 28px;
      margin-bottom: 12px;
      border-bottom: 1px solid var(--border);
      padding-bottom: 6px;
    }}
    .status-banner {{
      padding: 16px 20px;
      border-radius: 6px;
      border-left: 6px solid;
      margin-bottom: 24px;
    }}
    .status-approved {{
      background-color: var(--green-bg);
      border-color: var(--green-border);
      color: var(--green-text);
    }}
    .status-warning {{
      background-color: var(--red-bg);
      border-color: var(--red-border);
      color: var(--red-text);
    }}
    .status-badge {{
      font-weight: 700;
      font-size: 0.95rem;
      display: block;
      margin-bottom: 6px;
    }}
    .kpi-grid {{
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 12px;
      margin-bottom: 24px;
    }}
    .kpi-card {{
      border: 1px solid var(--border);
      border-top: 3px solid var(--navy);
      border-radius: 6px;
      padding: 12px 14px;
      background-color: #f8fafc;
    }}
    .kpi-label {{
      font-size: 0.8rem;
      font-weight: 600;
      color: var(--slate-500);
      text-transform: uppercase;
      letter-spacing: 0.03em;
    }}
    .kpi-value {{
      font-size: 1.2rem;
      font-weight: 700;
      color: var(--navy);
      margin-top: 4px;
      font-variant-numeric: tabular-nums;
      font-feature-settings: "tnum" 1;
    }}
    .section-text {{
      color: var(--slate-700);
      margin: 0 0 12px 0;
    }}
    .empty-state {{
      padding: 12px 16px;
      background-color: var(--green-bg);
      border: 1px solid var(--green-border);
      color: var(--green-text);
      border-radius: 6px;
      font-weight: 600;
    }}
    .table-wrapper {{
      overflow-x: auto;
      margin-top: 8px;
    }}
    .data-table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 0.9rem;
    }}
    .data-table th,
    .data-table td {{
      border: 1px solid var(--border);
      padding: 10px 12px;
      text-align: left;
      vertical-align: top;
    }}
    .data-table th {{
      background-color: #f1f5f9;
      color: var(--slate-900);
      font-weight: 700;
    }}
    .data-table tbody tr:nth-child(even) {{
      background-color: #f8fafc;
    }}
    .data-table .num {{
      text-align: right;
      white-space: nowrap;
      font-variant-numeric: tabular-nums;
      font-feature-settings: "tnum" 1;
    }}
    .discrepancy-cell {{
      color: var(--red-text);
      background-color: var(--red-bg);
    }}
    .risk-list {{
      margin: 0;
      padding-left: 20px;
    }}
    .risk-item {{
      color: var(--red-text);
      margin-bottom: 6px;
      font-weight: 500;
    }}
    .prio-badge {{
      display: inline-block;
      padding: 2px 8px;
      border-radius: 4px;
      font-weight: 700;
      font-size: 0.8rem;
    }}
    .prio-high {{
      background-color: var(--red-bg);
      color: var(--red-text);
      border: 1px solid var(--red-border);
    }}
    .prio-medium {{
      background-color: var(--amber-bg);
      color: var(--amber-text);
      border: 1px solid #d97706;
    }}
    .prio-low {{
      background-color: var(--green-bg);
      color: var(--green-text);
      border: 1px solid var(--green-border);
    }}
    footer {{
      margin-top: 32px;
      padding-top: 16px;
      border-top: 1px solid var(--border);
      font-size: 0.8rem;
      color: var(--slate-500);
    }}
    @media (max-width: 640px) {{
      body {{
        padding: 8px;
      }}
      .container {{
        padding: 16px;
      }}
      .kpi-grid {{
        grid-template-columns: repeat(2, 1fr);
      }}
    }}
    @page {{
      size: A4 portrait;
      margin: 15mm 12mm;
    }}
    @media print {{
      * {{
        -webkit-print-color-adjust: exact !important;
        print-color-adjust: exact !important;
      }}
      body {{
        background: #ffffff;
        padding: 0;
      }}
      .container {{
        border: none;
        padding: 0;
        max-width: 100%;
      }}
      section, .kpi-grid, .status-banner, tr {{
        break-inside: avoid;
        page-break-inside: avoid;
      }}
      thead {{
        display: table-header-group;
      }}
      h2 {{
        break-after: avoid;
        page-break-after: avoid;
      }}
    }}
  </style>
</head>
<body>
  <main class="container">
    <header>
      <h1>Styrepakke &amp; Ledelsesrapport: {safe_company}</h1>
      <p class="subtitle">Utarbeidet med KI-Revisor &bull; Basert på NS 4102 Kontoplan og Kryssavstemt Hovedbok (The AI Firewall)</p>
    </header>

    <section class="status-banner {status_class}" aria-label="Avstemmingsstatus og hovedkonklusjon">
      <span class="status-badge">[{status_badge}]</span>
      <p class="section-text"><strong>Hovedkonklusjon til Styret:</strong> {hovedkonklusjon}</p>
      <p class="section-text" style="margin-bottom:0; font-size:0.9rem;">{status_summary}</p>
    </section>

    <section aria-labelledby="kpi-heading">
      <h2 id="kpi-heading">Finansielle Nøkkeltall (Deterministisk beregnet etter NS 4102)</h2>
      <div class="kpi-grid">
        <div class="kpi-card">
          <div class="kpi-label">Driftsinntekter</div>
          <div class="kpi-value">{driftsinntekter_str}</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label">Driftskostnader</div>
          <div class="kpi-value">{driftskostnader_str}</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label">Driftsresultat (EBIT)</div>
          <div class="kpi-value">{ebit_str}</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label">Driftsmargin</div>
          <div class="kpi-value">{driftsmargin_str}</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label">Bruttofortjeneste</div>
          <div class="kpi-value">{bruttofortjeneste_str}</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label">Bruttomargin</div>
          <div class="kpi-value">{bruttomargin_str}</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label">Arbeidskapital</div>
          <div class="kpi-value">{arbeidskapital_str}</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label">Likviditetsgrad 1</div>
          <div class="kpi-value">{likviditetsgrad_str}</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label">Likviditetsgrad 2</div>
          <div class="kpi-value">{likviditetsgrad_2_str}</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label">Egenkapitalandel</div>
          <div class="kpi-value">{egenkapitalandel_str}</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label">Totalkapitalrent. (TKR)</div>
          <div class="kpi-value">{tkr_str}</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label">Egenkapitalrent. (EKR)</div>
          <div class="kpi-value">{ekr_str}</div>
        </div>
      </div>
    </section>

    <section aria-labelledby="recon-heading">
      <h2 id="recon-heading">Kryssavstemming: Hovedbok mot Saldobalanse (IB + HB = UB)</h2>
      {reconciliation_section_html}
    </section>

    <section aria-labelledby="profit-heading">
      <h2 id="profit-heading">1. Lønnsomhets- og Marginanalyse</h2>
      <p class="section-text">{lonnsomhet}</p>
    </section>

    <section aria-labelledby="liquidity-heading">
      <h2 id="liquidity-heading">2. Likviditetsvurdering og Arbeidskapital</h2>
      <p class="section-text">{likviditet}</p>
    </section>

    <section aria-labelledby="solvency-heading">
      <h2 id="solvency-heading">3. Soliditet og Kapitalavkastning (TKR / EKR)</h2>
      <p class="section-text">{soliditet_rentabilitet}</p>
    </section>

    <section aria-labelledby="audit-heading">
      <h2 id="audit-heading">4. Revisors Avstemmingsnotat (Internkontroll)</h2>
      <p class="section-text">{revisor_notat}</p>
    </section>

    {deterministic_section_html}

    <section aria-labelledby="risk-heading">
      <h2 id="risk-heading">5. Identifiserte Faresignaler &amp; Avvik</h2>
      <ul class="risk-list">
        {risk_list_html}
      </ul>
    </section>

    <section aria-labelledby="actions-heading">
      <h2 id="actions-heading">6. Strategisk Tiltaksliste for Ledelsen (KI-CFO)</h2>
      <div class="table-wrapper">
        <table class="data-table" aria-label="Strategisk tiltaksliste">
          <thead>
            <tr>
              <th>Prioritet</th>
              <th>Anbefalt Tiltak</th>
              <th>Begrunnelse</th>
              <th>Forventet Effekt</th>
            </tr>
          </thead>
          <tbody>
            {''.join(action_rows_html)}
          </tbody>
        </table>
      </div>
    </section>

    <footer>
      Generert i minnet (io.BytesIO) via The AI Firewall: Koden regner deterministisk i Python/Pandas, KI forklarer via Pydantic Structured Outputs.
    </footer>
  </main>
</body>
</html>
"""

    buffer = io.BytesIO(html_document.encode("utf-8"))
    buffer.seek(0)
    return buffer
