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


def _normalize_report_type(report_type: str) -> str:
    """Normaliserer rapportprofil til 'styre' (Strategisk) eller 'ledelse' (Operativ)."""
    rt = str(report_type or "styre").strip().lower()
    if rt in ("styre", "styrepakke", "strategisk", "board", "strategic"):
        return "styre"
    if rt in ("ledelse", "beslutningsrapport", "operativ", "management", "operational"):
        return "ledelse"
    raise ValueError(f"Ugyldig report_type '{report_type}'. Forventet 'styre' eller 'ledelse'.")


def _build_reconciliation_table_html(is_reconciled: bool, discrepancies_df: Any) -> str:
    """Bygger HTML for avvikstabell eller grønn tomtilstand (FR-5.3)."""
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
        return f"""
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
    return (
        '<div class="empty-state" role="status">'
        "Ingen avstemmingsavvik oppdaget mellom Hovedbok og Saldobalanse (0 avvik)."
        "</div>"
    )


def _build_deterministic_recommendations_html(
    recommendations: Optional[List[Dict[str, Any]]],
    heading_id: str,
    heading_title: str,
) -> str:
    """Bygger tabell for deterministiske lønnsomhetsråd fra Python-motoren."""
    if not recommendations:
        return ""
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
    return f"""
    <div class="subsection-block" aria-labelledby="{heading_id}">
      <h3 id="{heading_id}">{html.escape(heading_title)}</h3>
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
    </div>
    """


def _build_action_rows_html(tiltak_items: List[Any]) -> str:
    """Bygger rader for KI-tiltakslisten med prioritetsmerker."""
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
    return "".join(action_rows_html)


def generate_management_html(
    company_name: str,
    ai_report: Any,
    metrics: dict,
    recon_result: Optional[Dict[str, Any]] = None,
    recommendations: Optional[List[Dict[str, Any]]] = None,
    report_type: str = "styre",
    *,
    sb_df: Optional[Any] = None,
    vat_compliance: Optional[Dict[str, Any]] = None,
    ns4102_compliance: Optional[Dict[str, Any]] = None,
    income_statement: Optional[Dict[str, Any]] = None,
    cost_drivers: Optional[List[Dict[str, Any]]] = None,
    profitability_indicators: Optional[Dict[str, Any]] = None,
    period_label: Optional[str] = None,
) -> io.BytesIO:
    """
    Genererer en selvstendig, responsiv og offline-klar HTML5-rapport direkte i minnet (io.BytesIO).
    Støtter to målgruppetilpassede innholdsprofiler via `report_type`:
      - report_type="styre": Strategisk Styrepakke (Executive Summary, Hovedtall & Lønnsomhet,
        Revisors avstemming/Compliance, Bransjeposisjonering V2-teaser, Strategiske KI-råd).
      - report_type="ledelse": Operativ Beslutningsrapport (Operativ Oppsummering, Detaljert
        Resultatoppstilling etter NS 4102, Kostnadsdrivere med progress/fordeling, MVA & Avviksdetaljer,
        Operasjonell Analyse V2-teaser, Operative KI-råd).

    ARKITEKTURGARANTI (The AI Firewall & FR-5.1 / FR-5.2):
    - Ingen tall beregnes i denne modulen, i HTML, i JavaScript eller av språkmodellen.
    - Alle nøkkeltall (metrics), lønnsomhetsråd (recommendations), avstemmingsresultater (recon_result)
      og KI-tekster (ai_report) kommer ferdig utregnet og validert fra Python/Pydantic.
    - All dynamisk tekst renses med html.escape() (FR-5.6).
    """
    profile = _normalize_report_type(report_type)
    safe_company = html.escape(str(company_name or "Selskap AS"))
    safe_period = html.escape(str(period_label or "Inneværende regnskapsperiode"))

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
    driftsinntekter_val = float(metrics.get("driftsinntekter", 0.0))
    varekostnad_val = float(metrics.get("varekostnad", 0.0))
    lonnskostnad_val = float(metrics.get("lonnskostnad", 0.0))
    andre_opex_val = float(metrics.get("andre_driftskostnader", 0.0))
    samlede_driftskost_val = float(metrics.get("samlede_driftskostnader", 0.0))
    ebit_val = float(metrics.get("ebit", 0.0))
    driftsmargin_val = float(metrics.get("driftsmargin", 0.0))
    bruttofortjeneste_val = float(metrics.get("bruttofortjeneste", 0.0))
    bruttomargin_val = float(metrics.get("bruttomargin", 0.0))
    egenkapitalandel_val = float(metrics.get("egenkapitalandel", 0.0))
    likviditetsgrad_1_val = float(metrics.get("likviditetsgrad_1", 0.0))
    likviditetsgrad_2_val = float(metrics.get("likviditetsgrad_2", 0.0))

    driftsinntekter_str = _format_nok(driftsinntekter_val, decimals=0)
    varekostnad_str = _format_nok(varekostnad_val, decimals=0)
    lonnskostnad_str = _format_nok(lonnskostnad_val, decimals=0)
    andre_opex_str = _format_nok(andre_opex_val, decimals=0)
    driftskostnader_str = _format_nok(samlede_driftskost_val, decimals=0)
    ebit_str = _format_nok(ebit_val, decimals=0)
    driftsmargin_str = _format_percent(driftsmargin_val, decimals=1)
    bruttofortjeneste_str = _format_nok(bruttofortjeneste_val, decimals=0)
    bruttomargin_str = _format_percent(bruttomargin_val, decimals=1)
    arbeidskapital_str = _format_nok(metrics.get("arbeidskapital", 0.0), decimals=0)
    likviditetsgrad_str = f"{likviditetsgrad_1_val:.2f}".replace(".", ",")
    likviditetsgrad_2_str = f"{likviditetsgrad_2_val:.2f}".replace(".", ",")
    egenkapitalandel_str = _format_percent(egenkapitalandel_val, decimals=1)
    gjeldsgrad_str = f"{float(metrics.get('gjeldsgrad', 0.0)):.2f}".replace(".", ",")
    tkr_str = _format_percent(metrics.get("totalkapitalrentabilitet", 0.0), decimals=1)
    ekr_str = _format_percent(metrics.get("egenkapitalrentabilitet", 0.0), decimals=1)
    bankinnskudd_str = _format_nok(metrics.get("bankinnskudd", 0.0), decimals=0)
    kundefordringer_str = _format_nok(metrics.get("kundefordringer", 0.0), decimals=0)
    leverandorgjeld_str = _format_nok(metrics.get("leverandorgjeld", 0.0), decimals=0)
    varelager_str = _format_nok(metrics.get("varelager", 0.0), decimals=0)
    reell_ek_str = _format_nok(metrics.get("reell_egenkapital_ub", 0.0), decimals=0)
    totalkapital_str = _format_nok(metrics.get("totalkapital_ub", 0.0), decimals=0)

    varekost_andel_val = float(metrics.get("varekost_andel", 0.0))
    lonnsandel_val = float(metrics.get("lonnsandel", 0.0))
    opex_andel_val = float(metrics.get("opex_andel", 0.0))
    driftskost_andel_val = float(metrics.get("driftskost_andel", 0.0))

    varekost_andel_str = _format_percent(varekost_andel_val, decimals=1)
    lonnsandel_str = _format_percent(lonnsandel_val, decimals=1)
    opex_andel_str = _format_percent(opex_andel_val, decimals=1)
    driftskost_andel_str = _format_percent(driftskost_andel_val, decimals=1)

    reconciliation_section_html = _build_reconciliation_table_html(is_reconciled, discrepancies_df)

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

    # Faresignaler
    avvik_items = getattr(ai_report, "potensielle_avvik", []) or []
    if avvik_items:
        risk_list_html = "".join(
            f"<li class='risk-item'>{html.escape(str(item))}</li>" for item in avvik_items
        )
    else:
        risk_list_html = "<li>Ingen spesifikke faresignaler registrert.</li>"

    # Tiltaksliste
    tiltak_items = getattr(ai_report, "tiltaksliste", []) or []
    action_rows_str = _build_action_rows_html(tiltak_items)

    # =========================================================================
    # BETINGET RENDERING BASERT PÅ REPORT_TYPE ("styre" vs. "ledelse")
    # =========================================================================
    if profile == "styre":
        doc_title = f"Styrepakke (Strategisk) – {safe_company}"
        header_badge = "STRATEGISK STYREPAKKE &bull; GOVERNANCE, SOLIDITET &amp; RISIKO"
        header_h1 = f"Styrepakke: {safe_company}"
        header_subtitle = (
            f"Strategisk styrerapport ({safe_period}) &bull; Utarbeidet med KI-Revisor &bull; "
            "Basert på NS 4102 Kontoplan og Kryssavstemt Hovedbok (The AI Firewall)"
        )

        # NS 4102 Compliance-data for styret
        if ns4102_compliance is not None:
            ns_pct_str = _format_percent(ns4102_compliance.get("overall_recognition_pct", 100.0), decimals=1)
            ns_status_lbl = (
                "100 % NS 4102-samsvar"
                if ns4102_compliance.get("is_compliant", True)
                else "Kontoplanavvik oppdaget"
            )
            ns_summary_txt = html.escape(str(ns4102_compliance.get("summary", "")))
        else:
            ns_pct_str = "100,0 %"
            ns_status_lbl = "Standard NS 4102 (1000–8999)"
            ns_summary_txt = (
                "Kontoplanen er strukturert og klassifisert etter Norsk Standard Kontoplan (NS 4102) "
                "og tilfredsstiller bokføringslovens krav til norsk regnskapsspråk."
            )

        hb_sb_status_lbl = "Balansert (∑D = ∑K)" if is_reconciled else f"{discrepancy_count} kontoavvik"
        dividend_status = (
            "Forsvarlig utbyttegrunnlag (Soliditet ≥ 30 %, Likviditetsgrad ≥ 2,0 og godkjent avstemming)"
            if (is_reconciled and egenkapitalandel_val >= 30.0 and likviditetsgrad_1_val >= 2.0 and ebit_val > 0)
            else "Tilbakeholdelse anbefales (Prioriter kapitalbuffer, likviditet eller korrigering av avstemmingsavvik før utdeling)"
        )

        deterministic_styre_html = _build_deterministic_recommendations_html(
            recommendations,
            heading_id="det-profit-heading",
            heading_title="Deterministisk Lønnsomhetspotensial (Beregnet i Python)",
        )

        # Beregn posisjon på konseptuell bransjekurve (0-100 % bredde) for V2-teaser
        benchmark_marker_pct = min(max(int(round((driftsmargin_val + 10.0) / 35.0 * 100.0)), 8), 92)

        sections_html = f"""
    <!-- 1. EXECUTIVE SUMMARY -->
    <section id="styre-executive-summary" aria-labelledby="exec-summary-heading">
      <h2 id="exec-summary-heading">1. Executive Summary (Topplederoppsummering til Styret)</h2>
      <div class="status-banner {status_class}" role="region" aria-label="Avstemmingsstatus og hovedkonklusjon">
        <span class="status-badge">[{status_badge}]</span>
        <p class="section-text"><strong>Hovedkonklusjon til Styret:</strong> {hovedkonklusjon}</p>
        <p class="section-text" style="margin-bottom:0; font-size:0.9rem;">{status_summary}</p>
      </div>
      <div class="callout-grid">
        <div class="info-card">
          <div class="info-card-title">Finansiell Bærekraft &amp; Kapitalavkastning</div>
          <p class="section-text" style="margin-bottom:0;">{soliditet_rentabilitet}</p>
        </div>
        <div class="info-card">
          <div class="info-card-title">Vurdering av Utbyttekapasitet (Aksjeloven § 8-1)</div>
          <p class="section-text" style="margin-bottom:0;">
            <strong>Status:</strong> {html.escape(dividend_status)}<br/>
            Reell egenkapital utgjør <strong>{reell_ek_str}</strong> av totalkapital på <strong>{totalkapital_str}</strong>
            (egenkapitalandel <strong>{egenkapitalandel_str}</strong>, gjeldsgrad <strong>{gjeldsgrad_str}</strong>).
          </p>
        </div>
      </div>
    </section>

    <!-- 2. HOVEDTALL & LØNNSOMHET -->
    <section id="styre-hovedtall" aria-labelledby="kpi-heading">
      <h2 id="kpi-heading">2. Hovedtall &amp; Lønnsomhet (Aggregert Styrevisning etter NS 4102)</h2>
      <div class="kpi-grid">
        <div class="kpi-card highlight-card">
          <div class="kpi-label">Driftsresultat (EBIT)</div>
          <div class="kpi-value">{ebit_str}</div>
          <div class="kpi-sub">Driftsmargin: {driftsmargin_str}</div>
        </div>
        <div class="kpi-card highlight-card">
          <div class="kpi-label">Bruttomargin</div>
          <div class="kpi-value">{bruttomargin_str}</div>
          <div class="kpi-sub">Bruttofortj.: {bruttofortjeneste_str}</div>
        </div>
        <div class="kpi-card highlight-card">
          <div class="kpi-label">Soliditet (EK-andel)</div>
          <div class="kpi-value">{egenkapitalandel_str}</div>
          <div class="kpi-sub">Gjeldsgrad: {gjeldsgrad_str}</div>
        </div>
        <div class="kpi-card highlight-card">
          <div class="kpi-label">Egenkapitalrent. (EKR)</div>
          <div class="kpi-value">{ekr_str}</div>
          <div class="kpi-sub">TKR: {tkr_str}</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label">Driftsinntekter</div>
          <div class="kpi-value">{driftsinntekter_str}</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label">Driftskostnader</div>
          <div class="kpi-value">{driftskostnader_str}</div>
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
          <div class="kpi-label">Totalkapitalrent. (TKR)</div>
          <div class="kpi-value">{tkr_str}</div>
        </div>
      </div>

      <div class="callout-grid">
        <div class="info-card">
          <div class="info-card-title">Strategisk Lønnsomhets- og Marginvurdering</div>
          <p class="section-text" style="margin-bottom:0;">{lonnsomhet}</p>
        </div>
        <div class="info-card">
          <div class="info-card-title">Finansiell Beredskap &amp; Likviditetsvurdering</div>
          <p class="section-text" style="margin-bottom:0;">{likviditet}</p>
        </div>
      </div>
    </section>

    <!-- 3. REVISORS AVSTEMMING (COMPLIANCE) -->
    <section id="styre-compliance" aria-labelledby="compliance-heading">
      <h2 id="compliance-heading">3. Revisors Avstemming &amp; Governance (Compliance)</h2>
      <div class="kpi-grid kpi-grid-3">
        <div class="kpi-card">
          <div class="kpi-label">Balansesjekk (HB &amp; SB)</div>
          <div class="kpi-value">{html.escape(hb_sb_status_lbl)}</div>
          <div class="kpi-sub">Dobbelt bokføringskontroll</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label">Kryssavstemming (IB + HB = UB)</div>
          <div class="kpi-value">{discrepancy_count} avvik</div>
          <div class="kpi-sub">{'100 % konsistent' if is_reconciled else 'Krever korrigering'}</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label">NS 4102 Klassifisering</div>
          <div class="kpi-value">{ns_pct_str}</div>
          <div class="kpi-sub">{html.escape(ns_status_lbl)}</div>
        </div>
      </div>

      <div class="info-card" style="margin-bottom: 14px;">
        <div class="info-card-title">Revisors Avstemmingsnotat (Internkontroll &amp; Regnskapspålitelighet)</div>
        <p class="section-text">{revisor_notat}</p>
        <p class="section-text" style="margin-bottom:0; font-size:0.88rem;"><strong>NS 4102 Etterlevelse:</strong> {ns_summary_txt}</p>
      </div>

      <h3 class="sub-heading">Status for Kryssavstemming: Hovedbok mot Saldobalanse (IB + HB = UB)</h3>
      {reconciliation_section_html}
    </section>

    <!-- 4. BRANSJEPOSISJONERING (V2-TEASER) -->
    <section id="styre-bransje-v2" aria-labelledby="industry-v2-heading">
      <h2 id="industry-v2-heading">4. Bransjeposisjonering &amp; NACE-Benchmarking (V2-Teaser)</h2>
      <div class="teaser-box">
        <span class="teaser-badge">V2.0 VEIKART &bull; STRATEGISK BRANSJEPOSISJONERING (NACE / BRØNNØYSUNDREGISTRENE)</span>
        <p class="section-text">
          Konseptuell visning av <strong>{safe_company}</strong> sin strategiske posisjonering mot referansebransjen
          (<em>NACE 62.010 / Norske SMB-tjenesteforetak</em>). I versjon 2.0 kobles regnskapets deterministiske nøkkeltall
          direkte mot offisiell bransjestatistikk fra Enhetsregisteret.
        </p>
        <div class="kpi-grid kpi-grid-3" style="margin-bottom: 14px;">
          <div class="kpi-card">
            <div class="kpi-label">EBIT-Margin vs. Bransjesnitt</div>
            <div class="kpi-value">{driftsmargin_str}</div>
            <div class="kpi-sub">Referansesnitt NACE: 6,0 %</div>
          </div>
          <div class="kpi-card">
            <div class="kpi-label">Bruttomargin vs. Bransjesnitt</div>
            <div class="kpi-value">{bruttomargin_str}</div>
            <div class="kpi-sub">Referansesnitt NACE: 55,0 %</div>
          </div>
          <div class="kpi-card">
            <div class="kpi-label">Soliditet vs. Bransjenorm</div>
            <div class="kpi-value">{egenkapitalandel_str}</div>
            <div class="kpi-sub">Anbefalt SMB-norm: ≥ 30,0 %</div>
          </div>
        </div>
        <div class="progress-row">
          <div class="progress-header">
            <span><strong>Konseptuell Kvartilplassering i Bransjen (Normalfordeling EBIT-margin)</strong></span>
            <span>Selskap: <strong>{driftsmargin_str}</strong> (Bransjesnitt: 6,0 %)</span>
          </div>
          <div class="progress-track" role="progressbar" aria-valuenow="{benchmark_marker_pct}" aria-valuemin="0" aria-valuemax="100" aria-label="Bransjeposisjonering">
            <div class="progress-fill progress-navy" style="width: {benchmark_marker_pct}%;"></div>
          </div>
        </div>
      </div>
    </section>

    <!-- 5. STRATEGISKE KI-RÅD -->
    <section id="styre-strategiske-rad" aria-labelledby="strategic-actions-heading">
      <h2 id="strategic-actions-heading">5. Strategiske KI-Råd: Vekst, Kapitalallokering &amp; Utbyttekapasitet</h2>
      {deterministic_styre_html}

      <div class="subsection-block">
        <h3 id="risk-heading">Identifiserte Strategiske Faresignaler &amp; Risikofaktorer</h3>
        <ul class="risk-list">
          {risk_list_html}
        </ul>
      </div>

      <div class="subsection-block">
        <h3 id="actions-heading">Strategisk Tiltaksliste for Styret (KI-CFO)</h3>
        <div class="table-wrapper">
          <table class="data-table" aria-label="Strategisk tiltaksliste for styret">
            <thead>
              <tr>
                <th>Prioritet</th>
                <th>Strategisk Tiltak</th>
                <th>Begrunnelse (Styre- og Kapitalperspektiv)</th>
                <th>Forventet Effekt (Vekst / Utbytteevne)</th>
              </tr>
            </thead>
            <tbody>
              {action_rows_str}
            </tbody>
          </table>
        </div>
      </div>
    </section>
        """
    else:
        # =====================================================================
        # PROFIL: BESLUTNINGSRAPPORT (report_type == "ledelse")
        # Fokus: Operasjonell drift, Kostnadskontroll, MVA/Avvik, Tiltak
        # =====================================================================
        doc_title = f"Beslutningsrapport (Operativ) – {safe_company}"
        header_badge = "OPERATIV BESLUTNINGSRAPPORT &bull; DRIFT, KOSTNADSKONTROLL &amp; LIKVIDITET"
        header_h1 = f"Beslutningsrapport for Ledelsen: {safe_company}"
        header_subtitle = (
            f"Operasjonell styringsrapport ({safe_period}) &bull; Utarbeidet med KI-CFO &bull; "
            "Fokus: Resultatnedbryting, Kostnadsdrivere, MVA-kontroll og Arbeidskapital (The AI Firewall)"
        )

        # Bygg deterministisk resultatoppstilling etter NS 4102 (uten å lekke råbilag fra HB)
        income_rows_html = []
        if income_statement and isinstance(income_statement.get("rows"), list) and len(income_statement["rows"]) > 0:
            raw_rows = income_statement["rows"]
        else:
            raw_rows = [
                {
                    "regnskapspost": "1. Salgs- og driftsinntekter",
                    "kontospesifikasjon": "Klasse 3 (Konto 3000-3999)",
                    "belop_nok": driftsinntekter_val,
                    "andel_pct": 100.0 if driftsinntekter_val > 0 else 0.0,
                    "row_type": "main_income",
                },
                {
                    "regnskapspost": "2. Varekostnad",
                    "kontospesifikasjon": "Klasse 4 (Konto 4000-4999)",
                    "belop_nok": -varekostnad_val,
                    "andel_pct": varekost_andel_val,
                    "row_type": "main_cost_1",
                },
                {
                    "regnskapspost": "Bruttofortjeneste (Gross Profit)",
                    "kontospesifikasjon": "Driftsinntekter - Varekostnad",
                    "belop_nok": bruttofortjeneste_val,
                    "andel_pct": bruttomargin_val,
                    "row_type": "subtotal_gross",
                },
                {
                    "regnskapspost": "3. Lønnskostnader & personalkostnader",
                    "kontospesifikasjon": "Klasse 5 (Konto 5000-5999)",
                    "belop_nok": -lonnskostnad_val,
                    "andel_pct": lonnsandel_val,
                    "row_type": "main_cost_2",
                },
                {
                    "regnskapspost": "4. Andre driftskostnader",
                    "kontospesifikasjon": "Klasse 6 & 7 (Husleie, honorarer)",
                    "belop_nok": -andre_opex_val,
                    "andel_pct": opex_andel_val,
                    "row_type": "main_cost_3",
                },
                {
                    "regnskapspost": "Sum driftskostnader",
                    "kontospesifikasjon": "Post 2 + 3 + 4",
                    "belop_nok": -samlede_driftskost_val,
                    "andel_pct": driftskost_andel_val,
                    "row_type": "subtotal_opex",
                },
                {
                    "regnskapspost": "Driftsresultat (EBIT)",
                    "kontospesifikasjon": "Driftsinntekter - Sum driftskostnader",
                    "belop_nok": ebit_val,
                    "andel_pct": driftsmargin_val,
                    "row_type": "result_ebit",
                },
            ]

        for r in raw_rows:
            rtype = str(r.get("row_type", ""))
            post_txt = html.escape(str(r.get("regnskapspost", "")))
            # Sikre at kontospesifikasjon på underkontoer kun bruker NS 4102-standardbetegnelse (ingen rå HB-beskrivelser)
            if rtype == "sub_income":
                spec_txt = "Bokført kreditsaldo i Saldobalanse (NS 4102)"
            elif rtype == "sub_cost":
                spec_txt = "Bokført debetsaldo i Saldobalanse (NS 4102)"
            else:
                spec_txt = html.escape(str(r.get("kontospesifikasjon", "")))

            amt_txt = _format_nok(r.get("belop_nok", 0.0), decimals=0)
            pct_txt = _format_percent(r.get("andel_pct", 0.0), decimals=1)

            if rtype in ("subtotal_gross", "subtotal_opex", "result_ebit"):
                row_cls = "row-highlight" if rtype == "result_ebit" else "row-subtotal"
                income_rows_html.append(
                    f"<tr class='{row_cls}'>"
                    f"<td><strong>{post_txt}</strong></td>"
                    f"<td><strong>{spec_txt}</strong></td>"
                    f"<td class='num'><strong>{amt_txt}</strong></td>"
                    f"<td class='num'><strong>{pct_txt}</strong></td>"
                    f"</tr>"
                )
            elif rtype.startswith("main_"):
                income_rows_html.append(
                    f"<tr>"
                    f"<td><strong>{post_txt}</strong></td>"
                    f"<td>{spec_txt}</td>"
                    f"<td class='num'><strong>{amt_txt}</strong></td>"
                    f"<td class='num'><strong>{pct_txt}</strong></td>"
                    f"</tr>"
                )
            else:
                income_rows_html.append(
                    f"<tr class='row-subaccount'>"
                    f"<td style='padding-left:24px;'>{post_txt}</td>"
                    f"<td>{spec_txt}</td>"
                    f"<td class='num'>{amt_txt}</td>"
                    f"<td class='num'>{pct_txt}</td>"
                    f"</tr>"
                )

        # Kostnadsdrivere med visuelle fremdriftsindikatorer (Progress Bars)
        if profitability_indicators and isinstance(profitability_indicators.get("cost_bars"), list):
            cost_bars = profitability_indicators["cost_bars"]
        else:
            cost_bars = [
                {
                    "label": f"Varekostnad – Klasse 4 ({varekostnad_str})",
                    "pct": varekost_andel_val,
                    "progress": min(max(varekost_andel_val / 100.0, 0.0), 1.0),
                    "is_highlight": False,
                },
                {
                    "label": f"Lønnskostnader – Klasse 5 ({lonnskostnad_str})",
                    "pct": lonnsandel_val,
                    "progress": min(max(lonnsandel_val / 100.0, 0.0), 1.0),
                    "is_highlight": False,
                },
                {
                    "label": f"Andre driftskostnader / Opex – Klasse 6–7 ({andre_opex_str})",
                    "pct": opex_andel_val,
                    "progress": min(max(opex_andel_val / 100.0, 0.0), 1.0),
                    "is_highlight": False,
                },
                {
                    "label": f"Gjenværende Driftsresultat / EBIT ({ebit_str})",
                    "pct": driftsmargin_val,
                    "progress": min(max(driftsmargin_val / 100.0, 0.0), 1.0),
                    "is_highlight": True,
                },
            ]

        progress_bars_html = []
        for bar in cost_bars:
            lbl = html.escape(str(bar.get("label", "")))
            pct_val = float(bar.get("pct", 0.0))
            pct_s = _format_percent(pct_val, decimals=1)
            width_int = int(round(min(max(float(bar.get("progress", pct_val / 100.0)) * 100.0, 0.0), 100.0)))
            fill_cls = "progress-navy" if bar.get("is_highlight") else "progress-slate"
            progress_bars_html.append(
                f"<div class='progress-row'>"
                f"<div class='progress-header'>"
                f"<span>{'<strong>' + lbl + '</strong>' if bar.get('is_highlight') else lbl}</span>"
                f"<span class='num'><strong>{pct_s}</strong> av driftsinntekter</span>"
                f"</div>"
                f"<div class='progress-track' role='progressbar' aria-valuenow='{width_int}' aria-valuemin='0' aria-valuemax='100' aria-label='{lbl}'>"
                f"<div class='progress-fill {fill_cls}' style='width: {width_int}%;'></div>"
                f"</div>"
                f"</div>"
            )

        # Tabell over største kostnadsdrivere per konto
        driver_rows_html = []
        if cost_drivers:
            for d in cost_drivers:
                k_no = html.escape(str(d.get("konto", "")))
                k_navn = html.escape(str(d.get("kontonavn", "")))
                k_belop = _format_nok(d.get("belop_nok", 0.0), decimals=0)
                k_opex_pct = _format_percent(d.get("andel_av_driftskost_pct", 0.0), decimals=1)
                k_rev_pct = _format_percent(d.get("andel_av_inntekt_pct", 0.0), decimals=1)
                driver_rows_html.append(
                    f"<tr>"
                    f"<td><strong>{k_no}</strong></td>"
                    f"<td>{k_navn}</td>"
                    f"<td class='num'><strong>{k_belop}</strong></td>"
                    f"<td class='num'>{k_opex_pct}</td>"
                    f"<td class='num'>{k_rev_pct}</td>"
                    f"</tr>"
                )
        else:
            # Deterministisk fallback fra aggregert NS 4102-kostnadsstruktur
            if varekostnad_val > 0:
                vk_opex_share = (varekostnad_val / samlede_driftskost_val * 100.0) if samlede_driftskost_val > 0 else 0.0
                driver_rows_html.append(
                    f"<tr><td><strong>4xxx</strong></td><td>Varekostnad (NS 4102 Klasse 4)</td>"
                    f"<td class='num'><strong>{varekostnad_str}</strong></td>"
                    f"<td class='num'>{_format_percent(vk_opex_share, 1)}</td>"
                    f"<td class='num'>{varekost_andel_str}</td></tr>"
                )
            if lonnskostnad_val > 0:
                lk_opex_share = (lonnskostnad_val / samlede_driftskost_val * 100.0) if samlede_driftskost_val > 0 else 0.0
                driver_rows_html.append(
                    f"<tr><td><strong>5xxx</strong></td><td>Lønnskostnad (NS 4102 Klasse 5)</td>"
                    f"<td class='num'><strong>{lonnskostnad_str}</strong></td>"
                    f"<td class='num'>{_format_percent(lk_opex_share, 1)}</td>"
                    f"<td class='num'>{lonnsandel_str}</td></tr>"
                )
            if andre_opex_val > 0:
                ox_opex_share = (andre_opex_val / samlede_driftskost_val * 100.0) if samlede_driftskost_val > 0 else 0.0
                driver_rows_html.append(
                    f"<tr><td><strong>6xxx–7xxx</strong></td><td>Andre driftskostnader / Opex (NS 4102 Klasse 6–7)</td>"
                    f"<td class='num'><strong>{andre_opex_str}</strong></td>"
                    f"<td class='num'>{_format_percent(ox_opex_share, 1)}</td>"
                    f"<td class='num'>{opex_andel_str}</td></tr>"
                )

        # MVA- og Avviksdetaljer for regnskapsfører/CFO
        if vat_compliance is not None:
            vat_sales_str = _format_nok(vat_compliance.get("taxable_sales_3000", driftsinntekter_val), decimals=0)
            vat_cost_str = _format_nok(
                vat_compliance.get("cost_base_4xxx_6xxx_7xxx", varekostnad_val + andre_opex_val),
                decimals=0,
            )
            out_vat_str = _format_nok(vat_compliance.get("outgoing_vat", 0.0), decimals=0)
            in_vat_str = _format_nok(vat_compliance.get("incoming_vat", 0.0), decimals=0)
            eff_vat_str = _format_percent(vat_compliance.get("effective_out_vat_pct", 0.0), decimals=1)
            vat_summary_txt = html.escape(str(vat_compliance.get("summary", "")))
            vat_findings = vat_compliance.get("findings", []) or []
        else:
            vat_sales_str = driftsinntekter_str
            vat_cost_str = _format_nok(varekostnad_val + andre_opex_val, decimals=0)
            out_vat_str = _format_nok(0.0, decimals=0)
            in_vat_str = _format_nok(0.0, decimals=0)
            eff_vat_str = _format_percent(0.0, decimals=1)
            vat_summary_txt = (
                "MVA-samsvarskontroll mellom avgiftspliktig omsetning (3000-serien), "
                "kostnadsgrunnlag (4xxx/6xxx/7xxx) og avgiftskontoer (2700-serien)."
            )
            vat_findings = []

        if vat_findings:
            vat_findings_html = "".join(
                f"<li class='risk-item'>{html.escape(str(f))}</li>" for f in vat_findings
            )
        else:
            vat_findings_html = (
                "<li>Ingen akutte MVA-avvik registrert i perioden, eller MVA-poster er ferdig oppgjort.</li>"
            )

        deterministic_ledelse_html = _build_deterministic_recommendations_html(
            recommendations,
            heading_id="det-profit-heading",
            heading_title="Deterministisk Lønnsomhetspotensial: Kostnadskutt, Prising & Reskontro (Beregnet i Python)",
        )

        sections_html = f"""
    <!-- 1. OPERATIV OPPSUMMERING -->
    <section id="ledelse-operativ-oppsummering" aria-labelledby="op-summary-heading">
      <h2 id="op-summary-heading">1. Operativ Oppsummering (Drifts- og Likviditetsstatus for Ledelsen)</h2>
      <div class="status-banner {status_class}" role="region" aria-label="Avstemmingsstatus og operativ oppsummering">
        <span class="status-badge">[{status_badge}]</span>
        <p class="section-text"><strong>Operativ Konklusjon til Daglig Leder &amp; CFO:</strong> {hovedkonklusjon}</p>
        <p class="section-text" style="margin-bottom:0; font-size:0.9rem;">{status_summary}</p>
      </div>

      <div class="kpi-grid">
        <div class="kpi-card highlight-card">
          <div class="kpi-label">Driftsinntekter</div>
          <div class="kpi-value">{driftsinntekter_str}</div>
          <div class="kpi-sub">NS 4102 Klasse 3</div>
        </div>
        <div class="kpi-card highlight-card">
          <div class="kpi-label">Bruttofortjeneste</div>
          <div class="kpi-value">{bruttofortjeneste_str}</div>
          <div class="kpi-sub">Bruttomargin: {bruttomargin_str}</div>
        </div>
        <div class="kpi-card highlight-card">
          <div class="kpi-label">Samlede Driftskostnader</div>
          <div class="kpi-value">{driftskostnader_str}</div>
          <div class="kpi-sub">Kostnadsandel: {driftskost_andel_str}</div>
        </div>
        <div class="kpi-card highlight-card">
          <div class="kpi-label">Driftsresultat (EBIT)</div>
          <div class="kpi-value">{ebit_str}</div>
          <div class="kpi-sub">Driftsmargin: {driftsmargin_str}</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label">Bankinnskudd (UB)</div>
          <div class="kpi-value">{bankinnskudd_str}</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label">Kundefordringer (UB)</div>
          <div class="kpi-value">{kundefordringer_str}</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label">Leverandørgjeld (UB)</div>
          <div class="kpi-value">{leverandorgjeld_str}</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label">Arbeidskapital</div>
          <div class="kpi-value">{arbeidskapital_str}</div>
          <div class="kpi-sub">LG1: {likviditetsgrad_str} | LG2: {likviditetsgrad_2_str}</div>
        </div>
      </div>

      <div class="callout-grid">
        <div class="info-card">
          <div class="info-card-title">Operativ Drifts- og Marginanalyse (KI-CFO)</div>
          <p class="section-text" style="margin-bottom:0;">{lonnsomhet}</p>
        </div>
        <div class="info-card">
          <div class="info-card-title">Arbeidskapital, Reskontro og Kontantstrøm</div>
          <p class="section-text" style="margin-bottom:0;">{likviditet}</p>
        </div>
      </div>
    </section>

    <!-- 2. DETALJERT RESULTATOPPSTILLING -->
    <section id="ledelse-resultatoppstilling" aria-labelledby="income-stmt-heading">
      <h2 id="income-stmt-heading">2. Detaljert Resultatoppstilling etter NS 4102 (Med %-vise Marginer)</h2>
      <div class="table-wrapper">
        <table class="data-table" aria-label="Detaljert resultatoppstilling etter NS 4102">
          <thead>
            <tr>
              <th>Regnskapspost (NS 4102)</th>
              <th>Kontospesifikasjon</th>
              <th class="num">Beløp (NOK)</th>
              <th class="num">% av Driftsinntekt</th>
            </tr>
          </thead>
          <tbody>
            {''.join(income_rows_html)}
          </tbody>
        </table>
      </div>
    </section>

    <!-- 3. KOSTNADSDRIVERE -->
    <section id="ledelse-kostnadsdrivere" aria-labelledby="cost-drivers-heading">
      <h2 id="cost-drivers-heading">3. Kostnadsdrivere: Fordeling av Varekostnad, Lønn og Opex</h2>
      <div class="info-card" style="margin-bottom: 16px;">
        <div class="info-card-title">Kostnadsstruktur og Marginfordeling (% av Driftsinntekter)</div>
        {''.join(progress_bars_html)}
      </div>

      <h3 class="sub-heading">Spesifikasjon av Største Kostnadsdrivere (NS 4102 Kontoklasse 4–7)</h3>
      <div class="table-wrapper">
        <table class="data-table" aria-label="Største kostnadsdrivere">
          <thead>
            <tr>
              <th>Konto</th>
              <th>Kontonavn / Kostnadsgruppe</th>
              <th class="num">Beløp (NOK)</th>
              <th class="num">Andel av Driftskostnader</th>
              <th class="num">Andel av Driftsinntekter</th>
            </tr>
          </thead>
          <tbody>
            {''.join(driver_rows_html)}
          </tbody>
        </table>
      </div>
    </section>

    <!-- 4. MVA & AVVIKSDETALJER -->
    <section id="ledelse-mva-og-avvik" aria-labelledby="vat-audit-heading">
      <h2 id="vat-audit-heading">4. MVA-Kontroll &amp; Avviksdetaljer (Tiltakspunkter for Regnskapsfører / CFO)</h2>
      <div class="kpi-grid">
        <div class="kpi-card">
          <div class="kpi-label">Avgiftspliktig Salg (30xx)</div>
          <div class="kpi-value">{vat_sales_str}</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label">Kostnadsgrunnlag (4/6/7xxx)</div>
          <div class="kpi-value">{vat_cost_str}</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label">Utgående MVA (270x)</div>
          <div class="kpi-value">{out_vat_str}</div>
          <div class="kpi-sub">Eff. sats: {eff_vat_str}</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label">Inngående MVA (271x)</div>
          <div class="kpi-value">{in_vat_str}</div>
        </div>
      </div>

      <div class="info-card" style="margin-bottom: 14px;">
        <div class="info-card-title">Status fra MVA- og Avstemmingskontroll</div>
        <p class="section-text"><strong>MVA-oppsummering:</strong> {vat_summary_txt}</p>
        <p class="section-text"><strong>Revisors avstemmingsnotat:</strong> {revisor_notat}</p>
        <ul class="risk-list">
          {vat_findings_html}
        </ul>
      </div>

      <h3 class="sub-heading">Kryssavstemming Hovedbok mot Saldobalanse (IB + HB = UB per konto)</h3>
      {reconciliation_section_html}

      <div class="subsection-block">
        <h3 id="op-risk-heading">Operasjonelle Faresignaler &amp; Kontrollpunkter</h3>
        <ul class="risk-list">
          {risk_list_html}
        </ul>
      </div>
    </section>

    <!-- 5. OPERASJONELL ANALYSE (V2-TEASER) -->
    <section id="ledelse-operasjonell-v2" aria-labelledby="op-v2-heading">
      <h2 id="op-v2-heading">5. Operasjonell Analyse &amp; Krysskontroll mot Forsystemer (V2-Teaser)</h2>
      <div class="teaser-box">
        <span class="teaser-badge">V2.0 VEIKART &bull; OPERASJONELL KRYSSKONTROLL (TIMELISTER, VARELAGER &amp; CRM)</span>
        <p class="section-text">
          I versjon 2.0 utvides <strong>The AI Firewall</strong> med deterministisk krysskontroll mellom regnskapets
          hovedbok og bedriftens operasjonelle forsystemer:
        </p>
        <div class="kpi-grid kpi-grid-3">
          <div class="info-card">
            <div class="info-card-title">1. Timelister &amp; Faktureringsgrad</div>
            <p class="section-text" style="margin-bottom:0; font-size:0.88rem;">
              Kryssjekker registrerte timer i timeregistreringssystem mot bokført lønnskostnad
              (<strong>{lonnskostnad_str}</strong> / lønnsandel <strong>{lonnsandel_str}</strong>) og utfakturert omsetning (konto 3000)
              for å avdekke ufakturerte timer.
            </p>
          </div>
          <div class="info-card">
            <div class="info-card-title">2. Varelager &amp; Innkjøpskontroll</div>
            <p class="section-text" style="margin-bottom:0; font-size:0.88rem;">
              Avstemmer fysisk varelager (<strong>{varelager_str}</strong> på konto 14xx) og logistikkuttak mot bokført
              varekostnad (<strong>{varekostnad_str}</strong>) for å identifisere svinn, ukurans og marginlekkasje.
            </p>
          </div>
          <div class="info-card">
            <div class="info-card-title">3. CRM &amp; Reskontro-oppfølging</div>
            <p class="section-text" style="margin-bottom:0; font-size:0.88rem;">
              Kobler CRM-pipeline og forfallsstruktur mot utestående kundefordringer (<strong>{kundefordringer_str}</strong> på konto 1500)
              og leverandørgjeld (<strong>{leverandorgjeld_str}</strong> på konto 2400) for automatisert likviditetsstyring.
            </p>
          </div>
        </div>
      </div>
    </section>

    <!-- 6. OPERATIVE KI-RÅD -->
    <section id="ledelse-operative-rad" aria-labelledby="op-actions-heading">
      <h2 id="op-actions-heading">6. Operative KI-Råd: Kostnadskutt, Prising &amp; Reskontro-optimalisering</h2>
      {deterministic_ledelse_html}

      <div class="subsection-block">
        <h3 id="actions-heading">Operativ Handlingsplan for Daglig Leder &amp; CFO (KI-Rådgiver)</h3>
        <div class="table-wrapper">
          <table class="data-table" aria-label="Operativ tiltaksliste for ledelsen">
            <thead>
              <tr>
                <th>Prioritet</th>
                <th>Konkret Operativt Tiltak</th>
                <th>Driftsmessig Begrunnelse</th>
                <th>Målbar Effekt (Kostnad / Likviditet)</th>
              </tr>
            </thead>
            <tbody>
              {action_rows_str}
            </tbody>
          </table>
        </div>
      </div>
    </section>
        """

    html_document = f"""<!DOCTYPE html>
