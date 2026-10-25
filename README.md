# G56 — Ledelsesrapport og forenklet kontroll av regnskap med KI

Gruppeprosjekt i **IBE160 Programmering med KI** ved Høgskolen i Molde, høsten 2026 (15 studiepoeng).

**Prosjektmedlem:**
* Victor Guimaraes (Gruppe G56)

---

## 📌 Om Prosjektet

Dette prosjektet leverer en automatisert webapplikasjon bygget i **Python** og **Streamlit** som løser to sentrale problemer for små og mellomstore bedrifter (SMB) uten egen økonomisjef:

1. **Automatisk Regnskapskontroll og Kryssavstemming:** 
   * Dobbelt bokføringskontroll: Verifiserer at $\sum \text{Debet} = \sum \text{Kredit}$ i både **Saldobalanse (SB)** og **Hovedbok (HB)**.
   * Kryssavstemming av bevegelse: Verifiserer at formelen $\text{Inngående Balanse (IB)} + \sum(\text{Transaksjoner i HB}) = \text{Utgående Balanse (UB i SB)}$ stemmer per konto. Eventuelle avvik flagges med kontonummer, kontonavn og differanse.
2. **Deterministiske Nøkkeltall og Strategisk KI-Rapport:**
   * Automatisk mapping mot **Norsk Standard Kontoplan (NS 4102)**.
   * Deterministisk beregning av driftsinntekter, varekostnad, bruttomargin, lønnskostnad, driftsresultat (EBIT) og driftsmargin.
   * **The AI Firewall:** *Koden regner, KI-en forklarer.* Språkmodellen (`gpt-4o-mini` via Pydantic Structured Outputs) mottar kun ferdig utregnede tall og forfatter et profesjonelt ledelsesnotat (CFO-tone) med revisjonsmerknad og strategiske tiltak.
3. **Piksel-perfekt PDF-eksport:**
   * Genererer en presentasjonsklar styrepakke (PDF) direkte i minnet via ReportLab.

```text
+------------------------------------------------------------------------------------+
|  📊 Ledelsesrapport og Regnskapskontroll med KI                                    |
|  [ Driftsinntekter: 200 000 NOK ]  [ EBIT: 110 000 NOK ]  [ Margin: 55.0 % ]       |
|  🏆 Hovedkonklusjon: Selskapet leverer en solid periode med full avstemming.       |
|  [ 📊 Lønnsomhet ]   [ 💧 Likviditet & Arbeidskapital ]   [ 🛡️ Revisors Avstemming ]|
|  [ 📥 Last ned Ledelsesrapport (PDF) ]                                             |
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
git clone https://github.com/ditt-brukernavn/G56-guimaraes.git
cd G56-guimaraes
```

### 2. Opprett virtuelt miljø og installer avhengigheter
```bash
# Opprett virtuelt miljø
python -m venv venv

# Aktiver miljøet (Windows PowerShell)
.\venv\Scripts\Activate.ps1
# ELLER (macOS / Linux)
# source venv/bin/activate

# Installer nødvendige pakker
pip install -r requirements.txt
```

### 3. Start applikasjonen
Du kan starte appen med én enkel kommando fra rotmappen:
```bash
streamlit run app.py
```
*(Alternativt: `streamlit run src/app.py`)*

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
For å kjøre samtlige **13 automatiserte enhetstester** som verifiserer regnskapslogikken, feilhåndtering og PDF-generering:
```bash
pytest -v tests/
```

---

## 📚 Prosessdokumentasjon (BMAD og Sensorveiledning)

For å sikre full sporbarhet fra idé og krav til ferdig kode og kvalitetssikring (kriterium 1–5 i sensorveiledningen), er dokumentasjonen strukturert etter BMAD-metodikken:

* 🏛️ **[course/sensorveiledning.md](./course/sensorveiledning.md)**: *(Offisiell sensorveiledning for emnet IBE160)*
  * Eksamensveiledningens 7 vurderingskriterier, vekting og A–F kjennetegn.
* 🏛️ **[course/tilbakemelding-product-brief.md](./course/tilbakemelding-product-brief.md)**: *(Faglærers evaluering av opprinnelig brief)*
  * Tilbakemeldingen som la grunnlaget for scoping og spisset kjerneflyt (SB + HB).
* 📋 **[planning-artifacts/briefs/brief-prompt/](./planning-artifacts/briefs/brief-prompt/)**: *(BMAD Planleggingsartefakter)*
  * Inneholder `brief.md`, `tilbakemelding-product-brief.md`, `addendum.md`, `ki-logg.md` og `.memlog.md`.
* 📄 **[docs/KI_STYRING_OG_PROMPTS.md](./docs/KI_STYRING_OG_PROMPTS.md)**: *(Sensorveiledning Kriterium 1 - 30 %)*
  * Dokumentasjon av hvordan gruppen har styrt, korrigert og forbedret KI gjennom fire iterasjoner.
  * Fullstendig oversikt over system- og brukerprompts, hyperparametre og governance-regler.
