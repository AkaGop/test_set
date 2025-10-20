# app.py

import streamlit as st
import pandas as pd
from log_parser import parse_log_file
from config import CEID_MAP
# Import the new pattern finding function
from analyzer import analyze_data, perform_eda, find_precursor_patterns 

st.set_page_config(page_title="Hirata Log Analyzer", layout="wide")
st.title("Hirata Equipment Log Analyzer")

with st.sidebar:
    # ... (sidebar code is unchanged) ...

if uploaded_file:
    with st.spinner("Analyzing log file..."):
        parsed_events = parse_log_file(uploaded_file)
        df = pd.json_normalize(parsed_events)
        
        # Data Enrichment
        if 'details.CEID' in df.columns:
            df['EventName'] = pd.to_numeric(df['details.CEID'], errors='coerce').map(CEID_MAP).fillna("Unknown")
        if 'details.RCMD' in df.columns:
            df.loc[df['EventName'].isnull(), 'EventName'] = df['details.RCMD']
        
        # Perform all analyses
        summary = analyze_data(parsed_events)
        eda_results = perform_eda(df)
        # --- NEW: Call the pattern finding function ---
        precursor_df = find_precursor_patterns(df)

    # ... (Dashboard and Summary sections are unchanged) ...

    # --- Exploratory Data Analysis (EDA) Section ---
    with st.expander("Show Exploratory Data Analysis (EDA)"):
        # ... (EDA code is unchanged) ...

    # --- START OF HIGHLIGHTED CHANGE ---
    # --- Predictive Maintenance Insights Section ---
    st.header("Predictive Maintenance Insights")
    st.markdown("---")
    st.subheader("High-Frequency Warning Patterns Before Failures")

    if not precursor_df.empty:
        st.write(
            "The table below shows sequences of 'soft' warning alarms that repeatedly occurred "
            "just before a critical, process-stopping 'hard' alarm. These are strong predictive indicators."
        )
        st.dataframe(precursor_df, hide_index=True, use_container_width=True)
    else:
        st.success("✅ No recurring warning patterns leading to critical failures were detected in this log.")
    # --- END OF HIGHLIGHTED CHANGE ---

    # --- Detailed Log Table ---
    st.header("Detailed Event Log")
    if not df.empty:
        # ... (DataFrame display logic is unchanged) ...
    
else:
    st.title("Welcome")
    st.info("⬅️ Please upload a log file using the sidebar to begin analysis.")
