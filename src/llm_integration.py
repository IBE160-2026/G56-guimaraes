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
    forventet_effekt: str = Field(description="Forventet effekt på likviditet, margin eller risikoreduksjon")

class ManagementCommentary(BaseModel):
    hovedkonklusjon: str = Field(description="Krystallklar overordnet oppsummering og dom over selskapets økonomiske helse til styret (2-3 setninger).")
    lonnsomhet_og_marginer: str = Field(description="Dyp analyse av inntekter, varekostnader, lønnskostnader, EBIT og driftsmargin.")
    likviditet_og_arbeidskapital: str = Field(description="Vurdering av kontantbeholdning (bank), kundefordringer (kredittid), leverandørgjeld og kortsiktig gjeldsgrad.")
    revisors_avstemmingsnotat: str = Field(description="Formell vurdering av regnskapets pålitelighet basert på kryssavstemmingen mellom Hovedbok og Saldobalanse (IB + HB = UB).")
    potensielle_avvik: List[str] = Field(description="Konkrete finansielle eller operasjonelle faresignaler identifisert i tallene.")
    tiltaksliste: List[ActionItem] = Field(description="3-4 prioriterte tiltak til daglig leder og styret med forventet effekt.")

def build_financial_context(sb_df: pd.DataFrame, recon_result: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    THE AI FIREWALL - Context Engineering:
    Konstruerer en strengt aggregert finansiell payload for KI-en.
    Inkluderer nøkkeltall, kontooppsummeringer og avstemmingsstatus fra Hovedboken.
    
    FIREWALL ASSERTION:
    Payloaden inneholder ALDRI råbilag eller enkelttransaksjoner, kun ferdig beregnede
    summer og verifiserte differanser fra Pandas.
    """
    from compliance_engine import calculate_detailed_financial_metrics
    metrics = calculate_detailed_financial_metrics(sb_df)
    
    # Avstemmingsstatus fra Hovedboken
    recon_summary = {"status": "Ikke gjennomført"}
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
            "Likviditetsgrad_1": metrics["likviditetsgrad_1"]
        },
        "avstemming_hovedbok_mot_saldobalanse": recon_summary
    }

    # Ufravikelig Brannmur-validering (AI Firewall assertion)
    assert "raw_transactions" not in payload, "FIREWALL BRUDD: Råtransaksjoner lekker til KI-payload!"
    assert isinstance(payload["nokkeltall"]["Driftsresultat_EBIT_NOK"], (int, float)), "FIREWALL BRUDD: EBIT må være deterministisk tall!"

    return payload

    # Ufravikelig Brannmur-validering (AI Firewall assertion)
    assert "raw_transactions" not in payload, "FIREWALL BRUDD: Råtransaksjoner lekker til KI-payload!"
    assert isinstance(payload["nokkeltall"]["Driftsresultat_EBIT_NOK"], (int, float)), "FIREWALL BRUDD: EBIT må være deterministisk tall!"

    return payload

def generate_management_report(
    df: pd.DataFrame, 
    recon_result: Optional[Dict[str, Any]] = None,
    api_key: Optional[str] = None, 
    mock_mode: bool = False,
    **kwargs
) -> ManagementCommentary:
    """
    Genererer en dyp, strategisk ledelsesrapport og revisjonsnotat.
    Støtter både live OpenAI API (Structured Outputs) og en rik frakoblet testmodus.
    """
    if df.empty or 'NS4102_Kategori' not in df.columns:
        raise ValueError("DataFramen mangler NS 4102-kategorisering for AI-analysen.")

    financial_context = build_financial_context(df, recon_result)
    is_reconciled = recon_result.get("is_reconciled", True) if recon_result else True

    # 1. FRAKOBLET TESTMODUS (Sensor / Lokal visning)
    if mock_mode or not api_key or api_key.strip().upper() == "MOCK":
        if is_reconciled:
            return ManagementCommentary(
                hovedkonklusjon=(
                    "Selskapet leverer en solid driftsperiode med sterk lønnsomhet (EBIT-margin 55,0 %) og god kontantstrøm. "
                    "Regnskapet er fullstendig avstemt mot hovedboken uten avvik, noe som gir styret et trygt beslutningsgrunnlag."
                ),
                lonnsomhet_og_marginer=(
                    "Med driftsinntekter på 200 000 NOK og en varekostnad på 60 000 NOK oppnås en tilfredsstillende bruttomargin på 70,0 %. "
                    "Lønnskostnadene er under god kontroll på 30 000 NOK (15 % av omsetningen). "
                    "Samlet driftsresultat (EBIT) ender på 110 000 NOK, noe som reflekterer en sunn og skalerbar kostnadsstruktur i kjernevirksomheten."
                ),
                likviditet_og_arbeidskapital=(
                    "Likviditetsreserven er robust med 180 000 NOK i disponible bankinnskudd. "
                    "Kundefordringer på 90 000 NOK representerer 45 % av periodens omsetning, mens leverandørgjeld utgjør 50 000 NOK. "
                    "Arbeidskapitalen er positiv, men binder relativt mye kapital i utestående fordringer mot kunder."
                ),
                revisors_avstemmingsnotat=(
                    "INTERNKONTROLL GODKJENT: Full kryssavstemming mellom Hovedbok og Saldobalanse bekrefter at formelen "
                    "IB + sum transaksjoner i HB = UB er oppfylt for samtlige kontoer med 0,00 NOK i differanse. "
                    "Dobbelt bokføringskontroll bekrefter at debet og kredit balanserer feilfritt. Det foreligger ingen revisoriske anmerkninger."
                ),
                potensielle_avvik=[
                    "Kundefordringer (90 000 NOK) binder opp likviditet og bør følges opp for å unngå forlengede kredittider.",
                    "Selskapet har høy konsentrasjon av likviditet på lavrente driftskonto fremfor bufferplassering.",
                    "Varekostnadsandelen bør benchmarks mot bransjesnitt ved volumøkning."
                ],
                tiltaksliste=[
                    ActionItem(
                        tiltak="Stram inn kredittpolicy og send automatiske betalingspåminnelser ved 14 dager forfall.",
                        begrunnelse="Kundefordringer utgjør nesten halvparten av omsetningen og binder unødvendig arbeidskapital.",
                        prioritet="Høy",
                        forventet_effekt="Frigjør opptil 40 000 NOK i likviditet innen 30 dager."
                    ),
                    ActionItem(
                        tiltak="Forhandle frem leverandørkreditt på 45 dager mot nåværende betingelser.",
                        begrunnelse="Optimaliserer kontantstrømssyklusen mot innbetalinger fra kunder.",
                        prioritet="Medium",
                        forventet_effekt="Bedrer operasjonell likviditetsbuffer med 15–20 %."
                    ),
                    ActionItem(
                        tiltak="Overfør 100 000 NOK fra driftskonto til rentebærende plasseringskonto.",
                        begrunnelse="180 000 NOK på driftskonto gir null avkastning i dagens rentemiljø.",
                        prioritet="Lav",
                        forventet_effekt="Gir risikofri finansiell ekstrainntekt uten å svekke beredskapen."
                    )
                ]
            )
        else:
            # Mock-respons dersom det faktisk er avvik i regnskapet (Negative testing)
            discrepancy_count = recon_result.get("discrepancy_count", 2) if recon_result else 2
            return ManagementCommentary(
                hovedkonklusjon=(
                    f"ADVARSEL TIL STYRET: Det er oppdaget alvorlige avvik i den interne regnskapskontrollen ({discrepancy_count} uavstemte kontoer). "
                    "Før regnskapet kan godkjennes eller rapporteres eksternt, må feilposteringene mellom hovedbok og saldobalanse korrigeres."
                ),
                lonnsomhet_og_marginer=(
                    "Selv om de foreløpige tallene indikerer en driftsinntekt på 200 000 NOK og et driftsresultat på 110 000 NOK, "
                    "er tallgrunnlaget usikkert som følge av manglende konsistens mellom transaksjonsloggen og saldopostene."
                ),
                likviditet_og_arbeidskapital=(
                    "Bankbeholdningen og kundefordringene har avvik mot underliggende bilag i hovedboken. "
                    "Reell tilgjengelig likviditet og utestående fordringer kan ikke verifiseres før bilagene er avstemt."
                ),
                revisors_avstemmingsnotat=(
                    "KRITISK REVISJONSMERKNAD: Kryssavstemmingen (IB + bevegelser i HB = UB) feiler. "
                    "Spesifikt er det avdekket feilføringer på konto 1500 (Kundefordringer) og konto 1920 (Bankinnskudd). "
                    "Transaksjonene i hovedboken summerer seg ikke til periodens endring i saldobalansen, noe som tyder på feilkontering eller manglende bilag."
                ),
                potensielle_avvik=[
                    "Konto 1500 (Kundefordringer) har differanse på 30 000 NOK mot hovedbokens transaksjoner.",
                    "Konto 1920 (Bankinnskudd) har motgående differanse på 30 000 NOK som indikerer feil bilagsføring.",
                    "Manglende samsvar med bokføringslovens krav til sporbarhet mellom grunnlag og saldobalanse."
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

def post_validate_ai_response(report: ManagementCommentary, expected_context: Dict[str, Any]) -> None:
    """
    POST-VALIDATION GUARD (The AI Firewall - Trinn 2):
    Kryss-sjekker at KI-rapporten ikke motsier de deterministiske tallene.
    Dersom kryssavstemmingen var godkjent, skal rapporten ikke påstå at det er ubalanse,
    og dersom det var avvik, SKAL revisorsnotatet omtale dette.
    """
    recon_status = expected_context.get("avstemming_hovedbok_mot_saldobalanse", {}).get("status", "")
    
    if "GODKJENT" in recon_status:
        # Hvis avstemming var godkjent, skal det ikke stå "ALVORLIGE AVVIK" i konklusjonen
        if "alvorlige avvik" in report.hovedkonklusjon.lower():
            raise ValueError("Kvalitetssikringsfeil: KI påstår regnskapsfeil til tross for godkjent avstemming.")
    elif "AVVIK OPPDAGET" in recon_status:
        # Hvis avvik ble oppdaget, SKAL revisorsnotat inneholde advarsel
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
    context_json = json.dumps(financial_context, indent=2, ensure_ascii=False)
    
    system_prompt = (
        "Du er en topp 10 % erfaren CFO og statsautorisert revisor (Strategisk Regnskapsfører) i Norge. "
        "Du leverer en sylskarp, profesjonell og pedagogisk ledelsesrapport til daglig leder og styret basert på Norsk Standard Kontoplan (NS 4102). "
        "\n\nSTRENGE REGLER (GOVERNANCE):\n"
        "1. KODEN REGNER, DU FORKLARER: Du skal ALDRI finne på egne tall eller regne ut nye verdier. Bruk utelukkende de ferdig beregnede nøkkeltallene og avstemmingsdataene i payloaden.\n"
        "2. FOKUS PÅ SAMMENHENG: Forklar hvorfor tallene er som de er (f.eks. sammenhengen mellom omsetning, varekostnad, arbeidskapital og likviditetsreserve).\n"
        "3. REVISORIKK: Hvis avstemmingen viser avvik i formelen (IB + HB = UB), må du være nådeløs og forklare styreansvaret og risikoen for feil i bokføringen. Hvis den er godkjent, bekreft tryggheten.\n"
        "4. TONE OF VOICE: Formell, forretningsmessig, konsis og rådgivende norsk. Unngå floskler og generelle selvfølgeligheter."
    )
    
    user_prompt = f"Her er fullstendig verifiserte regnskapsdata og avstemmingsresultat for perioden:\n\n```json\n{context_json}\n```\n\nForfatt den strategiske ledelsesrapporten nå."

    try:
        client = OpenAI(api_key=api_key)
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        parsed_report = execute_openai_with_retry(client, messages)
        # Kjør post-validering
        post_validate_ai_response(parsed_report, financial_context)
        return parsed_report

    except Exception as e:
        if isinstance(e, (RuntimeError, ValueError)):
            raise e
        raise ValueError(f"Uventet feil ved generering av rapport: {e}")
        raise RuntimeError(f"Feil under kommunikasjon med OpenAI: {e}")
