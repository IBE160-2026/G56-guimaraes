# Tilbakemelding på PRD

| | |
|---|---|
| **Gruppe** | G56 – G56-guimaraes |
| **PRD vurdert** | `docs/02_product/PRD.md` (status i dokumentkontrollen: «Godkjent», v2.0, ingen frontmatter; sist endret 2026-11-07, commit 3cc7b6f) |
| **Dato** | 2026-11-12 |
| **Type** | Formativ tilbakemelding, ikke karakter |

## 1. Samlet inntrykk

PRD-en har en tydelig tese («Koden regner, KI-en forklarer»), akseptkriterier med konkrete fasitverdier og en ærlig liste over det som er utenfor scope. Risikoen er at dokumentet har blitt en beskrivelse av ferdig kode (alt står som «Implementert», med funksjons- og testnavn i hvert krav) mer enn et krav- og beslutningsgrunnlag, og at omfanget har vokst til åtte epics, stikk i strid med rådet om én kjerneflyt fra briefen.

## 2. Dette fungerer godt

- **Testbare fasitverdier.** Story 2.1 og 2.2 sier hva som skal skje med kjente data: «`discrepancy_count == 2`, og konto `1500` og `1920` flagges med `abs(Avvik) == 30000.0`» og «`ebit == 110000.0` … `driftsmargin == 55.0`». Slike kriterier kan brukes direkte som testtilfeller.
- **KI-grensen er et reelt designvalg.** § 1 og NFR-1.1 skiller klart mellom beregning (Python/Pandas) og forklaring (språkmodell), og FR-3.3/NFR-1.2 gir en frakoblet testmodus. Dette svarer på det som ble etterlyst i briefen om testmodus.
- **Ærlig avgrensning.** § 3.2 lister utelatelser med begrunnelse («Ingen SAF-T», «Ingen reskontro …», «Ingen chatbot»). Dere holder dessuten sensors kjørbarhet (NFR-1.2) adskilt fra funksjonene.

## 3. Oversikt per dimensjon

| Dimensjon | Vurdering | Kort begrunnelse |
|---|---|---|
| Beslutningsklarhet | god | Viktige valg er stilt som beslutninger (firewall, Streamlit beholdes), men det er ingen åpne spørsmål, antakelser eller avveininger. |
| Substans | god | Fag- og produktinnhold er ekte og spesifikt. Persona-delen er tynn, og «Evaluator» (sensor) er ikke en bruker av produktet. |
| Strategisk sammenheng | god | Tesen er sterk, men § 2.1 lover å forklare *hvorfor* tallene svinger, mens funksjonene i hovedsak kontrollerer og regner nøkkeltall. |
| Testbarhet | god | Epic 1–5 er sterke. Epic 6–8, NFR-ene og flere KPI-er mangler målbare kriterier. |
| Scope og avgrensning | svak | Åtte epics og 25 FR for ett semester. Motstrid mellom «kun i minnet» og SQLite. Ingen åpne punkter. |
| Brukbarhet for neste fase | god | Sporbarhetsmatrisen er grundig, men det mangler glossar, og versjonsmerking og mål er delvis utdatert. |
| Formtilpasning | god | Capability-spec med stories passer et enkeltbrukerverktøy, men samme informasjon gjentas tre steder (stories, FR-tabell, matrise). |

## 4. Viktigste forbedringer

### 4.1 PRD-en beskriver kode, ikke krav, og omfanget har vokst
- **Alvorlighet:** høy
- **Hvor:** § 1 «Denne PRD-en er den overordnede kontrakten …», alle statusfelt «Implementert», § 3.1b (SQLite, drilldown, flersides UI)
- **Problem og hvorfor det betyr noe:** Når modul-, funksjons- og testnavn (`reconcile_hb_with_sb`, `st.navigation`, `PRAGMA foreign_keys`) står i selve kravene, kan ikke arkitektur og stories velge noe selv, og PRD-en kan ikke lenger styre koden. Kontraktsformuleringen er heller ikke reell når alt allerede er bygget. V2 er dessuten mye større enn kjerneflyten briefen anbefalte.
- **Forslag:** Merk Epic 1–4 som «MVP-kjerne» og Epic 5–8 som «utvidelser, kuttes først». Skriv kravene som oppførsel («Systemet flagger konto med kontonummer, navn og beløp når IB + netto HB ≠ UB») og flytt funksjons- og testnavn til sporbarhetsmatrisen eller arkitekturdokumentet.

### 4.2 Motstrid om lagring og uklar personvernregel
- **Alvorlighet:** høy
- **Hvor:** NFR-3.1 «behandles utelukkende i minnet» og Story 1.1 «uten diskskriving», mot § 3.1b «lagret i … `data/g56_accounting.db`»
- **Problem og hvorfor det betyr noe:** Regnskapsdata lagres nå varig på disk, så to krav motsier hverandre. PRD-en sier heller ikke hva som skjer med historikken (hvem sletter, hva om to selskaper lastes opp) eller om selskapsnavn og kontonavn kan sendes til OpenAI.
- **Forslag:** «Opplastede *filer* behandles i minnet. Verifiserte analyser lagres lokalt i SQLite. Eksempelfiler er syntetiske; ekte regnskapsdata skal ikke committes. Til OpenAI sendes kun aggregerte tall, uten selskapsnavn og kontonavn.» Legg til hvordan bruker sletter lagrede kjøringer.

