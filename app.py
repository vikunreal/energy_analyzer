import streamlit as st
import pandas as pd
import datetime

def is_off_peak(time_obj, start_time, end_time):
    """Determines if a given time falls within the defined off-peak window."""
    return start_time <= time_obj <= end_time

st.set_page_config(page_title="Energy Bill Calculator", layout="wide", page_icon="⚡")

st.title("⚡ Energy Bill Data Analyzer")
st.markdown("Upload your smart meter half-hourly or hourly consumption data to calculate your exact costs.")

# --- Input Controls: File Uploader and Tariff Configuration ---
st.subheader("📊 Input Data & Settings")
st.markdown("Use the columns below to upload your data and configure your tariff rules.")
st.markdown("---")

col1, col2 = st.columns([1, 3])

with col1:
    st.subheader("📥 Data Upload")
    uploaded_file = st.file_uploader("Upload your Smart Meter CSV", type=["csv"])

with col2:
    st.subheader("⚙️ Tariff Configuration")
    tariff_type = st.radio("Tariff Type", ["Flat Rate", "Dual-Rate (Peak/Off-Peak)"])

    # Shared settings display
    if tariff_type == "Flat Rate":
        standing_charge = st.number_input("Standing Charge (p/day)", min_value=0.0, value=50.0, step=0.1) / 100
        peak_rate = st.number_input("Unit Rate (p/kWh)", min_value=0.0, value=25.0, step=0.1) / 100
        off_peak_rate = peak_rate
        off_peak_start = datetime.time(0, 0)
        off_peak_end = datetime.time(0, 0)
    else:
        peak_rate = st.number_input("Peak Unit Rate (p/kWh)", min_value=0.0, value=30.0, step=0.1) / 100
        off_peak_rate = st.number_input("Off-Peak Unit Rate (p/kWh)", min_value=0.0, value=15.0, step=0.1) / 100
        off_peak_start = st.time_input("Start Time", datetime.time(0, 0))
        off_peak_end = st.time_input("End Time", datetime.time(6, 0))


# --- Main Calculation ---
st.markdown("---")

if uploaded_file is not None:
    try:
        # Read CSV
        df = pd.read_csv(uploaded_file)

        # Clean columns (strip whitespace/lowercase for easier matching)
        df.columns = df.columns.str.strip().str.lower()

        # Identify columns dynamically
        time_col = next((col for col in df.columns if 'time' in col or 'date' in col), None)
        usage_col = next((col for col in df.columns if 'use' in col or 'consumption' in col or 'kwh' in col), None)

        if not time_col or not usage_col:
            st.error("Could not automatically find timestamp or consumption columns. Please ensure your CSV has headers like 'Timestamp' and 'kWh'.")
            st.write("Detected columns:", list(df.columns))
            st.stop()

        # Parse data
        df[time_col] = pd.to_datetime(df[time_col])
        df[usage_col] = pd.to_numeric(df[usage_col], errors='coerce').fillna(0)

        # Date range calculations
        min_date = df[time_col].min()
        max_date = df[time_col].max()
        total_days = max((max_date - min_date).days, 1)

        # Apply tariff rates based on time windows
        if tariff_type == "Dual-Rate (Peak/Off-Peak)":
            df['is_off_peak'] = df[time_col].apply(lambda x: is_off_peak(x, off_peak_start, off_peak_end))
            df['rate'] = df['is_off_peak'].map({True: off_peak_rate, False: peak_rate})
        else:
            df['is_off_peak'] = False
            df['rate'] = peak_rate

        df['cost'] = df[usage_col] * df['rate']

        # Summary metrics
        total_kwh = df[usage_col].sum()
        total_usage_cost = df['cost'].sum()
        total_standing_cost = total_days * standing_charge
        grand_total = total_usage_cost + total_standing_cost

        # Metrics Display
        st.subheader(f"📊 Bill Summary ({min_date.strftime('%Y-%m-%d')} to {max_date.strftime('%Y-%m-%d')})")

        col3, col4 = st.columns(2)
        col3.metric("Total Usage", f"{total_kwh:,.2f} kWh")
        col4.metric("Estimated Bill Total", f"£{grand_total:,.2f}", delta_color="inverse")

        # Visual Breakdowns
        st.markdown("---")

        left_chart, right_chart = st.columns(2)

        with left_chart:
            st.subheader("Daily Usage Breakdown")
            df['date'] = df[time_col].dt.date
            daily_summary = df.groupby('date').agg({usage_col: 'sum', 'cost': 'sum'}).reset_index()
            st.bar_chart(data=daily_summary, x='date', y=usage_col, use_container_width=True)

        with right_chart:
            st.subheader("Cost Structure")
            if tariff_type == "Dual-Rate (Peak/Off-Peak)":
                peak_kwh = df[~df['is_off_peak']][usage_col].sum()
                off_peak_kwh = df[df['is_off_peak']][usage_col].sum()

                breakdown_df = pd.DataFrame({
                    'Category': ['Standing Charge', 'Peak Usage Cost', 'Off-Peak Usage Cost'],
                    'Cost (£)': [total_standing_cost, df[~df['is_off_peak']]['cost'].sum(), df[df['is_off_peak']]['cost'].sum()]
                })
                st.dataframe(breakdown_df, hide_index=True, use_container_width=True)
                st.caption(f"Peak Usage: {peak_kwh:,.2f} kWh | Off-Peak Usage: {off_peak_kwh:,.2f} kWh")
            else:
                breakdown_df = pd.DataFrame({
                    'Category': ['Standing Charge', 'Usage Cost'],
                    'Cost (£)': [total_standing_cost, total_usage_cost]
                })
                st.dataframe(breakdown_df, hide_index=True, use_container_width=True)

        # Raw Data View
        with st.expander("🔍 View Cleaned Source Data"):
            st.dataframe(df[[time_col, usage_col, 'rate', 'cost']], use_container_width=True)

    except Exception as e:
        st.error(f"Error processing file: {e}")