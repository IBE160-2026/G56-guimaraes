# Kvalitetssikring, Testing og Retting av KI-generert Kode

* **Dokument-ID:** QA-REPORT-01
* **Prosjekt:** G56 – Ledelsesrapport og forenklet kontroll av regnskap med KI
* **Emne:** IBE160 Programmering med KI (Kriterium 3: Kvalitetssikring og testing - 15 %)
* **Formål:** Dokumentere systematisk testing, automatisert testdekning, samt konkrete eksempler på feil som ble avdekket i KI-generert kode og hvordan de ble rettet.

---

## 1. Teststrategi og Testdekning

Testregimet i prosjektet er bygget opp med **43 automatiserte enhetstester i `pytest`** som dekker samtlige åtte Epics definert i `PRD.md` (v2.0). Testene kjøres lokalt med kommandoen:

```bash
pytest -v tests/
```

### Oversikt over Automatiserte Tester

| Testfil | Testfunksjon | Epic / Krav | Hva som faktisk testes | Resultat |
|:---|:---|:---|:---|:---:|
| `test_compliance.py` | `test_validate_balance_success` | Epic 1 / FR-1.3 | Bekrefter at en balansert saldobalanse godkjennes uten feil. | **PASSED** |
| `test_compliance.py` | `test_validate_balance_failure` | Epic 1 / FR-1.3 | Bekrefter at ubalanse mellom Debet og Kredit fanges og reiser `ValueError`. | **PASSED** |
| `test_compliance.py` | `test_validate_sample_files` | Epic 1 / FR-1.3 | Verifiserer de faktiske filene i `data/sample/` (både balansert og ubalansert). | **PASSED** |
| `test_compliance.py` | `test_reconciliation_happy_path` | Epic 2 / FR-2.1 | Verifiserer at $IB + \Delta HB = UB$ gir 0 avvik for balansert datasett. | **PASSED** |
| `test_compliance.py` | `test_reconciliation_detects_discrepancy` | Epic 2 / FR-2.2 | Verifiserer at differanser på konto 1500 og 1920 fanges med nøyaktig beløp ($\pm 30\ 000$). | **PASSED** |
| `test_compliance.py` | `test_ns4102_mapping` | Epic 2 / FR-2.3 | Tester mapping av 4-sifrede norske kontonumre til korrekte NS 4102-kategorier. | **PASSED** |
| `test_compliance.py` | `test_reconciliation_account_only_in_hb_detected` | Epic 2 / FR-2.1 | Edge case: Konto som kun eksisterer i Hovedboken fanges opp via outer join. | **PASSED** |
| `test_compliance.py` | `test_reconciliation_account_only_in_sb_with_zero_movement` | Epic 2 / FR-2.1 | Edge case: Konto kun i SB uten bevegelse ($IB == UB$) avstemmes som godkjent. | **PASSED** |
| `test_compliance.py` | `test_calculate_detailed_financial_metrics` | Epic 2 / FR-2.4 | Verifiserer deterministisk utregning av driftsinntekter, kostnader, EBIT, marginer og arbeidskapital. | **PASSED** |
| `test_compliance.py` | `test_cfo_metrics_and_sign_normalization_on_sample_data` | Epic 7 / FR-7.1 | Verifiserer `abs()`-fortegnsnormalisering på klasse 2 samt LG1/LG2, mellombalanse-egenkapital, Gjeldsgrad, TKR og EKR. | **PASSED** |
| `test_compliance.py` | `test_zero_division_safety_in_cfo_metrics` | Epic 7 / FR-7.1 | Verifiserer at alle brøkbaserte CFO-nøkkeltall returnerer `0.0` uten `ZeroDivisionError` ved null-saldoer. | **PASSED** |
| `test_data_pipeline.py` | `test_parametrized_invalid_csv_inputs` (3 cases) | Epic 1 / FR-1.2 | Parametrisert test for tom CSV, manglende Konto-kolonne og manglende beløpskolonner. | **PASSED** |
| `test_data_pipeline.py` | `test_validate_input_detects_empty_dataframe` | Epic 1 / FR-1.2 | Verifiserer at tomme DataFrames avvises med forklarende feilmelding. | **PASSED** |
| `test_data_pipeline.py` | `test_large_numbers_and_norwegian_special_characters_pdf` | Epic 4 / FR-4.1 | Tester at milliardbeløp og norske spesialtegn (`ÆØÅ`) rendres feilfritt i PDF. | **PASSED** |
| `test_data_pipeline.py` | `test_excel_file_processing` | Epic 1 / FR-1.1 | Verifiserer in-memory innlesing og normalisering av `.xlsx`-filer. | **PASSED** |
| `test_data_pipeline.py` | `test_norwegian_semicolon_and_comma_decimal` | Epic 1 / FR-1.1 | Tester autodeteksjon av semikolon (`;`), tusenskilletegn (`100 000,00`) og norsk desimalkomma. | **PASSED** |
| `test_data_pipeline.py` | `test_missing_account_column_raises_clear_error` | Epic 1 / FR-1.2 | Verifiserer at manglende `Konto`-kolonne gir en pedagogisk feilmelding fremfor krasj. | **PASSED** |
| `test_data_pipeline.py` | `test_empty_file_raises_clear_error` | Epic 1 / FR-1.1 | Sikrer at tomme filer avvises kontrollert med beskrivende feilmelding. | **PASSED** |
| `test_data_pipeline.py` | `test_clean_norwegian_numeric_series` | Epic 1 / FR-1.1 | Tester parsing av tallstrenger med ulike formater (`1 500,50`, `15.000,25`, osv.). | **PASSED** |
| `test_data_pipeline.py` | `test_norwegian_erp_column_variations` | Epic 1 / FR-1.2 | Tester normalisering av kolonnenavn fra Tripletex/Visma (`Konto ID`, `Debetbeløp`, osv.). | **PASSED** |
| `test_data_pipeline.py` | `test_mixed_decimal_and_spaces_in_currency` | Epic 1 / FR-1.1 | Tester tallparsing med ledende/etterfølgende mellomrom og blandede skilletegn. | **PASSED** |
| `test_data_pipeline.py` | `test_ledger_upload_preserves_both_kontonavn_and_beskrivelse` | Epic 7 / FR-7.2 | Sikrer at opplastet Hovedbok med både `Kontonavn` og `Beskrivelse` beholder begge uten duplikatkolonne. | **PASSED** |
| `test_reporting.py` | `test_mock_mode_generates_valid_commentary` | Epic 3 / FR-3.3 | Verifiserer at frakoblet mock-modus returnerer et komplett Pydantic-validert objekt. | **PASSED** |
| `test_reporting.py` | `test_mock_mode_with_discrepancies` | Epic 3 / FR-3.3 | Verifiserer at KI-rapporten automatisk tilpasser revisjonsadvarselen dersom det er avvik. | **PASSED** |
| `test_reporting.py` | `test_pdf_generation_produces_valid_pdf_buffer` | Epic 4 / FR-4.1 | Verifiserer at PDF-motoren produserer en gyldig binær PDF-strøm (`%PDF-`) in-memory med nøkkeltall. | **PASSED** |
| `test_reporting.py` | `test_ai_firewall_context_never_contains_raw_transactions` | Epic 3 / FR-3.1 | Verifiserer at KI-payload aldri inneholder råtransaksjoner og at EBIT er deterministisk. | **PASSED** |
| `test_reporting.py` | `test_pydantic_schema_consistency_between_mock_and_class` | Epic 3 / FR-3.2 | Sikrer at Mock-modus produserer nøyaktig samme Pydantic-skjema som live OpenAI API. | **PASSED** |
| `test_reporting.py` | `test_html_generation_produces_valid_self_contained_html` | Epic 5 / FR-5.1–5.6 | Verifiserer gyldig HTML5 i minnet, EBIT/driftsmargin fra fasit, grønn tomtilstand og `html.escape()`. | **PASSED** |
| `test_reporting.py` | `test_html_generation_includes_discrepancies_and_excludes_raw_transactions` | Epic 5 / FR-5.2–5.3 | Verifiserer at avvikskontoer (`1500`/`1920`) vises i HTML ved avvik, og at råtransaksjoner aldri lekker. | **PASSED** |
| `test_reporting.py` | `test_live_api_flow_with_mocked_openai_client` | Epic 3 / FR-3.2 | Verifiserer live OpenAI-stien (`mock_mode=False`) ende-til-ende via `unittest.mock.patch`. | **PASSED** |
| `test_reporting.py` | `test_post_validate_ai_response_catches_contradictions` | Epic 3 / FR-3.2 | Verifiserer at `post_validate_ai_response()` avviser KI-svar som motsier avstemmingsstatusen. | **PASSED** |
| `test_reporting.py` | `test_pdf_and_html_include_extended_cfo_metrics_and_recommendations` | Epic 8 / FR-8.2 | Verifiserer at både PDF og HTML inkluderer Soliditet, LG2, TKR, EKR og deterministisk lønnsomhetspotensial. | **PASSED** |
| `test_database.py` | `test_persistent_sqlite_file_and_sha256_deduplication` | Epic 6 / FR-6.1 | Verifiserer persistent SQLite-lagring på fil på tvers av instanser og SHA-256-deduplikasjon ved rerun. | **PASSED** |
| `test_database.py` | `test_ai_insight_upsert_and_run_details` | Epic 6 / FR-6.1 | Verifiserer upsert av `ManagementCommentary` på `run_id` og gjeninnlasting av komplette analysedetaljer. | **PASSED** |
| `test_database.py` | `test_sql_window_function_running_balance_and_cascade_delete` | Epic 6 / FR-6.2 | Verifiserer SQLite Window Function (`SUM(...) OVER (...)`) for løpende saldo og `ON DELETE CASCADE`. | **PASSED** |
| `test_ledger_analytics.py` | `test_extract_period_label` | Epic 7 / FR-7.2 | Verifiserer utledning av periodeetikett (`YYYY-MM`) fra Hovedbokens datoer og sikker fallback. | **PASSED** |
| `test_ledger_analytics.py` | `test_account_drilldown_running_balance_matches_ub` | Epic 7 / FR-7.2 | Verifiserer konto-drilldown med løpende saldo fra IB til UB både ved samsvar og konstruert avvik. | **PASSED** |
| `test_ledger_analytics.py` | `test_voucher_details_balances_per_voucher` | Epic 7 / FR-7.2 | Verifiserer bilagsinspektør og dobbelt bokføring ($\sum D = \sum K$) på enkeltbilagsnivå. | **PASSED** |
| `test_ledger_analytics.py` | `test_cost_drivers_and_deterministic_profitability_recommendations` | Epic 7 / FR-7.3 | Verifiserer topp kostnadsdrivere og regelbasert beregning av NOK-lønnsomhetspotensial (f.eks. 50 000 NOK frigjort kapital). | **PASSED** |
| `test_app_ui.py` | `test_multipage_views_and_orchestrator_compile_and_export_callables` | Epic 8 / FR-8.1 | Verifiserer AST-kompilering og sidefunksjoner for alle 4 visningsmoduler i `src/views/` og `src/app.py`. | **PASSED** |
| `test_app_ui.py` | `test_end_to_end_v2_pipeline_green_and_red_paths_with_sqlite_history` | Epic 8 / FR-8.1 | Ende-til-ende integrasjonstest av grønn sti (semikolon-CSV) og rød sti (avvik) med SQLite-historikk og eksport. | **PASSED** |

