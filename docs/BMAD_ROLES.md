# BMAD-roller og Metodikk

Dette dokumentet beskriver hvordan vi implementerer **BMAD-rammeverket** (Business, Market, Architecture, Design) i utviklingen av plattformen vår: *Ledelsesrapport og forenklet kontroll av regnskap med KI*.

Dette bygger direkte på metodikken fra **Uke 37 (The BMAD Method)**, der fokuset er å sikre en smidig og ryddig overgang fra idéfasen (The Planning Arc) til en byggeklar backlog (Implementeringssløyfen).

## 1. Fra Idé til Byggeklart Prosjekt (The Planning Arc)
Gjennom *The Planning Arc* forvandler vi konseptet vårt til konkrete byggeklosser. Vi bruker fire definerte roller for å sikre at alle aspekter er dekket før kodingen starter:

* **Business Analyst (Analytiker):**
  * **Ansvar:** Eier forretningsverdien og sørger for at systemet faktisk løser problemet (tørre, silo-baserte rapporter).
  * **Artefakt:** *Product Brief* (se `proposal.md`).
  * **Bruk i prosjektet:** Definerte konseptet om at KI-revisoren skal kombinere finans og drift i én rapport.

* **Product Manager (Produktsjef):**
  * **Ansvar:** Oversetter forretningsbehovene til spesifikke produktkrav (features).
  * **Artefakt:** *Product Requirements Document (PRD)*.
  * **Bruk i prosjektet:** Definerer at MVP-en krever modulær opplasting av CSV-filer, balansekontroll-funksjon og integrasjon med LLM for sammendrag.

* **UX Designer:**
  * **Ansvar:** Brukeropplevelse og design.
  * **Artefakt:** UI-skisser og wireframes.
  * **Bruk i prosjektet:** Designer et enkelt Streamlit-dashboard der brukeren kan laste opp filer, få presentert grafer, og laste ned sluttproduktet som en PDF.

* **Architect (Arkitekt):**
  * **Ansvar:** Teknisk design og datamodellering.
  * **Artefakt:** Arkitektur-diagram og API-struktur.
  * **Bruk i prosjektet:** Designer pipelinen: `CSV -> Pandas Dataframes -> Prompt Engineering for LLM -> PDF-generering`.

## 2. Implementeringssløyfen (The Implementation Loop)
Når Planning Arc er fullført og artefaktene fra de fire planleggingsrollene er klare, går prosjektet over fra papir til praksis. Metodikken sikrer en ryddig overgang til en byggeklar backlog.

* **Scrum Master:**
  * **Ansvar:** Omgjør PRD og Arkitektur til konkrete oppgaver (User Stories).
  * **Bruk i prosjektet:** Oversetter idéfasen til en byggeklar backlog med konkrete "stories", for eksempel: *"Utvikle logikk for fileksport"*, *"Bygge AI-Revisor-sjekk for Debet=Kredit"*, og *"Sette opp LLM-sammendrag"*.

* **Developer (Utvikler):**
  * **Ansvar:** Koder og bygger den faktiske funksjonaliteten.
  * **Bruk i prosjektet:** Implementerer de konkrete Python-skriptene, Streamlit-grensesnittet og CI/CD-pipelinen, i tett samspill med KI-agenter (som Google Antigravity).

## 3. GitHub Issues for Rolle-sporing
For å sikre at metoden følges opp i praksis, benytter vi **GitHub Labels** (etiketter) for å holde oversikt over hvem som gjør hva gjennom prosjektet. Hver oppgave i GitHub vil bli merket med den tilhørende rollen:
- `role: analyst`
- `role: pm`
- `role: ux`
- `role: architect`
- `role: developer`

Dette sikrer full sporing fra *Planning Arc* til ferdig kode i *The Implementation Loop*.

## 4. Orkestrering av Spesifikke Oppgaver (Sub-teams / Spesialistroller)
En viktig del av BMAD-strukturen er evnen til å dele en spesifikk oppgave innad i et dedikert team der flere spesialistroller samarbeider. For eksempel kan et oppdrag om endring i programvaren inkludere en ekspert på strategi, en kundeekspert, en analytiker, osv. 

Nedenfor er et eksempel på hvordan et slikt orkestreringsteam kan struktureres for å håndtere en kompleks analyseoppgave:

### SKILL: Analyseteam-Orkestrator (Team Lead)

