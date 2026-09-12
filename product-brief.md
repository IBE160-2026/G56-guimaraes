# Product Brief: Ledelsesrapport og forenklet kontroll av regnskap med KI (Multi-Source Edition)

Ledelsesrapport og forenklet kontroll av regnskap med KI er en helhetlig plattform for automatisert finans- og operasjonsrapportering, avvikskontroll og kvalitetssikring. Plattformen er designet for daglige ledere, styremedlemmer, økonomiansvarlige og regnskapsførere i små og mellomstore bedrifter (SMB).

Fysiske rapporteringer og manuelle analyser tar timer hver måned og produserer data som må sammenstilles for hånd. Eksisterende ERP-systemer (som Fiken, Tripletex, Xero) leverer tørre, silo-baserte standardrapporter uten kobling mot bedriftens reelle operasjonelle hverdag. Denne plattformen lukker dette gapet: modulær opplasting av rådata, automatisk balanseavstemming, tverrfaglig samstilling av finanstall mot operasjonelle KPI-er, og KI-genererte ledelsessammendrag som forklarer den faktiske driften.

Tidspunktet er avgjørende. LLM API-er gjør nå to tidligere upraktiske ting til rutine: troverdig automatisert deteksjon av logiske avvik i regnskap, og personlig, velskrevet narrativ ledelsesrapportering på sekunder. Kombinert med en moderne, administrert backend og KI-assistert utvikling, er det mulig å bygge en MVP for dette i løpet av en 5-ukers prosjektperiode, noe som tidligere ville krevd mange måneders utvikling.

## The Problem
Økonomisk rapportering og internkontroll i SMB-markedet er lite intuitivt og preget av siloer. Standardrapporter viser kun historiske finanstall og forklarer ikke hvorfor tallene svinger i forhold til den faktiske driften (f.eks. vrakprosent i produksjon eller tapte anbud). Systemet løser dette ved å ta imot standardiserte fil-eksporter og umiddelbart gi brukerne en fullverdig analyse. Mange timer med manuell "Excel-propp" elimineres. Plattformen visualiserer dataene gjennom interaktive grafer og eksporterer til presentasjonsklare PDF-dokumenter, samtidig som skjulte feil og ubalanser i bokføringen oppdages lenge før årsoppgjøret.

Primærbrukere er daglige ledere og gründere i SMB-er som må forklare sammenhengen mellom drift, salg og regnskap for styret, men som trenger en lavterskel inngang uten tunge integrasjoner. 

Sekundærbrukere er regnskapsførere, rådgivere og styremedlemmer som ønsker strukturerte, operasjonelt forankrede beslutningsdata fra repeterbare prosesser.

## Success Criteria
Funksjonelt: En bruker kan laste opp saldobalanse og valgfrie operasjonelle filer og fullføre løpet fra a til å. Systemet gjennomfører automatisk mapping til Norsk Standard Kontoplan (NS 4102). KI-genererte avviksforklaringer og tiltakslister er presise og bygger direkte på bedriftens faktiske data. Sluttrapporten genereres uten feil.

Teknisk: 99 % oppetid. Prosessering og samstilling av flere datakilder, samt generering av ferdig PDF-rapport, tar under 30 sekunder. Databasespørringer og filhåndtering er optimalisert for rask lasting og høy datasikkerhet.

Innsikts- og læringsverdi (Educational): Minst 80 % av brukerne (ledelse/styre) rapporterer at de har fått en vesentlig bedre forståelse av sammenhengen mellom operasjonell drift og finansiell konsekvens. Regnskapsførere rapporterer at de sparer 2-5 timer per klient per måned.

Forretningsmessig: 10+ betalende regnskapsbyråer eller SMB-kunder innen tre måneder etter lansering. Et gjennomsnitt på over 2 genererte rapporter per aktive bruker per måned. Høy konvertering (70 %+) fra gratis prøveperiode til betalt abonnement.

## Scope
In for v1.
Brukerside: Modulær opplasting av saldobalanse, reskontro, CRM-data, timelister og ESG-forbruk i CSV/Excel-format.
Systemside: Automatisk mapping til kontoplan; Revisor KI-sjekk for balansekontroll (Debet = Kredit) og flagging av uvanlige transaksjoner; samstilling av operasjonelle og finansielle nøkkeltall; KI-generert ledelseskommentar og tiltaksliste på norsk; generering og nedlasting av komplett PDF-rapport; enkelt brukergrensesnitt for sikker opplasting.

Explicitly out of v1.
Direkte live API-koblinger mot ERP-systemer (kun filopplasting i V1). Automatisk skatte- eller årsregnskapsinnsending til Altinn. Flervalutasammenstilling i samme rapport (støtter kun én valuta per kjøring). Chatbot-funksjonalitet for å "snakke" med regnskapet (dette blir en naturlig utvidelse etter lansering).

## Vision
På kort sikt er målet enkelt: Bli standardverktøyet for hvordan SMB-er og regnskapsførere utarbeider styrepakker, fordi det er en løsning som er gratis å teste, fungerer like godt for én som for førti klienter, og leverer en ferdig, visuell PDF på sekunder.

På lang sikt er applikasjonen første steg mot en "Continuous AI CFO". Ved å etter hvert tilby direkte API-koblinger mot ERP og CRM, vil plattformen kontinuerlig overvåke hele verdikjeden i bakgrunnen og gi proaktive, menneskelignende strategiske råd til ledelsen.
