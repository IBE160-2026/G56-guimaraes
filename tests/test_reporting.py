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
        """Tester at PDF-motoren bygger et gyldig PDF-dokument in-memory med nøkkeltall og avvikstabell."""
        recon_mock = {"is_reconciled": True, "discrepancy_count": 0}
        metrics = calculate_detailed_financial_metrics(sample_mapped_df)
        report = generate_management_report(sample_mapped_df, recon_result=recon_mock, mock_mode=True)
        pdf_buffer = generate_management_pdf(
            company_name="Testbedrift AS",
            ai_report=report,
            ns4102_summary=metrics,
            recon_result=recon_mock
        )
        
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

    def test_live_api_flow_with_mocked_openai_client(self, sample_mapped_df):
        """
        Tester live OpenAI-stien (mock_mode=False) med mocket OpenAI-klient
        slik at execute_openai_with_retry og post_validate_ai_response verifiseres ende-til-ende.
        """
        from unittest.mock import MagicMock, patch

        recon_mock = {"is_reconciled": True, "discrepancy_count": 0}
        expected_report = generate_management_report(sample_mapped_df, recon_result=recon_mock, mock_mode=True)

        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock()]
        mock_completion.choices[0].message.parsed = expected_report

        with patch("llm_integration.OpenAI") as mock_openai_cls:
            mock_client = MagicMock()
            mock_client.beta.chat.completions.parse.return_value = mock_completion
            mock_openai_cls.return_value = mock_client

            live_report = generate_management_report(
                sample_mapped_df,
                recon_result=recon_mock,
                api_key="sk-test-valid-key",
                mock_mode=False
            )

            assert isinstance(live_report, ManagementCommentary)
            assert live_report.hovedkonklusjon == expected_report.hovedkonklusjon
            mock_client.beta.chat.completions.parse.assert_called_once()

    def test_post_validate_ai_response_catches_contradictions(self, sample_mapped_df):
        """
        Tester at post_validate_ai_response reiser ValueError dersom KI-rapporten
        påstår alvorlige avvik ved godkjent avstemming, eller unnlater å varsle ved avvik.
        """
        from llm_integration import post_validate_ai_response

        good_report = generate_management_report(
            sample_mapped_df,
            recon_result={"is_reconciled": True, "discrepancy_count": 0},
            mock_mode=True
        )

        # 1. KI hevder "alvorlige avvik" til tross for godkjent status -> ValueError
        contradicting_approved = good_report.model_copy(
            update={"hovedkonklusjon": "Det er oppdaget alvorlige avvik i regnskapet."}
        )
        ctx_approved = {"avstemming_hovedbok_mot_saldobalanse": {"status": "GODKJENT (100% konsistent)"}}
        with pytest.raises(ValueError, match="Kvalitetssikringsfeil"):
            post_validate_ai_response(contradicting_approved, ctx_approved)

        # 2. KI unnlater å nevne avvik/feil til tross for "AVVIK OPPDAGET" -> ValueError
        contradicting_warning = good_report.model_copy(
            update={
                "hovedkonklusjon": "Alt ser strålende ut i perioden.",
                "revisors_avstemmingsnotat": "Alt stemmer helt fint."
            }
        )
        ctx_discrepancy = {"avstemming_hovedbok_mot_saldobalanse": {"status": "AVVIK OPPDAGET"}}
        with pytest.raises(ValueError, match="Kvalitetssikringsfeil"):
            post_validate_ai_response(contradicting_warning, ctx_discrepancy)

    def test_pdf_and_html_include_extended_cfo_metrics_and_recommendations(self):
        """
        Tester at både PDF- og HTML-styrepakken inkluderer de nye CFO-nøkkeltallene
        (Soliditet, LG2, TKR, EKR) og de deterministiske lønnsomhetsrådene med XSS-sikring.
        """
        from ledger_analytics import summarize_cost_drivers, generate_profitability_recommendations

        sample_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../data/sample'))
        sb = pd.read_csv(os.path.join(sample_dir, 'saldobalanse_balansert.csv'))
        hb = pd.read_csv(os.path.join(sample_dir, 'hovedbok_balansert.csv'))
        sb['NS4102_Kategori'] = sb['Konto'].apply(map_to_ns4102)

        recon_res = reconcile_hb_with_sb(sb, hb)
        metrics = calculate_detailed_financial_metrics(sb)
        drivers = summarize_cost_drivers(sb, hb)
        recs = generate_profitability_recommendations(metrics, drivers)
        report = generate_management_report(sb, recon_result=recon_res, mock_mode=True, hb_df=hb)

        pdf_buf = generate_management_pdf(
            company_name="CFO Test AS",
            ai_report=report,
            ns4102_summary=metrics,
            recon_result=recon_res,
            recommendations=recs,
        )
        assert pdf_buf.getvalue().startswith(b"%PDF-")
        assert len(pdf_buf.getvalue()) > 1500

        html_buf = generate_management_html(
            company_name="CFO Test AS",
            ai_report=report,
            metrics=metrics,
            recon_result=recon_res,
            recommendations=recs,
        )
        html_str = html_buf.getvalue().decode("utf-8")
        assert "81,5 %" in html_str  # Egenkapitalandel (81.48 avrundet til 1 desimal)
        assert "52,4 %" in html_str  # TKR (52.38 avrundet til 1 desimal)
        assert "66,7 %" in html_str  # EKR (66.67 avrundet til 1 desimal)
        assert "Deterministisk Lønnsomhetspotensial" in html_str
        assert "50 000 NOK" in html_str

    def test_html_report_profiles_styre_vs_ledelse_conditional_rendering(self):
        """
        Tester at generate_management_html skiller tydelig mellom report_type='styre' (Styrepakke)
        og report_type='ledelse' (Beslutningsrapport) med riktig innholdsprofil, Pydantic-domeneobjekter,
        null eksterne avhengigheter, full The AI Firewall-beskyttelse og støtte for @media print.
        """
        from compliance_engine import evaluate_ns4102_compliance, evaluate_vat_compliance
        from html_report import (
            EbitDriverSensitivityModel,
            NaceBenchmarkingModel,
            OperationalCrossCheckModel,
            RfqBiddingModel,
        )
        from ledger_analytics import (
            build_ns4102_income_statement,
            calculate_ebit_driver_sensitivity,
            evaluate_profitability_indicators,
            generate_profitability_recommendations,
            summarize_cost_drivers,
        )

        sample_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/sample"))
        sb = pd.read_csv(os.path.join(sample_dir, "saldobalanse_balansert.csv"))
        hb = pd.read_csv(os.path.join(sample_dir, "hovedbok_balansert.csv"))
        sb["NS4102_Kategori"] = sb["Konto"].apply(map_to_ns4102)

        recon_res = reconcile_hb_with_sb(sb, hb)
        vat_res = evaluate_vat_compliance(sb, hb)
        ns_res = evaluate_ns4102_compliance(sb, hb)
        metrics = calculate_detailed_financial_metrics(sb)
        income_stmt = build_ns4102_income_statement(sb, hb, metrics)
        prof_ind = evaluate_profitability_indicators(metrics)
        sens_dict = calculate_ebit_driver_sensitivity(metrics)
        sens_model = EbitDriverSensitivityModel(**sens_dict)
        nace_model = NaceBenchmarkingModel()
        rfq_model = RfqBiddingModel()
        op_check_model = OperationalCrossCheckModel()
        drivers = summarize_cost_drivers(sb, hb)
        recs = generate_profitability_recommendations(metrics, drivers)
        report = generate_management_report(sb, recon_result=recon_res, mock_mode=True, hb_df=hb)

        # 1. Generer Styrepakke (Strategisk)
        styre_buf = generate_management_html(
            company_name="ProfilTest AS",
            ai_report=report,
            metrics=metrics,
            recon_result=recon_res,
            recommendations=recs,
            report_type="styre",
            sb_df=sb,
            vat_compliance=vat_res,
            ns4102_compliance=ns_res,
            income_statement=income_stmt,
            cost_drivers=drivers,
            profitability_indicators=prof_ind,
            ebit_sensitivity=sens_model,
            nace_benchmark=nace_model,
            rfq_report=rfq_model,
            operational_check=op_check_model,
            period_label="2026-01",
        )
        styre_html = styre_buf.getvalue().decode("utf-8")

        assert 'data-report-type="styre"' in styre_html
        assert "theme-styre" in styre_html
        assert "print-page-break" in styre_html
        assert 'id="styre-executive-summary"' in styre_html
        assert 'id="styre-hovedtall"' in styre_html
        assert 'id="styre-compliance"' in styre_html
        assert 'id="styre-bransje-v2"' in styre_html
        assert 'id="styre-strategiske-rad"' in styre_html
        assert "Utbyttekapasitet" in styre_html
        assert "Strategisk Posisjonering" in styre_html
        assert "<svg" in styre_html  # Innebygd normalfordelingskurve (Bell Curve)
        assert "54 000 NOK" in styre_html  # NACE gap-potensial
        assert "Makrotrender" in styre_html
        assert 'id="ledelse-resultatoppstilling"' not in styre_html
        assert 'id="ledelse-anbud-rfq"' not in styre_html
        assert 'id="ledelse-operasjonell-v2"' not in styre_html
        assert "@media print" in styre_html

        # 2. Generer Beslutningsrapport (Operativ)
        ledelse_buf = generate_management_html(
            company_name="ProfilTest AS",
            ai_report=report,
            metrics=metrics,
            recon_result=recon_res,
            recommendations=recs,
            report_type="ledelse",
            sb_df=sb,
            vat_compliance=vat_res,
            ns4102_compliance=ns_res,
            income_statement=income_stmt,
            cost_drivers=drivers,
            profitability_indicators=prof_ind,
            ebit_sensitivity=sens_model,
            nace_benchmark=nace_model,
            rfq_report=rfq_model,
            operational_check=op_check_model,
            period_label="2026-01",
        )
        ledelse_html = ledelse_buf.getvalue().decode("utf-8")

        assert 'data-report-type="ledelse"' in ledelse_html
        assert "theme-ledelse" in ledelse_html
        assert 'id="ledelse-operativ-oppsummering"' in ledelse_html
        assert 'id="ledelse-resultatoppstilling"' in ledelse_html
        assert 'id="ledelse-kostnadsdrivere"' in ledelse_html
        assert 'id="ledelse-anbud-rfq"' in ledelse_html
        assert 'id="ledelse-mva-og-avvik"' in ledelse_html
        assert 'id="ledelse-operasjonell-v2"' in ledelse_html
        assert 'id="ledelse-operative-rad"' in ledelse_html
        assert "Effekt av 1 % kutt i varekostnad" in ledelse_html
        assert "+2 000 NOK" in ledelse_html  # 1 % prisøkning
        assert "+600 NOK" in ledelse_html  # 1 % kutt i varekostnad
        assert "+300 NOK" in ledelse_html  # 1 % kutt i Opex
        assert "45 000 NOK/år" in ledelse_html  # Bankrente RFQ
        assert "24 000 NOK/år" in ledelse_html  # Forsikring RFQ
        assert "12 000 NOK/år" in ledelse_html  # Strøm RFQ
        assert "81 000 NOK/år" in ledelse_html  # Totalt RFQ sparepotensial
        assert "Varelager vs. Konto 1460" in ledelse_html
        assert "Timelister vs. Lønnskostnad" in ledelse_html
        assert "Reforhandling av Avtaler" in ledelse_html
        assert "Reduksjon av Reskontrotid" in ledelse_html
        assert "Fjerning av Inaktive Lisenser" in ledelse_html
        assert 'id="styre-executive-summary"' not in ledelse_html
        assert 'id="styre-bransje-v2"' not in ledelse_html

        # 3. Sjekk at heller ikke Beslutningsrapporten lekker rå HB-transaksjonstekster
        for raw_hb_text in ["Faktura 101", "Innbetaling kunde", "Varekjøp", "Lønnsutbetaling", "Bilagsnr"]:
            assert raw_hb_text not in ledelse_html

        # 4. Ugyldig report_type skal reise ValueError
        with pytest.raises(ValueError, match="Ugyldig report_type"):
            generate_management_html("ProfilTest AS", report, metrics, recon_res, recs, report_type="ukjent")



