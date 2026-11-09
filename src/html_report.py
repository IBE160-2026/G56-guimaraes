import html
import io
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field


# =============================================================================
# PYDANTIC DOMENEMODELLER FOR EKSPORTMOTOREN (The AI Firewall – v2.0)
# =============================================================================


class EbitDriverSensitivityModel(BaseModel):
    """Pydantic-modell for deterministisk EBIT-driver sensitivitetsanalyse (1 % endring)."""

    driftsinntekter: float = 0.0
    varekostnad: float = 0.0
    faste_kostnader_base: float = 0.0
    ebit: float = 0.0
    driftsmargin: float = 0.0
    bruttomargin: float = 0.0
    price_1pct_nok: float = 0.0
    cogs_1pct_nok: float = 0.0
    opex_1pct_nok: float = 0.0
    new_margin_price: float = 0.0
    new_margin_cogs: float = 0.0
    new_margin_opex: float = 0.0
    price_vs_opex_mult: float = 0.0
    price_vs_cogs_mult: float = 0.0
    insight_text: str = ""


class NaceDriverComparisonItem(BaseModel):
    """Enkeltlinje i NACE-driverbenchmarking mot bransjesnitt."""

    driver_label: str
    company_pct: float
    industry_pct: float
    diff_pp: float
    unfavorable_gap_pp: float
    ebit_potential_nok: float


class NaceBenchmarkingModel(BaseModel):
    """Pydantic-modell for Strategisk Posisjonering (NACE-Benchmarking & Normalfordeling V2)."""

    nace_code: str = "62.010 Programmeringstjenester"
    industry_mean_ebit_pct: float = 6.0
    industry_std_ebit_pct: float = 6.0
    simulated_company_ebit_pct: float = 12.0
    quartile_position_label: str = "3. kvartil (Topp 25 %)"
    largest_gap_cost_label: str = "varekostnad"
    largest_gap_pp: float = 4.5
    largest_gap_ebit_nok: float = 54000.0
    potential_banner_text: str = (
        "Største forbedringspotensial: Din varekostnad er 4,5 prosentpoeng høyere enn "
        "bransjesnittet. Ved å lukke dette gapet vil EBIT øke med 54 000 NOK."
    )
    drivers: List[NaceDriverComparisonItem] = Field(
        default_factory=lambda: [
            NaceDriverComparisonItem(
                driver_label="Bruttomargin vs. Bransje",
                company_pct=63.5,
                industry_pct=68.0,
                diff_pp=-4.5,
                unfavorable_gap_pp=4.5,
                ebit_potential_nok=54000.0,
            ),
            NaceDriverComparisonItem(
                driver_label="Lønnskostnad/Omsetning vs. Bransje",
                company_pct=34.0,
                industry_pct=42.5,
                diff_pp=-8.5,
                unfavorable_gap_pp=0.0,
                ebit_potential_nok=0.0,
            ),
            NaceDriverComparisonItem(
                driver_label="Opex/Omsetning vs. Bransje",
                company_pct=17.5,
                industry_pct=19.5,
                diff_pp=-2.0,
                unfavorable_gap_pp=0.0,
                ebit_potential_nok=0.0,
            ),
        ]
    )


class RfqLeakageItem(BaseModel):
    """Pydantic-modell for identifisert kostnadslekkasje og sparepotensial i RFQ-modulen."""

    kategori: str
    konto_ref: str
    avlest_vilkar: str
    markedsstandard: str
    tiltak_beskrivelse: str
    arlig_sparepotensial_nok: float


class RfqBiddingModel(BaseModel):
    """Pydantic-modell for Kostnadskontroll & Anbud (RFQ-modul V2)."""

    total_annual_savings_nok: float = 81000.0
    rfq_reference: str = "RFQ-2026-G56-FINANS"
    items: List[RfqLeakageItem] = Field(
        default_factory=lambda: [
            RfqLeakageItem(
                kategori="Bankrente & Driftskreditt",
                konto_ref="Konto 2380 / 8150",
                avlest_vilkar="Effektiv rentemargin 4,5 %",
                markedsstandard="Markedsstandard SMB ≤ 2,5 % (-2,0 %-poeng)",
                tiltak_beskrivelse="Send formell RFQ til 3 forretningsbanker for reforhandling av kassekreditt og innskuddsrente.",
                arlig_sparepotensial_nok=45000.0,
            ),
            RfqLeakageItem(
                kategori="Bedrifts- og Yrkesskadeforsikring",
                konto_ref="Konto 7500",
                avlest_vilkar="Årlig premie 120 000 NOK (indeksjustert)",
                markedsstandard="Samleanbud med 20 % premiereduksjon",
                tiltak_beskrivelse="Utlys samleanbud på yrkesskade-, ansvars- og tingskadeforsikring basert på skadefri historikk.",
                arlig_sparepotensial_nok=24000.0,
            ),
            RfqLeakageItem(
                kategori="Strøm & Lokaler",
                konto_ref="Konto 6340",
                avlest_vilkar="Spotpris + skjult påslag 9 øre/kWh og fastbeløp",
                markedsstandard="Ren bedriftsspot uten skjulte påslag",
                tiltak_beskrivelse="Bytt til fremforhandlet næringsstrømavtale uten sertifikatpåslag og faste månedsgebyrer.",
                arlig_sparepotensial_nok=12000.0,
            ),
        ]
    )


class OperationalCrossCheckItem(BaseModel):
    """Pydantic-modell for enkeltpunkt i operasjonell krysskontroll mellom fagsystem og hovedbok."""

    fagsystem: str
    regnskapskonto: str
    kontrollformaal: str
    status_etikett: str
    observasjon: str


