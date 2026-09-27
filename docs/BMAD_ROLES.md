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
