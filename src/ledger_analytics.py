"""
Deterministisk Hovedboks- og Lønnsomhetsmotor (The AI Firewall – v2.0).

Leverer:
1. Periodeutledning fra hovedboksdatoer (`extract_period_label`)
2. Konto-drilldown med løpende saldo fra IB til UB (`get_account_drilldown`)
3. Bilagsinspektør med motkontoer og intern balansekontroll (`get_voucher_details`)
4. Rangering av kostnadsdrivere i kontoklasse 4–7 (`summarize_cost_drivers`)
5. Regelbasert, deterministisk lønnsomhetsmotor med ferdigkalkulerte kronepotensialer
   (`generate_profitability_recommendations`)
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd


def extract_period_label(hb_df: pd.DataFrame) -> str:
    """
    Utleder en lesbar periodeetikett fra Hovedbokens `Dato`-kolonne (f.eks. '2026-01'
    eller '2026-01 til 2026-03'). Returnerer 'Inneværende periode' hvis dato mangler.
    """
    if hb_df is None or hb_df.empty or "Dato" not in hb_df.columns:
        return "Inneværende periode"

    parsed = pd.to_datetime(hb_df["Dato"], errors="coerce").dropna()
    if parsed.empty:
        return "Inneværende periode"

    min_ym = parsed.min().strftime("%Y-%m")
    max_ym = parsed.max().strftime("%Y-%m")
    return min_ym if min_ym == max_ym else f"{min_ym} til {max_ym}"


def get_account_drilldown(
    hb_df: pd.DataFrame,
    sb_df: pd.DataFrame,
    account_no: str,
) -> Dict[str, Any]:
    """
    Returnerer samtlige transaksjoner for en valgt konto i Hovedboken med kronologisk
    løpende saldo (`Lopende_Saldo`) fra `IB` i Saldobalansen frem til `Beregnet_UB`.
    """
    target_acc = str(account_no).strip().split(".")[0]

    sb = sb_df.copy()
    sb["Konto_norm"] = sb["Konto"].astype(str).str.split(".").str[0].str.strip() if "Konto" in sb.columns else ""

    sb_match = sb[sb["Konto_norm"] == target_acc]
    if not sb_match.empty:
        row0 = sb_match.iloc[0]
        ib_val = float(pd.to_numeric(row0.get("IB", 0.0), errors="coerce") or 0.0)
        ub_sb_val = float(pd.to_numeric(row0.get("UB", 0.0), errors="coerce") or 0.0)
        account_name = str(row0.get("Kontonavn", f"Konto {target_acc}"))
    else:
        ib_val = 0.0
        ub_sb_val = 0.0
        account_name = f"Konto {target_acc}"

    hb = hb_df.copy()
    hb["Konto_norm"] = hb["Konto"].astype(str).str.split(".").str[0].str.strip()
    hb_acc = hb[hb["Konto_norm"] == target_acc].copy()

    if hb_acc.empty:
        empty_tx = pd.DataFrame(
            columns=["Bilagsnr", "Dato", "Konto", "Kontonavn", "Beskrivelse", "Debet", "Kredit", "Netto", "Lopende_Saldo"]
        )
        return {
            "account_no": target_acc,
            "account_name": account_name,
            "ib": ib_val,
            "net_hb": 0.0,
            "calculated_ub": ib_val,
            "ub_sb": ub_sb_val,
            "discrepancy": round(ub_sb_val - ib_val, 2),
            "is_reconciled": bool(np.isclose(ub_sb_val, ib_val, atol=0.01)),
            "transaction_count": 0,
            "transactions": empty_tx,
        }

    if account_name == f"Konto {target_acc}" and "Kontonavn" in hb_acc.columns:
        first_name = str(hb_acc["Kontonavn"].iloc[0] or "").strip()
        if first_name:
            account_name = first_name

    hb_acc["Debet"] = pd.to_numeric(hb_acc["Debet"], errors="coerce").fillna(0.0)
    hb_acc["Kredit"] = pd.to_numeric(hb_acc["Kredit"], errors="coerce").fillna(0.0)
    hb_acc["Netto"] = hb_acc["Debet"] - hb_acc["Kredit"]

    # Sorter på dato (hvis den finnes) + opprinnelig rekkefølge
    hb_acc["_orig_order"] = range(len(hb_acc))
    if "Dato" in hb_acc.columns:
        hb_acc = hb_acc.sort_values(by=["Dato", "_orig_order"], kind="mergesort")
    else:
        hb_acc["Dato"] = ""

    if "Bilagsnr" not in hb_acc.columns:
        hb_acc["Bilagsnr"] = ""
    if "Beskrivelse" not in hb_acc.columns:
        hb_acc["Beskrivelse"] = hb_acc.get("Kontonavn", "")
    if "Kontonavn" not in hb_acc.columns:
        hb_acc["Kontonavn"] = account_name

    hb_acc["Lopende_Saldo"] = (ib_val + hb_acc["Netto"].cumsum()).round(2)
    net_hb = float(hb_acc["Netto"].sum())
    calculated_ub = round(ib_val + net_hb, 2)
    discrepancy = round(ub_sb_val - calculated_ub, 2)

    out_cols = ["Bilagsnr", "Dato", "Konto", "Kontonavn", "Beskrivelse", "Debet", "Kredit", "Netto", "Lopende_Saldo"]
    clean_tx = hb_acc[out_cols].reset_index(drop=True)

    return {
        "account_no": target_acc,
        "account_name": account_name,
        "ib": ib_val,
        "net_hb": round(net_hb, 2),
        "calculated_ub": calculated_ub,
        "ub_sb": ub_sb_val,
        "discrepancy": discrepancy,
        "is_reconciled": bool(np.isclose(ub_sb_val, calculated_ub, atol=0.01)),
        "transaction_count": len(clean_tx),
        "transactions": clean_tx,
    }


def get_voucher_details(hb_df: pd.DataFrame, voucher_no: str) -> Dict[str, Any]:
    """
    Henter alle posteringslinjer (motkontoer) knyttet til et spesifikt `Bilagsnr`
    og verifiserer om bilaget isolert sett går i null (Debet = Kredit).
    """
    if hb_df is None or hb_df.empty or "Bilagsnr" not in hb_df.columns:
        return {
            "voucher_no": str(voucher_no),
            "is_balanced": True,
            "debit_sum": 0.0,
            "credit_sum": 0.0,
            "lines": pd.DataFrame(),
        }

    target_v = str(voucher_no).strip()
    hb = hb_df.copy()
    hb["Bilagsnr_str"] = hb["Bilagsnr"].astype(str).str.strip()
    matched = hb[hb["Bilagsnr_str"] == target_v].copy()

    if matched.empty:
        return {
            "voucher_no": target_v,
            "is_balanced": True,
            "debit_sum": 0.0,
            "credit_sum": 0.0,
            "lines": pd.DataFrame(),
        }

    matched["Debet"] = pd.to_numeric(matched["Debet"], errors="coerce").fillna(0.0)
    matched["Kredit"] = pd.to_numeric(matched["Kredit"], errors="coerce").fillna(0.0)
    d_sum = float(matched["Debet"].sum())
    c_sum = float(matched["Kredit"].sum())

    keep_cols = [c for c in ["Bilagsnr", "Dato", "Konto", "Kontonavn", "Beskrivelse", "Debet", "Kredit"] if c in matched.columns]
    return {
        "voucher_no": target_v,
        "is_balanced": bool(np.isclose(d_sum, c_sum, atol=0.01)),
        "debit_sum": round(d_sum, 2),
        "credit_sum": round(c_sum, 2),
        "lines": matched[keep_cols].reset_index(drop=True),
    }


def summarize_cost_drivers(
    sb_df: pd.DataFrame,
    hb_df: Optional[pd.DataFrame] = None,
    top_n: int = 5,
) -> List[Dict[str, Any]]:
    """
    Rangerer de største driftskostnadskontoene (NS 4102 kontoklasse 4–7) deterministisk
    med beløp, andel av samlede driftskostnader, andel av driftsinntekter og antall HB-posteringer.
    """
    if sb_df is None or sb_df.empty or "Konto" not in sb_df.columns:
        return []

    df = sb_df.copy()
    df["Konto_str"] = df["Konto"].astype(str).str.split(".").str[0].str.strip()
    df["Debet_num"] = pd.to_numeric(df.get("Debet", 0.0), errors="coerce").fillna(0.0)
    df["Kredit_num"] = pd.to_numeric(df.get("Kredit", 0.0), errors="coerce").fillna(0.0)

    revenue = float(df[df["Konto_str"].str.startswith("3")]["Kredit_num"].sum())
    cost_df = df[df["Konto_str"].str.startswith(("4", "5", "6", "7"))].copy()
    cost_df["Netto_Kostnad"] = (cost_df["Debet_num"] - cost_df["Kredit_num"]).clip(lower=0.0)
    cost_df = cost_df[cost_df["Netto_Kostnad"] > 0].sort_values(by="Netto_Kostnad", ascending=False)

    total_opex = float(cost_df["Netto_Kostnad"].sum())
    if total_opex <= 0:
        return []

    hb_counts: Dict[str, int] = {}
    if hb_df is not None and not hb_df.empty and "Konto" in hb_df.columns:
        hb_acc_series = hb_df["Konto"].astype(str).str.split(".").str[0].str.strip()
        hb_counts = hb_acc_series.value_counts().to_dict()

    drivers: List[Dict[str, Any]] = []
    for _, row in cost_df.head(top_n).iterrows():
        acc_no = str(row["Konto_str"])
        amount = round(float(row["Netto_Kostnad"]), 2)
        drivers.append(
            {
                "konto": acc_no,
                "kontonavn": str(row.get("Kontonavn", f"Konto {acc_no}")),
                "belop_nok": amount,
                "andel_av_driftskost_pct": round((amount / total_opex) * 100, 2),
                "andel_av_inntekt_pct": round((amount / revenue) * 100, 2) if revenue > 0 else 0.0,
                "antall_posteringer_hb": int(hb_counts.get(acc_no, 0)),
            }
        )
    return drivers


def generate_profitability_recommendations(
    metrics: Dict[str, Any],
    cost_drivers: Optional[List[Dict[str, Any]]] = None,
) -> List[Dict[str, Any]]:
    """
    DETERMINISTISK LØNNSOMHETSMOTOR (Prescriptive Analytics uten slidere):
    Evaluerer selskapets nøkkeltall mot norske SMB-normer og beregner eksakte,
    etterprøvbare forbedringspotensialer i NOK. Disse vises i UI/PDF/HTML og
    sendes som ferdigkalkulerte fakta over The AI Firewall til KI-CFO.
    """
    recs: List[Dict[str, Any]] = []
    drivers = cost_drivers or []

    inntekter = float(metrics.get("driftsinntekter", 0.0))
    varekostnad = float(metrics.get("varekostnad", 0.0))
    lonnskostnad = float(metrics.get("lonnskostnad", 0.0))
    andre_opex = float(metrics.get("andre_driftskostnader", 0.0))
    kundefordringer = float(metrics.get("kundefordringer", 0.0))
    bankinnskudd = float(metrics.get("bankinnskudd", 0.0))
    kortsiktig_gjeld = float(metrics.get("kortsiktig_gjeld", metrics.get("leverandorgjeld", 0.0)))
    lg1 = float(metrics.get("likviditetsgrad_1", 0.0))
    ek_andel = float(metrics.get("egenkapitalandel", 0.0))

    # 1. Arbeidskapital & Kundefordringsbinding (Norm: <= 20 % av periodens omsetning)
    if inntekter > 0 and kundefordringer > 0:
        fordring_andel_pct = round((kundefordringer / inntekter) * 100, 1)
        target_receivables = inntekter * 0.20
        if kundefordringer > target_receivables:
            freed_cash = round(kundefordringer - target_receivables, 0)
            recs.append(
                {
                    "id": "ARBEIDSKAPITAL_FORDRINGER",
                    "kategori": "Arbeidskapital & Likviditet",
                    "prioritet": "Høy" if fordring_andel_pct >= 35.0 else "Medium",
                    "tittel": "Reduser kapitalbinding i kundefordringer",
                    "utlosende_indikator": f"Kundefordringer utgjør {fordring_andel_pct:.1f} % av driftsinntektene (norm ≤ 20,0 %).",
                    "anbefaling": "Stram inn betalingsbetingelser (f.eks. 14 dagers forfall) og automatiser purrerutiner.",
                    "mal_kpi": "Arbeidskapital / Banklikviditet",
                    "beregnet_effekt_nok": freed_cash,
                    "effekt_beskrivelse": f"Frigjør {freed_cash:,.0f} NOK i kontanter ved normalisering til 20 % fordringsandel.".replace(",", " "),
                }
            )

    # 2. Varekostnad & Bruttomarginoptimalisering (5 % innkjøps-/prisforbedring)
    if varekostnad > 0:
        cogs_saving = round(varekostnad * 0.05, 0)
        new_ebit = float(metrics.get("ebit", 0.0)) + cogs_saving
        new_margin = round((new_ebit / inntekter) * 100, 1) if inntekter > 0 else 0.0
        recs.append(
            {
                "id": "BRUTTOMARGIN_VAREKOST",
                "kategori": "Bruttomargin & Innkjøp",
                "prioritet": "Høy" if float(metrics.get("bruttomargin", 0.0)) < 45.0 else "Medium",
                "tittel": "Optimaliser innkjøpsbetingelser og varekostnad (Konto 4xxx)",
                "utlosende_indikator": f"Varekostnad er {varekostnad:,.0f} NOK (bruttomargin {float(metrics.get('bruttomargin', 0.0)):.1f} %).".replace(",", " "),
                "anbefaling": "Reforhandle leverandøravtaler på største varekjøpsposter eller juster utsalgspriser tilsvarende 5 % varekostnadsreduksjon.",
                "mal_kpi": "Driftsresultat (EBIT) & Bruttomargin",
                "beregnet_effekt_nok": cogs_saving,
                "effekt_beskrivelse": f"Øker EBIT direkte med {cogs_saving:,.0f} NOK (løfter driftsmargin til {new_margin:.1f} %).".replace(",", " "),
            }
        )

    # 3. Drifts- og lønnseffektivitet på største kostnadsdriver (klasse 5–7)
    opex_base = lonnskostnad + andre_opex
    if opex_base > 0:
        opex_saving = round(opex_base * 0.05, 0)
        top_opex_name = next(
            (f"{d['konto']} {d['kontonavn']}" for d in drivers if not str(d["konto"]).startswith("4")),
            "Lønn og faste driftskostnader (5xxx–7xxx)",
        )
        recs.append(
            {
                "id": "DRIFTSEFFEKTIVITET_OPEX",
                "kategori": "Kostnadseffektivitet",
                "prioritet": "Høy" if float(metrics.get("driftsmargin", 0.0)) < 15.0 else "Lav",
                "tittel": f"Effektiviser faste driftskostnader ({top_opex_name})",
                "utlosende_indikator": f"Lønn og øvrige driftskostnader utgjør {opex_base:,.0f} NOK ({float(metrics.get('lonnsandel', 0.0)):.1f} % lønnsandel).".replace(",", " "),
                "anbefaling": "Gjennomgå ressursutnyttelse og løpende avtaler på de største kostnadskontoene med mål om 5 % effektivisering.",
                "mal_kpi": "Driftsresultat (EBIT)",
                "beregnet_effekt_nok": opex_saving,
                "effekt_beskrivelse": f"Forbedrer EBIT med {opex_saving:,.0f} NOK uten behov for økt salgsvolum.".replace(",", " "),
            }
        )

    # 4. Likviditetsplassering eller likviditetsstyrking
    if kortsiktig_gjeld > 0 and lg1 < 2.0:
        needed_buffer = round(max(0.0, (2.0 * kortsiktig_gjeld) - float(metrics.get("omlopsmidler", 0.0))), 0)
        recs.append(
            {
                "id": "LIKVIDITETSVARSEL_LG1",
                "kategori": "Likviditetsrisiko",
                "prioritet": "Høy",
                "tittel": "Styrk kortsiktig betalingsevne (Likviditetsgrad 1 under norm)",
                "utlosende_indikator": f"Likviditetsgrad 1 er {lg1:.2f} (anbefalt SMB-norm ≥ 2,00).",
                "anbefaling": "Forleng leverandørkreditt eller frigjør omløpsmidler for å dekke kortsiktige forpliktelser.",
                "mal_kpi": "Likviditetsgrad 1",
                "beregnet_effekt_nok": needed_buffer,
                "effekt_beskrivelse": f"Krever {needed_buffer:,.0f} NOK i økt arbeidskapital for å nå normkravet på 2,0.".replace(",", " "),
            }
        )
    elif bankinnskudd > (kortsiktig_gjeld * 1.5) and bankinnskudd > 50000:
        excess_cash = round(bankinnskudd - (kortsiktig_gjeld * 1.5), 0)
        annual_interest = round(excess_cash * 0.045, 0)
        recs.append(
            {
                "id": "FINANSINNTEKT_PLASSERING",
                "kategori": "Kapitalavkastning (TKR/EKR)",
                "prioritet": "Lav",
                "tittel": "Plasser overskuddslikviditet på høyrentekonto",
                "utlosende_indikator": f"Bankinnskudd ({bankinnskudd:,.0f} NOK) overstiger 1,5x kortsiktig gjeld med god margin.".replace(",", " "),
                "anbefaling": f"Flytt {excess_cash:,.0f} NOK fra lavrente driftskonto til likvid plasseringskonto (4,5 % p.a.).".replace(",", " "),
                "mal_kpi": "Ordinært resultat & EKR",
                "beregnet_effekt_nok": annual_interest,
                "effekt_beskrivelse": f"Gir estimert {annual_interest:,.0f} NOK i årlig risikofri finansinntekt.".replace(",", " "),
            }
        )

    # 5. Soliditetsvurdering (Norm: Egenkapitalandel >= 30 %)
    if float(metrics.get("totalkapital_ub", 0.0)) > 0 and ek_andel < 30.0:
        target_eq = float(metrics.get("totalkapital_ub", 0.0)) * 0.30
        eq_gap = round(max(0.0, target_eq - float(metrics.get("reell_egenkapital_ub", 0.0))), 0)
        recs.append(
            {
                "id": "SOLIDITET_EK_ANDEL",
                "kategori": "Soliditet & Finansiell Risiko",
                "prioritet": "Høy",
                "tittel": "Styrk egenkapitalandelen gjennom tilbakeholdt overskudd",
                "utlosende_indikator": f"Egenkapitalandel er {ek_andel:.1f} % (anbefalt norm ≥ 30,0 %).",
                "anbefaling": "Unngå utbytteutdeling i perioden og hold tilbake overskudd for å styrke soliditeten.",
                "mal_kpi": "Egenkapitalandel (%)",
                "beregnet_effekt_nok": eq_gap,
                "effekt_beskrivelse": f"Styrker egenkapitalen med {eq_gap:,.0f} NOK opp til 30 %-terskelen.".replace(",", " "),
            }
        )

    return recs


def build_ns4102_income_statement(
    sb_df: pd.DataFrame,
    hb_df: Optional[pd.DataFrame] = None,
    metrics: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    DETERMINISTISK RESULTATOPPSTILLING ETTER NS 4102 (The AI Firewall):
    Bygger en hierarkisk resultatoppstilling (Income Statement) med hovedlinjer,
    underliggende kontospesifikasjoner fra Saldobalanse/Hovedbok, beløp i NOK og % av driftsinntekter.
    """
    from compliance_engine import calculate_detailed_financial_metrics

    m = metrics if metrics is not None else calculate_detailed_financial_metrics(sb_df)

    inntekter = float(m.get("driftsinntekter", 0.0))
    varekostnad = float(m.get("varekostnad", 0.0))
    bruttofortjeneste = float(m.get("bruttofortjeneste", inntekter - varekostnad))
    bruttomargin = float(m.get("bruttomargin", round((bruttofortjeneste / inntekter * 100), 2) if inntekter > 0 else 0.0))
    lonnskostnad = float(m.get("lonnskostnad", 0.0))
    andre_driftskostnader = float(m.get("andre_driftskostnader", 0.0))
    samlede_driftskostnader = float(
        m.get("samlede_driftskostnader", varekostnad + lonnskostnad + andre_driftskostnader)
    )
    ebit = float(m.get("ebit", inntekter - samlede_driftskostnader))
    driftsmargin = float(m.get("driftsmargin", round((ebit / inntekter * 100), 2) if inntekter > 0 else 0.0))

    varekost_pct = round((varekostnad / inntekter * 100), 1) if inntekter > 0 else 0.0
    lonn_pct = round((lonnskostnad / inntekter * 100), 1) if inntekter > 0 else 0.0
    opex_pct = round((andre_driftskostnader / inntekter * 100), 1) if inntekter > 0 else 0.0
    sum_kost_pct = round((samlede_driftskostnader / inntekter * 100), 1) if inntekter > 0 else 0.0
    inntekt_pct = 100.0 if inntekter > 0 else 0.0

    df = sb_df.copy() if sb_df is not None else pd.DataFrame()
    if not df.empty and "Konto" in df.columns:
        df["Konto_str"] = df["Konto"].astype(str).str.split(".").str[0].str.strip()
        df["Debet_num"] = pd.to_numeric(df.get("Debet", 0.0), errors="coerce").fillna(0.0)
        df["Kredit_num"] = pd.to_numeric(df.get("Kredit", 0.0), errors="coerce").fillna(0.0)
    else:
        df["Konto_str"] = pd.Series(dtype=str)
        df["Debet_num"] = pd.Series(dtype=float)
        df["Kredit_num"] = pd.Series(dtype=float)

    hb_desc_map: Dict[str, str] = {}
    if hb_df is not None and not hb_df.empty and "Konto" in hb_df.columns and "Beskrivelse" in hb_df.columns:
        hb_temp = hb_df.copy()
        hb_temp["Konto_str"] = hb_temp["Konto"].astype(str).str.split(".").str[0].str.strip()
        for acc_no, grp in hb_temp.groupby("Konto_str"):
            descs = [str(x).strip() for x in grp["Beskrivelse"].dropna().tolist() if str(x).strip()]
            if descs:
                hb_desc_map[str(acc_no)] = descs[0]

    def _extract_sub_accounts(prefixes: tuple[str, ...], is_revenue: bool, default_spec: str) -> List[Dict[str, Any]]:
        if df.empty:
            return []
        sub_df = df[df["Konto_str"].str.startswith(prefixes)].copy()
        if sub_df.empty:
            return []
        sub_df = sub_df.sort_values(by="Konto_str")
        items: List[Dict[str, Any]] = []
        for _, row in sub_df.iterrows():
            acc = str(row["Konto_str"])
            name = str(row.get("Kontonavn", f"Konto {acc}")).strip() or f"Konto {acc}"
            if is_revenue:
                raw_amt = float(row["Kredit_num"])
                signed_amt = raw_amt
                spec = "Kreditsaldo i SB"
            else:
                raw_amt = float(row["Debet_num"])
                signed_amt = -raw_amt
                spec = hb_desc_map.get(acc, default_spec)
            pct = round((raw_amt / inntekter * 100), 1) if inntekter > 0 else 0.0
            items.append(
                {
                    "regnskapspost": f"• Konto {acc}: {name}",
                    "kontospesifikasjon": spec,
                    "belop_nok": signed_amt,
                    "andel_pct": pct,
                    "row_type": "sub_income" if is_revenue else "sub_cost",
                }
            )
        return items

    acc_3 = _extract_sub_accounts(("3",), is_revenue=True, default_spec="Kreditsaldo i SB")
    acc_4 = _extract_sub_accounts(("4",), is_revenue=False, default_spec="Varekjøp")
    acc_5 = _extract_sub_accounts(("5",), is_revenue=False, default_spec="Lønn til ansatte")
    acc_67 = _extract_sub_accounts(("6", "7"), is_revenue=False, default_spec="Driftskostnad")

    rows: List[Dict[str, Any]] = [
        {
            "regnskapspost": "1. Salgs- og driftsinntekter",
            "kontospesifikasjon": "Klasse 3 (Konto 3000-3999)",
            "belop_nok": inntekter,
            "andel_pct": inntekt_pct,
            "row_type": "main_income",
        },
        *acc_3,
        {
            "regnskapspost": "2. Varekostnad",
            "kontospesifikasjon": "Klasse 4 (Konto 4000-4999)",
            "belop_nok": -varekostnad,
            "andel_pct": varekost_pct,
            "row_type": "main_cost_1",
        },
        *acc_4,
        {
            "regnskapspost": "Bruttofortjeneste (Gross Profit)",
            "kontospesifikasjon": "Driftsinntekter - Varekostnad",
            "belop_nok": bruttofortjeneste,
            "andel_pct": round(bruttomargin, 1),
            "row_type": "subtotal_gross",
        },
        {
            "regnskapspost": "3. Lønnskostnader & personalkostnader",
            "kontospesifikasjon": "Klasse 5 (Konto 5000-5999)",
            "belop_nok": -lonnskostnad,
            "andel_pct": lonn_pct,
            "row_type": "main_cost_2",
        },
        *acc_5,
        {
            "regnskapspost": "4. Andre driftskostnader",
            "kontospesifikasjon": "Klasse 6 & 7 (Husleie, honorarer)",
            "belop_nok": -andre_driftskostnader,
            "andel_pct": opex_pct,
            "row_type": "main_cost_3",
        },
        *acc_67,
        {
            "regnskapspost": "Sum driftskostnader",
            "kontospesifikasjon": "Post 2 + 3 + 4",
            "belop_nok": -samlede_driftskostnader,
            "andel_pct": sum_kost_pct,
            "row_type": "subtotal_opex",
        },
        {
            "regnskapspost": "Driftsresultat (EBIT)",
            "kontospesifikasjon": "Driftsinntekter - Sum driftskostnader",
            "belop_nok": ebit,
            "andel_pct": round(driftsmargin, 1),
            "row_type": "result_ebit",
        },
    ]

    stmt_df = pd.DataFrame(rows).rename(
        columns={
            "regnskapspost": "Regnskapspost (NS 4102)",
            "kontospesifikasjon": "Kontospesifikasjon",
            "belop_nok": "Beløp (NOK)",
            "andel_pct": "% av Inntekt",
        }
    )

    return {
        "rows": rows,
        "dataframe": stmt_df,
        "driftsmargin": round(driftsmargin, 1),
    }


