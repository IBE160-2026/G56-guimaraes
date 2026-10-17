import pandas as pd
import numpy as np

def validate_balance(df: pd.DataFrame, debit_col: str = 'Debet', credit_col: str = 'Kredit') -> bool:
    """
    ELITE COMPLIANCE PATTERN:
    Sjekker at summen av Debet er lik summen av Kredit i en gitt rapport (SB eller HB).
    En regnskapsfil SKAL avvises hvis dette ikke stemmer (Double-entry bookkeeping).
    
    Bruker np.isclose for å unngå flyttallsfeil (floating point precision issues).
    """
    if debit_col not in df.columns or credit_col not in df.columns:
        raise ValueError(f"Manglende kolonner for saldo. Forventet '{debit_col}' og '{credit_col}'.")
    
    debit_sum = pd.to_numeric(df[debit_col], errors='coerce').fillna(0).sum()
    credit_sum = pd.to_numeric(df[credit_col], errors='coerce').fillna(0).sum()
    
    if not np.isclose(debit_sum, credit_sum, atol=0.01):
        raise ValueError(f"BALANSEFEIL (Debet ≠ Kredit): Debet sum er {debit_sum:.2f}, Kredit sum er {credit_sum:.2f}. Differanse: {abs(debit_sum - credit_sum):.2f}")
    
    return True

def reconcile_hb_with_sb(sb_df: pd.DataFrame, hb_df: pd.DataFrame) -> dict:
    """
    ELITE KRYSSAVSTEMMING (Kjernefunksjon i v1):
    Sjekker konsistensen mellom Saldobalanse (SB) og Hovedbok (HB).
    Regel: Inngående balanse (IB) + sum transaksjoner i HB = Utgående balanse (UB) i SB.
    
    Forventer:
      sb_df med kolonnene: 'Konto', 'IB', 'UB' (og evt 'Kontonavn')
      hb_df med kolonnene: 'Konto', 'Debet', 'Kredit'
    """
    # Sikre string-matching på kontonummer
    sb = sb_df.copy()
    hb = hb_df.copy()
    sb['Konto'] = sb['Konto'].astype(str).str.strip()
    hb['Konto'] = hb['Konto'].astype(str).str.strip()
    
    sb['IB'] = pd.to_numeric(sb['IB'], errors='coerce').fillna(0.0)
    sb['UB'] = pd.to_numeric(sb['UB'], errors='coerce').fillna(0.0)
    
    hb['Debet'] = pd.to_numeric(hb['Debet'], errors='coerce').fillna(0.0)
    hb['Kredit'] = pd.to_numeric(hb['Kredit'], errors='coerce').fillna(0.0)
    
    # Beregn netto transaksjon per konto i Hovedboken (Debet minus Kredit)
    hb['Netto_HB'] = hb['Debet'] - hb['Kredit']
    hb_grouped = hb.groupby('Konto')['Netto_HB'].sum().reset_index()
    
    # Slå sammen med Saldobalansen
    merged = pd.merge(sb, hb_grouped, on='Konto', how='left')
    merged['Netto_HB'] = merged['Netto_HB'].fillna(0.0)
    
    # Beregnet UB basert på HB
    merged['Beregnet_UB'] = merged['IB'] + merged['Netto_HB']
    merged['Avvik'] = (merged['UB'] - merged['Beregnet_UB']).round(2)
    merged['Stemmer'] = np.isclose(merged['UB'], merged['Beregnet_UB'], atol=0.01)
    
    discrepancies = merged[~merged['Stemmer']]
    is_reconciled = len(discrepancies) == 0
    
    return {
        "is_reconciled": is_reconciled,
        "discrepancy_count": len(discrepancies),
        "reconciliation_table": merged,
        "discrepancies": discrepancies
    }

def map_to_ns4102(account_number: str) -> str:
    """
    Mapping til Norsk Standard Kontoplan (NS 4102).
    Klassifiserer standard 4-sifrede kontonumre til overordnede kontoklasser.
    """
    acc_str = str(account_number).strip()
    
    if acc_str.startswith('1'):
        return "Eiendeler (NS 4102)"
    elif acc_str.startswith('2'):
        return "Egenkapital og Gjeld (NS 4102)"
    elif acc_str.startswith('3'):
        return "Salgs- og Driftsinntekt (NS 4102)"
    elif acc_str.startswith(('4', '5', '6', '7')):
        return "Driftskostnader (NS 4102)"
    elif acc_str.startswith('8'):
        return "Finans og Skatt (NS 4102)"
    else:
        return "Ukjent / Udefinert"
