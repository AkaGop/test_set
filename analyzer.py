# analyzer.py
from datetime import datetime
import pandas as pd
from collections import Counter
from config import ALARM_MAP, CRITICAL_ALARM_IDS

def find_precursor_patterns(df, window_size=5):
    if 'details.AlarmID' not in df.columns: return pd.DataFrame()
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
    if not precursor_sequences: return pd.DataFrame()
    counts = Counter((s['Pattern'], s['Leads_To_Failure']) for s in precursor_sequences)
    result = [{"Precursor Pattern": p, "Leads to Failure": f, "Occurrences": c} for (p, f), c in counts.items()]
    return pd.DataFrame(result).sort_values(by="Occurrences", ascending=False)

def perform_eda(df):
    eda = {}
    if 'EventName' in df.columns: eda['event_counts'] = df['EventName'].value_counts()
    else: eda['event_counts'] = pd.Series()
    if 'details.AlarmID' in df.columns:
        alarms = df[df['details.AlarmID'].notna()].copy()
        if not alarms.empty:
            ids = pd.to_numeric(alarms['details.AlarmID'], errors='coerce').dropna()
            eda['alarm_counts'] = ids.value_counts()
            eda['alarm_table'] = alarms[['timestamp', 'EventName', 'details.AlarmID']]
        else: eda['alarm_counts'], eda['alarm_table'] = pd.Series(), pd.DataFrame()
    else: eda['alarm_counts'], eda['alarm_table'] = pd.Series(), pd.DataFrame()
    return eda

def analyze_data(events):
    summary = {"operators": set(), "magazines": set(), "lot_id": "N/A", "panel_count": 0, "total_duration_sec": 0.0, "avg_cycle_time_sec": 0.0, "job_status": "No Job Found", "control_state_changes": []}
    if not events: return summary
    start = next((e for e in events if e.get('details', {}).get('RCMD') == 'LOADSTART'), None)
    if start:
        summary['lot_id'] = start['details'].get('LotID', 'N/A')
        if not summary['lot_id'] or summary['lot_id'] == 'N/A':
            summary['lot_id'] = next((e['details'].get('LotID') for e in events if e.get('details', {}).get('LotID')), 'N/A')
        try: summary['panel_count'] = int(start['details'].get('PanelCount', 0))
        except: summary['panel_count'] = 0
        summary['job_status'] = "Started but did not complete"
        start_idx = events.index(start)
        end = next((e for e in events[start_idx:] if e.get('details', {}).get('CEID') in [131, 132]), None)
        if end:
            summary['job_status'] = "Completed"
            try:
                t_s, t_e = datetime.strptime(start['timestamp'],"%Y/%m/%d %H:%M:%S.%f"), datetime.strptime(end['timestamp'],"%Y/%m/%d %H:%M:%S.%f")
                dur = (t_e - t_s).total_seconds()
                if dur >= 0:
                    summary['total_duration_sec'] = round(dur, 2)
                    if summary['panel_count'] > 0: summary['avg_cycle_time_sec'] = round(dur / summary['panel_count'], 2)
            except: summary['job_status'] = "Time Calc Error"
    else:
        if any(e.get('details', {}).get('CEID') in [120, 127] for e in events): summary['lot_id'] = "Dummy/Test Panels"
    for e in events:
        d = e.get('details', {})
        if d.get('OperatorID'): summary['operators'].add(d['OperatorID'])
        if d.get('MagazineID'): summary['magazines'].add(d['MagazineID'])
        ceid = d.get('CEID')
        if ceid == 12: summary['control_state_changes'].append({"Timestamp": e['timestamp'], "State": "LOCAL"})
        elif ceid == 13: summary['control_state_changes'].append({"Timestamp": e['timestamp'], "State": "REMOTE"})
    return summary
