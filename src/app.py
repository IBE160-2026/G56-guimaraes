"""
Hovedapplikasjon for G56 – Ledelsesrapport, Finansanalyse & Regnskapskontroll med KI (v2.0).
Orkestrerer sidepanel-navigasjon (st.sidebar.radio), modulære visninger og automatisk SQLite-synkronisering.
"""

import io
import os
import pandas as pd
import streamlit as st

from app_logging import setup_app_logging
from compliance_engine import (
    calculate_detailed_financial_metrics,
    evaluate_ns4102_compliance,
    evaluate_vat_compliance,
    map_to_ns4102,
    reconcile_hb_with_sb,
    validate_balance,
)
from data_pipeline import process_csv_in_memory, validate_input
from database import DatabaseManager
from ledger_analytics import (
    build_ns4102_income_statement,
    calculate_ebit_driver_sensitivity,
    evaluate_profitability_indicators,
    extract_period_label,
    generate_profitability_recommendations,
    summarize_cost_drivers,
)
from llm_integration import ManagementCommentary
from views.ai_advisor_and_export import render_ai_advisor_and_export
from views.auditor_reconciliation import render_auditor_reconciliation
from views.financial_analysis import render_financial_analysis
from views.history_and_trends import render_history_and_trends
from views.industry_benchmarking import render_industry_benchmarking_mockup
from views.negotiation_and_bidding import render_negotiation_and_bidding_mockup
from views.operational_analysis import render_operational_analysis
from views.upload_and_control import render_upload_and_control

logger = setup_app_logging()


def check_env_security() -> None:
    """Varsler i loggen hvis .env-fil er til stede."""
    if os.path.exists(".env"):
        logger.warning(".env fil detektert. Verifiserer at den er ignorert av Git.")


check_env_security()

st.set_page_config(
    page_title="Ledelsesrapport & Finansanalyse (KI)",
    layout="wide",
    page_icon="📊",
)

# Initialiser SQLite DatabaseManager (støtter overstyring via miljøvariabel ved automatisert testing)
if "db_manager" not in st.session_state:
    custom_db_path = os.environ.get("G56_DB_PATH")
    st.session_state["db_manager"] = (
        DatabaseManager(db_path=custom_db_path) if custom_db_path else DatabaseManager()
    )

db: DatabaseManager = st.session_state["db_manager"]
sample_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/sample"))


def on_demo_mode_change() -> None:
    st.session_state["quick_semicolon_mode"] = False


def activate_semicolon_demo() -> None:
    st.session_state["quick_semicolon_mode"] = True
    if st.session_state.get("sb_upload") is not None:
        f = st.session_state["sb_upload"]
        st.session_state["ignored_sb_token"] = (f.name, f.size)
    if st.session_state.get("hb_upload") is not None:
        f = st.session_state["hb_upload"]
        st.session_state["ignored_hb_token"] = (f.name, f.size)
    st.session_state.pop("sb_upload", None)
    st.session_state.pop("hb_upload", None)


def reset_to_sample_data() -> None:
    st.session_state["quick_semicolon_mode"] = False
    st.session_state["demo_mode_radio"] = "Bruk eksempeldata (Balansert - Grønn sti)"
    st.session_state.pop("persisted_custom_sb", None)
    st.session_state.pop("persisted_custom_hb", None)
    st.session_state.pop("persisted_custom_sb_token", None)
    st.session_state.pop("persisted_custom_hb_token", None)
    if st.session_state.get("sb_upload") is not None:
        f = st.session_state["sb_upload"]
        st.session_state["ignored_sb_token"] = (f.name, f.size)
    if st.session_state.get("hb_upload") is not None:
        f = st.session_state["hb_upload"]
        st.session_state["ignored_hb_token"] = (f.name, f.size)
    st.session_state.pop("sb_upload", None)
    st.session_state.pop("hb_upload", None)


st.session_state["cb_activate_semicolon"] = activate_semicolon_demo
st.session_state["cb_reset_sample"] = reset_to_sample_data

NAV_OPTIONS = [
    "📂 1. Opplasting & Kontroll",
    "🔎 2. Revisors avstemming",
    "📊 3. Finansiell Analyse & HB",
    "⚙️ 4. Operasjonell analyse (v2.)",
    "🏢 5. Bransjesammenligning (v2.)",
    "🤝 6. Forhandling og anbud (v2.)",
    "💡 7. KI-Rådgiver & Eksport",
    "🗄️ 8. Historikk & Trendanalyse",
]

selected_step = st.sidebar.radio(
    "Navigasjon:",
    NAV_OPTIONS,
    index=0,
    key="sidebar_nav_radio",
)