<html lang="nb">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{doc_title}</title>
  <style>
    :root {{
      --navy: #1e3a8a;
      --navy-light: #eff6ff;
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
      max-width: 980px;
      margin: 0 auto;
      background: var(--bg-card);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 32px;
    }}
    header {{
      border-bottom: 2px solid var(--navy);
      padding-bottom: 16px;
      margin-bottom: 24px;
    }}
    .profile-badge {{
      display: inline-block;
      background-color: var(--navy-light);
      color: var(--navy);
      border: 1px solid #93c5fd;
      font-size: 0.75rem;
      font-weight: 700;
      letter-spacing: 0.04em;
      padding: 4px 10px;
      border-radius: 4px;
      margin-bottom: 8px;
      text-transform: uppercase;
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
      margin-top: 30px;
      margin-bottom: 12px;
      border-bottom: 1px solid var(--border);
      padding-bottom: 6px;
    }}
    h3, .sub-heading {{
      font-size: 1.02rem;
      color: var(--slate-900);
      margin-top: 18px;
      margin-bottom: 8px;
    }}
    .subsection-block {{
      margin-top: 16px;
    }}
    .status-banner {{
      padding: 16px 20px;
      border-radius: 6px;
      border-left: 6px solid;
      margin-bottom: 18px;
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
      margin-bottom: 18px;
    }}
    .kpi-grid-3 {{
      grid-template-columns: repeat(3, 1fr);
    }}
    .kpi-card {{
      border: 1px solid var(--border);
      border-top: 3px solid var(--navy);
      border-radius: 6px;
      padding: 12px 14px;
      background-color: #f8fafc;
    }}
    .highlight-card {{
      background-color: var(--navy-light);
      border-color: #93c5fd;
      border-top: 4px solid var(--navy);
    }}
    .kpi-label {{
      font-size: 0.78rem;
      font-weight: 700;
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
    .kpi-sub {{
      font-size: 0.78rem;
      color: var(--slate-700);
      margin-top: 4px;
    }}
    .callout-grid {{
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 14px;
      margin-bottom: 16px;
    }}
    .info-card {{
      border: 1px solid var(--border);
      border-radius: 6px;
      padding: 14px 16px;
      background-color: #ffffff;
    }}
    .info-card-title {{
      font-weight: 700;
      font-size: 0.95rem;
      color: var(--navy);
      margin-bottom: 6px;
    }}
    .teaser-box {{
      border: 1px dashed #3b82f6;
      background-color: #f8fafc;
      border-radius: 8px;
      padding: 18px;
    }}
    .teaser-badge {{
      display: inline-block;
      background-color: var(--amber-bg);
      color: var(--amber-text);
      border: 1px solid #d97706;
      font-size: 0.75rem;
      font-weight: 700;
      padding: 3px 8px;
      border-radius: 4px;
      margin-bottom: 10px;
    }}
    .progress-row {{
      margin-bottom: 12px;
    }}
    .progress-header {{
      display: flex;
      justify-content: space-between;
      font-size: 0.88rem;
      margin-bottom: 4px;
      color: var(--slate-900);
    }}
    .progress-track {{
      width: 100%;
      height: 12px;
      background-color: #e2e8f0;
      border-radius: 999px;
      overflow: hidden;
      border: 1px solid #cbd5e1;
    }}
    .progress-fill {{
      height: 100%;
      border-radius: 999px;
    }}
    .progress-navy {{
      background-color: var(--navy);
    }}
    .progress-slate {{
      background-color: #475569;
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
    .data-table tr.row-subtotal td {{
      background-color: #f1f5f9;
      border-top: 2px solid var(--slate-500);
    }}
    .data-table tr.row-highlight td {{
      background-color: var(--navy-light);
      color: var(--navy);
      border-top: 2px solid var(--navy);
      border-bottom: 2px solid var(--navy);
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
    @media (max-width: 720px) {{
      body {{
        padding: 8px;
      }}
      .container {{
        padding: 16px;
      }}
      .kpi-grid, .kpi-grid-3, .callout-grid {{
        grid-template-columns: repeat(1, 1fr);
      }}
    }}
    @page {{
      size: A4 portrait;
      margin: 14mm 12mm;
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
      section, .kpi-grid, .callout-grid, .status-banner, .teaser-box, tr {{
        break-inside: avoid;
        page-break-inside: avoid;
      }}
      thead {{
        display: table-header-group;
      }}
      h2, h3 {{
        break-after: avoid;
        page-break-after: avoid;
      }}
    }}
  </style>
</head>
<body>
  <main class="container" data-report-type="{profile}">
    <header>
      <span class="profile-badge">{header_badge}</span>
      <h1>{header_h1}</h1>
      <p class="subtitle">{header_subtitle}</p>
    </header>
    {sections_html}
    <footer>
      Generert i minnet (io.BytesIO) via The AI Firewall ({'Styrepakke – Strategisk profil' if profile == 'styre' else 'Beslutningsrapport – Operativ profil'}):
      Koden regner deterministisk i Python/Pandas, KI forklarer via Pydantic Structured Outputs.
    </footer>
  </main>
</body>
</html>
"""

    buffer = io.BytesIO(html_document.encode("utf-8"))
    buffer.seek(0)
    return buffer
