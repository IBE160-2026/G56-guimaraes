"""
Side 2: Revisors avstemming (ISA / Bokføringsloven / NS 4102).
Gjennomfører deterministiske revisjonskontroller på innleste datarammer for Hovedbok (HB) og Saldobalanse (SB)
fra st.session_state, samt presenterer kommende V2.0-revisjonshandlinger.
"""

import numpy as np
import pandas as pd
import streamlit as st

from compliance_engine import (
    evaluate_ns4102_compliance,
    evaluate_vat_compliance,
    reconcile_hb_with_sb,
    validate_balance,
)


def render_auditor_reconciliation() -> None:
    ws = st.session_state.get("workspace", {})
    sb_df = ws.get("sb_df") if ws.get("sb_df") is not None else st.session_state.get("sb_df")
    hb_df = ws.get("hb_df") if ws.get("hb_df") is not None else st.session_state.get("hb_df")

    st.title("🔎 2. Revisors avstemming")
    st.markdown(
        "Uavhengig revisjons- og etterlevelseskontroll av **Saldobalanse (SB)** og **Hovedbok (HB)**. "
        "Alle kontroller utføres 100 % deterministisk i Python/Pandas i tråd med *The AI Firewall*, "
        "Bokføringsloven, Merverdiavgiftsloven og Norsk Standard Kontoplan (**NS 4102**)."
    )

    if sb_df is None or hb_df is None:
        st.warning(
            "⚠️ Ingen aktive regnskapsrammer funnet i sesjonen. "
            "Gå til **📂 1. Opplasting & Kontroll** for å laste opp Saldobalanse og Hovedbok eller velge eksempeldata."
        )
        return

    # Hent eller beregn avstemmingsdata deterministisk fra datarammer i session_state
    sb_ok = ws.get("sb_ok")
    if sb_ok is None:
        try:
            sb_ok = validate_balance(sb_df, "Debet", "Kredit")
        except Exception:
            sb_ok = False

    hb_ok = ws.get("hb_ok")
    if hb_ok is None:
        try:
            hb_ok = validate_balance(hb_df, "Debet", "Kredit")
        except Exception:
            hb_ok = False

    recon_result = ws.get("recon_result")
    if recon_result is None:
        recon_result = reconcile_hb_with_sb(sb_df, hb_df)

    vat_res = ws.get("vat_compliance") or evaluate_vat_compliance(sb_df, hb_df)
    ns_res = ws.get("ns4102_compliance") or evaluate_ns4102_compliance(sb_df, hb_df)

    # -------------------------------------------------------------------------
    # SEKSJON A: Aktive systemkontroller (V1 - Funksjonelt)
    # -------------------------------------------------------------------------
    st.header("🛡️ Seksjon A: Aktive systemkontroller (V1)")

    # 1. Balansesjekk (HB vs SB)
    with st.container(border=True):
        st.subheader("⚖️ 1. Balansesjekk (HB vs. SB)")
        st.caption(
            "Kontrollerer at Saldobalansen går i null ($\\sum \\text{Debet} - \\sum \\text{Kredit} = 0$ og $\\sum \\text{UB} = 0$), "
            "samt at $\\text{Inngående Balanse (IB)} + \\text{Bevegelse i Hovedbok (HB)} = \\text{Utgående Balanse (UB)}$."
        )

        sb_debet = float(pd.to_numeric(sb_df["Debet"], errors="coerce").fillna(0.0).sum()) if "Debet" in sb_df.columns else 0.0
        sb_kredit = float(pd.to_numeric(sb_df["Kredit"], errors="coerce").fillna(0.0).sum()) if "Kredit" in sb_df.columns else 0.0
        sb_net_diff = round(sb_debet - sb_kredit, 2)
        sb_ub_sum = round(float(pd.to_numeric(sb_df["UB"], errors="coerce").fillna(0.0).sum()), 2) if "UB" in sb_df.columns else sb_net_diff
        sb_zero_ok = bool(sb_ok) and bool(np.isclose(sb_net_diff, 0.0, atol=0.01)) and bool(np.isclose(sb_ub_sum, 0.0, atol=0.01))

        hb_debet = float(pd.to_numeric(hb_df["Debet"], errors="coerce").fillna(0.0).sum()) if "Debet" in hb_df.columns else 0.0
        hb_kredit = float(pd.to_numeric(hb_df["Kredit"], errors="coerce").fillna(0.0).sum()) if "Kredit" in hb_df.columns else 0.0
        hb_net_diff = round(hb_debet - hb_kredit, 2)

        recon_table = recon_result["reconciliation_table"]
        max_abs_diff = round(float(recon_table["Avvik"].abs().max()), 2) if len(recon_table) > 0 else 0.0
        is_reconciled = bool(recon_result["is_reconciled"])
        disc_count = int(recon_result["discrepancy_count"])

        col_b1, col_b2, col_b3, col_b4 = st.columns(4)
        col_b1.metric(
            "Saldobalanse Netto (∑UB)",
            f"{sb_ub_sum:,.2f} NOK".replace(",", " "),
            delta="Går i null (Godkjent)" if sb_zero_ok else f"Differanse: {sb_net_diff:,.2f} NOK".replace(",", " "),
            delta_color="normal" if sb_zero_ok else "inverse",
            help=f"Debet: {sb_debet:,.2f} NOK | Kredit: {sb_kredit:,.2f} NOK".replace(",", " "),
        )
        col_b2.metric(
            "Hovedbok Netto (∑D − ∑K)",
            f"{hb_net_diff:,.2f} NOK".replace(",", " "),
            delta="Går i null (Godkjent)" if hb_ok else "Ubalanse i HB",
            delta_color="normal" if hb_ok else "inverse",
            help=f"Debet: {hb_debet:,.2f} NOK | Kredit: {hb_kredit:,.2f} NOK".replace(",", " "),
        )
        col_b3.metric(
            "Kryssavstemming (IB + HB = UB)",
            "0 avvik" if is_reconciled else f"{disc_count} kontoavvik",
            delta="100 % avstemt" if is_reconciled else "Avvik oppdaget",
            delta_color="normal" if is_reconciled else "inverse",
            help="Kontrollerer at IB + netto bevegelse i Hovedbok er lik bokført UB per konto.",
        )
        col_b4.metric(
            "Største Kontoavvik (|UB − Beregnet|)",
            f"{max_abs_diff:,.2f} NOK".replace(",", " "),
            delta="0,00 NOK differanse" if is_reconciled else "Krever revisjon",
            delta_color="normal" if is_reconciled else "inverse",
            help="Høyeste absolutte differanse mellom bokført UB i Saldobalansen og beregnet UB fra Hovedboken.",
        )

        if sb_zero_ok and hb_ok and is_reconciled:
            st.success(
                "✅ **Balansesjekk og kryssavstemming godkjent:** Summen av Saldobalansen går i null "
                f"($\\sum \\text{{Debet}} = \\sum \\text{{Kredit}} = {sb_debet:,.2f}\\text{{ NOK}}$), "
                "og $\\text{IB} + \\text{bevegelse i Hovedbok} = \\text{UB}$ på samtlige kontoer.".replace(",", " ")
            )
        else:
            if not sb_zero_ok:
                st.error(
                    f"❌ **Balansefeil i Saldobalanse:** Summen av Saldobalansen går ikke i null "
                    f"(Netto Debet − Kredit = {sb_net_diff:,.2f} NOK, Sum UB = {sb_ub_sum:,.2f} NOK).".replace(",", " ")
                )
            if not hb_ok:
                st.error(
                    f"❌ **Balansefeil i Hovedbok:** Debet minus Kredit i Hovedboken er {hb_net_diff:,.2f} NOK.".replace(",", " ")
                )
            if not is_reconciled:
                st.error(
                    f"❌ **Kryssavstemmingsavvik:** Inngående balanse + bevegelse i Hovedbok ≠ Utgående balanse på "
                    f"**{disc_count}** konto(er)."
                )
                st.dataframe(
                    recon_result["discrepancies"][["Konto", "Kontonavn", "IB", "Netto_HB", "Beregnet_UB", "UB", "Avvik"]],
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Konto": st.column_config.TextColumn("Konto"),
                        "Kontonavn": st.column_config.TextColumn("Kontonavn"),
                        "IB": st.column_config.NumberColumn("IB (NOK)", format="%.2f kr"),
                        "Netto_HB": st.column_config.NumberColumn("Bevegelse HB (NOK)", format="%.2f kr"),
                        "Beregnet_UB": st.column_config.NumberColumn("Beregnet UB (NOK)", format="%.2f kr"),
                        "UB": st.column_config.NumberColumn("UB i SB (NOK)", format="%.2f kr"),
                        "Avvik": st.column_config.NumberColumn("⚠️ Avvik (NOK)", format="%.2f kr"),
                    },
                )

    # 2. MVA-klassifisering på tvers av kontoer
    with st.container(border=True):
        st.subheader("🧾 2. MVA-klassifisering på tvers av kontoer")
        st.caption(
            "Kontrollerer logisk sammenheng mellom MVA-kontoer i **2700-serien**, salgsinntekter i **3000-serien** "
            "og varekjøp/driftskostnader (**4000/6000/7000-serien**) opp mot norsk MVA-lovgivning."
        )

        m1, m2, m3, m4 = st.columns(4)
        m1.metric(
            "Salgsinntekter (3000-serien)",
            f"{vat_res['taxable_sales_3000']:,.0f} NOK".replace(",", " "),
            help="Bokførte kreditposteringer på ordinære salgskontoer i 3000-serien.",
        )
        m2.metric(
            "Kostnadsgrunnlag (4xxx/6xxx/7xxx)",
            f"{vat_res['cost_base_4xxx_6xxx_7xxx']:,.0f} NOK".replace(",", " "),
            help="Varekostnad og andre driftskostnader som normalt utløser fradrag for inngående MVA.",
        )
        m3.metric(
            "Utgående MVA (270x)",
            f"{vat_res['outgoing_vat']:,.0f} NOK".replace(",", " "),
            delta=f"Eff. sats: {vat_res['effective_out_vat_pct']:.1f} %".replace(".", ","),
            delta_color="off",
            help="Bokført utgående merverdiavgift på konto 2700–2709.",
        )
        m4.metric(
            "Inngående MVA (271x)",
            f"{vat_res['incoming_vat']:,.0f} NOK".replace(",", " "),
            delta=f"{vat_res['vat_account_count']} MVA-konto(er) i SB",
            delta_color="off",
            help="Bokført inngående merverdiavgift på konto 2710–2719.",
        )

        if vat_res["status"] == "ok":
            st.success(f"✅ **MVA-samsvar bekreftet:** {vat_res['summary']}")
        elif vat_res["status"] == "warning":
            st.warning(f"⚠️ **Revisjonsmerknad – MVA-kontroll:** {vat_res['summary']}")
            for finding in vat_res["findings"]:
                st.write(f"• {finding}")
        else:
            st.error(f"❌ **Kritisk MVA-avvik:** {vat_res['summary']}")
            for finding in vat_res["findings"]:
                st.write(f"• {finding}")

        if not vat_res["account_summary_df"].empty:
            with st.expander("📋 Vis MVA-relevante kontoer og avgiftsklassifisering"):
                st.dataframe(
                    vat_res["account_summary_df"],
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Konto": st.column_config.TextColumn("Konto"),
                        "Kontonavn": st.column_config.TextColumn("Kontonavn"),
                        "MVA_Rolle": st.column_config.TextColumn("MVA-Klassifisering"),
                        "Debet": st.column_config.NumberColumn("Debet (NOK)", format="%.2f kr"),
                        "Kredit": st.column_config.NumberColumn("Kredit (NOK)", format="%.2f kr"),
                        "UB": st.column_config.NumberColumn("UB (NOK)", format="%.2f kr"),
                    },
                )

    # 3. Presentasjon og Regnskapsspråk (NS 4102)
    with st.container(border=True):
        st.subheader("🇳🇴 3. Presentasjon og Regnskapsspråk (NS 4102)")
        st.caption(
            "Evaluerer om kontoplanen følger **Norsk Standard Kontoplan (NS 4102)** med 4-sifret kontostruktur (1000–8999) "
            "og norsk regnskapsspråk (jf. Bokføringsloven og Regnskapsloven § 3-4)."
        )

        n1, n2, n3 = st.columns(3)
        n1.metric(
            "Kontonummer (NS 4102)",
            f"{ns_res['number_recognition_pct']:.1f} %".replace(".", ","),
            delta=f"{ns_res['valid_number_count']} av {ns_res['total_accounts']} gyldige",
            delta_color="normal" if ns_res["number_recognition_pct"] == 100.0 else "inverse",
        )
        n2.metric(
            "Kontonavn (Norsk språk)",
            f"{ns_res['name_recognition_pct']:.1f} %".replace(".", ","),
            delta=f"{ns_res['valid_name_count']} av {ns_res['total_accounts']} gjenkjent",
            delta_color="normal" if ns_res["name_recognition_pct"] == 100.0 else "inverse",
        )
        n3.metric(
            "Samlet gjenkjennelsesgrad",
            f"{ns_res['overall_recognition_pct']:.1f} %".replace(".", ","),
            delta="NS 4102 Godkjent" if ns_res["is_compliant"] else "Avvik i kontoplan",
            delta_color="normal" if ns_res["is_compliant"] else "inverse",
        )

        if ns_res["is_compliant"]:
            st.success(f"✅ **NS 4102 & Norsk regnskapsspråk godkjent:** {ns_res['summary']}")
        else:
            st.warning(f"⚠️ **Avvik i kontoplan / regnskapsspråk:** {ns_res['summary']}")
            for finding in ns_res["findings"]:
                st.write(f"• {finding}")

        with st.expander("📋 Vis detaljert NS 4102-verifisering per konto"):
            st.dataframe(
                ns_res["details_df"],
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Konto": st.column_config.TextColumn("Konto"),
                    "Kontonavn": st.column_config.TextColumn("Kontonavn"),
                    "NS4102_Kategori": st.column_config.TextColumn("NS 4102 Kontoklasse"),
                    "Nummer_OK": st.column_config.CheckboxColumn("Gyldig nr. (1000–8999)"),
                    "Sprak_OK": st.column_config.CheckboxColumn("Gyldig norsk navn"),
                    "Status": st.column_config.TextColumn("Revisjonsstatus"),
                },
            )

    # -------------------------------------------------------------------------
    # SEKSJON B: Fremtidige moduler (Teasere for V2.0)
    # -------------------------------------------------------------------------
    st.divider()
    st.subheader("Fremtidige revisjonshandlinger")

    teaser_col1, teaser_col2 = st.columns(2)

    with teaser_col1:
        with st.container(border=True):
            st.markdown("### 📄 Bilagstesting (V2)")
            st.markdown("**🚧 Under utvikling**")
            st.write(
                "Automatisk stikkprøveutvelgelse og OCR-krysskontroll av PDF-bilag opp mot bokførte transaksjoner."
            )
            st.button("Start bilagskontroll", disabled=True, key="btn_voucher_audit_v2")

    with teaser_col2:
        with st.container(border=True):
            st.markdown("### 🔐 Prosessgjennomgang (V2)")
            st.markdown("**🚧 Under utvikling**")
            st.write(
                "Kartlegging og LLM-drevet analyse av bedriftens interne rutiner, attestasjonshierarki og systemtilganger."
            )
            st.button("Analyser rutiner", disabled=True, key="btn_process_audit_v2")
