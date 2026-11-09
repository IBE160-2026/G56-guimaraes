"""
Side 5: Bransjesammenligning (NACE) (v2.) – Visuell teaser for NACE-basert benchmarking mot Brønnøysundregistrene.
Inkluderer deterministisk EBIT-driver-benchmarking og algoritmisk gap-identifikator (BMAD Strict / The AI Firewall).
"""

import numpy as np
import pandas as pd
import streamlit as st

from ledger_analytics import calculate_nace_driver_benchmarking


def render_industry_benchmarking_mockup() -> None:
    """Bygger statisk v2.0-teaser for NACE-basert bransjesammenligning og EBIT-driveranalyse."""
    st.title("🏢 5. Bransjesammenligning (NACE) (v2.)")
    st.markdown(
        "Benchmarking av selskapets lønnsomhet, kostnadsstruktur og marginer mot bransjekollegaer "
        "basert på offisielle NACE-næringskoder."
    )

    # 1. Teaser-advarsel (Banner)
    st.info(
        "🚧 Sneaktitt på v2.0: Denne modulen er under utvikling. I neste versjon vil systemet automatisk "
        "hente inn bransjedata via Brønnøysundregistrene (NACE-koder) for å benchmarke selskapets "
        "lønnsomhet mot konkurrentene."
    )

    # 2. Toppseksjon & NACE-valg (Mockup)
    st.subheader("🏛️ Bransjevalg & Nøkkeltalls-benchmarking (NACE)")
    st.selectbox(
        "Velg bransje (NACE-kode fra Enhetsregisteret):",
        options=[
            "62.010 Programmeringstjenester",
            "62.020 Konsulentvirksomhet tilknyttet informasjonsteknologi",
            "69.201 Regnskap og bokføring",
            "70.220 Bedriftsrådgivning og annen administrativ rådgivning",
        ],
        index=0,
        disabled=True,
        key="nace_selectbox_mockup_v2",
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        with st.container(border=True):
            st.metric(
                label="Driftsinntekter vs Bransjesnitt",
                value="1 200 000 NOK",
                delta="+18,5 % mot bransjesnitt",
                help="Simulert sammenligning av driftsinntekter mot medianbedriften i NACE 62.010.",
            )
    with col2:
        with st.container(border=True):
            st.metric(
                label="Opex vs Bransjesnitt",
                value="450 000 NOK",
                delta="-8,4 % mot bransjesnitt",
                help="Simulert sammenligning av operasjonelle driftskostnader (Opex) mot bransjesnittet.",
            )
    with col3:
        with st.container(border=True):
            st.metric(
                label="EBIT-margin vs Bransjesnitt",
                value="12,0 %",
                delta="+6,0 %-poeng (Snitt: 6,0 %)",
                help="Simulert driftsmargin (EBIT-%) sammenlignet med bransjens gjennomsnitt på 6,0 %.",
            )

    st.divider()

    # 3. Normalfordelingskurve (Lønnsomhet)
    with st.container(border=True):
        st.subheader("📈 Normalfordelingskurve – Lønnsomhet i bransjen (EBIT-margin %)")
        st.caption(
            "Statisk simulering av normalfordelt lønnsomhet (Bell Curve) for norske foretak innen NACE 62.010 "
            "Programmeringstjenester ($\\mu = 6,0\\%$, $\\sigma = 6,0\\%$). "
            "Selskapets estimerte plassering er i 3. kvartil (75. persentil) ved 12,0 % EBIT-margin."
        )

        # Generer deterministisk normalfordeling (Bell Curve) med numpy
        mu = 6.0
        sigma = 6.0
        x_vals = np.linspace(-12.0, 24.0, 121)
        bell_curve = (1.0 / (sigma * np.sqrt(2.0 * np.pi))) * np.exp(-0.5 * ((x_vals - mu) / sigma) ** 2)
        density_scaled = np.round(bell_curve * 100.0, 4)

        bell_df = pd.DataFrame(
            {"Bransjefordeling (Tetthet)": density_scaled},
            index=pd.Index(np.round(x_vals, 2), name="EBIT-margin (%)"),
        )

        st.area_chart(bell_df, use_container_width=True)

        st.markdown(
            "📍 Simulert posisjon: Selskapet ligger i 3. kvartil (Topp 25 %) med en margin på 12 %, mot et bransjesnitt på 6 %."
        )

    # 4. Avviksanalyse på EBIT-drivere & Algoritmisk Potensial-identifikator (NY)
    nace_bench = calculate_nace_driver_benchmarking(revenue_nok=1_200_000.0)
    drivers_df = nace_bench["drivers_df"]

    with st.container(border=True):
        st.subheader("🎯 Avviksanalyse på EBIT-drivere (Driver-benchmarking mot NACE)")
        st.caption(
            "Deterministisk gap-analyse beregnet med Python/Pandas over *The AI Firewall*. "
            "Sammenligner selskapets kjernekomponenter i resultatregnskapet mot bransjesnittet (NACE 62.010) "
            "og identifiserer algoritmisk hvor det største uforløste EBIT-potensialet ligger."
        )

        d_col1, d_col2, d_col3 = st.columns(3)
        row_brutto = drivers_df.iloc[0]
        row_lonn = drivers_df.iloc[1]
        row_opex = drivers_df.iloc[2]

        with d_col1:
            with st.container(border=True):
                st.metric(
                    label="Bruttomargin vs. Bransje",
                    value=f"{row_brutto['company_pct']:.1f} %".replace(".", ","),
                    delta=f"{row_brutto['diff_pp']:+.1f} %-poeng (Bransje: {row_brutto['industry_pct']:.1f} %)".replace(".", ","),
                    delta_color="normal",
                    help="Bruttofortjeneste i % av driftsinntekter. Lavere bruttomargin indikerer høyere varekostnadsandel (konto 4xxx) enn bransjen.",
                )
        with d_col2:
            with st.container(border=True):
                st.metric(
                    label="Lønnskostnad/Omsetning vs. Bransje",
                    value=f"{row_lonn['company_pct']:.1f} %".replace(".", ","),
                    delta=f"{row_lonn['diff_pp']:+.1f} %-poeng (Bransje: {row_lonn['industry_pct']:.1f} %)".replace(".", ","),
                    delta_color="inverse",
                    help="Lønnskostnader (konto 5xxx) i % av driftsinntekter. Lavere andel enn bransjen er gunstig for EBIT.",
                )
        with d_col3:
            with st.container(border=True):
                st.metric(
                    label="Opex/Omsetning vs. Bransje",
                    value=f"{row_opex['company_pct']:.1f} %".replace(".", ","),
                    delta=f"{row_opex['diff_pp']:+.1f} %-poeng (Bransje: {row_opex['industry_pct']:.1f} %)".replace(".", ","),
                    delta_color="inverse",
                    help="Øvrige faste driftskostnader (konto 6xxx–7xxx) i % av driftsinntekter. Lavere andel enn bransjen er gunstig.",
                )

        st.dataframe(
            nace_bench["display_df"],
            use_container_width=True,
            hide_index=True,
        )

        # Algoritmisk Potensial-identifikator fremhevet i UI
        st.success(nace_bench["potential_banner_text"])

    # 5. Handlingsrettede Tips (KI-Rådgiver for vekst)
    with st.container(border=True):
        st.subheader("🚀 Strategiske tiltak for å øke bransjescore (Kommer i v2)")
        st.write(
            "I versjon 2.0 vil **The AI Firewall** kombinere selskapets deterministiske posisjon på "
            "normalfordelingskurven (kvartilplassering, Opex-avvik og marginspread beregnet i Python/Pandas) "
            "med strukturerte bransjenormer fra Brønnøysundregistrene. Språkmodellen mottar kun de ferdigkalkulerte "
            "avvikene og foreslår målrettede, konkrete tiltak for å klatre til øverste desil – eksempelvis "
            "**reforhandling av leverandøravtaler og SaaS-lisenser (konto 6xxx)**, **justering av timepris- og "
            "prisingstrategier (konto 3xxx)**, samt **optimalisering av kapasitetsutnyttelse og faktureringsgrad**."
        )
        st.button("Generer bransjetiltak med KI", disabled=True, key="btn_generate_industry_ai_v2")


# Bakoverkompatibelt alias dersom andre moduler refererer til standard navnemønster
render_industry_benchmarking = render_industry_benchmarking_mockup
