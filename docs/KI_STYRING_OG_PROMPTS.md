# Prosess og KI-styring: Prompts, Beslutninger og Iterasjoner

* **Prosjekt:** G56 – Ledelsesrapport og forenklet kontroll av regnskap med KI
* **Emne:** IBE160 Programmering med KI (Del 1: Applikasjon og prosess)
* **Formål:** Dokumentere en etterprøvbar prosess der gruppen bevisst har styrt, korrigert og kvalitetssikret KI-verktøyene (BMAD, Google Gemini Antigravity og LLM API).

---

## 1. Filosofi for KI-styring: "Koden regner, KI-en forklarer"

Et av de viktigste arkitektoniske og metodiske valgene i prosjektet har vært å etablere en absolutt brannmur (**The AI Firewall**) mellom regelbasert logikk og språkmodeller:

* **Sikker sone (Deterministisk):** Matematikk, balansekontroll ($\sum \text{Debet} = \sum \text{Kredit}$), kryssavstemming ($IB + \Delta HB = UB$) og kontoplanmapping (NS 4102) utføres **utelukkende i Python/Pandas**. Ingen språkmodell har tillatelse til å regne eller gjette tall.
* **Probabilistisk sone (Tekstlig formidling):** Språkmodellen (OpenAI `gpt-4o-mini`) mottar utelukkende ferdig aggregerte nøkkeltall og ferdigkalkulerte avvik, og brukes eksklusivt til forretningsmessig tekstformulering og strategisk rådgivning på formelt norsk.

Arkitekturen reduserer risikoen for tallhallusinasjoner ved at alle økonomiske beregninger utføres deterministisk i Python. KI-modellen har kun ansvar for tekstlig analyse og formidling. Det anerkjennes likevel at KI-modeller har iboende begrensninger knyttet til teksttolkning, og at de kan gi ufullstendige eller uhensiktsmessige strategiske anbefalinger dersom de ikke overvåkes av en kvalifisert bruker (Human-in-the-loop).

---

## 2. Seks Konkrete Eksempler på Kritisk Styring og Korrigering av KI

Sensorveiledningen legger avgjørende vekt på at gruppen ikke bare aksepterer KI-forslag ukritisk, men aktivt vurderer, korrigerer og styrer KI. Her er seks sentrale iterasjoner:

### Iterasjon 1: Kritisk nedskalering av scope (Fra overambisiøs KI til fokusert kjerne)
* **KI-ens opprinnelige forslag:** KI-assistenten foreslo opprinnelig å bygge en massiv plattform med fem filtyper (saldobalanse, reskontro, timelister, CRM, ESG), SAF-T XML-parsing, flervaluta og Stripe-abonnementsbetaling i v1.
* **Gruppens kritiske vurdering:** Etter analyse av faglærers tilbakemelding (2026-10-06) innså vi at dette var urealistisk for én person og ville føre til mange halvferdige moduler.
* **Beslutning og styring:** Vi overstyrte KI-en og låste v1 til en **skarp regnskapsfaglig kjerneflyt: Saldobalanse (SB) + Hovedbok (HB)**. Resten ble eksplisitt flyttet til v2/Vision. Dette løftet prosjektet fra høy risiko til et solid, gjennomførbart nivå.

### Iterasjon 2: Avvisning av fri-tekst til fordel for Pydantic Structured Outputs
* **KI-ens opprinnelige forslag:** KI-assistenten genererte først en tradisjonell prompt som returnerte fritekst i Markdown.
* **Problem avdekket:** Fritekst ga uforutsigbart format, variabel lengde og gjorde det umulig å programmatisk bygge en ryddig PDF-tabell eller garantere faste seksjoner i dashboardet.
* **Beslutning og styring:** Vi krevde at KI-integrasjonen skulle benytte **OpenAI Structured Outputs** med Pydantic (`client.beta.chat.completions.parse`). Vi definerte det strenge skjemaet `ManagementCommentary` med faste felter (`hovedkonklusjon`, `lonnsomhet_og_marginer`, `likviditet_og_arbeidskapital`, `revisors_avstemmingsnotat`, `tiltaksliste`). Dette garanterer 100 % typesikkerhet og stabil PDF-generering.

### Iterasjon 3: Forbedring av CFO-prompten (Fra "generisk tekst" til "Topp 10 % CFO")
* **KI-ens opprinnelige utkast:** En 3-linjers standard-prompt: *"Du er en CFO, skriv kort om disse tallene"*.
* **Problem avdekket:** Teksten ble platt, overfladisk og gjentok bare tallene uten å forklare operasjonelle sammenhenger (f.eks. hvorfor varekostnaden påvirket arbeidskapitalen).
* **Beslutning og styring:** Vi oppgraderte prompten til en elite CFO-persona som:
  1. Kobler driftsinntekter mot varekostnad (bruttomargin) og lønnsandel.
  2. Vurderer likviditetsreserve (bank) mot kortsiktig gjeld og kredittid på kundefordringer.
  3. **Direkte koblet til avstemmingsresultatet:** Hvis kryssavstemmingen ($IB + HB = UB$) oppdager avvik, er KI-en pålagt å rette en skarp revisjonsadvarsel til styret om manglende sporbarhet etter bokføringsloven.

