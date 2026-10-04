# 04 Architecture Phase (Backend, AI & Security)

Her lagres teknisk systemdesign, dataflyt, infrastruktur og sikkerhetskrav.

## Roller tilknyttet denne fasen

### Kjerneteam
* **Architect (Arkitekt):** Definerer den overordnede teknologiske retningen og datamodelleringen. Bygger pipelinen: `CSV/SAF-T -> Pandas -> AI Prompting -> PDF`.

### Spesialiserte Engineering Roller (Topp 10 % Personas)
* **Data Pipeline & Performance Architect (Elite Backend / Data Engineer):** Bygger selve "rørsystemet". Benytter vektoriserte operasjoner (Polars), in-memory prosessering og `iterparse` for store XML-filer. Prosesserer 2 GB finansdata på få sekunder med minimalt minnebruk.
* **Cognitive / LLM Integration Engineer (Elite AI-Backend & Prompt Engineer):** Bygger skuddsikre integrasjoner mot OpenAI. Bruker *Structured Outputs* og Function Calling for deterministiske svar. Håndterer token-optimalisering, fallback, og AI "Tone-of-Voice".
* **AppSec & LLM Firewall Engineer (Sikkerhet / CISO):** Koder med "In-Memory Only" - sensitive regnskapsfiler berører aldri disken, kun RAM (`io.BytesIO`). Bygger LLM-guardrails mot "Prompt Injection" i filene.
* **Test Automation Engineer (SDET):** Koder *Property-Based Testing* (f.eks. med `hypothesis`). Genererer tusenvis av unormale og provoserende scenarier (negative valutaer, ødelagt XML) for å stresse avviksdeteksjonen.
* **Kontroller av Anbefalinger (AI Fact-Checker):** Filtrerer AI-ens utdata, og kjører "LLM-as-a-judge"-rutiner for å sikre null hallusinasjoner i ledelsesrapportene.

**Eksempler på innhold i denne mappen:**
- Systemarkitektur-diagrammer
- Datamodeller, SAF-T parsere og flytskjemaer
- Sikkerhetsvurderinger og LLM API-design
