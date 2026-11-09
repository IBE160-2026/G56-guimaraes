# Bransjesammenligning (NACE) (v2.) og EBIT-drivermodell

## 2026-11-09 kl. 20:47 — turnaround1207

### Oppgave
1. Utvide Streamlit-applikasjonen (`src/app.py`) med «🏢 5. Bransjesammenligning (v2.)» på 5. plass i sidepanelnavigasjonen (`st.sidebar.radio`) og bygge en statisk v2.0-teaser (`render_industry_benchmarking_mockup()`).
2. Introdusere en deterministisk EBIT-drivermodell over *The AI Firewall*:
   - Oppdatere «📊 3. Finansiell Analyse & HB» (`src/views/financial_analysis.py`) med seksjonen `🔍 Analyse av EBIT-drivere` (sensitivitetsanalyse for 1 % økning i pris, 1 % reduksjon i varekostnad, og 1 % reduksjon i faste kostnader / Opex, samt forklarende CFO-innsikt).
   - Oppdatere «🏢 5. Bransjesammenligning (v2.)» (`src/views/industry_benchmarking.py`) med konseptkort for driver-benchmarking mot NACE (Bruttomargin, Lønnskostnad/Omsetning, Opex/Omsetning) og en algoritmisk potensial-identifikator som fremhever driveren med størst ugunstig avvik og beregner EBIT-effekten i NOK.

### Plan
- Oppdatere `NAV_OPTIONS` og ruting i `src/app.py` til 7 navigasjonssteg (`📂 1.` til `🗄️ 7.`).
- Implementere deterministiske beregningsfunksjoner i `src/ledger_analytics.py`:
  - `calculate_ebit_driver_sensitivity(metrics)` for 1 % sensitivitetsanalyse og operasjonell giring.
  - `calculate_nace_driver_benchmarking(revenue_nok)` for Pandas-basert gap-analyse mot bransjesnittet og identifikasjon av største forbedringspotensial.
- Integrere UI-seksjonene i `src/views/financial_analysis.py` og `src/views/industry_benchmarking.py` kun med native Streamlit-komponenter (uten `unsafe_allow_html`).
- Utvide testsuiten i `tests/test_ledger_analytics.py` og `tests/test_app_ui.py`.

### Resultat
- Opprettet `calculate_ebit_driver_sensitivity` og `calculate_nace_driver_benchmarking` i `src/ledger_analytics.py`.
- Utvidet `src/views/financial_analysis.py` med `st.subheader("🔍 Analyse av EBIT-drivere")`, tre `st.metric`-kort i `st.columns(3)` og dynamisk `st.info()` med CFO-innsikt om multiplikatoreffekten av pris kontra varekostnad og Opex.
- Utvidet `src/views/industry_benchmarking.py` med `🎯 Avviksanalyse på EBIT-drivere (Driver-benchmarking mot NACE)`, sammenligningskort for *Bruttomargin vs. Bransje*, *Lønnskostnad/Omsetning vs. Bransje* og *Opex/Omsetning vs. Bransje*, oversiktstabell (`st.dataframe`), og fremhevet `st.success()`-banner:
  `🎯 Største forbedringspotensial: Din varekostnad er 4,5 prosentpoeng høyere enn bransjesnittet. Ved å lukke dette gapet vil EBIT øke med 54 000 NOK.`
- Alle 47 enhetstester i testsuiten passerer uten feil eller advarsler.

### Åpne punkter
- Ingen.
