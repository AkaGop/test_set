# analyzer.py
from datetime import datetime
import pandas as pd

def perform_eda(df: pd.DataFrame) -> dict:
    """
    Performs Exploratory Data Analysis on the parsed log data.
    This function is now robust against missing columns.
    """
    eda_results = {}

    # Event Frequency Analysis
    if 'EventName' in df.columns:
        eda_results['event_counts'] = df['EventName'].value_counts()
    else:
        eda_results['event_counts'] = pd.Series(dtype='int64')

    # Alarm Analysis
    if 'details.AlarmID' in df.columns:
        alarm_events = df[df['details.AlarmID'].notna()].copy()
        if not alarm_events.empty:
            alarm_ids = pd.to_numeric(alarm_events['details.AlarmID'], errors='coerce').dropna()
            eda_results['alarm_counts'] = alarm_ids.value_counts()
            eda_results['alarm_table'] = alarm_events[['timestamp', 'EventName', 'details.AlarmID']]
        else:
            eda_results['alarm_counts'] = pd.Series(dtype='int64')
            eda_results['alarm_table'] = pd.DataFrame()
    else:
        # If the 'details.AlarmID' column doesn't exist at all.
        eda_results['alarm_counts'] = pd.Series(dtype='int64')
        eda_results['alarm_table'] = pd.DataFrame()
        
    return eda_results

def analyze_data(events: list) -> dict:
    """
    Analyzes a list of parsed events to calculate high-level KPIs.
    This function is robust and handles various job scenarios.
    """
    summary = {
        "operators": set(), "magazines": set(), "lot_id": "N/A", "panel_count": 0,
        "job_start_time": "N/A", "job_end_time": "N/A", "total_duration_sec": 0.0,
        "avg_cycle_time_sec": 0.0, "job_status": "No Job Found",
        "anomalies": [], "alarms": [], "control_state_changes": []
    }

    if not events: return summary

    # Find the first LOADSTART command to define the start of a potential job.
    start_event = next((e for e in events if e.get('details', {}).get('RCMD') == 'LOADSTART'), None)
    
    if start_event:
        # If a job starts, populate the known info.
        summary['lot_id'] = start_event['details'].get('LotID', 'N/A')
        try:
            summary['panel_count'] = int(start_event['details'].get('PanelCount', 0))
        except (ValueError, TypeError):
             summary['panel_count'] = 0
        summary['job_start_time'] = start_event['timestamp']
        summary['job_status'] = "Started but did not complete"
        
        # Search forward from the start event for a completion event.
        start_index = events.index(start_event)
        end_event = next((e for e in events[start_index:] if e.get('details', {}).get('CEID') in [131, 132]), None)
        
        if end_event:
            summary['job_status'] = "Completed"
            summary['job_end_time'] = end_event.get('timestamp')
            try:
                t_start = datetime.strptime(start_event['timestamp'], "%Y/%m/%d %H:%M:%S.%f")
                t_end = datetime.strptime(end_event['timestamp'], "%Y/%m/%d %H:%M:%S.%f")
                duration = (t_end - t_start).total_seconds()
                if duration >= 0:
                    summary['total_duration_sec'] = round(duration, 2)
                    if summary['panel_count'] > 0:
                        summary['avg_cycle_time_sec'] = round(duration / summary['panel_count'], 2)
            except (ValueError, TypeError):
                summary['job_status'] = "Time Calculation Error"
    else:
        # If no LOADSTART, check for other panel activity.
        panel_activity = any(e.get('details', {}).get('CEID') in [120, 127] for e in events)
        if panel_activity:
            summary['lot_id'] = "Dummy/Test Panels"

    # Aggregate summary data from all events in the log.
    for event in events:
        details = event.get('details', {})
        if details.get('OperatorID'): summary['operators'].add(details['OperatorID'])
        if details.get('MagazineID'): summary['magazines'].add(details['MagazineID'])
        if str(details.get('Result', '')).startswith("Failure"):
            summary['anomalies'].append(f"{event['timestamp']}: Host command failed.")
        if details.get('AlarmID'):
            summary['alarms'].append(f"{event['timestamp']}: Alarm {details['AlarmID']} occurred.")
        
        ceid = details.get('CEID')
        if ceid == 12: summary['control_state_changes'].append({"Timestamp": event['timestamp'], "State": "LOCAL"})
        elif ceid == 13: summary['control_state_changes'].append({"Timestamp": event['timestamp'], "State": "REMOTE"})
            
    return summary
