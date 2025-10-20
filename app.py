# app.py
import streamlit as st
import pandas as pd
from log_parser import parse_log_file
from config import CEID_MAP
from analyzer import analyze_data, perform_eda, find_precursor_patterns

st.set_page_config(page_title="Hirata Log Analyzer - Final", layout="wide")
st.title("Hirata Equipment Log Analyzer - Final")

with st.sidebar:
    # ... (Sidebar code is correct and unchanged) ...

if uploaded_file:
    with st.spinner("Analyzing log file..."):
        parsed_events = parse_log_file(uploaded_file)
        df = pd.json_normalize(parsed_events)
        if 'details.CEID' in df.columns:
            df['EventName'] = pd.to_numeric(df['details.CEID'], errors='coerce').map(CEID_MAP).fillna("Unknown")
        if 'details.RCMD' in df.columns:
            df.loc[df['EventName'].isnull(), 'EventName'] = df['details.RCMD']
        
        summary = analyze_data(parsed_events)
        eda_results = perform_eda(df)
        precursor_df = find_precursor_patterns(df) # Call the new function

    # ... (Dashboard and Overall Summary are correct and unchanged) ...
    
    # --- START OF HIGHLIGHTED CHANGE ---
    # Re-integrating the EDA and Predictive Maintenance sections
    st.header("Advanced Analysis")
    st.markdown("---")

    with st.expander("Show Exploratory Data Analysis (EDA)"):
        st.subheader("Event Frequency")
        if not eda_results.get('event_counts', pd.Series()).empty: st.bar_chart(eda_results['event_counts'])
        else: st.info("No events to analyze.")
        
        st.subheader("Alarm Analysis")
        if not eda_results.get('alarm_table', pd.DataFrame()).empty:
            st.write("Alarm Counts:"); st.bar_chart(eda_results['alarm_counts'])
            st.write("Alarm Events Log:"); st.dataframe(eda_results['alarm_table'], use_container_width=True)
        else: st.success("✅ No Alarms Found in Log")

    with st.expander("Show Predictive Maintenance Insights"):
        st.subheader("High-Frequency Warning Patterns Before Failures")
        if not precursor_df.empty:
            st.write("The table below shows sequences of 'soft' warnings that repeatedly occurred just before a critical failure.")
            st.dataframe(precursor_df, hide_index=True, use_container_width=True)
        else:
            st.success("✅ No recurring failure patterns were detected in this log.")
    # --- END OF HIGHLIGHTED CHANGE ---

    st.header("Detailed Event Log")
    if not df.empty:
        # ... (DataFrame display logic is correct and unchanged) ...
else:
    st.title("Welcome")
    st.info("⬅️ Please upload a log file to begin analysis.")
