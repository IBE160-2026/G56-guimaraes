# KI-Logg: Utvikling og raffinering av Product Brief

**Prosjekt:** G56 — Ledelsesrapport og regnskapskontroll med KI  
**Emne:** IBE160 Programmering med KI  
**Student:** Victor Guimaraes  
**Formål:** Dokumentere systematisk styring, prompting og kritisk korrigering av KI under utarbeidelsen av prosjektets Product Brief og omfangsavgrensning (Sensorveiledning Kriterium 1).

---

## Iterasjon 1: Innledende idémyldring og forslag (Proposal)
* **Brukerprompt:**  
  > *"Jeg vil bygge en AI-løsning for regnskap i SMB-markedet. Den skal analysere regnskapsdata, ta imot PDF-kvitteringer med OCR, hente banktransaksjoner, sjekke mot skatteregler og skrive ledelsesrapporter. Lag et forslag til prosjektplan og brief."*
* **KI-respons:**  
  Genererte et svært ambisiøst forslag med 6 moduler (OCR-fakturatolkning, bank-scraping, momskontroll, Altinn-innsending, SAF-T parser, og LLM-chat).
* **Menneskelig vurdering og korreksjon:**  
  Dette var et klassisk tilfelle av overoptimistisk KI-scoping. Ingen enkeltstudent kan bygge OCR, bank-API og Altinn-integrasjon på ett semester. Vi forkastet OCR og bank-integrasjon for å unngå implementasjonskollaps.

---

## Iterasjon 2: Første utkast til Product Brief
* **Brukerprompt:**  
  > *"Kutt ut OCR og Altinn. Vi fokuserer på filopplasting av regnskapstall. Strukturer briefen etter BMAD-malen: The Problem, Who This Serves, The Solution, What Makes This Different, Success Criteria, Scope (In/Out) og Vision."*
* **KI-respons:**  
  Strukturen var god, men KI-en foreslo fremdeles å sende hele CSV-filen direkte til en LLM for at den skulle 'finne avvik og regne ut nøkkeltall'.
* **Menneskelig vurdering og korreksjon:**  
  Kritisk regnskapsfaglig svakhet: LLM-er kan ikke addere store tallrekker pålitelig (hallusinasjoner). Vi innførte prinsippet **"The AI Firewall"**: Python og Pandas må gjøre alle beregninger deterministisk. KI skal kun motta ferdig beregnede aggregater.

---

## Iterasjon 3: Justering etter faglærers tilbakemelding
* **Brukerprompt:**  
  > *"Her er tilbakemeldingen fra faglærer: 'Prosjektet er for bredt. Spiss inn mot kjerneflyten Saldobalanse + Hovedbok. Dobbelt bokføringskontroll og kryssavstemming (IB + HB = UB) er gullstandarden.' Omskriv briefen slik at v1 utelukkende handler om SB + HB, med deterministisk sjekk og Pydantic-strukturert CFO-rapport."*
* **KI-respons:**  
  Produserte det spissede utkastet som nå utgjør `brief.md`.
* **Menneskelig vurdering og kvalitetssikring:**  
  Briefen er nå skarp, realistisk og har 100 % faglig forankring i pensum for IBE160.

---

## Nøkkelinnsikt fra KI-samarbeidet
1. **KI tenderer mot funksjonskryp (feature creep):** Uten streng styring foreslår modellen for mange tredjepartsbiblioteker og funksjoner.
2. **Kritisk sans er avgjørende:** Ved å tvinge modellen inn i en deterministisk arkitektur ("The AI Firewall") unngås regnefeil i regnskapsrapporteringen.
