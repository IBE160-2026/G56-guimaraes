import pytest
import pandas as pd
import sys
import os

# Legger src-mappen til i system path for å kunne importere modulene
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from compliance_engine import validate_balance, map_to_ns4102, reconcile_hb_with_sb

class TestComplianceEngine:
    
    def test_validate_balance_success(self):
        """Tester at en fil i balanse godkjennes."""
        data = {
            'Konto': ['3000', '1920', '4000', '2050'],
            'Debet': [0.0, 15000.50, 5000.0, 0.0],
            'Kredit': [15000.50, 0.0, 0.0, 5000.0]
        }
        df = pd.DataFrame(data)
        assert validate_balance(df, 'Debet', 'Kredit') is True

    def test_validate_balance_failure(self):
        """Tester at AI-revisoren avviser ubalanse."""
        data = {
            'Konto': ['3000', '1920'],
            'Debet': [0.0, 15000.0],
            'Kredit': [14999.0, 0.0]  # Ubalanse med 1 krone
        }
        df = pd.DataFrame(data)
        with pytest.raises(ValueError, match="BALANSEFEIL"):
            validate_balance(df, 'Debet', 'Kredit')

    def test_validate_sample_files(self):
        """Tester de faktiske sample-filene i data/sample/."""
        sample_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../data/sample'))
        
        # 1. Balansert saldobalanse
        sb_bal = pd.read_csv(os.path.join(sample_dir, 'saldobalanse_balansert.csv'))
        assert validate_balance(sb_bal, 'Debet', 'Kredit') is True
        
        # 2. Balansert hovedbok
        hb_bal = pd.read_csv(os.path.join(sample_dir, 'hovedbok_balansert.csv'))
        assert validate_balance(hb_bal, 'Debet', 'Kredit') is True
        
        # 3. Ubalansert saldobalanse (skal feile med 10 000 diff)
        sb_ubal = pd.read_csv(os.path.join(sample_dir, 'saldobalanse_med_ubalanse.csv'))
        with pytest.raises(ValueError, match="Differanse: 10000.00"):
            validate_balance(sb_ubal, 'Debet', 'Kredit')

    def test_reconciliation_happy_path(self):
        """Tester at kryssavstemming mellom balansert SB og HB gir 0 avvik."""
        sample_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../data/sample'))
        sb = pd.read_csv(os.path.join(sample_dir, 'saldobalanse_balansert.csv'))
        hb = pd.read_csv(os.path.join(sample_dir, 'hovedbok_balansert.csv'))
        
        result = reconcile_hb_with_sb(sb, hb)
        assert result["is_reconciled"] is True
        assert result["discrepancy_count"] == 0

    def test_reconciliation_detects_discrepancy(self):
        """Tester at kryssavstemming fanger opp avvik på konto 1500 og 1920."""
        sample_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../data/sample'))
        sb = pd.read_csv(os.path.join(sample_dir, 'saldobalanse_balansert.csv'))
        hb_err = pd.read_csv(os.path.join(sample_dir, 'hovedbok_med_avvik.csv'))
        
        result = reconcile_hb_with_sb(sb, hb_err)
        assert result["is_reconciled"] is False
        assert result["discrepancy_count"] == 2
        
        discrepancies = result["discrepancies"].set_index('Konto')
        assert '1500' in discrepancies.index
        assert '1920' in discrepancies.index
        # Avvik på konto 1500 er -30000 (UB er 90000, men beregnet er 60000 -> avvik 30000)
        assert abs(discrepancies.loc['1500', 'Avvik']) == 30000.0
        assert abs(discrepancies.loc['1920', 'Avvik']) == 30000.0

    def test_ns4102_mapping(self):
        """Tester at kontonummer blir klassifisert riktig i norsk standard."""
        assert map_to_ns4102('1920') == "Eiendeler (NS 4102)"
        assert map_to_ns4102('2400') == "Egenkapital og Gjeld (NS 4102)"
        assert map_to_ns4102('3000') == "Salgs- og Driftsinntekt (NS 4102)"
        assert map_to_ns4102('4000') == "Driftskostnader (NS 4102)"
        assert map_to_ns4102('5000') == "Driftskostnader (NS 4102)"
        assert map_to_ns4102('8000') == "Finans og Skatt (NS 4102)"
        assert map_to_ns4102('9999') == "Ukjent / Udefinert"

    def test_reconciliation_account_only_in_hb_detected(self):
        """Edge case: En konto finnes bare i Hovedboken (ikke oppført i Saldobalansen)."""
        sb = pd.DataFrame({
            'Konto': ['3000'],
            'Kontonavn': ['Salgsinntekter'],
            'IB': [0.0],
            'UB': [100000.0]
        })
        hb = pd.DataFrame({
            'Konto': ['3000', '9999'],
            'Debet': [0.0, 5000.0],
            'Kredit': [100000.0, 0.0]
        })
        result = reconcile_hb_with_sb(sb, hb)
        assert result["is_reconciled"] is False
        assert result["discrepancy_count"] >= 1
        assert '9999' in result["discrepancies"]['Konto'].values

    def test_reconciliation_account_only_in_sb_with_zero_movement(self):
        """Edge case: En konto finnes i Saldobalansen med uendret saldo (IB == UB), ingen poster i HB."""
        sb = pd.DataFrame({
            'Konto': ['1000'],
            'Kontonavn': ['Forskning og utvikling'],
            'IB': [50000.0],
            'UB': [50000.0]
        })
        hb = pd.DataFrame({
            'Konto': ['3000'],
            'Debet': [0.0],
            'Kredit': [0.0]
        })
        result = reconcile_hb_with_sb(sb, hb)
        # Konto 1000 skal stemme fordi IB(50000) + Netto(0) == UB(50000)
        table = result["reconciliation_table"].set_index('Konto')
        assert bool(table.loc['1000', 'Stemmer']) is True

    def test_calculate_detailed_financial_metrics(self):
        """Tester at den deterministiske nøkkeltallsmotoren regner ut bruttofortjeneste, EBIT og arbeidskapital nøyaktig."""
        from compliance_engine import calculate_detailed_financial_metrics
        sb_df = pd.DataFrame({
            'Konto': ['3000', '4000', '5000', '6000', '1920', '1500', '2400'],
            'Debet': [0.0, 50000.0, 30000.0, 10000.0, 0.0, 0.0, 0.0],
            'Kredit': [200000.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            'UB': [0.0, 0.0, 0.0, 0.0, 100000.0, 40000.0, 30000.0]
        })
        m = calculate_detailed_financial_metrics(sb_df)
        assert m["driftsinntekter"] == 200000.0
        assert m["varekostnad"] == 50000.0
        assert m["bruttofortjeneste"] == 150000.0
        assert m["bruttomargin"] == 75.0
        assert m["samlede_driftskostnader"] == 90000.0
        assert m["ebit"] == 110000.0
        assert m["driftsmargin"] == 55.0
        assert m["arbeidskapital"] == 110000.0  # (100k bank + 40k fordring) - 30k gjeld = 110k

    def test_cfo_metrics_and_sign_normalization_on_sample_data(self):
        """
        Tester at kreditsaldoer med negativt fortegn (slik norske ERP-systemer eksporterer klasse 2)
        håndteres korrekt med abs(), og verifiserer Likviditetsgrad 1/2, Soliditet (inkl. mellombalanse-EK),
        Gjeldsgrad, Totalkapitalrentabilitet (TKR) og Egenkapitalrentabilitet (EKR).
        """
        from compliance_engine import calculate_detailed_financial_metrics
        sample_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../data/sample'))
        sb = pd.read_csv(os.path.join(sample_dir, 'saldobalanse_balansert.csv'))

        m = calculate_detailed_financial_metrics(sb)
        # Likviditet: Omløpsmidler (180k + 90k = 270k), Kortsiktig gjeld (|-50k| = 50k)
        assert m["arbeidskapital"] == 220000.0
        assert m["likviditetsgrad_1"] == 5.4
        assert m["likviditetsgrad_2"] == 5.4

        # Soliditet ved mellombalanse: Bokført EK (110k) + Udisponert resultat (110k) = 220k av 270k TK
        assert m["bokfort_egenkapital_ub"] == 110000.0
        assert m["reell_egenkapital_ub"] == 220000.0
        assert m["egenkapitalandel"] == 81.48
        assert m["gjeldsgrad"] == 0.23

        # Rentabilitet (snitt TK = (150k + 270k)/2 = 210k; snitt EK = (110k + 220k)/2 = 165k)
        assert m["totalkapitalrentabilitet"] == 52.38
        assert m["egenkapitalrentabilitet"] == 66.67

    def test_zero_division_safety_in_cfo_metrics(self):
        """Tester at alle brøkbaserte CFO-nøkkeltall returnerer 0.0 uten ZeroDivisionError ved tomme saldoer."""
        from compliance_engine import calculate_detailed_financial_metrics
        zero_df = pd.DataFrame({
            'Konto': ['1920', '2400', '3000'],
            'IB': [0.0, 0.0, 0.0],
            'Debet': [0.0, 0.0, 0.0],
            'Kredit': [0.0, 0.0, 0.0],
            'UB': [0.0, 0.0, 0.0],
        })
        m = calculate_detailed_financial_metrics(zero_df)
        assert m["likviditetsgrad_1"] == 0.0
        assert m["likviditetsgrad_2"] == 0.0
        assert m["egenkapitalandel"] == 0.0
        assert m["totalkapitalrentabilitet"] == 0.0
        assert m["egenkapitalrentabilitet"] == 0.0

    def test_evaluate_vat_compliance_detects_missing_vat_and_approves_consistent_vat(self):
        """
        Tester at evaluate_vat_compliance flagger omsetning på 3000-serien uten MVA-kontoer i 2700-serien,
        og godkjenner et regnskap med konsistent 25 % utgående MVA og inngående MVA.
        """
        from compliance_engine import evaluate_vat_compliance

        sample_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/sample"))
        sb = pd.read_csv(os.path.join(sample_dir, "saldobalanse_balansert.csv"))
        hb = pd.read_csv(os.path.join(sample_dir, "hovedbok_balansert.csv"))

        # Eksempeldata har 200 000 på 3000 Salgsinntekter og 0 på 2700-serien -> skal gi warning
        vat_warn = evaluate_vat_compliance(sb, hb)
        assert vat_warn["status"] == "warning"
        assert vat_warn["taxable_sales_3000"] == 200000.0
        assert len(vat_warn["findings"]) >= 1

        # Konstruer et MVA-komplett regnskap (100 000 salg + 25 000 utg. MVA 2700, 40 000 kjøp + 10 000 inng. MVA 2710)
        sb_vat_ok = pd.DataFrame({
            "Konto": ["1500", "2400", "2700", "2710", "3000", "4000"],
            "Kontonavn": [
                "Kundefordringer",
                "Leverandørgjeld",
                "Utgående merverdiavgift høy sats",
                "Inngående merverdiavgift høy sats",
                "Salgsinntekter avgiftspliktig",
                "Varekostnad",
            ],
            "Debet": [125000.0, 0.0, 0.0, 10000.0, 0.0, 40000.0],
            "Kredit": [0.0, 50000.0, 25000.0, 0.0, 100000.0, 0.0],
            "UB": [125000.0, -50000.0, -25000.0, 10000.0, -100000.0, 40000.0],
        })
        hb_vat_ok = pd.DataFrame({
            "Bilagsnr": ["1", "1", "1"],
            "Konto": ["1500", "3000", "2700"],
            "Debet": [125000.0, 0.0, 0.0],
            "Kredit": [0.0, 100000.0, 25000.0],
        })
        vat_ok = evaluate_vat_compliance(sb_vat_ok, hb_vat_ok)
        assert vat_ok["status"] == "ok"
        assert vat_ok["effective_out_vat_pct"] == 25.0
        assert len(vat_ok["findings"]) == 0

    def test_evaluate_ns4102_compliance_recognition_rate(self):
        """
        Tester at evaluate_ns4102_compliance gir 100 % gjenkjennelsesgrad på gyldig norsk kontoplan
        og fanger opp ukjente kontonumre (9999) eller manglende kontonavn.
        """
        from compliance_engine import evaluate_ns4102_compliance

        sample_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/sample"))
        sb = pd.read_csv(os.path.join(sample_dir, "saldobalanse_balansert.csv"))
        hb = pd.read_csv(os.path.join(sample_dir, "hovedbok_balansert.csv"))

        ns_ok = evaluate_ns4102_compliance(sb, hb)
        assert ns_ok["is_compliant"] is True
        assert ns_ok["overall_recognition_pct"] == 100.0
        assert ns_ok["number_recognition_pct"] == 100.0
        assert ns_ok["name_recognition_pct"] == 100.0

        sb_bad = pd.DataFrame({
            "Konto": ["1920", "9999"],
            "Kontonavn": ["Bankinnskudd", ""],
            "Debet": [100.0, 0.0],
            "Kredit": [0.0, 100.0],
        })
        ns_bad = evaluate_ns4102_compliance(sb_bad)
        assert ns_bad["is_compliant"] is False
        assert ns_bad["overall_recognition_pct"] == 50.0
        assert "9999" in ns_bad["unmapped_accounts"]
