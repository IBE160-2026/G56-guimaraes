# G56 — Ledelsesrapport og forenklet kontroll av regnskap med KI

Gruppeprosjekt i **IBE160 Programmering med KI** ved Høgskolen i Molde, høsten 2026 (15 studiepoeng).

**Prosjektmedlem:**
* Victor Guimaraes (Gruppe G56)

---

## 🎓 Hvordan prosjektet oppfyller IBE160-læringsmålene

Dette prosjektet er utviklet for å demonstrere samtlige kjernekompetanser i **IBE160 Programmering med KI**:

1. **Aktiv styring av KI (Ikke passiv bruk):**
   * Utviklingen er utført utelukkende med **Google Gemini Antigravity** som agentisk parprogrammerer.
   * Studenten har definert arkitektoniske rekkverk (*The AI Firewall*), avvist overoptimistiske forslag (f.eks. OCR-tolkning og Altinn-scraping) og styrt utviklingen gjennom seks dokumenterte iterasjoner.
2. **Klar arbeidsdeling: "Koden regner, KI forklarer":**
   * Ingen språkmodell utfører summeringer eller regnskapskontroll.
   * Dobbelt bokføring ($\sum D = \sum K$), kryssavstemming ($IB + \Delta HB = UB$), CFO-nøkkeltall og lønnsomhetspotensial i NOK skjer 100 % deterministisk i Python/Pandas/SQLite. Runtime-LLM (`gpt-4o-mini`) mottar utelukkende ferdig aggregerte nøkkeltall og valideres via Pydantic.
3. **Kvalitetssikring og feilretting av KI-generert kode:**
   * **43 automatiserte enhetstester (`pytest`)** dekker balansekontroll, kryssavstemming, CFO-nøkkeltall, HB-drilldown, SQLite-historikk, filformater samt PDF- og HTML-generering.
   * Seks konkrete bugs i kode og dataflyt (flyttallsunøyaktighet, død kode, særnorske skilletegn, rapportkonsistens, fortegnsfeil i klasse 2 og duplikatkolonner i HB) ble identifisert og rettet (dokumentert i `docs/KVALITETSSIKRING_OG_TESTING.md`).
4. **Frakoblet sensormodus:**
   * Applikasjonen kjører 100 % lokalt og offline via syntetiske eksempeldatasett med fasit og innebygd SQLite (`sqlite3`), uten behov for eksterne API-nøkler eller databaseservere.

---

## 📌 Om Prosjektet (v2.0 — Strategisk Finansanalyse & Regnskapskontroll)

Dette prosjektet leverer en flersides webapplikasjon bygget i **Python**, **Streamlit (`st.navigation`)** og **SQLite** som løser sentrale behov for små og mellomstore bedrifter (SMB) uten egen økonomisjef:

1. **Automatisk Regnskapskontroll og Kryssavstemming (Side 1):** 
   * Dobbelt bokføringskontroll: Verifiserer at $\sum \text{Debet} = \sum \text{Kredit}$ i både **Saldobalanse (SB)** og **Hovedbok (HB)**.
   * Kryssavstemming av bevegelse: Verifiserer at formelen $\text{Inngående Balanse (IB)} + \sum(\text{Transaksjoner i HB}) = \text{Utgående Balanse (UB i SB)}$ stemmer per konto. Eventuelle avvik flagges med kontonummer, kontonavn og differanse.
2. **CFO-Nøkkeltall og Hovedbok-Drilldown (Side 2):**
   * Automatisk mapping mot **Norsk Standard Kontoplan (NS 4102)**.
   * Deterministisk beregning av **Lønnsomhet** (driftsinntekter, bruttomargin, lønnsandel, EBIT, driftsmargin), **Likviditet** (arbeidskapital, likviditetsgrad 1 og 2), **Soliditet** (mellombalanse-egenkapital, egenkapitalandel, gjeldsgrad) og **Rentabilitet** (TKR og EKR).
   * Interaktiv **Hovedbok-utforsker** med løpende saldo fra IB til UB og **bilagsinspektør** som sjekker debet/kredit på enkeltbilag.
3. **Deterministisk Lønnsomhetsmotor, KI-Rådgiver og Eksport (Side 3):**
   * Regelbasert Python-motor som beregner eksakt NOK-potensial opp mot SMB-normer før tallene sendes over **The AI Firewall** til `gpt-4o-mini` (via Pydantic `ManagementCommentary`).
   * Genererer en presentasjonsklar styrepakke direkte i minnet (`io.BytesIO`) både som **PDF** (ReportLab) og som en selvstendig, offline-klar **HTML5-fil**.
