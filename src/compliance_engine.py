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
    
    # Slå sammen med Saldobalansen (outer join for å fange kontoer som kun finnes i HB eller SB)
    merged = pd.merge(sb, hb_grouped, on='Konto', how='outer')
    merged['IB'] = merged['IB'].fillna(0.0)
    merged['UB'] = merged['UB'].fillna(0.0)
    merged['Netto_HB'] = merged['Netto_HB'].fillna(0.0)
    if 'Kontonavn' in merged.columns:
        merged['Kontonavn'] = merged['Kontonavn'].fillna('Ukjent konto (Kun i Hovedbok)')
    
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
    Klassifiserer standard 4-sifrede kontonumre til overordnede kontoklasser:
    - 1xxx: Eiendeler (Omløpsmidler & Anleggsmidler)
    - 2xxx: Egenkapital og Gjeld (Langsiktig & Kortsiktig gjeld)
    - 3xxx: Salgs- og Driftsinntekt
    - 4xxx: Varekostnad (Driftskostnader)
    - 5xxx: Lønnskostnad (Driftskostnader)
    - 6xxx-7xxx: Andre driftskostnader
    - 8xxx: Finansposter og Skattekostnad
    """
    acc_str = str(account_number).strip().split('.')[0]
    
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

def calculate_detailed_financial_metrics(sb_df: pd.DataFrame) -> dict:
    """
    DETERMINISTISK NØKKELTALLSMOTOR (The AI Firewall):
    Beregner fullstendige regnskapsmessige og operasjonelle nøkkeltall etter Norsk Regnskapsstandard.
    Koden regner - KI forklarer.
    """
    df = sb_df.copy()
    if 'Konto' not in df.columns:
        raise ValueError("DataFramen mangler 'Konto' for beregning av nøkkeltall.")
        
    df['Konto_str'] = df['Konto'].astype(str).str.split('.').str[0].str.strip()
    df['Debet_num'] = pd.to_numeric(df['Debet'], errors='coerce').fillna(0.0) if 'Debet' in df.columns else pd.Series(0.0, index=df.index)
    df['Kredit_num'] = pd.to_numeric(df['Kredit'], errors='coerce').fillna(0.0) if 'Kredit' in df.columns else pd.Series(0.0, index=df.index)
    df['UB_num'] = pd.to_numeric(df['UB'], errors='coerce').fillna(0.0) if 'UB' in df.columns else pd.Series(0.0, index=df.index)

    # Inntekter (Klasse 3, normalt kredit)
    inntekter = float(df[df['Konto_str'].str.startswith('3')]['Kredit_num'].sum())
    
    # Kostnadsposter
    varekostnad = float(df[df['Konto_str'].str.startswith('4')]['Debet_num'].sum())
    lonnskostnad = float(df[df['Konto_str'].str.startswith('5')]['Debet_num'].sum())
    andre_driftskostnader = float(df[df['Konto_str'].str.startswith(('6', '7'))]['Debet_num'].sum())
    samlede_driftskostnader = varekostnad + lonnskostnad + andre_driftskostnader
    
    # Resultatlinjer
    bruttofortjeneste = inntekter - varekostnad
    bruttomargin = round((bruttofortjeneste / inntekter * 100), 2) if inntekter > 0 else 0.0
    
    ebit = inntekter - samlede_driftskostnader
    driftsmargin = round((ebit / inntekter * 100), 2) if inntekter > 0 else 0.0
    
    # Finansposter (Klasse 8)
    finansinntekter = float(df[df['Konto_str'].str.startswith(('80', '81'))]['Kredit_num'].sum())
    finanskostnader = float(df[df['Konto_str'].str.startswith(('81', '82', '83', '84'))]['Debet_num'].sum())
    ordinart_resultat = ebit + finansinntekter - finanskostnader
    
    # Balansestørrelser
    omlopsmidler = float(df[df['Konto_str'].str.startswith(('14', '15', '19'))]['UB_num'].sum())
    kortsiktig_gjeld = float(df[df['Konto_str'].str.startswith('24')]['UB_num'].sum())
    arbeidskapital = omlopsmidler - kortsiktig_gjeld
    likviditetsgrad_1 = round((omlopsmidler / kortsiktig_gjeld), 2) if kortsiktig_gjeld > 0 else 0.0
    
    bankinnskudd = float(df[df['Konto_str'].str.startswith('19')]['UB_num'].sum())
    kundefordringer = float(df[df['Konto_str'].str.startswith('15')]['UB_num'].sum())
    leverandorgjeld = float(df[df['Konto_str'].str.startswith('24')]['UB_num'].sum())
    
    return {
        "driftsinntekter": inntekter,
        "varekostnad": varekostnad,
        "bruttofortjeneste": bruttofortjeneste,
        "bruttomargin": bruttomargin,
        "lonnskostnad": lonnskostnad,
        "andre_driftskostnader": andre_driftskostnader,
        "samlede_driftskostnader": samlede_driftskostnader,
        "ebit": ebit,
        "driftsmargin": driftsmargin,
        "ordinart_resultat": ordinart_resultat,
        "bankinnskudd": bankinnskudd,
        "kundefordringer": kundefordringer,
        "leverandorgjeld": leverandorgjeld,
        "arbeidskapital": arbeidskapital,
        "likviditetsgrad_1": likviditetsgrad_1
    }
