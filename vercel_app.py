"""
Vercel-inngangspunkt for G56 – Ledelsesrapport og regnskapskontroll med KI.

Streamlit krever en langlevende server med WebSocket-tilkobling og kan derfor
ikke kjøres som en Vercel Function. Denne lette WSGI-appen (kun standardbibliotek)
gir Vercel et gyldig `app`-objekt og serverer en informasjonsside, mens selve
applikasjonen fortsatt startes lokalt med `streamlit run app.py`.
"""

from html import escape

PROJECT_TITLE = "G56 – Ledelsesrapport og regnskapskontroll med KI"

FEATURES = [
    "Opplasting av saldobalanse og hovedbok (.csv / .xlsx) med norsk tallformat",
    "Mapping mot Norsk Standard Kontoplan (NS 4102) og resultatoppstilling",
    "Balansekontroll og kryssavstemming (IB + HB = UB) for revisor",
    "Finansanalyse, nøkkeltall og bransjesammenligning",
    "KI-generert ledelseskommentar med deterministiske beregninger i Python",
    "Eksport av styrepakke og beslutningsrapport til PDF og HTML",
]

PAGE_TEMPLATE = """<!doctype html>
<html lang="nb">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="{description}">
<meta name="theme-color" content="#0f2a44">
<title>{title}</title>
<style>
  :root {{ --bg:#f5f7fa; --fg:#14202e; --muted:#4a5868; --accent:#0f2a44; --card:#ffffff; --border:#dde3ea; }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; font-family:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif; background:var(--bg); color:var(--fg); line-height:1.6; }}
  main {{ max-width:760px; margin:0 auto; padding:56px 24px; display:flex; flex-direction:column; gap:28px; }}
  .eyebrow {{ font-size:.8rem; letter-spacing:.08em; text-transform:uppercase; color:var(--muted); margin:0; }}
  h1 {{ font-size:clamp(1.75rem,4vw,2.4rem); line-height:1.2; margin:8px 0 0; color:var(--accent); text-wrap:balance; }}
  h2 {{ font-size:1.15rem; margin:0 0 12px; }}
  p {{ margin:0; color:var(--muted); }}
  section {{ background:var(--card); border:1px solid var(--border); border-radius:12px; padding:24px; }}
  ul {{ margin:0; padding-left:20px; display:flex; flex-direction:column; gap:6px; }}
  pre {{ margin:12px 0 0; background:var(--accent); color:#f5f7fa; padding:16px; border-radius:8px; overflow-x:auto; font-size:.9rem; }}
  footer {{ font-size:.85rem; color:var(--muted); }}
</style>
</head>
<body>
<main>
  <header>
    <p class="eyebrow">IBE160 Programmering med KI · Høgskolen i Molde</p>
    <h1>{title}</h1>
  </header>
  <p>Applikasjonen er bygget med Streamlit, som krever en kontinuerlig kjørende server.
  Denne siden er publisert på Vercel som prosjektside; selve analyseverktøyet kjøres lokalt.</p>
  <section aria-labelledby="funksjoner">
    <h2 id="funksjoner">Funksjoner</h2>
    <ul>{features}</ul>
  </section>
  <section aria-labelledby="kom-i-gang">
    <h2 id="kom-i-gang">Kjør applikasjonen lokalt</h2>
    <p>Fungerer 100 % offline i «Mock KI»-modus uten API-nøkkel.</p>
    <pre><code>pip install -r requirements.txt
streamlit run app.py</code></pre>
  </section>
  <footer>Kode regner, KI forklarer.</footer>
</main>
</body>
</html>
"""


def _render_page() -> bytes:
    features = "".join(f"<li>{escape(item)}</li>" for item in FEATURES)
    html = PAGE_TEMPLATE.format(
        title=escape(PROJECT_TITLE),
        description=escape("Ledelsesrapport, finansanalyse og regnskapskontroll med KI (NS 4102)."),
        features=features,
    )
    return html.encode("utf-8")


def app(environ, start_response):
    """WSGI-applikasjon som Vercel laster som funksjonshåndterer."""
    path = environ.get("PATH_INFO", "/") or "/"

    if path == "/health":
        body = b'{"status":"ok"}'
        content_type = "application/json"
        status = "200 OK"
    elif path in ("/", "/index.html"):
        body = _render_page()
        content_type = "text/html; charset=utf-8"
        status = "200 OK"
    else:
        body = "Siden finnes ikke.".encode("utf-8")
        content_type = "text/plain; charset=utf-8"
        status = "404 Not Found"

    headers = [
        ("Content-Type", content_type),
        ("Content-Length", str(len(body))),
        ("X-Content-Type-Options", "nosniff"),
        ("Referrer-Policy", "strict-origin-when-cross-origin"),
        ("Strict-Transport-Security", "max-age=63072000"),
    ]
    start_response(status, headers)
    return [body]