4. **Relasjonell SQLite-Database og Historikksammenligning (Side 4):**
   * Automatisk lagring i en lokal, git-ignorert SQLite-database (`data/g56_accounting.db`) med 6 normaliserte tabeller, fremmednøkler (`ON DELETE CASCADE`), SQLite Window Functions og SHA-256-deduplikasjon.

```text
+------------------------------------------------------------------------------------+
|  🧭 Navigasjon: [1. Kontroll] [2. Finansanalyse & HB] [3. KI & Eksport] [4. Historikk]
|  [ Driftsinntekter: 200 000 NOK ] [ EBIT: 110 000 NOK ] [ EK-andel: 81.5 % ]       |
|  🏆 Hovedkonklusjon: Selskapet leverer 55.0 % driftsmargin med full avstemming.    |
|  [ 📊 Lønnsomhet ] [ 💧 Likviditet ] [ 🏛️ Soliditet & TKR/EKR ] [ 🛡️ Revisor ]      |
|  [ 📥 Last ned Ledelsesrapport (PDF) ]   [ 📥 Last ned Styrepakke (HTML) ]         |
+------------------------------------------------------------------------------------+
```

---

## 🚀 Hurtigstart for Sensor (Kjøres lokalt på 1-2-3)

Applikasjonen er designet for å kunne evalueres raskt og feilfritt på enhver maskin. Den krever **ingen eksterne databaser, Docker eller skytjenester**.

### Systemkrav
* **Python:** Versjon 3.10 eller 3.11 (anbefalt).
* **Internett:** Kun nødvendig ved installasjon av pakker (`pip`) eller ved live OpenAI API-kall. **Appen fungerer 100 % frakoblet i testmodus.**

### 1. Klon repositoriet og naviger til mappen
```bash
git clone https://github.com/IBE160-2026/G56-guimaraes.git
cd G56-guimaraes
```

### 2. Opprett virtuelt miljø og installer avhengigheter
```bash
# Opprett virtuelt miljø
python -m venv .venv

# Aktiver miljøet (Windows PowerShell)
.\.venv\Scripts\Activate.ps1
# ELLER (macOS / Linux)
# source .venv/bin/activate

# Installer nødvendige pakker
pip install -r requirements.txt
```

### 3. Start applikasjonen
Du kan starte appen med én enkel kommando fra rotmappen:
```bash
streamlit run app.py
```
*(Merk: `app.py` i rotmappen er startpunktet som automatisk ruter til `src/app.py` med korrekte miljøstier).*

Applikasjonen åpner seg automatisk i nettleseren din på `http://localhost:8501`.

---

## 🧪 Testing og Sensor-Visning (Ingen API-nøkkel påkrevd)

I sidepanelet til venstre i applikasjonen kan du teste hele systemet uten å laste opp egne filer eller oppgi API-nøkkel:

1. **"Bruk eksempeldata (Balansert)":** 
   * Laster automatisk inn `data/sample/saldobalanse_balansert.csv` og `data/sample/hovedbok_balansert.csv`.
   * Viser grønn balansekontroll og full avstemmingskonsistens (0 avvik).
   * Klikk **"🚀 Generer Strategisk Ledelsesrapport (KI)"** for å se CFO-analysen, og last ned PDF-rapporten.
2. **"Bruk eksempeldata (Med avvik)":** 
   * Laster inn `data/sample/hovedbok_med_avvik.csv`.
   * Viser hvordan systemet umiddelbart oppdager konstruerte avvik på konto 1500 (-30 000 NOK) og 1920 (+30 000 NOK) i en rød varslingstabell.
   * Se hvordan KI-en automatisk tilpasser analysen og utsteder en formell revisjonsadvarsel til styret!
3. **Frakoblet Sensormodus (Mock KI):** 
   * Avkrysset som standard. Bypasser OpenAI API og returnerer en deterministisk, Pydantic-validert rapport offline.
   * Dersom du ønsker å teste med en ekte OpenAI-nøkkel, fjerner du bare avkrysningen og limer inn nøkkelen din i feltet (eller oppretter `.env` basert på `.env.example`).

