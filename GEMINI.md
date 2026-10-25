# Gemini Antigravity — Prosjektinstruksjoner og BMAD-rammeverk

Dette prosjektet er utviklet for emnet **IBE160 Programmering med KI** ved Høgskolen i Molde.
Prosjektet implementerer en spesialisert regnskapsapplikasjon for SMB: **Ledelsesrapport og Regnskapskontroll med KI**.

---

## 🏛️ BMAD Roller og Agent-ferdigheter i Antigravity

Prosjektet følger **BMAD-metodologien** (Business, Market, Architecture, Design) tilpasset **Gemini Antigravity**. Ferdighetene er plassert i `.agents/skills/` og aktiveres automatisk etter behov (Progressive Disclosure):

* **Analyst (`.agents/skills/bmad-agent-analyst`):** Domeneanalyse, regnskapsregler, NS 4102-kontoplan og faglærers føringer.
* **PM (`.agents/skills/bmad-agent-pm`):** Produktstyring, scoping, PRD og agile brukerhistorier.
* **Architect (`.agents/skills/bmad-agent-architect`):** Systemdesign, "The AI Firewall" og deterministisk dataintegritet.
* **UX Designer (`.agents/skills/bmad-agent-ux-designer`):** Streamlit-grensesnitt, informasjonsarkitektur, WCAG og ReportLab PDF-design.
* **Developer (`.agents/skills/bmad-agent-dev`):** Python-kodebase, Pandas-transformasjoner, Pydantic-skjemaer og testdrevet utvikling.
* **Quality Assurance (`.agents/skills/bmad-code-review`):** Sensorveiledning-compliance, balansekontroll ($\sum D = \sum K$) og kryssavstemming ($IB + HB = UB$).

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
