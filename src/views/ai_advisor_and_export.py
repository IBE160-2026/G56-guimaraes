"""
Side 6: Deterministiske Lønnsomhetsråd, KI-CFO over The AI Firewall, og målgruppetilpasset Eksport
(Styrepakke for styret og Beslutningsrapport for ledelsen).
"""

import streamlit as st

from html_report import generate_management_html
from llm_integration import ManagementCommentary, generate_management_report
from pdf_generator import generate_management_pdf


def render_ai_advisor_and_export() -> None:
    ws = st.session_state.get("workspace", {})
    db = st.session_state.get("db_manager")

    st.title("💡 6. KI-Rådgiver & Eksport")
    st.markdown(
        "**The AI Firewall i praksis:** Python beregner faste forbedringspotensialer deterministisk ut fra regnskapsnormer, "
        "mens språkmodellen utdyper sammenhengene uten å regne på tallene selv."
    )

    if not (ws.get("sb_ok") and ws.get("hb_ok")):
        st.warning(
            "⚠️ Regnskapet må bestå balansekontrollen på **1. Opplasting & Kontroll** før lønnsomhetsråd og rapporter genereres."
        )
        return

    sb_mapped = ws["sb_mapped"]
    hb_df = ws["hb_df"]
    recon_result = ws["recon_result"]
    vat_compliance = ws.get("vat_compliance")
    ns4102_compliance = ws.get("ns4102_compliance")
    metrics = ws["metrics"]
    income_statement = ws.get("income_statement")
    profitability_indicators = ws.get("profitability_indicators")
    cost_drivers = ws.get("cost_drivers", [])
    recommendations = ws.get("recommendations", [])
    period_label = ws.get("period_label")
    company_name = ws.get("company_name", "Bedrift AS")
    use_mock_ai = ws.get("use_mock_ai", True)
    openai_api_key = ws.get("openai_api_key", "")
    run_id = ws.get("run_id")

    # Del 1: Deterministisk lønnsomhetsmotor (Python)
    st.header("📐 Steg A: Deterministisk Lønnsomhetsmotor (Beregnet i Python)")
    st.caption("Disse forbedringspotensialene er regnet ut 100 % regelbasert fra Saldobalanse og Hovedbok – helt uavhengig av KI.")

    if recommendations:
        rec_cols = st.columns(2)
        for idx, rec in enumerate(recommendations):
            prio = rec.get("prioritet", "Medium")
            p_color = "red" if prio == "Høy" else ("orange" if prio == "Medium" else "green")
            with rec_cols[idx % 2]:
                with st.container(border=True):
                    st.markdown(f"**:{p_color}[[{prio}]]** **{rec['tittel']}**  \n*{rec['kategori']} • Mål-KPI: {rec['mal_kpi']}*")
                    st.write(f"**Observasjon:** {rec['utlosende_indikator']}")
                    st.write(f"**Anbefalt grep:** {rec['anbefaling']}")
                    st.info(f"💰 **Beregnet potensial:** {rec['effekt_beskrivelse']}")
    else:
        st.success("Ingen normavvik utløst – selskapets marginer, likviditet og soliditet ligger godt innenfor målområdene.")

    st.markdown("---")
    st.header("🤖 Steg B: Strategisk & Operativ KI-Rådgiver (CFO-Agent)")

    if st.button("🚀 Generer Strategisk Ledelsesrapport (KI)", type="primary"):
        with st.status("🤖 CFO-Agent analyserer nøkkeltall og lønnsomhetsråd over The AI Firewall...", expanded=True) as status:
            try:
                st.write("🔒 Verifiserer deterministisk nøkkeltalls- og scenariopayload (ingen råtransaksjoner)...")
                report = generate_management_report(
                    sb_mapped,
                    recon_result=recon_result,
                    api_key=openai_api_key if not use_mock_ai else None,
                    mock_mode=use_mock_ai,
                    hb_df=hb_df,
                )
                st.write("✅ Strukturert `ManagementCommentary` validert mot Pydantic-skjema og kryssavstemming.")
                st.session_state["active_ai_report"] = report
                if db is not None and run_id is not None:
                    db.save_ai_insight(run_id, report, is_mock=use_mock_ai)
                    st.write(f"🗄️ KI-innsikt lagret til lokal SQLite-historikk (Kjøring #{run_id}).")
                status.update(label="✅ KI-analyse ferdigstilt!", state="complete", expanded=False)
            except Exception as e:
                status.update(label="❌ Feil under generering av rapport", state="error", expanded=True)
                st.error(f"Feil ved generering av rapport: {e}")

    report = st.session_state.get("active_ai_report")
    if isinstance(report, dict):
        report = ManagementCommentary(**report)
        st.session_state["active_ai_report"] = report

    if report is not None:
        st.markdown("### 🏆 Hovedkonklusjon")
        if not recon_result["is_reconciled"]:
            st.error(report.hovedkonklusjon)
        else:
            st.info(report.hovedkonklusjon)

        tab1, tab2, tab3, tab4 = st.tabs([
            "📊 Lønnsomhet & Marginer",
            "💧 Likviditet & Arbeidskapital",
            "🏛️ Soliditet & Rentabilitet (TKR/EKR)",
            "🛡️ Revisors Avstemmingsnotat",
        ])

        with tab1:
            with st.container(border=True):
                st.markdown(report.lonnsomhet_og_marginer)
        with tab2:
            with st.container(border=True):
                st.markdown(report.likviditet_og_arbeidskapital)
        with tab3:
            with st.container(border=True):
                st.markdown(report.soliditet_og_rentabilitet)
        with tab4:
            with st.container(border=True):
                st.markdown(report.revisors_avstemmingsnotat)

        st.markdown("---")
        col_ai1, col_ai2 = st.columns([1, 2])
        with col_ai1:
            st.markdown("### 🚩 Identifiserte Faresignaler")
            for avvik in report.potensielle_avvik:
                st.warning(f"• {avvik}")

        with col_ai2:
            st.markdown("### 🎯 Prioritert Handlingsplan (KI-CFO)")
            for tiltak in report.tiltaksliste:
                prio_color = "red" if tiltak.prioritet == "Høy" else ("orange" if tiltak.prioritet == "Medium" else "green")
                with st.container(border=True):
                    st.markdown(
                        f"**:{prio_color}[[{tiltak.prioritet}]]** **{tiltak.tiltak}**  \n"
                        f"*Begrunnelse:* {tiltak.begrunnelse}  \n"
                        f"*Forventet effekt:* {tiltak.forventet_effekt}"
                    )

    # Del 3: Dynamisk valg av Rapportprofil (Styrepakke vs. Beslutningsrapport)
    st.markdown("---")
    with st.container(border=True):
        st.subheader("📄 Steg C: Eksport av Rapporter (Styrepakke & Beslutningsrapport)")
        st.caption(
            "Velg hvilken rapportprofil som skal genereres basert på målgruppens informasjonsbehov. "
            "Alle rapporter genereres 100 % i minnet (`io.BytesIO`) uten eksterne avhengigheter."
        )

        chk_col1, chk_col2 = st.columns(2)
        with chk_col1:
            gen_styre = st.checkbox(
                "Generer Styrepakke (Strategisk)",
                value=True,
                key="chk_export_styre",
                help="For styret: Fokus på Executive Summary, hovedtall/soliditet, revisors compliance-avstemming, bransjeposisjonering (V2) og strategiske KI-råd.",
            )
        with chk_col2:
            gen_ledelse = st.checkbox(
                "Generer Beslutningsrapport (Operativ)",
                value=False,
                key="chk_export_ledelse",
                help="For daglig leder og CFO: Fokus på operativ oppsummering, detaljert NS 4102 resultatoppstilling, kostnadsdrivere (progress), MVA/avvik, operasjonell analyse (V2) og operative KI-råd.",
            )

        if report is None:
            st.info(
                "Trykk på **🚀 Generer Strategisk Ledelsesrapport (KI)** ovenfor for å produsere KI-analysen "
                "og aktivere nedlastingsknappene for valgt(e) rapportprofil(er)."
            )
        elif not gen_styre and not gen_ledelse:
            st.warning("⚠️ Kryss av for minst én rapportprofil ovenfor (Styrepakke eller Beslutningsrapport) for å vise nedlastingsknapper.")
        else:
            if gen_styre:
                with st.container(border=True):
                    st.markdown("#### 🏛️ Styrepakke (Strategisk – For Styret)")
                    st.caption(
                        "Innholdsprofil: Executive Summary • Hovedtall & Lønnsomhet (EBIT, Bruttomargin, Soliditet) • "
                        "Revisors avstemming (Compliance & NS 4102) • Bransjeposisjonering (V2-teaser) • Strategiske KI-råd."
                    )
                    html_styre_buf = generate_management_html(
                        company_name=company_name,
                        ai_report=report,
                        metrics=metrics,
                        recon_result=recon_result,
                        recommendations=recommendations,
                        report_type="styre",
                        sb_df=sb_mapped,
                        vat_compliance=vat_compliance,
                        ns4102_compliance=ns4102_compliance,
                        income_statement=income_statement,
                        cost_drivers=cost_drivers,
                        profitability_indicators=profitability_indicators,
                        period_label=period_label,
                    )
                    pdf_styre_buf = generate_management_pdf(
                        company_name=company_name,
                        ai_report=report,
                        ns4102_summary=metrics,
                        recon_result=recon_result,
                        recommendations=recommendations,
                        report_type="styre",
                    )
                    s_col1, s_col2 = st.columns(2)
                    with s_col1:
                        st.download_button(
                            label="📥 Last ned Styrepakke (HTML)",
                            data=html_styre_buf,
                            file_name="Styrepakke_Strategisk.html",
                            mime="text/html",
                            type="primary",
                            use_container_width=True,
                            key="dl_styrepakke_html",
                        )
                    with s_col2:
                        st.download_button(
                            label="📥 Last ned Styrepakke (PDF)",
                            data=pdf_styre_buf,
                            file_name="Styrepakke_Strategisk.pdf",
                            mime="application/pdf",
                            type="secondary",
                            use_container_width=True,
                            key="dl_styrepakke_pdf",
                        )

            if gen_ledelse:
                with st.container(border=True):
                    st.markdown("#### ⚙️ Beslutningsrapport (Operativ – For Ledelsen / CFO)")
                    st.caption(
                        "Innholdsprofil: Operativ Oppsummering • Detaljert Resultatoppstilling (NS 4102) • "
                        "Kostnadsdrivere (Varekostnad, Lønn, Opex med progress) • MVA & Avviksdetaljer • "
                        "Operasjonell Analyse (V2-teaser) • Operative KI-råd."
                    )
                    html_ledelse_buf = generate_management_html(
                        company_name=company_name,
                        ai_report=report,
                        metrics=metrics,
                        recon_result=recon_result,
                        recommendations=recommendations,
                        report_type="ledelse",
                        sb_df=sb_mapped,
                        vat_compliance=vat_compliance,
                        ns4102_compliance=ns4102_compliance,
                        income_statement=income_statement,
                        cost_drivers=cost_drivers,
                        profitability_indicators=profitability_indicators,
                        period_label=period_label,
                    )
                    pdf_ledelse_buf = generate_management_pdf(
                        company_name=company_name,
                        ai_report=report,
                        ns4102_summary=metrics,
                        recon_result=recon_result,
                        recommendations=recommendations,
                        report_type="ledelse",
                    )
                    l_col1, l_col2 = st.columns(2)
                    with l_col1:
                        st.download_button(
                            label="📥 Last ned Beslutningsrapport (HTML)",
                            data=html_ledelse_buf,
                            file_name="Beslutningsrapport_Operativ.html",
                            mime="text/html",
                            type="primary",
                            use_container_width=True,
                            key="dl_beslutningsrapport_html",
                        )
                    with l_col2:
                        st.download_button(
                            label="📥 Last ned Beslutningsrapport (PDF)",
                            data=pdf_ledelse_buf,
                            file_name="Beslutningsrapport_Operativ.pdf",
                            mime="application/pdf",
                            type="secondary",
                            use_container_width=True,
                            key="dl_beslutningsrapport_pdf",
                        )
