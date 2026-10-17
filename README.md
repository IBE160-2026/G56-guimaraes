# G56 — Ledelsesrapport og forenklet kontroll av regnskap med KI

Gruppeprosjekt i **IBE160 Programmering med KI** ved Høgskolen i Molde, høsten 2026.

**Prosjektmedlem:**
* Victor Guimaraes

---

## 📌 Om Prosjektet

Dette prosjektet leverer en automatisert webapplikasjon bygget i **Python** og **Streamlit** som løser to sentrale problemer for små og mellomstore bedrifter (SMB) uten egen økonomisjef:
1. **Regnskapskontroll og kryssavstemming:** Automatisk kontroll av at $\sum \text{Debet} = \sum \text{Kredit}$ i både **Saldobalanse (SB)** og **Hovedbok (HB)**, samt full kryssavstemming av bevegelse ($IB + \text{netto føringer i HB} = UB \text{ i SB}$) per konto.
2. **KI-ledelsesnotat og PDF-eksport:** Deterministisk beregning av nøkkeltall etter Norsk Standard Kontoplan (NS 4102) og generering av et strukturert, forklarende ledelsesnotat (CFO-tone) med tilhørende PDF-rapport til styret.

*Kjerneprinsipp: Koden regner, KI-en forklarer.* Språkmodellen mottar kun ferdig utregnede tall, og hallusinerer dermed ikke tallverdier.

---

## 🚀 Hurtigstart for Sensor (Kjøres lokalt)

Applikasjonen kan kjøres lokalt uten behov for eksterne skytjenester, Docker eller betalte kontoer. Den inkluderer en **innebygd testmodus (Mock KI)** og syntetiske eksempeldata.

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
```bash
streamlit run src/app.py
```
Applikasjonen åpner seg automatisk i nettleseren din (vanligvis på `http://localhost:8501`).

---

## 🧪 Testing og Sensor-Visning

I sidepanelet til venstre i appen kan du velge mellom:
1. **Bruk eksempeldata (Balansert):** Laster automatisk inn `data/sample/saldobalanse_balansert.csv` og `data/sample/hovedbok_balansert.csv`. Gir 100 % godkjent balanse og full avstemmingskonsistens.
2. **Bruk eksempeldata (Med avvik):** Laster inn `data/sample/hovedbok_med_avvik.csv`. Viser hvordan applikasjonen umiddelbart oppdager og flagger feilkonteringer mellom hovedbok og saldobalanse på spesifikke kontoer (konto 1500 og 1920).
3. **Testmodus (Mock KI):** Avkrysset som standard. Lar deg generere ledelseskommentar og laste ned PDF uten å oppgi en OpenAI API-nøkkel.

### Kjøre automatiserte tester (`pytest`)
For å verifisere internkontrollen og regnskapsberegningene:
```bash
pytest tests/
```

---

## 📂 Prosjektstruktur

* **`product-brief.md`**: Det reviderte Product Briefet med spisset kjerneflyt, testbare suksesskriterier, The Solution og What Makes This Different.
* **`prosjektplan.md`**: Fremdriftsplanen gjennom semesteret tilpasset emnets innleveringsfrister.
* **`src/`**: Kildekode for applikasjonen:
  * `app.py`: Streamlit-brukergrensesnitt.
  * `compliance_engine.py`: Dobbelt bokføringskontroll, kryssavstemming ($IB + HB = UB$) og NS 4102-mapping.
  * `data_pipeline.py`: In-memory prosessering av CSV og Excel.
  * `llm_integration.py`: OpenAI-integrasjon med Structured Outputs og frakoblet testmodus.
  * `pdf_generator.py`: In-memory PDF-rapportgenerering via ReportLab.
* **`tests/`**: Automatiserte enhetstester (`test_compliance.py`).
* **`data/sample/`**: Syntetiske testdata med fasit (`saldobalanse_balansert.csv`, `hovedbok_balansert.csv`, osv.).
* **`docs/`**: BMAD-dokumentasjon fordelt på fasene Analysis, Product, UX og Architecture.
