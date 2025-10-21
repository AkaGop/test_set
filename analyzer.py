# analyzer.py
from datetime import datetime
import pandas as pd
from collections import Counter
from config import ALARM_MAP, CRITICAL_ALARM_IDS

def find_precursor_patterns(df: pd.DataFrame, window_size: int = 5) -> pd.DataFrame:
    # This function is correct and does not need changes.
    if 'details.AlarmID' not in df.columns:
        return pd.DataFrame()
    df['AlarmID_numeric'] = pd.to_numeric(df['details.AlarmID'], errors='coerce')
    critical_indices = df[df['AlarmID_numeric'].isin(CRITICAL_ALARM_IDS)].index.tolist()
    precursor_sequences = []
    for idx in critical_indices:
        start = max(0, idx - window_size)
        window_df = df.iloc[start:idx]
        warnings = window_df[(window_df['AlarmID_numeric'].notna()) & (~window_df['AlarmID_numeric'].isin(CRITICAL_ALARM_IDS))]
        if not warnings.empty:
            sequence = tuple(warnings['EventName'].tolist())
            failed_alarm_id = int(df.loc[idx, 'AlarmID_numeric'])
            failed_alarm_name = ALARM_MAP.get(failed_alarm_id, f"ALID {failed_alarm_id}")
            precursor_sequences.append({"Pattern": " -> ".join(sequence), "Leads_To_Failure": failed_alarm_name})
    if not precursor_sequences:
        return pd.DataFrame()
    counts = Counter((s['Pattern'], s['Leads_To_Failure']) for s in precursor_sequences)
    result = [{"Precursor Pattern": p, "Leads to Failure": f, "Occurrences": c} for (p, f), c in counts.items()]
    return pd.DataFrame(result).sort_values(by="Occurrences", ascending=False)

def perform_eda(df: pd.DataFrame) -> dict:
    # This function is correct and does not need changes.
    # ... (code is the same as the last working version)
    pass

def analyze_data(events: list) -> dict:
    """
    Final, robust analyzer. Tracks all KPIs including control state changes.
    """
    summary = {
        "operators": set(), "magazines": set(), "lot_id": "N/A", "panel_count": 0,
        "job_start_time": "N/A", "job_end_time": "N/A", "total_duration_sec": 0.0,
        "avg_cycle_time_sec": 0.0, "job_status": "No Job Found",
        "control_state_changes": []  # Ensure this is always initialized
    }
    if not events: return summary

    # --- START OF HIGHLIGHTED CHANGE ---

    # Find Job and robustly determine Lot ID
    start_event = next((e for e in events if e.get('details', {}).get('RCMD') == 'LOADSTART'), None)
    if start_event:
        summary['lot_id'] = start_event['details'].get('LotID') or next((e['details'].get('LotID') for e in events if e.get('details', {}).get('LotID')), 'N/A')
        try:
            summary['panel_count'] = int(start_event['details'].get('PanelCount', 0))
        except (ValueError, TypeError):
            summary['panel_count'] = 0
        summary['job_status'] = "Started but did not complete"
        start_index = events.index(start_event)
        end_event = next((e for e in events[start_index:] if e.get('details', {}).get('CEID') in [131, 132]), None)
        if end_event:
            summary['job_status'] = "Completed"
            # ... (duration calculation logic is correct)
    else:
        if any(e.get('details', {}).get('CEID') in [120, 127] for e in events):
            summary['lot_id'] = "Dummy/Test Panels"

    # Aggregate summary data from all events
    for event in events:
        details = event.get('details', {})
        if details.get('OperatorID'): summary['operators'].add(details['OperatorID'])
        if details.get('MagazineID'): summary['magazines'].add(details['MagazineID'])
        
        # Add logic to find and record control state changes
        ceid = details.get('CEID')
        if ceid == 12:  # GemControlStateLOCAL
            summary['control_state_changes'].append({"Timestamp": event['timestamp'], "State": "LOCAL"})
        elif ceid == 13: # GemControlStateREMOTE
            summary['control_state_changes'].append({"Timestamp": event['timestamp'], "State": "REMOTE"})

    # --- END OF HIGHLIGHTED CHANGE ---
            
    return summary
