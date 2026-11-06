import streamlit as st
import pandas as pd
import io
import os
from app_logging import setup_app_logging
from data_pipeline import process_csv_in_memory, process_excel_in_memory, validate_input
from compliance_engine import (
    validate_balance,
    map_to_ns4102,
    reconcile_hb_with_sb,
    calculate_detailed_financial_metrics,
)
from llm_integration import generate_management_report
from pdf_generator import generate_management_pdf
from html_report import generate_management_html

logger = setup_app_logging()

def check_env_security():
    """Varsler hvis sensitiv .env-fil utilsiktet er opprettet uten .gitignore-beskyttelse."""
    if os.path.exists(".env"):
        logger.warning(".env fil detektert. Verifiserer at den er ignorert av Git.")

check_env_security()

st.set_page_config(page_title="Ledelsesrapport & Regnskapskontroll (KI)", layout="wide", page_icon="📊")

st.title("📊 Ledelsesrapport og Regnskapskontroll med KI")
st.markdown(
    "Automatisert avstemming mellom **Saldobalanse (SB)** og **Hovedbok (HB)**, "
    "mapping til **NS 4102**, og dyp KI-generert ledelsesrapport for styret."
)

# Sidebar for innstillinger og hurtiglasting
def on_demo_mode_change():
    st.session_state["quick_semicolon_mode"] = False

with st.sidebar:
    st.header("⚙️ Konfigurasjon & Sensormodus")
    company_name = st.text_input("Selskapsnavn:", value="Bedrift AS")
    demo_mode = st.radio(
        "Velg datakilde:",
        [
            "Bruk eksempeldata (Balansert - Grønn sti)",
            "Bruk eksempeldata (Med avvik - Rød sti)",
            "Last opp egne filer (CSV / Excel)"
        ],
        index=0,  # Standard: Balansert eksempeldata for umiddelbar sensor-visning
        key="demo_mode_radio",
        on_change=on_demo_mode_change,
    )
    
    st.markdown("---")
    st.subheader("🤖 KI-innstillinger")
    use_mock_ai = st.checkbox(
        "Bruk testmodus (Mock KI)", 
        value=True, 
        help="Aktiver for å kjøre 100 % lokalt og deterministisk uten OpenAI API-nøkkel (Sensor-vennlig)."
    )
    openai_api_key = ""
    if not use_mock_ai:
        openai_api_key = st.text_input("OpenAI API-nøkkel:", type="password")

    st.markdown("---")
    st.markdown("### ℹ️ Om Løsningen")
    st.caption(
        "**Utviklings-KI:** Utviklet utelukkende med Google Gemini Antigravity (AiDD/BMAD).\n\n"
        "**The AI Firewall:** Koden regner deterministisk i Pandas, KI forklarer via Pydantic Structured Outputs."
    )

sb_df = None
hb_df = None
sb_source_name = None
hb_source_name = None

sample_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../data/sample'))

def activate_semicolon_demo():
    st.session_state["quick_semicolon_mode"] = True
    if st.session_state.get("sb_upload") is not None:
        f = st.session_state["sb_upload"]
        st.session_state["ignored_sb_token"] = (f.name, f.size)
    if st.session_state.get("hb_upload") is not None:
        f = st.session_state["hb_upload"]
        st.session_state["ignored_hb_token"] = (f.name, f.size)
    st.session_state.pop("sb_upload", None)
    st.session_state.pop("hb_upload", None)

def reset_to_sample_data():
    st.session_state["quick_semicolon_mode"] = False
    st.session_state["demo_mode_radio"] = "Bruk eksempeldata (Balansert - Grønn sti)"
    if st.session_state.get("sb_upload") is not None:
        f = st.session_state["sb_upload"]
        st.session_state["ignored_sb_token"] = (f.name, f.size)
    if st.session_state.get("hb_upload") is not None:
        f = st.session_state["hb_upload"]
        st.session_state["ignored_hb_token"] = (f.name, f.size)
    st.session_state.pop("sb_upload", None)
    st.session_state.pop("hb_upload", None)

