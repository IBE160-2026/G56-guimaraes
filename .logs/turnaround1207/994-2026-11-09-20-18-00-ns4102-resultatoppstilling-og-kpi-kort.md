# Visuell refaktorering av Finansiell Analyse: Resultatoppstilling etter NS 4102 og KPI-kort

## 2026-11-09 kl. 20:18 — turnaround1207

### Oppgave
Visuelt refaktorere steget `📊 3. Finansiell Analyse & HB` (`src/views/financial_analysis.py` og `src/app.py`) fra enkle stolpediagrammer til et enterprise-grade finansielt dashboard med hierarkisk **Resultatoppstilling etter NS 4102** (Oppgave 1) og et 2-kolonners KPI-panel for **Kostnadsstruktur (% av Driftsinntekter)** og **Lønnsomhetsindikatorer** (Oppgave 2), bygget utelukkende med native Streamlit og deterministiske data fra pipelinen (*The AI Firewall*).

### Plan
- Utvide `calculate_detailed_financial_metrics` i `src/compliance_engine.py` med deterministiske kostnadsandeler (`varekost_andel`, `opex_andel`, `driftskost_andel`).
- Implementere `build_ns4102_income_statement` og `evaluate_profitability_indicators` i `src/ledger_analytics.py` samt koble dem inn i `workspace` i `src/app.py`.
- Erstatte tidligere `st.bar_chart`-seksjon i `src/views/financial_analysis.py` med:
  1. Innrammet `📈 Resultatoppstilling etter NS 4102` med `Driftsmargin` uthevet øverst til høyre, kontospesifikasjoner fra SB/HB, fargekodede hovedlinjer (grønn inntekt, rød/negativ kostnad, fiolett bruttofortjeneste, blå/uthevet EBIT) og høyrejusterte beløp/prosenter.
  2. 2-kolonners layout under oppstillingen med **Kostnadsstruktur (% av Driftsinntekter)** (`st.progress`) til venstre og **Lønnsomhetsindikatorer** (2x2 rutenett + dynamisk `st.success`/`st.info`-oppsummering) til høyre.
- Utvide testsuiten i `tests/test_ledger_analytics.py` og `tests/test_app_ui.py` og verifisere med `pytest`.

### Resultat
- **Deterministisk motor (`src/compliance_engine.py`, `src/ledger_analytics.py`, `src/app.py`):**
  - Lagt til `build_ns4102_income_statement(sb_df, hb_df, metrics)` som aggregerer Klasse 3 (`1. Salgs- og driftsinntekter`), Klasse 4 (`2. Varekostnad`), `Bruttofortjeneste (Gross Profit)`, Klasse 5 (`3. Lønnskostnader & personalkostnader`), Klasse 6 & 7 (`4. Andre driftskostnader`), `Sum driftskostnader` og `Driftsresultat (EBIT)` med underliggende enkeltkontoer, beløp i NOK og `% av Inntekt`.
  - Lagt til `evaluate_profitability_indicators(metrics)` som beregner fremdriftsverdier (`0.0–1.0`) for kostnadsstruktur, nøkkeltall med vurderingstekster og kvartil-/marginoppsummering.
- **UI/UX i `src/views/financial_analysis.py`:**
  - Bygget **Resultatoppstilling etter NS 4102** i `st.container(border=True)` med `st.badge` for `Driftsmargin` øverst til høyre og kolonnebaserte rader uten bruk av rå HTML.
  - Bygget 2-kolonners seksjon under oppstillingen med **Kostnadsstruktur (% av Driftsinntekter)** (`st.progress` + venstre/høyrejusterte kolonner) og **Lønnsomhetsindikatorer** (2x2 rutenett med `st.columns(2)` for `Bruttomargin`, `Driftsmargin (EBIT)`, `Lønn / Omsetning` og `Opex / Omsetning`, samt dynamisk `st.success`/`st.info`-oppsummering nederst).
- **Verifisering:**
  - Kjørt full testsuite med `pytest`: **46 passed**.

### Åpne punkter
- Ingen.
