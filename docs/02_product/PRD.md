# Product Requirements Document (PRD)
## Ledelsesrapport og forenklet kontroll av regnskap med KI

---

## 1. Dokumentkontroll

| Felt | Verdi |
|:---|:---|
| **Dokument-ID** | PRD-01 |
| **Versjon** | v1.1 |
| **Dato** | 2026-11-02 |
| **Eier** | Victor Guimaraes / Gruppe G56 (IBE160 Programmering med KI, Høgskolen i Molde) |
| **Status** | Godkjent (v1.1) |
| **Kildegrunnlag** | `product-brief.md` (revidert v1), `docs/01_analysis/AVVIK_FRA_PROPOSAL.md`, `course/sensorveiledning.md` |
| **Utviklingsverktøy** | Google Gemini Antigravity (BMAD / AiDD) |
| **Runtime-LLM** | OpenAI `gpt-4o-mini` (kun tekst via Pydantic Structured Outputs) + lokal Mock-modus |

### Kontrakt og styringsregel (K1: Prosess og KI-styring)
Denne PRD-en er den overordnede kontrakten mellom prosjekteier og utviklingsagenter. Ingen annen agent, UX-fil eller arkitekturfil har myndighet til å omdefinere hva produktet er eller utvide omfanget. **Kodingsagenten skal stoppe umiddelbart og be om avklaring dersom et spørsmål, grensesnitt eller forretningskrav ikke er besvart i denne PRD-en.**

Kjerneprinsippet for applikasjonen er ufravikelig:
> **Koden regner, KI-en forklarer (The AI Firewall).**

All matematikk, balansekontroll ($\sum \text{Debet} = \sum \text{Kredit}$), kryssavstemming ($\text{IB} + \Delta \text{HB} = \text{UB}$) og nøkkeltallsberegning utføres deterministisk i Python/Pandas. Språkmodellen mottar kun ferdig utregnede nøkkeltall og verifiserte avvik.

---

## 2. Problem, Bruker og Suksesskriterier

### 2.1 Problemet
Økonomisk rapportering og internkontroll i små og mellomstore bedrifter (SMB) preges av manuelle prosesser. Standardrapporter fra regnskapssystemer som Fiken, Tripletex og Xero viser historiske tall hver for seg, men forklarer ikke *hvorfor* tallene svinger. Når en daglig leder forbereder seg til styremøte, må vedkommende manuelt bla i hovedboken, kryssjekke bilag i Excel og skrive ledelseskommentarer for hånd. Samtidig oppdages feilkonteringer eller ubalanser ofte for sent fordi bedriften mangler en automatisert rutine som kontrollerer at transaksjonene i hovedboken (HB) faktisk summerer seg opp til endringen mellom inngående balanse (IB) og utgående balanse (UB) i saldobalansen (SB).

### 2.2 Målgruppe (Brukere)
* **Primærbruker:** Daglig leder i en SMB uten egen økonomiavdeling eller interncontroller, som trenger rask, pålitelig kvalitetssikring av periodetallene og en presentasjonsklar styrepakke (PDF og HTML) uten manuell Excel-avstemming.
* **Sekundærbruker:** Ekstern regnskapsfører eller økonomisk rådgiver som betjener flere SMB-klienter og ønsker å automatisere rutinekontrollen mellom hovedbok og saldobalanse ved månedsavslutning.
* **Evaluator:** Sensor i IBE160 som skal klone repositoriet og kjøre hele verdikjeden lokalt uten API-nøkkel eller betalte tjenester.

### 2.3 Funksjonelle og testbare suksesskriterier
1. **Balansekontroll:** En saldobalanse eller hovedbok der $\sum \text{Debet} \neq \sum \text{Kredit}$ (utover flyttallstoleranse $\le 0,01$ NOK) blir umiddelbart flagget med synlig feilmelding og nøyaktig differanse, og videre rapportgenerering blokkeres.
2. **Kryssavstemming (HB mot SB):** For hver konto kontrollerer systemet at $\text{IB} + \sum(\text{Debet}_{\text{HB}} - \text{Kredit}_{\text{HB}}) = \text{UB}$. Ved avvik flagges den spesifikke kontoen med kontonummer, kontonavn og nøyaktig feilbeløp.
3. **Mapping til NS 4102:** Standard 4-sifrede norske kontonumre mappes deterministisk til sine respektive kontoklasser etter Norsk Standard Kontoplan (NS 4102).
4. **Deterministiske nøkkeltall:** Systemet beregner driftsinntekter, varekostnad, bruttofortjeneste, bruttomargin, lønnskostnad, andre driftskostnader, samlede driftskostnader, driftsresultat (EBIT), driftsmargin, ordinært resultat, bankinnskudd, kundefordringer, leverandørgjeld, arbeidskapital og likviditetsgrad 1 i ren Python/Pandas.
5. **Strukturert KI-ledelseskommentar:** Språkmodellen mottar kun aggregerte nøkkeltall og avviksstatus (ingen råtransaksjoner), og returnerer et strukturert ledelsesnotat på formelt norsk validert mot Pydantic-skjemaet `ManagementCommentary`.
6. **Frakoblet sensormodus (Mock KI):** Sensor kan kjøre applikasjonen 100 % lokalt og offline med eksempeldataene i `data/sample/` uten OpenAI API-nøkkel.
7. **To-formats styrepakke i minnet (PDF og HTML):** Brukeren kan laste ned styrepakken både som PDF (`Styrepakke_Ledelsesrapport.pdf`) og som én selvstendig HTML-fil (`Styrepakke_Ledelsesrapport.html`), generert i minnet (`io.BytesIO`) fra nøyaktig samme datagrunnlag og Pydantic-objekt.
8. **Responstid:** Hele løpet fra filopplasting til ferdig skjermrapport og eksport utføres på under 5 sekunder ved lokal kjøring i testmodus.

