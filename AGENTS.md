# AGENTS.md — Felles Agentinstruksjoner og BMAD-rammeverk

Dette prosjektet er utviklet for emnet **IBE160 Programmering med KI** ved Høgskolen i Molde.
Prosjektet implementerer: **Ledelsesrapport og regnskapskontroll med KI (G56-guimaraes)**.

Språk for all dokumentasjon, brukergrensesnitt og agent-dialog: **Norsk (Bokmål)**.

---

## 🏛️ BMAD Roller og Agent-ferdigheter (AiDD)

Prosjektet benytter **BMAD-metodologien** (Business, Market, Architecture, Design).
Ferdighetene er implementert i både `.agents/skills/` (for Gemini Antigravity) og `.claude/skills/` (for Claude Code):

* **Analyst (`bmad-agent-analyst`):** Domeneanalyse, regnskapsregler, NS 4102-kontoplan og faglærers føringer.
* **PM (`bmad-agent-pm`):** Produktledelse, PRD, scoping, Epics og User Stories med akseptansekriterier.
* **Architect (`bmad-agent-architect`):** Systemdesign, "The AI Firewall" og deterministisk dataintegritet.
* **UX Designer (`bmad-agent-ux-designer`):** Streamlit-grensesnitt, informasjonsarkitektur, WCAG og ReportLab PDF-design.
* **Developer (`bmad-agent-dev`):** Python-kodebase, Pandas-transformasjoner, Pydantic-skjemaer og testdrevet utvikling.
* **QA & Compliance (`bmad-code-review`):** Sensorveiledning-sjekk, balansekontroll ($\sum D = \sum K$) og kryssavstemming ($IB + HB = UB$).

---

## 🛡️ "The AI Firewall" (Ufravikelige arkitekturregler)

1. **Kode regner, KI forklarer:**
   * Språkmodeller (LLM) skal **aldri** summere, trekke fra eller regne på regnskapstall.
   * Alle summeringer, differanser og avstemminger skal utføres deterministisk i Python/Pandas.
2. **Strukturert KI-utdata:**
   * LLM-respons skal alltid valideres via Pydantic Structured Outputs (`ManagementCommentary`).
3. **Frakoblet sensormodus:**
   * Applikasjonen skal alltid kunne kjøres 100 % lokalt og offline via "Mock KI"-modus uten API-nøkkel.
4. **Norske standarder:**
   * Støtte semikolon (`;`) og komma (`,`) som skilletegn, samt komma som desimaltegn (`100 000,00`).
   * Mapping mot Norsk Standard Kontoplan (NS 4102).
5. **Datasikkerhet og minne:**
   * Regnskapsfiler skal aldri lagres persistent på disk eller lekkes utenfor minnet (`io.BytesIO`).
