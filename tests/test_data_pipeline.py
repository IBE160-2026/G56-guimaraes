import pytest
import io
import sys
import os
import pandas as pd

# Legger src-mappen til i system path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from data_pipeline import (
    process_csv_in_memory, 
    process_excel_in_memory, 
    detect_csv_delimiter_and_encoding, 
    clean_norwegian_numeric_series,
    validate_input
)

class TestDataPipelineEdgeCases:

    @pytest.mark.parametrize("invalid_csv,expected_err", [
        (b"", "er tom"),
        (b"Header1,Header2\nVal1,Val2", "mangler den p.*krevde kolonnen 'Konto'"),
        (b"Konto;Kontonavn\n1000;Kasse", "mangler p.*krevde bel.*pskolonner"),
    ])
    def test_parametrized_invalid_csv_inputs(self, invalid_csv, expected_err):
        """Tester flere typer ugyldige CSV-inndata via pytest-parametrisering."""
        buf = io.BytesIO(invalid_csv)
        with pytest.raises(ValueError, match=expected_err):
            df = process_csv_in_memory(buf, "ugyldig.csv")
            validate_input(df, expected_type="SB")

    def test_validate_input_detects_empty_dataframe(self):
        """Tester at validate_input avviser tomme DataFrames."""
        with pytest.raises(ValueError, match="Datagrunnlaget er tomt"):
            validate_input(pd.DataFrame(), expected_type="SB")

    def test_large_numbers_and_norwegian_special_characters_pdf(self):
        """Tester at store tall (milliarder) og æ, ø, å håndteres uten overflyt eller tegnsettfeil."""
        from pdf_generator import generate_management_pdf
        from llm_integration import ManagementCommentary, ActionItem
        
        rep = ManagementCommentary(
            hovedkonklusjon="Selskapet har omsatt for 1 250 000 000,50 NOK med sunn vekst i Ålesund og Tromsø.",
            lonnsomhet_og_marginer="Lønnskostnadene i perioden utgjør 450 000 000 NOK. Driftsmarginen er 18,5 %.",
            likviditet_og_arbeidskapital="Bankinnskudd utgjør 320 000 000 NOK hos DNB og SpareBank 1.",
            revisors_avstemmingsnotat="Ingen feil i avstemmingen. Debet = Kredit på tvers av samtlige poster.",
            potensielle_avvik=["Råvareprisene øker, valutapåvirkning bør overvåkes."],
            tiltaksliste=[
                ActionItem(
                    tiltak="Iverksett sikringsavtaler for råvarekjøp i euro.",
                    begrunnelse="Valutasvingninger truer driftsmarginen.",
                    prioritet="Høy",
                    forventet_effekt="Reduserer finansiell risiko med 25 %."
                )
            ]
        )
        pdf_buf = generate_management_pdf("Norsk Storkonsern AS (ÆØÅ)", rep)
        assert len(pdf_buf.getvalue()) > 1000
        assert pdf_buf.getvalue().startswith(b"%PDF-")

    def test_excel_file_processing(self):
        """Tester at in-memory Excel-filer (.xlsx) leses og normaliseres korrekt."""
        # Opprett et test-Excel ark i minnet
        df_sample = pd.DataFrame({
            'Kontonummer': ['3000', '4000'],
            'Kontonavn': ['Salgsinntekter', 'Varekostnad'],
            'Debet': ['0,00', '40 000,00'],
            'Kredit': ['100 000,00', '0,00']
        })
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            df_sample.to_excel(writer, index=False, sheet_name='Saldobalanse')
            
        excel_buffer.seek(0)
        res_dict = process_excel_in_memory(excel_buffer, "test_saldobalanse.xlsx")
        
        assert 'Saldobalanse' in res_dict
        sheet_df = res_dict['Saldobalanse']
        assert 'Konto' in sheet_df.columns
        assert sheet_df['Kredit'].sum() == 100000.0
        assert sheet_df['Debet'].sum() == 40000.0

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

    def test_norwegian_erp_column_variations(self):
        """Tester at typiske kolonnenavn fra Tripletex/Visma (f.eks. 'Konto ID', 'Debetbeløp') normaliseres."""
        from data_pipeline import normalize_column_names
        raw_df = pd.DataFrame(columns=['Konto ID', 'Kontotekst', 'Debetbeløp', 'Kreditbeløp', 'IB Beløp', 'UB Beløp'])
        normalized = normalize_column_names(raw_df)
        assert 'Konto' in normalized.columns
        assert 'Kontonavn' in normalized.columns
        assert 'Debet' in normalized.columns
        assert 'Kredit' in normalized.columns
        assert 'IB' in normalized.columns
        assert 'UB' in normalized.columns

    def test_mixed_decimal_and_spaces_in_currency(self):
        """Tester robusthet mot ekstreme norske tallformater som ' 1 250 450,75 '."""
        s = pd.Series([" 1 250 450,75 ", "25 000.00", "0,50", " -150,00 "])
        cleaned = clean_norwegian_numeric_series(s)
        assert cleaned.iloc[0] == 1250450.75
        assert cleaned.iloc[1] == 25000.00
        assert cleaned.iloc[2] == 0.50
        assert cleaned.iloc[3] == -150.00