---

## 3. Scope (Avgrensning)

### 3.1 Inkludert i v1 / v1.1 (Kjerneflyt + HTML-tillegg)
* **Filinntak i minnet:** Opplasting av Saldobalanse (SB) og Hovedbok (HB) i CSV- (`,`, `;`, `\t`) og Excel-format (`.xlsx`) via `io.BytesIO`, inkludert håndtering av norske tallformater (`100 000,00`) og kolonnenormalisering.
* **Deterministisk internkontroll:**
  * Dobbelt bokføringskontroll ($\sum \text{Debet} = \sum \text{Kredit}$) i både SB og HB.
  * Kryssavstemming av bevegelse ($\text{IB} + \text{netto HB} = \text{UB}$) per konto med outer join mellom SB og HB.
* **NS 4102-mapping og nøkkeltall:** Klassifisering av 4-sifrede norske kontoer (1xxx–8xxx) og deterministisk utregning av resultat- og balansenøkkeltall.
* **KI-integrasjon med The AI Firewall:** OpenAI `gpt-4o-mini` med Pydantic Structured Outputs (`ManagementCommentary`), runtime firewall-assertions, post-valideringsvakt (`post_validate_ai_response`) og komplett frakoblet testmodus (`mock_mode=True`).
* **Streamlit-brukergrensesnitt:** Dashboard med sidepanel for valg av innebygde eksempeldatasett (Grønn sti: balansert / Rød sti: med avvik) eller egen filopplasting, visning av kontrollstatus, nøkkeltall og KI-analyse.
* **PDF-eksport:** In-memory PDF-styrepakke via ReportLab (`src/pdf_generator.py`).
* **HTML-eksport (Nytt i v1.1):** In-memory, selvstendig HTML-styrepakke (`src/html_report.py`) med inline CSS som kan åpnes direkte i nettleser uten Streamlit og uten nettverkstilgang.
* **Syntetiske testdata:** Eksempelfiler med kjent fasit i `data/sample/`.

### 3.2 Eksplisitt utenfor scope
* **Ingen utskifting av Streamlit:** UI-et skal ikke byttes ut med en frittstående HTML-applikasjon eller Single Page Application (SPA). HTML-leveransen er kun en nedlastbar rapportfil i tillegg til PDF.
* **Ingen eksterne ressurser i HTML:** Ingen Chart.js eller andre biblioteker fra CDN, ingen eksterne stilark eller fonter, og ingen JavaScript-beregninger.
* **Ingen reskontro eller operative tilleggskilder:** Kundereskontro, leverandørreskontro, CRM-data, timelister og ESG-rapportering er utelatt (begrunnet i `docs/01_analysis/AVVIK_FRA_PROPOSAL.md`).
* **Ingen SAF-T (XML):** Kompleks XML-parsing av SAF-T Financial er flyttet til fremtidige faser.
* **Ingen flervaluta:** Kun NOK støttes i v1/v1.1.
* **Ingen direkte ERP-API eller Altinn:** Ingen integrasjon mot Fiken/Tripletex API eller innsending til Altinn/Skatteetaten.
* **Ingen autentisering eller betaling:** Ingen brukerinnlogging, rollebasert tilgang eller Stripe-betaling.
* **Ingen chatbot:** Ingen fritekst-chat mot regnskapet.

---

## 4. Epics og Brukerhistorier (User Stories)

### Epic 1: Dataopptak og Validering
*Mål: Sikre robust in-memory inntak av norske regnskapsfiler og umiddelbar matematisk kontroll av dobbelt bokføring.*

* **Story 1.1: Sikker filopplasting og norsk formatnormalisering**
  * **Brukerhistorie:** Som daglig leder ønsker jeg å laste opp Saldobalanse (SB) og Hovedbok (HB) som CSV- eller Excel-filer (inkludert norske eksportformater med semikolon og desimalkomma) i minnet, slik at jeg kan kontrollere regnskapet uten manuell filkonvertering eller lagring på disk.
  * **Kravkobling:** FR-1.1, FR-1.2, NFR-3.1, NFR-5.1
  * **Testbare akseptkriterier:**
    1. CSV med `,`, `;` eller `\t` og tegnsett `utf-8-sig`, `utf-8` eller `latin1` leses fra `io.BytesIO` uten diskskriving.
    2. Norske tallformater som `"100 000,00"` og `"15.000,25"` konverteres feilfritt til `float`.
    3. Kolonnevarianter som `Kontonr`, `Konto ID`, `Debetbeløp`, `Kreditbeløp`, `IB Beløp` og `UB Beløp` normaliseres til standardnavnene `Konto`, `Kontonavn`, `Debet`, `Kredit`, `IB`, `UB`.
    4. Tom fil eller manglende påkrevde kolonner (`Konto`, `Debet`, `Kredit`) reiser `ValueError` med norsk forklaring.
  * **Pytest-referanse:** `tests/test_data_pipeline.py::TestDataPipelineEdgeCases::test_norwegian_semicolon_and_comma_decimal`, `test_excel_file_processing`, `test_parametrized_invalid_csv_inputs`, `test_validate_input_detects_empty_dataframe`, `test_missing_account_column_raises_clear_error`, `test_empty_file_raises_clear_error`, `test_clean_norwegian_numeric_series`, `test_norwegian_erp_column_variations`, `test_mixed_decimal_and_spaces_in_currency`
  * **Status:** Implementert

