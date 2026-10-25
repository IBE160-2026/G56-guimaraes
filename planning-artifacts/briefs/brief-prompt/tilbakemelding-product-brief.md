# Tilbakemelding på product brief

| | |
|---|---|
| **Gruppe** | G56 – G56-guimaraes |
| **Product brief** | `product-brief.md` (commit `10ff5c7`). `prosjektplan.md` er lest som kontekst. |
| **Tilbakemelding fra** | Faglærer i IBE160 (utarbeidet med KI-støtte) |
| **Dato** | 2026-10-06 |

## Samlet vurdering

- **Bør revideres før dere går videre.** Rett punktene markert «Endre» før dere lager PRD og arkitektur.

**Det som er bra:**

1. Problemet er reelt og godt forklart: standardrapporter fra Fiken, Tripletex og Xero viser tallene, men ikke *hvorfor* de svinger i forhold til driften (for eksempel vrakprosent eller tapte anbud). Kombinasjonen av balansekontroll (debet = kredit), mapping til NS 4102 og et KI-skrevet ledelsessammendrag er en spennende idé.
2. Dere har et godt prinsipp i prosjektplanen: KI-en skal analysere «ferdig utregnede tall» og ikke regne selv, slik at den ikke «hallusinerer tall». Det er akkurat riktig arbeidsdeling mellom vanlig kode og språkmodell. At direkte ERP-koblinger og Altinn-innsending er holdt utenfor v1, er også klokt.

**De viktigste endringene:**

1. Omfanget i v1 er altfor stort for en gruppe på én person. V1 inneholder i dag fem filtyper (saldobalanse, reskontro, CRM, timelister, ESG), tre formater inkludert SAF-T, automatisk kontoplanmapping, avviksdeteksjon, flervalutasammenstilling, KI-kommentar og PDF-rapport. Velg én kjerneflyt: last opp én saldobalanse i CSV → kontroller balansen og map til NS 4102 → få nøkkeltall og et KI-skrevet sammendrag. Alt annet bør ut av v1.
2. Skriv om suksesskriteriene. «99 % oppetid», «80 % av brukerne rapporterer …», «10+ betalende regnskapsbyråer» og «70 % konvertering til betalt abonnement» kan ikke måles i emnet. Erstatt dem med funksjonelle kriterier, for eksempel «en saldobalanse der debet ≠ kredit blir flagget med differansen» og «konto 3000 blir mappet til gruppen Salgsinntekt».
3. Fyll inn delene som mangler eller er slått sammen: The Solution (hva brukeren ser og gjør), What Makes This Different og en egen Who This Serves. Velg én primærbruker – i dag nevnes daglige ledere, gründere, styremedlemmer, økonomiansvarlige, regnskapsførere og rådgivere.

## Vanskelighetsgrad og gjennomførbarhet

### Vurdert vanskelighetsgrad

- **Vanskelig**

**Sammenlignbart med:** 4) KI-støttet MRP II (vanskelig). Som MRP II har briefen mange moduler som henger sammen, forretningskritiske data og fagregler som må stemme (regnskap, kontoplan, SAF-T, valuta). Avgrenset til én saldobalanse med kontroll, mapping og KI-sammendrag vil prosjektet ligge på middels, nær 2) AI CV- og søknadsassistent.

**Begrunnelse:**

| Faktor | Nivå (lav / middels / høy) | Kommentar |
|---|---|---|
| Domenelogikk – hvor mange og hvor kompliserte regler og beregninger må stemme? | Høy | Balanseavstemming, mapping til NS 4102, flagging av uvanlige transaksjoner, flervaluta og kobling mot operasjonelle KPI-er. Alt må være regnskapsfaglig riktig. |
| Datamodell – antall entiteter og relasjoner mellom dem | Høy | Konto, kontogruppe, transaksjon, reskontro, kunde/CRM, timer, ESG-forbruk, valuta, KPI og rapport. |
| Brukere, roller og innlogging | Middels | Ikke beskrevet i briefen, men «sikker opplasting» og regnskapsførere med «førti klienter» forutsetter innlogging og tilgangsstyring. |
| KI-funksjonalitet i appen, f.eks. kall til språkmodell, prompts i koden og håndtering av usikre svar | Middels | Ledelseskommentar og tiltaksliste på norsk, og «Revisor KI-sjekk». Avgrenset hvis KI bare skriver tekst ut fra ferdige tall. |
| Integrasjoner og eksterne tjenester, f.eks. API-er, betaling og e-post | Middels | LLM-API. ERP-API er riktignok holdt utenfor. Betaling og abonnement nevnes i suksesskriteriene, men ikke i Scope. |
| Sanntid, samtidighet eller flere brukere som påvirker hverandre | Lav | Ingen sanntid beskrevet. |
| Filhåndtering, f.eks. opplasting, PDF-lesing og eksport | Høy | CSV, Excel og SAF-T (XML) fra flere kilder, pluss generering av PDF-rapport med grafer. SAF-T alene er et omfattende format. |
| Sikkerhet og personvern | Høy | Regnskapsdata er forretningskritiske, reskontro og CRM kan inneholde personopplysninger, og data sendes til en ekstern språkmodell. |

