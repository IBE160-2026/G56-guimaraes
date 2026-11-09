import os
import sys
import pandas as pd
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from compliance_engine import calculate_detailed_financial_metrics
from ledger_analytics import (
    build_ns4102_income_statement,
    calculate_ebit_driver_sensitivity,
    calculate_nace_driver_benchmarking,
    evaluate_profitability_indicators,
    extract_period_label,
    generate_profitability_recommendations,
    get_account_drilldown,
    get_voucher_details,
    summarize_cost_drivers,
)


class TestLedgerAnalytics:
    @pytest.fixture
    def sample_dfs(self):
        sample_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/sample"))
        sb = pd.read_csv(os.path.join(sample_dir, "saldobalanse_balansert.csv"))
        hb = pd.read_csv(os.path.join(sample_dir, "hovedbok_balansert.csv"))
        hb_err = pd.read_csv(os.path.join(sample_dir, "hovedbok_med_avvik.csv"))
        return sb, hb, hb_err

    def test_extract_period_label(self, sample_dfs):
        _, hb, _ = sample_dfs
        assert extract_period_label(hb) == "2026-01"
        assert extract_period_label(pd.DataFrame()) == "Inneværende periode"

    def test_account_drilldown_running_balance_matches_ub(self, sample_dfs):
        sb, hb, hb_err = sample_dfs

        # Balansert konto 1500: IB = 50 000 + 150 000 - 110 000 = 90 000 (stemmer med SB UB)
        drill_ok = get_account_drilldown(hb, sb, "1500")
        assert drill_ok["is_reconciled"] is True
        assert drill_ok["ib"] == 50000.0
        assert drill_ok["calculated_ub"] == 90000.0
        assert drill_ok["ub_sb"] == 90000.0
        assert drill_ok["transactions"].iloc[-1]["Lopende_Saldo"] == 90000.0

        # Avvikskonto 1500 i hovedbok_med_avvik.csv skal flagges deterministisk
        drill_err = get_account_drilldown(hb_err, sb, "1500")
        assert drill_err["is_reconciled"] is False
        assert abs(drill_err["discrepancy"]) == 30000.0

    def test_voucher_details_balances_per_voucher(self, sample_dfs):
        _, hb, _ = sample_dfs
        v1 = get_voucher_details(hb, "1")
        assert v1["is_balanced"] is True
        assert v1["debit_sum"] == 150000.0
        assert v1["credit_sum"] == 150000.0
        assert len(v1["lines"]) == 2
        assert set(v1["lines"]["Konto"].astype(str)) == {"1500", "3000"}

    def test_cost_drivers_and_deterministic_profitability_recommendations(self, sample_dfs):
        sb, hb, _ = sample_dfs
        metrics = calculate_detailed_financial_metrics(sb)
        drivers = summarize_cost_drivers(sb, hb)

        assert len(drivers) == 2
        assert drivers[0]["konto"] == "4000"
        assert drivers[0]["belop_nok"] == 60000.0
        assert drivers[0]["andel_av_driftskost_pct"] == 66.67

        recs = generate_profitability_recommendations(metrics, drivers)
        assert len(recs) >= 3
        rec_ids = {r["id"] for r in recs}
        # Kundefordringer er 90 000 av 200 000 (45 % > 20 % norm) -> frigjort 50 000 NOK
        assert "ARBEIDSKAPITAL_FORDRINGER" in rec_ids
        fordring_rec = next(r for r in recs if r["id"] == "ARBEIDSKAPITAL_FORDRINGER")
        assert fordring_rec["beregnet_effekt_nok"] == 50000.0

    def test_build_ns4102_income_statement_and_profitability_indicators(self, sample_dfs):
        sb, hb, _ = sample_dfs
        metrics = calculate_detailed_financial_metrics(sb)
        stmt = build_ns4102_income_statement(sb, hb, metrics)

        assert stmt["driftsmargin"] == 55.0
        rows = stmt["rows"]
        main_titles = [r["regnskapspost"] for r in rows if not r["regnskapspost"].startswith("•")]
        assert main_titles == [
            "1. Salgs- og driftsinntekter",
            "2. Varekostnad",
            "Bruttofortjeneste (Gross Profit)",
            "3. Lønnskostnader & personalkostnader",
            "4. Andre driftskostnader",
            "Sum driftskostnader",
            "Driftsresultat (EBIT)",
        ]

        ebit_row = next(r for r in rows if r["row_type"] == "result_ebit")
        assert ebit_row["belop_nok"] == 110000.0
        assert ebit_row["andel_pct"] == 55.0

        prof = evaluate_profitability_indicators(metrics)
        assert len(prof["cost_bars"]) == 4
        assert prof["kpis"]["bruttomargin"]["pct"] == 70.0
        assert prof["kpis"]["driftsmargin"]["pct"] == 55.0
        assert prof["kpis"]["lonn_omsetning"]["pct"] == 15.0
        assert prof["kpis"]["opex_omsetning"]["pct"] == 0.0
        assert prof["summary_level"] == "success"
        assert "øverste kvartil" in prof["summary_text"]

    def test_ebit_driver_sensitivity_and_nace_benchmarking(self, sample_dfs):
        sb, _, _ = sample_dfs
        metrics = calculate_detailed_financial_metrics(sb)
        sens = calculate_ebit_driver_sensitivity(metrics)

        # Inntekter = 200 000 -> 1 % prisøkning = 2 000 NOK
        # Varekostnad = 60 000 -> 1 % reduksjon = 600 NOK
        # Faste kostnader (Opex kl. 5-7) = 30 000 -> 1 % reduksjon = 300 NOK
        assert sens["price_1pct_nok"] == 2000.0
        assert sens["cogs_1pct_nok"] == 600.0
        assert sens["opex_1pct_nok"] == 300.0
        assert sens["price_vs_opex_mult"] == 6.7
        assert sens["price_vs_cogs_mult"] == 3.3
        assert "bruttomarginen på **70.0 %**" in sens["insight_text"]

        nace = calculate_nace_driver_benchmarking(revenue_nok=1_200_000.0)
        assert nace["largest_gap_cost_label"] == "varekostnad"
        assert nace["largest_gap_pp"] == 4.5
        assert nace["largest_gap_ebit_nok"] == 54000.0
        assert (
            nace["potential_banner_text"]
            == "🎯 Største forbedringspotensial: Din varekostnad er 4,5 prosentpoeng høyere enn bransjesnittet. Ved å lukke dette gapet vil EBIT øke med 54 000 NOK."
        )