* **Story 1.2: Dobbelt bokføringskontroll ($\sum \text{Debet} = \sum \text{Kredit}$)**
  * **Brukerhistorie:** Som regnskapsfører eller daglig leder ønsker jeg at systemet umiddelbart stopper prosesseringen dersom $\sum \text{Debet} \neq \sum \text{Kredit}$ i Saldobalansen eller Hovedboken, slik at jeg aldri rapporterer på et matematisk ubalansert regnskap.
  * **Kravkobling:** FR-1.3
  * **Testbare akseptkriterier:**
    1. `validate_balance()` bruker `np.isclose(..., atol=0.01)` og returnerer `True` når differansen er $\le 0,01$ NOK.
    2. Ved differanse $> 0,01$ NOK reises `ValueError` med strengen `"BALANSEFEIL (Debet ≠ Kredit)"` og nøyaktig differansebeløp med to desimaler.
    3. I UI-et blokkeres Steg 2 (nøkkeltall, KI-rapport og eksport) dersom `sb_ok` eller `hb_ok` er `False`.
  * **Pytest-referanse:** `tests/test_compliance.py::TestComplianceEngine::test_validate_balance_success`, `test_validate_balance_failure`, `test_validate_sample_files`
  * **Status:** Implementert

---

### Epic 2: Kryssavstemming og NS 4102-mapping
*Mål: Verifisere logisk konsistens mellom transaksjonslogg (HB) og saldobalanse (SB), samt beregne deterministiske nøkkeltall.*

* **Story 2.1: Kryssavstemming mellom Hovedbok og Saldobalanse ($\text{IB} + \Delta \text{HB} = \text{UB}$)**
  * **Brukerhistorie:** Som daglig leder ønsker jeg at systemet automatisk kontrollerer at $\text{IB} + \sum(\text{Debet}_{\text{HB}} - \text{Kredit}_{\text{HB}}) = \text{UB}$ for samtlige kontoer på tvers av SB og HB, slik at feilkonteringer eller manglende bilag avdekkes med kontonummer og beløp før styremøtet.
  * **Kravkobling:** FR-2.1, FR-2.2
  * **Testbare akseptkriterier:**
    1. `reconcile_hb_with_sb(sb_df, hb_df)` utfører en `outer` join på `Konto` slik at også kontoer som kun finnes i HB eller kun i SB fanges opp.
    2. For `saldobalanse_balansert.csv` + `hovedbok_balansert.csv` returneres `is_reconciled == True` og `discrepancy_count == 0`.
    3. For `saldobalanse_balansert.csv` + `hovedbok_med_avvik.csv` returneres `is_reconciled == False`, `discrepancy_count == 2`, og konto `1500` og `1920` flagges med `abs(Avvik) == 30000.0`.
  * **Pytest-referanse:** `tests/test_compliance.py::TestComplianceEngine::test_reconciliation_happy_path`, `test_reconciliation_detects_discrepancy`, `test_reconciliation_account_only_in_hb_detected`, `test_reconciliation_account_only_in_sb_with_zero_movement`
  * **Status:** Implementert

* **Story 2.2: Mapping til NS 4102 og deterministisk nøkkeltallsberegning**
  * **Brukerhistorie:** Som daglig leder ønsker jeg at kontoene klassifiseres etter NS 4102 og at resultat- og balansenøkkeltall beregnes deterministisk i Python, slik at nøkkeltallene er 100 % etterprøvbare og fri for KI-hallusinasjoner.
  * **Kravkobling:** FR-2.3, FR-2.4
  * **Testbare akseptkriterier:**
    1. `map_to_ns4102()` mapper `1xxx` til `"Eiendeler (NS 4102)"`, `2xxx` til `"Egenkapital og Gjeld (NS 4102)"`, `3xxx` til `"Salgs- og Driftsinntekt (NS 4102)"`, `4xxx–7xxx` til `"Driftskostnader (NS 4102)"`, `8xxx` til `"Finans og Skatt (NS 4102)"`, og øvrige til `"Ukjent / Udefinert"`.
    2. `calculate_detailed_financial_metrics()` beregner deterministisk `driftsinntekter`, `varekostnad`, `bruttofortjeneste`, `bruttomargin`, `lonnskostnad`, `andre_driftskostnader`, `samlede_driftskostnader`, `ebit`, `driftsmargin`, `ordinart_resultat`, `bankinnskudd`, `kundefordringer`, `leverandorgjeld`, `arbeidskapital` og `likviditetsgrad_1`.
    3. For balansert eksempeldata (`saldobalanse_balansert.csv`) er `driftsinntekter == 200000.0`, `samlede_driftskostnader == 90000.0`, `ebit == 110000.0` og `driftsmargin == 55.0`.
  * **Pytest-referanse:** `tests/test_compliance.py::TestComplianceEngine::test_ns4102_mapping`, `test_calculate_detailed_financial_metrics`
  * **Status:** Implementert

---

### Epic 3: KI-rapportering og Frakoblet Sensormodus
*Mål: Produsere et strukturert, Pydantic-validert ledelsesnotat over The AI Firewall, med fullverdig lokal mock-modus.*

* **Story 3.1: Strukturert KI-ledelsessammendrag via The AI Firewall**
  * **Brukerhistorie:** Som daglig leder ønsker jeg et strukturert ledelsesnotat på norsk (CFO-tone) med hovedkonklusjon, lønnsomhetsanalyse, likviditetsvurdering, revisors avstemmingsnotat, faresignaler og prioritert tiltaksliste, slik at jeg kan legge frem en gjennomarbeidet analyse for styret.
  * **Kravkobling:** FR-3.1, FR-3.2
  * **Testbare akseptkriterier:**
    1. `build_financial_context()` sender kun aggregerte nøkkeltall og avstemmingsoppsummering, verifisert med runtime-assertion `assert "raw_transactions" not in payload`.
    2. Både live API (`gpt-4o-mini`, `temperature=0.2`) og mock-modus returnerer en gyldig instans av Pydantic-modellen `ManagementCommentary`.
    3. `post_validate_ai_response()` sikrer at KI-teksten ikke motsier avstemmingsstatusen.
  * **Pytest-referanse:** `tests/test_reporting.py::TestReportingAndExport::test_ai_firewall_context_never_contains_raw_transactions`, `test_pydantic_schema_consistency_between_mock_and_class`, `test_live_api_flow_with_mocked_openai_client`, `test_post_validate_ai_response_catches_contradictions`
  * **Status:** Implementert

