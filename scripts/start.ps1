# scripts/start.ps1 - Starter Streamlit-appen i prosjektets venv
Write-Host "==========================================" -ForegroundColor Green
Write-Host "🚀 Starter Ledelsesrapport og Regnskapskontroll..." -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green

if (Test-Path ".\.venv\Scripts\streamlit.exe") {
    .\.venv\Scripts\streamlit.exe run app.py
} elseif (Get-Command streamlit -ErrorAction SilentlyContinue) {
    streamlit run app.py
} else {
    Write-Host "❌ Fant ikke streamlit. Aktiver virtuelt miljø først: .\.venv\Scripts\Activate.ps1" -ForegroundColor Red
    exit 1
}