**Hva vanskelighetsgraden betyr for dere:**

- _Vanskelig:_ Et vanskelig prosjekt gir større mulighet for toppkarakter, men også større risiko. Definer en minimal versjon som sikkert kan bli ferdig – én saldobalanse, balansekontroll, mapping og KI-sammendrag – og legg resten (reskontro, CRM, timer, ESG, SAF-T, flervaluta) i tydelige trinn etterpå.

### Gjennomførbarhet med BMAD og Claude Code

Dere skal planlegge med BMAD (product brief → PRD → arkitektur → epics og stories) og implementere med Claude Code. Vurderingen under tar hensyn til at det må være tid til hele denne flyten, og til testing, retting og README til slutt.

| Spørsmål | Vurdering (OK / risiko / stor risiko) | Kommentar |
|---|---|---|
| **Tid og omfang** – kan v1 realistisk bli ferdig og stabil i løpet av semesteret, med tid til flere iterasjoner? | Stor risiko | Briefen nevner «en 5-ukers prosjektperiode», og prosjektplanen legger koding til uke 44 og ferdigstilling til uke 45. Med dagens v1 og én person er det ikke realistisk. Kontroller også planen mot emnets faktiske innleveringsfrist. |
| **BMAD-flyten** – er briefen konkret nok til at PRD, arkitektur og stories kan lages uten store hull, og blir det overkommelig mange stories? | Risiko | Scope er en lang liste uten prioritering, og løsning og brukeropplevelse er ikke beskrevet. Det gir svært mange stories og hull KI-en vil fylle selv. |
| **Egnet for Claude Code** – bruker løsningen en vanlig, godt dokumentert teknologistakk som Claude Code håndterer godt, eller krever den nisjeteknologi, spesialmaskinvare eller mye manuell konfigurasjon? | OK | Python, Pandas og Streamlit (fra prosjektplanen) er godt dokumentert og passer godt for en dataapp som kjøres lokalt. |
| **Kontroll på KI-ens arbeid** – kan gruppen selv avgjøre om koden gjør det riktige? Krever domenet kunnskap gruppen ikke har, f.eks. avanserte beregninger eller fagregler, så er det vanskelig å kvalitetssikre. | Risiko | Krever regnskapskunnskap (NS 4102, SAF-T, avstemming). Hvis dere har denne kunnskapen, er det en styrke. Hvis ikke, blir det vanskelig å vite om mappingen og flaggingen er riktig. |
| **Testbarhet** – finnes det tydelige regler og forventede resultater som tester kan skrives mot? | OK | Balansekontroll og kontoplanmapping har tydelige regler og er svært godt egnet for automatiske tester – når kriteriene er skrevet om. |
| **Kjørbar for sensor** – kan appen kjøres lokalt etter README, uten gruppens nøkler, betalte kontoer eller egen infrastruktur? | Risiko | Streamlit lokalt er enkelt, men KI-sammendraget krever en API-nøkkel. Lag en testmodus med lagret svar og en oppdiktet saldobalanse. Docker og skydrift (uke 46) er ikke nødvendig for å kjøre appen lokalt. |
| **Avhengigheter og kostnader** – krever løsningen betalte API-er, f.eks. språkmodeller, og finnes det en plan for kostnad, testmodus eller mock-data? | Risiko | LLM-API er forutsatt, men leverandør, kostnad og testmodus er ikke beskrevet. |

**Konklusjon om gjennomførbarhet:**

- **Lite realistisk uten vesentlige endringer.** Se forslagene under.

**Forslag til justering av omfang eller vanskelighetsgrad:**

1. Definer v1 som: opplasting av én saldobalanse i CSV/Excel → kontroll av debet = kredit → mapping til NS 4102-grupper → enkle nøkkeltall og grafer → KI-skrevet ledelsessammendrag på norsk → nedlasting som PDF. Flytt reskontro, CRM, timelister, ESG, SAF-T og flervaluta til senere trinn eller Vision.
2. Når kjerneflyten er stabil og testet, kan dere legge til én operasjonell fil (for eksempel timelister) for å vise «samstilling av drift og økonomi». Det er det som skiller idéen fra et standard ERP, og det er bedre å vise det godt for én kilde enn halvveis for fem.

## Hvorfor product brief er viktig for mappen

Product brief er utgangspunktet for PRD, arkitektur, stories og til slutt koden. Del 1 av mappen vurderes blant annet på om sensor kan følge en sporbar vei fra plan til ferdig app. Den vurderes også på om appen gjør det dere har beskrevet, om den er testet, om den er godt designet, og om den kan kjøres etter README. Et uklart, for stort eller for lite brief gjør alt dette vanskeligere senere. Det er mye enklere å rette nå enn sent i semesteret.

## 1. Gjennomgang av briefens deler

