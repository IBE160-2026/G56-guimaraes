# Revisors avstemming og omorganisering av sidepanel-navigasjon

## 2026-11-08 kl. 20:46 — turnaround1207

### Oppgave
Utvide Streamlit-applikasjonen (`src/app.py`) etter BMAD-metodikken med et nytt hovedsteg for revisjonskontroller (`🔎 2. Revisors avstemming`), omorganisere navigasjonen i sidepanelet med `st.sidebar.radio` til 6 steg (inkl. `💡 4. Operasjonell analyse (v2.)` og `🗄️ 6. Historikk & Trendanalyse`), og implementere deterministiske kontroller i Python/Pandas uten å endre *The AI Firewall* eller bruke `unsafe_allow_html`.

### Plan
- Avklare teknisk navigasjonskomponent (`st.sidebar.radio`) og håndtering av steg 4 (`Operasjonell analyse (v2.)`) samt steg 6 (`Historikk & Trendanalyse`).
- Utvide `src/compliance_engine.py` med deterministiske kontrollfunksjoner for MVA-samsvar på tvers av kontoer (`evaluate_vat_compliance`) og NS 4102 / norsk regnskapsspråk (`evaluate_ns4102_compliance`).
- Opprette `src/views/auditor_reconciliation.py` (`render_auditor_reconciliation`) med Seksjon A (Balansesjekk HB vs. SB, MVA-klassifisering på tvers av 2700/3000/4000-serien, og NS 4102 regnskapsspråk/gjenkjennelsesgrad) og Seksjon B (V2-teasere for Bilagstesting og Prosessgjennomgang med deaktiverte knapper).
- Opprette `src/views/operational_analysis.py` (`render_operational_analysis`) som V2-plassholder for steg 4, oppdatere `src/app.py` og øvrige visninger i `src/views/`, og verifisere med automatiserte pytest-tester.

### Resultat
- **Sidepanel-navigasjon (`src/app.py`):**
  - Implementert `st.sidebar.radio` med de 6 stegene: `📂 1. Opplasting & Kontroll`, `🔎 2. Revisors avstemming`, `📊 3. Finansiell Analyse & HB`, `💡 4. Operasjonell analyse (v2.)`, `⚙️ 5. KI-Rådgiver & Eksport` og `🗄️ 6. Historikk & Trendanalyse`.
  - Lagt til automatisk synkronisering av `sb_df`, `hb_df`, `vat_compliance` og `ns4102_compliance` i `st.session_state`.
- **Revisors avstemming (`src/views/auditor_reconciliation.py` og `src/compliance_engine.py`):**
  - **Seksjon A (Aktive systemkontroller V1):**
    1. *Balansesjekk (HB vs. SB):* Viser med `st.columns`, `st.metric` og `st.success`/`st.error` at Saldobalansen går i null ($\sum \text{Debet} - \sum \text{Kredit} = 0$, $\sum \text{UB} = 0$) og at $\text{IB} + \text{HB} = \text{UB}$ per konto.
    2. *MVA-klassifisering (`evaluate_vat_compliance`):* Kontrollerer logisk sammenheng mellom MVA-kontoer i 2700-serien (`270x`, `271x`, `274x`), salgsinntekter i 3000-serien og kostnadskontoer (`4xxx`/`6xxx`/`7xxx`), samt MVA-splitt på salgsbilag i Hovedbok.
    3. *Presentasjon og Regnskapsspråk (`evaluate_ns4102_compliance`):* Beregner gjenkjennelsesgrad (%) på 4-sifrede NS 4102-kontonumre (1000–8999) og norske kontonavn.
  - **Seksjon B (Fremtidige revisjonshandlinger V2):**
    - `st.divider()` og undertittel etterfulgt av kort i `st.container(border=True)` for **Bilagstesting (V2)** (`st.button("Start bilagskontroll", disabled=True)`) og **Prosessgjennomgang (V2)** (`st.button("Analyser rutiner", disabled=True)`).
- **Operasjonell analyse (`src/views/operational_analysis.py`):**
  - Opprettet V2-plassholder (`🚧 Under utvikling`) for kunde-/produktlønnsomhet og lagerstyring.
- **Testing:**
  - Utvidet `tests/test_compliance.py` og `tests/test_app_ui.py` til **45 tester** (`45 passed`). Ingen endringer i kode er committet ennå (kun sesjonsloggen committes iht. instruks).

### Åpne punkter
- Ingen.