---

## 2. Konkrete Eksempler på Feil i KI-generert Kode og Retting (Code Review)

Sensorveiledningen krever dokumentasjon av feil som ble funnet i KI-generert kode og hvordan gruppen rettet dem. Her er seks sentrale eksempler:

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

### Eksempel 2: Feilplasserte hjelpefunksjoner og død kode i `src/llm_integration.py`
* **Feil funnet i KI-koden under Code Review:**
  Da KI-assistenten la til hjelpefunksjonene `post_validate_ai_response()` og `execute_openai_with_retry()`, ble disse skutt inn *mellom* mock-blokken (`if mock_mode...`) og live OpenAI-blokken inne i `generate_management_report()`. Dermed ble live API-koden (`context_json = json.dumps(...)`) liggende på slutten av `execute_openai_with_retry()` som uoppnåelig kode, samtidig som `build_financial_context()` fikk en duplisert `assert`/`return`-blokk.
* **Hvorfor det ikke ble fanget tidligere:**
  De opprinnelige enhetstestene testet kun `mock_mode=True`, som returnerte tidlig i funksjonen.
* **Hvordan vi rettet det:**
  Vi flyttet `post_validate_ai_response()` og `execute_openai_with_retry()` ut som selvstendige toppnivå-funksjoner *før* `generate_management_report()`, fjernet de dupliserte linjene, og skrev to nye enhetstester (`test_live_api_flow_with_mocked_openai_client` med `unittest.mock.patch` og `test_post_validate_ai_response_catches_contradictions`) som verifiserer live-stien uten ekte nettverkskall.