### 4.3 Feilhåndtering, kostnad og kontroll av KI-teksten er ikke spesifisert
- **Alvorlighet:** høy
- **Hvor:** Story 3.1 «`post_validate_ai_response()` sikrer at KI-teksten ikke motsier avstemmingsstatusen»; FR-3.2
- **Problem og hvorfor det betyr noe:** Firewallen hindrer at KI regner, men ikke at teksten *siterer* feil tall. Det står ikke hva «motsier» betyr, hva som skjer ved timeout, ugyldig JSON, avvist svar eller mislykket validering, eller hva en kjøring koster.
- **Forslag:** Legg til et FR som: «Hvis API-kallet feiler eller validering mislykkes, vises det deterministiske mock-notatet med merknaden *KI utilgjengelig*, og appen krasjer ikke. Alle beløp i KI-teksten skal finnes i `metrics`; ellers forkastes svaret.» Angi modell, maks ett kall per kjøring og et kostnadsanslag per kjøring.

### 4.4 Epic 6–8 og KPI-ene mangler kriterier som kan sjekkes
- **Alvorlighet:** medium
- **Hvor:** Story 6.1, 7.1, 8.1 (ingen «Testbare akseptkriterier»); FR-7.1 «beregner … TKR og EKR»; FR-7.3 «mot SMB-normer»; NFR-2.1 «Vektoriserte Pandas-operasjoner»
- **Problem og hvorfor det betyr noe:** Uten formler og normverdier kan ingen utenfor gruppen avgjøre om TKR, EKR eller «lønnsomhetspotensial» er riktig, og regnskapsfaglig korrekthet er hovedrisikoen i domenet. NFR-2.1 og NFR-4.1 oppgir en implementasjon eller en «gjennomgang» som verifikasjon, ikke en måling.
- **Forslag:** Legg inn formel og ett regneeksempel per KPI («Egenkapitalandel = reell EK / sum eiendeler; eksempeldata gir 42,0 %»), og list normverdiene med kilde. For NFR-2.1: «5 000 rader gir ferdig rapport på under 5 s, målt i en pytest med tidtaking».

### 4.5 Ingen åpne spørsmål, antakelser eller motmål
- **Alvorlighet:** medium
- **Hvor:** § 2.1 «forklarer ikke *hvorfor* tallene svinger»; § 2.3 (kriterium 4 lister flere KPI-er enn FR-2.4); § 2.2 «Evaluator»
- **Problem og hvorfor det betyr noe:** PRD-en er «Godkjent» uten én synlig antakelse, selv om lønnsomhetsråd og fortegnsnormalisering (`abs()`) bygger på faglige valg. Tesen om å forklare *hvorfor* dekkes bare delvis av én periode med aggregerte tall. Ingen mål beskytter mot at KI-teksten blir overtydelig om usikre forklaringer.
- **Forslag:** Legg til en kort «Antakelser og åpne spørsmål» (f.eks. «ANTAKELSE: SMB-normene er veiledende, ikke revisjonsstandard») og ett motmål («Ingen KI-tekst presenterer en årsak som sikker uten deterministisk støtte»). Gjør daglig leder konkret med en tre-linjers situasjon.

## 5. Mekaniske funn

- **ID-er:** FR-1.1 til FR-8.2 er sammenhengende, og stories lenker til FR/NFR som finnes. Matrisen dekker FR, men ikke NFR.
- **Glossar mangler.** IB/UB/HB/SB forklares bare ved første bruk. «Styrepakke», «Mock KI»/«testmodus», «sensormodus» og «AI Firewall» brukes om hverandre.
- **Utdatert merking:** § 3.1 «v1 / v1.1» og § 8 «revisjonen til v1.1» står i en v2.0-PRD; § 3.2 sier «Kun NOK i v1/v1.1». «Status: Godkjent» og versjonslogg erstatter ikke frontmatter-status.
- **Små avvik:** NFR-6.1 `streamlit run app.py` mot `src/app.py`; § 2.3 pkt. 9 har ingen størrelsesgrense, mens NFR-2.1 har 5 000 rader; kodene K1–K7 forklares ikke i selve PRD-en.
- Ingen sensitive opplysninger funnet utover eierlinjen i dokumentkontrollen.

## 6. Før dere går videre

**Må avklares nå (før UX, arkitektur og epics):**
- Lagring og personvern (4.2), og hva som sendes til OpenAI.
- Hva som er MVP-kjerne og hva som kan kuttes (4.1).
- Feilhåndtering og kostnad for KI-kallet (4.3).
- Formler og normverdier for KPI-ene (4.4).

**Kan vente:** glossar, rydding av v1/v1.1-merking, korte NFR-presiseringer, flytting av testnavn til matrisen.

**Oppfølging av briefen:** *Delvis.* Fulgt opp: funksjonelle og testbare suksesskriterier med fasit, én primærbruker (daglig leder), testmodus uten API-nøkkel og oppdiktede eksempeldata. Ikke fulgt opp: omfanget (v2 er mye større enn én kjerneflyt) og en konkret styremøte-situasjon som eksempel.

## 7. Refleksjonsspørsmål

1. PRD-en er skrevet etter at koden fantes. Hvilke krav ville dere ha formulert annerledes, eller kuttet, hvis PRD-en var skrevet før koding, og hvordan kontrollerte dere at KI-en ikke bare beskrev det som allerede var bygget?
2. Hvordan har dere sjekket at formlene for TKR, EKR og lønnsomhetspotensial er regnskapsfaglig riktige, og hva godtok dere fra KI uten å kontrollere?

_Vurdert mot kvalitetsrubrikken i bmad-prd. Dette er veiledning, ikke sensur._