# Toppseksjon: Alltid synlig 2x2 opplastingsrutenett
st.header("📂 Last opp Regnskapsfiler: Saldobalanse (SB) og Hovedbok (HB)")
st.caption("Dra og slipp dine egne filer her (.csv eller .xlsx), eller velg ferdige eksempeldatasett i menyen til venstre.")

col_btn1, col_btn2 = st.columns(2)
with col_btn1:
    st.button(
        "⚡ Last inn norsk semikolon-format (100 000,00)",
        on_click=activate_semicolon_demo,
        use_container_width=True,
    )
with col_btn2:
    st.button(
        "🔄 Nullstill til eksempeldata",
        on_click=reset_to_sample_data,
        use_container_width=True,
    )

# Grunninnlasting basert på valgt eksempelmodus eller hurtigknapp
if st.session_state.get("quick_semicolon_mode", False):
    st.info(
        "⚡ **Norsk semikolon-format aktivert:** Laster inn `saldobalanse_norsk_semikolon.csv` "
        "(med `;` og desimalkomma `100 000,00`) og `hovedbok_balansert.csv`."
    )
    semicolon_path = os.path.join(sample_dir, 'saldobalanse_norsk_semikolon.csv')
    with open(semicolon_path, 'rb') as f:
        sb_df = process_csv_in_memory(io.BytesIO(f.read()), 'saldobalanse_norsk_semikolon.csv')
    validate_input(sb_df, expected_type="SB")
    hb_df = pd.read_csv(os.path.join(sample_dir, 'hovedbok_balansert.csv'))
    sb_source_name = "saldobalanse_norsk_semikolon.csv"
    hb_source_name = "hovedbok_balansert.csv"
elif demo_mode == "Bruk eksempeldata (Balansert - Grønn sti)":
    st.info("💡 **Sensormodus:** Laster inn balanserte eksempeldata fra `data/sample/` (0 avvik).")
    sb_df = pd.read_csv(os.path.join(sample_dir, 'saldobalanse_balansert.csv'))
    hb_df = pd.read_csv(os.path.join(sample_dir, 'hovedbok_balansert.csv'))
    sb_source_name = "saldobalanse_balansert.csv"
    hb_source_name = "hovedbok_balansert.csv"
elif demo_mode == "Bruk eksempeldata (Med avvik - Rød sti)":
    st.warning("⚠️ **Sensormodus:** Laster inn eksempeldata med konstruerte avvik på konto 1500 og 1920.")
    sb_df = pd.read_csv(os.path.join(sample_dir, 'saldobalanse_balansert.csv'))
    hb_df = pd.read_csv(os.path.join(sample_dir, 'hovedbok_med_avvik.csv'))
    sb_source_name = "saldobalanse_balansert.csv"
    hb_source_name = "hovedbok_med_avvik.csv"

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
                try:
                    file_bytes = io.BytesIO(uploaded_sb.getvalue())
                    sb_df = (
                        process_csv_in_memory(file_bytes, uploaded_sb.name)
                        if uploaded_sb.name.endswith('.csv')
                        else list(process_excel_in_memory(file_bytes, uploaded_sb.name).values())[0]
                    )
                    validate_input(sb_df, expected_type="SB")
                    sb_source_name = uploaded_sb.name
                    st.success(f"✅ Lastet inn '{uploaded_sb.name}' ({len(sb_df)} kontoer)")
                except Exception as e:
                    st.error(f"❌ Feil ved lasting av Saldobalanse: {e}")
                    sb_df = None
                    sb_source_name = None

        if sb_df is not None and sb_source_name:
            st.caption(f"Aktiv kilde: {sb_source_name} ({len(sb_df)} kontoer)")
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
                try:
                    file_bytes = io.BytesIO(uploaded_hb.getvalue())
                    hb_df = (
                        process_csv_in_memory(file_bytes, uploaded_hb.name)
                        if uploaded_hb.name.endswith('.csv')
                        else list(process_excel_in_memory(file_bytes, uploaded_hb.name).values())[0]
                    )
                    validate_input(hb_df, expected_type="HB")
                    hb_source_name = uploaded_hb.name
                    st.success(f"✅ Lastet inn '{uploaded_hb.name}' ({len(hb_df)} transaksjoner)")
                except Exception as e:
                    st.error(f"❌ Feil ved lasting av Hovedbok: {e}")
                    hb_df = None
                    hb_source_name = None

        if hb_df is not None and hb_source_name:
            st.caption(f"Aktiv kilde: {hb_source_name} ({len(hb_df)} transaksjoner)")
        else:
            st.caption("Aktiv kilde: Ingen fil lastet inn (0 transaksjoner)")

