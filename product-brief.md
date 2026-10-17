# Product Brief: Ledelsesrapport og forenklet kontroll av regnskap med KI (Kjerneversjon: Saldobalanse & Hovedbok)

Ledelsesrapport og forenklet kontroll av regnskap med KI er en spisset webapplikasjon designet for å automatisere avstemming, avvikskontroll og ledelsesrapportering for små og mellomstore bedrifter (SMB). Applikasjonen tar imot bedriftens to mest sentrale regnskapsrapporter – **Saldobalanse (SB)** og **Hovedbok (HB)** – verifiserer at tallene henger logisk og matematisk sammen, mapper postene til Norsk Standard Kontoplan (NS 4102), og produserer et forklarende ledelsessammendrag og en presentasjonsklar PDF-rapport ved hjelp av en språkmodell (LLM).

Ved å fokusere v1 utelukkende på samspillet mellom saldobalanse og hovedbok, etableres en bunnsolid regnskapsfaglig kjerne: Dobbelt bokføringskontroll ($\sum \text{Debet} = \sum \text{Kredit}$) og kryssavstemming ($IB + \text{bevegelser i HB} = UB \text{ i SB}$). KI-en brukes målrettet der den skaper størst verdi: til å formulere et konsist, forretningsmessig narrativ på norsk basert på ferdig utregnede og kontrollerte tall, uten risiko for at modellen "regner selv" eller hallusinerer tallverdier.

---

## The Problem
Økonomisk rapportering og internkontroll i SMB-markedet er preget av siloer og manuelle prosesser. Standardrapporter fra regnskapssystemer som Fiken, Tripletex og Xero viser historiske tall hver for seg, men forklarer ikke *hvorfor* tallene svinger i forhold til den underliggende driften. 

Et typisk eksempel er en daglig leder som forbereder seg til et styremøte. Saldobalansen viser at driftskostnadene har økt med 25 % mot forrige periode, men for å finne årsaken må lederen manuelt bla gjennom hundrevis av poster i hovedboken, kryssjekke bilag i Excel og skrive en forklarende tekst for hånd. Samtidig oppdages feilkonteringer eller ubalanser ofte for sent fordi bedriften mangler en enkel, automatisert rutine for å kontrollere at alle transaksjoner i hovedboken faktisk summerer seg opp til endringen i saldobalansen. Dette skaper usikkerhet, stjeler verdifulle timer i månedsslutten og øker risikoen for at styret fatter beslutninger på mangelfullt grunnlag.

---

## Who This Serves
* **Primærbruker:** Daglig leder i en liten til mellomstor bedrift (SMB) uten egen økonomiavdeling eller interncontroller. Brukeren har behov for en rask, pålitelig kvalitetssikring av periodetallene og et velskrevet ledelsesnotat som kan legges frem for styret eller banken, uten å bruke timer på manuell avstemming i Excel.
* **Sekundærbruker:** Ekstern regnskapsfører eller økonomisk rådgiver som betjener flere SMB-klienter. Brukeren ønsker et effektivt verktøy for å automatisere den rutinemessige kontrollen mellom hovedbok og saldobalanse ved månedsavslutning, og raskt levere verdiøkende ledelseskommentarer til sine oppdragsgivere.

---

## The Solution
Applikasjonen leveres som et lokalt kjørbart Streamlit-dashboard i Python. Brukergrensesnittet er intuitivt og bygget rundt én lineær arbeidsflyt:

1. **Opplasting:** Brukeren laster opp to filer – Saldobalanse (SB) og Hovedbok (HB) – i CSV- eller Excel-format via et enkelt grensesnitt.
2. **Automatisk kontroll og kryssavstemming:** Systemet utfører en todelt deterministisk kontroll i koden:
   * **Balansekontroll:** Verifiserer at $\sum \text{Debet} = \sum \text{Kredit}$ i både saldobalanse og hovedbok.
   * **Kryssavstemming (HB mot SB):** Kontrollerer for hver enkelt konto at Inngående Balanse ($IB$) pluss summen av periodens transaksjoner i hovedboken tilsvarer Utgående Balanse ($UB$) i saldobalansen ($IB + \sum \text{HB} = UB$). Eventuelle avvik flagges med rød varsling, kontonummer og nøyaktig avviksbeløp.
