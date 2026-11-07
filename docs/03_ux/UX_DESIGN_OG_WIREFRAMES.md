# UX-Design, Wireframes og Brukerreise (Flersides Streamlit v2.0)

* **Dokument-ID:** UX-SPEC-01
* **Versjon:** v2.0
* **Prosjekt:** G56 – Ledelsesrapport og forenklet kontroll av regnskap med KI
* **Emne:** IBE160 Programmering med KI (Kriterium 4: Design og brukeropplevelse - 10 %)
* **Formål:** Dokumentere informasjonsarkitektur, flersides navigasjon (`st.navigation`), wireframes og universell utforming (WCAG).

---

## 1. Informasjonsarkitektur (Flersides Navigasjon)

For å romme utvidet CFO-analyse (Lønnsomhet, Likviditet, Soliditet, TKR og EKR), detaljert Hovedbok-utforsker, deterministiske lønnsomhetsråd og databasehistorikk *uten visuell overbelastning*, er applikasjonen delt inn i **fire dedikerte sider** via `st.navigation`:

1. **📂 1. Opplasting & Kontroll (`src/views/upload_and_control.py`):** 2x2 opplastingsrutenett, hurtigknapp for norsk semikolon-format, balansekontroll ($\sum D = \sum K$), kryssavstemming ($IB + HB = UB$) og status for automatisk SQLite-synkronisering.
2. **📊 2. Finansiell Analyse & HB (`src/views/financial_analysis.py`):** To strukturerte arbeidsfaner – (A) CFO KPI-dashboard med 12 nøkkeltall mot SMB-normer og kostnadsdrivere, og (B) Hovedbok-utforsker med filtre, kontokort med løpende saldo og bilagsinspektør.
3. **💡 3. KI-Rådgiver & Eksport (`src/views/ai_advisor_and_export.py`):** Pre-kalkulerte deterministiske lønnsomhetsråd i NOK fra Python, generering av strukturert KI-rapport over *The AI Firewall*, og ett-klikks nedlasting av PDF- og HTML-styrepakke.
4. **🗄️ 4. Historikk & Trendanalyse (`src/views/history_and_trends.py`):** Sammenligning av lagrede kjøringer fra `data/g56_accounting.db` over tid, trendgrafer for inntekt/EBIT/soliditet/rentabilitet, og gjenåpning/re-eksport av tidligere KI-rapporter.

---

## 2. Skjermbilde-Wireframes (ASCII)

### Side 1: Opplasting & Automatisk Internkontroll
```text
+------------------------------------------------------------------------------------------------------+
|  [Sidemeny: st.navigation] |  📂 1. Opplasting & Automatisk Internkontroll                           |
|  > 📂 1. Opplasting & Kont.|  [ ⚡ Norsk semikolon-format (100 000,00) ]   [ 🔄 Nullstill eksempel ] |
|    📊 2. Finansiell Analyse|                                                                         |
|    💡 3. KI-Rådgiver       |  +----------------------------------+  +--------------------------------+
|    🗄️ 4. Historikk (SQLite)|  | 📊 1. Saldobalanse (SB)          |  | 📘 2. Hovedbok (HB)            |
|  ------------------------- |  | [ Browse files (.csv / .xlsx) ]  |  | [ Browse files (.csv / .xlsx) ]|
|  ⚙️ Konfigurasjon          |  +----------------------------------+  +--------------------------------+
|  Selskapsnavn: [Bedrift AS]|                                                                         |
|  (•) Balansert (Grønn sti) |  🔍 Steg 1: Automatisk Internkontroll & Kryssavstemming                 |
|  ( ) Med avvik (Rød sti)   |  [ ✅ SB: Debet = Kredit ]            [ ✅ HB: Debet = Kredit ]         |
|  ( ) Egne filer            |  ⚖️ Kryssavstemming (IB + HB = UB): ✅ Full konsistens (0 avvik)       |
|  [x] Testmodus (Mock KI)   |  🗄️ SQLite Auto-Sync: Synkronisert som Kjøring #1 (Periode: 2026-01)   |
+------------------------------------------------------------------------------------------------------+
```

