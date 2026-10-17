import pandas as pd
import io
import xml.etree.ElementTree as ET

def process_csv_in_memory(file_buffer: io.BytesIO, filename: str) -> pd.DataFrame:
    """
    Sikker in-memory prosessering av CSV-filer.
    Laster filen direkte inn i Pandas DataFrame uten å berøre disken.
    """
    try:
        # Laster filen fra buffer
        df = pd.read_csv(file_buffer)
        return df
    except Exception as e:
        raise ValueError(f"Kunne ikke parse CSV-filen {filename}: {e}")

def process_excel_in_memory(file_buffer: io.BytesIO, filename: str) -> dict:
    """
    In-memory prosessering av Excel-filer. Returnerer en dict med ark-navn og DataFrames.
    """
    try:
        # Laster filen fra buffer (krever openpyxl for .xlsx)
        df_dict = pd.read_excel(file_buffer, sheet_name=None)
        return df_dict
    except Exception as e:
        raise ValueError(f"Kunne ikke parse Excel-filen {filename}: {e}")

def parse_saft_xml_iterative(file_buffer: io.BytesIO) -> dict:
    """
    TOP 10% ELITE DATA PIPELINE PATTERN:
    Iterativ parsing av SAF-T XML (Standard Audit File - Tax).
    Bruk av iterparse forhindrer minnelekkasjer på filer opp mot flere Gigabyte.
    Extracter grunnleggende metadata og kontoinformasjon som en start.
    """
    metadata = {}
    accounts = []
    
    # iterparse lar oss lese XML-noder en etter en uten å laste hele treet i RAM
    context = ET.iterparse(file_buffer, events=("start", "end"))
    
    try:
        for event, elem in context:
            # Fjern namespace for enklere tag-matching
            tag = elem.tag.split('}')[-1]
            
            if event == "end" and tag == "Company":
                # Eksempel: Trekker ut selskapsnavn
                name_elem = elem.find('.//*Name')
                if name_elem is not None:
                    metadata['CompanyName'] = name_elem.text
            
            elif event == "end" and tag == "Account":
                # Eksempel: Trekker ut kontodetaljer fra MasterFiles
                account_id = elem.find('.//*AccountID')
                account_desc = elem.find('.//*AccountDescription')
                if account_id is not None and account_desc is not None:
                    accounts.append({
                        "AccountID": account_id.text,
                        "Description": account_desc.text
                    })
            
            # Frigjør minne kontinuerlig for å bevare RAM
            if event == "end":
                elem.clear()
                
    except ET.ParseError as e:
        raise ValueError(f"Ugyldig eller korrupt SAF-T XML struktur: {e}")
        
    return {
        "metadata": metadata,
        "accounts_preview": pd.DataFrame(accounts).head(10) if accounts else pd.DataFrame()
    }
