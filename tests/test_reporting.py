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
        """Tester at mock-modus returnerer en rik, validert CFO-analyse uten API-nøkkel."""
        recon_mock = {"is_reconciled": True, "discrepancy_count": 0}
        report = generate_management_report(sample_mapped_df, recon_result=recon_mock, api_key=None, mock_mode=True)
        
        assert isinstance(report, ManagementCommentary)
        assert len(report.hovedkonklusjon) > 20
        assert len(report.lonnsomhet_og_marginer) > 50
        assert len(report.likviditet_og_arbeidskapital) > 50
        assert len(report.revisors_avstemmingsnotat) > 50
        assert len(report.potensielle_avvik) >= 2
        assert len(report.tiltaksliste) >= 2
        
        # Sjekk at tiltakene har prioriteter og begrunnelser
        for item in report.tiltaksliste:
            assert item.prioritet in ["Høy", "Medium", "Lav"]
            assert len(item.tiltak) > 5
            assert len(item.begrunnelse) > 5
            assert len(item.forventet_effekt) > 5

    def test_mock_mode_with_discrepancies(self, sample_mapped_df):
        """Tester at mock-modus flagger revisjonsavvik dersom regnskapet ikke stemmer."""
        recon_err = {"is_reconciled": False, "discrepancy_count": 2}
        report = generate_management_report(sample_mapped_df, recon_result=recon_err, api_key=None, mock_mode=True)
        
        assert "ADVARSEL" in report.hovedkonklusjon.upper()
        assert "feil" in report.revisors_avstemmingsnotat.lower()

    def test_pdf_generation_produces_valid_pdf_buffer(self, sample_mapped_df):
        """Tester at PDF-motoren bygger et gyldig PDF-dokument in-memory med ny layout."""
        recon_mock = {"is_reconciled": True, "discrepancy_count": 0}
        report = generate_management_report(sample_mapped_df, recon_result=recon_mock, mock_mode=True)
        pdf_buffer = generate_management_pdf(company_name="Testbedrift AS", ai_report=report)
        
        assert isinstance(pdf_buffer, io.BytesIO)
        pdf_bytes = pdf_buffer.getvalue()
        
        # Sjekk at PDF-en ikke er tom og har gyldige magic bytes
        assert len(pdf_bytes) > 1000
        assert pdf_bytes.startswith(b"%PDF-")