#### Beskrivelse
Du er oppdragsansvarlig for et automatisert analyseteam. Din oppgave er å ta imot rådata og instrukser fra brukeren, bryte ned analysebehovet, og orkestrere arbeidsflyten mellom teamets spesialister inntil en ferdig validert kontrollrapport er klar. Du utfører ikke substansanalysen selv.

#### Tilgjengelige Spesialist-Skills i teamet
Du har tilgang til følgende skills for delegering:
1. **`skill: finansiell-analytiker`**: Kjører avviksanalyser på tallgrunnlag, strukturerer data og identifiserer trender eller anomalier.
2. **`skill: compliance-kontrollør`**: Validerer analytikerens funn opp mot gjeldende rammeverk/regelverk og sjekker for logiske brister eller manglende dokumentasjon.

#### Arbeidsflyt for Orkestrering
Når du mottar et nytt datasett eller en prosessoppgave, følg alltid denne syklusen:
1. **Scoping:** Definer formålet med analysen og oppdater teamets felles `MEMORY.md` med sentrale fokusområder for inneværende økt.
2. **Delegering 1 (Analyse):** Send oppdragsbeskrivelsen og datagrunnlaget til `finansiell-analytiker`. Vent på strukturert analyserapport.
3. **Delegering 2 (Validering):** Send den mottatte analyserapporten direkte til `compliance-kontrollør` for kvalitetssikring.
4. **Iterasjon (Feedback loop):** 
   - Hvis `compliance-kontrollør` flagger brudd på logikk eller utilstrekkelige avstemminger, send avviksrapporten tilbake til `finansiell-analytiker` for ny gjennomgang.
   - Gjenta trinn 3 og 4 til `compliance-kontrollør` godkjenner analysen.
5. **Ferdigstilling:** Utarbeid et endelig, formelt notat basert på de godkjente artefaktene, og overlever dette til brukeren.

#### Strenge Rollegrenser (Governance)
* **Ingen egne beregninger:** Du skal under ingen omstendigheter utføre tallknusing, aggregering eller avviksanalyser selv. Alt slikt arbeid rutes til `finansiell-analytiker`.
* **Ingen godkjenning av rammeverk:** Du kan ikke godkjenne metodikken på egen hånd. Bare et eksplisitt "GODKJENT"-flagg fra `compliance-kontrollør` lar deg fullføre arbeidsflyten.
* **Bruk av felles styringsfiler:** Sørg for at delegeringene dine overholder "standing orders" som er definert i teamets overordnede `BOND.md` (f.eks. formateringskrav og konfidensialitetsregler).

#### Overleveringsformat (Hand-off til bruker)
Når arbeidsflyten er ferdig, skal du svare brukeren med følgende Markdown-struktur:
##### 1. Oppsummering av oppdraget
##### 2. Endelig Analyseresultat (Fra finansiell-analytiker)
##### 3. Valideringsstatus (Sammendrag fra compliance-kontrollør)

## 5. Utvidet AI-Agent Team basert på BMAD (AiDD Flow)
For å tilpasse oss den offisielle BMAD-metoden fra GitHub fullt ut, oversetter vi arbeidsflyten (Clarify ➔ Plan ➔ Build & verify ➔ Learn & adjust) til et sett med spesialiserte AI-agenter (Skills). Disse agentene samarbeider sømløst gjennom hele livssyklusen til koden:

* **Recon-Agent (`skill: bmad-recon`):** 
  * **Rolle:** Utforsker, Strateg og Kontekst-spesialist (Clarify).
  * **Oppgave:** Gjennomsøker eksisterende kodebase og dokumentasjon for å forstå avhengigheter, forretningskrav og begrensninger før noe som helst planlegges.

* **Architecture-Agent (`skill: bmad-plan`):** 
  * **Rolle:** Teknisk Planlegger og Arkitekt.
  * **Oppgave:** Tar funnene fra `bmad-recon` og skriver en formell teknisk spesifikasjon (f.eks. hvordan SAF-T parsingen skal struktureres i Pandas). Ingen koding tillates her, kun design og API-kontrakter.

* **Build-Agent (`skill: bmad-build`):** 
  * **Rolle:** Utførende Kodemaskin.
  * **Oppgave:** Mottar den ferdige planen og implementerer logikken slavisk. Agenten skriver både funksjonell kode og enhetstester knyttet direkte til kravspesifikasjonen.