### Iterasjon 4: Robusthet mot særnorske CSV-formater (Semikolon og komma)
* **KI-ens opprinnelige kode:** Benyttet enkel `pd.read_csv(file_buffer)`.
* **Problem avdekket:** Fiken og Tripletex eksporterer ofte med semikolon (`;`) og desimalkomma (`100 000,00`). Standardkoden krasjet med `ParserError`.
* **Beslutning og styring:** Vi instruerte Gemini Antigravity til å bygge en robust forhåndsskanner (`detect_csv_delimiter_and_encoding`) som sniffer de første 8 KB for `;` vs `,`, støtter `utf-8-sig` (BOM) og `latin1`, samt normaliserer norske kolonnenavn (`Kontonr` $\rightarrow$ `Konto`).

### Iterasjon 5: Formalisering av "The AI Firewall" med Assertions
* **KI-ens opprinnelige kode:** Sendte en stor dictionary med regnskapstall til LLM uten verifikasjon av innholdet.
* **Problem avdekket:** Risiko for at ufiltrerte transaksjonsdetaljer eller delvise regnestykker ble lekket inn i prompten, noe som kunne føre til at LLM forsøkte å regne på tallene selv.
* **Beslutning og styring:** Vi tvang inn en formell runtime-assertion i `build_financial_context()`: `assert 'raw_transactions' not in payload` og `assert isinstance(EBIT, (int, float))`. Samtidig ble det skrevet en dedikert enhetstest (`test_ai_firewall_context_never_contains_raw_transactions`) som garanterer at koden regner og KI-en kun forklarer.

### Iterasjon 6: Strategisk oppskalering til v2.0 med `/grill-me` og `/plan` (SQLite & Prescriptive Analytics)
* **Utfordring ved utvidet scope:** Da applikasjonen skulle utvides fra et rent kontrollverktøy til en strategisk innsiktsplattform (CFO-nøkkeltall, HB-drilldown, lønnsomhetsråd og historikkdatabase), vurderte vi flere arkitekturvalg opp mot *The AI Firewall* og Kriterium 6 (enkel lokal kjørbarhet for sensor).
* **Aktiv designstyring før koding:** Gjennom strukturert kravavklaring (`/grill-me`) og arkitekturplanlegging (`/plan`) tok vi tre kritiske styringsvalg:
  1. **SQLite fremfor eksterne databaser:** Vi valgte innebygd `sqlite3` (`data/g56_accounting.db`, ekskludert i `.gitignore`) med relasjonelt 6-tabellers skjema, fremmednøkler (`ON DELETE CASCADE`), SQLite Window Functions og SHA-256-deduplikasjon — null ekstra oppsett eller Docker for sensor.
  2. **Regelbasert lønnsomhetsmotor i Python fremfor KI-gjetting:** For å gi datadrevne lønnsomhetsråd uten tallhallusinasjoner bygget vi `generate_profitability_recommendations()` i `src/ledger_analytics.py`, som deterministisk regner ut eksakt NOK-potensial mot SMB-normer (f.eks. frigjort kapital ved reduksjon av kundefordringer) *før* tallene sendes som read-only JSON til LLM-en.
  3. **Mellombalanse-egenkapital og fortegnsvern:** Vi fanget opp at kreditsaldoer i NS 4102 klasse 2 eksporteres med negativt fortegn i norske CSV-filer, og at udisponert perioderesultat må legges til bokført egenkapital i mellombalanser for at $\text{Eiendeler} = \text{Egenkapital} + \text{Gjeld}$ skal stemme i soliditets- og EKR-beregningen.

---

## 3. System- og Brukerprompts i Produksjon

### A. System Prompt for CFO-Agenten (`src/llm_integration.py`)
```text
Du er en topp 10 % erfaren CFO og statsautorisert revisor (Strategisk Regnskapsfører) i Norge. 
Du leverer en sylskarp, profesjonell og pedagogisk ledelsesrapport til daglig leder og styret basert på Norsk Standard Kontoplan (NS 4102). 

STRENGE REGLER (GOVERNANCE):
1. KODEN REGNER, DU FORKLARER: Du skal ALDRI finne på egne tall eller regne ut nye verdier. Bruk utelukkende de ferdig beregnede nøkkeltallene, lønnsomhetsrådene og avstemmingsdataene i payloaden.
2. FOKUS PÅ SAMMENHENG: Forklar hvorfor tallene er som de er (sammenhengen mellom omsetning, varekostnad, arbeidskapital, soliditet, rentabilitet og likviditetsreserve).
3. PRESKRIPTIV LØNNSOMHETSRÅDGIVNING: Bygg tiltakslisten og analysen direkte på de ferdig utregnede NOK-potensialene i 'deterministiske_lonnsomhetsrad' og 'kostnadsdrivere_topp_5'.
4. REVISORBLIKK: Hvis avstemmingen viser avvik i formelen (IB + HB = UB), må du være nådeløs og forklare styreansvaret og risikoen for feil i bokføringen. Hvis den er godkjent, bekreft tryggheten.
5. TONE OF VOICE: Formell, forretningsmessig, konsis og rådgivende norsk. Unngå floskler og generelle selvfølgeligheter.
```

