import streamlit as st
import pandas as pd
import io
import os
from data_pipeline import process_csv_in_memory, process_excel_in_memory
from compliance_engine import validate_balance, map_to_ns4102, reconcile_hb_with_sb
from llm_integration import generate_management_report
from pdf_generator import generate_management_pdf

st.set_page_config(page_title="Ledelsesrapport & Regnskapskontroll (KI)", layout="wide", page_icon="📊")

st.title("📊 Ledelsesrapport og Regnskapskontroll med KI")
st.markdown(
    "Automatisert avstemming mellom **Saldobalanse (SB)** og **Hovedbok (HB)**, "
    "mapping til **NS 4102**, og KI-generert ledelsesnotat for styret."
)

# Sidebar for innstillinger og hurtiglasting
with st.sidebar:
    st.header("⚙️ Konfigurasjon")
    demo_mode = st.radio(
        "Velg datakilde:",
        ["Last opp egne filer", "Bruk eksempeldata (Balansert)", "Bruk eksempeldata (Med avvik)"],
        index=0
    )
    
    st.markdown("---")
    st.subheader("🤖 KI-innstillinger")
    use_mock_ai = st.checkbox("Bruk testmodus (Mock KI)", value=True, help="Aktiver for å kjøre uten OpenAI API-nøkkel (Sensor-vennlig).")
    openai_api_key = ""
    if not use_mock_ai:
        openai_api_key = st.text_input("OpenAI API-nøkkel:", type="password")

sb_df = None
hb_df = None

# Håndter datakilde
sample_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../data/sample'))

if demo_mode == "Bruk eksempeldata (Balansert)":
    st.info("💡 Laster inn balanserte eksempeldata fra `data/sample/`.")
    sb_df = pd.read_csv(os.path.join(sample_dir, 'saldobalanse_balansert.csv'))
    hb_df = pd.read_csv(os.path.join(sample_dir, 'hovedbok_balansert.csv'))

elif demo_mode == "Bruk eksempeldata (Med avvik)":
    st.warning("⚠️ Laster inn eksempeldata med bevisst ubalanse og kryssavvik for testing.")
    sb_df = pd.read_csv(os.path.join(sample_dir, 'saldobalanse_balansert.csv'))
    hb_df = pd.read_csv(os.path.join(sample_dir, 'hovedbok_med_avvik.csv'))

else:
    col_up1, col_up2 = st.columns(2)
    with col_up1:
        st.subheader("1. Saldobalanse (SB)")
        uploaded_sb = st.file_uploader("Last opp Saldobalanse (CSV / Excel)", type=["csv", "xlsx"], key="sb_upload")
        if uploaded_sb:
            file_bytes = io.BytesIO(uploaded_sb.getvalue())
            sb_df = process_csv_in_memory(file_bytes, uploaded_sb.name) if uploaded_sb.name.endswith('.csv') else list(process_excel_in_memory(file_bytes, uploaded_sb.name).values())[0]
            
    with col_up2:
        st.subheader("2. Hovedbok (HB)")
        uploaded_hb = st.file_uploader("Last opp Hovedbok (CSV / Excel)", type=["csv", "xlsx"], key="hb_upload")
        if uploaded_hb:
            file_bytes = io.BytesIO(uploaded_hb.getvalue())
            hb_df = process_csv_in_memory(file_bytes, uploaded_hb.name) if uploaded_hb.name.endswith('.csv') else list(process_excel_in_memory(file_bytes, uploaded_hb.name).values())[0]

