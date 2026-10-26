# CLAUDE.md — Agentinstruksjoner for Claude Code

Se fullstendige agentinstruksjoner i [AGENTS.md](./AGENTS.md) og [GEMINI.md](./GEMINI.md).

## Prosjektoversikt
* **Prosjekt:** G56 — Ledelsesrapport og regnskapskontroll med KI
* **Emne:** IBE160 Programmering med KI (Høgskolen i Molde)
* **BMAD Skills:** Plassert i `.claude/skills/` og `.agents/skills/`
* **Arkitekturregel:** "The AI Firewall" — koden regner deterministisk i Pandas, KI forklarer via Pydantic Structured Outputs.
* **Språk:** Norsk

## Sesjonslogg

Når en oppgave eller økt avsluttes, før sluttoppsummeringen, bruk `sesjonslogg`-skillen: dokumenter Oppgave + Plan + Resultat + åpne punkter i `.logs/<bruker>/`, og før åpne punkter i `.logs/<bruker>/issues.md`. Skillen committer loggfila lokalt; push gjør du selv. Gruppens egne regler for commit og språk gjelder foran dette.
