# Kvalitetssikring, Testing og Retting av KI-generert Kode

* **Dokument-ID:** QA-REPORT-01
* **Prosjekt:** G56 – Ledelsesrapport og forenklet kontroll av regnskap med KI
* **Emne:** IBE160 Programmering med KI (Kriterium 3: Kvalitetssikring og testing - 15 %)
* **Formål:** Dokumentere systematisk testing, automatisert testdekning, samt konkrete eksempler på feil som ble avdekket i KI-generert kode og hvordan de ble rettet.

---

## 1. Teststrategi og Testdekning

Testregimet i prosjektet er bygget opp med **13 automatiserte enhetstester i `pytest`** som dekker alle fire Epics definert i `PRD.md`. Testene kjøres lokalt med kommandoen:

```bash
pytest -v tests/
```

### Oversikt over Automatiserte Tester

| Testfil | Testfunksjon | Epic / Krav | Hva som faktisk testes | Resultat |
|:---|:---|:---|:---|:---:|
| `test_compliance.py` | `test_validate_balance_success` | Epic 1 / FR-1.3 | Bekrefter at en balansert saldobalanse godkjennes uten feil. | **PASSED** |
| `test_compliance.py` | `test_validate_balance_failure` | Epic 1 / FR-1.3 | Bekrefter at ubalanse mellom Debet og Kredit fanges og reiser `ValueError`. | **PASSED** |
| `test_compliance.py` | `test_validate_sample_files` | Epic 1 / DoD | Verifiserer de faktiske filene i `data/sample/` (både balansert og ubalansert). | **PASSED** |
| `test_compliance.py` | `test_reconciliation_happy_path` | Epic 2 / FR-2.1 | Verifiserer at $IB + \Delta HB = UB$ gir 0 avvik for balansert datasett. | **PASSED** |
| `test_compliance.py` | `test_reconciliation_detects_discrepancy` | Epic 2 / FR-2.1 | Verifiserer at differanser på konto 1500 og 1920 fanges med nøyaktig beløp ($\pm 30\ 000$). | **PASSED** |
| `test_compliance.py` | `test_ns4102_mapping` | Epic 2 / FR-2.3 | Tester mapping av 4-sifrede norske kontonumre til korrekte NS 4102-kategorier. | **PASSED** |
| `test_data_pipeline.py` | `test_norwegian_semicolon_and_comma_decimal` | Epic 1 / FR-1.1 | Tester autodeteksjon av semikolon (`;`), tusenskilletegn (`100 000,00`) og norsk desimalkomma. | **PASSED** |
| `test_data_pipeline.py` | `test_missing_account_column_raises_clear_error` | Epic 1 / FR-1.2 | Verifiserer at manglende `Konto`-kolonne gir en pedagogisk feilmelding fremfor krasj. | **PASSED** |
| `test_data_pipeline.py` | `test_empty_file_raises_clear_error` | Epic 1 / FR-1.1 | Sikrer at tomme filer avvises kontrollert med beskrivende feilmelding. | **PASSED** |
| `test_data_pipeline.py` | `test_clean_norwegian_numeric_series` | Epic 1 / NFR-2.1 | Tester parsing av tallstrenger med ulike formater (`1 500,50`, `15.000,25`, osv.). | **PASSED** |
| `test_reporting.py` | `test_mock_mode_generates_valid_commentary` | Epic 3 / FR-3.3 | Verifiserer at frakoblet mock-modus returnerer et komplett Pydantic-validert objekt. | **PASSED** |
| `test_reporting.py` | `test_mock_mode_with_discrepancies` | Epic 3 / FR-3.1 | Verifiserer at KI-rapporten automatisk tilpasser revisjonsadvarselen dersom det er avvik. | **PASSED** |
| `test_reporting.py` | `test_pdf_generation_produces_valid_pdf_buffer` | Epic 4 / FR-4.1 | Verifiserer at PDF-motoren produserer en gyldig binær PDF-strøm (`%PDF-`) in-memory. | **PASSED** |

---

## 2. Konkrete Eksempler på Feil i KI-generert Kode og Retting (Code Review)

Sensorveiledningen krever dokumentasjon av feil som ble funnet i KI-generert kode og hvordan gruppen rettet dem. Her er tre sentrale eksempler:

### Eksempel 1: Flyttallsfeil i regnskapsavstemming (Floating Point Inexactness)
* **Feil funnet i KI-koden:** 
  KI-en genererte opprinnelig koden:
  ```python
  if debit_sum != credit_sum:
      raise ValueError("Ubalanse")
  ```
