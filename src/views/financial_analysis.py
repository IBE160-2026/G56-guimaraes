"""
Side 2: Finansiell Analyse (Utvidet CFO KPI-pakke inkl. TKR/EKR & Soliditet) og Hovedbok-Utforsker (Drill-down).
"""

import pandas as pd
import streamlit as st

from ledger_analytics import get_account_drilldown, get_voucher_details


def render_financial_analysis() -> None:
    ws = st.session_state.get("workspace", {})
    st.title("📊 2. Finansiell Analyse & Hovedbok-Utforsker")
    st.markdown(
        "100 % deterministisk finansanalyse (**Lønnsomhet, Likviditet, Soliditet og Rentabilitet TKR/EKR**) "
        "kombinert med interaktiv drill-down i **Hovedboken (HB)** ned til enkeltkonto, løpende saldo og bilagsnivå."
    )

    if not (ws.get("sb_ok") and ws.get("hb_ok")):
        st.warning(
            "⚠️ Begge regnskapsfiler (SB og HB) må være lastet inn og bestå balansekontrollen "
            "($\\sum \\text{Debet} = \\sum \\text{Kredit}$) før finansielle nøkkeltall vises. "
            "Gå til **1. Opplasting & Kontroll**."
        )
        return

    metrics = ws["metrics"]
    sb_mapped = ws["sb_mapped"]
    hb_df = ws["hb_df"]
    cost_drivers = ws.get("cost_drivers", [])

    if not ws["recon_result"]["is_reconciled"]:
        st.warning(
            f"⚠️ **Merk:** Kryssavstemmingen har avdekket {ws['recon_result']['discrepancy_count']} uavstemt(e) konto(er) "
            "mellom Hovedbok og Saldobalanse. Inspiser kontoene i Hovedbok-utforskeren nedenfor."
        )

    tab_kpi, tab_hb = st.tabs([
        "📈 CFO Nøkkeltalls-Dashboard (KPI-er)",
        "📘 Hovedbok-Utforsker (Drill-down & Bilagsinspektør)",
    ])

    with tab_kpi:
        st.subheader("1. Lønnsomhet og Kostnadsstruktur")
        ebit_pos = metrics["ebit"] >= 0
        c1, c2, c3, c4 = st.columns(4)
        c1.metric(
            "Driftsinntekter",
            f"{metrics['driftsinntekter']:,.0f} NOK".replace(",", " "),
            help="Samlede salgs- og driftsinntekter (NS 4102 kontoklasse 3).",
        )
        c2.metric(
            "Bruttomargin",
            f"{metrics['bruttomargin']:.1f} %".replace(".", ","),
            delta=f"Bruttofortj.: {metrics['bruttofortjeneste']:,.0f} NOK".replace(",", " "),
            delta_color="off",
            help="Bruttofortjeneste (Inntekter minus Varekostnad 4xxx) i prosent av driftsinntekter.",
        )
        c3.metric(
            "Driftsresultat (EBIT)",
            f"{metrics['ebit']:,.0f} NOK".replace(",", " "),
            delta="Positiv drift" if ebit_pos else "Driftsunderskudd",
            delta_color="normal" if ebit_pos else "inverse",
            help="Driftsinntekter fratrukket samlede driftskostnader (klasse 4–7).",
        )
        c4.metric(
            "Driftsmargin (EBIT-%)",
            f"{metrics['driftsmargin']:.1f} %".replace(".", ","),
            delta=f"Lønnsandel: {metrics['lonnsandel']:.1f} %".replace(".", ","),
            delta_color="off",
            help="Driftsresultat i prosent av driftsinntekter.",
        )

        st.subheader("2. Likviditet og Arbeidskapital")
        lg1_ok = metrics["likviditetsgrad_1"] >= 2.0
        lg2_ok = metrics["likviditetsgrad_2"] >= 1.0
        ak_pos = metrics["arbeidskapital"] >= 0
        l1, l2, l3, l4 = st.columns(4)
        l1.metric(
            "Bankinnskudd (UB)",
            f"{metrics['bankinnskudd']:,.0f} NOK".replace(",", " "),
            help="Disponible likvider på bankkontoer (NS 4102 gruppe 19xx).",
        )
        l2.metric(
            "Arbeidskapital",
            f"{metrics['arbeidskapital']:,.0f} NOK".replace(",", " "),
            delta="Positiv buffer" if ak_pos else "Negativ buffer",
            delta_color="normal" if ak_pos else "inverse",
            help="Omløpsmidler (14xx–19xx) fratrukket kortsiktig gjeld (24xx–29xx).",
        )
        l3.metric(
            "Likviditetsgrad 1",
            f"{metrics['likviditetsgrad_1']:.2f}".replace(".", ","),
            delta="Sterk (≥ 2,0)" if lg1_ok else "Under norm (< 2,0)",
            delta_color="normal" if lg1_ok else "inverse",
            help="Omløpsmidler dividert på kortsiktig gjeld (anbefalt norm ≥ 2,0).",
        )
        l4.metric(
            "Likviditetsgrad 2",
            f"{metrics['likviditetsgrad_2']:.2f}".replace(".", ","),
            delta="Godkjent (≥ 1,0)" if lg2_ok else "Under norm (< 1,0)",
            delta_color="normal" if lg2_ok else "inverse",
            help="(Omløpsmidler minus Varelager 14xx) dividert på kortsiktig gjeld (norm ≥ 1,0).",
        )

        st.subheader("3. Soliditet og Rentabilitet (TKR / EKR)")
        ek_ok = metrics["egenkapitalandel"] >= 30.0
        gjeldsgrad_ok = metrics["gjeldsgrad"] <= 2.3
        s1, s2, s3, s4 = st.columns(4)
        s1.metric(
            "Egenkapitalandel (Soliditet)",
            f"{metrics['egenkapitalandel']:.1f} %".replace(".", ","),
            delta="Solid (≥ 30 %)" if ek_ok else "Lav (< 30 %)",
            delta_color="normal" if ek_ok else "inverse",
            help=(
                f"Reell utgående egenkapital ({metrics['reell_egenkapital_ub']:,.0f} NOK inkl. perioderesultat, "
                f"bokført 20xx: {metrics['bokfort_egenkapital_ub']:,.0f} NOK) i % av totalkapital ({metrics['totalkapital_ub']:,.0f} NOK)."
            ).replace(",", " "),
        )
        s2.metric(
            "Gjeldsgrad",
            f"{metrics['gjeldsgrad']:.2f}".replace(".", ","),
            delta="Sunn gjeldsgrad" if gjeldsgrad_ok else "Høy belåning",
            delta_color="normal" if gjeldsgrad_ok else "inverse",
            help="Total gjeld dividert på reell egenkapital.",
        )
        s3.metric(
            "Totalkapitalrentabilitet (TKR)",
            f"{metrics['totalkapitalrentabilitet']:.1f} %".replace(".", ","),
            delta=f"Snitt TK: {metrics['gjennomsnittlig_totalkapital']:,.0f} NOK".replace(",", " "),
            delta_color="off",
            help="(EBIT + Finansinntekter) i prosent av gjennomsnittlig totalkapital ((IB + UB) / 2) for perioden.",
        )
        s4.metric(
            "Egenkapitalrentabilitet (EKR)",
            f"{metrics['egenkapitalrentabilitet']:.1f} %".replace(".", ","),
            delta=f"Snitt EK: {metrics['gjennomsnittlig_egenkapital']:,.0f} NOK".replace(",", " "),
            delta_color="off",
            help="Ordinært resultat i prosent av gjennomsnittlig egenkapital ((IB + Reell UB) / 2) for perioden.",
        )

        st.markdown("---")
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            with st.container(border=True):
                st.markdown("#### 📊 Resultatstruktur (NOK)")
                chart_df = pd.DataFrame({
                    "Post": ["Driftsinntekter", "Varekostnad", "Lønn & Øvrig Opex", "EBIT"],
                    "Beløp (NOK)": [
                        float(metrics["driftsinntekter"]),
                        float(metrics["varekostnad"]),
                        float(metrics["lonnskostnad"] + metrics["andre_driftskostnader"]),
                        float(metrics["ebit"]),
                    ],
                }).set_index("Post")
                st.bar_chart(chart_df)

        with col_g2:
            with st.container(border=True):
                st.markdown("#### 🔥 Største Kostnadsdrivere (NS 4102 Klasse 4–7)")
                if cost_drivers:
                    drivers_df = pd.DataFrame(cost_drivers)
                    st.dataframe(
                        drivers_df,
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            "konto": st.column_config.TextColumn("Konto"),
                            "kontonavn": st.column_config.TextColumn("Kontonavn"),
                            "belop_nok": st.column_config.NumberColumn("Beløp (NOK)", format="%.0f kr"),
                            "andel_av_driftskost_pct": st.column_config.NumberColumn("Andel av kost.", format="%.1f %%"),
                            "andel_av_inntekt_pct": st.column_config.NumberColumn("Andel av innt.", format="%.1f %%"),
                            "antall_posteringer_hb": st.column_config.NumberColumn("HB-linjer"),
                        },
                    )
                else:
                    st.info("Ingen kostnadsposter i klasse 4–7 funnet.")

    with tab_hb:
        st.subheader("🔎 Filtrer Hovedbok og Kontobevegelser")

        db = st.session_state.get("db_manager")
        run_id = ws.get("run_id")

        # Hent unike kontoer og NS 4102-kategorier
        all_accounts = sorted(
            set(sb_mapped["Konto"].astype(str).str.strip().tolist())
            | set(hb_df["Konto"].astype(str).str.strip().tolist())
        )
        account_labels = {}
        for _, r in sb_mapped.iterrows():
            acc = str(r["Konto"]).strip()
            account_labels[acc] = f"{acc} – {r.get('Kontonavn', '')}"
        for acc in all_accounts:
            if acc not in account_labels:
                account_labels[acc] = f"{acc} – (Kun i Hovedbok)"

        ns_categories = ["Alle"] + sorted(sb_mapped["NS4102_Kategori"].dropna().unique().tolist())

        f1, f2, f3 = st.columns([1.2, 1.4, 1.4])
        with f1:
            selected_ns = st.selectbox("NS 4102 Kontoklasse:", ns_categories, index=0)
        with f2:
            account_options = ["Alle"] + all_accounts
            selected_acc = st.selectbox(
                "Velg konto for løpende saldo-drilldown:",
                account_options,
                format_func=lambda x: "Alle kontoer" if x == "Alle" else account_labels.get(x, x),
            )
        with f3:
            search_txt = st.text_input("Fritekstsøk (Beskrivelse / Bilagsnr / Kontonavn):", value="")

        if selected_acc != "Alle":
            drill = get_account_drilldown(hb_df, sb_mapped, selected_acc)
            with st.container(border=True):
                st.markdown(f"#### 📘 Kontokort: `{drill['account_no']}` – {drill['account_name']}")
                d1, d2, d3, d4, d5 = st.columns(5)
                d1.metric("Inngående Balanse (IB)", f"{drill['ib']:,.2f} kr".replace(",", " "))
                d2.metric("Netto HB-bevegelse", f"{drill['net_hb']:,.2f} kr".replace(",", " "))
                d3.metric("Beregnet UB (IB + HB)", f"{drill['calculated_ub']:,.2f} kr".replace(",", " "))
                d4.metric("Bokført UB i SB", f"{drill['ub_sb']:,.2f} kr".replace(",", " "))
                d5.metric(
                    "Avstemmingsavvik",
                    f"{drill['discrepancy']:,.2f} kr".replace(",", " "),
                    delta="Avstemt" if drill["is_reconciled"] else "AVVIK!",
                    delta_color="normal" if drill["is_reconciled"] else "inverse",
                )

        if db is not None and run_id is not None:
            ledger_view = db.query_ledger_transactions(
                run_id=run_id,
                account_no=selected_acc,
                ns4102_category=selected_ns,
                search_text=search_txt,
            )
        else:
            ledger_view = hb_df.copy()

        st.markdown(f"**Viser {len(ledger_view)} posteringer fra Hovedboken (med SQLite Window Function løpende saldo per konto):**")
        st.dataframe(
            ledger_view,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Bilagsnr": st.column_config.TextColumn("Bilagsnr"),
                "Dato": st.column_config.TextColumn("Dato"),
                "Konto": st.column_config.TextColumn("Konto"),
                "Kontonavn": st.column_config.TextColumn("Kontonavn"),
                "NS4102_Kategori": st.column_config.TextColumn("NS 4102"),
                "Beskrivelse": st.column_config.TextColumn("Beskrivelse"),
                "Debet": st.column_config.NumberColumn("Debet (NOK)", format="%.2f kr"),
                "Kredit": st.column_config.NumberColumn("Kredit (NOK)", format="%.2f kr"),
                "Netto": st.column_config.NumberColumn("Netto (NOK)", format="%.2f kr"),
                "Lopende_Saldo": st.column_config.NumberColumn("Løpende Saldo (NOK)", format="%.2f kr"),
            },
        )

        # Bilagsinspektør (Motkonto-visning)
        if "Bilagsnr" in hb_df.columns:
            vouchers = sorted(
                hb_df["Bilagsnr"].dropna().astype(str).str.strip().unique().tolist(),
                key=lambda x: (0, int(x)) if x.isdigit() else (1, x),
            )
            if vouchers:
                st.markdown("---")
                with st.container(border=True):
                    st.subheader("🧾 Bilagsinspektør (Kontroll av dobbelt bokføring per enkeltbilag)")
                    chosen_voucher = st.selectbox("Velg Bilagsnr for å se samtlige motposter:", vouchers)
                    v_info = get_voucher_details(hb_df, chosen_voucher)
                    if v_info["is_balanced"]:
                        st.success(
                            f"✅ Bilag #{v_info['voucher_no']} balanserer: "
                            f"Debet = {v_info['debit_sum']:,.2f} NOK | Kredit = {v_info['credit_sum']:,.2f} NOK".replace(",", " ")
                        )
                    else:
                        st.error(
                            f"❌ Bilag #{v_info['voucher_no']} er i ubalanse: "
                            f"Debet = {v_info['debit_sum']:,.2f} NOK vs. Kredit = {v_info['credit_sum']:,.2f} NOK".replace(",", " ")
                        )
                    st.dataframe(v_info["lines"], use_container_width=True, hide_index=True)
