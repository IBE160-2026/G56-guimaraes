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
