"""
Hovedinngangspunkt for applikasjonen.
Gjør det mulig for sensor og brukere å starte appen direkte med:
    streamlit run app.py
"""
import sys
import os
import runpy

# Sikre at src-mappen er i Python-søkeveien
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'src'))
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Kjør applikasjonen fra src/app.py
runpy.run_path(os.path.join(src_path, 'app.py'), run_name='__main__')