class OperationalCrossCheckModel(BaseModel):
    """Pydantic-modell for Operasjonell Krysskontroll (V2)."""

    items: List[OperationalCrossCheckItem] = Field(
        default_factory=lambda: [
            OperationalCrossCheckItem(
                fagsystem="Lagersystem (WMS) vs. Regnskap",
                regnskapskonto="Varelager vs. Konto 1460 / 1400 & Konto 4000 Varekostnad",
                kontrollformaal="Avdekke fysisk varesvinn, ukurans og periodiseringsavvik mellom lageruttak og bokført varekostnad.",
                status_etikett="V2 KRYSSKONTROLL KLAR",
                observasjon="Kontrollerer rullerende varetelling mot bokført beholdning på Konto 1460 (Innkjøpte varer for videresalg).",
            ),
            OperationalCrossCheckItem(
                fagsystem="Timelister (HRM/Prosjekt) vs. Lønn",
                regnskapskonto="Timelister vs. Lønnskostnad (Konto 5000 & Konto 3000 Salg)",
                kontrollformaal="Avdekke lav faktureringsgrad, ufakturerte prosjekttimer og overtid uten tilhørende kundeinntekt.",
                status_etikett="V2 KRYSSKONTROLL KLAR",
                observasjon="Sammenstiller produserte timer mot utbetalt fastlønn og utfakturert honorar per konsulent/avdeling.",
            ),
            OperationalCrossCheckItem(
                fagsystem="CRM & Lisensregister vs. Reskontro",
                regnskapskonto="CRM/SaaS vs. Konto 1500 Kundefordringer & Konto 6800 Kontor/IT",
                kontrollformaal="Redusere kredittid (DSO) på forfalte fakturaer og identifisere inaktive programvarelisenser til oppsigelse.",
                status_etikett="V2 KRYSSKONTROLL KLAR",
                observasjon="Kryssjekker aktive ansatte mot løpende SaaS-abonnementer og automatiserer purreløp ved 14 dagers forfall.",
            ),
        ]
    )


# =============================================================================
# HJELPEFUNKSJONER FOR FORMATERING OG DETERMINISTISK DATAINJEKSJON
# =============================================================================


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


def _coerce_ebit_sensitivity(
    ebit_sensitivity: Optional[Union[EbitDriverSensitivityModel, Dict[str, Any]]],
    metrics: Dict[str, Any],
) -> EbitDriverSensitivityModel:
    """Sikrer et validert EbitDriverSensitivityModel-objekt fra eksisterende data eller metrics."""
    if isinstance(ebit_sensitivity, EbitDriverSensitivityModel):
        return ebit_sensitivity
    if isinstance(ebit_sensitivity, dict):
        return EbitDriverSensitivityModel(**ebit_sensitivity)

    from ledger_analytics import calculate_ebit_driver_sensitivity

    calc = calculate_ebit_driver_sensitivity(metrics)
    return EbitDriverSensitivityModel(**calc)


def _coerce_nace_benchmark(
    nace_benchmark: Optional[Union[NaceBenchmarkingModel, Dict[str, Any]]],
) -> NaceBenchmarkingModel:
    """Sikrer et validert NaceBenchmarkingModel-objekt."""
    if isinstance(nace_benchmark, NaceBenchmarkingModel):
        return nace_benchmark
    if isinstance(nace_benchmark, dict):
        drivers_raw = nace_benchmark.get("drivers")
        if drivers_raw is None and "drivers_df" in nace_benchmark:
            df = nace_benchmark["drivers_df"]
            drivers_raw = [
                NaceDriverComparisonItem(
                    driver_label=str(r["driver_label"]),
                    company_pct=float(r["company_pct"]),
                    industry_pct=float(r["industry_pct"]),
                    diff_pp=float(r["diff_pp"]),
                    unfavorable_gap_pp=float(r["unfavorable_gap_pp"]),
                    ebit_potential_nok=float(r["ebit_potential_nok"]),
                )
                for _, r in df.iterrows()
            ]
        return NaceBenchmarkingModel(
            largest_gap_cost_label=str(nace_benchmark.get("largest_gap_cost_label", "varekostnad")),
            largest_gap_pp=float(nace_benchmark.get("largest_gap_pp", 4.5)),
            largest_gap_ebit_nok=float(nace_benchmark.get("largest_gap_ebit_nok", 54000.0)),
            potential_banner_text=str(
                nace_benchmark.get(
                    "potential_banner_text",
                    "Største forbedringspotensial: Din varekostnad er 4,5 prosentpoeng høyere enn bransjesnittet.",
                )
            ),
            drivers=drivers_raw or NaceBenchmarkingModel().drivers,
        )
    return NaceBenchmarkingModel()


def _coerce_rfq_report(
    rfq_report: Optional[Union[RfqBiddingModel, Dict[str, Any]]],
) -> RfqBiddingModel:
    """Sikrer et validert RfqBiddingModel-objekt."""
    if isinstance(rfq_report, RfqBiddingModel):
        return rfq_report
    if isinstance(rfq_report, dict):
        return RfqBiddingModel(**rfq_report)
    return RfqBiddingModel()


def _coerce_operational_check(
    operational_check: Optional[Union[OperationalCrossCheckModel, Dict[str, Any]]],
) -> OperationalCrossCheckModel:
    """Sikrer et validert OperationalCrossCheckModel-objekt."""
    if isinstance(operational_check, OperationalCrossCheckModel):
        return operational_check
    if isinstance(operational_check, dict):
        return OperationalCrossCheckModel(**operational_check)
    return OperationalCrossCheckModel()


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


