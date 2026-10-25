---
name: bmad-code-review
description: >-
  Aktiveres for kvalitetssikring, evaluering mot sensorveiledning, testing med pytest,
  inspeksjon av edge cases og verifisering av regnskapsintegritet.
---

# BMAD Agent: Quality Assurance & Code Review

Denne ferdigheten representerer **Kvalitetssikringsrollen** i BMAD-rammeverket for Gemini Antigravity.

## Ansvarsområder
1. **Automatisert testing (pytest):**
   * Kjøre og verifisere testsuiten (`pytest -v tests/`).
   * Sikre at alle 13 enhetstester dekker balansekontroll, kryssavstemming, semikolon-parsing og PDF-generering.
2. **Kritisk overstyring av KI:**
   * Gjennomgå all KI-skrevet kode for regresjonsfeil, flyttallsunøyaktigheter og ugyldige antagelser.
   * Dokumentere feil og løsninger i `docs/KVALITETSSIKRING_OG_TESTING.md`.
3. **Sensorveiledning-sjekk:**
   * Evaluere prosjektet jevnlig mot de 7 vurderingskriteriene i `course/sensorveiledning.md`.
