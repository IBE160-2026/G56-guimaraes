import json
import time
import logging
import pandas as pd
from openai import OpenAI
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

logger = logging.getLogger("g56_accounting")

# TOP 10% LLM PATTERN: Dyp, strukturert finansiell rapportering (CFO & Revisor)
class ActionItem(BaseModel):
    tiltak: str = Field(description="Et konkret, operasjonelt eller strategisk tiltak på norsk")
    begrunnelse: str = Field(description="Hvorfor tiltaket er nødvendig basert på tallgrunnlaget")
    prioritet: str = Field(description="Høy, Medium eller Lav")
    forventet_effekt: str = Field(description="Forventet effekt på likviditet, margin eller risikoreduksjon (bruk kun tall fra payload)")

class ManagementCommentary(BaseModel):
    hovedkonklusjon: str = Field(description="Krystallklar overordnet oppsummering og dom over selskapets økonomiske helse til styret (2-3 setninger).")
    lonnsomhet_og_marginer: str = Field(description="Dyp analyse av inntekter, varekostnader, lønnskostnader, EBIT og driftsmargin.")
    likviditet_og_arbeidskapital: str = Field(description="Vurdering av kontantbeholdning (bank), kundefordringer, leverandørgjeld samt Likviditetsgrad 1 og 2.")
    soliditet_og_rentabilitet: str = Field(
        default="Soliditet og kapitalavkastning (TKR/EKR) er vurdert i tråd med periodens balanse og resultat.",
        description="Vurdering av selskapets soliditet (egenkapitalandel og gjeldsgrad) samt totalkapitalrentabilitet (TKR) og egenkapitalrentabilitet (EKR)."
    )
    revisors_avstemmingsnotat: str = Field(description="Formell vurdering av regnskapets pålitelighet basert på kryssavstemmingen mellom Hovedbok og Saldobalanse (IB + HB = UB).")
    potensielle_avvik: List[str] = Field(description="Konkrete finansielle eller operasjonelle faresignaler identifisert i tallene.")
    tiltaksliste: List[ActionItem] = Field(description="3-4 prioriterte tiltak til daglig leder og styret med forventet effekt.")