* **Story 3.2: Frakoblet sensormodus (Mock KI)**
  * **Brukerhistorie:** Som sensor ønsker jeg å kjøre hele applikasjonen lokalt uten OpenAI API-nøkkel via en forhåndsvalgt testmodus-bryter, slik at jeg kan verifisere både grønn sti (balansert) og rød sti (avvik i hovedbok) helt frakoblet.
  * **Kravkobling:** FR-3.3, NFR-1.2
  * **Testbare akseptkriterier:**
    1. Når `mock_mode=True` eller `api_key` er tom, utføres ingen nettverkskall.
    2. Ved `is_reconciled=True` returneres et godkjent `ManagementCommentary`-objekt; ved `is_reconciled=False` returneres et `ManagementCommentary`-objekt med `"ADVARSEL"` i `hovedkonklusjon` og omtale av feil på konto 1500 og 1920 i `revisors_avstemmingsnotat`.
  * **Pytest-referanse:** `tests/test_reporting.py::TestReportingAndExport::test_mock_mode_generates_valid_commentary`, `test_mock_mode_with_discrepancies`
  * **Status:** Implementert

---

### Epic 4: PDF-styrepakke og Dashboard-visning
*Mål: Presentere innsikten oversiktlig i Streamlit og levere en nedlastbar PDF-rapport.*

* **Story 4.1: Nedlasting av PDF-styrepakke i minnet**
  * **Brukerhistorie:** Som daglig leder ønsker jeg å laste ned en ferdig formatert PDF-rapport med tittel, avstemmingsstatus, ledelsesanalyse, faresignaler og tiltakstabell, slik at jeg kan distribuere en utskriftsklar styrepakke.
  * **Kravkobling:** FR-4.1, FR-4.2
  * **Testbare akseptkriterier:**
    1. `generate_management_pdf()` bygger PDF-en i `io.BytesIO` uten å skrive til disk, håndterer norske spesialtegn (`ÆØÅ`) og store tall, og returnerer en buffer som starter med `%PDF-`.
    2. I Streamlit-grensesnittet tilbys nedlasting med filnavn `Styrepakke_Ledelsesrapport.pdf`.
  * **Pytest-referanse:** `tests/test_reporting.py::TestReportingAndExport::test_pdf_generation_produces_valid_pdf_buffer`, `tests/test_data_pipeline.py::TestDataPipelineEdgeCases::test_large_numbers_and_norwegian_special_characters_pdf`
  * **Status:** Implementert

---

### Epic 5: Presentasjonsklar HTML-styrepakke (Nytt i v1.1)
*Mål: Levere en selvstendig, responsiv og offline-klar HTML-styrepakke fra nøyaktig samme verifiserte datakilde som PDF-en, uten å endre regnskapskjernen.*

* **Story 5.1: Nedlasting av selvstendig HTML-styrepakke i minnet**
  * **Brukerhistorie:** Som daglig leder vil jeg laste ned én selvstendig HTML-fil (med samme innhold som PDF: tittel, nøkkeltall, avstemmingsstatus, avvikstabell og ledelsesnotat) slik at jeg kan åpne styrepakken direkte i en nettleser på PC, nettbrett eller mobil uten Streamlit og uten ekstern CSS/JS.
  * **Kravkobling:** FR-5.1, FR-5.2, FR-5.3, FR-5.4, FR-5.5, FR-5.6
  * **Testbare akseptkriterier:**
    1. **Dedikert modul og låst funksjonssignatur uten forretningslogikk (K5):** HTML-generatoren plasseres i egen modul `src/html_report.py` med den eksakte funksjonssignaturen:
       ```python
       def generate_management_html(
           company_name: str,
           ai_report: ManagementCommentary,
           metrics: dict,
           recon_result: Optional[Dict[str, Any]] = None
       ) -> io.BytesIO:
       ```
       Modulen inneholder kun presentasjon/serialisering (HTML-mal med inline CSS og `html.escape`-sikring), ingen regnskapsberegninger.
    2. **In-memory og selvforsynt:** Returnerer en `io.BytesIO`-buffer kodet i UTF-8 som starter med `<!DOCTYPE html>`, inneholder `<html lang="nb">`, inline `<style>`, og **ingen** eksterne `<script src=...>` eller `<link rel="stylesheet" href=...>`. Ingen filer skrives til disk.
    3. **Tallkonsistens (Ingen avvik mellom Python, PDF og HTML):** Alle nøkkeltall (`driftsinntekter`, `samlede_driftskostnader`, `ebit`, `driftsmargin`, `bruttofortjeneste`, `bruttomargin`, `arbeidskapital`, `likviditetsgrad_1`), avstemmingsresultat (`recon_result`) og KI-kommentarer (`ManagementCommentary`) sendes ferdig utregnet fra Python inn i generatoren. Ingen tall regnes ut i HTML, JavaScript eller av språkmodellen.
    4. **Visuell status, kontrast og responsivitet (K4):**
       * Grønn statusboks (`#16a34a` / lys grønn bakgrunn `#f0fdf4`, mørk tekst `#14532d`) når `is_reconciled == True`, med tydelig tomtilstand for avvikstabellen (*«Ingen avstemmingsavvik oppdaget mellom Hovedbok og Saldobalanse (0 avvik).»*).
       * Rød varselboks (`#b91c1c` / lys rød bakgrunn `#fef2f2`, mørk tekst `#7f1d1d`) når `is_reconciled == False`, etterfulgt av en formatert HTML-tabell med de uavstemte kontoene (`Konto`, `Kontonavn`, `IB`, `Netto_HB`, `Beregnet_UB`, `UB`, `Avvik`).
       * Responsiv layout via CSS Grid / Flexbox og `@media (max-width: 640px)` samt `@media print`, med WCAG 2.1 AA-kontrast ($\ge 4,5:1$).
    5. **XSS-sikring og norske spesialtegn (K3 / K5):** All dynamisk tekst (`company_name`, `Kontonavn`, samt tekstfeltene i `ManagementCommentary` og `ActionItem`) renses med `html.escape()` før innsetting i HTML-malen, og norske tegn (`ÆØÅ`) gjengis feilfritt i UTF-8.
    6. **Streamlit-integrasjon:** I `src/app.py` (under «Eksport til Styret») plasseres en `st.download_button` for HTML (`📥 Last ned Styrepakke (HTML)`, filnavn `Styrepakke_Ledelsesrapport.html`, `mime="text/html"`) side om side med PDF-nedlastingsknappen.
    7. **Automatisk verifikasjon i pytest (K3):** Dedikerte tester i `tests/test_reporting.py` åpner HTML-bufferen og verifiserer gyldig HTML-struktur, at EBIT (`110 000`) og driftsmargin (`55,0 %` / `55.0 %`) fra fasit vises, at avvikskontoene (`1500` og `1920`) vises når testdata har avvik, at `html.escape()` beskytter mot spesialtegn, og at ingen rå transaksjonslinjer (bilagsnummer/enkeltposteringer fra HB) finnes i HTML-en.
  * **Pytest-referanse:** `tests/test_reporting.py::TestReportingAndExport::test_html_generation_produces_valid_self_contained_html`, `tests/test_reporting.py::TestReportingAndExport::test_html_generation_includes_discrepancies_and_excludes_raw_transactions`
  * **Status:** Implementert