* 📄 **[docs/01_analysis/AVVIK_FRA_PROPOSAL.md](./docs/01_analysis/AVVIK_FRA_PROPOSAL.md)**: *(Sensorveiledning Kriterium 2 - 20 %)*
  * Begrunnelse for omfangsjustering fra opprinnelig proposal til v1 etter faglærers tilbakemelding.
* 📄 **[docs/KVALITETSSIKRING_OG_TESTING.md](./docs/KVALITETSSIKRING_OG_TESTING.md)**: *(Sensorveiledning Kriterium 3 - 15 %)*
  * Dokumentasjon av alle 13 enhetstester i pytest.
  * Tre konkrete eksempler på feil avdekket i KI-generert kode og hvordan de ble rettet (Code Review).
* 📄 **[docs/03_ux/UX_DESIGN_OG_WIREFRAMES.md](./docs/03_ux/UX_DESIGN_OG_WIREFRAMES.md)**: *(Sensorveiledning Kriterium 4 - 10 %)*
  * Brukerreise for daglig leder, ASCII-wireframes, fargehierarki og universell utforming (WCAG).
* 📄 **[docs/04_architecture/ARCHITECTURE.md](./docs/04_architecture/ARCHITECTURE.md)**: *(Sensorveiledning Kriterium 5 - 10 %)*
  * Teknisk systemdesign, dataflyt, "The AI Firewall" og mock-arkitektur.
* 📄 **[docs/02_product/PRD.md](./docs/02_product/PRD.md)**:
  * Product Requirements Document med 4 Epics, 7 User Stories og sporbarhetsmatrise.
* 📄 **[data/sample/README.md](./data/sample/README.md)**:
  * Dokumentasjon av testdatasett og matematisk fasit (både balanserte filer og filer med konstruerte feil).

---

## 📂 Mappestruktur

```text
G56-guimaraes/
├── app.py                              # Hovedinngangspunkt for Streamlit (rot)
├── requirements.txt                    # Nødvendige Python-avhengigheter
├── .env.example                        # Mal for API-nøkler (ingen hemmeligheter)
├── .gitignore                          # Ekskluderer venv, cache og hemmeligheter
├── README.md                           # Denne veiledningen
├── product-brief.md                    # Revidert Product Brief
├── prosjektplan.md                     # Fremdriftsplan for semesteret
├── course/                             # Kursdokumentasjon og sensorveiledning
│   ├── sensorveiledning.md             # Eksamensveiledning Del 1 (70%)
│   └── tilbakemelding-product-brief.md # Faglærers evaluering av product brief
├── planning-artifacts/                 # BMAD planleggingsartefakter
│   └── briefs/brief-prompt/            # Brief, KI-logg, addendum og memlog
│       ├── brief.md                    # Product Brief
│       ├── tilbakemelding-product-brief.md # Tilbakemelding fra faglærer
│       ├── addendum.md                 # Omfangsjustering etter feedback
│       ├── ki-logg.md                  # Logg over KI-styring under brief-fasen
│       └── .memlog.md                  # BMAD minnelogg og regler
├── src/                                # Kildekode
│   ├── app.py                          # Streamlit brukergrensesnitt
│   ├── compliance_engine.py            # Balansekontroll, kryssavstemming og NS 4102
│   ├── data_pipeline.py                # Skuddsikker fillasting (komma, semikolon, desimaler)
│   ├── llm_integration.py              # OpenAI Pydantic Structured Outputs og mock-modus
│   └── pdf_generator.py                # In-memory ReportLab PDF-motor
├── tests/                              # Automatiserte tester (pytest)
│   ├── test_compliance.py             # Tester for balanse, avstemming og mapping
│   ├── test_data_pipeline.py           # Tester for semikolon, desimalkomma og feilhåndtering
│   └── test_reporting.py               # Tester for KI-sammendrag og PDF-eksport
├── data/
│   └── sample/                         # Syntetiske testdatasett med kjent fasit
│       ├── saldobalanse_balansert.csv  # Grønn test: 100 % balanse
│       ├── hovedbok_balansert.csv      # Grønn test: matcher SB perfekt
│       ├── saldobalanse_norsk_semikolon.csv # Norsk eksportformat med semikolon og desimalkomma
│       ├── saldobalanse_med_ubalanse.csv   # Rød test: ubalanse på 10 000 NOK
│       ├── hovedbok_med_avvik.csv      # Rød test: avstemmingsavvik på 30 000 NOK
│       └── README.md                   # Dokumentasjon av testdata og fasit
└── docs/                               # BMAD-dokumentasjon
    ├── KI_STYRING_OG_PROMPTS.md        # Kriterium 1: Prompts, KI-styring og iterasjoner
    ├── KVALITETSSIKRING_OG_TESTING.md  # Kriterium 3: Teststrategi og feilrettingslogg
    ├── 01_analysis/                    # Kriterium 2: Domeneanalyse og avvik fra proposal
    ├── 02_product/                     # PRD, Epics og User Stories
    ├── 03_ux/                          # Kriterium 4: Wireframes og UX-design
    └── 04_architecture/                # Kriterium 5: Teknisk arkitektur og systemdesign
```