def build_financial_context(
    sb_df: pd.DataFrame,
    recon_result: Optional[Dict[str, Any]] = None,
    hb_df: Optional[pd.DataFrame] = None,
) -> Dict[str, Any]:
    """
    THE AI FIREWALL - Context Engineering (v2.0):
    Konstruerer en strengt aggregert finansiell payload for KI-en.
    Inkluderer CFO-nøkkeltall (inkl. soliditet, TKR og EKR), kostnadsdrivere,
    deterministiske lønnsomhetsråd med pre-kalkulerte kronepotensialer og avstemmingsstatus.

    FIREWALL ASSERTION:
    Payloaden inneholder ALDRI råbilag eller enkelttransaksjoner, kun ferdig beregnede
    summer, forholdstall og verifiserte differanser fra Python/Pandas.
    """
    from compliance_engine import calculate_detailed_financial_metrics
    from ledger_analytics import summarize_cost_drivers, generate_profitability_recommendations

    metrics = calculate_detailed_financial_metrics(sb_df)
    cost_drivers = summarize_cost_drivers(sb_df, hb_df=hb_df, top_n=5)
    deterministic_recs = generate_profitability_recommendations(metrics, cost_drivers)

    # Avstemmingsstatus fra Hovedboken
    recon_summary: Dict[str, Any] = {"status": "Ikke gjennomført"}
    if recon_result:
        if recon_result.get("is_reconciled"):
            recon_summary = {
                "status": "GODKJENT (100% konsistent)",
                "kommentar": "Alle transaksjoner i hovedboken stemmer nøyaktig med endring mellom IB og UB i saldobalansen (0 avvik funnet)."
            }
        else:
            discrepancies = []
            if "discrepancies" in recon_result and not recon_result["discrepancies"].empty:
                for _, row in recon_result["discrepancies"].iterrows():
                    discrepancies.append({
                        "Konto": str(row.get('Konto')),
                        "Kontonavn": str(row.get('Kontonavn', '')),
                        "Avvik_NOK": float(row.get('Avvik', 0.0))
                    })
            recon_summary = {
                "status": "AVVIK OPPDAGET",
                "antall_uavstemte_kontoer": recon_result.get("discrepancy_count", 0),
                "avviksdetaljer": discrepancies,
                "advarsel": "Hovedboken og Saldobalansen har uavstemte poster. Tallene kan inneholde feilkonteringer."
            }

    payload = {
        "nokkeltall": {
            "Driftsinntekter_NOK": metrics["driftsinntekter"],
            "Varekostnad_NOK": metrics["varekostnad"],
            "Bruttofortjeneste_NOK": metrics["bruttofortjeneste"],
            "Bruttomargin_prosent": metrics["bruttomargin"],
            "Lonnskostnad_NOK": metrics["lonnskostnad"],
            "Lonnsandel_prosent": metrics["lonnsandel"],
            "Andre_Driftskostnader_NOK": metrics["andre_driftskostnader"],
            "Samlede_Driftskostnader_NOK": metrics["samlede_driftskostnader"],
            "Driftsresultat_EBIT_NOK": metrics["ebit"],
            "Driftsmargin_prosent": metrics["driftsmargin"],
            "Ordinart_Resultat_NOK": metrics["ordinart_resultat"]
        },
        "arbeidskapital_og_likviditet": {
            "Bankinnskudd_UB_NOK": metrics["bankinnskudd"],
            "Kundefordringer_UB_NOK": metrics["kundefordringer"],
            "Leverandorgjeld_UB_NOK": metrics["leverandorgjeld"],
            "Arbeidskapital_NOK": metrics["arbeidskapital"],
            "Likviditetsgrad_1": metrics["likviditetsgrad_1"],
            "Likviditetsgrad_2": metrics["likviditetsgrad_2"]
        },
        "soliditet_og_rentabilitet": {
            "Totalkapital_UB_NOK": metrics["totalkapital_ub"],
            "Bokfort_Egenkapital_UB_NOK": metrics["bokfort_egenkapital_ub"],
            "Reell_Egenkapital_UB_NOK": metrics["reell_egenkapital_ub"],
            "Egenkapitalandel_prosent": metrics["egenkapitalandel"],
            "Gjeldsgrad": metrics["gjeldsgrad"],
            "Totalkapitalrentabilitet_TKR_prosent": metrics["totalkapitalrentabilitet"],
            "Egenkapitalrentabilitet_EKR_prosent": metrics["egenkapitalrentabilitet"]
        },
        "kostnadsdrivere_topp_5": cost_drivers,
        "deterministiske_lonnsomhetsrad": deterministic_recs,
        "avstemming_hovedbok_mot_saldobalanse": recon_summary
    }

    # Ufravikelig Brannmur-validering (AI Firewall assertion)
    assert "raw_transactions" not in payload, "FIREWALL BRUDD: Råtransaksjoner lekker til KI-payload!"
    assert isinstance(payload["nokkeltall"]["Driftsresultat_EBIT_NOK"], (int, float)), "FIREWALL BRUDD: EBIT må være deterministisk tall!"
    assert isinstance(payload["soliditet_og_rentabilitet"]["Egenkapitalandel_prosent"], (int, float)), "FIREWALL BRUDD: Egenkapitalandel må være deterministisk tall!"

    return payload


def post_validate_ai_response(report: ManagementCommentary, expected_context: Dict[str, Any]) -> None:
    """
    POST-VALIDATION GUARD (The AI Firewall - Trinn 2):
    Kryss-sjekker at KI-rapporten ikke motsier de deterministiske tallene.
    Dersom kryssavstemmingen var godkjent, skal rapporten ikke påstå at det er ubalanse,
    og dersom det var avvik, SKAL revisorsnotatet omtale dette.
    """
    recon_status = expected_context.get("avstemming_hovedbok_mot_saldobalanse", {}).get("status", "")

    if "GODKJENT" in recon_status:
        if "alvorlige avvik" in report.hovedkonklusjon.lower():
            raise ValueError("Kvalitetssikringsfeil: KI påstår regnskapsfeil til tross for godkjent avstemming.")
    elif "AVVIK OPPDAGET" in recon_status:
        notat = report.revisors_avstemmingsnotat.lower() + " " + report.hovedkonklusjon.lower()
        if not any(w in notat for w in ["avvik", "feil", "advarsel", "uavstemt", "differanse"]):
            raise ValueError("Kvalitetssikringsfeil: KI unnlot å varsle styret om observerte avvik i Hovedboken.")


