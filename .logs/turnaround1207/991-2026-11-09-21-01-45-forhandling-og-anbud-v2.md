# Forhandling og anbud (v2.)

## 2026-11-09 kl. 21:01 — turnaround1207

### Oppgave
Utvide Streamlit-applikasjonen (`src/app.py`) med en ny konseptuell v2.0-teasermodul kalt «🤝 6. Forhandling og anbud (v2.)», plassere den som valg nr. 6 i sidepanelet (`st.sidebar.radio`), og bygge en native Streamlit-visning (`render_negotiation_and_bidding_mockup()`) som demonstrerer fremtidig OCR/PDF-kontraktsanalyse over *The AI Firewall*, simulert sparepotensial (Bank & Finans, Forsikring, Strøm & Lokaler) og en interaktiv RFQ-anbudsgenerator med ferdigskrevet eksempelanbud.

### Plan
- Opprette `src/views/negotiation_and_bidding.py` med `render_negotiation_and_bidding_mockup()` bygget utelukkende med native Streamlit-komponenter (`st.info`, `st.header`, `st.columns(3)`, `st.container(border=True)`, `st.selectbox(disabled=True)`, `st.button(disabled=True)` og `st.expander`).
- Oppdatere `NAV_OPTIONS` og hovedrouteren i `src/app.py` til 8 steg, samt oppdatere stegnummereringen på steg 7 (`💡 7. KI-Rådgiver & Eksport`) og steg 8 (`🗄️ 8. Historikk & Trendanalyse`) i tilhørende visningsfiler.
- Utvide testsuiten i `tests/test_app_ui.py` til å verifisere ny navigasjon, kompilering uten `unsafe_allow_html` og alle obligatoriske UI-elementer i modulen.

### Resultat
- Opprettet `src/views/negotiation_and_bidding.py` med:
  - Teaser-banner (`st.info`) om automatisk PDF/OCR-innlesing og ekstraksjon av skjulte kontraktsvilkår i v2.0.
  - Toppseksjon (`st.header("🤝 Forhandling og anbud på tjenester")`) og 3 KPI-kort i `st.columns(3)` med `st.container(border=True)` for **Bank & Finans** (`45 000 kr/år`), **Forsikring** (`24 000 kr/år`) og **Strøm & Lokaler** (`12 000 kr/år`).
  - Mockup av RFQ Builder med deaktivert `st.selectbox`, deaktivert `st.button("Generer formell anbudsforespørsel (RFQ) med KI", disabled=True)` og `st.expander("Se eksempel på generert anbud")` med et komplett, profesjonelt CFO-anbud basert på NS 4102.
- Oppdatert `src/app.py`, `src/views/ai_advisor_and_export.py`, `src/views/history_and_trends.py`, `src/views/operational_analysis.py`, `src/views/upload_and_control.py` og `tests/test_app_ui.py`.
- Verifisert med `pytest -v` (48 av 48 tester bestått, 0 advarsler).

### Åpne punkter
- Ingen.
