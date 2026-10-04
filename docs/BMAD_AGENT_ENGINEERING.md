# BMAD Agent Engineering for Ledelsesrapport KI

Dette dokumentet definerer hvordan vi tilpasser den offisielle [BMAD-metoden (Agile AiDD)](https://github.com/bmad-code-org/BMAD-METHOD) for å bygge plattformen beskrevet i `product-brief.md`.

## 1. Fra Menneskelige Roller til Agent-Skills (AiDD)
Den offisielle BMAD-metoden erstatter tradisjonelle "menneskelige roller" med prosessdrevne **Skills** for KI-agenter. Prosessen er delt i "Thinking Skills" og "Building Skills" som går i en kontinuerlig sløyfe: *Clarify ➔ Plan ➔ Build & Verify ➔ Learn & Adjust*.

I vårt prosjekt oversetter vi dette slik:
* **Thinking Skills (`bmad-recon` og `bmad-plan`):** Agentens evne til å analysere `product-brief.md`, forstå regnskapskonteksten og designe dataflyten (CSV/SAF-T -> Pandas -> Norsk Standard Kontoplan NS 4102 -> PDF, med støtte for valutaomregning).
* **Building Skills (`bmad-build`):** Agentens utførende gren, som skriver koden, kjører Streamlit-appen og bygger enheten for balansekontroll (Debet = Kredit).

## 2. Implementering av BMAD-sløyfen
Når vi skal utvikle en ny funksjon (f.eks. modulær opplasting av CSV og SAF-T), følger vi denne agent-arbeidsflyten:

1. **Clarify (Deep Recon):** Utvikleren instruerer agenten om å lese `product-brief.md` og eventuelle rådata (test-filer). Agenten oppsummerer avgrensningene for den spesifikke oppgaven.
2. **Plan:** Agenten formulerer en presis teknisk plan, inkludert nødvendige Pandas-transformasjoner for å knytte dataene til NS 4102.
3. **Build & Verify:** Agenten aktiverer `bmad-build`. Koden skrives, en lokalt test kjøres for å sikre at logikken er "bug-free", og resultatene valideres mot planen.
4. **Learn & Adjust:** Hvis en "Debet=Kredit"-sjekk feiler i test, går agenten automatisk tilbake til Plan/Build-steget for å rette feilen før koden merkes som ferdig.

## 3. Governance: Sikring av Fagets Avgrensninger
Det viktigste ved BMAD-metodologien er **styring og avgrensning**. For å unngå at agenten bygger funksjoner utenfor MVP-ens scope, eller feiltolker norsk regnskapsskikk, legger vi inn følgende "System Rules" for alle agenter som berører koden:

### Absolute Constraints (BOND)
* **Scope Lock:** Agenten har *forbud* mot å skrive kode for direkte API-integrasjoner mot ERP (Tripletex/Fiken) eller Altinn. All inndata skal hardkodes til å akseptere filopplasting (CSV/Excel/SAF-T) inntil versjon 2.0.
* **Valuta:** Agenten skal bygge støtte for flervaluta, slik at brukere kan samstille og rapportere på operasjonelle og finansielle nøkkeltall på tvers av ulike valutaer i samme rapport.
* **SAF-T (Standard Audit File-Tax):** Agenten må bygge inn og benytte spesifikke parsere for SAF-T formatet (XML), slik at nasjonale standardfiler for regnskap kan leses og analyseres direkte.
* **Compliance-Kontrollør (Innebygd sjekk):** Agentens `bmad-build`-skill er pålagt å skrive unit-tester for *hver* eneste regnskapsberegning. Koden for avviksdeteksjon *må* inneholde en assert som sjekker `sum(Debet) == sum(Kredit)` før en fil kan behandles videre.
* **Tone-of-Voice:** Ved generering av ledelseskommentarer skal agentens integrerte LLM-prompts settes opp til å være formelle, konsise og faktabaserte (forankret i bedriftens tall), uten unødvendig fyllord.

Gjennom dette oppsettet fungerer BMAD-metoden som rekkverk: Den gir agenten frihet til å kode raskt og effektivt, samtidig som den holdes strengt innenfor de forretningsmessige og fagspesifikke grensene satt for MVP-en.
