# app.py
import streamlit as st
import pandas as pd
from log_parser import parse_log_file
from config import CEID_MAP
from analyzer import analyze_data, perform_eda, find_precursor_patterns

st.set_page_config(page_title="Hirata Log Analyzer", layout="wide")
st.title("Hirata Equipment Log Analyzer")

with st.sidebar:
    st.title("🤖 Log Analyzer")
    uploaded_file = st.file_uploader("Upload Hirata Log File", type=['txt', 'log'])
    st.info("This tool provides engineering analysis of Hirata SECS/GEM logs.")

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
        precursor_df = find_precursor_patterns(df)

    st.header("Job Performance Dashboard")
    # ... (Dashboard metric display is correct and unchanged) ...

    # --- START OF HIGHLIGHTED CHANGE ---
    st.header("Overall Log Summary")
    st.markdown("---")
    colA, colB, colC = st.columns(3)
    
    with colA:
        st.subheader("Operators Found")
        st.dataframe(pd.DataFrame(list(summary.get('operators', [])), columns=["ID"]), hide_index=True, use_container_width=True)
    with colB:
        st.subheader("Magazines Found")
        st.dataframe(pd.DataFrame(list(summary.get('magazines', [])), columns=["ID"]), hide_index=True, use_container_width=True)
    with colC:
        st.subheader("Control State Changes")
        state_changes = summary.get('control_state_changes', [])
        if state_changes:
            st.dataframe(pd.DataFrame(state_changes), hide_index=True, use_container_width=True)
        else:
            st.info("No Local/Remote changes detected.")
    # --- END OF HIGHLIGHTED CHANGE ---

    # ... (EDA and Detailed Log sections are correct and unchanged) ...

else:
    st.title("Welcome"); st.info("⬅️ Upload a log file to begin analysis.")
