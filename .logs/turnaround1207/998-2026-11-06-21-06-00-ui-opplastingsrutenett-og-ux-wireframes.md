# UI-opplastingsrutenett og UX-wireframes

## 2026-11-06 kl. 21:06 — turnaround1207

### Oppgave
Videreutvikle og sluttpolere brukergrensesnittet i `src/app.py` for å maksimere Kriterium 4 (Design og brukeropplevelse) ved å etablere et statisk, alltid synlig 2×2-opplastingsrutenett og hurtigknapper i toppseksjonen, samt synkronisere UX-dokumentasjonen i `docs/03_ux/UX_DESIGN_OG_WIREFRAMES.md`.

### Plan
- Refaktorere toppseksjonen i `src/app.py` (før Steg 1) med overskrift, undertittel og to hurtigknapper på én rad (norsk semikolon-format og tilbakestilling til eksempeldata).
- Etablere et alltid synlig 2×2-rutenett med `st.columns(2)` og `st.container(border=True)` for både aktive moduler (1. Saldobalanse og 2. Hovedbok) og låste v2.0-moduler (3. CRM & Kundereskontro og 4. Lagerdata & Vareflyt).
- Oppdatere ASCII-wireframen under «Skjerm 1» i `docs/03_ux/UX_DESIGN_OG_WIREFRAMES.md` til å speile 2×2-rutenettet.
- Verifisere med `pytest -v tests/` at ingen eksisterende tester eller regnskapsregler i *The AI Firewall* er brutt.

### Diskusjon & Prompting
- Vi spesifiserte hvordan toppseksjonen i `src/app.py` skulle utformes for å gi sensor umiddelbar oversikt over både aktiv kjernefunksjonalitet (Saldobalanse + Hovedbok), ett-klikks testing av norske spesialformater (semikolon `;` og desimalkomma `100 000,00`), og tydelig produkt-scoping (låste v2.0-kort for CRM & Kundereskontro og Lagerdata & Vareflyt).
- **Arkitektonisk etterlevelse:** Alt ble implementert i 100 % ren native Streamlit (ingen `unsafe_allow_html=True`) og uten endringer i regnskapslogikken (`src/compliance_engine.py`), datapipelinen (`src/data_pipeline.py`) eller *The AI Firewall* (`src/llm_integration.py`).

### Resultat
- **Oppdatert `src/app.py` (ukommittert i arbeidskopien):**
  - Etablert ny toppseksjon med `st.header("📂 Last opp Regnskapsfiler: Saldobalanse (SB) og Hovedbok (HB)")` og undertittel.
  - Lagt til hurtigknapper på én rad via `activate_semicolon_demo` (`⚡ Last inn norsk semikolon-format (100 000,00)`, som laster `data/sample/saldobalanse_norsk_semikolon.csv` via `process_csv_in_memory` og `data/sample/hovedbok_balansert.csv`) og `reset_to_sample_data` (`🔄 Nullstill til eksempeldata`).
  - Implementert alltid synlig 2×2-kortrutenett:
    - **Boks 1 (`📊 1. Saldobalanse (SB)`):** Aktiv filopplaster (`key="sb_upload"`), validering med `validate_input(..., expected_type="SB")`, overstyring av eksempeldata og kildeindikator i bunn (`Aktiv kilde: [Filnavn] ([Antall] kontoer)`).
    - **Boks 2 (`📘 2. Hovedbok (HB)`):** Aktiv filopplaster (`key="hb_upload"`), validering med `validate_input(..., expected_type="HB")`, overstyring av eksempeldata og kildeindikator i bunn (`Aktiv kilde: [Filnavn] ([Antall] transaksjoner)`).
    - **Boks 3 (`🤝 3. CRM & Kundereskontro`):** Låst v2.0-kort (`🚧 Under utvikling – Ikke tilgjengelig`) med beskrivelse mot konto 1500 og 3000, deaktivert knapp og scoping-status i bunn.
    - **Boks 4 (`📦 4. Lagerdata & Vareflyt`):** Låst v2.0-kort (`🚧 Under utvikling – Ikke tilgjengelig`) med beskrivelse mot konto 1400 og 4000, deaktivert knapp og låst-status i bunn.
- **Oppdatert `docs/03_ux/UX_DESIGN_OG_WIREFRAMES.md` (ukommittert i arbeidskopien):**
  - Oppdatert ASCII-wireframen under «Skjerm 1» slik at den nøyaktig gjenspeiler hurtigknappene og 2×2-opplastingsrutenettet med aktive og låste moduler.
- **Verifisering:**
  - Kjørt `pytest -v tests/`: **30 av 30 tester bestått** (`30 passed`).
- **Lukket åpent punkt:**
  - Lukket punktet fra [etablering-og-funksjonsforbedringer](999-2026-11-06-20-00-00-etablering-og-funksjonsforbedringer.md) i `issues.md` vedrørende sluttpolering av UI for Kriterium 4.

### Åpne punkter
- Gjennomføre avsluttende sensorgjennomgang og sluttverifisering før innlevering.
