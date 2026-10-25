@echo off
echo ==========================================
echo Running unit tests (pytest)...
echo ==========================================
if exist ".\.venv\Scripts\pytest.exe" (
    ".\.venv\Scripts\pytest.exe" -v tests/
) else (
    pytest -v tests/
)