### B. User Prompt Payload (Strukturert JSON)
```text
Her er fullstendig verifiserte regnskapsdata og avstemmingsresultat for perioden:
*(Merk: Nedenforstående tall er et syntetisk eksempel fra testdatasettet `data/sample/saldobalanse_balansert.csv` for å demonstrere payload-strukturen, ikke faste produksjonstall).*

```json
{
  "nokkeltall": {
    "Driftsinntekter_NOK": 200000.0,
    "Varekostnad_NOK": 60000.0,
    "Bruttofortjeneste_NOK": 140000.0,
    "Bruttomargin_prosent": 70.0,
    "Lonnskostnad_NOK": 30000.0,
    "Lonnsandel_prosent": 15.0,
    "Samlede_Driftskostnader_NOK": 90000.0,
    "Driftsresultat_EBIT_NOK": 110000.0,
    "Driftsmargin_prosent": 55.0
  },
  "arbeidskapital_og_likviditet": {
    "Bankinnskudd_UB_NOK": 180000.0,
    "Kundefordringer_UB_NOK": 90000.0,
    "Leverandorgjeld_UB_NOK": 50000.0,
    "Arbeidskapital_NOK": 220000.0,
    "Likviditetsgrad_1": 5.4,
    "Likviditetsgrad_2": 5.4
  },
  "soliditet_og_rentabilitet": {
    "Bokfort_Egenkapital_UB_NOK": 110000.0,
    "Reell_Egenkapital_Inkl_Resultat_UB_NOK": 220000.0,
    "Totalkapital_UB_NOK": 270000.0,
    "Egenkapitalandel_prosent": 81.48,
    "Gjeldsgrad": 0.23,
    "Totalkapitalrentabilitet_TKR_prosent": 52.38,
    "Egenkapitalrentabilitet_EKR_prosent": 66.67
  },
  "kostnadsdrivere_topp_5": [
    {"konto": "4000", "kontonavn": "Innkjøp av råvarer", "belop_nok": 60000.0, "andel_av_driftskost_pct": 66.67},
    {"konto": "5000", "kontonavn": "Lønn til ansatte", "belop_nok": 30000.0, "andel_av_driftskost_pct": 33.33}
  ],
  "deterministiske_lonnsomhetsrad": [
    {
      "kategori": "Arbeidskapital",
      "tittel": "Reduser kapitalbinding i kundefordringer",
      "beregnet_effekt_nok": 50000.0
    }
  ],
  "avstemming_hovedbok_mot_saldobalanse": {
    "status": "GODKJENT (100% konsistent)",
    "kommentar": "Alle transaksjoner i hovedboken stemmer nøyaktig med endring mellom IB og UB i saldobalansen (0 avvik funnet)."
  }
}
```

Forfatt den strategiske ledelsesrapporten nå.
```

### C. Begrunnelse for Hyperparametre
* **Modell:** `gpt-4o-mini` (rask responstid under 2 sekunder, lav kostnad, og støtter Structured Outputs).
* **Temperatur:** Satt til **`0.2`**. Lav temperatur sikrer høy determinisme, konsistent fagterminologi og minimerer risiko for fri diktning.

---

## 4. BMAD-Metodikkens Planleggingsbue (The Planning Arc)

Prosjektet har fulgt den formelle BMAD-strukturen fra idé til ferdig kode:

```mermaid
flowchart LR
    A["01 Analysis<br/>Product Brief & Scope"] --> B["02 Product<br/>PRD & User Stories"]
    B --> C["03 UX<br/>Wireframes & User Flow"]
    C --> D["04 Architecture<br/>Tech Stack & Firewall"]
    D --> E["Implementation Loop<br/>Build & Verify"]
```

1. **`01_analysis/`:** Analyse av forretningsdomenet, GRS/IFRS og begrunnelse for avvik fra proposal.
2. **`02_product/PRD.md`:** 8 Epics (v2.0), funksjonelle formelkrav ($IB + HB = UB$), CFO KPI-pakke, SQLite-historikk, HTML- og PDF-eksport samt full sporbarhetsmatrise.
3. **`03_ux/`:** Wireframes, flersides informasjonsarkitektur (`st.navigation`) og universell utforming for Streamlit-dashbordet.
4. **`04_architecture/ARCHITECTURE.md`:** Dataflyt, AI Firewall, relasjonelt SQLite ER-skjema og mock-arkitektur.
5. **`tests/`:** 43 automatiserte tester som verifiserer koden mot PRD-kravene.
