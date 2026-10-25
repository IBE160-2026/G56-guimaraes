# Avvik fra Opprinnelig Proposal (Begrunnelse for Endret Omfang)

* **Dokument-ID:** SCOPE-DIFF-01
* **Prosjekt:** G56 – Ledelsesrapport og forenklet kontroll av regnskap med KI
* **Forankring:** Vurderingskriterium 2 i sensorveiledningen for IBE160 («At det som er utelatt eller endret fra proposal, er beskrevet og begrunnet»).

---

## 1. Bakgrunn for Justeringen

I det opprinnelige prosjektforslaget (Proposal / tidlig idéutkast) var ambisjonsnivået svært bredt. Forslaget skisserte en omfattende fler-kilde plattform som skulle håndtere:
* 5 ulike filtyper (Saldobalanse, Reskontro, CRM-data, Timelister og ESG-forbruk).
* 3 filformater, inkludert full XML-parsing av komplekse SAF-T Financial filer.
* Samstilling på tvers av flere valutaer.
* Direkte Altinn-rapportering og Stripe-betalingsløsninger.

### Faglærers Tilbakemelding (2026-10-06)
Faglærer evaluerte opprinnelig brief med følgende konklusjon:
> *"Vanskelighetsgrad: Vanskelig... Omfanget i v1 er altfor stort for en gruppe på én person... Definer en minimal versjon som sikkert kan bli ferdig – én saldobalanse med kontroll, mapping og KI-sammendrag – og legg resten i tydelige trinn etterpå."*

---

## 2. Gruppens Valg: Spisset Kjerneflyt med Saldobalanse OG Hovedbok

Gruppen vurderte faglærers forslag om å kun se på saldobalansen, men valgte bevisst å beholde **både Saldobalanse (SB) og Hovedbok (HB)**. 

### Faglig Begrunnelse:
En saldobalanse alene viser kun statiske periodetall. Ved å inkludere Hovedboken (transaksjonsloggen) kunne vi etablere en **reell, dyp regnskapskontroll**:
$$\text{Inngående Balanse (IB)} + \sum(\text{Transaksjoner i Hovedboken}) = \text{Utgående Balanse (UB)}$$

Dette hever det faglige nivået i applikasjonen betydelig, samtidig som det holder seg strengt innenfor et realistisk tids- og kodeomfang for én person.

---

## 3. Matrise over Hva som er Med (v1) vs. Hva som er Flyttet (v2 / Vision)

| Funksjon / Modul | Status i Proposal | Status i v1 (Nå) | Begrunnelse for Endring |
|:---|:---|:---|:---|
| **Saldobalanse (SB)** | Inkludert | 🟢 **Inkludert i v1** | Kjernegrunnlag for balanse- og resultatrapportering etter NS 4102. |
| **Hovedbok (HB)** | Inkludert | 🟢 **Inkludert i v1** | Nødvendig for å utføre kryssavstemming ($IB + HB = UB$) og avdekke feilkonteringer. |
| **Balansekontroll ($\sum D = \sum K$)** | Inkludert | 🟢 **Inkludert i v1** | Grunnleggende dobbelt bokføringskontroll implementert i Pandas. |
| **NS 4102 Mapping** | Inkludert | 🟢 **Inkludert i v1** | Standardisering til norsk kontoplan for deterministisk nøkkeltallsberegning. |
| **KI-ledelsesnotat** | Inkludert | 🟢 **Inkludert i v1** | OpenAI Structured Outputs (Pydantic) med CFO Tone-of-Voice. |
| **Frakoblet Testmodus (Mock)** | Ikke beskrevet | 🟢 **Lagt til i v1** | Sikrer at sensor kan kjøre full flyt lokalt uten egen API-nøkkel (Sensorveiledning krav 6). |
| **PDF-eksport** | Inkludert | 🟢 **Inkludert i v1** | Programmatisk ReportLab-generering direkte in-memory. |
| **SAF-T (XML-format)** | Inkludert | 🟡 **Flyttet til v2** | SAF-T er en omfattende XML-standard med tusenvis av noder. Tar uforholdsmessig mye tid å feilsøke i et 15-studiepoengs emne. CSV/Excel dekker 100 % av behovet for SMB. |
| **Flervaluta** | Inkludert | 🟡 **Flyttet til v2** | V1 begrenses til NOK. Flervaluta krever håndtering av agio/disagio og historiske kurser, som trekker fokus bort fra kjerneflyten. |
| **Reskontro, CRM, Timer, ESG** | Inkludert | 🟡 **Flyttet til v2** | Ekstra operasjonelle kilder flyttet til videre arbeid. Én stabil og testet kjerneflyt gir høyere faglig verdi enn 5 uferdige moduler. |
| **Direkte ERP API & Altinn** | Inkludert | 🔴 **Eksplisitt ute** | Krever produksjonsnøkler fra Altinn/Skatteetaten og betalte ERP-utviklerkontoer som sensor ikke kan teste lokalt. |
| **Stripe / Abonnementsbetaling** | Nevnt i mål | 🔴 **Eksplisitt ute** | Kommersiell funksjon uten faglig relevans for vurdering av applikasjonslogikk i IBE160. |

---

## 4. Konklusjon
Ved å gjøre denne bevisste omfangsjusteringen har vi gått fra en urealistisk plan med stor risiko for uferdige komponenter, til et **komplett, stabilt og 100 % testet produkt**. 

Appen løser kjerneproblemet fra proposal – *å eliminere manuell Excel-avstemming og forklare regnskapstall for styret* – på en mer robust og elegant måte enn opprinnelig foreslått.
