# Prosjektplan: Ledelsesrapport og forenklet kontroll av regnskap med KI (Kjerneversjon: Saldobalanse & Hovedbok)

Dette er fremdriftsplanen for utviklingen av vår applikasjon gjennom høstsemesteret i IBE160, basert på "Agentic Programming" med BMAD-rammeverket. Planen beskriver hva som skal gjøres når, og sikrer en sporbar, realistisk vei fra revidert idé til ferdig testet og dokumentert produkt for én person.

---

## Uke 35–36 (24.08 – 06.09): Verktøy og infrastruktur (Tools of the Trade)
* **Hva gjøres:** Grunnleggende oppsett av tradisjonelle utviklingsverktøy, pakkehåndtering, samt introduksjon til KI-utviklingsverktøy og Context Engineering.
* **Bruk i prosjektet:** Vi setter opp kodemiljøet, GitHub-repositoriet (`G56-guimaraes`) og forbereder bibliotekene (Python, Streamlit, Pandas, ReportLab). Fundamentet for KI-assistert utvikling legges.

## Uke 37 (07.09 – 13.09): BMAD-rammeverket (The BMAD Method)
* **Hva gjøres:** Innføring i BMAD med fokus på overgangen fra idé (The Planning Arc) til en byggeklar backlog (Implementeringssløyfen).
* **Bruk i prosjektet:** Vi tar i bruk BMAD-metodikken for å strukturere prosjektet. Idéen forankres i et Product Brief, og vi forbereder overgangen til PRD, arkitektur og konkrete "stories" for regnskapskontroll og KI-rapportering.

## Uke 38 (14.09 – 20.09): Agentic Programming
* **Hva gjøres:** Teoretisk og praktisk innføring i Agentic Programming – inkludert context engineering og CLI-baserte kodingsagenter.
* **Bruk i prosjektet:** Vi forbereder delegering av implementasjonsoppgaver til KI-agenter (Google Antigravity / Claude Code). Vi etablerer regler for at KI-en kun skal bygge kode etter spesifikasjonene i BMAD-artefaktene.

## Uke 39–40 (21.09 – 04.10): Context Engineering & LLM som resonneringsmotor
* **Hva gjøres:** Dypdykk i hvordan Large Language Models (LLMs) fungerer som resonneringsmotorer, prompt engineering, strukturerte utdata (JSON/Pydantic) og governance.
* **Bruk i prosjektet:** Vi etablerer kjerneprinsippet: **Koden regner, KI-en forklarer**. Vi designer prompts der LLM-en utelukkende mottar ferdig kontrollerte og aggregerte nøkkeltall, slik at risiko for tallhallusinasjoner elimineres.

## Uke 41 (05.10 – 11.10): Google Antigravity Fundamentals & Tilbakemelding
* **Hva gjøres:** Praktisk arbeid med Antigravity som utviklingsassistent. Mottak og analyse av tilbakemelding på opprinnelig Product Brief.
* **Bruk i prosjektet:** Vi evaluerer tilbakemeldingen fra faglærer. Omfanget spisses fra en urealistisk bred plattform til en skarp, faglig forankret kjerneflyt: **Saldobalanse (SB) og Hovedbok (HB)**.

## Uke 42 (12.10 – 18.10): Revidert Planlegging (Scope, PRD & Arkitektur)
* **Hva gjøres:** Revisjon av Product Brief, utarbeidelse av Product Requirements Document (PRD) og teknisk arkitektur i tråd med faglærers tilbakemelding.
* **Bruk i prosjektet:** 
  * *Product Brief:* Revideres med én kjerneflyt (SB + HB), testbare funksjonelle suksesskriterier, samt nye seksjoner for *The Solution* og *What Makes This Different*.
  * *PRD & Arkitektur:* Spesifiserer datamodellen for SB og HB, avstemmingsformelen ($IB + \sum \text{HB} = UB$), mapping til NS 4102, samt arkitektur for frakoblet testmodus (mock) for sensor.

## Uke 43 (19.10 – 25.10): Utviklingsiterasjon 1 – Datainntak og Regnskapskontroll
* **Hva gjøres:** Oppstart av implementeringssløyfen via BMAD-stories.
* **Bruk i prosjektet:**
  * Bygge Streamlit-brukergrensesnitt for opplasting av to filer (SB og HB i CSV/Excel).
  * Implementere deterministisk balansekontroll ($\sum \text{Debet} = \sum \text{Kredit}$) i Pandas.
  * Implementere kryssavstemming mellom hovedbok og saldobalanse ($IB + \sum \text{HB} = UB$) med flagging av differanser per konto.
  * Etablere syntetiske testdatasett i `data/sample/` (både balanserte filer og filer med konstruerte feil).

## Uke 44 (26.10 – 01.11): Utviklingsiterasjon 2 – Mapping, KI-sammendrag & PDF
* **Hva gjøres:** Videreutvikling av kjernefunksjonaliteten.
* **Bruk i prosjektet:**
  * Implementere automatisk mapping av kontonumre til Norsk Standard Kontoplan (NS 4102).
  * Beregning av sentrale nøkkeltall (driftsinntekter, driftskostnader, EBIT, margin).
  * Koble på LLM-integrasjonen (OpenAI API) med Pydantic Structured Outputs for norsk ledelseskommentar og tiltaksliste.
  * Bygge **lokal test-/mock-modus** i appen slik at sensor kan kjøre full analyse uten egen API-nøkkel.
  * Utvikle eksportfunksjon som genererer en ryddig PDF-rapport via ReportLab.

## Uke 45 (02.11 – 08.11): Utviklingsiterasjon 3 – Testing, QA og Robusthet
* **Hva gjøres:** Testing, feilretting og verifisering mot suksesskriteriene.
* **Bruk i prosjektet:**
  * Skrive automatiserte enhetstester med `pytest` for alle avstemmingsregler og mapping-funksjoner.
  * Kjøre tester mot uvanlige kantsituasjoner (tomme filer, feil skilletegn i CSV, store avvik, manglende kontonumre).
  * Sikre at applikasjonen kjører stabilt på under 5 sekunder lokalt.

## Uke 46 (09.11 – 15.11): Dokumentasjon, Sensorvennlighet og Ryddighet
* **Hva gjøres:** Forberedelse av mappen for ekstern evaluering og sensor.
* **Bruk i prosjektet:**
  * Skrive en krystallklar `README.md` med trinn-for-trinn-instruksjoner for hvordan sensor kloner repoet, installerer avhengigheter og kjører appen lokalt med testdata.
  * Etablere `.env.example` for miljøvariabler og verifisere at ingen hemmeligheter eller ekte regnskapsdata ligger i git-historikken.
  * Koble GitHub Issues / Labels mot de fullførte BMAD-storiene for å sikre full sporbarhet fra brief til kode.

## Uke 47 (16.11 – 22.11): Evalueringsrapport, Etikk og Endelig Levering
* **Hva gjøres:** Akademisk rapportskriving, etisk analyse og innlevering av mappen.
* **Bruk i prosjektet:**
  * Ferdigstille den helhetlige prosjektrapporten i tråd med kravene i IBE160.
  * Drøfte etiske problemstillinger: Ansvar for økonomiske beslutninger basert på KI-anbefalinger, feilkilder ved automatisk regnskapsanalyse og personvern.
  * Formulere erfaringer med BMAD-metoden og evaluere hvordan agentic programming påvirket prosjektets fremdrift og kodekvalitet.