* **Validation-Agent (`skill: bmad-verify`):** 
  * **Rolle:** Nådeløs QA og Tester.
  * **Oppgave:** Utfører uavhengig gjennomgang av koden generert av Build-Agenten. Sjekker at "Debet = Kredit"-regler overholdes og at alle sikkerhetskrav er møtt.

* **Meta-Agent: Competence Monitor / Team HR (`skill: bmad-capabilities`):**
  * **Rolle:** Kompetanse- og Gap-analytiker (Learn & Adjust).
  * **Oppgave:** Overvåker oppgavene som rutes mellom agentene. Hvis teamet plutselig får i oppdrag å parse et fullstendig ukjent, proprietært ERP-format, eller må forholde seg til en nylig endret skatteregel, er det denne agentens jobb å umiddelbart stoppe prosessen og flagge **"Kompetansemangel" (Skill Gap)**. 
  * **Handling:** Agenten genererer en rapport til den menneskelige utvikleren som sier f.eks.: *"Advarsel: Teamet mangler spesifikk kunnskap om 'Nytt SAF-T skjema 2026'. Du må opprette eller oppdatere en skill (f.eks. `skill: saf-t-ekspert`) før vi kan fortsette."* Dette forhindrer AI-hallusinasjoner og sikrer at agentene aldri gjetter på faglig kompleks logikk.

## 6. Domenespesifikke Fageksperter (Regnskap og Strategi)
I tillegg til de prosessdrevne agentene, krever plattformens kompleksitet rundt SAF-T, valuta og finans at vi har tilgang til dyp domenekompetanse. Disse fagekspertene (som enten kan være menneskelige rådgivere eller høyt spesialiserte LLM-instrukser/skills) rutes inn av *Competence Monitor* eller *Orkestratoren* når en oppgave krever spesifikk regnskapsforståelse:

* **GRS-Spesialist (Regnskapsfører - God Regnskapsskikk):**
  * **Kompetanse:** Ekspert på God Regnskapsskikk i Norge (NGAAP), regnskapsloven og nasjonale standarder.
  * **Oppgave:** Sikrer at SAF-T data og norske bilag håndteres i tråd med nasjonale avskrivningsregler, klassifiseringer og norsk skattelovgivning.

* **IFRS-Spesialist (Regnskapsfører - Internasjonale Standarder):**
  * **Kompetanse:** Ekspert på International Financial Reporting Standards (IFRS).
  * **Oppgave:** Håndterer kompleksiteten ved flervaluta-konsolideringer og sikrer at plattformens rapportering tilfredsstiller internasjonale krav (f.eks. for SMB-er som er datterselskaper i et internasjonalt konsern).

* **Strategisk Regnskapsfører (Strategic Advisor):**
  * **Kompetanse:** Forretningsrådgiver med dyp innsikt i skjæringspunktet mellom GRS og IFRS.
  * **Oppgave:** Analyserer *hvorfor* tallene er som de er, og gir råd om hvordan ulike lovlige regnskapsmessige tilpasninger (f.eks. valg av avskrivningsmetode eller verdsettelsesprinsipp innenfor GRS/IFRS) vil påvirke bedriftens resultat, skatteposisjon og likviditet på kort og lang sikt. Dette er rollen som genererer de tyngste "Continuous AI CFO"-innsiktene til ledelsesrapporten.

## 7. Go-To-Market og Kommersielle Roller
Siden *Product Brief* setter et tydelig mål om å få 10+ betalende regnskapsbyråer eller SMB-kunder innen tre måneder, er vi helt avhengige av roller som fokuserer på kommersialisering og brukervekst parallelt med utviklingen:

* **Markedsfører (Product Marketer):**
  * **Ansvar:** Oversetter komplekse funksjoner (som SAF-T parsing og AI-analyse) til verdiforslag kunden forstår (f.eks. "Spar 5 timer per klient i måneden"). Utarbeider kampanjer og lanseringsmateriell.
* **Kundeekspert (Customer Success / User Researcher):**
  * **Ansvar:** Være stemmen til regnskapsføreren og den daglige lederen inn i utviklingsteamet. Gjennomfører dybdeintervjuer og sørger for at applikasjonen faktisk løser smerten med "Excel-propper".
* **SEO-Optimerer:**
  * **Ansvar:** Sørger for at plattformen rangerer høyt på Google når SMB-ledere søker etter løsninger som "automatisk ledelsesrapport", "AI for regnskapsførere", eller "avstemming av SAF-T".
