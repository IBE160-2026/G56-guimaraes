"""
Side 8: Historikk & Trendanalyse fra lokal SQLite-database (data/g56_accounting.db).
"""

import pandas as pd
import streamlit as st

from html_report import generate_management_html
from llm_integration import ManagementCommentary
from pdf_generator import generate_management_pdf


def render_history_and_trends() -> None:
    db = st.session_state.get("db_manager")
    st.title("🗄️ 8. Historikk & Trendanalyse (SQLite)")
    st.markdown(
        "Sammenlign lagrede regnskapsanalyser på tvers av perioder og sesjoner, inspiser historiske "
        "saldobalanser, hovedbøker og KI-rapporter, eller eksporter tidligere styrepakker."
    )

    if db is None:
        st.error("Databasemotoren er ikke initialisert.")
        return

    runs_df = db.list_analysis_runs()
    if runs_df.empty:
        st.info("Ingen lagrede analyser funnet i SQLite-databasen ennå. Last inn et gyldig datasett på Side 1.")
        return

    st.subheader(f"📋 Lagrede regnskapsanalyser ({len(runs_df)} kjøring(er) i lokal database)")

    display_df = runs_df.copy()
    display_df["Avstemt"] = display_df["is_reconciled"].apply(lambda x: "✅ Godkjent" if x else "❌ Avvik")
    display_df["KI-rapport"] = display_df["has_ai_report"].apply(lambda x: "🤖 Lagret" if x else "—")

    st.dataframe(
        display_df[[
            "run_id",
            "company_name",
            "period_label",
            "Avstemt",
            "revenue",
            "ebit",
            "operating_margin_pct",
            "liquidity_ratio_1",
            "equity_ratio_pct",
            "roa_tkr_pct",
            "roe_ekr_pct",
            "KI-rapport",
            "created_at",
        ]],
        use_container_width=True,
        hide_index=True,
        column_config={
            "run_id": st.column_config.NumberColumn("Kjøring #"),
            "company_name": st.column_config.TextColumn("Selskap"),
            "period_label": st.column_config.TextColumn("Periode"),
            "revenue": st.column_config.NumberColumn("Inntekter (NOK)", format="%.0f kr"),
            "ebit": st.column_config.NumberColumn("EBIT (NOK)", format="%.0f kr"),
            "operating_margin_pct": st.column_config.NumberColumn("Driftsmargin", format="%.1f %%"),
            "liquidity_ratio_1": st.column_config.NumberColumn("LG1", format="%.2f"),
            "equity_ratio_pct": st.column_config.NumberColumn("Soliditet", format="%.1f %%"),
            "roa_tkr_pct": st.column_config.NumberColumn("TKR", format="%.1f %%"),
            "roe_ekr_pct": st.column_config.NumberColumn("EKR", format="%.1f %%"),
            "created_at": st.column_config.TextColumn("Lagret tidspunkt"),
        },
    )

    if len(runs_df) >= 2:
        st.markdown("---")
        st.subheader("📈 Utvikling på tvers av lagrede kjøringer")
        trend_df = runs_df.sort_values(by="run_id", ascending=True).copy()
        trend_df["Etikett"] = (
            "#" + trend_df["run_id"].astype(str) + " " + trend_df["company_name"] + " (" + trend_df["period_label"] + ")"
        )
        t_col1, t_col2 = st.columns(2)
        with t_col1:
            with st.container(border=True):
                st.markdown("**Driftsinntekter vs. EBIT (NOK)**")
                st.bar_chart(trend_df.set_index("Etikett")[["revenue", "ebit"]])
        with t_col2:
            with st.container(border=True):
                st.markdown("**Soliditet (EK-andel %) og Rentabilitet (TKR/EKR %)**")
                st.bar_chart(trend_df.set_index("Etikett")[["equity_ratio_pct", "roa_tkr_pct", "roe_ekr_pct"]])

    st.markdown("---")
    st.subheader("🔍 Inspiser eller administrer en lagret kjøring")

    run_options = runs_df["run_id"].tolist()
    run_label_map = {
        int(r["run_id"]): (
            f"Kjøring #{int(r['run_id'])} – {r['company_name']} ({r['period_label']}) • "
            f"{'Godkjent' if r['is_reconciled'] else 'Med avvik'} • {r['sb_filename']} / {r['hb_filename']}"
        )
        for _, r in runs_df.iterrows()
    }

    sel_col1, sel_col2 = st.columns([3, 1])
    with sel_col1:
        selected_run_id = st.selectbox(
            "Velg lagret analyse:",
            run_options,
            format_func=lambda rid: run_label_map.get(int(rid), str(rid)),
        )
    with sel_col2:
        st.write("")
        st.write("")
        active_run_id = st.session_state.get("workspace", {}).get("run_id")
        can_delete = int(selected_run_id) != int(active_run_id or -1)
        if st.button(
            "🗑️ Slett valgt kjøring",
            disabled=not can_delete,
            use_container_width=True,
            help="Du kan slette tidligere kjøringer (bytt datakilde først dersom du vil slette den som er aktiv nå).",
        ):
            db.delete_analysis_run(int(selected_run_id))
            st.success(f"Slettet Kjøring #{selected_run_id} fra SQLite-databasen.")
            st.rerun()

    details = db.get_run_details(int(selected_run_id))
    if details is not None:
        h_tab1, h_tab2, h_tab3 = st.tabs([
            "📊 Lagret Saldobalanse & Avstemming",
            "📘 Lagret Hovedbok",
            "🤖 Lagret KI-Rapport & Re-eksport",
        ])
        with h_tab1:
            st.dataframe(details["trial_balance"], use_container_width=True, hide_index=True)
        with h_tab2:
            st.dataframe(details["ledger"], use_container_width=True, hide_index=True)
        with h_tab3:
            ai_info = details.get("ai_insight")
            if ai_info is None:
                st.info("Det er ikke lagret noen KI-ledelsesrapport på denne kjøringen ennå.")
            else:
                hist_report = ManagementCommentary(**ai_info["commentary"])
                mode_lbl = "Frakoblet Mock-KI" if ai_info["is_mock"] else "Live OpenAI API"
                st.caption(f"Generert: {ai_info['created_at']} • Modus: **{mode_lbl}**")
                st.info(hist_report.hovedkonklusjon)
                st.markdown(f"**Lønnsomhet & Marginer:** {hist_report.lonnsomhet_og_marginer}")
                st.markdown(f"**Likviditet & Arbeidskapital:** {hist_report.likviditet_og_arbeidskapital}")
                st.markdown(f"**Soliditet & Rentabilitet:** {hist_report.soliditet_og_rentabilitet}")
                st.markdown(f"**Revisors Avstemmingsnotat:** {hist_report.revisors_avstemmingsnotat}")

                tb_df = details["trial_balance"]
                disc_df = tb_df[tb_df["Avvik"].abs() > 0.01]
                hist_recon = {
                    "is_reconciled": bool(details["metadata"]["is_reconciled"]),
                    "discrepancy_count": int(details["metadata"]["discrepancy_count"]),
                    "discrepancies": disc_df,
                }
                hist_company = details["metadata"]["company_name"]
                pdf_buf = generate_management_pdf(
                    company_name=hist_company,
                    ai_report=hist_report,
                    ns4102_summary=details["metrics"],
                    recon_result=hist_recon,
                    recommendations=details["recommendations"],
                    report_type="styre",
                )
                html_styre_buf = generate_management_html(
                    company_name=hist_company,
                    ai_report=hist_report,
                    metrics=details["metrics"],
                    recon_result=hist_recon,
                    recommendations=details["recommendations"],
                    report_type="styre",
                )
                html_ledelse_buf = generate_management_html(
                    company_name=hist_company,
                    ai_report=hist_report,
                    metrics=details["metrics"],
                    recon_result=hist_recon,
                    recommendations=details["recommendations"],
                    report_type="ledelse",
                )
                dl1, dl2, dl3 = st.columns(3)
                with dl1:
                    st.download_button(
                        f"📥 Last ned Styrepakke HTML (#{selected_run_id})",
                        data=html_styre_buf,
                        file_name=f"Styrepakke_Run_{selected_run_id}.html",
                        mime="text/html",
                        use_container_width=True,
                        key=f"hist_html_styre_{selected_run_id}",
                    )
                with dl2:
                    st.download_button(
                        f"📥 Last ned Beslutningsrapport HTML (#{selected_run_id})",
                        data=html_ledelse_buf,
                        file_name=f"Beslutningsrapport_Run_{selected_run_id}.html",
                        mime="text/html",
                        use_container_width=True,
                        key=f"hist_html_ledelse_{selected_run_id}",
                    )
                with dl3:
                    st.download_button(
                        f"📥 Last ned PDF (Kjøring #{selected_run_id})",
                        data=pdf_buf,
                        file_name=f"Styrepakke_Run_{selected_run_id}.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                        key=f"hist_pdf_{selected_run_id}",
                    )