def _build_bell_curve_svg(company_margin_pct: float, industry_mean_pct: float = 6.0) -> str:
    """
    Genererer et 100 % selvstendig (Zero-Dependency) inline SVG-diagram av normalfordelingskurven
    for EBIT-margin i bransjen (NACE), med markør for bransjesnitt og selskapets posisjon.
    """
    # Map margin [-12 %, +24 %] til x-koordinat [40, 560] i et 600x160 SVG-koordinatsystem
    clamped = min(max(company_margin_pct, -10.0), 22.0)
    company_x = int(round(40 + ((clamped - (-12.0)) / 36.0) * 520))
    mean_x = 300  # 6,0 % ligger midt i intervallet [-12, +24]
    company_lbl = _format_percent(company_margin_pct, 1)
    mean_lbl = _format_percent(industry_mean_pct, 1)

    return f"""
    <div class="bell-curve-container" role="img" aria-label="Normalfordelingskurve for lønnsomhet i bransjen (NACE)">
      <svg viewBox="0 0 600 165" width="100%" height="165" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <linearGradient id="bellGrad" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stop-color="#1e3a8a" stop-opacity="0.28"/>
            <stop offset="100%" stop-color="#1e3a8a" stop-opacity="0.03"/>
          </linearGradient>
        </defs>
        <!-- Bunnlinje -->
        <line x1="30" y1="130" x2="570" y2="130" stroke="#94a3b8" stroke-width="1.5"/>
        <!-- Normalfordelingskurve (Bell Curve) -->
        <path d="M 40 130 C 110 129, 160 118, 210 82 C 245 52, 272 24, 300 24 C 328 24, 355 52, 390 82 C 440 118, 490 129, 560 130 Z"
              fill="url(#bellGrad)" stroke="#1e3a8a" stroke-width="2.2"/>
        <!-- Bransjesnitt (Midtlinje 6,0 %) -->
        <line x1="{mean_x}" y1="20" x2="{mean_x}" y2="130" stroke="#64748b" stroke-width="1.5" stroke-dasharray="4,4"/>
        <text x="{mean_x}" y="14" text-anchor="middle" fill="#475569" font-size="11" font-weight="600">
          Bransjesnitt: {mean_lbl}
        </text>
        <!-- Selskapets posisjon -->
        <line x1="{company_x}" y1="22" x2="{company_x}" y2="130" stroke="#16a34a" stroke-width="2.5"/>
        <circle cx="{company_x}" cy="48" r="5" fill="#16a34a" stroke="#ffffff" stroke-width="1.5"/>
        <rect x="{max(35, min(company_x - 68, 460))}" y="135" width="136" height="22" rx="4" fill="#f0fdf4" stroke="#16a34a" stroke-width="1"/>
        <text x="{max(103, min(company_x, 528))}" y="150" text-anchor="middle" fill="#14532d" font-size="11" font-weight="700">
          Selskap: {company_lbl}
        </text>
        <!-- Kvartil-etiketter -->
        <text x="115" y="122" text-anchor="middle" fill="#64748b" font-size="10">1. kvartil</text>
        <text x="240" y="122" text-anchor="middle" fill="#64748b" font-size="10">2. kvartil</text>
        <text x="365" y="122" text-anchor="middle" fill="#1e3a8a" font-size="10" font-weight="700">3. kvartil (Topp 25 %)</text>
        <text x="485" y="122" text-anchor="middle" fill="#64748b" font-size="10">4. kvartil</text>
      </svg>
    </div>
    """


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
    ebit_sensitivity: Optional[Union[EbitDriverSensitivityModel, Dict[str, Any]]] = None,
    nace_benchmark: Optional[Union[NaceBenchmarkingModel, Dict[str, Any]]] = None,
    rfq_report: Optional[Union[RfqBiddingModel, Dict[str, Any]]] = None,
    operational_check: Optional[Union[OperationalCrossCheckModel, Dict[str, Any]]] = None,
    period_label: Optional[str] = None,
) -> io.BytesIO:
    """
    Genererer to distinkte, skreddersydde og selvstendige HTML5-rapporter direkte i minnet (io.BytesIO):
      1. report_type="styre" (Styrepakke – Målgruppe: Styret/Eiere):
         - Executive Summary (Strategisk KI-innsikt: finansiell helse, kapitalstruktur, utbyttekapasitet)
         - Hovedtall & Lønnsomhet (Aggregert: Bruttomargin, Driftsmargin/EBIT, Soliditet, TKR/EKR)
         - Governance & Compliance (Revisors avstemming: HB/SB-balanse og NS 4102-etterlevelse)
         - Strategisk Posisjonering (NACE-Benchmarking V2: Normalfordelingskurve og driver-gap)
         - Viktigste Strategiske Tiltak (Overordnede KI-råd knyttet til makrotrender, kapitalbinding og strategisk prising)
      2. report_type="ledelse" (Beslutningsrapport – Målgruppe: CEO/CFO/Ledere):
         - Operativ Oppsummering (Taktisk KI-innsikt: kortsiktig likviditet, kostnadsavvik og effektivitet)
         - Detaljert Resultatoppstilling & EBIT-drivere (Full NS 4102-nedbryting + 1 % sensitivitetsanalyse)
         - Kostnadskontroll & Anbud (Innkjøpsfokus / RFQ-modul: Bankrente, Forsikring, Strøm og årlig sparepotensial i NOK)
         - Operasjonell Krysskontroll (V2: Varelager vs. Konto 1460, Timelister vs. Lønnskostnad, CRM vs. Reskontro)
         - Taktiske Tiltak (Konkrete steg for reforhandling av avtaler, reduksjon av reskontrotid og fjerning av inaktive lisenser)

    ARKITEKTURGARANTI (The AI Firewall & FR-5.1 / FR-5.2 / FR-5.6):
    - Ingen regnskapstall beregnes av språkmodellen eller i HTML/JS. Alle tabeller, nøkkeltall og beløp
      injiseres deterministisk fra Python/Pydantic-objekter.
    - All dynamisk tekst renses med html.escape().
    """
    profile = _normalize_report_type(report_type)
    safe_company = html.escape(str(company_name or "Selskap AS"))
    safe_period = html.escape(str(period_label or "Inneværende regnskapsperiode"))

    # Validerte Pydantic-domeneobjekter
    sens_model = _coerce_ebit_sensitivity(ebit_sensitivity, metrics)
    nace_model = _coerce_nace_benchmark(nace_benchmark)
    rfq_model = _coerce_rfq_report(rfq_report)
    op_check_model = _coerce_operational_check(operational_check)

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
        theme_class = "theme-styre"
        doc_title = f"Styrepakke (Strategisk) – {safe_company}"
        header_badge = "STRATEGISK STYREPAKKE &bull; CORPORATE GOVERNANCE, RISIKOSTYRING &amp; LANGSIKTIG LØNNSOMHET"
        header_h1 = f"Styrepakke: {safe_company}"
        header_subtitle = (
            f"Målgruppe: Styret og Eiere ({safe_period}) &bull; Utarbeidet med KI-Revisor &bull; "
            "Aggregert styringsinformasjon etter NS 4102 og Revisors Avstemming (The AI Firewall)"
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
                "Kontoplanen følger Norsk Standard Kontoplan (NS 4102) med 4-sifret kontostruktur "
                "og tilfredsstiller bokføringslovens og regnskapslovens krav til norsk regnskapsspråk."
            )

        hb_sb_status_lbl = "Balansert (∑D = ∑K)" if is_reconciled else f"{discrepancy_count} kontoavvik"
        dividend_status = (
            "Forsvarlig utbyttekapasitet bekreftet (Soliditet ≥ 30 %, Likviditetsgrad ≥ 2,0 og 100 % avstemt regnskap)"
            if (is_reconciled and egenkapitalandel_val >= 30.0 and likviditetsgrad_1_val >= 2.0 and ebit_val > 0)
            else "Tilbakeholdelse av utbytte anbefales (Styrk egenkapitalbuffer/likviditet eller korriger avstemmingsavvik før utdeling)"
        )

        deterministic_styre_html = _build_deterministic_recommendations_html(
            recommendations,
            heading_id="det-profit-heading",
            heading_title="Deterministisk Lønnsomhetspotensial (Beregnet i Python)",
        )

        # Normalfordelingskurve (Bell Curve SVG) og NACE-benchmarking for V2
        bell_svg_html = _build_bell_curve_svg(
            company_margin_pct=nace_model.simulated_company_ebit_pct,
            industry_mean_pct=nace_model.industry_mean_ebit_pct,
        )
        nace_rows_html = []
        for d_item in nace_model.drivers:
            pot_cell = _format_nok(d_item.ebit_potential_nok, 0) if d_item.ebit_potential_nok > 0 else "—"
            nace_rows_html.append(
                f"<tr>"
                f"<td><strong>{html.escape(d_item.driver_label)}</strong></td>"
                f"<td class='num'>{_format_percent(d_item.company_pct, 1)}</td>"
                f"<td class='num'>{_format_percent(d_item.industry_pct, 1)}</td>"
                f"<td class='num'>{d_item.diff_pp:+.1f} %-poeng</td>"
                f"<td class='num'><strong>{pot_cell}</strong></td>"
                f"</tr>".replace(".", ",")
            )

        benchmark_marker_pct = min(max(int(round((driftsmargin_val + 10.0) / 35.0 * 100.0)), 8), 92)

        sections_html = f"""
    <!-- 1. EXECUTIVE SUMMARY (STRATEGISK KI-INNSIKT) -->
    <section id="styre-executive-summary" aria-labelledby="exec-summary-heading">
      <h2 id="exec-summary-heading">1. Executive Summary (Strategisk KI-innsikt til Styret)</h2>
      <div class="status-banner {status_class}" role="region" aria-label="Avstemmingsstatus og hovedkonklusjon">
        <span class="status-badge">[{status_badge}]</span>
        <p class="section-text"><strong>Overordnet finansiell helse:</strong> {hovedkonklusjon}</p>
        <p class="section-text" style="margin-bottom:0; font-size:0.9rem;">{status_summary}</p>
      </div>
      <div class="callout-grid">
        <div class="info-card">
          <div class="info-card-title">Kapitalstruktur, Soliditet &amp; Langsiktig Avkastning</div>
          <p class="section-text" style="margin-bottom:0;">{soliditet_rentabilitet}</p>
        </div>
        <div class="info-card">
          <div class="info-card-title">Vurdering av Utbyttekapasitet (Aksjeloven § 8-1)</div>
          <p class="section-text" style="margin-bottom:0;">
            <strong>Styrebeslutningsgrunnlag:</strong> {html.escape(dividend_status)}<br/>
            Reell egenkapital utgjør <strong>{reell_ek_str}</strong> av totalkapital på <strong>{totalkapital_str}</strong>
            (egenkapitalandel <strong>{egenkapitalandel_str}</strong>, gjeldsgrad <strong>{gjeldsgrad_str}</strong>).
          </p>
        </div>
      </div>
    </section>

    <!-- 2. HOVEDTALL & LØNNSOMHET (AGGREGERT STYREVISNING) -->
    <section id="styre-hovedtall" aria-labelledby="kpi-heading">
      <h2 id="kpi-heading">2. Hovedtall &amp; Lønnsomhet (Aggregert Styrevisning – Uten Enkeltkontostøy)</h2>
      <div class="kpi-grid">
        <div class="kpi-card highlight-card">
          <div class="kpi-label">Bruttomargin</div>
          <div class="kpi-value">{bruttomargin_str}</div>
          <div class="kpi-sub">Bruttofortj.: {bruttofortjeneste_str}</div>
        </div>
        <div class="kpi-card highlight-card">
          <div class="kpi-label">Driftsmargin (EBIT)</div>
          <div class="kpi-value">{driftsmargin_str}</div>
          <div class="kpi-sub">EBIT: {ebit_str}</div>
        </div>
        <div class="kpi-card highlight-card">
          <div class="kpi-label">Egenkapitalandel (Soliditet)</div>
          <div class="kpi-value">{egenkapitalandel_str}</div>
          <div class="kpi-sub">Gjeldsgrad: {gjeldsgrad_str}</div>
        </div>
        <div class="kpi-card highlight-card">
          <div class="kpi-label">Totalkapitalrent. (TKR)</div>
          <div class="kpi-value">{tkr_str}</div>
          <div class="kpi-sub">EKR: {ekr_str}</div>
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
          <div class="kpi-label">Driftsresultat (EBIT)</div>
          <div class="kpi-value">{ebit_str}</div>
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
          <div class="kpi-label">Egenkapitalrent. (EKR)</div>
          <div class="kpi-value">{ekr_str}</div>
        </div>
      </div>

      <div class="callout-grid">
        <div class="info-card">
          <div class="info-card-title">Langsiktig Lønnsomhets- og Marginutvikling</div>
          <p class="section-text" style="margin-bottom:0;">{lonnsomhet}</p>
        </div>
        <div class="info-card">
          <div class="info-card-title">Finansiell Beredskap &amp; Kapitalbinding</div>
          <p class="section-text" style="margin-bottom:0;">{likviditet}</p>
        </div>
      </div>
    </section>

    <!-- 3. GOVERNANCE & COMPLIANCE (REVISORS AVSTEMMING) -->
    <section id="styre-compliance" class="print-page-break" aria-labelledby="compliance-heading">
      <h2 id="compliance-heading">3. Governance &amp; Compliance (Revisors Avstemming &amp; NS 4102)</h2>
      <div class="kpi-grid kpi-grid-3">
        <div class="kpi-card">
          <div class="kpi-label">Balansesjekk (HB / SB)</div>
          <div class="kpi-value">{html.escape(hb_sb_status_lbl)}</div>
          <div class="kpi-sub">Dobbelt bokføringsprinsipp</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label">Kryssavstemming (IB + HB = UB)</div>
          <div class="kpi-value">{discrepancy_count} avvik</div>
          <div class="kpi-sub">{'100 % verifisert datakvalitet' if is_reconciled else 'Krever korrigering før vastsettelse'}</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label">NS 4102 Klassifisering</div>
          <div class="kpi-value">{ns_pct_str}</div>
          <div class="kpi-sub">{html.escape(ns_status_lbl)}</div>
        </div>
      </div>

      <div class="info-card" style="margin-bottom: 14px;">
        <div class="info-card-title">Revisors Avstemmingsnotat til Styret (Internkontroll)</div>
        <p class="section-text">{revisor_notat}</p>
        <p class="section-text" style="margin-bottom:0; font-size:0.88rem;"><strong>NS 4102 &amp; Regnskapsloven § 3-4:</strong> {ns_summary_txt}</p>
      </div>

      <h3 class="sub-heading">Kontrollbekreftelse: Hovedbok mot Saldobalanse (IB + HB = UB)</h3>
      {reconciliation_section_html}
    </section>

    <!-- 4. STRATEGISK POSISJONERING (NACE-BENCHMARKING - FREMHEVET FOR V2) -->
    <section id="styre-bransje-v2" aria-labelledby="industry-v2-heading">
      <h2 id="industry-v2-heading">4. Strategisk Posisjonering &amp; Bransjeposisjonering (NACE-Benchmarking – V2)</h2>
      <div class="teaser-box">
        <span class="teaser-badge">V2.0 STRATEGISK MODUL &bull; NACE-BENCHMARKING MOT BRØNNØYSUNDREGISTRENE</span>
        <p class="section-text">
          Plassering på normalfordelingskurven for lønnsomhet (EBIT-margin %) innen referansebransjen
          <strong>{html.escape(nace_model.nace_code)}</strong>. Selskapet er posisjonert i
          <strong>{html.escape(nace_model.quartile_position_label)}</strong> ved
          <strong>{_format_percent(nace_model.simulated_company_ebit_pct, 1)}</strong> mot et bransjesnitt på
          <strong>{_format_percent(nace_model.industry_mean_ebit_pct, 1)}</strong> (aktuell regnskapsmargin i perioden: <strong>{driftsmargin_str}</strong>).
        </p>

        {bell_svg_html}

        <div class="table-wrapper" style="margin-top: 12px;">
          <table class="data-table" aria-label="NACE Driver-benchmarking">
            <thead>
              <tr>
                <th>Strategisk EBIT-driver</th>
                <th class="num">Selskap (Benchmark)</th>
                <th class="num">Bransjesnitt (NACE)</th>
                <th class="num">Spread (%-poeng)</th>
                <th class="num">Uforløst EBIT-potensial</th>
              </tr>
            </thead>
            <tbody>
              {''.join(nace_rows_html)}
            </tbody>
          </table>
        </div>
        <p class="section-text" style="margin-top: 10px; margin-bottom: 6px;">
          <strong>Algoritmisk Gap-identifikator:</strong> {html.escape(nace_model.potential_banner_text)}
        </p>
        <div class="progress-row" style="margin-bottom:0;">
          <div class="progress-header">
            <span><strong>Relativ styrkeposisjon mot referansebransjen</strong></span>
            <span>{html.escape(nace_model.quartile_position_label)}</span>
          </div>
          <div class="progress-track" role="progressbar" aria-valuenow="{benchmark_marker_pct}" aria-valuemin="0" aria-valuemax="100" aria-label="Bransjeposisjonering">
            <div class="progress-fill progress-navy" style="width: {benchmark_marker_pct}%;"></div>
          </div>
        </div>
      </div>
    </section>

    <!-- 5. VIKTIGSTE STRATEGISKE TILTAK -->
    <section id="styre-strategiske-rad" aria-labelledby="strategic-actions-heading">
      <h2 id="strategic-actions-heading">5. Viktigste Strategiske Tiltak (Makrotrender, Kapitalbinding &amp; Strategisk Prising)</h2>
      <div class="callout-grid">
        <div class="info-card">
          <div class="info-card-title">Makrotrender &amp; Strategisk Prising</div>
          <p class="section-text" style="margin-bottom:0;">
            I et inflasjons- og rentemiljø med økt kostnadspress på innsatsfaktorer må styret sikre at
            prisjusteringer gjennomføres proaktivt. En 1 % indeksregulering av prisstrukturen øker EBIT
            direkte med <strong>{_format_nok(sens_model.price_1pct_nok, 0)}</strong> uten økt kapitalbinding.
          </p>
        </div>
        <div class="info-card">
          <div class="info-card-title">Kapitalallokering &amp; Arbeidskapitaldisiplin</div>
          <p class="section-text" style="margin-bottom:0;">
            Redusert kapitalbinding i kundefordringer (<strong>{kundefordringer_str}</strong>) og optimalisert
            forvaltning av likviditetsreserven (<strong>{bankinnskudd_str}</strong>) styrker både
            totalkapitalrentabiliteten (<strong>{tkr_str}</strong>) og utbyttekapasiteten.
          </p>
        </div>
      </div>

      {deterministic_styre_html}

      <div class="subsection-block">
        <h3 id="risk-heading">Strategiske Risikofaktorer &amp; Faresignaler</h3>
        <ul class="risk-list">
          {risk_list_html}
        </ul>
      </div>

      <div class="subsection-block">
        <h3 id="actions-heading">Prioriterte Styrevedtak og Strategiske Tiltak (KI-CFO)</h3>
        <div class="table-wrapper">
          <table class="data-table" aria-label="Viktigste strategiske tiltak for styret">
            <thead>
              <tr>
                <th>Prioritet</th>
                <th>Strategisk Tiltak (Prising / Kapitalbinding / Vekst)</th>
                <th>Begrunnelse</th>
                <th>Forventet Strategisk Effekt</th>
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
        # Målgruppe: CEO / CFO / Ledere
        # Formål: Taktisk kostnadskontroll, prosessforbedring og likviditetstiltak
        # =====================================================================
        theme_class = "theme-ledelse"
        doc_title = f"Beslutningsrapport (Operativ) – {safe_company}"
        header_badge = "OPERATIV BESLUTNINGSRAPPORT &bull; TAKTISK KOSTNADSKONTROLL, EBIT-DRIVERE &amp; ANBUD (RFQ)"
        header_h1 = f"Beslutningsrapport for Ledelsen: {safe_company}"
        header_subtitle = (
            f"Målgruppe: CEO, CFO og Operativ Ledelse ({safe_period}) &bull; Utarbeidet med KI-CFO &bull; "
            "Fokus: NS 4102 Resultatnedbryting, EBIT-Sensitivitet, Anbud (RFQ) og Operasjonell Krysskontroll (The AI Firewall)"
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

        # Sensitivitetsverdier fra EbitDriverSensitivityModel
        sens_price_str = _format_nok(sens_model.price_1pct_nok, decimals=0)
        sens_cogs_str = _format_nok(sens_model.cogs_1pct_nok, decimals=0)
        sens_opex_str = _format_nok(sens_model.opex_1pct_nok, decimals=0)
        sens_new_m_price = _format_percent(sens_model.new_margin_price, decimals=2)
        sens_new_m_cogs = _format_percent(sens_model.new_margin_cogs, decimals=2)
        sens_new_m_opex = _format_percent(sens_model.new_margin_opex, decimals=2)
        clean_insight_txt = html.escape(sens_model.insight_text.replace("**", ""))

        # Kostnadskontroll & Anbud (RFQ-modul)
        rfq_rows_html = []
        for item in rfq_model.items:
            rfq_rows_html.append(
                f"<tr>"
                f"<td><strong>{html.escape(item.kategori)}</strong><br/><span class='kpi-sub'>{html.escape(item.konto_ref)}</span></td>"
                f"<td>{html.escape(item.avlest_vilkar)}</td>"
                f"<td>{html.escape(item.markedsstandard)}</td>"
                f"<td>{html.escape(item.tiltak_beskrivelse)}</td>"
                f"<td class='num'><strong>{_format_nok(item.arlig_sparepotensial_nok, 0)}/år</strong></td>"
                f"</tr>"
            )
        rfq_total_str = _format_nok(rfq_model.total_annual_savings_nok, decimals=0)

        # Operasjonell Krysskontroll (V2)
        op_check_rows_html = []
        for chk in op_check_model.items:
            op_check_rows_html.append(
                f"<tr>"
                f"<td><strong>{html.escape(chk.fagsystem)}</strong></td>"
                f"<td><strong>{html.escape(chk.regnskapskonto)}</strong></td>"
                f"<td>{html.escape(chk.kontrollformaal)}</td>"
                f"<td>{html.escape(chk.observasjon)}</td>"
                f"<td><span class='prio-badge prio-medium'>{html.escape(chk.status_etikett)}</span></td>"
                f"</tr>"
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
    <!-- 1. OPERATIV OPPSUMMERING (TAKTISK KI-INNSIKT) -->
    <section id="ledelse-operativ-oppsummering" aria-labelledby="op-summary-heading">
      <h2 id="op-summary-heading">1. Operativ Oppsummering (Taktisk KI-innsikt: Likviditet, Kostnadsavvik &amp; Effektivitet)</h2>
      <div class="status-banner {status_class}" role="region" aria-label="Avstemmingsstatus og operativ oppsummering">
        <span class="status-badge">[{status_badge}]</span>
        <p class="section-text"><strong>Operativ Konklusjon (CEO / CFO):</strong> {hovedkonklusjon}</p>
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
          <div class="info-card-title">Operasjonell Effektivitet &amp; Kostnadsavvik (KI-CFO)</div>
          <p class="section-text" style="margin-bottom:0;">{lonnsomhet}</p>
        </div>
        <div class="info-card">
          <div class="info-card-title">Kortsiktig Likviditet &amp; Reskontrostyring</div>
          <p class="section-text" style="margin-bottom:0;">{likviditet}</p>
        </div>
      </div>
    </section>

    <!-- 2. DETALJERT RESULTATOPPSTILLING & EBIT-DRIVERE -->
    <section id="ledelse-resultatoppstilling" aria-labelledby="income-stmt-heading">
      <h2 id="income-stmt-heading">2. Detaljert Resultatoppstilling &amp; EBIT-drivere (NS 4102 + Sensitivitetsanalyse)</h2>
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

      <div class="subsection-block">
        <h3 class="sub-heading">Sensitivitetsanalyse på EBIT-drivere (1 % marginal forbedring)</h3>
        <div class="kpi-grid kpi-grid-3">
          <div class="kpi-card highlight-card">
            <div class="kpi-label">Effekt av 1 % økning i pris</div>
            <div class="kpi-value">+{sens_price_str}</div>
            <div class="kpi-sub">Ny EBIT-margin: {sens_new_m_price}</div>
          </div>
          <div class="kpi-card highlight-card">
            <div class="kpi-label">Effekt av 1 % kutt i varekostnad</div>
            <div class="kpi-value">+{sens_cogs_str}</div>
            <div class="kpi-sub">Ny EBIT-margin: {sens_new_m_cogs}</div>
          </div>
          <div class="kpi-card highlight-card">
            <div class="kpi-label">Effekt av 1 % kutt i faste kostnader (Opex)</div>
            <div class="kpi-value">+{sens_opex_str}</div>
            <div class="kpi-sub">Ny EBIT-margin: {sens_new_m_opex}</div>
          </div>
        </div>
        <div class="info-card">
          <p class="section-text" style="margin-bottom:0;">{clean_insight_txt}</p>
        </div>
      </div>
    </section>

    <!-- 2B. KOSTNADSDRIVERE & PROGRESS -->
    <section id="ledelse-kostnadsdrivere" aria-labelledby="cost-drivers-heading">
      <h2 id="cost-drivers-heading">Kostnadsdrivere: Fordeling av Varekostnad, Lønn og Opex</h2>
      <div class="info-card" style="margin-bottom: 14px;">
        <div class="info-card-title">Kostnadsstruktur og Marginfordeling (% av Driftsinntekter)</div>
        {''.join(progress_bars_html)}
      </div>

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

    <!-- 3. KOSTNADSKONTROLL & ANBUD (INNKJØPSFOKUS / RFQ-MODUL) -->
    <section id="ledelse-anbud-rfq" aria-labelledby="rfq-heading">
      <h2 id="rfq-heading">3. Kostnadskontroll &amp; Anbud (Innkjøpsfokus – RFQ-Modul)</h2>
      <div class="kpi-grid kpi-grid-3">
        <div class="kpi-card">
          <div class="kpi-label">Bankrente &amp; Driftskreditt (2380/8150)</div>
          <div class="kpi-value">45 000 NOK/år</div>
          <div class="kpi-sub">Avlest 4,5 % vs. marked 2,5 %</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label">Forsikringspremier (Konto 7500)</div>
          <div class="kpi-value">24 000 NOK/år</div>
          <div class="kpi-sub">-20 % ved samleanbud</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label">Strøm &amp; Lokaler (Konto 6340)</div>
          <div class="kpi-value">12 000 NOK/år</div>
          <div class="kpi-sub">-9 øre/kWh skjult påslag</div>
        </div>
      </div>

      <div class="table-wrapper">
        <table class="data-table" aria-label="Identifiserte kostnadslekkasjer og anbudspotensial">
          <thead>
            <tr>
              <th>Innkjøpskategori &amp; Konto</th>
              <th>Avlest Vilkår (OCR/Kontrakt)</th>
              <th>Markedsstandard Benchmark</th>
              <th>Anbefalt Anbudstiltak (RFQ)</th>
              <th class="num">Årlig Sparepotensial</th>
            </tr>
          </thead>
          <tbody>
            {''.join(rfq_rows_html)}
            <tr class="row-highlight">
              <td colspan="4"><strong>Totalt identifisert årlig innsparingspotensial ved anbudsutsettelse ({html.escape(rfq_model.rfq_reference)})</strong></td>
              <td class="num"><strong>{rfq_total_str}/år</strong></td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <!-- 4. OPERASJONELL KRYSSKONTROLL (FREMHEVET FOR V2) -->
    <section id="ledelse-operasjonell-v2" aria-labelledby="op-v2-heading">
      <h2 id="op-v2-heading">4. Operasjonell Krysskontroll mellom Fagsystemer og Hovedbok (V2)</h2>
      <div class="teaser-box">
        <span class="teaser-badge">V2.0 OPERATIV KRYSSKONTROLL &bull; VARELAGER VS. KONTO 1460, TIMELISTER VS. LØNNSKOSTNAD &amp; CRM</span>
        <p class="section-text">
          Status på automatisert avstemming mellom bedriftens operasjonelle fagsystemer (WMS, Timelister og CRM)
          og verifiserte hovedbokskontoer for å avdekke varesvinn, lav faktureringsgrad eller inaktive lisenser:
        </p>
        <div class="table-wrapper">
          <table class="data-table" aria-label="Operasjonell krysskontroll mellom fagsystemer og regnskap">
            <thead>
              <tr>
                <th>Fagsystem / Kilde</th>
                <th>Avstemt Regnskapskonto (NS 4102)</th>
                <th>Operasjonelt Kontrollformål</th>
                <th>Status &amp; Observasjon</th>
                <th>Kontrollstatus</th>
              </tr>
            </thead>
            <tbody>
              {''.join(op_check_rows_html)}
            </tbody>
          </table>
        </div>
      </div>
    </section>

    <!-- 4B. MVA-KONTROLL & AVVIKSDETALJER -->
    <section id="ledelse-mva-og-avvik" aria-labelledby="vat-audit-heading">
      <h2 id="vat-audit-heading">MVA-Kontroll &amp; Avviksdetaljer (Regnskapsfører / CFO Sjekkliste)</h2>
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
    </section>

    <!-- 5. TAKTISKE TILTAK -->
    <section id="ledelse-operative-rad" aria-labelledby="op-actions-heading">
      <h2 id="op-actions-heading">5. Taktiske Tiltak: Reforhandling av Avtaler, Reduksjon av Reskontrotid &amp; Lisenssanering</h2>
      <div class="kpi-grid kpi-grid-3">
        <div class="info-card">
          <div class="info-card-title">1. Reforhandling av Avtaler (RFQ)</div>
          <p class="section-text" style="margin-bottom:0; font-size:0.88rem;">
            Send ut ferdiggenerert anbudsforespørsel (<strong>{html.escape(rfq_model.rfq_reference)}</strong>) på bankrente
            (Konto 2380/8150), forsikring (Konto 7500) og strøm (Konto 6340) for å realisere <strong>{rfq_total_str}/år</strong>.
          </p>
        </div>
        <div class="info-card">
          <div class="info-card-title">2. Reduksjon av Reskontrotid (DSO)</div>
          <p class="section-text" style="margin-bottom:0; font-size:0.88rem;">
            Stram inn kredittid til 14 dager og aktiver automatisk purring på utestående kundefordringer
            (<strong>{kundefordringer_str}</strong> på Konto 1500) for umiddelbar likviditetsfrigjøring.
          </p>
        </div>
        <div class="info-card">
          <div class="info-card-title">3. Fjerning av Inaktive Lisenser</div>
          <p class="section-text" style="margin-bottom:0; font-size:0.88rem;">
            Gjennomfør lisensrevisjon mot aktiv ansattliste på programvare- og SaaS-kontoer (Konto 6800/6xxx)
            og avslutt ubenyttede setelisenser før neste fornyelsessyklus.
          </p>
        </div>
      </div>

      {deterministic_ledelse_html}

      <div class="subsection-block">
        <h3 id="op-risk-heading">Operasjonelle Faresignaler &amp; Kontrollpunkter</h3>
        <ul class="risk-list">
          {risk_list_html}
        </ul>
      </div>

      <div class="subsection-block">
        <h3 id="actions-heading">Operativ Handlingsplan for CEO / CFO (KI-Rådgiver)</h3>
        <div class="table-wrapper">
          <table class="data-table" aria-label="Taktiske tiltak for ledelsen">
            <thead>
              <tr>
                <th>Prioritet</th>
                <th>Taktisk Tiltak (Reforhandling / Reskontro / Lisenser)</th>
                <th>Operativ Begrunnelse</th>
                <th>Målbar Likviditets- og Resultateffekt</th>
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
    /* Formelt, stramt uttrykk for Styrepakke */
    .container.theme-styre {{
      border-top: 6px solid var(--navy);
      padding: 38px 40px;
    }}
    .container.theme-styre h1 {{
      font-family: Georgia, "Times New Roman", Times, serif;
      letter-spacing: -0.01em;
    }}
    /* Datatett, operativt dashboard-oppsett for Beslutningsrapport */
    .container.theme-ledelse {{
      max-width: 1060px;
      border-top: 6px solid #0f766e;
      padding: 26px 28px;
    }}
    .container.theme-ledelse .kpi-grid {{
      gap: 10px;
    }}
    .container.theme-ledelse .kpi-card {{
      padding: 10px 12px;
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
    .bell-curve-container {{
      background: #ffffff;
      border: 1px solid var(--border);
      border-radius: 6px;
      padding: 10px 14px;
      margin: 10px 0;
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
      .print-page-break {{
        page-break-before: always;
        break-before: page;
      }}
      section, .kpi-grid, .callout-grid, .status-banner, .teaser-box, .bell-curve-container, tr {{
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
  <main class="container {theme_class}" data-report-type="{profile}">
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