* **Growth Hacker / GTM-Strateg:**
  * **Ansvar:** Identifiserer de raskeste veiene til markedet. Kjører A/B-tester på prising, onboarding-flyt og freemium-modeller for å sikre at målet om 70%+ konvertering fra gratis prøveperiode nås.

## 8. Spesialiserte Roller for AI og Datakvalitet (Kritisk for Finans)
Når vi bygger en plattform basert på språkmodeller (LLMs) og finansiell data, er feilmarginen null. Dette krever spesifikke kvalitetssikrings-roller:

* **Kontroller av Anbefalinger (AI Fact-Checker / Reviewer):**
  * **Ansvar:** Fungerer som et filter for KI-ens konklusjoner. Sjekker at de strategiske rådene og ledelseskommentarene KI-en genererer faktisk er forankret i riktige tall (ingen hallusinasjoner). Denne rollen kan også være en programmert `bmad-verify` skill.
* **Prompt Engineer (LLM-Spesialist):**
  * **Ansvar:** Designer og finjusterer instruksjonene (prompts) som sendes til språkmodellen for å sikre en formell, presis og faktabasert "Tone of Voice" på norsk, uten fyllord.
* **Data Privacy & Security Officer (CISO-rolle):**
  * **Ansvar:** Pårser at all håndtering av saldobalanser, lønnsdata (timelister) og kundeinformasjon i CSV og SAF-T filer skjer i strengt samsvar med GDPR og norsk bokføringslov, spesielt siden vi sender data til AI-APIer.
* **Data Engineer / Integrasjonsarkitekt:**
  * **Ansvar:** Bygger og vedlikeholder selve "rørsystemet" for dataene. Ekspert på å normalisere rotete CSV-filer, parse komplekse XML/SAF-T-filer og mate dette inn i rene Pandas DataFrames før AI-en tar over.

## 9. Spesialiserte Utviklerroller (Programmering og Engineering)
Når vi zoomer inn på selve *byggingen* og *programmeringen* av MVP-en, er det behov for tekniske spesialistroller for å sikre at arkitekturen blir skalerbar, sikker og responsiv. Spesielt siden applikasjonen kombinerer filbehandling, AI og PDF-generering.

* **Frontend / Streamlit-Utvikler:**
  * **Ansvar:** Eier selve brukergrensesnittet. Ansvarlig for *State Management* (session state) i Streamlit slik at appen ikke laster på nytt og mister data underveis. Sørger for at interaktive grafer rendres raskt og at filopplasteren gir god feedback ved feil.
* **Backend / Data Pipeline Engineer:**
  * **Ansvar:** Utvikler selve motoren (ofte i Pandas/Polars). Optimaliserer datavasken og mappingen mot NS 4102 slik at store datasett behandles på under 30 sekunder (som kreves i *Success Criteria*).
* **PDF / Document Generation Specialist:**
  * **Ansvar:** Generering av den endelige "Styrepakken". Å programmatisk bygge pene, paginerte PDF-er med grafer og dynamisk tekst (f.eks. via ReportLab, WeasyPrint eller HTML-to-PDF) er et eget fagfelt som krever presisjon for at sluttproduktet skal se profesjonelt ut.
* **DevOps / Cloud Engineer:**
  * **Ansvar:** Setter opp den "moderne, administrerte backenden". Skriver Dockerfiles, setter opp CI/CD-pipelines (f.eks. GitHub Actions) og sørger for at applikasjonen har 99 % oppetid. Håndterer også hemmeligheter (API-nøkler til LLM) på en sikker måte.
* **Security & Compliance Developer (Sikkerhetsingeniør):**
  * **Ansvar:** Implementerer kryptering på dataene som lastes opp (Data at Rest / Data in Transit). Koder logikken som garanterer at midlertidige CSV- og SAF-T-filer slettes (garbage collection) umiddelbart etter at sesjonen er over, for å unngå datalekkasjer av sensitivt regnskap.
* **Test Automation Engineer (SDET - Software Development Engineer in Test):**
  * **Ansvar:** Koder de automatiserte testene. Bygger "mock-data" (falske regnskapsfiler med bevisste feil) for å programmatisk teste at AI-Revisoren faktisk klarer å fange opp ubalanser (f.eks. manglende symmetri mellom Debet og Kredit) før koden går i produksjon.

