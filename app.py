# app.py

import streamlit as st
import pandas as pd
from log_parser import parse_log_file
from config import CEID_MAP
from analyzer import analyze_data, perform_eda

st.set_page_config(
    page_title="Hirata Log Analyzer",
    page_icon="🤖",
    layout="wide"
)

# --- Sidebar ---
with st.sidebar:
    st.title("🤖 Hirata Log Analyzer")
    uploaded_file = st.file_uploader("Upload Log File", type=['txt', 'log'])
    st.write("---")
    st.header("About")
    st.info(
        "This tool provides engineering analysis of Hirata SECS/GEM logs, "
        "focusing on job performance, equipment states, and anomalies."
    )
    with st.expander("Metric Definitions"):
        st.markdown("""
        *   **Lot ID:** The unique ID for the batch. Defaults to 'Dummy/Test Panels' if panel movement is detected without a formal `LOADSTART` command.
        *   **Total Panels:** The number of panels specified in the job command.
        *   **Job Duration:** Total time from `LOADSTART` to job completion.
        *   **Avg Cycle Time:** The average time to process a single panel during the job.
        """)

# --- Main Page Display ---
if uploaded_file:
    with st.spinner("Analyzing log file..."):
        parsed_events = parse_log_file(uploaded_file)
        df = pd.json_normalize(parsed_events)
        
        # Enrich the DataFrame with a human-readable EventName column
        if 'details.CEID' in df.columns:
            df['EventName'] = pd.to_numeric(df['details.CEID'], errors='coerce').map(CEID_MAP).fillna("Unknown")
        if 'details.RCMD' in df.columns:
            df.loc[df['EventName'].isnull(), 'EventName'] = df['details.RCMD']
        
        # Perform analyses
        summary = analyze_data(parsed_events)
        eda_results = perform_eda(df)

    # --- KPI Dashboard ---
    st.header("Job Performance Dashboard")
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Lot ID", str(summary.get('lot_id', 'N/A')))
    col2.metric("Total Panels", int(summary.get('panel_count', 0)))
    col3.metric("Job Duration (sec)", f"{summary.get('total_duration_sec', 0.0):.2f}")
    col4.metric("Avg Cycle Time (sec)", f"{summary.get('avg_cycle_time_sec', 0.0):.2f}")

    # --- Overall Log Summary ---
    st.header("Overall Log Summary")
    st.markdown("---")
    colA, colB, colC, colD = st.columns([1, 1, 1, 2])
    
    with colA:
        st.subheader("Operators")
        st.dataframe(pd.DataFrame(list(summary.get('operators', [])), columns=["ID"]), hide_index=True, use_container_width=True)
    with colB:
        st.subheader("Magazines")
        st.dataframe(pd.DataFrame(list(summary.get('magazines', [])), columns=["ID"]), hide_index=True, use_container_width=True)
    with colC:
        st.subheader("State Changes")
        state_changes = summary.get('control_state_changes', [])
        if state_changes:
            st.dataframe(pd.DataFrame(state_changes), hide_index=True, use_container_width=True)
        else:
            st.info("No Local/Remote changes.")
    with colD:
        st.subheader("Alarms & Anomalies")
        alarms = summary.get('alarms', [])
        anomalies = summary.get('anomalies', [])
        if not alarms and not anomalies:
            st.success("✅ No Alarms or Anomalies Found")
        else:
            for alarm in alarms: st.warning(f"⚠️ {alarm}")
            for anomaly in anomalies: st.error(f"❌ {anomaly}")

    st.write("---")
    
    # --- Exploratory Data Analysis Section ---
    with st.expander("Show Exploratory Data Analysis (EDA)"):
        st.subheader("Event Frequency")
        if not eda_results.get('event_counts', pd.Series()).empty:
            st.bar_chart(eda_results['event_counts'])
        else:
            st.info("No events to analyze.")
            
        st.subheader("Alarm Analysis")
        if not eda_results.get('alarm_table', pd.DataFrame()).empty:
            st.write("Alarm Counts:")
            st.bar_chart(eda_results['alarm_counts'])
            st.write("Alarm Events Log:")
            st.dataframe(eda_results['alarm_table'], use_container_width=True)
        else:
            st.success("✅ No Alarms Found in Log")

    # --- Detailed Log Table ---
    st.header("Detailed Event Log")
    if not df.empty:
        cols_in_order = [
            "timestamp", "msg_name", "EventName", "details.LotID", "details.PanelCount",
            "details.MagazineID", "details.OperatorID", "details.PortID", "details.PortStatus", "details.AlarmID"
        ]
        display_cols = [col for col in cols_in_order if col in df.columns]
        st.dataframe(df[display_cols], hide_index=True)
        
        with st.expander("Show Raw JSON Data (for debugging)"):
            st.json(parsed_events)
    else:
        st.warning("No meaningful events were found.")

else:
    st.title("Welcome to the Hirata Log Analyzer")
    st.info("⬅️ Please upload a log file using the sidebar to begin.")