### Kjøre automatiserte tester (`pytest`)
For å kjøre samtlige **43 automatiserte enhetstester** som verifiserer regnskapslogikken, CFO-nøkkeltall, Hovedbok-drilldown, SQLite-historikk, feilhåndtering samt PDF- og HTML-generering:
```bash
pytest -v tests/
```
*(Alternativt i Windows: Dobbeltklikk på `scripts/run_tests.bat`)*

---

## 📚 Prosessdokumentasjon (BMAD og Sensorveiledning)

For å sikre full sporbarhet fra idé og krav til ferdig kode og kvalitetssikring (kriterium 1–5 i sensorveiledningen), er dokumentasjonen strukturert etter BMAD-metodikken:

* 🏛️ **[docs/00_course_and_brief/sensorveiledning.md](./docs/00_course_and_brief/sensorveiledning.md)**: *(Offisiell sensorveiledning for emnet IBE160)*
  * Eksamensveiledningens 7 vurderingskriterier, vekting og A–F kjennetegn.
* 🏛️ **[docs/00_course_and_brief/tilbakemelding-product-brief.md](./docs/00_course_and_brief/tilbakemelding-product-brief.md)**: *(Faglærers evaluering av opprinnelig brief)*
  * Tilbakemeldingen som la grunnlaget for scoping og spisset kjerneflyt (SB + HB).
* 📋 **[docs/00_course_and_brief/brief-ki-logg.md](./docs/00_course_and_brief/brief-ki-logg.md)**: *(KI-logg fra brief-fasen)*
  * Dokumenterer systematisk styring, prompting og korrigering av KI under utarbeidelsen av Product Brief.
* 📄 **[docs/KI_STYRING_OG_PROMPTS.md](./docs/KI_STYRING_OG_PROMPTS.md)**: *(Sensorveiledning Kriterium 1 - 30 %)*
  * Dokumentasjon av hvordan gruppen har styrt, korrigert og forbedret KI gjennom seks iterasjoner.
  * Fullstendig oversikt over system- og brukerprompts, hyperparametre og governance-regler.
* 📄 **[docs/01_analysis/AVVIK_FRA_PROPOSAL.md](./docs/01_analysis/AVVIK_FRA_PROPOSAL.md)**: *(Sensorveiledning Kriterium 2 - 20 %)*
  * Begrunnelse for omfangsjustering fra opprinnelig proposal til v1 etter faglærers tilbakemelding.
* 📄 **[docs/KVALITETSSIKRING_OG_TESTING.md](./docs/KVALITETSSIKRING_OG_TESTING.md)**: *(Sensorveiledning Kriterium 3 - 15 %)*
  * Dokumentasjon av alle 43 enhetstester i pytest.
  * Seks konkrete eksempler på feil avdekket i kode/dataflyt og hvordan de ble rettet (Code Review).
* 📄 **[docs/03_ux/UX_DESIGN_OG_WIREFRAMES.md](./docs/03_ux/UX_DESIGN_OG_WIREFRAMES.md)**: *(Sensorveiledning Kriterium 4 - 10 %)*
  * Brukerreise for daglig leder, 4-siders `st.navigation`-arkitektur, ASCII-wireframes og universell utforming (WCAG).
* 📄 **[docs/04_architecture/ARCHITECTURE.md](./docs/04_architecture/ARCHITECTURE.md)**: *(Sensorveiledning Kriterium 5 - 10 %)*
  * Teknisk systemdesign, dataflyt, "The AI Firewall", relasjonelt SQLite ER-skjema og mock-arkitektur.
* 📄 **[docs/02_product/PRD.md](./docs/02_product/PRD.md)**:
  * Product Requirements Document (v2.0) med 8 Epics, funksjonelle krav og komplett sporbarhetsmatrise.
* 📄 **[data/sample/README.md](./data/sample/README.md)**:
  * Dokumentasjon av testdatasett og matematisk fasit (både balanserte filer og filer med konstruerte feil).

---

## 📂 Mappestruktur