def evaluate_profitability_indicators(metrics: Dict[str, Any]) -> Dict[str, Any]:
    """
    DETERMINISTISK VURDERING AV LØNNSOMHETSINDIKATORER OG KOSTNADSSTRUKTUR (The AI Firewall):
    Beregner ferdige prosenter, fremdriftsverdier (0.0–1.0 for st.progress) og diagnostiske
    hjelpetekster for CFO-kortene under Resultatoppstillingen.
    """
    inntekter = float(metrics.get("driftsinntekter", 0.0))
    varekostnad = float(metrics.get("varekostnad", 0.0))
    lonnskostnad = float(metrics.get("lonnskostnad", 0.0))
    andre_opex = float(metrics.get("andre_driftskostnader", 0.0))
    ebit = float(metrics.get("ebit", 0.0))

    bruttomargin = round(float(metrics.get("bruttomargin", 0.0)), 1)
    driftsmargin = round(float(metrics.get("driftsmargin", 0.0)), 1)
    varekost_pct = round((varekostnad / inntekter * 100), 1) if inntekter > 0 else 0.0
    lonn_pct = round(float(metrics.get("lonnsandel", (lonnskostnad / inntekter * 100) if inntekter > 0 else 0.0)), 1)
    opex_pct = round(float(metrics.get("opex_andel", (andre_opex / inntekter * 100) if inntekter > 0 else 0.0)), 1)

    if bruttomargin >= 50.0:
        brutto_note = "God prisingsmakt"
    elif bruttomargin >= 30.0:
        brutto_note = "Moderat bruttomargin"
    else:
        brutto_note = "Presset bruttomargin"

    if driftsmargin >= 20.0:
        ebit_note = "Solid overskudd"
    elif driftsmargin >= 10.0:
        ebit_note = "Sunn drift"
    elif driftsmargin >= 0.0:
        ebit_note = "Positiv drift"
    else:
        ebit_note = "Driftsunderskudd"

    if lonn_pct <= 25.0:
        lonn_note = "Under 25 % måltall"
    elif lonn_pct <= 45.0:
        lonn_note = "Normalt kostnadsnivå"
    else:
        lonn_note = "Høy lønnsintensitet"

    if opex_pct <= 15.0:
        opex_note = "Lav fastkostnadsbase"
    elif opex_pct <= 25.0:
        opex_note = "Moderat fastkostnadsbase"
    else:
        opex_note = "Høy fastkostnadsbase"

    if driftsmargin >= 20.0:
        summary_level = "success"
        summary_text = (
            f"Med en EBIT-margin på **{driftsmargin:.1f} %** er selskapet i øverste kvartil "
            "blant norske SMB-virksomheter."
        )
    elif driftsmargin >= 10.0:
        summary_level = "info"
        summary_text = (
            f"Med en EBIT-margin på **{driftsmargin:.1f} %** leverer selskapet god lønnsomhet "
            "over bransjesnittet for norske SMB-virksomheter."
        )
    elif driftsmargin >= 0.0:
        summary_level = "info"
        summary_text = (
            f"Med en EBIT-margin på **{driftsmargin:.1f} %** går driften i pluss, men økt "
            "kostnadskontroll anbefales for å styrke resultatbufferen."
        )
    else:
        summary_level = "info"
        summary_text = (
            f"Med en EBIT-margin på **{driftsmargin:.1f} %** er driftsresultatet negativt. "
            "Tiltak på varekostnad og faste kostnader bør prioriteres."
        )

    def _clamp_progress(pct: float) -> float:
        return float(min(max(pct / 100.0, 0.0), 1.0))

    return {
        "cost_bars": [
            {
                "key": "varekostnad",
                "label": f"Varekostnad ({varekostnad:,.0f} NOK)".replace(",", " "),
                "belop_nok": varekostnad,
                "pct": varekost_pct,
                "progress": _clamp_progress(varekost_pct),
                "is_highlight": False,
            },
            {
                "key": "lonnskostnader",
                "label": f"Lønnskostnader ({lonnskostnad:,.0f} NOK)".replace(",", " "),
                "belop_nok": lonnskostnad,
                "pct": lonn_pct,
                "progress": _clamp_progress(lonn_pct),
                "is_highlight": False,
            },
            {
                "key": "andre_driftskostnader",
                "label": f"Andre driftskostnader ({andre_opex:,.0f} NOK)".replace(",", " "),
                "belop_nok": andre_opex,
                "pct": opex_pct,
                "progress": _clamp_progress(opex_pct),
                "is_highlight": False,
            },
            {
                "key": "ebit",
                "label": f"Gjenværende Driftsresultat / EBIT ({ebit:,.0f} NOK)".replace(",", " "),
                "belop_nok": ebit,
                "pct": driftsmargin,
                "progress": _clamp_progress(driftsmargin),
                "is_highlight": True,
            },
        ],
        "kpis": {
            "bruttomargin": {"title": "Bruttomargin", "pct": bruttomargin, "note": brutto_note, "highlight": False},
            "driftsmargin": {"title": "Driftsmargin (EBIT)", "pct": driftsmargin, "note": ebit_note, "highlight": True},
            "lonn_omsetning": {"title": "Lønn / Omsetning", "pct": lonn_pct, "note": lonn_note, "highlight": False},
            "opex_omsetning": {"title": "Opex / Omsetning", "pct": opex_pct, "note": opex_note, "highlight": False},
        },
        "summary_level": summary_level,
        "summary_text": summary_text,
    }


