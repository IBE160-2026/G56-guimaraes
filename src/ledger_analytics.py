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
