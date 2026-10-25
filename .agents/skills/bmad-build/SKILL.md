---
name: bmad-build
description: >-
  Aktiveres for den utførende byggesløyfen i BMAD: kodegenerering, kjøring av tester,
  integrasjon av moduler og verifisering av funksjonell virkemåte.
---

# BMAD Skill: Build & Verify Loop

Instruksjoner for byggeprosessen i Gemini Antigravity.

## Fremgangsmåte
1. **Les spesifikasjon:** Konsulter `docs/02_product/PRD.md` og `docs/04_architecture/ARCHITECTURE.md`.
2. **Implementer kode:** Skriv ny modul eller modifiser eksisterende i `src/`.
3. **Kjør tester:** Verifiser med `pytest -v tests/`.
4. **Verifiser i app:** Test i Streamlit lokalt med eksempeldata i `data/sample/`.