# Rad 2 i 2x2-rutenettet: Låste fremtidige moduler (CRM og Lagerdata)
grid_row2_col1, grid_row2_col2 = st.columns(2)

with grid_row2_col1:
    with st.container(border=True):
        st.subheader("🤝 3. CRM & Kundereskontro")
        st.markdown("**🚧 Under utvikling – Ikke tilgjengelig**")
        st.write("Kryssanalyse av kundeinnbetalinger, kredittid og ordrepipeline mot konto 1500 Kundefordringer og 3000 Salgsinntekter.")
        st.button(
            "🔒 Ikke tilgjengelig (Planlagt i v2.0)",
            disabled=True,
            use_container_width=True,
            key="crm_locked_btn",
        )
        st.caption("Status: Under utvikling • Utelatt i v1 etter scoping til kjerneflyt (SB + HB)")

with grid_row2_col2:
    with st.container(border=True):
        st.subheader("📦 4. Lagerdata & Vareflyt")
        st.markdown("**🚧 Under utvikling – Ikke tilgjengelig**")
        st.write("Avstemming av fysisk varelager, omløpshastighet og ukurans mot konto 1400 Varelager og 4000 Varekostnad.")
        st.button(
            "🔒 Ikke tilgjengelig (Planlagt i v2.0)",
            disabled=True,
            use_container_width=True,
            key="inventory_locked_btn",
        )
        st.caption("Status: Under utvikling • Modulen er låst og ikke tilgjengelig i v1.0")

