# Prosjektplan: Ledelsesrapport og forenklet kontroll av regnskap med KI

Dette er fremdriftsplanen for utviklingen av vår applikasjon gjennom høstsemesteret, basert på "Agentic Programming" med BMAD-rammeverket. Planen beskriver hva som skal gjøres når, og forklarer hvordan de ulike fasene i emnet anvendes direkte for å bygge og forbedre vår spesifikke løsning.

## Uke 35–36 (24.08 – 06.09): Verktøy og infrastruktur (Tools of the Trade)
* **Hva gjøres:** Grunnleggende oppsett av tradisjonelle utviklingsverktøy, pakkehåndtering, samt introduksjon til KI-utviklingsverktøy og Context Engineering.
* **Bruk i prosjektet:** Vi setter opp kodemiljøet, GitHub-repositoriet (`G56-guimaraes`) og installerer nødvendige biblioteker (f.eks. Python, Streamlit, Pandas). Vi gjør klart fundamentet og verktøykassen som de KI-drevne kodingsagentene våre vil trenge når de etter hvert skal programmere selve rapport-generatoren.

## Uke 37 (07.09 – 13.09): BMAD-rammeverket (The BMAD Method)
* **Hva gjøres:** Innføring i BMAD (et smidig, modell-agnostisk rammeverk) med fokus på de ulike fasene fra idé til byggeklart prosjekt (The Planning Arc) og implementeringssløyfen.
* **Bruk i prosjektet:** Vi tar i bruk BMAD-metodikken for å strukturere prosjektet vårt formelt. Metodikken sikrer en ryddig overgang fra idéfasen vår (Product Brief / proposal) til en byggeklar backlog med konkrete "stories" (oppgaver) for utvikling av fileksport, AI-Revisor og LLM-sammendrag.

## Uke 38 (14.09 – 20.09): Agentic Programming
* **Hva gjøres:** Teoretisk og praktisk innføring i Agentic Programming – inkludert "vibe programming", "context engineering" og CLI-baserte kodingsagenter. Man ser på behovet for rammeverk (som BMAD) på toppen av kodingsagenter.
* **Bruk i prosjektet:** Vi setter "Agentic Programming" ut i praksis. I stedet for at vi skriver hver linje med Python-kode manuelt for datavask av saldobalansen eller formatering av PDF, delegerer vi selve implementeringen til KI-agenter. Ved å bruke "context engineering" gir vi agenten en presis beskrivelse av bedriftens ERP-logikk og hva appen skal gjøre, slik at agenten koder med riktig kontekst.

## Uke 39–40 (21.09 – 04.10): Context Engineering & MCP
* **Hva gjøres:** Dypdykk i hvordan Large Language Models (LLMs) fungerer som resonneringsmotorer, prompt engineering, agenter med "memory" og introduksjon til Model Context Protocol (MCP).
* **Bruk i prosjektet:** Dette er helt kritisk for selve kjernen i plattformen vår. Vi designer system-prompts som instruerer LLM-en i å analysere de ferdig utregnede tallene (fra Cross-Data Fusion Engine), og utforme det skriftlige ledelsessammendraget. Vi sørger for at KI-en har riktig arkitektur til å koble operasjonelle data uten å hallusinere tall.

## Uke 41 (05.10 – 11.10): Google Antigravity Fundamentals
* **Hva gjøres:** Spisset fokus på verktøyet Google Antigravity som kode-assistent.
* **Bruk i prosjektet:** Vi bruker Google Antigravity operativt i terminalen for å iterere på Streamlit-brukergrensesnittet (opplastingslogikken for CSV) og for å debugge eventuelle feil underveis i utviklingen.

## Uke 42 (12.10 – 18.10): Prosjektoppsett og planlegging (Scope & Tech Stack)
* **Hva gjøres:** Utarbeidelse av Project Scope, definering av MVP (Minimum Viable Product), teknologistack, og forberedelse til BMADs planleggingsarbeidsflyt.
* **Bruk i prosjektet:** Her spikres innholdet i v1 av vår plattform. Vi slår fast at MVP-en skal støtte CSV-opplasting, mapping til NS 4102, og kjøres lokalt via Streamlit (Python), mens direkte API-koblinger mot Fiken/Tripletex legges ut av scope.

## Uke 43 (19.10 – 25.10): BMAD-rollene i praksis (Analysis, PM, UX, Architecture)
* **Hva gjøres:** Rollene Business Analyst, Product Manager (PRD), UX Designer (UI) og Architect kjøres for å spesifisere applikasjonen i detalj før kodingen starter.
* **Bruk i prosjektet:** 
  - **PM & Analyst:** Dokumenterer kravene for hvordan systemet skal takle feil ved opplasting av ukurante Excel-filer.
  - **UX:** Designer et friksjonsløst Streamlit-dashboard der brukeren kun laster opp to filer og trykker "Generer rapport".
  - **Architect:** Definerer dataflyten fra filopplasting -> Pandas Datavask -> LLM API -> Generering av PDF.

## Uke 44 (26.10 – 01.11): Utviklingssyklusen (Development Cycle)
* **Hva gjøres:** Sprint-planlegging, opprettelse av oppgaver (Stories), implementering via utvikler-agenten, kodegjennomgang (Code Review) og kontinuerlig iterering.
* **Bruk i prosjektet:** Den faktiske kodingen av plattformen! Hver funksjon (som Revisor AI-sjekken for $Debet = Kredit$) blir en egen "Story". Koden skrives av en KI-agent, testes (ofte av en annen KI-agent eller oss), gjennomgås i `bmad-code-review`, og rettes kontinuerlig opp til modulen fungerer feilfritt.

## Uke 45 (02.11 – 08.11): Prosjektuke & Innlevering
* **Hva gjøres:** Prosjektuke uten ny lesing. Fase II-IV ferdigstilles og selve rapporten leveres.
* **Bruk i prosjektet:** Vi ferdigstiller MVP-en vår. Vi verifiserer at CSV-import, AI-analysen og PDF-eksporten henger sammen i én fungerende flyt, og ferdigstiller den akademiske prosjektrapporten for faget.

## Uke 46 (09.11 – 15.11): Drift, infrastruktur og CI/CD (DevOps & IaC)
* **Hva gjøres:** Prinsipper for Infrastructure as Code (IaC), containerisering (Docker), CI/CD-pipelines (GitHub Actions), samt overvåking av løsningen (Observability) i produksjon.
* **Bruk i prosjektet:** For at plattformen skal kunne brukes av reelle SMB-er, bygger vi en CI/CD-pipeline. Vi setter opp GitHub Actions slik at all ny kode testes automatisk. Vi "containeriserer" Streamlit-appen vår via Docker slik at den enkelt kan driftes (deployes) på en skyløsning, med monitorering for å sikre høy oppetid og ytelse (respons under 30 sekunder).

## Uke 47 (16.11 – 22.11): Oppsummering og Etikk (Retrospective)
* **Hva gjøres:** Gjennomgang av prosjektet fra start til slutt, evaluering av BMAD, etiske problemstillinger rundt KI og fremtidens utviklerrolle.
* **Bruk i prosjektet:** Vi evaluerer vår reise med appen. Vi diskuterer spesielt etikken rundt plattformen vår: Hva skjer dersom LLM-en gjør en feiltolkning av bedriftens økonomi? Hvem har ansvaret – revisor, daglig leder eller KI-en? Vi konkluderer med plattformens videre "Vision" mot å bli en autonom "Continuous AI CFO".