```text
G56-guimaraes/
├── .agents/skills/                     # Gemini Antigravity Skills (BMAD roller & sesjonslogg)
├── .github/workflows/ci.yml           # GitHub Actions automatisert testkjøring (CI)
├── .githooks/pre-push                  # Lokal git hook for forhåndstesting før push
├── .logs/turnaround1207/               # Sesjonslogger og åpne punkter (issues.md)
├── .streamlit/config.toml              # Tema- og serverkonfigurasjon for Streamlit
├── _bmad/                              # BMAD rammeverkmoduler (_config, bmm, cis, core, custom)
├── scripts/                            # Hjelpeskript for oppstart og testkjøring
├── app.py                              # Hovedinngangspunkt for Streamlit (rot)
├── AGENTS.md                           # Felles agentinstruksjoner (Norsk språk, BMAD-regler)
├── GEMINI.md                           # Gemini Antigravity prosjektregler ("The AI Firewall")
├── .gitattributes                      # Konsistente linjeskift (LF) på tvers av OS
├── requirements.txt                    # Nødvendige Python-avhengigheter
├── .env.example                        # Mal for API-nøkler (ingen hemmeligheter)
├── .gitignore                          # Ekskluderer venv, cache, *.db og hemmeligheter
├── README.md                           # Denne veiledningen
├── product-brief.md                    # Revidert Product Brief (Kjerneversjon: SB + HB)
├── prosjektplan.md                     # Fremdriftsplan for semesteret
├── src/                                # Kildekode
│   ├── app.py                          # Flersides Streamlit-orkestrator (st.navigation)
│   ├── app_logging.py                  # Strukturert in-memory/stdout logging
│   ├── compliance_engine.py            # Balansekontroll, kryssavstemming, NS 4102 og CFO KPI-er
│   ├── data_pipeline.py                # Skuddsikker fillasting (komma, semikolon, desimaler)
│   ├── database.py                     # Relasjonell SQLite-motor (6 tabeller, SHA-256, Window Func)
│   ├── ledger_analytics.py             # HB konto-drilldown, bilagsinspektør og lønnsomhetsmotor
│   ├── llm_integration.py              # OpenAI Pydantic Structured Outputs og mock-modus
│   ├── pdf_generator.py                # In-memory ReportLab PDF-motor
│   ├── html_report.py                  # In-memory selvstendig HTML5-styrepakke
│   └── views/                          # Flersides visningsmoduler
│       ├── upload_and_control.py       # Side 1: Filinntak, balanse- og kryssavstemming
│       ├── financial_analysis.py       # Side 2: CFO nøkkeltall, HB-utforsker og bilagsinspektør
│       ├── ai_advisor_and_export.py    # Side 3: Lønnsomhetsmotor, KI-rapport og PDF/HTML-eksport
│       └── history_and_trends.py       # Side 4: SQLite-historikk, trendgrafer og gjenåpning
├── tests/                              # Automatiserte tester (pytest — 43 tester)
│   ├── test_compliance.py             # Tester for balanse, avstemming, NS 4102 og CFO KPI-er
│   ├── test_data_pipeline.py           # Tester for semikolon, desimalkomma og kolonnenormalisering
│   ├── test_database.py                # Tester for SQLite-persistens, SHA-256 og Window Functions
│   ├── test_ledger_analytics.py        # Tester for HB-drilldown, bilag og lønnsomhetsråd
│   ├── test_reporting.py               # Tester for KI-sammendrag, AI Firewall, PDF- og HTML-eksport
│   └── test_app_ui.py                  # Tester for flersides arkitektur og ende-til-ende flyt
├── data/
│   └── sample/                         # Syntetiske testdatasett med kjent fasit
│       ├── saldobalanse_balansert.csv  # Grønn test: 100 % balanse
│       ├── hovedbok_balansert.csv      # Grønn test: matcher SB perfekt
│       ├── saldobalanse_norsk_semikolon.csv # Norsk eksportformat med semikolon og desimalkomma
│       ├── saldobalanse_med_ubalanse.csv   # Rød test: ubalanse på 10 000 NOK
│       ├── hovedbok_med_avvik.csv      # Rød test: avstemmingsavvik på 30 000 NOK
│       └── README.md                   # Dokumentasjon av testdata og fasit
└── docs/                               # Samlet BMAD- og prosjektdokumentasjon
    ├── KI_STYRING_OG_PROMPTS.md        # Kriterium 1: Prompts, KI-styring og iterasjoner
    ├── KVALITETSSIKRING_OG_TESTING.md  # Kriterium 3: Teststrategi og feilrettingslogg
    ├── 00_course_and_brief/            # Sensorveiledning, tilbakemelding på brief og brief-logg
    ├── 01_analysis/                    # Kriterium 2: Domeneanalyse og avvik fra proposal
    ├── 02_product/                     # PRD (v2.0), Epics og sporbarhetsmatrise
    ├── 03_ux/                          # Kriterium 4: Wireframes og flersides UX-design
    └── 04_architecture/                # Kriterium 5: Teknisk arkitektur og SQLite ER-skjema
```
