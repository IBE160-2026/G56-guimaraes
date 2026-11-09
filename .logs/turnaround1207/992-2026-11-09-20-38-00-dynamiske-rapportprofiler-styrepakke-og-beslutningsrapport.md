# Dynamiske Rapportprofiler: Styrepakke og Beslutningsrapport

## 2026-11-09 kl. 21:09 — turnaround1207

### Oppgave
Ferdigstille eksportmotoren i `src/html_report.py` (`generate_management_html`) og eksportsteget i `src/views/ai_advisor_and_export.py` slik at applikasjonen genererer to distinkte, skreddersydde HTML-rapporter basert på mottakerens informasjonsbehov (Corporate Governance vs. operativ ledelse): **Styrepakke** (`report_type="styre"`) og **Beslutningsrapport** (`report_type="ledelse"`), med Pydantic-domenemodeller for finansiell analyse, EBIT-drivere (1 % sensitivitet), revisors avstemming, NACE-benchmarking (normalfordelingskurve), anbudsforhandling (RFQ-modul) og operasjonell krysskontroll.

### Plan
- Definere og validere Pydantic-domenemodeller i `src/html_report.py` (`EbitDriverSensitivityModel`, `NaceBenchmarkingModel`, `RfqBiddingModel`, `OperationalCrossCheckModel`) og koble dem inn i `generate_management_html` og `src/views/ai_advisor_and_export.py`.
- Implementere betinget HTML/CSS-rendering for `report_type="styre"` (formelt uttrykk med `theme-styre`, sidebrytning for utskrift og innebygd SVG normalfordelingskurve for NACE-benchmarking) og `report_type="ledelse"` (datatett dashboard-uttrykk med `theme-ledelse`, 1 % EBIT-sensitivitetsanalyse, RFQ-sparepotensial på 81 000 NOK/år og operasjonell krysskontroll mot Konto 1460 / Timelister / CRM).
- Utvide testsuiten i `tests/test_reporting.py` og verifisere at alle 48 tester i `pytest` passerer.

### Resultat
- Utvidet `src/html_report.py` med Pydantic-domenemodellene `EbitDriverSensitivityModel`, `NaceBenchmarkingModel`, `RfqBiddingModel` og `OperationalCrossCheckModel`, samt betinget rendering i `generate_management_html`:
  - **Styrepakke (`report_type="styre"`, `theme-styre`):**
    1. *Executive Summary (Strategisk KI-innsikt):* Overordnet finansiell helse, kapitalstruktur og deterministisk utbyttekapasitetsvurdering (Aksjeloven § 8-1).
    2. *Hovedtall & Lønnsomhet:* Aggregert visning av Bruttomargin, Driftsmargin (EBIT), Egenkapitalandel (Soliditet) og Totalkapitalrentabilitet (TKR/EKR) uten enkeltkontostøy.
    3. *Governance & Compliance (Revisors avstemming):* Bekreftelse på HB/SB-balanse ($\sum D = \sum K$, $\text{IB} + \text{HB} = \text{UB}$) og NS 4102-klassifisering (med `.print-page-break` for utskrift).
    4. *Strategisk Posisjonering (NACE-Benchmarking V2):* Selvstendig inline SVG normalfordelingskurve (Bell Curve, 3. kvartil / Topp 25 % mot 6,0 % bransjesnitt) og driver-benchmarking med algoritmisk gap-identifikator (`54 000 NOK` EBIT-potensial).
    5. *Viktigste Strategiske Tiltak:* Overordnede KI-råd knyttet til makrotrender, kapitalbinding og strategisk prising.
  - **Beslutningsrapport (`report_type="ledelse"`, `theme-ledelse`):**
    1. *Operativ Oppsummering (Taktisk KI-innsikt):* Fokus på kortsiktig likviditet, kostnadsavvik og operasjonell effektivitet.
    2. *Detaljert Resultatoppstilling & EBIT-drivere:* Full NS 4102-nedbryting med %-marginer, kostnadsdrivere med `role="progressbar"` og deterministisk 1 % sensitivitetsanalyse (`+2 000 NOK` ved 1 % prisøkning, `+600 NOK` ved 1 % kutt i varekostnad, `+300 NOK` ved 1 % kutt i faste kostnader/Opex).
    3. *Kostnadskontroll & Anbud (Innkjøpsfokus / RFQ-modul):* Oversikt over kostnadslekkasjer på Bankrente (`45 000 NOK/år`), Forsikring (`24 000 NOK/år`) og Strøm (`12 000 NOK/år`) med samlet årlig sparepotensial på `81 000 NOK/år`.
    4. *Operasjonell Krysskontroll (V2):* Avstemmingsstatus mellom fagsystemer og hovedbok (**Varelager vs. Konto 1460**, **Timelister vs. Lønnskostnad**, **CRM/SaaS vs. Kundefordringer og Lisenser**), etterfulgt av MVA- og avvikssjekkliste.
    5. *Taktiske Tiltak:* Konkrete steg for reforhandling av avtaler (RFQ), reduksjon av reskontrotid (DSO) og fjerning av inaktive lisenser.
- Oppdatert `src/views/ai_advisor_and_export.py` og `tests/test_reporting.py` – alle 48 tester i `pytest` passerer (`48 passed`).

### Åpne punkter
- Ingen.