with st.sidebar:
    st.markdown("---")
    st.header("⚙️ Konfigurasjon & Sensormodus")
    company_name = st.text_input("Selskapsnavn:", value="Bedrift AS")
    demo_mode = st.radio(
        "Velg datakilde:",
        [
            "Bruk eksempeldata (Balansert - Grønn sti)",
            "Bruk eksempeldata (Med avvik - Rød sti)",
            "Last opp egne filer (CSV / Excel)",
        ],
        index=0,
        key="demo_mode_radio",
        on_change=on_demo_mode_change,
    )

    st.markdown("---")
    st.subheader("🤖 KI-innstillinger")
    use_mock_ai = st.checkbox(
        "Bruk testmodus (Mock KI)",
        value=True,
        help="Aktiver for å kjøre 100 % lokalt og deterministisk uten OpenAI API-nøkkel (Sensor-vennlig).",
    )
    openai_api_key = ""
    if not use_mock_ai:
        openai_api_key = st.text_input("OpenAI API-nøkkel:", type="password")

# Synkroniser aktivt regnskapsdatasett og lagre automatisk (SHA-256 deduplisert) i SQLite
sb_df = None
hb_df = None
sb_source_name = None
hb_source_name = None
source_banner = None

if st.session_state.get("quick_semicolon_mode", False):
    source_banner = (
        "info",
        "⚡ **Norsk semikolon-format aktivert:** Laster inn `saldobalanse_norsk_semikolon.csv` "
        "(med `;` og desimalkomma `100 000,00`) og `hovedbok_balansert.csv`.",
    )
    semicolon_path = os.path.join(sample_dir, "saldobalanse_norsk_semikolon.csv")
    with open(semicolon_path, "rb") as f:
        sb_df = process_csv_in_memory(io.BytesIO(f.read()), "saldobalanse_norsk_semikolon.csv")
    validate_input(sb_df, expected_type="SB")
    hb_df = pd.read_csv(os.path.join(sample_dir, "hovedbok_balansert.csv"))
    sb_source_name = "saldobalanse_norsk_semikolon.csv"
    hb_source_name = "hovedbok_balansert.csv"
elif demo_mode == "Bruk eksempeldata (Balansert - Grønn sti)":
    source_banner = (
        "info",
        "💡 **Sensormodus:** Laster inn balanserte eksempeldata fra `data/sample/` (0 avvik).",
    )
    sb_df = pd.read_csv(os.path.join(sample_dir, "saldobalanse_balansert.csv"))
    hb_df = pd.read_csv(os.path.join(sample_dir, "hovedbok_balansert.csv"))
    sb_source_name = "saldobalanse_balansert.csv"
    hb_source_name = "hovedbok_balansert.csv"
elif demo_mode == "Bruk eksempeldata (Med avvik - Rød sti)":
    source_banner = (
        "warning",
        "⚠️ **Sensormodus:** Laster inn eksempeldata med konstruerte avvik på konto 1500 og 1920.",
    )
    sb_df = pd.read_csv(os.path.join(sample_dir, "saldobalanse_balansert.csv"))
    hb_df = pd.read_csv(os.path.join(sample_dir, "hovedbok_med_avvik.csv"))
    sb_source_name = "saldobalanse_balansert.csv"
    hb_source_name = "hovedbok_med_avvik.csv"
else:
    if "persisted_custom_sb" in st.session_state:
        sb_source_name, sb_df = st.session_state["persisted_custom_sb"]
    if "persisted_custom_hb" in st.session_state:
        hb_source_name, hb_df = st.session_state["persisted_custom_hb"]

st.session_state["sb_df"] = sb_df
st.session_state["hb_df"] = hb_df

workspace = {
    "company_name": company_name,
    "use_mock_ai": use_mock_ai,
    "openai_api_key": openai_api_key,
    "sb_df": sb_df,
    "hb_df": hb_df,
    "sb_source_name": sb_source_name,
    "hb_source_name": hb_source_name,
    "source_banner": source_banner,
    "sb_ok": False,
    "hb_ok": False,
    "sb_error": None,
    "hb_error": None,
    "recon_result": None,
    "recon_error": None,
    "vat_compliance": None,
    "ns4102_compliance": None,
    "sb_mapped": None,
    "metrics": None,
    "income_statement": None,
    "profitability_indicators": None,
    "cost_drivers": [],
    "recommendations": [],
    "period_label": None,
    "run_id": None,
    "export_profiles": {
        "styre": "Generer Styrepakke (Strategisk)",
        "ledelse": "Generer Beslutningsrapport (Operativ)",
    },
}

