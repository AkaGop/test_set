# app.py
import streamlit as st
import pandas as pd
from log_parser import parse_log_file
from config import CEID_MAP
from analyzer import analyze_data, perform_eda

st.set_page_config(page_title="Hirata Log Analyzer - Final", layout="wide")
st.title("Hirata Equipment Log Analyzer - Final")

with st.sidebar:
    st.title("🤖 Log Analyzer")
    uploaded_file = st.file_uploader("Upload Hirata Log File", type=['txt', 'log'])
    st.info("This tool provides engineering analysis of Hirata SECS/GEM logs.")

if uploaded_file:
    with st.spinner("Analyzing log file..."):
        parsed_events = parse_log_file(uploaded_file)
        df = pd.json_normalize(parsed_events)
        
        # --- START OF HIGHLIGHTED FINAL FIX ---
        # This logic block is now fully defensive and handles all cases.

        # 1. Initialize EventName column safely.
        if 'EventName' not in df.columns:
            df['EventName'] = "Unknown"

        # 2. Populate from CEID if available.
        if 'details.CEID' in df.columns:
            df['EventName'] = pd.to_numeric(df['details.CEID'], errors='coerce').map(CEID_MAP).fillna("Unknown")
        
        # 3. Populate any remaining Unknowns from RCMD, only if RCMD column exists.
        if 'details.RCMD' in df.columns:
            # Use .loc with a boolean mask to safely fill in only the necessary rows.
            # This requires 'EventName' to exist first.
            df.loc[df['EventName'] == "Unknown", 'EventName'] = df['details.RCMD']
        
        # --- END OF HIGHLIGHTED FINAL FIX ---

        summary = analyze_data(parsed_events)
        eda_results = perform_eda(df)

    st.header("Job Performance Dashboard")
    st.markdown("---")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Lot ID", str(summary.get('lot_id', 'N/A')))
    c2.metric("Total Panels", int(summary.get('panel_count', 0)))
    c3.metric("Job Duration (sec)", f"{summary.get('total_duration_sec', 0.0):.2f}")
    c4.metric("Avg Cycle Time (sec)", f"{summary.get('avg_cycle_time_sec', 0.0):.2f}")
    
    with st.expander("Show Exploratory Data Analysis (EDA)"):
        st.subheader("Event Frequency")
        if not eda_results.get('event_counts', pd.Series()).empty: st.bar_chart(eda_results['event_counts'])
        else: st.info("No events to analyze.")
        st.subheader("Alarm Analysis")
        if not eda_results.get('alarm_table', pd.DataFrame()).empty:
            st.write("Alarm Counts:"); st.bar_chart(eda_results['alarm_counts'])
            st.write("Alarm Events Log:"); st.dataframe(eda_results['alarm_table'], use_container_width=True)
        else: st.success("✅ No Alarms Found in Log")

    st.header("Detailed Event Log")
    if not df.empty:
        df.columns = [col.replace('details.', '') for col in df.columns]
        cols = ["timestamp", "msg_name", "EventName", "LotID", "PanelCount", "MagazineID", "OperatorID", "PortID", "PortStatus", "AlarmID"]
        display_cols = [col for col in cols if col in df.columns]
        st.dataframe(df[display_cols], hide_index=True)
    else: st.warning("No meaningful events were found.")
else:
    st.title("Welcome"); st.info("⬅️ Upload a log file to begin analysis.")