| Del av brief | Status | Kommentar |
|---|---|---|
| Executive Summary – er det klart hva appen er, og hvilket problem den løser? | Juster | Innledningen forklarer idéen, men beskriver en «helhetlig plattform» for mange brukergrupper. Gjør den kortere og tilpass den til v1. |
| The Problem – er problemet konkret, med reelle situasjoner og brukere? | OK | Konkret om silo-rapporter og «Excel-propp». Gi gjerne ett konkret eksempel på en situasjon der en daglig leder må forklare et avvik for styret. |
| The Solution – beskriver løsningen brukeropplevelsen, ikke bare teknologi? | Endre | Mangler som egen del. Beskriv hva brukeren gjør steg for steg og hva de får se, i stedet for systemfunksjoner. |
| What Makes This Different – er vurderingen ærlig og realistisk? | Endre | Mangler. Skriv ærlig hvordan dette skiller seg fra rapportmoduler i eksisterende ERP-systemer og regnskapsbyråenes egne verktøy. |
| Who This Serves – er primærbrukerne tydelige, og vet vi hva de trenger? | Juster | Primær- og sekundærbrukere står under The Problem. Velg én primærbruker (for eksempel daglig leder i en liten bedrift uten økonomiavdeling) og beskriv situasjonen konkret. |
| Success Criteria – kan kriteriene faktisk sjekkes eller testes? | Endre | Tekniske, læringsmessige og forretningsmessige mål kan ikke måles i emnet. Behold de funksjonelle og gjør dem konkrete. |
| Scope – er det klart hva som er med i første versjon, og hva som ikke er det? | Endre | «Explicitly out» er bra, men «In for v1» er for stort. Begrens til én kjerneflyt. |
| Vision – henger visjonen sammen med resten uten å blåse opp omfanget? | OK | «Continuous AI CFO» er tydelig plassert på lang sikt. |

## 2. Utgangspunkt for del 1 av mappen

Punktene følger kriteriene i sensorveiledningen for del 1. Vektene i parentes viser hvor mye hvert kriterium teller i del 1.

| Kriterium i del 1 | Hva briefen bør legge til rette for | Status | Kommentar |
|---|---|---|---|
| **1. Prosess og KI-styring** (30 %) | Brief som er presis nok til at PRD og stories kan bygges direkte på den, slik at krav kan spores fra brief til kode. | Endre | Briefen mangler løsning og prioritering, og prosjektplanen beskriver delvis andre verktøy og frister enn emnet. Revider briefen først, så PRD og stories får et klart grunnlag. |
| **2. Funksjonalitet og omfang** (20 %) | Realistisk omfang for gruppen og semesteret: en tydelig kjerneflyt som kan bli ferdig og stabil, og nok innhold til å vise reell funksjonalitet. | Endre | Omfanget er for stort. Én stabil kjerneflyt gir bedre grunnlag enn mange halvferdige moduler. |
| **3. Kvalitetssikring og testing** (15 %) | Suksesskriterier og funksjoner som er konkrete nok til å bli testtilfeller. | Endre | Balansekontroll og mapping er svært testbare, men kriteriene må skrives om fra forretningsmål til funksjonelle testtilfeller. |
| **4. Design og brukeropplevelse** (10 %) | Tydelige brukere og brukssituasjoner som designet kan bygges rundt, gjerne med de viktigste skjermbildene eller flytene skissert. | Juster | Prosjektplanen beskriver et Streamlit-dashboard der brukeren «laster opp to filer og trykker ‘Generer rapport’». Ta denne flyten inn i briefen og skissér rapportsiden. |
| **5. Kodekvalitet og arkitektur** (10 %) | Teknologivalg som er begrunnet og ikke mer komplekse enn appen trenger. | Juster | Streamlit og Pandas er et fornuftig valg. CI/CD, Docker og skydrift med overvåking er ikke nødvendig for v1 og bør vente. |
| **6. README og kjørbarhet** (10 %) | Løsning som andre kan kjøre lokalt uten betalte kontoer, og uten tilgang til gruppens egne tjenester og nøkler. | Juster | Lokal Streamlit-app er lett å kjøre. Planlegg testmodus for KI-delen og en oppdiktet saldobalanse som eksempeldata. |
| **7. Ryddighet i repoet** (5 %) | En plan for hvor hemmeligheter, testdata og dokumentasjon skal ligge. | Juster | Ikke beskrevet. Bruk `.env.example` for API-nøkkel, legg oppdiktede testfiler i en egen mappe, og bruk aldri ekte regnskapsdata i det offentlige repoet. |

## 3. Neste steg for gruppen

1. Skriv om Scope til én kjerneflyt (én saldobalanse → kontroll → mapping → nøkkeltall → KI-sammendrag → PDF), og flytt resten til senere trinn.
2. Erstatt suksesskriteriene med 5–8 funksjonelle kriterier som kan testes, og lag en oppdiktet saldobalanse med kjent fasit (inkludert én med ubalanse).
3. Legg til The Solution, What Makes This Different og én tydelig primærbruker. Oppdater deretter prosjektplanen slik at den følger emnets innleveringsfrist og har tid til flere utviklingsrunder med testing.

Oppdater product brief i repoet når dere har gjort endringene, slik at historikken viser hvordan planen utviklet seg. Det er en del av prosessen sensor ser etter.