### Side 2: Finansiell Analyse & Hovedbok-Utforsker
```text
+------------------------------------------------------------------------------------------------------+
|  📊 2. Finansiell Analyse & Hovedbok-Utforsker                                                       |
|  [ 📈 CFO Nøkkeltalls-Dashboard (KPI-er) ]   [ 📘 Hovedbok-Utforsker (Drill-down & Bilagsinspektør) ]|
|  --------------------------------------------------------------------------------------------------- |
|  1. Lønnsomhet:  [ Driftsinnt.: 200k ] [ Bruttomargin: 70,0 % ] [ EBIT: 110k ] [ Driftsmargin: 55 % ]|
|  2. Likviditet:  [ Bank: 180k ]        [ Arbeidskap.: 220k ]    [ LG1: 5,40 ]  [ LG2: 5,40 ]         |
|  3. Soliditet:   [ EK-andel: 81,5 % ]  [ Gjeldsgrad: 0,23 ]     [ TKR: 52,4 %] [ EKR: 66,7 % ]       |
|                                                                                                      |
|  --- (I fanen Hovedbok-Utforsker): ---                                                               |
|  Filter: [ NS 4102: Alle v ]   [ Konto: 1500 Kundefordringer v ]   [ Søk: Faktura 101            ]   |
|  Kontokort 1500: IB 50 000 kr | Netto HB +40 000 kr | Beregnet UB 90 000 kr | Avvik 0,00 kr (Avstemt)|
|  Tabell med Løpende Saldo (SQLite Window Function) + 🧾 Bilagsinspektør per Bilagsnr                 |
+------------------------------------------------------------------------------------------------------+
```

### Side 3 & Side 4: Lønnsomhetsråd, KI-CFO & SQLite-Historikk
```text
+------------------------------------------------------------------------------------------------------+
|  💡 3. Lønnsomhetsråd, KI-Rådgiver & Eksport                                                         |
|  📐 Steg A: Deterministisk Lønnsomhetsmotor (Beregnet i Python)                                      |
|  +------------------------------------------------+ +----------------------------------------------+ |
|  | [Høy] Reduser kapitalbinding i kundefordringer | | [Medium] Optimaliser varekostnad (Konto 4000)| |
|  | 💰 Beregnet potensial: Frigjør 50 000 NOK      | | 💰 Beregnet potensial: Øker EBIT med 3 000 kr| |
|  +------------------------------------------------+ +----------------------------------------------+ |
|  🤖 Steg B: [ 🚀 Generer Strategisk Ledelsesrapport (KI) ] -> 4 analysefaner + Tiltaksliste          |
|  📄 Steg C: [ 📥 Last ned Ledelsesrapport (PDF) ]   [ 📥 Last ned Styrepakke (HTML) ]                |
+------------------------------------------------------------------------------------------------------+
```

---

## 3. Designprinsipper og Universell Utforming (WCAG 2.1 AA)

* **Semantisk trafikklys-hierarki (med tekstetiketter):**
  * 🟢 **Grønn (`#16a34a`):** Matematisk godkjent balanse, avstemt konto og nøkkeltall over norm (f.eks. `Sterk (≥ 2,0)` på LG1 og `Solid (≥ 30 %)` på Egenkapitalandel).
  * 🔴 **Rød (`#b91c1c`):** Balansefeil, avstemmingsavvik mellom HB og SB, og høyprioriterte risikovarsler.
  * 🔵 **Mørk marineblå (`#1e3a8a`):** Nøytral strukturfarge for CFO-typografi i PDF og HTML (kontrastforhold $> 8:1$ mot hvit bakgrunn).
* **Progressiv detaljering:** Brukeren tvinges ikke til å rulle gjennom lange tabeller; opplasting/kontroll, dyp tallanalyse, strategisk rådgivning og historikk har hver sin dedikerte arbeidsflate med bevart sesjonstilstand.
