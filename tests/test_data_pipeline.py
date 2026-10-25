import pytest
import io
import sys
import os
import pandas as pd

# Legger src-mappen til i system path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from data_pipeline import process_csv_in_memory, detect_csv_delimiter_and_encoding, clean_norwegian_numeric_series

class TestDataPipelineEdgeCases:

    def test_norwegian_semicolon_and_comma_decimal(self):
        """Tester at en typisk norsk regnskaps-CSV (semikolon, Kontonr, desimalkomma, tusenskilletegn) parses feilfritt."""
        sample_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../data/sample/saldobalanse_norsk_semikolon.csv'))
        with open(sample_path, 'rb') as f:
            file_bytes = io.BytesIO(f.read())
            
        df = process_csv_in_memory(file_bytes, "saldobalanse_norsk_semikolon.csv")
        
        # Sjekk at 'Kontonr' er normalisert til 'Konto'
        assert 'Konto' in df.columns
        assert 'Kontonavn' in df.columns
        
        # Sjekk at tallene er konvertert fra '100 000,00' til 100000.0
        assert df.loc[df['Konto'] == '1920', 'IB'].iloc[0] == 100000.0
        assert df.loc[df['Konto'] == '1920', 'Debet'].iloc[0] == 200000.0
        assert df.loc[df['Konto'] == '1920', 'Kredit'].iloc[0] == 120000.0
        assert df.loc[df['Konto'] == '1920', 'UB'].iloc[0] == 180000.0
        
        # Total sum Debet og Kredit skal stemme
        assert df['Debet'].sum() == 530000.0
        assert df['Kredit'].sum() == 530000.0

    def test_missing_account_column_raises_clear_error(self):
        """Tester at manglende Konto-kolonne gir en pedagogisk og vennlig feilmelding."""
        bad_csv = io.BytesIO(b"FeilKolonne1,FeilKolonne2,Debet,Kredit\n10,20,100,100")
        with pytest.raises(ValueError, match="mangler den p.*krevde kolonnen 'Konto'"):
            process_csv_in_memory(bad_csv, "ugyldig_fil.csv")

    def test_empty_file_raises_clear_error(self):
        """Tester at en tom fil avvises med forklarende feilmelding."""
        empty_csv = io.BytesIO(b"")
        with pytest.raises(ValueError, match="er tom"):
            process_csv_in_memory(empty_csv, "tom_fil.csv")

    def test_clean_norwegian_numeric_series(self):
        """Tester konvertering av ulike varianter av norske tallformater."""
        raw_series = pd.Series(["1 500,50", "15.000,25", "100", "-50,00", None, ""])
        cleaned = clean_norwegian_numeric_series(raw_series)
        
        assert cleaned.iloc[0] == 1500.50
        assert cleaned.iloc[1] == 15000.25
        assert cleaned.iloc[2] == 100.0
        assert cleaned.iloc[3] == -50.00
        assert cleaned.iloc[4] == 0.0
        assert cleaned.iloc[5] == 0.0
