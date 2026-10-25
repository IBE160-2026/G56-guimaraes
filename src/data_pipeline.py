import pandas as pd
import io
import re

def detect_csv_delimiter_and_encoding(file_bytes: bytes) -> tuple[str, str]:
    """
    Autodetekterer skilletegn (; vs , vs tab) og tegnsett (utf-8, utf-8-sig, latin1).
    Norske ERP-systemer som Fiken og Tripletex eksporterer ofte semikolon-separerte CSV-er.
    """
    # 1. Prøv vanlige tegnsett for norske regnskapsdata
    encoding = 'utf-8-sig'
    try:
        sample_text = file_bytes[:8192].decode('utf-8-sig')
    except UnicodeDecodeError:
        try:
            sample_text = file_bytes[:8192].decode('utf-8')
            encoding = 'utf-8'
        except UnicodeDecodeError:
            sample_text = file_bytes[:8192].decode('latin1', errors='replace')
            encoding = 'latin1'
            
    # 2. Tell forekomster på første linje (header)
    first_line = sample_text.split('\n')[0] if sample_text else ""
    semicolon_count = first_line.count(';')
    comma_count = first_line.count(',')
    tab_count = first_line.count('\t')
    
    if semicolon_count > comma_count and semicolon_count > tab_count:
        delimiter = ';'
    elif tab_count > comma_count and tab_count > semicolon_count:
        delimiter = '\t'
    else:
        delimiter = ','
        
    return delimiter, encoding

def normalize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normaliserer typiske norske og engelske kolonnenavn til standard konvensjoner:
    - 'Kontonr', 'Konto nr', 'Account', 'AccountID' -> 'Konto'
    - 'Kontonavn', 'Beskrivelse', 'AccountName' -> 'Kontonavn'
    - 'Debit' -> 'Debet'
    - 'Credit' -> 'Kredit'
    - 'Inngående balanse', 'Opening Balance' -> 'IB'
    - 'Utgående balanse', 'Closing Balance' -> 'UB'
    """
    column_mapping = {}
    for col in df.columns:
        clean_col = str(col).strip().lower()
        if clean_col in ['kontonr', 'konto nr', 'kontonummer', 'account', 'accountid', 'account_id', 'konto_nr']:
            column_mapping[col] = 'Konto'
        elif clean_col in ['kontonavn', 'konto navn', 'kontobeskrivelse', 'accountname', 'account_name', 'beskrivelse', 'tekst']:
            column_mapping[col] = 'Kontonavn'
        elif clean_col in ['debit']:
            column_mapping[col] = 'Debet'
        elif clean_col in ['credit']:
            column_mapping[col] = 'Kredit'
        elif clean_col in ['inngående balanse', 'inngående', 'opening balance', 'opening_balance', 'ib_beløp']:
            column_mapping[col] = 'IB'
        elif clean_col in ['utgående balanse', 'utgående', 'closing balance', 'closing_balance', 'ub_beløp']:
            column_mapping[col] = 'UB'
            
    if column_mapping:
        df = df.rename(columns=column_mapping)
        
    return df

def clean_norwegian_numeric_series(series: pd.Series) -> pd.Series:
    """
    Håndterer norske tallformater med desimalkomma og tusenskilletegn (f.eks. '15 000,50' eller '15.000,50').
    Konverterer trygt til float.
    """
    if pd.api.types.is_numeric_dtype(series):
        return pd.to_numeric(series, errors='coerce').fillna(0.0)
        
    def parse_norwegian_num(val):
        if pd.isna(val) or val == '':
            return 0.0
        val_str = str(val).strip()
        # Fjern vanlige tusenskilletegn (mellomrom, hardt mellomrom, apostrof)
        val_str = val_str.replace('\xa0', '').replace(' ', '').replace("'", "")
        
        # Hvis både punktum og komma finnes: '15.000,50' -> '15000.50'
        if '.' in val_str and ',' in val_str:
            val_str = val_str.replace('.', '').replace(',', '.')
        elif ',' in val_str:
            # Kun komma: '15000,50' -> '15000.50'
            val_str = val_str.replace(',', '.')
            
        try:
            return float(val_str)
        except ValueError:
            return 0.0

    return series.apply(parse_norwegian_num)

def process_csv_in_memory(file_buffer: io.BytesIO, filename: str) -> pd.DataFrame:
    """
    Skuddsikker in-memory CSV-leser for norske regnskapsdata:
    - Autodetekterer komma vs semikolon.
    - Håndterer desimalkomma (1000,50).
    - Normaliserer kolonnenavn (f.eks. Kontonr -> Konto).
    - Validerer at påkrevde kolonner finnes, med vennlige feilmeldinger.
    """
    try:
        raw_bytes = file_buffer.getvalue()
        if not raw_bytes or len(raw_bytes.strip()) == 0:
            raise ValueError(f"Filen '{filename}' er tom.")
            
        delimiter, encoding = detect_csv_delimiter_and_encoding(raw_bytes)
        
        # Les inn med Pandas
        file_buffer.seek(0)
        df = pd.read_csv(
            file_buffer,
            sep=delimiter,
            encoding=encoding,
            dtype=str  # Laster først inn som strenger for å bevare kontonumre med ledende nuller og rense tallformat
        )
        
        # 1. Normaliser kolonnenavn
        df = normalize_column_names(df)
        
        # 2. Fjern eventuelle tomme rader
        df = df.dropna(how='all')
        
        # 3. Valider obligatorisk kolonne
        if 'Konto' not in df.columns:
            funnede_kolonner = ", ".join([f"'{c}'" for c in df.columns])
            raise ValueError(
                f"Filen '{filename}' mangler den påkrevde kolonnen 'Konto' (eller 'Kontonr'). "
                f"Fant følgende kolonner: [{funnede_kolonner}]. Vennligst kontroller filformatet."
            )
            
        # 4. Rens numeriske kolonner dersom de finnes
        for num_col in ['Debet', 'Kredit', 'IB', 'UB']:
            if num_col in df.columns:
                df[num_col] = clean_norwegian_numeric_series(df[num_col])
                
        # 5. Sørg for at Konto forblir streng
        df['Konto'] = df['Konto'].astype(str).str.strip()
        
        return df

    except ValueError as ve:
        raise ve
    except Exception as e:
        raise ValueError(f"Kunne ikke lese CSV-filen '{filename}': {e}")

def process_excel_in_memory(file_buffer: io.BytesIO, filename: str) -> dict[str, pd.DataFrame]:
    """
    In-memory prosessering av Excel-filer (.xlsx).
    Normaliserer og vasker tallkolonner på samme måte som CSV.
    """
    try:
        raw_bytes = file_buffer.getvalue()
        if not raw_bytes or len(raw_bytes) == 0:
            raise ValueError(f"Excel-filen '{filename}' er tom.")
            
        file_buffer.seek(0)
        df_dict = pd.read_excel(file_buffer, sheet_name=None, dtype=str)
        
        cleaned_dict = {}
        for sheet_name, df in df_dict.items():
            df = normalize_column_names(df)
            df = df.dropna(how='all')
            for num_col in ['Debet', 'Kredit', 'IB', 'UB']:
                if num_col in df.columns:
                    df[num_col] = clean_norwegian_numeric_series(df[num_col])
            if 'Konto' in df.columns:
                df['Konto'] = df['Konto'].astype(str).str.strip()
            cleaned_dict[sheet_name] = df
            
        return cleaned_dict
    except Exception as e:
        raise ValueError(f"Kunne ikke lese Excel-filen '{filename}': {e}")