* **Hvorfor det feilet:** 
  I Python fører binær flyttallslagring (IEEE 754) til at f.eks. `10.0 + 0.000000000000001 != 10.0`. I et regnskap med tusenvis av summeringer førte dette til at en fullstendig balansert saldobalanse ble feilaktig avvist med differanse `0.0000000000000014 NOK`.
* **Hvordan vi rettet det:**
  Vi erstattet likhetssjekken med Numpys toleransetest:
  ```python
  if not np.isclose(debit_sum, credit_sum, atol=0.01):
      raise ValueError(f"BALANSEFEIL: Differanse {abs(debit_sum - credit_sum):.2f}")
  ```
  Dette tillater avrundingsdifferanser under 1 øre, som er standard i finansiell revisjon.

### Eksempel 2: Modul-caching i Streamlit (`unexpected keyword argument`)
* **Feil funnet i KI-koden:**
  Da vi utvidet `generate_management_report()` med parameteren `recon_result`, krasjet Streamlit med:
  `TypeError: generate_management_report() got an unexpected keyword argument 'recon_result'`.
* **Hvorfor det feilet:**
  Streamlit overvåker og reloader kun `app.py`, men beholder underliggende moduler (`src/llm_integration.py`) i `sys.modules`. Dermed benyttet appen den gamle funksjonssignaturen som lå i minnet fra serverstart.
* **Hvordan vi rettet det:**
  Vi implementerte to forsvarsmekanismer:
  1. I `src/llm_integration.py` la vi til `**kwargs` for bakoverkompatibilitet.
  2. I `src/app.py` la vi inn tvungen dynamisk oppdatering:
     ```python
     import llm_integration
     import importlib
     importlib.reload(llm_integration)
     ```
  Dette garanterer at endringer i logikk umiddelbart slår igjennom i grensesnittet uten krasj.

### Eksempel 3: Særnorske eksportformater fra Fiken/Tripletex
* **Feil funnet i KI-koden:**
  KI-en antok at CSV-filer alltid er komma-separerte med punktum som desimal. Da vi testet en reell eksport fra et norsk regnskapssystem, feilet innlesingen fullstendig fordi filen brukte semikolon (`;`) og formatet `100 000,00`.
* **Hvordan vi rettet det:**
  Vi bygget `detect_csv_delimiter_and_encoding()` og `clean_norwegian_numeric_series()` i `src/data_pipeline.py`. Funksjonen sniffer de første 8 KB av filen, gjenkjenner semikolon og håndterer både mellomrom som tusenskilletegn og komma som desimalskilletegn.

---

## 3. Manuell Testprotokoll (End-to-End UI & PDF)

For funksjonalitet som ikke fanges 100 % av enhetstester (spesielt visuell rendering og nedlasting i nettleser), er det etablert følgende manuelle testprotokoll:

| Steg | Testet Funksjon | Forventet Oppførsel | Verifisert Status |
|:---:|:---|:---|:---:|
| 1 | Oppstart via README-kommando | Applikasjonen starter på `http://localhost:8501` uten feilmeldinger i terminalen. | ✅ Verifisert |
| 2 | Hurtigvalg: "Bruk eksempeldata (Balansert)" | Data lastes inn automatisk, balansekontroll viser grønt flagg, kryssavstemming viser "0 avvik". | ✅ Verifisert |
| 3 | Hurtigvalg: "Bruk eksempeldata (Med avvik)" | Rød feilmelding vises umiddelbart med tabell over avvik på konto 1500 (-30 000) og 1920 (+30 000). | ✅ Verifisert |
| 4 | Generer KI-rapport i testmodus | Rapport genereres på under 1 sekund. Hovedkonklusjon og tre faner (Lønnsomhet, Likviditet, Revisor) vises ryddig. | ✅ Verifisert |
| 5 | Nedlasting av PDF | Filen `Styrepakke_Ledelsesrapport.pdf` lastes ned lokalt. Åpnes i PDF-leser; overskrifter, callout-boks og 4-kolonners tiltakstabell har korrekt styling uten tekstkutt. | ✅ Verifisert |
| 6 | Ekte filopplasting (Drag and drop) | Bruker drar inn `saldobalanse_norsk_semikolon.csv`; normaliseres og vises korrekt. | ✅ Verifisert |

---

## 4. Sikkerhet og Personvern (In-Memory Processing)

* **Ingen filpersistens:** Koden benytter `io.BytesIO` for både filopptak og PDF-generering. Ingen kundedata lagres til disk (`/tmp` eller lokale mapper).
* **Ingen hemmeligheter i git:** `.env` er inkludert i `.gitignore`. En `.env.example` ligger i repoet som dokumentert mal uten hemmeligheter.
* **Ingen sensitive testdata:** Alle filer i `data/sample/` er syntetiske og oppdiktede.