---

## 5. Funksjonelle Krav (FR-tabell)

| ID | Krav | Akseptkriterium (Testbart) | Automatisk Test (`pytest`) | Sensor-kriterium (1–7) | Status |
|:---|:---|:---|:---|:---:|:---|
| **FR-1.1** | **In-memory filinntak (CSV & Excel)** | Systemet leser `.csv` (autodeteksjon av `;`, `,`, `\t` samt `utf-8-sig`/`latin1`) og `.xlsx` via `io.BytesIO` uten å lagre filer på disk, og konverterer norske tallformater (`100 000,00`) til `float`. | `tests/test_data_pipeline.py::test_norwegian_semicolon_and_comma_decimal`, `test_excel_file_processing`, `test_clean_norwegian_numeric_series`, `test_mixed_decimal_and_spaces_in_currency` | K2, K3, K7 | Implementert |
| **FR-1.2** | **Kolonnenormalisering og validering** | Synonymer (`Kontonr`, `Konto ID`, `Debetbeløp`, `IB Beløp` m.fl.) mappes til `Konto`, `Kontonavn`, `Debet`, `Kredit`, `IB`, `UB`. Tomme filer eller manglende påkrevde kolonner avvises med norsk `ValueError`. | `tests/test_data_pipeline.py::test_parametrized_invalid_csv_inputs`, `test_validate_input_detects_empty_dataframe`, `test_missing_account_column_raises_clear_error`, `test_empty_file_raises_clear_error`, `test_norwegian_erp_column_variations` | K2, K3, K4 | Implementert |
| **FR-1.3** | **Balansekontroll ($\sum D = \sum K$)** | `validate_balance()` verifiserer at $\sum \text{Debet} = \sum \text{Kredit}$ med toleranse $\le 0,01$ NOK for både SB og HB. Ved avvik $> 0,01$ reises `ValueError("BALANSEFEIL...")` og videre analyse stoppes i UI. | `tests/test_compliance.py::test_validate_balance_success`, `test_validate_balance_failure`, `test_validate_sample_files` | K2, K3, K4 | Implementert |
| **FR-2.1** | **Kryssavstemming ($\text{IB} + \Delta \text{HB} = \text{UB}$)** | `reconcile_hb_with_sb()` beregner $\text{Netto\_HB} = \sum \text{Debet} - \sum \text{Kredit}$ per konto og sjekker $\text{Beregnet\_UB} = \text{IB} + \text{Netto\_HB}$ mot $\text{UB}$ via outer join. | `tests/test_compliance.py::test_reconciliation_happy_path`, `test_reconciliation_account_only_in_hb_detected`, `test_reconciliation_account_only_in_sb_with_zero_movement` | K2, K3 | Implementert |
| **FR-2.2** | **Avviksrapportering per konto** | Ved differanse $> 0,01$ NOK returneres `is_reconciled = False`, `discrepancy_count` og DataFrame `discrepancies` med kolonnene `Konto`, `Kontonavn`, `IB`, `Netto_HB`, `Beregnet_UB`, `UB`, `Avvik`. | `tests/test_compliance.py::test_reconciliation_detects_discrepancy` | K2, K3, K4 | Implementert |
| **FR-2.3** | **NS 4102 Kontoplanmapping** | `map_to_ns4102()` klassifiserer 4-sifrede kontonumre deterministisk til `1xxx` Eiendeler, `2xxx` Egenkapital og Gjeld, `3xxx` Salgs- og Driftsinntekt, `4xxx–7xxx` Driftskostnader, `8xxx` Finans og Skatt. | `tests/test_compliance.py::test_ns4102_mapping` | K2, K3 | Implementert |
| **FR-2.4** | **Deterministisk nøkkeltallsmotor** | `calculate_detailed_financial_metrics()` beregner driftsinntekter, varekostnad, bruttofortjeneste, bruttomargin, lønn, andre driftskostnader, EBIT, driftsmargin, ordinært resultat, arbeidskapital og likviditetsgrad 1 i Pandas. | `tests/test_compliance.py::test_calculate_detailed_financial_metrics` | K1, K2, K3 | Implementert |
| **FR-3.1** | **AI Firewall Payload-begrensning** | `build_financial_context()` sender utelukkende ferdig aggregerte nøkkeltall og avviksoppsummering til LLM. Valideres med `assert "raw_transactions" not in payload`. | `tests/test_reporting.py::test_ai_firewall_context_never_contains_raw_transactions` | K1, K3, K5 | Implementert |
| **FR-3.2** | **Strukturert LLM-utdata (Pydantic)** | `generate_management_report()` returnerer alltid et validert `ManagementCommentary`-objekt (enten fra `gpt-4o-mini` via Structured Outputs eller fra mock), kontrollert av `post_validate_ai_response()`. | `tests/test_reporting.py::test_pydantic_schema_consistency_between_mock_and_class`, `test_live_api_flow_with_mocked_openai_client`, `test_post_validate_ai_response_catches_contradictions` | K1, K2, K3, K5 | Implementert |
| **FR-3.3** | **Frakoblet Sensormodus (Mock KI)** | Når `mock_mode=True` (standard i UI), returneres et deterministisk `ManagementCommentary`-objekt lokalt uten API-nøkkel, tilpasset om `is_reconciled` er `True` eller `False`. | `tests/test_reporting.py::test_mock_mode_generates_valid_commentary`, `test_mock_mode_with_discrepancies` | K2, K3, K6 | Implementert |
| **FR-4.1** | **In-memory PDF-generering** | `generate_management_pdf()` bygger en formatert PDF med tittel, revisjonsstatus, ledelsesnotat, faresignaler og tiltakstabell i `io.BytesIO` (`%PDF-`). | `tests/test_reporting.py::test_pdf_generation_produces_valid_pdf_buffer`, `tests/test_data_pipeline.py::test_large_numbers_and_norwegian_special_characters_pdf` | K2, K3, K4 | Implementert |
| **FR-4.2** | **PDF-nedlasting i UI** | Streamlit-knapp laster ned PDF-bufferen som `Styrepakke_Ledelsesrapport.pdf` (`mime="application/pdf"`). | `tests/test_reporting.py::test_pdf_generation_produces_valid_pdf_buffer` + manuell UI-verifikasjon | K2, K4 | Implementert |
| **FR-5.1** | **Dedikert in-memory HTML-modul** | `src/html_report.py::generate_management_html(company_name, ai_report, metrics, recon_result=None) -> io.BytesIO` bygger én selvstendig HTML5-fil (`<!DOCTYPE html>`, UTF-8) i `io.BytesIO` med inline CSS, uten eksterne CSS/JS/font-lenker og uten diskskriving. | `tests/test_reporting.py::test_html_generation_produces_valid_self_contained_html` | K1, K2, K5, K7 | Implementert |
| **FR-5.2** | **Deterministisk tallkonsistens i HTML** | HTML-rapporten mottar samme `ManagementCommentary`-objekt, ferdig utregnede nøkkeltall (`metrics`) og `recon_result` som resten av appen. Ingen beregning skjer i HTML/JS/LLM. Inneholder EBIT og driftsmargin fra fasit, og aldri rå transaksjonslinjer. | `tests/test_reporting.py::test_html_generation_produces_valid_self_contained_html` | K1, K2, K3, K5 | Implementert |
| **FR-5.3** | **Avstemmingsstatus og avvikstabell i HTML** | HTML-rapporten viser grønn godkjent-boks og tydelig tomtilstand når `is_reconciled == True`, og rød varselboks samt full avvikstabell (`Konto`, `Kontonavn`, `IB`, `Netto_HB`, `Beregnet_UB`, `UB`, `Avvik`) når `is_reconciled == False`. | `tests/test_reporting.py::test_html_generation_includes_discrepancies_and_excludes_raw_transactions` | K2, K3, K4 | Implementert |
| **FR-5.4** | **Tilgjengelighet og responsivitet i HTML** | HTML-rapporten bruker semantiske HTML5-elementer, norsk språk (`lang="nb"`), WCAG AA-kontrast ($\ge 4,5:1$), responsiv visning for smal skjerm (`@media (max-width: 640px)`) og utskriftsstilark (`@media print`). | `tests/test_reporting.py::test_html_generation_produces_valid_self_contained_html` | K4, K5 | Implementert |
| **FR-5.5** | **HTML-nedlasting i Streamlit UI** | `src/app.py` viser en nedlastingsknapp (`📥 Last ned Styrepakke (HTML)`) ved siden av PDF-knappen som leverer `Styrepakke_Ledelsesrapport.html` (`mime="text/html"`). | `tests/test_reporting.py::test_html_generation_produces_valid_self_contained_html` + manuell UI-test | K2, K4 | Implementert |
| **FR-5.6** | **XSS-sikring og UTF-8 spesialtegn i HTML** | All dynamisk tekst (`company_name`, `Kontonavn` og tekstfelter fra `ManagementCommentary`) escapes med `html.escape()` før innsetting i HTML-malen, og norske tegn (`ÆØÅ`) gjengis uten tegnsettfeil. | `tests/test_reporting.py::test_html_generation_produces_valid_self_contained_html` | K3, K5 | Implementert |

