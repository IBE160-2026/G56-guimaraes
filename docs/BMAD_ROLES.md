# BMAD Metodikk og Rollesystem

Dette prosjektet bruker **BMAD-rammeverket** (Business, Market, Architecture, Design) for å sikre en strukturert og effektiv utviklingsprosess av plattformen: *Ledelsesrapport og forenklet kontroll av regnskap med KI*.

Alle roller, fra forretningsstrategi til elite-utvikling, er nå nøye fordelt inn i prosjektets respektive faser (mapper). 

## Faseinndeling og Rolleseparasjon

For detaljer om spesifikke fageksperter og topp-10 % agent-personas, se `README.md` filen i hver enkelt mappe:

1. **[01_analysis (Business)](./01_analysis/README.md):** 
   - Eies av *Business Analyst*.
   - Inneholder **Domenespesifikke Fageksperter** (GRS-spesialist, IFRS-spesialist, Strategisk Regnskapsfører) og AI-Orkestratoren for analyse.

2. **[02_product (Market & Growth)](./02_product/README.md):** 
   - Eies av *Product Manager*.
   - Inneholder **Go-To-Market og Kommersielle Roller** (Markedsfører, Kundeekspert, SEO-optimerer, Growth Hacker).

3. **[03_ux (Design & Frontend)](./03_ux/README.md):** 
   - Eies av *UX Designer*.
   - Inneholder spesialiserte roller for grensesnittet (Streamlit/SPA Architecture Master, Typographic & PDF Engine Developer).

4. **[04_architecture (System & Sikkerhet)](./04_architecture/README.md):** 
   - Eies av *Architect*.
   - Inneholder **Elite Engineering og Sikkerhetsroller** (Backend Pipeline Master, LLM Integration Engineer, AppSec / CISO, og Test Automation SDET).

## Utførelse og AI-Agents (AiDD)

Når oppgavene har gått gjennom disse fire fasene og er klare for koding (Implementation Loop), tar de prosessdrevne AI-Agentene over. Reglene og strukturen for byggefasen, inkludert funksjoner for *bmad-recon*, *bmad-build* og teamets **Competence Monitor** (Kvalitetssikrer), finnes dokumentert i et eget dedikert dokument for systemstyring:

➡️ **[Se BMAD_AGENT_ENGINEERING.md for oppsett av selve AI-utviklerne](./BMAD_AGENT_ENGINEERING.md)**

---
**GitHub Issues for Rolle-sporing**
Vi benytter fortsatt GitHub Labels for å holde oversikt over hvem som gjør hva. Hver oppgave merkes med f.eks. `role: analyst`, `role: pm`, `role: frontend`, `role: security`, og eventuelt `skill: bmad-build` for oppgaver sendt til agentene.
