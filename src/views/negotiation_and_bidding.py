"""
Side 6: Forhandling og anbud (v2.) – Konseptuell visuell teaser for versjon 2.0.
Fremtidig modul for automatisk kontrakts- og fakturaanalyse (OCR/PDF) over The AI Firewall,
benchmarking av reelle leverandørvilkår mot markedsstandarder og generering av formelle anbudsforespørsler (RFQ).
"""

import streamlit as st


def render_negotiation_and_bidding_mockup() -> None:
    """Bygger statisk v2.0-teaser for automatisert kontraktsanalyse, forhandling og anbudsgenerering (RFQ)."""
    st.title("🤝 6. Forhandling og anbud (v2.)")
    st.markdown(
        "Konseptuell forhandlings- og innkjøpsmodul som kobler verifiserte kostnadskontoer fra NS 4102 "
        "mot faktiske kontraktsvilkår fra fakturaer og avtaledokumenter."
    )

    # 1. Teaser-advarsel (Banner)
    st.info(
        "🚧 Sneaktitt på v2.0: Denne modulen er under utvikling. I neste versjon vil AI-en automatisk lese inn "
        "dine fakturaer og kontrakter (PDF/OCR), trekke ut skjulte vilkår (f.eks. strømpåslag, lånemargin, "
        "lisensgebyrer), og beregne eksakt innsparingspotensial før anbud genereres."
    )

    # 2. Toppseksjon (Simulert Sparepotensial)
    st.header("🤝 Forhandling og anbud på tjenester")
    st.caption(
        "**The AI Firewall (v2.0 Arkitektur):** OCR- og struktureringsmotoren ekstraherer satser og påslag fra PDF-fakturaer, "
        "Python/Pandas beregner eksakt avvik mot markedsstandard deterministisk (totalt simulert potensial: **81 000 kr/år**), "
        "og språkmodellen utformer selve anbudsforespørselen (RFQ) uten å regne på tallene."
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        with st.container(border=True):
            st.subheader("🏦 Bank & Finans")
            st.metric(
                label="Konto 2380 / 8150 – Kassekreditt & Renter",
                value="45 000 kr/år",
                delta="-2,0 %-poeng lånemargin",
            )
            st.markdown("**Avlest margin: 4,5 %. Markedsstandard: 2,5 %. Potensial: 45 000 kr/år**")
            st.caption(
                "Kilde (Simulert OCR): Kvartalsvis renteoppgave og låneavtale. "
                "Etablerings- og trekkprovisjon ligger over norm for SMB med egenkapitalandel > 35 %."
            )

    with col2:
        with st.container(border=True):
            st.subheader("🛡️ Forsikring")
            st.metric(
                label="Konto 7500 – Forsikringspremier",
                value="24 000 kr/år",
                delta="-20 % ved samleanbud",
            )
            st.markdown("**Avlest premie: 120 000 kr. Estimert kutt: 20 %. Potensial: 24 000 kr/år**")
            st.caption(
                "Kilde (Simulert OCR): Årlig poliseoversikt (yrkesskade, ansvar og innbo). "
                "Premien har økt automatisk med indeks uten reforhandling siste 24 måneder."
            )

    with col3:
        with st.container(border=True):
            st.subheader("⚡ Strøm & Lokaler")
            st.metric(
                label="Konto 6340 – Lys og varme",
                value="12 000 kr/år",
                delta="-9 øre/kWh i påslag",
            )
            st.markdown("**Oppdaget skjult påslag: 9 øre/kWh. Potensial: 12 000 kr/år**")
            st.caption(
                "Kilde (Simulert OCR): Månedlig strømfaktura (forbruk: 133 333 kWh/år). "
                "Avdekket fastbeløp og variabelt sertifikatpåslag over gjeldende bedriftsspot."
            )

    st.divider()

    # 3. Anbudsgenerator (Mockup av RFQ Builder)
    with st.container(border=True):
        st.subheader("📝 Anbudsgenerator – Request for Quotation (RFQ Builder)")
        st.write(
            "Når Python-motoren har verifisert kontraktsavviket mot markedsstandard, kan CFO-agenten "
            "generere en formell, skreddersydd anbudsforespørsel (RFQ) klar til utsendelse til konkurrerende tilbydere."
        )

        st.selectbox(
            "Velg kategori for anbudsgenerering (F.eks. Driftskreditt, Forsikring)",
            options=[
                "Driftskreditt & Bankbetingelser (Konto 2380 / 8150) – Potensial: 45 000 kr/år",
                "Bedrifts- og Yrkesskadeforsikring (Konto 7500) – Potensial: 24 000 kr/år",
                "Strømavtale Næring uten skjulte påslag (Konto 6340) – Potensial: 12 000 kr/år",
            ],
            index=0,
            disabled=True,
            key="rfq_category_selectbox_v2",
        )

        st.button(
            "Generer formell anbudsforespørsel (RFQ) med KI",
            disabled=True,
            key="btn_generate_rfq_v2",
        )

        with st.expander("Se eksempel på generert anbud"):
            st.markdown(
                """
**FORMELL ANBUDSFORESPØRSEL (REQUEST FOR QUOTATION – RFQ)**
**Til:** Aktuelle forretningsbanker og bedriftsforsikringsselskaper
**Fra:** Bedrift AS (v/ Daglig leder og CFO)
**Referanse:** RFQ-2026-G56-FINANS (Generert via *The AI Firewall* basert på revidert NS 4102-saldobalanse)

---

#### 1. Bakgrunn og finansiell soliditet
**Bedrift AS** gjennomfører en strukturert reforhandling av selskapets finansielle tjenester, driftskredittfasilitet og skade-/personforsikringer for kommende regnskapsperiode.
Selskapets regnskap er 100 % kryssavstemt mellom hovedbok og saldobalanse ($IB + HB = UB$ med 0,00 NOK i differanse), og viser en sunn operasjonell drift med dokumentert kontantstrøm, positiv driftsmargin (EBIT) og betryggende egenkapitalandel.

#### 2. Omfang av forespørselen (Scope of Services)
På bakgrunn av vår deterministiske kostnads- og kontraktsanalyse ber vi om bindende pristilbud på følgende pakker (enkeltvis eller samlet):

1. **Driftskreditt og konsernkonto (NS 4102 Konto 2380 / 8150):**
   * **Nåværende avlest vilkår:** Effektiv rentemargin på **4,5 %** over referanserente (NIBOR 3M).
   * **Krav i anbudet:** Vi etterspør en konkurransedyktig rentemargin i tråd med markedsstandard for solide SMB-foretak (**målmargin ≤ 2,5 %**), 0 kr i løpende administrasjonsgebyr og forbedret innskuddsrente på driftskonto (Konto 1920).
   * **Dokumentert besparelsesmål:** **45 000 NOK/år**.

2. **Bedrifts-, ansvars- og yrkesskadeforsikring (NS 4102 Konto 7500):**
   * **Nåværende avlest vilkår:** Årlig samlet premie på **120 000 NOK** med uendret skadehistorikk (0 meldte skader siste 36 måneder).
   * **Krav i anbudet:** Full gjennomgang av dekningssummer og egenandeler med mål om **20 % premiereduksjon** ved samling av selskapets poliser.
   * **Dokumentert besparelsesmål:** **24 000 NOK/år**.

3. **Næringsstrøm til forretningslokaler (NS 4102 Konto 6340):**
   * **Nåværende avlest vilkår:** Spotprisavtale med avdekket påslag på **9 øre/kWh** samt faste månedsgebyrer.
   * **Krav i anbudet:** Ren bedriftsspot uten skjulte administrasjonsgebyrer eller unødvendige tilleggstjenester.
   * **Dokumentert besparelsesmål:** **12 000 NOK/år**.

#### 3. Krav til tilbudets utforming og tilbudsfrist
* Alle priskomponenter (effektiv rentemargin, provisjoner, påslag i øre/kWh, fastbeløp og forsikringspremier) skal spesifiseres uten skjulte gebyrer.
* Revidert resultat- og balanseoppstilling etter NS 4102 (Styrepakke) oversendes ved signert konfidensialitetserklæring.
* **Tilbudsfrist:** Innen 14 dager fra mottak av denne forespørselen.

*Med vennlig hilsen,*
**Ledelsen / CFO – Bedrift AS**
                """
            )


# Bakoverkompatibelt alias
render_negotiation_and_bidding = render_negotiation_and_bidding_mockup