---

## 6. Ikke-funksjonelle Krav (NFR)

| ID | Kategori | Spesifikasjon | Verifikasjon |
|:---|:---|:---|:---|
| **NFR-1.1** | **The AI Firewall** | Språkmodellen (`gpt-4o-mini`) skal **aldri** utføre addisjon, subtraksjon, marginberegning eller avstemming. Alle tall beregnes deterministisk i Python/Pandas før de sendes som read-only kontekst, og tekstresponsen valideres via Pydantic (`ManagementCommentary`). | Runtime `assert` i `src/llm_integration.py` + `test_ai_firewall_context_never_contains_raw_transactions`. |
| **NFR-1.2** | **Frakoblet Sensormodus** | Applikasjonen skal fungere 100 % lokalt og offline uten OpenAI API-nøkkel, ekstern database, Docker eller betalte skytjenester når «Bruk testmodus (Mock KI)» er aktivert. | Standardvalg i `src/app.py` + `test_mock_mode_generates_valid_commentary`. |
| **NFR-2.1** | **Ytelse (< 5 sekunder)** | Lokal innlesing, balansekontroll, kryssavstemming, nøkkeltallsberegning, mock-KI og generering av både PDF og HTML for datasett opp til 5 000 rader skal fullføres på under 5 sekunder. | Vektoriserte Pandas-operasjoner og in-memory generering. |
| **NFR-3.1** | **Minnesikkerhet (In-Memory)** | Opplastede regnskapsfiler (`.csv`, `.xlsx`) og genererte styrepakker (`.pdf`, `.html`) skal behandles utelukkende i minnet (`io.BytesIO`) og aldri skrives til disk. | Kodeinspeksjon av `src/data_pipeline.py`, `src/pdf_generator.py` og `src/html_report.py`. |
| **NFR-3.2** | **Ingen hemmeligheter i repo** | Ingen API-nøkler eller passord skal ligge i kildekode eller git-historikk. `.env` ignoreres i `.gitignore`, og `.env.example` dokumenterer variabelnavn uten nøkkel. | Sjekk ved oppstart (`check_env_security()`) og `.gitignore`. |
| **NFR-4.1** | **Universell utforming (WCAG)** | Både Streamlit-UI, PDF og HTML-styrepakke skal benytte semantiske statusfarger (grønn `#16a34a` ved godkjent, rød `#b91c1c` ved avvik, mørk blå `#1e3a8a` for struktur) kombinert med tekstlig statusetikett og kontrastforhold $\ge 4,5:1$. | Gjennomgang mot `docs/03_ux/UX_DESIGN_OG_WIREFRAMES.md`. |
| **NFR-5.1** | **Norske regnskapsstandarder** | Støtte for semikolon (`;`) og komma (`,`) som feltskilletegn, mellomrom/punktum som tusenskilletegn og komma som desimaltegn (`100 000,00`), samt mapping mot NS 4102. | `test_norwegian_semicolon_and_comma_decimal` og `test_ns4102_mapping`. |
| **NFR-6.1** | **Plattform og Python-versjon** | Kjører på Python 3.10–3.11 på Windows, macOS og Linux via `pip install -r requirements.txt` og `streamlit run app.py`. Ingen nye tredjeparts C-avhengigheter skal introduseres for HTML-eksporten (bruker kun Python standardbibliotek + eksisterende stack). | CI-arbeidsflyt (`.github/workflows/ci.yml`) og `requirements.txt`. |