### Eksempel 3: Særnorske eksportformater fra Fiken/Tripletex
* **Feil funnet i KI-koden:**
  KI-en antok at CSV-filer alltid er komma-separerte med punktum som desimal. Da vi testet en reell eksport fra et norsk regnskapssystem, feilet innlesingen fullstendig fordi filen brukte semikolon (`;`) og formatet `100 000,00`.
* **Hvordan vi rettet det:**
  Vi bygget `detect_csv_delimiter_and_encoding()` og `clean_norwegian_numeric_series()` i `src/data_pipeline.py`. Funksjonen sniffer de første 8 KB av filen, gjenkjenner semikolon og håndterer både mellomrom som tusenskilletegn og komma som desimalskilletegn.

### Eksempel 4: Konsistens mellom PDF- og HTML-styrepakke
* **Feil funnet i KI-koden:**
  Opprinnelig versjon av `generate_management_pdf()` tok imot `ns4102_summary: dict = None`, men brukte aldri parameteren, slik at nøkkeltallstabellen og avvikstabellen manglet i PDF-en.
* **Hvordan vi rettet det:**
  Vi utvidet `src/pdf_generator.py` til å rendre både den deterministiske nøkkeltallstabellen (`ns4102_summary`) og avvikstabellen (`recon_result`), slik at PDF og HTML (`src/html_report.py`) presenterer nøyaktig samme verifiserte tallgrunnlag.