def calculate_ebit_driver_sensitivity(metrics: Dict[str, Any]) -> Dict[str, Any]:
    """
    DETERMINISTISK EBIT-DRIVER OG SENSITIVITETSANALYSE (The AI Firewall):
    Beregner eksakt kroneeffekt på bunnlinjen (EBIT) ved 1 % marginal forbedring i:
      1. Pris (Driftsinntekter +1 % ved uendret volum)
      2. Varekostnad (Konto 4xxx -1 %)
      3. Faste kostnader / Opex (Konto 5xxx–7xxx -1 %, eller 6xxx–7xxx dersom spesifisert)
    Returnerer ferdigkalkulerte beløp i NOK, ny EBIT-margin og en dynamisk, deterministisk innsiktstekst.
    """
    inntekter = float(metrics.get("driftsinntekter", 0.0))
    varekostnad = float(metrics.get("varekostnad", 0.0))
    lonnskostnad = float(metrics.get("lonnskostnad", 0.0))
    andre_opex = float(metrics.get("andre_driftskostnader", 0.0))
    ebit = float(metrics.get("ebit", 0.0))
    bruttomargin = round(float(metrics.get("bruttomargin", 0.0)), 1)
    driftsmargin = round(float(metrics.get("driftsmargin", 0.0)), 2)

    # Faste kostnader (Opex): Bruker andre_driftskostnader + lonnskostnad (samlede faste driftskostnader kl. 5-7)
    # slik at analysen alltid reflekterer selskapets faktiske fastkostnadsbase.
    faste_kostnader_base = lonnskostnad + andre_opex

    price_1pct_nok = round(inntekter * 0.01, 2)
    cogs_1pct_nok = round(varekostnad * 0.01, 2)
    opex_1pct_nok = round(faste_kostnader_base * 0.01, 2)
    lonn_1pct_nok = round(lonnskostnad * 0.01, 2)
    other_opex_1pct_nok = round(andre_opex * 0.01, 2)

    new_Revenue_price = inntekter * 1.01
    new_margin_price = round(((ebit + price_1pct_nok) / new_Revenue_price) * 100.0, 2) if new_Revenue_price > 0 else 0.0
    new_margin_cogs = round(((ebit + cogs_1pct_nok) / inntekter) * 100.0, 2) if inntekter > 0 else 0.0
    new_margin_opex = round(((ebit + opex_1pct_nok) / inntekter) * 100.0, 2) if inntekter > 0 else 0.0

    price_vs_opex_mult = round(price_1pct_nok / opex_1pct_nok, 1) if opex_1pct_nok > 0 else 0.0
    price_vs_cogs_mult = round(price_1pct_nok / cogs_1pct_nok, 1) if cogs_1pct_nok > 0 else 0.0

    if price_vs_opex_mult > 0 and price_vs_cogs_mult > 0:
        insight_text = (
            f"💡 **Operasjonell giring (CFO-innsikt):** For dette selskapet vil en prisøkning på **1 %** "
            f"(**+{price_1pct_nok:,.0f} NOK** rett på bunnlinjen) gi **{price_vs_opex_mult:.1f}x** større effekt på EBIT "
            f"enn et tilsvarende kutt på 1 % i faste kostnader (**+{opex_1pct_nok:,.0f} NOK**), og "
            f"**{price_vs_cogs_mult:.1f}x** større effekt enn 1 % reduksjon i varekostnad (**+{cogs_1pct_nok:,.0f} NOK**), "
            f"på grunn av den nåværende bruttomarginen på **{bruttomargin:.1f} %**."
        ).replace(",", " ")
    elif price_1pct_nok > 0:
        insight_text = (
            f"💡 **Operasjonell giring (CFO-innsikt):** En prisøkning på **1 %** øker EBIT direkte med "
            f"**+{price_1pct_nok:,.0f} NOK** ved uendret salgsvolum.".replace(",", " ")
        )
    else:
        insight_text = "💡 **Operasjonell giring:** Ingen driftsinntekter registrert i perioden for sensitivitetsberegning."

    return {
        "driftsinntekter": inntekter,
        "varekostnad": varekostnad,
        "faste_kostnader_base": faste_kostnader_base,
        "lonnskostnad": lonnskostnad,
        "andre_driftskostnader": andre_opex,
        "ebit": ebit,
        "driftsmargin": driftsmargin,
        "bruttomargin": bruttomargin,
        "price_1pct_nok": price_1pct_nok,
        "cogs_1pct_nok": cogs_1pct_nok,
        "opex_1pct_nok": opex_1pct_nok,
        "lonn_1pct_nok": lonn_1pct_nok,
        "other_opex_1pct_nok": other_opex_1pct_nok,
        "new_margin_price": new_margin_price,
        "new_margin_cogs": new_margin_cogs,
        "new_margin_opex": new_margin_opex,
        "price_vs_opex_mult": price_vs_opex_mult,
        "price_vs_cogs_mult": price_vs_cogs_mult,
        "insight_text": insight_text,
    }


