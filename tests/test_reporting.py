import pytest
import pandas as pd
import sys
import os
import io

# Legger src-mappen til i system path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from llm_integration import generate_management_report, ManagementCommentary
from pdf_generator import generate_management_pdf
from html_report import generate_management_html
from compliance_engine import calculate_detailed_financial_metrics, reconcile_hb_with_sb, map_to_ns4102

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

    def test_ai_firewall_context_never_contains_raw_transactions(self, sample_mapped_df):
        """Tester The AI Firewall: Sjekker at payloaden kun inneholder aggregerte tall, aldri råtransaksjoner."""
        from llm_integration import build_financial_context
        recon_mock = {"is_reconciled": True, "discrepancy_count": 0}
        ctx = build_financial_context(sample_mapped_df, recon_mock)
        
        assert "raw_transactions" not in ctx
        assert "nokkeltall" in ctx
        assert "Driftsresultat_EBIT_NOK" in ctx["nokkeltall"]
        # EBIT må være deterministisk utregnet (200000 - 90000 = 110000)
        assert ctx["nokkeltall"]["Driftsresultat_EBIT_NOK"] == 110000.0

    def test_pydantic_schema_consistency_between_mock_and_class(self, sample_mapped_df):
        """Tester at mock-KI produserer 100 % samsvarende Pydantic-skjema som forventet av API."""
        recon_mock = {"is_reconciled": True, "discrepancy_count": 0}
        report = generate_management_report(sample_mapped_df, recon_result=recon_mock, mock_mode=True)
        dumped = report.model_dump()
        
        required_keys = {
            "hovedkonklusjon", "lonnsomhet_og_marginer", "likviditet_og_arbeidskapital",
            "revisors_avstemmingsnotat", "potensielle_avvik", "tiltaksliste"
        }
        assert required_keys.issubset(dumped.keys())

    def test_html_generation_produces_valid_self_contained_html(self):
        """
        Tester FR-5.1, FR-5.2, FR-5.4 og FR-5.6:
        Åpner HTML-bufferen og verifiserer gyldig, selvstendig HTML5 uten eksterne avhengigheter,
        med EBIT (110 000 NOK) og driftsmargin (55,0 %) fra fasit, samt XSS-escaping og norske spesialtegn.
        """
        sample_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../data/sample'))
        sb = pd.read_csv(os.path.join(sample_dir, 'saldobalanse_balansert.csv'))
        hb = pd.read_csv(os.path.join(sample_dir, 'hovedbok_balansert.csv'))
        sb['NS4102_Kategori'] = sb['Konto'].apply(map_to_ns4102)

        recon_res = reconcile_hb_with_sb(sb, hb)
        metrics = calculate_detailed_financial_metrics(sb)
        report = generate_management_report(sb, recon_result=recon_res, mock_mode=True)

        html_buffer = generate_management_html(
            company_name="Bedrift ÆØÅ <script>alert(1)</script> AS",
            ai_report=report,
            metrics=metrics,
            recon_result=recon_res
        )

        assert isinstance(html_buffer, io.BytesIO)
        html_text = html_buffer.getvalue().decode("utf-8")

        # 1. Gyldig og selvstendig HTML5 uten eksterne ressurser
        assert html_text.startswith("<!DOCTYPE html>")
        assert '<html lang="nb">' in html_text
        assert "<style>" in html_text
        assert "</html>" in html_text
        assert "<script src=" not in html_text
        assert '<link rel="stylesheet"' not in html_text

        # 2. XSS-sikring (FR-5.6) og norske tegn
        assert "<script>alert(1)</script>" not in html_text
        assert "&lt;script&gt;alert(1)&lt;/script&gt;" in html_text
        assert "Bedrift ÆØÅ" in html_text

        # 3. Fasittall for EBIT (110 000 NOK) og driftsmargin (55,0 %) (FR-5.2)
        assert "110 000 NOK" in html_text
        assert "55,0 %" in html_text

        # 4. Grønn status og tomtilstand ved 0 avvik (FR-5.3 / FR-5.4)
        assert "status-approved" in html_text
        assert "Ingen avstemmingsavvik oppdaget mellom Hovedbok og Saldobalanse (0 avvik)." in html_text

    def test_html_generation_includes_discrepancies_and_excludes_raw_transactions(self):
        """
        Tester FR-5.2 og FR-5.3:
        Verifiserer at HTML-rapporten inneholder avvikskontoene (1500 og 1920) når testdata har avvik,
        og at ingen rå transaksjonslinjer fra hovedboken lekker inn i HTML-en.
        """
        sample_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../data/sample'))
        sb = pd.read_csv(os.path.join(sample_dir, 'saldobalanse_balansert.csv'))
        hb_err = pd.read_csv(os.path.join(sample_dir, 'hovedbok_med_avvik.csv'))
        sb['NS4102_Kategori'] = sb['Konto'].apply(map_to_ns4102)

        recon_err = reconcile_hb_with_sb(sb, hb_err)
        metrics = calculate_detailed_financial_metrics(sb)
        report = generate_management_report(sb, recon_result=recon_err, mock_mode=True)

        html_buffer = generate_management_html(
            company_name="Testbedrift AS",
            ai_report=report,
            metrics=metrics,
            recon_result=recon_err
        )

        html_text = html_buffer.getvalue().decode("utf-8")

        # 1. Rød varselstatus og spesifikke avvikskontoer (1500 og 1920 med 30 000,00 NOK)
        assert "status-warning" in html_text
        assert "1500" in html_text
        assert "1920" in html_text
        assert "30 000,00 NOK" in html_text

        # 2. Ingen rå transaksjonslinjer fra hovedboken (f.eks. tekst fra enkeltbilag i hovedbok_med_avvik.csv)
        for raw_hb_text in ["Faktura 101", "Innbetaling kunde", "Varekjøp", "Lønnsutbetaling"]:
            assert raw_hb_text not in html_text
        assert "Bilagsnr" not in html_text