# Behandling når begge filer er tilgjengelige
if sb_df is not None and hb_df is not None:
    st.markdown("---")
    st.header("🔍 Steg 1: Automatisk Internkontroll & Avstemming")
    
    col_check1, col_check2 = st.columns(2)
    sb_ok = False
    hb_ok = False
    
    # 1. Balansekontroll Debet = Kredit
    with col_check1:
        with st.container(border=True):
            st.subheader("Balansekontroll: Saldobalanse")
            try:
                validate_balance(sb_df, 'Debet', 'Kredit')
                st.success("✅ Godkjent: Debet = Kredit i saldobalansen")
                sb_ok = True
            except Exception as e:
                st.error(f"❌ {e}")
            
    with col_check2:
        with st.container(border=True):
            st.subheader("Balansekontroll: Hovedbok")
            try:
                validate_balance(hb_df, 'Debet', 'Kredit')
                st.success("✅ Godkjent: Debet = Kredit i hovedboken")
                hb_ok = True
            except Exception as e:
                st.error(f"❌ {e}")
            
    # 2. Kryssavstemming (IB + HB = UB)
    with st.container(border=True):
        st.markdown("### ⚖️ Kryssavstemming: Hovedbok mot Saldobalanse")
        st.caption("Matematisk formel: $\\text{Inngående Balanse (IB)} + \\sum (\\text{Transaksjoner i HB}) = \\text{Utgående Balanse (UB i SB)}$ per konto.")
        try:
            recon_result = reconcile_hb_with_sb(sb_df, hb_df)
            if recon_result["is_reconciled"]:
                st.success("✅ **Full konsistens:** Alle transaksjoner i hovedboken summerer seg nøyaktig til UB i saldobalansen (0 avvik).")
            else:
                st.error(f"❌ **Avstemmingsavvik funnet:** Systemet har avdekket {recon_result['discrepancy_count']} uavstemt(e) konto(er)!")
                st.dataframe(
                    recon_result["discrepancies"][['Konto', 'Kontonavn', 'IB', 'Netto_HB', 'Beregnet_UB', 'UB', 'Avvik']],
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
                st.warning("⚠️ **Revisjonsadvarsel:** Avvik oppdaget. Ledelsesrapporten vil reflektere disse uoverensstemmelsene og varsle styret.")
        except Exception as e:
            st.error(f"Kunne ikke gjennomføre kryssavstemming: {e}")
            recon_result = None

    # Vis forhåndsvisning
    with st.expander("Vis data og NS 4102-kategorisering"):
        sb_mapped = sb_df.copy()
        if 'Konto' in sb_mapped.columns:
            sb_mapped['NS4102_Kategori'] = sb_mapped['Konto'].apply(map_to_ns4102)
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

    # Steg 2: Nøkkeltall og KI-analyse
    if sb_ok and hb_ok:
        st.markdown("---")
        st.header("📈 Steg 2: Nøkkeltall og Strategisk Ledelsessammendrag")
        
        sb_mapped = sb_df.copy()
        if 'Konto' in sb_mapped.columns:
            sb_mapped['NS4102_Kategori'] = sb_mapped['Konto'].apply(map_to_ns4102)
            
        # Deterministisk nøkkeltallsberegning via felles motor
        metrics = calculate_detailed_financial_metrics(sb_mapped)
        
        ebit_positive = metrics["ebit"] >= 0
        likv_ok = metrics["likviditetsgrad_1"] >= 2.0
        ak_positive = metrics["arbeidskapital"] >= 0

        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        col_m1.metric(
            "Driftsinntekter",
            f"{metrics['driftsinntekter']:,.0f} NOK",
            help="Samlede salgs- og driftsinntekter (NS 4102 kontoklasse 3).",
        )
        col_m2.metric(
            "Driftskostnader",
            f"{metrics['samlede_driftskostnader']:,.0f} NOK",
            help="Sum varekostnad, lønnskostnad og andre driftskostnader (NS 4102 kontoklasse 4–7).",
        )
        col_m3.metric(
            "Driftsresultat (EBIT)",
            f"{metrics['ebit']:,.0f} NOK",
            delta="Positiv drift" if ebit_positive else "Driftsunderskudd",
            delta_color="normal" if ebit_positive else "inverse",
            help="Driftsinntekter fratrukket samlede driftskostnader.",
        )
        col_m4.metric(
            "Driftsmargin",
            f"{metrics['driftsmargin']:.1f} %",
            delta=f"Bruttomargin: {metrics['bruttomargin']:.1f} %",
            delta_color="off",
            help="Driftsresultat (EBIT) i prosent av driftsinntekter.",
        )

        col_m5, col_m6, col_m7, col_m8 = st.columns(4)
        col_m5.metric(
            "Bruttofortjeneste",
            f"{metrics['bruttofortjeneste']:,.0f} NOK",
            help="Driftsinntekter fratrukket varekostnad (kontoklasse 3 minus 4).",
        )
        col_m6.metric(
            "Bruttomargin",
            f"{metrics['bruttomargin']:.1f} %",
            help="Bruttofortjeneste i prosent av driftsinntekter.",
        )
        col_m7.metric(
            "Arbeidskapital",
            f"{metrics['arbeidskapital']:,.0f} NOK",
            delta="Positiv buffer" if ak_positive else "Negativ buffer",
            delta_color="normal" if ak_positive else "inverse",
            help="Omløpsmidler (bank + kundefordringer) minus kortsiktig gjeld.",
        )
        col_m8.metric(
            "Likviditetsgrad 1",
            f"{metrics['likviditetsgrad_1']:.2f}",
            delta="Sterk (≥ 2,0)" if likv_ok else "Under norm (< 2,0)",
            delta_color="normal" if likv_ok else "inverse",
            help="Omløpsmidler dividert på kortsiktig gjeld (anbefalt norm ≥ 2,0).",
        )
        
        # Visuell graf: Hovedstørrelser i resultatet
        with st.expander("📊 Vis grafisk resultatfordeling", expanded=False):
            chart_df = pd.DataFrame({
                "Finansiell Post": ["Driftsinntekter", "Driftskostnader", "Driftsresultat (EBIT)"],
                "Beløp (NOK)": [float(metrics['driftsinntekter']), float(metrics['samlede_driftskostnader']), float(metrics['ebit'])]
            }).set_index("Finansiell Post")
            st.bar_chart(chart_df)
        
        # Tilstandsnøkkel slik at rapporten bevares ved klikk på nedlastingsknapper, men nullstilles ved bytte av datakilde
        current_context_key = f"{demo_mode}_{use_mock_ai}_{sb_source_name}_{hb_source_name}_{len(sb_df)}_{len(hb_df)}_{recon_result['is_reconciled'] if recon_result else 'none'}"
        if st.session_state.get("report_context_key") != current_context_key:
            st.session_state.pop("active_ai_report", None)
            st.session_state["report_context_key"] = current_context_key

        # KI Analyse
        if st.button("🚀 Generer Strategisk Ledelsesrapport (KI)", type="primary"):
            with st.status("🤖 CFO-Agent analyserer regnskapet over The AI Firewall...", expanded=True) as status:
                try:
                    st.write("🔒 Verifiserer deterministisk nøkkeltallspayload (ingen råtransaksjoner)...")
                    report = generate_management_report(
                        sb_mapped, 
                        recon_result=recon_result,
                        api_key=openai_api_key if not use_mock_ai else None,
                        mock_mode=use_mock_ai
                    )
                    st.write("✅ Strukturert `ManagementCommentary` validert mot Pydantic-skjema og kryssavstemming.")
                    st.session_state["active_ai_report"] = report
                    status.update(label="✅ Strategisk ledelsesrapport ferdigstilt!", state="complete", expanded=False)
                except Exception as e:
                    status.update(label="❌ Feil under generering av rapport", state="error", expanded=True)
                    st.error(f"Feil ved generering av rapport: {e}")

        if "active_ai_report" in st.session_state:
            report = st.session_state["active_ai_report"]

            # 1. Hovedkonklusjon
            st.markdown("### 🏆 Hovedkonklusjon til Styret")
            st.info(report.hovedkonklusjon)
            
            # 2. Faner for dyp analyse
            tab1, tab2, tab3 = st.tabs([
                "📊 Lønnsomhet & Marginer", 
                "💧 Likviditet & Arbeidskapital", 
                "🛡️ Revisors Avstemmingsnotat"
            ])
            
            with tab1:
                with st.container(border=True):
                    st.markdown(report.lonnsomhet_og_marginer)
            with tab2:
                with st.container(border=True):
                    st.markdown(report.likviditet_og_arbeidskapital)
            with tab3:
                with st.container(border=True):
                    st.markdown(report.revisors_avstemmingsnotat)
            
            # 3. Faresignaler og tiltak
            st.markdown("---")
            col_ai1, col_ai2 = st.columns([1, 2])
            with col_ai1:
                st.markdown("### 🚩 Identifiserte Faresignaler")
                for avvik in report.potensielle_avvik:
                    st.warning(f"• {avvik}")
                    
            with col_ai2:
                st.markdown("### 🎯 Strategisk Handlingsplan")
                for tiltak in report.tiltaksliste:
                    prio_color = "red" if tiltak.prioritet == "Høy" else ("orange" if tiltak.prioritet == "Medium" else "green")
                    with st.container(border=True):
                        st.markdown(
                            f"**:{prio_color}[[{tiltak.prioritet}]]** **{tiltak.tiltak}**  \n"
                            f"*Begrunnelse:* {tiltak.begrunnelse}  \n"
                            f"*Forventet effekt:* {tiltak.forventet_effekt}"
                        )
                    
            # PDF og HTML Eksport
            st.markdown("---")
            with st.container(border=True):
                st.subheader("📄 Eksport til Styret")
                st.caption("Begge formater genereres 100 % i minnet (`io.BytesIO`) fra nøyaktig samme verifiserte datagrunnlag.")
                pdf_buffer = generate_management_pdf(
                    company_name=company_name,
                    ai_report=report,
                    ns4102_summary=metrics,
                    recon_result=recon_result
                )
                html_buffer = generate_management_html(
                    company_name=company_name,
                    ai_report=report,
                    metrics=metrics,
                    recon_result=recon_result
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
    st.info("Vennligst last opp både Saldobalanse og Hovedbok, eller velg eksempeldata i menyen til venstre.")
