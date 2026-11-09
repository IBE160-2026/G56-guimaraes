"""
Side 4: Operasjonell analyse (v2.) – Kommende utvidelse for operasjonell virksomhetsstyring.
"""

import streamlit as st


def render_operational_analysis() -> None:
    st.title("⚙️ 4. Operasjonell analyse (v2.)")
    st.markdown(
        "Modul for operasjonell drift- og ressurseffektivitet på tvers av avdelinger, prosjekter, "
        "kundereskontro og varelager."
    )

    st.info(
        "🚧 **Under utvikling (Planlagt i v2.0):** Denne modulen kobler regnskapsdata fra Hovedbok og Saldobalanse "
        "mot operasjonelle forssystemer (CRM, timeregistrering og logistikk). "
        "For aktive finansielle nøkkeltall og deterministiske lønnsomhetsråd, se **📊 3. Finansiell Analyse & HB** "
        "og **💡 7. KI-Rådgiver & Eksport**."
    )

    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.subheader("👥 Kunde- og Produktlønnsomhet (V2)")
            st.markdown("**🚧 Under utvikling**")
            st.write(
                "Dekningsbidragsanalyse per kundesegment og produktkategori koblet mot konto 1500 Kundefordringer "
                "og 3000 Salgsinntekter."
            )
            st.button("Start kundelønnsomhetsanalyse", disabled=True, key="btn_op_cust_v2")

    with col2:
        with st.container(border=True):
            st.subheader("📦 Lagerstyring & Innkjøpsoptimalisering (V2)")
            st.markdown("**🚧 Under utvikling**")
            st.write(
                "Beregning av omløpshastighet på varelager, kapitalbinding og leverandøravhengighet mot konto "
                "1400 Varelager og 4000 Varekostnad."
            )
            st.button("Analyser vareflyt", disabled=True, key="btn_op_inv_v2")
