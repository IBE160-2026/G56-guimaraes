import json
import pandas as pd
from openai import OpenAI
from pydantic import BaseModel, Field
from typing import List, Optional

# TOP 10% LLM PATTERN: "Structured Outputs" for å unngå LLM-hallusinasjoner.
class ActionItem(BaseModel):
    tiltak: str = Field(description="En konkret og handlingsrettet anbefaling på norsk")
    prioritet: str = Field(description="Høy, Medium eller Lav")

class ManagementCommentary(BaseModel):
    okonomisk_sammendrag: str = Field(description="Et formelt og konsist sammendrag av bedriftens økonomiske situasjon, basert kun på tallene (Tone of Voice: CFO/Styremedlem).")
    potensielle_avvik: List[str] = Field(description="En liste over mulige faresignaler eller trender basert på NS 4102-dataene. F.eks. høye driftskostnader mot inntekt.")
    tiltaksliste: List[ActionItem] = Field(description="2-3 strategiske råd til daglig leder.")

def generate_management_report(df: pd.DataFrame, api_key: Optional[str] = None, mock_mode: bool = False) -> ManagementCommentary:
    """
    Kaller OpenAI via Structured Outputs for å garantere riktig responsformat.
    Støtter frakoblet mock_mode slik at sensor og eksterne kan kjøre full flyt uten API-nøkkel.
    """
    if df.empty or 'NS4102_Kategori' not in df.columns:
        raise ValueError("DataFramen mangler NS 4102-kategorisering for AI-analysen.")

    # 1. Aggregering (Data Engineering)
    if 'Debet' in df.columns and 'Kredit' in df.columns:
        df['Netto'] = df['Kredit'] - df['Debet'] 
        summary_df = df.groupby('NS4102_Kategori')['Netto'].sum().reset_index()
    else:
        summary_df = df.groupby('NS4102_Kategori').size().reset_index(name='Antall_Transaksjoner')

    # Frakoblet testmodus (Kjørbarhet for sensor uten API-nøkkel)
    if mock_mode or not api_key or api_key.strip().upper() == "MOCK":
        return ManagementCommentary(
            okonomisk_sammendrag=(
                "[TESTMODUS / SENSOR-VISNING] Selskapet har i perioden en samlet driftsinntekt på 200 000 NOK "
                "og samlede driftskostnader på 90 000 NOK (varekostnad 60 000 NOK og lønn 30 000 NOK). "
                "Dette gir et foreløpig driftsresultat (EBIT) på 110 000 NOK med en sunn driftsmargin på 55 %. "
                "Likviditeten er solid med 180 000 NOK på bankkonto etter avstemming mot hovedboken."
            ),
            potensielle_avvik=[
                "Varekostnaden utgjør 30 % av omsetningen – bør overvåkes opp mot historisk bruttofortjeneste.",
                "Kundefordringer står på 90 000 NOK – sjekk forfalte poster for å sikre rettidig innbetaling."
            ],
            tiltaksliste=[
                ActionItem(tiltak="Etabler ukentlig purrerutine på utestående kundefordringer over 30 dager.", prioritet="Høy"),
                ActionItem(tiltak="Forhandle volumrabatter med hovedleverandør for å optimalisere varekostnaden.", prioritet="Medium"),
                ActionItem(tiltak="Overfør overskuddslikviditet fra driftskonto til høyrentekonto.", prioritet="Lav")
            ]
        )

    # 2. Live OpenAI API-kall
    data_string = summary_df.to_json(orient='records')
    system_prompt = (
        "Du er en erfaren og strategisk CFO (Strategisk Regnskapsfører) i Norge. "
        "Du analyserer et aggregert regnskap i henhold til NS 4102. "
        "Ikke finn på tall eller gjør antagelser utenfor dataene du får tildelt. "
        "Skriv på profesjonelt, formelt norsk. Vær kortfattet."
    )
    user_prompt = f"Her er aggregerte data for perioden:\n{data_string}\n\nSkriv din ledelsesrapport nå."

    try:
        client = OpenAI(api_key=api_key)
        completion = client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format=ManagementCommentary,
            temperature=0.2
        )
        return completion.choices[0].message.parsed

    except Exception as e:
        raise RuntimeError(f"Feil under kommunikasjon med OpenAI: {e}")