---

## 7. Sporbarhetsmatrise (Story $\rightarrow$ FR $\rightarrow$ Modul i `src/` $\rightarrow$ Testfunksjon $\rightarrow$ Sensor-kriterium)

Denne matrisen dokumenterer ende-til-ende-sporbarhet fra brukerhistorie til kildekode og automatisert test:

| Epic / Story | FR-ID | Modul og funksjon i `src/` | Testfunksjon i `tests/` | Sensor-kriterium | Status |
|:---|:---|:---|:---|:---:|:---|
| **Epic 1 / Story 1.1** | FR-1.1 | `src/data_pipeline.py::detect_csv_delimiter_and_encoding`, `clean_norwegian_numeric_series`, `process_csv_in_memory`, `process_excel_in_memory` | `tests/test_data_pipeline.py::TestDataPipelineEdgeCases::test_norwegian_semicolon_and_comma_decimal`, `test_excel_file_processing`, `test_clean_norwegian_numeric_series`, `test_mixed_decimal_and_spaces_in_currency` | K2, K3, K7 | Implementert |
| **Epic 1 / Story 1.1** | FR-1.2 | `src/data_pipeline.py::normalize_column_names`, `validate_input` | `tests/test_data_pipeline.py::TestDataPipelineEdgeCases::test_parametrized_invalid_csv_inputs`, `test_validate_input_detects_empty_dataframe`, `test_missing_account_column_raises_clear_error`, `test_empty_file_raises_clear_error`, `test_norwegian_erp_column_variations` | K2, K3, K4 | Implementert |
| **Epic 1 / Story 1.2** | FR-1.3 | `src/compliance_engine.py::validate_balance`, `src/app.py` | `tests/test_compliance.py::TestComplianceEngine::test_validate_balance_success`, `test_validate_balance_failure`, `test_validate_sample_files` | K2, K3, K4 | Implementert |
| **Epic 2 / Story 2.1** | FR-2.1 | `src/compliance_engine.py::reconcile_hb_with_sb` | `tests/test_compliance.py::TestComplianceEngine::test_reconciliation_happy_path`, `test_reconciliation_account_only_in_hb_detected`, `test_reconciliation_account_only_in_sb_with_zero_movement` | K2, K3 | Implementert |
| **Epic 2 / Story 2.1** | FR-2.2 | `src/compliance_engine.py::reconcile_hb_with_sb`, `src/app.py` | `tests/test_compliance.py::TestComplianceEngine::test_reconciliation_detects_discrepancy` | K2, K3, K4 | Implementert |
| **Epic 2 / Story 2.2** | FR-2.3 | `src/compliance_engine.py::map_to_ns4102` | `tests/test_compliance.py::TestComplianceEngine::test_ns4102_mapping` | K2, K3 | Implementert |
| **Epic 2 / Story 2.2** | FR-2.4 | `src/compliance_engine.py::calculate_detailed_financial_metrics`, `src/app.py` | `tests/test_compliance.py::TestComplianceEngine::test_calculate_detailed_financial_metrics` | K1, K2, K3 | Implementert |
| **Epic 3 / Story 3.1** | FR-3.1 | `src/llm_integration.py::build_financial_context` | `tests/test_reporting.py::TestReportingAndExport::test_ai_firewall_context_never_contains_raw_transactions` | K1, K3, K5 | Implementert |
| **Epic 3 / Story 3.1** | FR-3.2 | `src/llm_integration.py::ManagementCommentary`, `ActionItem`, `generate_management_report`, `post_validate_ai_response` | `tests/test_reporting.py::TestReportingAndExport::test_pydantic_schema_consistency_between_mock_and_class`, `test_live_api_flow_with_mocked_openai_client`, `test_post_validate_ai_response_catches_contradictions` | K1, K2, K3, K5 | Implementert |
| **Epic 3 / Story 3.2** | FR-3.3 | `src/llm_integration.py::generate_management_report` (`mock_mode=True`) | `tests/test_reporting.py::TestReportingAndExport::test_mock_mode_generates_valid_commentary`, `test_mock_mode_with_discrepancies` | K2, K3, K6 | Implementert |
| **Epic 4 / Story 4.1** | FR-4.1, FR-4.2 | `src/pdf_generator.py::generate_management_pdf`, `src/app.py` | `tests/test_reporting.py::TestReportingAndExport::test_pdf_generation_produces_valid_pdf_buffer`, `tests/test_data_pipeline.py::TestDataPipelineEdgeCases::test_large_numbers_and_norwegian_special_characters_pdf` | K2, K3, K4 | Implementert |
| **Epic 5 / Story 5.1** | FR-5.1, FR-5.2, FR-5.4, FR-5.5, FR-5.6 | `src/html_report.py::generate_management_html`, `src/app.py` | `tests/test_reporting.py::TestReportingAndExport::test_html_generation_produces_valid_self_contained_html` | K1, K2, K3, K4, K5 | Implementert |
| **Epic 5 / Story 5.1** | FR-5.3 | `src/html_report.py::generate_management_html` | `tests/test_reporting.py::TestReportingAndExport::test_html_generation_includes_discrepancies_and_excludes_raw_transactions` | K2, K3, K4, K5 | Implementert |

