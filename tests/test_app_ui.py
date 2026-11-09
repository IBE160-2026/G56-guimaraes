import ast
import io
import os
import sys
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from compliance_engine import calculate_detailed_financial_metrics, map_to_ns4102, reconcile_hb_with_sb, validate_balance
from data_pipeline import process_csv_in_memory, validate_input
from database import DatabaseManager
from html_report import generate_management_html
from ledger_analytics import (
    extract_period_label,
    generate_profitability_recommendations,
    get_account_drilldown,
    get_voucher_details,
    summarize_cost_drivers,
)
from llm_integration import generate_management_report
from pdf_generator import generate_management_pdf
from views.ai_advisor_and_export import render_ai_advisor_and_export
from views.auditor_reconciliation import render_auditor_reconciliation
from views.financial_analysis import render_financial_analysis
from views.history_and_trends import render_history_and_trends
from views.industry_benchmarking import render_industry_benchmarking_mockup
from views.operational_analysis import render_operational_analysis
from views.upload_and_control import render_upload_and_control


class TestMultipageArchitectureAndEndToEnd:
    def test_multipage_views_and_orchestrator_compile_and_export_callables(self):
        """
        Verifiserer at alle 7 visningsmoduler i src/views/ og src/app.py
        har gyldig syntaks, bruker st.sidebar.radio uten unsafe_allow_html, og eksponerer forventede funksjoner.
        """
        assert callable(render_upload_and_control)
        assert callable(render_auditor_reconciliation)
        assert callable(render_financial_analysis)
        assert callable(render_operational_analysis)
        assert callable(render_industry_benchmarking_mockup)
        assert callable(render_ai_advisor_and_export)
        assert callable(render_history_and_trends)

        repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        for rel_path in [
            "app.py",
            "src/app.py",
            "src/database.py",
            "src/ledger_analytics.py",
            "src/views/upload_and_control.py",
            "src/views/auditor_reconciliation.py",
            "src/views/financial_analysis.py",
            "src/views/operational_analysis.py",
            "src/views/industry_benchmarking.py",
            "src/views/ai_advisor_and_export.py",
            "src/views/history_and_trends.py",
        ]:
            full_path = os.path.join(repo_root, rel_path)
            with open(full_path, "r", encoding="utf-8") as f:
                source = f.read()
            ast.parse(source, filename=rel_path)
            assert "unsafe_allow_html" not in source

        with open(os.path.join(repo_root, "src/app.py"), "r", encoding="utf-8") as f:
            app_src = f.read()
        assert "st.sidebar.radio" in app_src
        assert "🔎 2. Revisors avstemming" in app_src
        assert "⚙️ 4. Operasjonell analyse (v2.)" in app_src
        assert "🏢 5. Bransjesammenligning (v2.)" in app_src
        assert "💡 6. KI-Rådgiver & Eksport" in app_src
        assert "🗄️ 7. Historikk & Trendanalyse" in app_src

        with open(os.path.join(repo_root, "src/views/financial_analysis.py"), "r", encoding="utf-8") as f:
            fin_src = f.read()
        assert "📈 Resultatoppstilling etter NS 4102" in fin_src
        assert "Kostnadsstruktur (% av Driftsinntekter)" in fin_src
        assert "Lønnsomhetsindikatorer" in fin_src
        assert "st.progress" in fin_src
        assert "🔍 Analyse av EBIT-drivere" in fin_src
        assert "1 % økning i pris" in fin_src
        assert "1 % reduksjon i varekostnad" in fin_src
        assert "1 % reduksjon i faste kostnader (Opex)" in fin_src

        with open(os.path.join(repo_root, "src/views/industry_benchmarking.py"), "r", encoding="utf-8") as f:
            ind_src = f.read()
        assert "62.010 Programmeringstjenester" in ind_src
        assert "Driftsinntekter vs Bransjesnitt" in ind_src
        assert "Opex vs Bransjesnitt" in ind_src
        assert "EBIT-margin vs Bransjesnitt" in ind_src
        assert "📍 Simulert posisjon: Selskapet ligger i 3. kvartil (Topp 25 %) med en margin på 12 %, mot et bransjesnitt på 6 %." in ind_src
        assert "Bruttomargin vs. Bransje" in ind_src
        assert "Lønnskostnad/Omsetning vs. Bransje" in ind_src
        assert "Opex/Omsetning vs. Bransje" in ind_src
        assert "🚀 Strategiske tiltak for å øke bransjescore (Kommer i v2)" in ind_src
        assert "Generer bransjetiltak med KI" in ind_src

        with open(os.path.join(repo_root, "src/views/ai_advisor_and_export.py"), "r", encoding="utf-8") as f:
            exp_src = f.read()
        assert "st.checkbox" in exp_src
        assert "Generer Styrepakke (Strategisk)" in exp_src
        assert "Generer Beslutningsrapport (Operativ)" in exp_src
        assert 'report_type="styre"' in exp_src
        assert 'report_type="ledelse"' in exp_src

    def test_end_to_end_v2_pipeline_green_and_red_paths_with_sqlite_history(self, tmp_path):
        """
        Ende-til-ende integrasjonstest av hele v2.0-arbeidsflyten på tvers av moduler:
        1. Norsk semikolon-opplasting (Grønn sti) -> CFO KPI -> HB Drilldown -> SQLite #1 -> KI -> PDF/HTML
        2. Avviksdatasett (Rød sti) -> Kryssavstemmingsfeil -> SQLite #2 -> KI Revisjonsadvarsel
        3. Historikksammenligning på tvers av begge kjøringer i SQLite.
        """
        sample_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/sample"))
        db = DatabaseManager(db_path=tmp_path / "e2e_history.db")

        # --- Kjøring 1: Grønn sti (Norsk semikolon SB + balansert HB) ---
        with open(os.path.join(sample_dir, "saldobalanse_norsk_semikolon.csv"), "rb") as f:
            sb_green = process_csv_in_memory(io.BytesIO(f.read()), "saldobalanse_norsk_semikolon.csv")
        with open(os.path.join(sample_dir, "hovedbok_balansert.csv"), "rb") as f:
            hb_green = process_csv_in_memory(io.BytesIO(f.read()), "hovedbok_balansert.csv")

        validate_input(sb_green, "SB")
        validate_input(hb_green, "HB")
        assert validate_balance(sb_green) is True
        assert validate_balance(hb_green) is True

        sb_green["NS4102_Kategori"] = sb_green["Konto"].apply(map_to_ns4102)
        recon_green = reconcile_hb_with_sb(sb_green, hb_green)
        assert recon_green["is_reconciled"] is True

        metrics_green = calculate_detailed_financial_metrics(sb_green)
        drivers_green = summarize_cost_drivers(sb_green, hb_green)
        recs_green = generate_profitability_recommendations(metrics_green, drivers_green)
        period_green = extract_period_label(hb_green)

        run_id_1, created_1 = db.save_or_get_analysis_run(
            company_name="Bedrift AS",
            period_label=period_green,
            sb_filename="saldobalanse_norsk_semikolon.csv",
            hb_filename="hovedbok_balansert.csv",
            sb_df=sb_green,
            hb_df=hb_green,
            recon_result=recon_green,
            metrics=metrics_green,
            recommendations=recs_green,
        )
        assert created_1 is True

        report_green = generate_management_report(sb_green, recon_result=recon_green, mock_mode=True, hb_df=hb_green)
        db.save_ai_insight(run_id_1, report_green, is_mock=True)

        # Verifiser Hovedbok-drilldown og bilagsinspektør
        drill_1920 = get_account_drilldown(hb_green, sb_green, "1920")
        assert drill_1920["calculated_ub"] == 180000.0
        voucher_2 = get_voucher_details(hb_green, "2")
        assert voucher_2["is_balanced"] is True

        # Verifiser eksport
        pdf_1 = generate_management_pdf("Bedrift AS", report_green, metrics_green, recon_green, recs_green)
        html_1 = generate_management_html("Bedrift AS", report_green, metrics_green, recon_green, recs_green)
        assert pdf_1.getvalue().startswith(b"%PDF-")
        assert "<!DOCTYPE html>" in html_1.getvalue().decode("utf-8")

        # --- Kjøring 2: Rød sti (Med avvik i hovedbok) ---
        hb_red = pd.read_csv(os.path.join(sample_dir, "hovedbok_med_avvik.csv"))
        recon_red = reconcile_hb_with_sb(sb_green, hb_red)
        assert recon_red["is_reconciled"] is False

        run_id_2, created_2 = db.save_or_get_analysis_run(
            company_name="Bedrift AS",
            period_label="2026-01 (Avvikstest)",
            sb_filename="saldobalanse_norsk_semikolon.csv",
            hb_filename="hovedbok_med_avvik.csv",
            sb_df=sb_green,
            hb_df=hb_red,
            recon_result=recon_red,
            metrics=metrics_green,
            recommendations=recs_green,
        )
        assert created_2 is True
        assert run_id_2 != run_id_1

        # Verifiser at begge kjøringer ligger i historikktabellen
        history_df = db.list_analysis_runs()
        assert len(history_df) == 2
        assert int(history_df["has_ai_report"].sum()) == 1
