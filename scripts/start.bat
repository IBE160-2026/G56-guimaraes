@echo off
echo ==========================================
echo Starting Streamlit App...
echo ==========================================
if exist ".\.venv\Scripts\streamlit.exe" (
    ".\.venv\Scripts\streamlit.exe" run app.py
) else (
    streamlit run app.py
)
