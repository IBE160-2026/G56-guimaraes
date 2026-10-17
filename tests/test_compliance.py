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