3. **Strukturering og mapping (NS 4102):** Kontoene aggregeres automatisk til standardiserte kontoklasser i Norsk Standard Kontoplan (1xxx: Eiendeler, 2xxx: Egenkapital og gjeld, 3xxx: Salgsinntekter, 4xxx–7xxx: Driftskostnader, 8xxx: Finansposter).
4. **Beregning av nøkkeltall:** Systemet beregner driftsinntekter, driftskostnader, driftsresultat (EBIT), samt de 3–5 største kostnadsdriverne og avvikene mellom perioder.
5. **KI-forfattet ledelsessammendrag:** De ferdig beregnede nøkkeltallene og eventuelle uavstemte poster oversendes til en språkmodell (LLM via OpenAI API) med en streng system-prompt (CFO-tone). Modellen returnerer et strukturert sammendrag, forklaring av observerte trender og en prioritert tiltaksliste på norsk. Appen har også en integrert **testmodus (mock)**, slik at hele flyten kan demonstreres og kjøres lokalt uten API-nøkkel.
6. **Eksport:** Brukeren får forhåndsvisning av grafer, nøkkeltall og KI-kommentarer direkte i nettleseren, og kan med ett klikk laste ned en komplett, formatert PDF-styrepakke.

---

## What Makes This Different
Eksisterende regnskapsprogrammer (som Fiken og Tripletex) og regnskapsbyråenes standardportaler leverer statiske tabelloppstillinger. De krever at brukeren selv må kryssjekke hovedbok mot saldobalanse dersom tall ikke stemmer, og de tilbyr ingen automatisert forklaring av hva tallene faktisk betyr for driften. 

Denne løsningen skiller seg ut på to avgjørende punkter:
1. **Integrert konsistenskontroll mellom to kilder ($IB + HB = UB$):** I stedet for å stole blindt på én enkelt saldobalanse, sikrer krysstestingen mot transaksjonsloggen i hovedboken at datagrunnlaget er regnskapsteknisk konsistent før noen form for analyse igangsettes.
2. **Klar arbeidsdeling mellom kode og KI:** Beregninger, avstemminger og mapping utføres utelukkende deterministisk i Python/Pandas. KI-en benyttes utelukkende til det den er best til – å formulere et pedagogisk, profesjonelt ledelsesnarrativ basert på verifiserte tall – noe som eliminerer risikoen for tallhallusinasjoner.

---

## Success Criteria
Suksesskriteriene for v1 er utelukkende funksjonelle og direkte testbare i emnet:

1. **Balansekontroll:** En saldobalanse eller hovedbok der $\sum \text{Debet} \neq \sum \text{Kredit}$ blir umiddelbart flagget med synlig feilmelding og nøyaktig differanse, og videre rapportgenerering blokkeres.
2. **Avstemming av Hovedbok mot Saldobalanse:** For hver konto i kontoplanen sjekker systemet om $IB + \sum(\text{Transaksjoner i HB}) = UB$. Minst én test med et konstruert avvik beviser at systemet oppdager og navngir den spesifikke kontoen og feilbeløpet.
3. **Mapping til NS 4102:** Standard 4-sifrede norske kontonumre (f.eks. konto 3000 Salgsinntekter, konto 4000 Varekostnad, konto 6000 Avskrivninger) mappes korrekt til sine respektive kontogrupper etter NS 4102.
4. **Deterministiske nøkkeltall:** Systemet beregner driftsinntekter, driftskostnader, driftsresultat (EBIT) og driftsmargin korrekt basert på de mappede tallene, uten avrundingsfeil eller flyttallsproblemer.
5. **Strukturert KI-ledelseskommentar:** Språkmodellen mottar kun aggregerte nøkkeltall og avvik, og produserer et strukturert ledelsessammendrag med tiltak på formelt norsk, formatert etter et fastsatt skjema (JSON/Pydantic).
6. **Kjørbarhet for sensor (Frakoblet testmodus):** Sensor kan klone repositoriet og kjøre applikasjonen lokalt etter instruksjonene i README ved hjelp av medfølgende eksempeldata i `data/sample/`, uten å oppgi egen API-nøkkel eller ha betalte kontoer (via en egen test/mock-bryter i brukergrensesnittet).
7. **Feilfri PDF-generering:** Systemet genererer en ryddig, formatert PDF-rapport med tittel, nøkkeltallstabell, avstemmingsstatus og ledelseskommentarer, som kan lastes ned direkte fra appen uten feilmeldinger.
8. **Responstid:** Hele løpet fra filopplasting til ferdig skjermrapport og PDF utføres på under 5 sekunder ved lokal kjøring.

