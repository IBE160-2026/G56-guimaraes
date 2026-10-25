# Addendum til Product Brief — Omfangsjustering etter faglærers tilbakemelding

**Dato:** Oktober 2026  
**Prosjekt:** G56 — Ledelsesrapport og regnskapskontroll med KI  
**Referanse:** `tilbakemelding-product-brief.md` og `course/sensorveiledning.md`

---

## 1. Hensikten med dette addendumet
Etter innlevering av det opprinnelige prosjektforslaget mottok gruppen grundig tilbakemelding fra faglærer. Faglærer påpekte at det opprinnelige konseptet favnet for bredt (både bankavstemming, OCR-tolkning av fakturaer, skattemelding og full revisjonskontroll) og innebar for høy implementasjonsrisiko for et enkelt semesterprosjekt.

Dette addendumet formaliserer de konkrete endringene som er gjort i prosjektets omfang og arkitektur for å sikre toppscore i henhold til sensorveiledningens kriterier.

---

## 2. Hovedgrep og omfangsavgrensning

| Område i opprinnelig forslag | Ny avgrensning i v1 (Spisset Kjerne) | Begrunnelse og faglig gevinst |
| :--- | :--- | :--- |
| **Kildedata:** Banktransaksjoner, PDF-bilag, saldobalanse, reskontro. | **KUN Saldobalanse (SB) og Hovedbok (HB)** i CSV/Excel. | Eliminerer feilkilder fra OCR og ustandardiserte bankformater. Etablerer en bunnsolid regnskapsmessig sammenheng. |
| **Balansekontroll:** Generell anomalisjekk. | **Formell dobbelt bokføringskontroll:** $\sum \text{Debet} = \sum \text{Kredit}$. | Grunnleggende regnskapsstandard. Sikrer at ubalanserte datasett stoppes før analyse. |
| **Avstemming:** Bankavstemming mot kontoutdrag. | **Kryssavstemming HB mot SB:** $IB + \Delta HB = UB$. | Avdekker transaksjoner som mangler i hovedboken eller feilaktig postering mot feil konto direkte i regnskapsmotoren. |
| **Kontoplan:** Ingen standardisert mapping. | **Mapping mot NS 4102:** Standard 4-sifrede norske kontoklasser (1000–8999). | Gjør det mulig å beregne deterministiske nøkkeltall (EBIT, bruttomargin, driftsmargin) uavhengig av ERP-system. |
| **Rollefordeling Kode vs. KI:** KI ble foreslått til å analysere rådata direkte. | **"The AI Firewall":** Python/Pandas regner ut alt. KI-en mottar kun ferdige tall og forfatter et profesjonelt styrenotat. | Eliminerer risikoen for tallhallusinasjoner fullstendig. |
| **Sensorvennlighet:** Krevde eksterne API-nøkler og miljøvariabler. | **Integrert Mock-modus og eksempeldata:** Kjøres 100 % lokalt og offline. | Sensor kan evaluere hele systemet på 2 minutter uten kostnad eller oppsett av nøkler. |

---

## 3. Konklusjon og sporbarhet
Endringene reduserer teknisk gjeld og sikrer full sporbarhet fra faglærers tilbakemelding til ferdig kodebase. Systemet demonstrerer høy regnskapsfaglig forståelse, solid programvarearkitektur og moden styring av kunstig intelligens.
