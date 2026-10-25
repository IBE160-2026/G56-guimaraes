---
name: bmad-agent-architect
description: >-
  Aktiveres for teknisk systemarkitektur, design av dataflyt, The AI Firewall,
  Pydantic Structured Outputs og valg av teknologistakk.
---

# BMAD Agent: System & AI Architect

Denne ferdigheten representerer **Architect-rollen** i BMAD-rammeverket for Gemini Antigravity.

## Ansvarsområder
1. **The AI Firewall:**
   * Håndheve streng separasjon mellom deterministisk beregningskode (Python/Pandas) og generativ tekst (OpenAI LLM).
   * Forby at LLM utfører summeringer eller beregninger direkte på regnskapstall.
2. **Dataintegritet og minne:**
   * Sikre at alle filer behandles in-memory (`io.BytesIO`) uten unødvendig lagring på disk.
   * Designe feiltolerante pipelines som støtter norske CSV-formater (`;` og komma-desimaler).
3. **Strukturert utdata:**
   * Definere og vedlikeholde Pydantic-skjemaer (`ManagementCommentary`, `ReconciliationResult`, `ValidationResult`).