---

## Scope

### In for v1 (Kjerneflyt):
* **Filinntak:** Opplasting av Saldobalanse (SB) og Hovedbok (HB) i CSV- og Excel-format (.xlsx).
* **Internkontroll:**
  * Kontroll av debet = kredit i både SB og HB.
  * Kryssavstemming av bevegelse: $IB + \text{sum føringer i HB} = UB \text{ i SB}$ per konto og totalt.
* **Datatransformasjon:** Automatisk mapping av 4-sifrede norske kontoer mot Norsk Standard Kontoplan (NS 4102).
* **Nøkkeltall:** Beregning av driftsinntekter, driftskostnader, driftsresultat (EBIT), samt topp 3 kostnadsposter.
* **KI-integrasjon:** Strukturert ledelsessammendrag og tiltaksliste generert via OpenAI API, samt en fullverdig lokal test-/mock-modus for sensor.
* **Brukergrensesnitt:** Streamlit-dashboard for opplasting, visning av avstemmingsstatus, nøkkeltallstabeller og KI-kommentar.
* **Eksport:** Generering og nedlasting av ferdig formatert PDF-rapport via ReportLab.
* **Testdata:** Oppdiktede eksempeldatasett (både et balansert regnskapssett og et sett med bevisst ubalanse/avvik) plassert i `data/sample/`.

### Explicitly out of v1:
* Ytterligere filkilder og moduler (reskontro, CRM-data, timelister, ESG-forbruk).
* SAF-T (XML) format og komplekse XML-parsere (flyttet til fremtidige iterasjoner).
* Flervalutasammenstilling (v1 støtter utelukkende én valuta: NOK).
* Direkte live API-koblinger mot ERP-systemer (kun filopplasting i v1).
* Automatisk skatte- eller årsregnskapsinnsending til Altinn.
* Brukerautentisering, innlogging, flerbrukertilgang og abonnementsbetaling (Stripe).
* Chatbot-funksjonalitet for å "snakke" med regnskapet.
* Docker- og skyløsning for produksjonsdrift (fokus i v1 er en robust, lokalt kjørbar applikasjon).

---

## Vision
På kort sikt er målet å etablere den mest pålitelige og pedagogiske "månedsavslutnings-assistenten" for SMB-ledere og regnskapsførere – en lettvektsløsning som på under fem sekunder avstemmer tallene, avslører feilføringer og formulerer en ferdig styrepakke.

På lengre sikt danner denne kjerneflyten grunnmuren for en **"Continuous AI CFO"**:
1. **Fase 2:** Utvidelse til operasjonelle datakilder (kobling av timelister mot lønnskostnader, CRM mot salgsinntekter) for å forklare operative årsakssammenhenger.
2. **Fase 3:** Støtte for SAF-T Financial (XML) for sømløs kompatibilitet med alle norske regnskapssystemer, samt flervaluta for selskaper med internasjonal handel.
3. **Fase 4:** Direkte toveis API-integrasjoner mot skytjenester (Fiken, Tripletex, PowerOffice Go) som overvåker bokføringen fortløpende og varsler ledelsen proaktivt før avvikene eskalerer.
