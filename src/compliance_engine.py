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
    DETERMINISTISK NØKKELTALLSMOTOR (The AI Firewall – v2.0 CFO-pakke):
    Beregner fullstendige regnskapsmessige og operasjonelle nøkkeltall etter Norsk Regnskapsstandard (NRS)
    og NS 4102, inkludert lønnsomhet, likviditet (LG1/LG2), soliditet (egenkapitalandel/gjeldsgrad)
    og rentabilitet (TKR og EKR basert på gjennomsnitt av IB og UB).
    Koden regner - KI forklarer.
    """
    df = sb_df.copy()
    if 'Konto' not in df.columns:
        raise ValueError("DataFramen mangler 'Konto' for beregning av nøkkeltall.")

    df['Konto_str'] = df['Konto'].astype(str).str.split('.').str[0].str.strip()
    df['Debet_num'] = pd.to_numeric(df['Debet'], errors='coerce').fillna(0.0) if 'Debet' in df.columns else pd.Series(0.0, index=df.index)
    df['Kredit_num'] = pd.to_numeric(df['Kredit'], errors='coerce').fillna(0.0) if 'Kredit' in df.columns else pd.Series(0.0, index=df.index)
    has_ib = 'IB' in df.columns
    has_ub = 'UB' in df.columns
    df['IB_num'] = pd.to_numeric(df['IB'], errors='coerce').fillna(0.0) if has_ib else pd.Series(0.0, index=df.index)
    df['UB_num'] = pd.to_numeric(df['UB'], errors='coerce').fillna(0.0) if has_ub else pd.Series(0.0, index=df.index)

    # 1. Resultatregnskap (NS 4102 klasse 3–8)
    inntekter = float(df[df['Konto_str'].str.startswith('3')]['Kredit_num'].sum())

    varekostnad = float(df[df['Konto_str'].str.startswith('4')]['Debet_num'].sum())
    lonnskostnad = float(df[df['Konto_str'].str.startswith('5')]['Debet_num'].sum())
    andre_driftskostnader = float(df[df['Konto_str'].str.startswith(('6', '7'))]['Debet_num'].sum())
    samlede_driftskostnader = varekostnad + lonnskostnad + andre_driftskostnader

    bruttofortjeneste = inntekter - varekostnad
    bruttomargin = round((bruttofortjeneste / inntekter * 100), 2) if inntekter > 0 else 0.0
    varekost_andel = round((varekostnad / inntekter * 100), 2) if inntekter > 0 else 0.0
    lonnsandel = round((lonnskostnad / inntekter * 100), 2) if inntekter > 0 else 0.0
    opex_andel = round((andre_driftskostnader / inntekter * 100), 2) if inntekter > 0 else 0.0
    driftskost_andel = round((samlede_driftskostnader / inntekter * 100), 2) if inntekter > 0 else 0.0

    ebit = inntekter - samlede_driftskostnader
    driftsmargin = round((ebit / inntekter * 100), 2) if inntekter > 0 else 0.0

    # Finansposter (Klasse 8)
    finansinntekter = float(df[df['Konto_str'].str.startswith('80')]['Kredit_num'].sum())
    finanskostnader = float(df[df['Konto_str'].str.startswith(('81', '82', '83', '84'))]['Debet_num'].sum())
    ordinart_resultat = ebit + finansinntekter - finanskostnader

    # 2. Eiendeler (NS 4102 klasse 1)
    anleggsmidler = float(df[df['Konto_str'].str.startswith(('10', '11', '12', '13'))]['UB_num'].sum())
    varelager = float(df[df['Konto_str'].str.startswith('14')]['UB_num'].sum())
    kundefordringer = float(df[df['Konto_str'].str.startswith('15')]['UB_num'].sum())
    bankinnskudd = float(df[df['Konto_str'].str.startswith('19')]['UB_num'].sum())
    omlopsmidler = float(df[df['Konto_str'].str.startswith(('14', '15', '16', '17', '18', '19'))]['UB_num'].sum())

    totalkapital_ib = float(df[df['Konto_str'].str.startswith('1')]['IB_num'].sum())
    totalkapital_ub = float(df[df['Konto_str'].str.startswith('1')]['UB_num'].sum())

    # 3. Egenkapital og Gjeld (NS 4102 klasse 2 – fortegnsnormalisert med abs() for kreditsaldoer)
    egenkapital_ib = abs(float(df[df['Konto_str'].str.startswith('20')]['IB_num'].sum()))
    bokfort_egenkapital_ub = abs(float(df[df['Konto_str'].str.startswith('20')]['UB_num'].sum()))

    langsiktig_gjeld = abs(float(df[df['Konto_str'].str.startswith(('21', '22', '23'))]['UB_num'].sum()))
    kortsiktig_gjeld = abs(float(df[df['Konto_str'].str.startswith(('24', '25', '26', '27', '28', '29'))]['UB_num'].sum()))
    leverandorgjeld = abs(float(df[df['Konto_str'].str.startswith('24')]['UB_num'].sum()))
    total_gjeld = langsiktig_gjeld + kortsiktig_gjeld

    # Reell mellombalanse-egenkapital: legger til udisponert perioderesultat når resultatregnskapet (3xxx–8xxx)
    # ikke er avsluttet mot 20xx, slik at Eiendeler = Reell EK + Gjeld balanserer.
    resultat_ub_sum = float(df[df['Konto_str'].str.startswith(('3', '4', '5', '6', '7', '8'))]['UB_num'].sum())
    udisponert_resultat_ub = -resultat_ub_sum
    reell_egenkapital_ub = bokfort_egenkapital_ub + udisponert_resultat_ub
    if bokfort_egenkapital_ub == 0.0 and abs(udisponert_resultat_ub) < 0.01 and totalkapital_ub > total_gjeld:
        reell_egenkapital_ub = totalkapital_ub - total_gjeld

    # 4. Likviditetsmål
    arbeidskapital = omlopsmidler - kortsiktig_gjeld
    likviditetsgrad_1 = round((omlopsmidler / kortsiktig_gjeld), 2) if kortsiktig_gjeld > 0 else 0.0
    likviditetsgrad_2 = round(((omlopsmidler - varelager) / kortsiktig_gjeld), 2) if kortsiktig_gjeld > 0 else 0.0

    # 5. Soliditetsmål
    egenkapitalandel = round((reell_egenkapital_ub / totalkapital_ub * 100), 2) if totalkapital_ub > 0 else 0.0
    gjeldsgrad = round((total_gjeld / reell_egenkapital_ub), 2) if reell_egenkapital_ub > 0 else 0.0

    # 6. Rentabilitetsmål (TKR og EKR basert på gjennomsnitt av IB og UB)
    if has_ib and (totalkapital_ib > 0 or totalkapital_ub > 0):
        gjennomsnittlig_totalkapital = (totalkapital_ib + totalkapital_ub) / 2.0
    else:
        gjennomsnittlig_totalkapital = totalkapital_ub

    if has_ib and (egenkapital_ib > 0 or reell_egenkapital_ub > 0):
        gjennomsnittlig_egenkapital = (egenkapital_ib + reell_egenkapital_ub) / 2.0
    else:
        gjennomsnittlig_egenkapital = reell_egenkapital_ub

    totalkapitalrentabilitet = (
        round(((ebit + finansinntekter) / gjennomsnittlig_totalkapital * 100), 2)
        if gjennomsnittlig_totalkapital > 0
        else 0.0
    )
    egenkapitalrentabilitet = (
        round((ordinart_resultat / gjennomsnittlig_egenkapital * 100), 2)
        if gjennomsnittlig_egenkapital > 0
        else 0.0
    )

    return {
        "driftsinntekter": inntekter,
        "varekostnad": varekostnad,
        "varekost_andel": varekost_andel,
        "bruttofortjeneste": bruttofortjeneste,
        "bruttomargin": bruttomargin,
        "lonnskostnad": lonnskostnad,
        "lonnsandel": lonnsandel,
        "andre_driftskostnader": andre_driftskostnader,
        "opex_andel": opex_andel,
        "samlede_driftskostnader": samlede_driftskostnader,
        "driftskost_andel": driftskost_andel,
        "ebit": ebit,
        "driftsmargin": driftsmargin,
        "finansinntekter": finansinntekter,
        "finanskostnader": finanskostnader,
        "ordinart_resultat": ordinart_resultat,
        "anleggsmidler": anleggsmidler,
        "varelager": varelager,
        "bankinnskudd": bankinnskudd,
        "kundefordringer": kundefordringer,
        "omlopsmidler": omlopsmidler,
        "totalkapital_ib": totalkapital_ib,
        "totalkapital_ub": totalkapital_ub,
        "gjennomsnittlig_totalkapital": gjennomsnittlig_totalkapital,
        "egenkapital_ib": egenkapital_ib,
        "bokfort_egenkapital_ub": bokfort_egenkapital_ub,
        "reell_egenkapital_ub": reell_egenkapital_ub,
        "gjennomsnittlig_egenkapital": gjennomsnittlig_egenkapital,
        "langsiktig_gjeld": langsiktig_gjeld,
        "kortsiktig_gjeld": kortsiktig_gjeld,
        "leverandorgjeld": leverandorgjeld,
        "total_gjeld": total_gjeld,
        "arbeidskapital": arbeidskapital,
        "likviditetsgrad_1": likviditetsgrad_1,
        "likviditetsgrad_2": likviditetsgrad_2,
        "egenkapitalandel": egenkapitalandel,
        "gjeldsgrad": gjeldsgrad,
        "totalkapitalrentabilitet": totalkapitalrentabilitet,
        "egenkapitalrentabilitet": egenkapitalrentabilitet,
    }


def evaluate_vat_compliance(sb_df: pd.DataFrame, hb_df: pd.DataFrame | None = None) -> dict:
    """
    DETERMINISTISK MVA-KONTROLL (Norsk MVA-lovgivning & NS 4102):
    Kontrollerer logisk sammenheng mellom:
      - MVA-kontoer i 2700-serien (2700-2709 Utgående MVA, 2710-2719 Inngående MVA, 2740 Oppgjørskonto MVA)
      - Salgsinntekter i 3000-serien (3000-3099 avgiftspliktig salg, 3100-3199 avgiftsfritt/unntatt salg)
      - Varekostnad (4000-serien) og andre driftskostnader (6000-7999)
    Ingen bruk av LLM – 100 % deterministisk Python/Pandas-logikk.
    """
    df = sb_df.copy()
    if "Konto" not in df.columns:
        raise ValueError("DataFramen mangler 'Konto' for MVA-kontroll.")

    df["Konto_str"] = df["Konto"].astype(str).str.split(".").str[0].str.strip()
    df["Kontonavn_str"] = (
        df["Kontonavn"].fillna("Ukjent kontonavn").astype(str).str.strip()
        if "Kontonavn" in df.columns
        else pd.Series("Ukjent kontonavn", index=df.index)
    )
    df["Debet_num"] = pd.to_numeric(df["Debet"], errors="coerce").fillna(0.0) if "Debet" in df.columns else pd.Series(0.0, index=df.index)
    df["Kredit_num"] = pd.to_numeric(df["Kredit"], errors="coerce").fillna(0.0) if "Kredit" in df.columns else pd.Series(0.0, index=df.index)
    df["UB_num"] = pd.to_numeric(df["UB"], errors="coerce").fillna(0.0) if "UB" in df.columns else (df["Debet_num"] - df["Kredit_num"])

    # Klassifiser MVA-relevante kontogrupper
    vat_mask = df["Konto_str"].str.startswith("27")
    out_vat_mask = df["Konto_str"].str.startswith("270")
    in_vat_mask = df["Konto_str"].str.startswith("271")
    settle_vat_mask = df["Konto_str"].str.startswith("274")

    taxable_sales_mask = df["Konto_str"].str.startswith("30")
    exempt_sales_mask = df["Konto_str"].str.startswith("31")
    all_sales_mask = df["Konto_str"].str.startswith("3")
    cost_mask = df["Konto_str"].str.startswith(("4", "6", "7"))

    taxable_sales_3000 = float(df[taxable_sales_mask]["Kredit_num"].sum())
    exempt_sales_3100 = float(df[exempt_sales_mask]["Kredit_num"].sum())
    total_sales_3xxx = float(df[all_sales_mask]["Kredit_num"].sum())
    cost_base = float(df[cost_mask]["Debet_num"].sum())

    outgoing_vat = float(df[out_vat_mask]["Kredit_num"].sum())
    outgoing_vat_debit = float(df[out_vat_mask]["Debet_num"].sum())
    incoming_vat = float(df[in_vat_mask]["Debet_num"].sum())
    settlement_vat_ub = float(df[settle_vat_mask]["UB_num"].sum())

    vat_accounts_df = df[vat_mask].copy()
    has_vat_accounts = len(vat_accounts_df) > 0

    effective_out_vat_pct = (
        round((outgoing_vat / taxable_sales_3000) * 100.0, 2)
        if taxable_sales_3000 > 0
        else 0.0
    )

    findings: list[str] = []
    status = "ok"

    # Regel 1: Salgsinntekter på 3000-serien (normalt avgiftspliktig) uten utgående MVA i 2700-serien
    if taxable_sales_3000 > 0 and outgoing_vat == 0.0 and not has_vat_accounts:
        status = "warning"
        findings.append(
            f"Det er bokført {taxable_sales_3000:,.2f} NOK på avgiftspliktige salgskontoer (3000-serien), "
            "men ingen MVA-kontoer i 2700-serien finnes i saldobalansen. Kontroller om virksomheten er "
            "unntatt MVA (f.eks. undervisning/helse/finans), eller om salg skulle vært ført på 3100-serien (avgiftsfritt).".replace(",", " ")
        )
    elif taxable_sales_3000 > 0 and outgoing_vat == 0.0 and has_vat_accounts:
        status = "warning"
        findings.append(
            f"Salgsinntekter i 3000-serien utgjør {taxable_sales_3000:,.2f} NOK, men utgående MVA (2700–2709) er 0,00 NOK.".replace(",", " ")
        )

    # Regel 2: Sjekk implisitt MVA-sats mot norske satser (12 %, 15 %, 25 %) når utgående MVA er bokført
    if taxable_sales_3000 > 0 and outgoing_vat > 0:
        if not (10.0 <= effective_out_vat_pct <= 26.0):
            status = "warning"
            findings.append(
                f"Beregnet utgående MVA-andel av avgiftspliktig salg er {effective_out_vat_pct:.1f} %, "
                "som avviker fra ordinære norske MVA-satser (12 %, 15 % eller 25 %)."
            )

    # Regel 3: Varekjøp / driftskostnader uten inngående MVA
    if cost_base > 0 and incoming_vat == 0.0:
        if status == "ok":
            status = "warning"
        findings.append(
            f"Bokførte varekjøp og driftskostnader (klasse 4/6/7) utgjør {cost_base:,.2f} NOK uten registrert "
            "fradrag for inngående MVA (konto 2710–2719).".replace(",", " ")
        )

    # Regel 4: Uvanlig netto debetsaldo på utgående MVA-konto
    out_vat_ub = float(df[out_vat_mask]["UB_num"].sum())
    if out_vat_ub > 0.01 and outgoing_vat_debit > outgoing_vat:
        status = "error"
        findings.append(
            f"Utgående MVA (2700-serien) har positiv debetsaldo ({out_vat_ub:,.2f} NOK). "
            "Utgående avgift skal normalt stå i kredit frem til MVA-oppgjør mot konto 2740.".replace(",", " ")
        )

    # Regel 5: Sjekk Hovedbok (HB) for salgsbilag på 3000-serien uten MVA-motpost
    if hb_df is not None and "Konto" in hb_df.columns and "Bilagsnr" in hb_df.columns:
        hb = hb_df.copy()
        hb["Konto_str"] = hb["Konto"].astype(str).str.split(".").str[0].str.strip()
        hb["Bilagsnr_str"] = hb["Bilagsnr"].astype(str).str.strip()
        sales_vouchers = set(hb[hb["Konto_str"].str.startswith("30")]["Bilagsnr_str"].unique())
        vat_vouchers = set(hb[hb["Konto_str"].str.startswith("27")]["Bilagsnr_str"].unique())
        vouchers_without_vat = sorted(sales_vouchers - vat_vouchers)
        if vouchers_without_vat:
            if status == "ok":
                status = "warning"
            findings.append(
                f"I Hovedboken er {len(vouchers_without_vat)} salgsbilag på 3000-serien "
                f"(Bilag #{', #'.join(vouchers_without_vat)}) bokført uten MVA-splitt mot 2700-serien."
            )

    if not findings:
        summary = (
            "Alle kontrollerte sammenhenger mellom salgsinntekter (3000-serien), kostnadskontoer (4xxx/6xxx/7xxx) "
            f"og MVA-kontoer (2700-serien) er konsistente (effektiv utgående MVA-sats: {effective_out_vat_pct:.1f} %)."
        )
    else:
        summary = (
            f"MVA-kontrollen avdekket {len(findings)} revisjonsobservasjon(er) på tvers av inntekts-, kostnads- og avgiftskontoer."
        )

    # Bygg oversiktstabell for relevante kontoer
    relevant_mask = vat_mask | all_sales_mask | cost_mask
    rel_df = df[relevant_mask].copy()

    def _classify_vat_role(acc: str) -> str:
        if acc.startswith("270"):
            return "Utgående MVA (270x)"
        if acc.startswith("271"):
            return "Inngående MVA (271x)"
        if acc.startswith("274"):
            return "Oppgjørskonto MVA (274x)"
        if acc.startswith("27"):
            return "Øvrig avgiftskonto (27xx)"
        if acc.startswith("30"):
            return "Avgiftspliktig salgsinntekt (30xx)"
        if acc.startswith("31"):
            return "Avgiftsfri salgsinntekt (31xx)"
        if acc.startswith("3"):
            return "Øvrig driftsinntekt (3xxx)"
        if acc.startswith("4"):
            return "Varekostnad – MVA-grunnlag kjøp (4xxx)"
        return "Driftskostnad – MVA-grunnlag kjøp (6xxx/7xxx)"

    rel_df["MVA_Rolle"] = rel_df["Konto_str"].apply(_classify_vat_role)
    account_summary_df = rel_df[["Konto_str", "Kontonavn_str", "MVA_Rolle", "Debet_num", "Kredit_num", "UB_num"]].rename(
        columns={
            "Konto_str": "Konto",
            "Kontonavn_str": "Kontonavn",
            "Debet_num": "Debet",
            "Kredit_num": "Kredit",
            "UB_num": "UB",
        }
    )

    return {
        "status": status,
        "has_vat_accounts": has_vat_accounts,
        "vat_account_count": int(len(vat_accounts_df)),
        "taxable_sales_3000": taxable_sales_3000,
        "exempt_sales_3100": exempt_sales_3100,
        "total_sales_3xxx": total_sales_3xxx,
        "cost_base_4xxx_6xxx_7xxx": cost_base,
        "outgoing_vat": outgoing_vat,
        "incoming_vat": incoming_vat,
        "settlement_vat_ub": settlement_vat_ub,
        "effective_out_vat_pct": effective_out_vat_pct,
        "findings": findings,
        "summary": summary,
        "account_summary_df": account_summary_df,
    }


def evaluate_ns4102_compliance(sb_df: pd.DataFrame, hb_df: pd.DataFrame | None = None) -> dict:
    """
    DETERMINISTISK NS 4102- OG REGNSKAPSSPRÅK-KONTROLL:
    Evaluerer om kontoplanen følger Norsk Standard Kontoplan (NS 4102) med:
      1. Gyldige 4-sifrede kontonumre i kontoklassene 1000–8999.
      2. Anerkjente norske kontonavn (Bokføringsloven / Regnskapsloven § 3-4 om norsk regnskapsspråk).
      3. Fullstendighet mellom Hovedbok og Saldobalanse (ingen udefinerte kontoer i HB).
    Returnerer gjenkjennelsesgrad (%) og detaljert tabell per konto.
    """
    df = sb_df.copy()
    if "Konto" not in df.columns:
        raise ValueError("DataFramen mangler 'Konto' for NS 4102-kontroll.")

    invalid_name_tokens = {
        "",
        "nan",
        "none",
        "null",
        "ukjent",
        "ukjent konto",
        "ukjent konto (kun i hovedbok)",
        "undefined",
        "unknown",
        "account",
        "n/a",
    }

    rows = []
    sb_accounts = set()

    for _, r in df.iterrows():
        acc_str = str(r["Konto"]).split(".")[0].strip()
        sb_accounts.add(acc_str)
        raw_name = str(r.get("Kontonavn", "")).strip() if "Kontonavn" in df.columns and pd.notna(r.get("Kontonavn")) else ""
        ns_cat = map_to_ns4102(acc_str)

        is_valid_number = (
            len(acc_str) == 4
            and acc_str.isdigit()
            and 1000 <= int(acc_str) <= 8999
            and ns_cat != "Ukjent / Udefinert"
        )
        is_valid_name = (
            len(raw_name) >= 3
            and raw_name.lower() not in invalid_name_tokens
            and not raw_name.isdigit()
        )

        rows.append({
            "Konto": acc_str,
            "Kontonavn": raw_name if raw_name else "(Mangler kontonavn)",
            "NS4102_Kategori": ns_cat,
            "Nummer_OK": is_valid_number,
            "Sprak_OK": is_valid_name,
            "Status": "✅ NS 4102 Godkjent" if (is_valid_number and is_valid_name) else "⚠️ Avvik",
        })

    hb_only_accounts: list[str] = []
    if hb_df is not None and "Konto" in hb_df.columns:
        for acc_val in hb_df["Konto"].dropna().unique():
            acc_str = str(acc_val).split(".")[0].strip()
            if acc_str not in sb_accounts:
                hb_only_accounts.append(acc_str)
                ns_cat = map_to_ns4102(acc_str)
                is_valid_number = (
                    len(acc_str) == 4
                    and acc_str.isdigit()
                    and 1000 <= int(acc_str) <= 8999
                    and ns_cat != "Ukjent / Udefinert"
                )
                rows.append({
                    "Konto": acc_str,
                    "Kontonavn": "Ukjent konto (Kun i Hovedbok)",
                    "NS4102_Kategori": ns_cat,
                    "Nummer_OK": is_valid_number,
                    "Sprak_OK": False,
                    "Status": "⚠️ Kun i Hovedbok",
                })

    details_df = pd.DataFrame(rows)
    total_accounts = len(details_df)
    valid_number_count = int(details_df["Nummer_OK"].sum()) if total_accounts > 0 else 0
    valid_name_count = int(details_df["Sprak_OK"].sum()) if total_accounts > 0 else 0
    fully_compliant_count = int((details_df["Nummer_OK"] & details_df["Sprak_OK"]).sum()) if total_accounts > 0 else 0

    number_recognition_pct = round((valid_number_count / total_accounts) * 100.0, 1) if total_accounts > 0 else 0.0
    name_recognition_pct = round((valid_name_count / total_accounts) * 100.0, 1) if total_accounts > 0 else 0.0
    overall_recognition_pct = round((fully_compliant_count / total_accounts) * 100.0, 1) if total_accounts > 0 else 0.0

    unmapped_accounts = details_df[~details_df["Nummer_OK"]]["Konto"].tolist() if total_accounts > 0 else []
    unnamed_accounts = details_df[~details_df["Sprak_OK"]]["Konto"].tolist() if total_accounts > 0 else []

    findings: list[str] = []
    if unmapped_accounts:
        findings.append(
            f"Kontonummer utenfor NS 4102 (1000–8999) oppdaget: {', '.join(unmapped_accounts)}."
        )
    if unnamed_accounts:
        findings.append(
            f"Manglende eller ikke-standardisert norsk kontonavn på konto: {', '.join(unnamed_accounts)}."
        )
    if hb_only_accounts:
        findings.append(
            f"Kontoer brukt i Hovedbok som mangler i Saldobalansens kontoplan: {', '.join(hb_only_accounts)}."
        )

    is_compliant = (overall_recognition_pct == 100.0) and (len(hb_only_accounts) == 0) and (total_accounts > 0)

    if is_compliant:
        summary = (
            f"Kontoplanen følger Norsk Standard Kontoplan (NS 4102) og norsk regnskapsspråk "
            f"med {overall_recognition_pct:.1f} % gjenkjennelsesgrad ({fully_compliant_count} av {total_accounts} kontoer godkjent)."
        )
    else:
        summary = (
            f"Gjenkjennelsesgrad mot NS 4102 er {overall_recognition_pct:.1f} % "
            f"({fully_compliant_count} av {total_accounts} kontoer godkjent). Se avviksdetaljer under."
        )

    return {
        "is_compliant": is_compliant,
        "total_accounts": total_accounts,
        "valid_number_count": valid_number_count,
        "valid_name_count": valid_name_count,
        "fully_compliant_count": fully_compliant_count,
        "number_recognition_pct": number_recognition_pct,
        "name_recognition_pct": name_recognition_pct,
        "overall_recognition_pct": overall_recognition_pct,
        "unmapped_accounts": unmapped_accounts,
        "unnamed_accounts": unnamed_accounts,
        "hb_only_accounts": hb_only_accounts,
        "findings": findings,
        "summary": summary,
        "details_df": details_df,
    }
