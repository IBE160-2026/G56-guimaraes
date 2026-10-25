# scripts/run_tests.ps1 - Kjører testsuiten i prosjektets venv
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "🧪 Kjører automatiserte tester for G56..." -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

if (Test-Path ".\.venv\Scripts\pytest.exe") {
    .\.venv\Scripts\pytest.exe -v tests/
} elseif (Get-Command pytest -ErrorAction SilentlyContinue) {
    pytest -v tests/
} else {
    Write-Host "❌ Fant ikke pytest. Aktiver virtuelt miljø først: .\.venv\Scripts\Activate.ps1" -ForegroundColor Red
    exit 1
}