def calculate_nace_driver_benchmarking(revenue_nok: float = 1_200_000.0) -> Dict[str, Any]:
    """
    DETERMINISTISK NACE DRIVER-BENCHMARKING & GAP-IDENTIFIKATOR (v2.0 Teaser):
    Sammenligner selskapets EBIT-drivere mot bransjesnittet (NACE 62.010), beregner
    differansen (gapet i prosentpoeng) med Pandas, og identifiserer algoritmisk
    driveren med størst ugunstig avvik og tilhørende EBIT-potensial i NOK.
    """
    # Konsistente bransje- og selskapstall:
    # Selskap: Bruttomargin 63,5 % (Varekostnad 36,5 %) - Lønn 34,0 % - Opex 17,5 % = 12,0 % EBIT-margin
    # Bransje: Bruttomargin 68,0 % (Varekostnad 32,0 %) - Lønn 42,5 % - Opex 19,5 % =  6,0 % EBIT-margin
    driver_rows = [
        {
            "key": "bruttomargin",
            "driver_label": "Bruttomargin vs. Bransje",
            "underlying_cost_label": "varekostnad",
            "company_pct": 63.5,
            "industry_pct": 68.0,
            "higher_is_better": True,
        },
        {
            "key": "lonn_omsetning",
            "driver_label": "Lønnskostnad/Omsetning vs. Bransje",
            "underlying_cost_label": "lønnskostnad",
            "company_pct": 34.0,
            "industry_pct": 42.5,
            "higher_is_better": False,
        },
        {
            "key": "opex_omsetning",
            "driver_label": "Opex/Omsetning vs. Bransje",
            "underlying_cost_label": "faste driftskostnader (Opex)",
            "company_pct": 17.5,
            "industry_pct": 19.5,
            "higher_is_better": False,
        },
    ]

    df = pd.DataFrame(driver_rows)
    df["diff_pp"] = (df["company_pct"] - df["industry_pct"]).round(1)

    # Ugunstig avvik i prosentpoeng (> 0 betyr at selskapet presterer svakere enn bransjesnittet)
    def _calc_unfavorable_gap(row: pd.Series) -> float:
        if bool(row["higher_is_better"]):
            return round(max(0.0, float(row["industry_pct"]) - float(row["company_pct"])), 1)
        return round(max(0.0, float(row["company_pct"]) - float(row["industry_pct"])), 1)

    df["unfavorable_gap_pp"] = df.apply(_calc_unfavorable_gap, axis=1)
    df["ebit_potential_nok"] = (revenue_nok * (df["unfavorable_gap_pp"] / 100.0)).round(0)

    # Identifiser driveren med størst ugunstig avvik
    worst_idx = int(df["unfavorable_gap_pp"].idxmax())
    worst_row = df.loc[worst_idx]
    gap_pp = float(worst_row["unfavorable_gap_pp"])
    potential_nok = float(worst_row["ebit_potential_nok"])
    cost_name = str(worst_row["underlying_cost_label"])

    gap_str = f"{gap_pp:.1f}".replace(".", ",")
    pot_str = f"{potential_nok:,.0f}".replace(",", " ")

    potential_banner_text = (
        f"🎯 Største forbedringspotensial: Din {cost_name} er {gap_str} prosentpoeng høyere enn "
        f"bransjesnittet. Ved å lukke dette gapet vil EBIT øke med {pot_str} NOK."
    )

    display_df = pd.DataFrame(
        {
            "EBIT-driver": df["driver_label"],
            "Selskap (%)": df["company_pct"].apply(lambda v: f"{v:.1f} %".replace(".", ",")),
            "Bransjesnitt NACE (%)": df["industry_pct"].apply(lambda v: f"{v:.1f} %".replace(".", ",")),
            "Avvik (prosentpoeng)": df["diff_pp"].apply(
                lambda v: f"{v:+.1f} %-poeng".replace(".", ",")
            ),
            "Ugunstig gap": df["unfavorable_gap_pp"].apply(
                lambda v: f"{v:.1f} %-poeng".replace(".", ",") if v > 0 else "0,0 %-poeng (Bedre enn snitt)"
            ),
            "EBIT-potensial (NOK)": df["ebit_potential_nok"].apply(
                lambda v: f"+{v:,.0f} NOK".replace(",", " ") if v > 0 else "—"
            ),
        }
    )

    return {
        "revenue_nok": revenue_nok,
        "drivers_df": df,
        "display_df": display_df,
        "largest_gap_driver": str(worst_row["driver_label"]),
        "largest_gap_cost_label": cost_name,
        "largest_gap_pp": gap_pp,
        "largest_gap_ebit_nok": potential_nok,
        "potential_banner_text": potential_banner_text,
    }