### Eksempel 5: Fortegnsfeil ved kreditsaldoer i klasse 2 og udisponert mellombalanse-resultat (`src/compliance_engine.py`)
* **Feil funnet under regnskapsfaglig gjennomgang (v2.0):**
  I reelle norske saldobalanser (inkludert `data/sample/saldobalanse_balansert.csv`) eksporteres kreditsaldoer i NS 4102 klasse 2 med negativt fortegn (f.eks. `2400 Leverandørgjeld = -50 000,00` og `2050 Annen egenkapital = -110 000,00`). I den tidligere koden trakk `arbeidskapital = omløpsmidler - kortsiktig_gjeld` fra et allerede negativt tall (`270 000 - (-50 000) = 320 000 NOK` i stedet for `220 000 NOK`), mens `if kortsiktig_gjeld > 0:` førte til at `likviditetsgrad_1` ble `0.0` i stedet for `5.40`. Samtidig er periodens overskudd i en mellombalanse ikke disponert til `20xx` ennå.
* **Hvordan vi rettet det:**
  Vi normaliserte klasse 2-saldoer med `abs()` (slik at både fortegnede CSV-eksporter og fortegnsløse test-DataFrames gir riktig tall), la til beregning av reell mellombalanse-egenkapital (`bokført EK + udisponert perioderesultat`) slik at $\text{Eiendeler} = \text{Egenkapital} + \text{Gjeld}$ alltid stemmer i soliditetsberegningen, og sikret dette med `test_cfo_metrics_and_sign_normalization_on_sample_data`.