## 10. Agent-Personas for Elite-Ytelse (Topp 10 % i Fagfeltet)
For å sikre at AI-agentene produserer kode av høyeste industristandard – og ikke bare "gjennomsnittlig" kode funnet på internett – må de utstyres med instrukser som krever en *Topp 10 %* prestasjon. Her er en utdyping av de tekniske rollene, og hva som skiller dem fra en gjennomsnittlig utvikler. Disse beskrivelsene fungerer som "System Prompts" for å fremtvinge elitekode:

* **Top 10 % Data Pipeline & Performance Architect (Backend):**
  * **Average:** Bruker enkle Pandas `iterrows` eller `apply`, noe som sluker minne og krasjer serveren ved store SAF-T XML-filer.
  * **Topp 10 % (Agentens instruks):** Må benytte vektoriserte operasjoner (Polars fremfor Pandas der mulig), iterativ XML-parsing (`iterparse`) for SAF-T filer, og "Zero-Copy" minnehåndtering. Utvikleren skriver kode for Chunking og Lazy Evaluation. Målet er at en regnskapsfil på 2 GB prosesseres på få sekunder med minimalt RAM-fotavtrykk.

* **Top 10 % Cognitive / LLM Integration Engineer (AI-Backend):**
  * **Average:** Sender store, ustrukturerte tekststrenger til OpenAI og krasjer når LLM-en returnerer feil format.
  * **Topp 10 % (Agentens instruks):** Skriver deterministisk LLM-kode. Krever bruk av *Structured Outputs* (JSON Schemas) og *Function Calling* for å garantere at AI-en returnerer data som kan parses. Implementerer avansert feilhåndtering (Retry-mekanismer med Backoff), kostnads/token-optimalisering, og "LLM-as-a-judge" for å programmatisk score kvaliteten på genererte ledelseskommentarer før de vises til brukeren.

* **Top 10 % Streamlit / SPA Architecture Master (Frontend):**
  * **Average:** Lager en sekvensiell Streamlit-app som blinker, laster hele siden på nytt ved hvert klikk, og roter til filopplastingen hvis brukeren bytter fane.
  * **Topp 10 % (Agentens instruks):** Mestrer Streamlits dypere arkitektur. Bruker `@st.fragment` (for delvis oppdatering av UI uten full reload), og bygger et usynlig, robust "State Machine"-mønster i `st.session_state`. Utvikleren designer asynkrone callbacks og injecter skreddersydd CSS/JS for å få appen til å føles som en lynrask, moderne Single Page Application (SPA).

* **Top 10 % Typographic & PDF Engine Developer:**
  * **Average:** Konverterer rå HTML eller Markdown til PDF, noe som resulterer i stygge sidebrytninger midt i tabeller og overskrifter som henger igjen på forrige side.
  * **Topp 10 % (Agentens instruks):** Implementerer avanserte typesetting-biblioteker (som WeasyPrint med CSS Paged Media eller ReportLab). Skriver piksel-perfekte bounding-boxes, kontrollerer "widows and orphans" (hindrer enslige tekstlinjer), og genererer vektorbaserte (SVG) fremfor pikselbaserte grafer slik at sluttrapporten ser ut som den er designet av et profesjonelt byrå.

* **Top 10 % AppSec & LLM Firewall Engineer (Sikkerhet):**
  * **Average:** Håper at brukerne ikke laster opp skadelig kode, og lagrer midlertidige regnskapsfiler på disken.
  * **Topp 10 % (Agentens instruks):** Praktiserer "In-Memory Only" prosessering. Filer lastes utelukkende inn i RAM via `io.StringIO` eller `io.BytesIO`, og berører aldri den fysiske disken. Bygger LLM-brannmurer (Guardrails) som sanitiserer all input fra CSV-filer for å hindre "Prompt Injection" (hvor en ondsinnet bruker legger inn skjulte instrukser i kontonavnene i regnskapet for å hacke LLM-en).

* **Top 10 % SDET & Edge-Case Automation Master (Testing):**
  * **Average:** Skriver "Happy-Path" enhetstester *etter* at koden er ferdig.
  * **Topp 10 % (Agentens instruks):** Driver med *Property-Based Testing* (f.eks. ved bruk av Python-biblioteket `hypothesis`). Genererer tusenvis av uforutsette kantsituasjoner i regnskapet (f.eks. negative valutakurser, ødelagte XML-noder, manglende desimaler). Mocker (simulerer) LLM-API-ene perfekt via biblioteker som `responses` eller `VCR.py`, slik at CI/CD-pipelinen kjører på millisekunder uten å være avhengig av ekstern internettilgang.