---

## 8. Beslutningslogg og Lukkede Dokumentasjonshull (K5–K7)

Følgende punkter ble identifisert under revisjonen til v1.1 og er nå **ferdig lukket og verifisert**:

1. **Konsistent testantall på tvers av dokumentasjonen (K3 / K6) — LUKKET:**
   * `pytest -v tests/` har nå **30** beståtte tester (9 i `test_compliance.py`, 12 inkl. parametriserte i `test_data_pipeline.py`, og 9 i `test_reporting.py`).
   * Tidligere avvik mellom `README.md` og `docs/KVALITETSSIKRING_OG_TESTING.md` er nå synkronisert til **30** i alle filer.
2. **Synkronisering av arkitektur- og UX-dokumentasjon etter Epic 5 (K1 / K4 / K5) — LUKKET:**
   * Mappestrukturen og dataflytdiagrammet i `docs/04_architecture/ARCHITECTURE.md`, wireframes i `docs/03_ux/UX_DESIGN_OG_WIREFRAMES.md`, testtabellen i `docs/KVALITETSSIKRING_OG_TESTING.md` og filoversikten i `README.md` er oppdatert med `src/html_report.py` slik at planleggingsdokumentene samsvarer 100 % med levert kode.
3. **Clone-URL i README (K6) — VERIFISERT:**
   * `README.md` peker direkte til kurs-repositoriet `https://github.com/IBE160-2026/G56-guimaraes.git`.
4. **Skille mellom faglærers rammeverksfiler og studentens utviklingsverktøy (K1 / K7) — FASTSATT:**
   * Eventuelle utdelte kursmaler (som `CLAUDE.md` eller `.claude/skills/sesjonslogg`) er faglærers utdelte rammeverk og skal aldri omtales som om applikasjonen ble utviklet i Claude Code. Utviklingsverktøyet i prosjektet G56 er utelukkende **Google Gemini Antigravity**.

---

## 9. Endringslogg

| Versjon | Dato | Forfatter | Beskrivelse av endring |
|:---|:---|:---|:---|
| **v1.0** | 2026-10-15 | Victor Guimaraes (G56) | Første utgave av PRD basert på revidert `product-brief.md` (Epic 1–4: Filinntak, Balanse- og kryssavstemming, KI-rapport med Mock-modus og PDF-eksport). |
| **v1.1** | 2026-11-02 | Victor Guimaraes (G56) / `bmad-agent-pm` | **Godkjent v1.1 — Lagt til Epic 5 (FR-5.1 til FR-5.6): Presentasjonsklar HTML-styrepakke.** Låst funksjonssignatur for `src/html_report.py::generate_management_html`, lagt til eksplisitt XSS-sikringskrav (`html.escape` i FR-5.6), oppdatert sporbarhetsmatrise med alle 26 eksisterende pytest-tester og planlagte HTML-tester, strammet kravkoblinger mot sensorveiledningens 7 kriterier, og dokumentert åpne punkter for K5–K7. **Hvorfor dette ikke endrer regnskapskjernen:** HTML-eksporten (`src/html_report.py`) er en ren visnings- og serialiseringsmodul nedstrøms for *The AI Firewall*. Den leser kun de allerede beregnede og testede datastrukturene fra `compliance_engine.py` og `llm_integration.py` (`ManagementCommentary`), og påvirker verken filinnlesing, balansekontroll ($\sum D = \sum K$), kryssavstemming ($\text{IB} + \text{HB} = \text{UB}$), NS 4102-mapping eller PDF-generering. |