# Behandling når begge filer er tilgjengelige
if sb_df is not None and hb_df is not None:
    st.markdown("---")
    st.header("🔍 Steg 1: Automatisk Internkontroll & Avstemming")
    
    col_check1, col_check2 = st.columns(2)
    sb_ok = False
    hb_ok = False
    
    # 1. Balansekontroll Debet = Kredit
    with col_check1:
        st.subheader("Balansekontroll: Saldobalanse")
        try:
            validate_balance(sb_df, 'Debet', 'Kredit')
            st.success("✅ Godkjent: Debet = Kredit i saldobalansen")
            sb_ok = True
        except Exception as e:
            st.error(f"❌ {e}")
            
    with col_check2:
        st.subheader("Balansekontroll: Hovedbok")
        try:
            validate_balance(hb_df, 'Debet', 'Kredit')
            st.success("✅ Godkjent: Debet = Kredit i hovedboken")
            hb_ok = True
        except Exception as e:
            st.error(f"❌ {e}")
            
    # 2. Kryssavstemming (IB + HB = UB)
    st.subheader("Kryssavstemming: Hovedbok mot Saldobalanse ($IB + \\sum HB = UB$)")
    try:
        recon_result = reconcile_hb_with_sb(sb_df, hb_df)
        if recon_result["is_reconciled"]:
            st.success("✅ Full konsistens: Alle transaksjoner i hovedboken summerer seg nøyaktig til UB i saldobalansen!")
        else:
            st.error(f"❌ Avstemmingsavvik funnet på {recon_result['discrepancy_count']} konto(er):")
            st.dataframe(recon_result["discrepancies"][['Konto', 'Kontonavn', 'IB', 'Netto_HB', 'Beregnet_UB', 'UB', 'Avvik']])
    except Exception as e:
        st.error(f"Kunne ikke gjennomføre kryssavstemming: {e}")
        recon_result = None

    # Vis forhåndsvisning
    with st.expander("Vis data og NS 4102-kategorisering"):
        sb_mapped = sb_df.copy()
        if 'Konto' in sb_mapped.columns:
            sb_mapped['NS4102_Kategori'] = sb_mapped['Konto'].apply(map_to_ns4102)
        st.dataframe(sb_mapped)

    # Steg 2: Nøkkeltall og KI-analyse
    if sb_ok and hb_ok:
        st.markdown("---")
        st.header("📈 Steg 2: Nøkkeltall og Strategisk Ledelsessammendrag")
        
        sb_mapped = sb_df.copy()
        if 'Konto' in sb_mapped.columns:
            sb_mapped['NS4102_Kategori'] = sb_mapped['Konto'].apply(map_to_ns4102)
            
        # Deterministisk nøkkeltallsberegning
        driftsinntekter = sb_mapped[sb_mapped['NS4102_Kategori'] == "Salgs- og Driftsinntekt (NS 4102)"]['Kredit'].sum()
        driftskostnader = sb_mapped[sb_mapped['NS4102_Kategori'] == "Driftskostnader (NS 4102)"]['Debet'].sum()
        ebit = driftsinntekter - driftskostnader
        margin = (ebit / driftsinntekter * 100) if driftsinntekter > 0 else 0
        
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        col_m1.metric("Driftsinntekter", f"{driftsinntekter:,.0f} NOK")
        col_m2.metric("Driftskostnader", f"{driftskostnader:,.0f} NOK")
        col_m3.metric("Driftsresultat (EBIT)", f"{ebit:,.0f} NOK")
        col_m4.metric("Driftsmargin", f"{margin:.1f} %")
        
        # KI Analyse
        if st.button("🚀 Generer Ledelsesrapport med KI", type="primary"):
            with st.spinner("Genererer ledelseskommentar og analyserapport..."):
                try:
                    report = generate_management_report(
                        sb_mapped, 
                        api_key=openai_api_key if not use_mock_ai else None,
                        mock_mode=use_mock_ai
                    )
                    
                    st.success("✅ Rapport generert!")
                    
                    st.subheader("📋 Ledelsessammendrag (CFO Tone-of-Voice)")
                    st.info(report.okonomisk_sammendrag)
                    
                    col_ai1, col_ai2 = st.columns(2)
                    with col_ai1:
                        st.subheader("🚩 Identifiserte Faresignaler / Avvik")
                        for avvik in report.potensielle_avvik:
                            st.warning(f"• {avvik}")
                    with col_ai2:
                        st.subheader("🎯 Prioritert Tiltaksliste")
                        for tiltak in report.tiltaksliste:
                            st.error(f"**[{tiltak.prioritet}]** {tiltak.tiltak}")
                            
                    # PDF Eksport
                    st.markdown("---")
                    st.subheader("📄 Eksport til Styret")
                    pdf_buffer = generate_management_pdf(company_name="Bedrift AS", ai_report=report)
                    st.download_button(
                        label="📥 Last ned Ledelsesrapport (PDF)",
                        data=pdf_buffer,
                        file_name="Styrepakke_Ledelsesrapport.pdf",
                        mime="application/pdf",
                        type="primary"
                    )
                except Exception as e:
                    st.error(f"Feil ved generering av rapport: {e}")
                    
else:
    st.info("Vennligst last opp både Saldobalanse og Hovedbok, eller velg eksempeldata i menyen til venstre.")
