# Repo-sanering og mappestruktur

## 2026-11-06 kl. 21:58 — turnaround1207

### Oppgave
Gjennomføre en fullstendig sanering og restrukturering av fil- og mappestrukturen i `G56-guimaraes` i henhold til BMAD-metodikken og sensorveiledningen i IBE160 (Kriterium 5, 6 og 7), for å fjerne byte-identiske duplikater, utdaterte proposal-artefakter («zombie-dokumentasjon») og overflødige toppnivåmapper.

### Plan
- Identifisere og fjerne 100 % byte-identiske duplikatfiler (`ai-log/`, `planning-artifacts/briefs/brief-prompt/brief.md`, `planning-artifacts/briefs/brief-prompt/tilbakemelding-product-brief.md`) og utdaterte logger (`_bmad-output/verification-log.md`, `addendum.md`, `.memlog.md`).
- Fjerne utdaterte dokumentasjonsfiler fra tidlig proposal-fase (`docs/BMAD_AGENT_ENGINEERING.md`, `docs/BMAD_ROLES.md`, og `README.md`-stubber i `docs/01_analysis/` til `04_architecture/`) som feilaktig beskrev SAF-T, Polars, WeasyPrint og kommersielle vekstmål.
- Konsolidere kursstyringsdokumenter og brief-logg (`sensorveiledning.md`, `tilbakemelding-product-brief.md` og `brief-ki-logg.md`) under `docs/00_course_and_brief/`, og fjerne toppnivåmappene `course/` og `planning-artifacts/`.
- Flytte `sesjonslogg`-ferdigheten fra `.claude/skills/sesjonslogg` til `.agents/skills/sesjonslogg`, forankre den i `AGENTS.md`, `GEMINI.md` og `_bmad/_config/skill-manifest.csv`, og fjerne `.claude/` samt `CLAUDE.md`.
- Rense `.gitignore` for Next.js/Node-støy, oppdatere alle interne lenker og mappetrær i `README.md`, `docs/02_product/PRD.md` og `docs/04_architecture/ARCHITECTURE.md`, og verifisere med `pytest -v tests/`.

### Resultat
- **Slettet duplikater og utdaterte mapper:**
  - Fjernet `ai-log/`, `_bmad-output/`, `course/`, `planning-artifacts/`, `.claude/` og `CLAUDE.md` (redusert fra 16 til 11 toppnivåmapper).
  - Fjernet utdaterte proposal-artefakter: `docs/BMAD_AGENT_ENGINEERING.md`, `docs/BMAD_ROLES.md`, `docs/01_analysis/README.md`, `docs/02_product/README.md`, `docs/03_ux/README.md` og `docs/04_architecture/README.md`.
- **Konsolidert dokumentasjon og ferdigheter:**
  - Etablert `docs/00_course_and_brief/` med `sensorveiledning.md`, `tilbakemelding-product-brief.md` og `brief-ki-logg.md`.
  - Flyttet `sesjonslogg` til `.agents/skills/sesjonslogg/SKILL.md` og oppdatert `AGENTS.md`, `GEMINI.md` og `_bmad/_config/skill-manifest.csv`.
- **Oppdatert konfigurasjon og kryssreferanser:**
  - Renset `.gitignore` til kun relevante Python-, test-, hemmelighets-, BMAD- og OS-regler.
  - Synkronisert alle dokumentasjonslenker og ASCII-mappetrær i `README.md`, `docs/02_product/PRD.md` og `docs/04_architecture/ARCHITECTURE.md`.
- **Verifisering:**
  - Kjørt `.\.venv\Scripts\pytest.exe -v tests/`: **30 av 30 enhetstester bestått** (`30 passed in 4.77s`).
- **Lukket åpent punkt:**
  - Lukket siste åpne punkt fra [ui-opplastingsrutenett-og-ux-wireframes](998-2026-11-06-21-06-00-ui-opplastingsrutenett-og-ux-wireframes.md) i `issues.md`.

### Åpne punkter
- Ingen.
