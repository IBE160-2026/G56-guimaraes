# Dynamiske Rapportprofiler: Styrepakke og Beslutningsrapport

## 2026-11-09 kl. 20:38 — turnaround1207

### Oppgave
Oppgradere rapport- og eksportmotoren slik at brukeren i «💡 6. KI-Rådgiver & Eksport» kan velge mellom å generere **Styrepakke (Strategisk)** for styret og/eller **Beslutningsrapport (Operativ)** for ledelsen via avkrysningsbokser (`st.checkbox`), og refaktorere `src/html_report.py` (`generate_management_html`) til å støtte betinget rendering (`report_type="styre" | "ledelse"`) med skreddersydde innholdsprofiler som gjenspeiler hele verdikjeden.

### Plan
- Oppdatere eksportsteget i `src/views/ai_advisor_and_export.py` (og tilstandsdefinisjoner i `src/app.py` samt historikkeksport i `src/views/history_and_trends.py`) med to `st.checkbox`-kontroller: `[x] Generer Styrepakke (Strategisk)` og `[ ] Generer Beslutningsrapport (Operativ)`, samt dynamiske nedlastingsknapper for HTML og PDF.
- Refaktorere `generate_management_html` i `src/html_report.py` til å ta inn `report_type="styre" | "ledelse"` og betingede `<section>`-blokker for de to målgruppene.
- Utvide `generate_management_pdf` i `src/pdf_generator.py` til også å støtte `report_type="styre" | "ledelse"`.
- Legge til enhetstester i `tests/test_reporting.py` og `tests/test_app_ui.py` og kjøre full `pytest`-verifisering.

### Resultat
- Oppdatert `src/views/ai_advisor_and_export.py` (og `src/app.py` / `src/views/history_and_trends.py`):
  - Lagt til `st.checkbox("Generer Styrepakke (Strategisk)", value=True)` og `st.checkbox("Generer Beslutningsrapport (Operativ)", value=False)`.
  - Genererer og viser separate, målrettede nedlastingsknapper (HTML og PDF) i minnet (`io.BytesIO`) for én eller begge rapportprofiler basert på brukerens valg.
- Refaktorert `src/html_report.py` (`generate_management_html`):
  - Støtter `report_type="styre"` (standard) og `report_type="ledelse"` med validering og betinget rendering av `<section>`-elementer.
  - **Styrepakke (`report_type="styre"`):** (1) Executive Summary med revisjonsstatus og utbyttekapasitetsvurdering, (2) Hovedtall & Lønnsomhet (EBIT, Bruttomargin, Soliditet, TKR/EKR), (3) Revisors avstemming (Compliance: HB/SB-balanse og NS 4102-klassifisering), (4) Bransjeposisjonering (V2-teaser med NACE-sammenligning og kvartilindikator), og (5) Strategiske KI-råd.
  - **Beslutningsrapport (`report_type="ledelse"`):** (1) Operativ Oppsummering med drifts- og arbeidskapitalfokus, (2) Detaljert Resultatoppstilling etter NS 4102 med %-vise marginer, (3) Kostnadsdrivere (Varekostnad, Lønn, Opex med tilgjengelige CSS progress-bars `role="progressbar"` og kontospesifikasjon), (4) MVA & Avviksdetaljer for regnskapsfører/CFO, (5) Operasjonell Analyse (V2-teaser: krysskontroll mot timelister, varelager og CRM), og (6) Operative KI-råd for kostnadskutt, prising og reskontro-optimalisering.
  - Bevarer 100 % in-memory generering (`io.BytesIO`), Zero-Dependency HTML5/CSS3, WCAG 2.1 AA-kontrast, `@media print`-støtte og streng *The AI Firewall*-beskyttelse (ingen råbilag lekker til HTML).
- Utvidet `tests/test_reporting.py` og `tests/test_app_ui.py` – samtlige 47 tester i testsuiten passerer (`47 passed`).

### Åpne punkter
- Ingen.
