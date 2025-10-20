# analyzer.py
from datetime import datetime
import pandas as pd
from collections import Counter
# Import the new critical alarm list
from config import ALARM_MAP, CRITICAL_ALARM_IDS 

def perform_eda(df: pd.DataFrame) -> dict:
    # ... (This function is correct and remains unchanged) ...

# --- START OF HIGHLIGHTED CHANGE ---

def find_precursor_patterns(df: pd.DataFrame, window_size: int = 5) -> pd.DataFrame:
    """
    Finds sequences of warning events that occur before a critical failure.
    """
    if 'details.AlarmID' not in df.columns:
        return pd.DataFrame()

    # Ensure AlarmID is numeric for comparison
    df['AlarmID_numeric'] = pd.to_numeric(df['details.AlarmID'], errors='coerce')
    
    # Find the index locations of all critical alarms
    critical_alarm_indices = df[df['AlarmID_numeric'].isin(CRITICAL_ALARM_IDS)].index.tolist()
    
    precursor_sequences = []
    
    for idx in critical_alarm_indices:
        # Define the window of events to look at before the critical alarm
        start_window = max(0, idx - window_size)
        end_window = idx
        
        # Get the slice of the DataFrame representing the events just before the failure
        window_df = df.iloc[start_window:end_window]
        
        # From that window, extract only the 'soft' warning alarms
        warnings_in_window = window_df[
            (window_df['AlarmID_numeric'].notna()) &
            (~window_df['AlarmID_numeric'].isin(CRITICAL_ALARM_IDS))
        ]
        
        if not warnings_in_window.empty:
            # Create a tuple of the warning event names to use as a sequence key
            sequence = tuple(warnings_in_window['EventName'].tolist())
            failed_alarm_id = int(df.loc[idx, 'AlarmID_numeric'])
            failed_alarm_name = ALARM_MAP.get(failed_alarm_id, "Unknown Critical Alarm")
            
            precursor_sequences.append({
                "Pattern": " -> ".join(sequence),
                "Leads_To_Failure": f"ALID {failed_alarm_id}: {failed_alarm_name}"
            })

    if not precursor_sequences:
        return pd.DataFrame()

    # Count the occurrences of each unique pattern-failure pair
    pattern_counts = Counter(
        (seq['Pattern'], seq['Leads_To_Failure']) for seq in precursor_sequences
    )
    
    # Format the results into a DataFrame
    result_list = [
        {"Precursor Pattern": pattern, "Leads to Failure": failure, "Occurrences": count}
        for (pattern, failure), count in pattern_counts.items()
    ]
    
    return pd.DataFrame(result_list).sort_values(by="Occurrences", ascending=False)

# --- END OF HIGHLIGHTED CHANGE ---

def analyze_data(events: list) -> dict:
    # ... (This function is correct and remains unchanged) ...
