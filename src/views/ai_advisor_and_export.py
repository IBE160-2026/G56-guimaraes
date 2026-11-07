"""
Side 3: Deterministiske Lønnsomhetsråd, KI-CFO over The AI Firewall, og PDF/HTML-eksport.
"""

import streamlit as st

from html_report import generate_management_html
from llm_integration import ManagementCommentary, generate_management_report
from pdf_generator import generate_management_pdf


def render_ai_advisor_and_export() -> None:
    ws = st.session_state.get("workspace", {})
    db = st.session_state.get("db_manager")

    st.title("💡 3. Lønnsomhetsråd, KI-Rådgiver & Eksport")
    st.markdown(
        "**The AI Firewall i praksis:** Python beregner faste forbedringspotensialer deterministisk ut fra regnskapsnormer, "
        "mens språkmodellen utdyper sammenhengene i et formelt styrenotat uten å regne på tallene selv."
    )

    if not (ws.get("sb_ok") and ws.get("hb_ok")):
        st.warning(
            "⚠️ Regnskapet må bestå balansekontrollen på **1. Opplasting & Kontroll** før lønnsomhetsråd og styrepakke genereres."
        )
        return

    sb_mapped = ws["sb_mapped"]
    hb_df = ws["hb_df"]
    recon_result = ws["recon_result"]
    metrics = ws["metrics"]
    recommendations = ws.get("recommendations", [])
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
    st.header("🤖 Steg B: Strategisk KI-Ledelsesrapport (CFO-Agent)")

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
                status.update(label="✅ Strategisk ledelsesrapport ferdigstilt!", state="complete", expanded=False)
            except Exception as e:
                status.update(label="❌ Feil under generering av rapport", state="error", expanded=True)
                st.error(f"Feil ved generering av rapport: {e}")

    report = st.session_state.get("active_ai_report")
    if isinstance(report, dict):
        report = ManagementCommentary(**report)
        st.session_state["active_ai_report"] = report

    if report is not None:
        st.markdown("### 🏆 Hovedkonklusjon til Styret")
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
            st.markdown("### 🎯 Strategisk Handlingsplan (KI-CFO)")
            for tiltak in report.tiltaksliste:
                prio_color = "red" if tiltak.prioritet == "Høy" else ("orange" if tiltak.prioritet == "Medium" else "green")
                with st.container(border=True):
                    st.markdown(
                        f"**:{prio_color}[[{tiltak.prioritet}]]** **{tiltak.tiltak}**  \n"
                        f"*Begrunnelse:* {tiltak.begrunnelse}  \n"
                        f"*Forventet effekt:* {tiltak.forventet_effekt}"
                    )

        st.markdown("---")
        with st.container(border=True):
            st.subheader("📄 Steg C: Eksport av Komplett Styrepakke (PDF & HTML)")
            st.caption(
                "Begge formater genereres 100 % i minnet (`io.BytesIO`) og inkluderer de nye CFO-nøkkeltallene "
                "(Soliditet, LG2, TKR, EKR), avstemmingsstatus, deterministiske lønnsomhetsråd og KI-kommentarer."
            )
            pdf_buffer = generate_management_pdf(
                company_name=company_name,
                ai_report=report,
                ns4102_summary=metrics,
                recon_result=recon_result,
                recommendations=recommendations,
            )
            html_buffer = generate_management_html(
                company_name=company_name,
                ai_report=report,
                metrics=metrics,
                recon_result=recon_result,
                recommendations=recommendations,
            )
            col_dl1, col_dl2 = st.columns(2)
            with col_dl1:
                st.download_button(
                    label="📥 Last ned Ledelsesrapport (PDF)",
                    data=pdf_buffer,
                    file_name="Styrepakke_Ledelsesrapport.pdf",
                    mime="application/pdf",
                    type="primary",
                    use_container_width=True,
                )
            with col_dl2:
                st.download_button(
                    label="📥 Last ned Styrepakke (HTML)",
                    data=html_buffer,
                    file_name="Styrepakke_Ledelsesrapport.html",
                    mime="text/html",
                    type="secondary",
                    use_container_width=True,
                )
    else:
        st.info("Trykk på **🚀 Generer Strategisk Ledelsesrapport (KI)** ovenfor for å produsere CFO-notatet og aktivere nedlasting av PDF/HTML-styrepakken.")
