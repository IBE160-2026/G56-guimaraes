import pytest
import pandas as pd
import sys
import os
import io

# Legger src-mappen til i system path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from llm_integration import generate_management_report, ManagementCommentary
from pdf_generator import generate_management_pdf

class TestReportingAndExport:
    
    @pytest.fixture
    def sample_mapped_df(self):
        """Oppretter en test-DataFrame med NS4102-kategorier."""
        return pd.DataFrame({
            'Konto': ['1920', '3000', '4000', '5000'],
            'Kontonavn': ['Bank', 'Salg', 'Varekostnad', 'Lønn'],
            'Debet': [200000.0, 0.0, 60000.0, 30000.0],
            'Kredit': [120000.0, 200000.0, 0.0, 0.0],
            'NS4102_Kategori': [
                'Eiendeler (NS 4102)',
                'Salgs- og Driftsinntekt (NS 4102)',
                'Driftskostnader (NS 4102)',
                'Driftskostnader (NS 4102)'
            ]
        })

    def test_mock_mode_generates_valid_commentary(self, sample_mapped_df):
        """Tester at mock-modus (frakoblet sensormodus) returnerer et validert Pydantic-objekt uten API-nøkkel."""
        report = generate_management_report(sample_mapped_df, api_key=None, mock_mode=True)
        
        assert isinstance(report, ManagementCommentary)
        assert len(report.okonomisk_sammendrag) > 50
        assert len(report.potensielle_avvik) >= 2
        assert len(report.tiltaksliste) >= 2
        
        # Sjekk at tiltakene har prioriteter
        for item in report.tiltaksliste:
            assert item.prioritet in ["Høy", "Medium", "Lav"]
            assert len(item.tiltak) > 5

    def test_pdf_generation_produces_valid_pdf_buffer(self, sample_mapped_df):
        """Tester at PDF-motoren bygger et gyldig PDF-dokument in-memory."""
        report = generate_management_report(sample_mapped_df, mock_mode=True)
        pdf_buffer = generate_management_pdf(company_name="Testbedrift AS", ai_report=report)
        
        assert isinstance(pdf_buffer, io.BytesIO)
        pdf_bytes = pdf_buffer.getvalue()
        
        # Sjekk at PDF-en ikke er tom
        assert len(pdf_bytes) > 1000
        # Sjekk standard PDF magic bytes
        assert pdf_bytes.startswith(b"%PDF-")