if sb_df is not None and hb_df is not None:
    try:
        validate_balance(sb_df, "Debet", "Kredit")
        workspace["sb_ok"] = True
    except Exception as e:
        workspace["sb_error"] = str(e)

    try:
        validate_balance(hb_df, "Debet", "Kredit")
        workspace["hb_ok"] = True
    except Exception as e:
        workspace["hb_error"] = str(e)

    try:
        workspace["recon_result"] = reconcile_hb_with_sb(sb_df, hb_df)
    except Exception as e:
        workspace["recon_error"] = str(e)

    workspace["vat_compliance"] = evaluate_vat_compliance(sb_df, hb_df)
    workspace["ns4102_compliance"] = evaluate_ns4102_compliance(sb_df, hb_df)

    sb_mapped = sb_df.copy()
    if "Konto" in sb_mapped.columns:
        sb_mapped["NS4102_Kategori"] = sb_mapped["Konto"].apply(map_to_ns4102)
    workspace["sb_mapped"] = sb_mapped

    if workspace["sb_ok"] and workspace["hb_ok"] and workspace["recon_result"] is not None:
        metrics = calculate_detailed_financial_metrics(sb_mapped)
        income_statement = build_ns4102_income_statement(sb_mapped, hb_df, metrics)
        profitability_indicators = evaluate_profitability_indicators(metrics)
        ebit_driver_sensitivity = calculate_ebit_driver_sensitivity(metrics)
        cost_drivers = summarize_cost_drivers(sb_mapped, hb_df)
        recommendations = generate_profitability_recommendations(metrics, cost_drivers)
        period_label = extract_period_label(hb_df)

        workspace["metrics"] = metrics
        workspace["income_statement"] = income_statement
        workspace["profitability_indicators"] = profitability_indicators
        workspace["ebit_driver_sensitivity"] = ebit_driver_sensitivity
        workspace["cost_drivers"] = cost_drivers
        workspace["recommendations"] = recommendations
        workspace["period_label"] = period_label

        run_id, _ = db.save_or_get_analysis_run(
            company_name=company_name,
            period_label=period_label,
            sb_filename=sb_source_name or "saldobalanse.csv",
            hb_filename=hb_source_name or "hovedbok.csv",
            sb_df=sb_mapped,
            hb_df=hb_df,
            recon_result=workspace["recon_result"],
            metrics=metrics,
            recommendations=recommendations,
        )
        workspace["run_id"] = run_id

        # Synkroniser tilstandsnøkkel for KI-rapport (gjenopprett lagret KI-rapport fra SQLite ved behov)
        context_key = f"run_{run_id}_mock_{use_mock_ai}"
        if st.session_state.get("report_context_key") != context_key:
            st.session_state.pop("active_ai_report", None)
            st.session_state["report_context_key"] = context_key
            saved_details = db.get_run_details(run_id)
            if saved_details and saved_details.get("ai_insight"):
                ai_saved = saved_details["ai_insight"]
                if bool(ai_saved["is_mock"]) == bool(use_mock_ai):
                    st.session_state["active_ai_report"] = ManagementCommentary(**ai_saved["commentary"])

st.session_state["workspace"] = workspace

with st.sidebar:
    st.markdown("---")
    runs_count = len(db.list_analysis_runs())
    active_run_txt = f"Kjøring #{workspace['run_id']}" if workspace.get("run_id") else "Ingen aktiv"
    st.markdown("### 🗄️ SQLite Database")
    st.caption(f"Aktiv sesjon: **{active_run_txt}**  \nLagrede analyser i historikk: **{runs_count}**")
    st.markdown("### ℹ️ Om Løsningen")
    st.caption(
        "**Utviklings-KI:** Google Gemini Antigravity (BMAD).\n\n"
        "**The AI Firewall:** Koden regner deterministisk i Python/SQLite, KI forklarer via Pydantic Structured Outputs."
    )

if selected_step == "📂 1. Opplasting & Kontroll":
    render_upload_and_control()
elif selected_step == "🔎 2. Revisors avstemming":
    render_auditor_reconciliation()
elif selected_step == "📊 3. Finansiell Analyse & HB":
    render_financial_analysis()
elif selected_step == "⚙️ 4. Operasjonell analyse (v2.)":
    render_operational_analysis()
elif selected_step == "🏢 5. Bransjesammenligning (v2.)":
    render_industry_benchmarking_mockup()
elif selected_step == "🤝 6. Forhandling og anbud (v2.)":
    render_negotiation_and_bidding_mockup()
elif selected_step == "💡 7. KI-Rådgiver & Eksport":
    render_ai_advisor_and_export()
elif selected_step == "🗄️ 8. Historikk & Trendanalyse":
    render_history_and_trends()