### Eksempel 6: Duplikatkolonne ved innlasting av Hovedbok med både `Kontonavn` og `Beskrivelse` (`src/data_pipeline.py`)
* **Feil funnet i kolonnenormaliseringen (v2.0):**
  `normalize_column_names()` mappet både `"kontonavn"` og `"beskrivelse"` til `"Kontonavn"`. Når en Hovedbok inneholdt begge kolonnene (`Kontonavn` *og* `Beskrivelse` med bilagstekst), oppsto to kolonner med identisk navn `Kontonavn`, mens selve `Beskrivelse`-kolonnen forsvant før drilldown og SQLite-lagring.
* **Hvordan vi rettet det:**
  Vi endret `normalize_column_names()` slik at `"beskrivelse"` kun mappes til `"Kontonavn"` dersom filen mangler et eksplisitt kontonavn, og ellers bevares som egen kolonne `"Beskrivelse"` sammen med `"Bilagsnr"` og `"Dato"`. Dekket med `test_ledger_upload_preserves_both_kontonavn_and_beskrivelse`.

---

## 3. Manuell Testprotokoll (End-to-End UI & PDF)

For funksjonalitet som ikke fanges 100 % av enhetstester (spesielt visuell rendering og nedlasting i nettleser), er det etablert følgende manuelle testprotokoll:

| Steg | Testet Funksjon | Forventet Oppførsel | Verifisert Status |
|:---:|:---|:---|:---:|
| 1 | Oppstart via README-kommando | Applikasjonen starter på `http://localhost:8501` med 4 sider i navigasjonen uten feilmeldinger i terminalen. | ✅ Verifisert |
| 2 | Hurtigvalg: "Bruk eksempeldata (Balansert)" | Data lastes inn automatisk, balansekontroll viser grønt flagg, kryssavstemming viser "0 avvik", og analysen synkroniseres til SQLite. | ✅ Verifisert |
| 3 | Hurtigvalg: "Bruk eksempeldata (Med avvik)" | Rød feilmelding vises umiddelbart med tabell over avvik på konto 1500 (-30 000) og 1920 (+30 000). | ✅ Verifisert |
| 4 | Finansiell Analyse & HB-drilldown | Side 2 viser CFO KPI-kort (Lønnsomhet, Likviditet LG1/LG2, Soliditet EK-andel, TKR/EKR), løpende kontosaldo i Hovedbok og bilagsinspektør. | ✅ Verifisert |
| 5 | Generer KI-rapport i testmodus | Side 3 viser deterministiske lønnsomhetsråd og genererer KI-rapport på under 1 sekund med fire faner (Lønnsomhet, Likviditet, Soliditet/Rentabilitet, Revisor). | ✅ Verifisert |
| 6 | Nedlasting av PDF og HTML | `Styrepakke_Ledelsesrapport.pdf` og `Styrepakke_Ledelsesrapport.html` lastes ned fra minnet med samtlige CFO-nøkkeltall og lønnsomhetspotensial. | ✅ Verifisert |
| 7 | Ekte filopplasting (Drag and drop) | Bruker drar inn `saldobalanse_norsk_semikolon.csv`; normaliseres, bevares ved sidebytte og vises korrekt. | ✅ Verifisert |
| 8 | Historikk & Trendanalyse (SQLite) | Side 4 viser lagrede kjøringer, trendgrafer på tvers av perioder, detaljinspeksjon og gjeneksport av tidligere rapporter. | ✅ Verifisert |

---

## 4. Sikkerhet, Minnehåndtering og Lokal SQLite-persistens

* **In-memory fil- og rapportstrømmer:** Koden benytter utelukkende `io.BytesIO` for opplastede regnskapsfiler (`.csv`, `.xlsx`) og for generering av styrepakker (`.pdf`, `.html`). Ingen råfiler lagres til `/tmp` eller disk.
* **Kontrollert lokal SQLite-historikk:** Verifiserte analyser og relasjoner lagres kun lokalt i `data/g56_accounting.db` (deduplisert med SHA-256 og strengt ekskludert via `*.db` i `.gitignore`), slik at verken kundedata eller lokale databaser noen gang spores i Git.
* **Ingen hemmeligheter i git:** `.env` er inkludert i `.gitignore`. En `.env.example` ligger i repoet som dokumentert mal uten hemmeligheter.
* **Ingen sensitive testdata:** Alle filer i `data/sample/` er syntetiske og oppdiktede.
