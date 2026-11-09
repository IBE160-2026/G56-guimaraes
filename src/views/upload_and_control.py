"""
Side 1: Opplasting & Automatisk Internkontroll (Balansekontroll og Kryssavstemming).
"""

import io
import streamlit as st

from data_pipeline import process_csv_in_memory, process_excel_in_memory, validate_input


def render_upload_and_control() -> None:
    ws = st.session_state.get("workspace", {})
    activate_semicolon_cb = st.session_state.get("cb_activate_semicolon")
    reset_sample_cb = st.session_state.get("cb_reset_sample")

    st.title("📂 1. Opplasting & Automatisk Internkontroll")
    st.markdown(
        "Last opp **Saldobalanse (SB)** og **Hovedbok (HB)**, kontroller at $\\sum \\text{Debet} = \\sum \\text{Kredit}$, "
        "og verifiser kryssavstemmingen ($\\text{IB} + \\sum \\text{HB} = \\text{UB}$). "
        "Gyldige analyser lagres automatisk og deduplisert (SHA-256) i den lokale SQLite-databasen."
    )

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        st.button(
            "⚡ Last inn norsk semikolon-format (100 000,00)",
            on_click=activate_semicolon_cb,
            use_container_width=True,
        )
    with col_btn2:
        st.button(
            "🔄 Nullstill til eksempeldata",
            on_click=reset_sample_cb,
            use_container_width=True,
        )

    status_banner = ws.get("source_banner")
    if status_banner:
        level, msg = status_banner
        if level == "info":
            st.info(msg)
        elif level == "warning":
            st.warning(msg)

    # Rad 1 i 2x2-rutenettet: Aktive moduler (SB og HB)
    grid_row1_col1, grid_row1_col2 = st.columns(2)

    with grid_row1_col1:
        with st.container(border=True):
            st.subheader("📊 1. Saldobalanse (SB)")
            uploaded_sb = st.file_uploader(
                "Dra og slipp Saldobalanse her, eller klikk for å velge fil (Konto, IB, Debet, Kredit, UB)",
                type=["csv", "xlsx"],
                key="sb_upload",
            )
            if uploaded_sb is not None:
                sb_token = (uploaded_sb.name, uploaded_sb.size)
                if sb_token != st.session_state.get("ignored_sb_token"):
                    st.session_state.pop("ignored_sb_token", None)
                    last_saved_sb = st.session_state.get("persisted_custom_sb_token")
                    if sb_token != last_saved_sb:
                        try:
                            file_bytes = io.BytesIO(uploaded_sb.getvalue())
                            parsed_sb = (
                                process_csv_in_memory(file_bytes, uploaded_sb.name)
                                if uploaded_sb.name.endswith(".csv")
                                else list(process_excel_in_memory(file_bytes, uploaded_sb.name).values())[0]
                            )
                            validate_input(parsed_sb, expected_type="SB")
                            st.session_state["persisted_custom_sb"] = (uploaded_sb.name, parsed_sb)
                            st.session_state["persisted_custom_sb_token"] = sb_token
                            st.session_state["demo_mode_radio"] = "Last opp egne filer (CSV / Excel)"
                            st.session_state["quick_semicolon_mode"] = False
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Feil ved lasting av Saldobalanse: {e}")

            sb_df = ws.get("sb_df")
            sb_source_name = ws.get("sb_source_name")
            if sb_df is not None and sb_source_name:
                st.caption(f"Aktiv kilde: **{sb_source_name}** ({len(sb_df)} kontoer)")
            else:
                st.caption("Aktiv kilde: Ingen fil lastet inn (0 kontoer)")

    with grid_row1_col2:
        with st.container(border=True):
            st.subheader("📘 2. Hovedbok (HB)")
            uploaded_hb = st.file_uploader(
                "Dra og slipp Hovedbok her, eller klikk for å velge fil (Bilagsnr, Dato, Konto, Debet, Kredit)",
                type=["csv", "xlsx"],
                key="hb_upload",
            )
            if uploaded_hb is not None:
                hb_token = (uploaded_hb.name, uploaded_hb.size)
                if hb_token != st.session_state.get("ignored_hb_token"):
                    st.session_state.pop("ignored_hb_token", None)
                    last_saved_hb = st.session_state.get("persisted_custom_hb_token")
                    if hb_token != last_saved_hb:
                        try:
                            file_bytes = io.BytesIO(uploaded_hb.getvalue())
                            parsed_hb = (
                                process_csv_in_memory(file_bytes, uploaded_hb.name)
                                if uploaded_hb.name.endswith(".csv")
                                else list(process_excel_in_memory(file_bytes, uploaded_hb.name).values())[0]
                            )
                            validate_input(parsed_hb, expected_type="HB")
                            st.session_state["persisted_custom_hb"] = (uploaded_hb.name, parsed_hb)
                            st.session_state["persisted_custom_hb_token"] = hb_token
                            st.session_state["demo_mode_radio"] = "Last opp egne filer (CSV / Excel)"
                            st.session_state["quick_semicolon_mode"] = False
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Feil ved lasting av Hovedbok: {e}")

            hb_df = ws.get("hb_df")
            hb_source_name = ws.get("hb_source_name")
            if hb_df is not None and hb_source_name:
                st.caption(f"Aktiv kilde: **{hb_source_name}** ({len(hb_df)} transaksjoner)")
            else:
                st.caption("Aktiv kilde: Ingen fil lastet inn (0 transaksjoner)")

    # Rad 2 i 2x2-rutenettet: Planlagte fremtidige datakilder
    grid_row2_col1, grid_row2_col2 = st.columns(2)
    with grid_row2_col1:
        with st.container(border=True):
            st.subheader("🤝 3. CRM & Kundereskontro")
            st.markdown("**🚧 Fremtidig utvidelse – Ikke aktivert**")
            st.write("Kryssanalyse av kundeinnbetalinger, kredittid og ordrepipeline mot konto 1500 Kundefordringer og 3000 Salgsinntekter.")
            st.button("🔒 Ikke tilgjengelig (Planlagt i v3.0)", disabled=True, use_container_width=True, key="crm_locked_btn")
            st.caption("Status: Avgrenset til kjerneflyt (SB + HB + SQLite-historikk)")

    with grid_row2_col2:
        with st.container(border=True):
            st.subheader("📦 4. Lagerdata & Vareflyt")
            st.markdown("**🚧 Fremtidig utvidelse – Ikke aktivert**")
            st.write("Avstemming av fysisk varelager, omløpshastighet og ukurans mot konto 1400 Varelager og 4000 Varekostnad.")
            st.button("🔒 Ikke tilgjengelig (Planlagt i v3.0)", disabled=True, use_container_width=True, key="inventory_locked_btn")
            st.caption("Status: Avgrenset til kjerneflyt (SB + HB + SQLite-historikk)")

    sb_df = ws.get("sb_df")
    hb_df = ws.get("hb_df")
    if sb_df is None or hb_df is None:
        st.info("Vennligst last opp både Saldobalanse og Hovedbok, eller velg eksempeldata i sidepanelet til venstre.")
        return

    st.markdown("---")
    st.header("🔍 Steg 1: Automatisk Internkontroll & Kryssavstemming")

    col_check1, col_check2 = st.columns(2)
    with col_check1:
        with st.container(border=True):
            st.subheader("Balansekontroll: Saldobalanse")
            if ws.get("sb_ok"):
                st.success("✅ Godkjent: Debet = Kredit i saldobalansen")
            else:
                st.error(f"❌ {ws.get('sb_error', 'Ubalanse i saldobalansen')}")

    with col_check2:
        with st.container(border=True):
            st.subheader("Balansekontroll: Hovedbok")
            if ws.get("hb_ok"):
                st.success("✅ Godkjent: Debet = Kredit i hovedboken")
            else:
                st.error(f"❌ {ws.get('hb_error', 'Ubalanse i hovedboken')}")

    recon_result = ws.get("recon_result")
    with st.container(border=True):
        st.markdown("### ⚖️ Kryssavstemming: Hovedbok mot Saldobalanse")
        st.caption("Matematisk formel: $\\text{Inngående Balanse (IB)} + \\sum (\\text{Transaksjoner i HB}) = \\text{Utgående Balanse (UB i SB)}$ per konto.")
        if recon_result is None:
            st.error(f"Kunne ikke gjennomføre kryssavstemming: {ws.get('recon_error', 'Ukjent feil')}")
        elif recon_result["is_reconciled"]:
            st.success("✅ **Full konsistens:** Alle transaksjoner i hovedboken summerer seg nøyaktig til UB i saldobalansen (0 avvik).")
        else:
            st.error(f"❌ **Avstemmingsavvik funnet:** Systemet har avdekket {recon_result['discrepancy_count']} uavstemt(e) konto(er)!")
            st.dataframe(
                recon_result["discrepancies"][["Konto", "Kontonavn", "IB", "Netto_HB", "Beregnet_UB", "UB", "Avvik"]],
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Konto": st.column_config.TextColumn("Konto"),
                    "Kontonavn": st.column_config.TextColumn("Kontonavn"),
                    "IB": st.column_config.NumberColumn("IB (NOK)", format="%.2f kr"),
                    "Netto_HB": st.column_config.NumberColumn("Netto HB (NOK)", format="%.2f kr"),
                    "Beregnet_UB": st.column_config.NumberColumn("Beregnet UB (NOK)", format="%.2f kr"),
                    "UB": st.column_config.NumberColumn("UB i SB (NOK)", format="%.2f kr"),
                    "Avvik": st.column_config.NumberColumn("⚠️ Avvik (NOK)", format="%.2f kr"),
                },
            )
            st.warning("⚠️ **Revisjonsadvarsel:** Avvik oppdaget. KI-ledelsesrapporten vil reflektere disse uoverensstemmelsene og varsle styret.")

    run_id = ws.get("run_id")
    if run_id is not None:
        st.caption(
            f"🗄️ **SQLite Auto-Sync:** Analysen er synkronisert til lokal database som **Kjøring #{run_id}** "
            f"(Periode: `{ws.get('period_label', 'Ukjent')}`, Selskap: `{ws.get('company_name', '')}`). "
            "Bruk menyen til venstre for å gå videre til **🔎 2. Revisors avstemming**, **📊 3. Finansiell Analyse & HB** eller **💡 7. KI-Rådgiver & Eksport**."
        )

    sb_mapped = ws.get("sb_mapped")
    if sb_mapped is not None:
        with st.expander("📋 Vis fullstendig Saldobalanse og NS 4102-kategorisering"):
            st.dataframe(
                sb_mapped,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Konto": st.column_config.TextColumn("Konto"),
                    "Debet": st.column_config.NumberColumn("Debet (NOK)", format="%.2f kr"),
                    "Kredit": st.column_config.NumberColumn("Kredit (NOK)", format="%.2f kr"),
                    "IB": st.column_config.NumberColumn("IB (NOK)", format="%.2f kr"),
                    "UB": st.column_config.NumberColumn("UB (NOK)", format="%.2f kr"),
                },
            )