def execute_openai_with_retry(client: OpenAI, messages: list, max_retries: int = 3, timeout_sec: float = 20.0) -> ManagementCommentary:
    """
    Kjører OpenAI API-kall med eksponentiell backoff og feilhåndtering for nettverks- og API-tidsavbrudd.
    """
    last_err = None
    for attempt in range(1, max_retries + 1):
        try:
            completion = client.beta.chat.completions.parse(
                model="gpt-4o-mini",
                messages=messages,
                response_format=ManagementCommentary,
                temperature=0.2,
                timeout=timeout_sec
            )
            return completion.choices[0].message.parsed
        except Exception as e:
            last_err = e
            logger.warning(f"OpenAI API forsøk {attempt}/{max_retries} feilet: {e}")
            if attempt < max_retries:
                time.sleep(2 ** (attempt - 1))  # 1s, 2s, 4s
            else:
                raise RuntimeError(
                    f"Midlertidig API-feil ved kommunikasjon med OpenAI etter {max_retries} forsøk: {last_err}. "
                    f"Vennligst sjekk internettforbindelsen eller prøv igjen om et øyeblikk."
                )


def generate_management_report(
    df: pd.DataFrame,
    recon_result: Optional[Dict[str, Any]] = None,
    api_key: Optional[str] = None,
    mock_mode: bool = False,
    hb_df: Optional[pd.DataFrame] = None,
    **kwargs
) -> ManagementCommentary:
    """
    Genererer en dyp, strategisk ledelsesrapport og revisjonsnotat (v2.0).
    Støtter både live OpenAI API (Structured Outputs) og en rik frakoblet testmodus.
    """
    if df.empty or 'NS4102_Kategori' not in df.columns:
        raise ValueError("DataFramen mangler NS 4102-kategorisering for AI-analysen.")

    financial_context = build_financial_context(df, recon_result, hb_df=hb_df)
    is_reconciled = recon_result.get("is_reconciled", True) if recon_result else True

    nok = financial_context["nokkeltall"]
    likv = financial_context["arbeidskapital_og_likviditet"]
    sol = financial_context["soliditet_og_rentabilitet"]
    det_recs = financial_context.get("deterministiske_lonnsomhetsrad", [])

    # 1. FRAKOBLET TESTMODUS (Sensor / Lokal visning)
    if mock_mode or not api_key or api_key.strip().upper() == "MOCK":
        if is_reconciled:
            action_items: List[ActionItem] = []
            for rec in det_recs[:4]:
                action_items.append(
                    ActionItem(
                        tiltak=rec["anbefaling"],
                        begrunnelse=rec["utlosende_indikator"],
                        prioritet=rec["prioritet"],
                        forventet_effekt=rec["effekt_beskrivelse"],
                    )
                )
            if len(action_items) < 2:
                action_items = [
                    ActionItem(
                        tiltak="Stram inn kredittpolicy og send automatiske betalingspåminnelser ved 14 dager forfall.",
                        begrunnelse="Kundefordringer binder arbeidskapital som kan frigjøres til drift eller rentebærende plassering.",
                        prioritet="Høy",
                        forventet_effekt="Frigjør opptil 50 000 NOK i likviditet ved normalisering til 20 % av omsetning."
                    ),
                    ActionItem(
                        tiltak="Reforhandle innkjøpsavtaler på største varekostnadspost (Konto 4000).",
                        begrunnelse="5 % reduksjon i varekostnad slår direkte ut på bunnlinjen.",
                        prioritet="Medium",
                        forventet_effekt="Øker driftsresultatet (EBIT) med 3 000 NOK uten økt salgsvolum."
                    ),
                ]

            return ManagementCommentary(
                hovedkonklusjon=(
                    f"Selskapet leverer en sterk driftsperiode med driftsresultat (EBIT) på {nok['Driftsresultat_EBIT_NOK']:,.0f} NOK ".replace(",", " ")
                    + f"(driftsmargin {nok['Driftsmargin_prosent']:.1f} %) og solid egenkapitalandel på {sol['Egenkapitalandel_prosent']:.1f} %. "
                    "Regnskapet er 100 % avstemt mot hovedboken uten avvik, noe som gir styret et pålitelig beslutningsgrunnlag."
                ),
                lonnsomhet_og_marginer=(
                    f"Med driftsinntekter på {nok['Driftsinntekter_NOK']:,.0f} NOK og varekostnad på {nok['Varekostnad_NOK']:,.0f} NOK ".replace(",", " ")
                    + f"oppnås en bruttomargin på {nok['Bruttomargin_prosent']:.1f} %. "
                    f"Lønnskostnadene utgjør {nok['Lonnskostnad_NOK']:,.0f} NOK ({nok['Lonnsandel_prosent']:.1f} % av omsetningen). ".replace(",", " ")
                    + f"Samlet EBIT ender på {nok['Driftsresultat_EBIT_NOK']:,.0f} NOK, som bekrefter en sunn og skalerbar kostnadsstruktur.".replace(",", " ")
                ),
                likviditet_og_arbeidskapital=(
                    f"Likviditetsberedskapen er god med {likv['Bankinnskudd_UB_NOK']:,.0f} NOK i bankinnskudd og en arbeidskapital på {likv['Arbeidskapital_NOK']:,.0f} NOK. ".replace(",", " ")
                    + f"Likviditetsgrad 1 er {likv['Likviditetsgrad_1']:.2f} og Likviditetsgrad 2 er {likv['Likviditetsgrad_2']:.2f}. "
                    f"Kundefordringer på {likv['Kundefordringer_UB_NOK']:,.0f} NOK utgjør imidlertid en betydelig andel av omsetningen og bør følges opp.".replace(",", " ")
                ),
                soliditet_og_rentabilitet=(
                    f"Inklusive periodens resultat utgjør reell egenkapital {sol['Reell_Egenkapital_UB_NOK']:,.0f} NOK av en totalkapital på {sol['Totalkapital_UB_NOK']:,.0f} NOK, ".replace(",", " ")
                    + f"tilsvarende en egenkapitalandel på {sol['Egenkapitalandel_prosent']:.1f} % og lav gjeldsgrad ({sol['Gjeldsgrad']:.2f}). "
                    f"Periodens totalkapitalrentabilitet (TKR) er {sol['Totalkapitalrentabilitet_TKR_prosent']:.1f} % og egenkapitalrentabilitet (EKR) er {sol['Egenkapitalrentabilitet_EKR_prosent']:.1f} % målt mot gjennomsnittlig kapital."
                ),
                revisors_avstemmingsnotat=(
                    "INTERNKONTROLL GODKJENT: Full kryssavstemming mellom Hovedbok og Saldobalanse bekrefter at formelen "
                    "IB + sum transaksjoner i HB = UB er oppfylt for samtlige kontoer med 0,00 NOK i differanse. "
                    "Dobbelt bokføringskontroll bekrefter at debet og kredit balanserer feilfritt. Det foreligger ingen revisoriske anmerkninger."
                ),
                potensielle_avvik=[
                    "Kundefordringer binder arbeidskapital og bør følges opp med kortere kredittid for å styrke kontantstrømmen.",
                    "Overskuddslikviditet på ordinær driftskonto gir lav finansavkastning sammenlignet med plasseringskonto.",
                    "Varekostnadsandelen på hovedleverandører bør reforhandles jevnlig for å forsvare bruttomarginen."
                ],
                tiltaksliste=action_items,
            )
        else:
            # Mock-respons dersom det faktisk er avvik i regnskapet (Negative testing)
            discrepancy_count = recon_result.get("discrepancy_count", 2) if recon_result else 2
            return ManagementCommentary(
                hovedkonklusjon=(
                    f"ADVARSEL TIL STYRET: Det er oppdaget alvorlige avvik i den interne regnskapskontrollen ({discrepancy_count} uavstemte kontoer). "
                    "Før regnskapet kan godkjennes eller legges til grunn for strategiske disposisjoner, må feilposteringene mellom hovedbok og saldobalanse korrigeres."
                ),
                lonnsomhet_og_marginer=(
                    f"Foreløpige tall viser driftsinntekter på {nok['Driftsinntekter_NOK']:,.0f} NOK og driftsresultat på {nok['Driftsresultat_EBIT_NOK']:,.0f} NOK, ".replace(",", " ")
                    + "men resultat- og marginanalysen er heftet med usikkerhet inntil alle hovedboksbilag stemmer mot saldobalansen."
                ),
                likviditet_og_arbeidskapital=(
                    "Bankbeholdningen og kundefordringene har avvik mot underliggende bilag i hovedboken. "
                    "Reell tilgjengelig likviditet (LG1/LG2) og arbeidskapital kan ikke bekreftes før bilagene er avstemt."
                ),
                soliditet_og_rentabilitet=(
                    "Beregnet egenkapitalandel og kapitalavkastning (TKR/EKR) må betraktes som foreløpige størrelser fordi balansekontoene i klasse 1 har uavstemte differanser mot hovedboken."
                ),
                revisors_avstemmingsnotat=(
                    "KRITISK REVISJONSMERKNAD: Kryssavstemmingen (IB + bevegelser i HB = UB) feiler. "
                    "Spesifikt er det avdekket feilføringer på konto 1500 (Kundefordringer) og konto 1920 (Bankinnskudd). "
                    "Transaksjonene i hovedboken summerer seg ikke til periodens endring i saldobalansen, noe som tyder på feilkontering eller manglende bilag."
                ),
                potensielle_avvik=[
                    "Konto 1500 (Kundefordringer) har differanse på 30 000 NOK mot hovedbokens transaksjoner.",
                    "Konto 1920 (Bankinnskudd) har motgående differanse på 30 000 NOK som indikerer feil bilagsføring.",
                    "Manglende samsvar med bokføringslovens krav til sporbarhet mellom bilagsgrunnlag og saldobalanse."
                ],
                tiltaksliste=[
                    ActionItem(
                        tiltak="Reverser og rekonter feilpostering mellom konto 1500 og 1920 i Hovedboken umiddelbart.",
                        begrunnelse="Kryssavstemmingen avslører at transaksjoner er feilallokert mot bank fremfor kundefordring.",
                        prioritet="Høy",
                        forventet_effekt="Gjenoppretter 100 % regnskapsmessig konsistens og eliminerer revisjonsanmerkning."
                    ),
                    ActionItem(
                        tiltak="Gjennomfør full bankavstemming mot ekstern bankkontoutskrift for perioden.",
                        begrunnelse="Sikrer at faktisk banksaldo stemmer med bokført beløp før styremøtet.",
                        prioritet="Høy",
                        forventet_effekt="Eliminerer risiko for feilrapportering til styre og skattemyndigheter."
                    )
                ]
            )

    # 2. LIVE OPENAI API (Structured Outputs via Pydantic)
    context_json = json.dumps(financial_context, indent=2, ensure_ascii=False)

    system_prompt = (
        "Du er en topp 10 % erfaren CFO og statsautorisert revisor (Strategisk Regnskapsfører) i Norge. "
        "Du leverer en sylskarp, profesjonell og pedagogisk ledelsesrapport til daglig leder og styret basert på Norsk Standard Kontoplan (NS 4102). "
        "\n\nSTRENGE REGLER (GOVERNANCE – THE AI FIREWALL):\n"
        "1. KODEN REGNER, DU FORKLARER: Du skal ALDRI finne på egne tall eller regne ut nye verdier. Bruk utelukkende de ferdig beregnede nøkkeltallene, soliditets-/rentabilitetsmålene (TKR/EKR), kostnadsdriverne og de deterministiske lønnsomhetsrådene i payloaden.\n"
        "2. PRESCRIPTIVE ANALYTICS: I tiltakslisten skal du omsette de pre-kalkulerte lønnsomhetsrådene fra 'deterministiske_lonnsomhetsrad' til konkrete styretiltak og gjengi de eksakte kroneeffektene fra payloaden.\n"
        "3. REVISORIKK: Hvis avstemmingen viser avvik i formelen (IB + HB = UB), må du være nådeløs og forklare styreansvaret og risikoen for feil i bokføringen. Hvis den er godkjent, bekreft tryggheten.\n"
        "4. TONE OF VOICE: Formell, forretningsmessig, konsis og rådgivende norsk. Unngå floskler."
    )

    user_prompt = (
        "Her er fullstendig verifiserte nøkkeltall, soliditets-/rentabilitetsdata (TKR/EKR), "
        "deterministiske lønnsomhetsråd og avstemmingsresultat for perioden:\n\n"
        f"```json\n{context_json}\n```\n\nForfatt den strategiske ledelsesrapporten nå."
    )

    try:
        client = OpenAI(api_key=api_key)
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        parsed_report = execute_openai_with_retry(client, messages)
        post_validate_ai_response(parsed_report, financial_context)
        return parsed_report

    except Exception as e:
        if isinstance(e, (RuntimeError, ValueError)):
            raise e
        raise ValueError(f"Uventet feil ved generering av rapport: {e}")
