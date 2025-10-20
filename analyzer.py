# analyzer.py
from datetime import datetime
import pandas as pd
from collections import Counter
from config import ALARM_MAP, CRITICAL_ALARM_IDS

def find_precursor_patterns(df: pd.DataFrame, window_size: int = 5) -> pd.DataFrame:
    """Finds sequences of warning events that occur before a critical failure."""
    if 'details.AlarmID' not in df.columns:
        return pd.DataFrame()

    df['AlarmID_numeric'] = pd.to_numeric(df['details.AlarmID'], errors='coerce')
    critical_indices = df[df['AlarmID_numeric'].isin(CRITICAL_ALARM_IDS)].index.tolist()
    
    precursor_sequences = []
    for idx in critical_indices:
        start = max(0, idx - window_size)
        window_df = df.iloc[start:idx]
        
        warnings = window_df[
            (window_df['AlarmID_numeric'].notna()) &
            (~window_df['AlarmID_numeric'].isin(CRITICAL_ALARM_IDS))
        ]
        
        if not warnings.empty:
            sequence = tuple(warnings['EventName'].tolist())
            failed_alarm_id = int(df.loc[idx, 'AlarmID_numeric'])
            failed_alarm_name = ALARM_MAP.get(failed_alarm_id, f"Critical Alarm {failed_alarm_id}")
            precursor_sequences.append({"Pattern": " -> ".join(sequence), "Leads_To_Failure": failed_alarm_name})

    if not precursor_sequences:
        return pd.DataFrame()

    pattern_counts = Counter((seq['Pattern'], seq['Leads_To_Failure']) for seq in precursor_sequences)
    result = [{"Precursor Pattern": p, "Leads to Failure": f, "Occurrences": c} for (p, f), c in pattern_counts.items()]
    return pd.DataFrame(result).sort_values(by="Occurrences", ascending=False)

def perform_eda(df: pd.DataFrame) -> dict:
    # ... (This function is correct and unchanged) ...

def analyze_data(events: list) -> dict:
    # ... (This function is correct and unchanged) ...
