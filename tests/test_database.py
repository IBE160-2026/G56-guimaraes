import os
import sys
import pandas as pd
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from compliance_engine import calculate_detailed_financial_metrics, map_to_ns4102, reconcile_hb_with_sb
from database import DatabaseManager
from ledger_analytics import extract_period_label, generate_profitability_recommendations, summarize_cost_drivers
from llm_integration import generate_management_report


class TestDatabaseLayer:
    @pytest.fixture
    def sample_bundle(self):
        sample_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/sample"))
        sb = pd.read_csv(os.path.join(sample_dir, "saldobalanse_balansert.csv"))
        hb = pd.read_csv(os.path.join(sample_dir, "hovedbok_balansert.csv"))
        sb["NS4102_Kategori"] = sb["Konto"].apply(map_to_ns4102)
        recon = reconcile_hb_with_sb(sb, hb)
        metrics = calculate_detailed_financial_metrics(sb)
        drivers = summarize_cost_drivers(sb, hb)
        recs = generate_profitability_recommendations(metrics, drivers)
        period = extract_period_label(hb)
        return sb, hb, recon, metrics, recs, period

    def test_persistent_sqlite_file_and_sha256_deduplication(self, tmp_path, sample_bundle):
        """
        Tester at SQLite lagrer analysen persistent på fil (overlever omstart med ny instans),
        og at identisk datasett dedupliseres via SHA-256 hash.
        """
        db_file = tmp_path / "g56_test_history.db"
        sb, hb, recon, metrics, recs, period = sample_bundle

        db1 = DatabaseManager(db_path=db_file)
        run_id_1, created_1 = db1.save_or_get_analysis_run(
            company_name="Bedrift AS",
            period_label=period,
            sb_filename="saldobalanse_balansert.csv",
            hb_filename="hovedbok_balansert.csv",
            sb_df=sb,
            hb_df=hb,
            recon_result=recon,
            metrics=metrics,
            recommendations=recs,
        )
        assert created_1 is True
        assert run_id_1 == 1

        # Duplikatkall (f.eks. ved Streamlit rerun) skal IKKE opprette ny rad
        run_id_dup, created_dup = db1.save_or_get_analysis_run(
            company_name="Bedrift AS",
            period_label=period,
            sb_filename="saldobalanse_balansert.csv",
            hb_filename="hovedbok_balansert.csv",
            sb_df=sb,
            hb_df=hb,
            recon_result=recon,
            metrics=metrics,
            recommendations=recs,
        )
        assert created_dup is False
        assert run_id_dup == run_id_1

        # Simuler app-omstart med helt ny DatabaseManager mot samme fil
        db2 = DatabaseManager(db_path=db_file)
        runs_df = db2.list_analysis_runs()
        assert len(runs_df) == 1
        assert runs_df.iloc[0]["company_name"] == "Bedrift AS"
        assert runs_df.iloc[0]["period_label"] == "2026-01"
        assert runs_df.iloc[0]["ebit"] == 110000.0
        assert runs_df.iloc[0]["equity_ratio_pct"] == 81.48

    def test_ai_insight_upsert_and_run_details(self, tmp_path, sample_bundle):
        """Tester at KI-rapporten lagres og oppdateres på eksisterende run_id og kan hentes opp igjen."""
        db_file = tmp_path / "g56_ai_test.db"
        sb, hb, recon, metrics, recs, period = sample_bundle
        db = DatabaseManager(db_path=db_file)

        run_id, _ = db.save_or_get_analysis_run(
            company_name="Innsikt AS",
            period_label=period,
            sb_filename="sb.csv",
            hb_filename="hb.csv",
            sb_df=sb,
            hb_df=hb,
            recon_result=recon,
            metrics=metrics,
            recommendations=recs,
        )

        report = generate_management_report(sb, recon_result=recon, mock_mode=True, hb_df=hb)
        db.save_ai_insight(run_id, report, is_mock=True)

        details = db.get_run_details(run_id)
        assert details is not None
        assert details["metadata"]["company_name"] == "Innsikt AS"
        assert len(details["trial_balance"]) == 7
        assert len(details["ledger"]) == 14
        assert details["ai_insight"] is not None
        assert details["ai_insight"]["is_mock"] is True
        assert "110 000 NOK" in details["ai_insight"]["commentary"]["hovedkonklusjon"]

    def test_sql_window_function_running_balance_and_cascade_delete(self, tmp_path, sample_bundle):
        """
        Tester SQL-spørring av Hovedbok med SQLite Window Function (løpende saldo fra IB til UB)
        samt at ON DELETE CASCADE fjerner alle relaterte tabellrader ved sletting.
        """
        db_file = tmp_path / "g56_query_test.db"
        sb, hb, recon, metrics, recs, period = sample_bundle
        db = DatabaseManager(db_path=db_file)

        run_id, _ = db.save_or_get_analysis_run(
            company_name="Drilldown AS",
            period_label=period,
            sb_filename="sb.csv",
            hb_filename="hb.csv",
            sb_df=sb,
            hb_df=hb,
            recon_result=recon,
            metrics=metrics,
            recommendations=recs,
        )

        # Filtrer på konto 1920 Bankinnskudd (IB = 100 000, UB = 180 000)
        tx_1920 = db.query_ledger_transactions(run_id, account_no="1920")
        assert len(tx_1920) == 5
        assert tx_1920.iloc[-1]["Lopende_Saldo"] == 180000.0

        # Fritekstsøk på 'Faktura 101'
        tx_search = db.query_ledger_transactions(run_id, search_text="Faktura 101")
        assert len(tx_search) >= 2

        # Slett kjøring og bekreft kaskadesletting
        deleted = db.delete_analysis_run(run_id)
        assert deleted is True
        assert db.get_run_details(run_id) is None
        assert db.list_analysis_runs().empty
