summary = analyze_data(parsed_events)
    eda_results = perform_eda(df)
    precursor_df = find_precursor_patterns(df)

st.header("Job Performance Dashboard")
st.markdown("---")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Lot ID", str(summary.get('lot_id', 'N/A')))
c2.metric("Total Panels", int(summary.get('panel_count', 0)))
c3.metric("Job Duration (sec)", f"{summary.get('total_duration_sec', 0.0):.2f}")
c4.metric("Avg Cycle Time (sec)", f"{summary.get('avg_cycle_time_sec', 0.0):.2f}")

with st.expander("Show Advanced Analysis"):
    st.subheader("Event Frequency")
    if not eda_results.get('event_counts', pd.Series()).empty: st.bar_chart(eda_results['event_counts'])
    else: st.info("No events to analyze.")
    
    st.subheader("Alarm Analysis")
    if not eda_results.get('alarm_table', pd.DataFrame()).empty:
        st.write("Alarm Counts:"); st.bar_chart(eda_results['alarm_counts'])
        st.write("Alarm Events Log:"); st.dataframe(eda_results['alarm_table'], use_container_width=True)
    else: st.success("✅ No Alarms Found in Log")

    st.subheader("Predictive Maintenance Insights")
    if not precursor_df.empty:
        st.write("Warning patterns that occurred before critical failures:")
        st.dataframe(precursor_df, hide_index=True, use_container_width=True)
    else:
        st.success("✅ No predictive failure patterns detected.")

st.header("Detailed Event Log")
if not df.empty:
    df.columns = [col.replace('details.', '') for col in df.columns]
    cols = ["timestamp", "msg_name", "EventName", "LotID", "PanelCount", "MagazineID", "OperatorID", "PortID", "PortStatus", "AlarmID"]
    display_cols = [col for col in cols if col in df.columns]
    st.dataframe(df[display_cols], hide_index=True)
else:
    st.warning("No meaningful events were found.")
