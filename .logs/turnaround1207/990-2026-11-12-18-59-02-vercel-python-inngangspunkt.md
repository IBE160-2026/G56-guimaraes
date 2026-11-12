# Vercel Python-inngangspunkt

## 2026-11-12 kl. 18:59 — v0

### Oppgave
Vercel-deploy feilet med `PYTHON_ENTRYPOINT_NOT_FOUND`: `app.py` og `src/app.py` er Streamlit-skript og eksporterer ingen `app`/`application`/`handler`.

### Plan
- Streamlit krever langlevende server + WebSocket og kan ikke kjøres som Vercel Function.
- Legge til et eget, lett WSGI-inngangspunkt (kun standardbibliotek) og peke Vercel dit via `[tool.vercel] entrypoint` i `pyproject.toml`, uten å endre Streamlit-appen.

### Resultat
- Ny `vercel_app.py`: WSGI-`app` som serverer en norsk prosjektside (`/`), `/health` og 404, med grunnleggende sikkerhetsheadere.
- Ny `pyproject.toml`: `entrypoint = "vercel_app:app"`, `dependencies = []` (Vercel-funksjonen trenger ingen pakker; `requirements.txt` brukes fortsatt lokalt).
- Verifisert lokalt med `vercel build` og prosjektets `python`-preset: bygget fullførte og produserte `python.func`.
- `streamlit run app.py` er uendret.

### Åpne punkter
- Selve Streamlit-appen er ikke tilgjengelig på Vercel; for en kjørbar nettversjon må den hostes på en plattform med langlevende servere (f.eks. Streamlit Community Cloud).
