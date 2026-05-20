1	import streamlit as st
2	import pandas as pd
3	import datetime
4
5	def is_off_peak(time_obj, start_time, end_time):
6	    """Determines if a given time falls within the defined off-peak window."""
7	    return start_time <= time_obj <= end_time
8
9	st.set_page_config(page_title="Energy Bill Calculator", layout="wide", page_icon="⚡")
10
11	st.title("⚡ Energy Bill Data Analyzer")
12	st.markdown("Upload your smart meter half-hourly or hourly consumption data to calculate your exact costs.")
13
14	# --- Input Controls: File Uploader and Tariff Configuration ---
15	st.subheader("📊 Input Data & Settings")
16	st.markdown("Use the columns below to upload your data and configure your tariff rules.")
17	st.markdown("---")
18
19	col1, col2 = st.columns([1, 3])
20
21	with col1:
22	    st.subheader("📥 Data Upload")
23	    uploaded_file = st.file_uploader("Upload your Smart Meter CSV", type=["csv"])
24
25	with col2:
26	    st.subheader("⚙️ Tariff Configuration")
27	    tariff_type = st.radio("Tariff Type", ["Flat Rate", "Dual-Rate (Peak/Off-Peak)"])
28
29	    # Shared settings display
30	    if tariff_type == "Flat Rate":
31	        standing_charge = st.number_input("Standing Charge (p/day)", min_value=0.0, value=50.0, step=0.1) / 100
32	        peak_rate = st.number_input("Unit Rate (p/kWh)", min_value=0.0, value=25.0, step=0.1) / 100
33	        off_peak_rate = peak_rate
34	        off_peak_start = datetime.time(0, 0)
35	        off_peak_end = datetime.time(0, 0)
36	    else:
37	        peak_rate = st.number_input("Peak Unit Rate (p/kWh)", min_value=0.0, value=30.0, step=0.1) / 100
38	        off_peak_rate = st.number_input("Off-Peak Unit Rate (p/kWh)", min_value=0.0, value=15.0, step=0.1) / 100
39	        off_peak_start = st.time_input("Start Time", datetime.time(0, 0))
40	        off_peak_end = st.time_input("End Time", datetime.time(6, 0))
41
42
43	# --- Main Calculation ---
44	st.markdown("---")
45
46	if uploaded_file is not None:
47	    try:
48	        # Read CSV
49	        df = pd.read_csv(uploaded_file)
50
51	        # Clean columns (strip whitespace/lowercase for easier matching)
52	        df.columns = df.columns.str.strip().str.lower()
53
54	        # Identify columns dynamically
55	        time_col = next((col for col in df.columns if 'time' in col or 'date' in col), None)
56	        usage_col = next((col for col in df.columns if 'use' in col or 'consumption' in col or 'kwh' in col), None)
57
58	        if not time_col or not usage_col:
59	            st.error("Could not automatically find timestamp or consumption columns. Please ensure your CSV has headers like 'Timestamp' and 'kWh'.")
60	            st.write("Detected columns:", list(df.columns))
61	            st.stop()
62
63	        # Parse data
64	        df[time_col] = pd.to_datetime(df[time_col])
65	        df[usage_col] = pd.to_numeric(df[usage_col], errors='coerce').fillna(0)
66
67	        # Date range calculations
68	        min_date = df[time_col].min()
69	        max_date = df[time_col].max()
70	        total_days = max((max_date - min_date).days, 1)
71
72	        # Apply tariff rates based on time windows
73	        if tariff_type == "Dual-Rate (Peak/Off-Peak)":
74	            df['is_off_peak'] = df[time_col].apply(lambda x: is_off_peak(x.time(), off_peak_start, off_peak_end))
75	            df['rate'] = df['is_off_peak'].map({True: off_peak_rate, False: peak_rate})
76	        else:
77	            df['is_off_peak'] = False
78	            df['rate'] = peak_rate
79
80	        df['cost'] = df[usage_col] * df['rate']
81
82	        # Summary metrics
83	        total_kwh = df[usage_col].sum()
84	        total_usage_cost = df['cost'].sum()
85	        total_standing_cost = total_days * standing_charge
86	        grand_total = total_usage_cost + total_standing_cost
87
88	        # Metrics Display
89	        st.subheader(f"📊 Bill Summary ({min_date.strftime('%Y-%m-%d')} to {max_date.strftime('%Y-%m-%d')})")
90
91	        col3, col4 = st.columns(2)
92	        col3.metric("Total Usage", f"{total_kwh:,.2f} kWh")
93	        col4.metric("Estimated Bill Total", f"£{grand_total:,.2f}", delta_color="inverse")
94
95	        # Visual Breakdowns
96	        st.markdown("---")
97
98	        left_chart, right_chart = st.columns(2)
99
100	        with left_chart:
101	            st.subheader("Daily Usage Breakdown")
102	            df['date'] = df[time_col].dt.date
103	            daily_summary = df.groupby('date').agg({usage_col: 'sum', 'cost': 'sum'}).reset_index()
104	            st.bar_chart(data=daily_summary, x='date', y=usage_col, use_container_width=True)
105
106	        with right_chart:
107	            st.subheader("Cost Structure")
108	            if tariff_type == "Dual-Rate (Peak/Off-Peak)":
109	                peak_kwh = df[~df['is_off_peak']][usage_col].sum()
110	                off_peak_kwh = df[df['is_off_peak']][usage_col].sum()
111
112	                breakdown_df = pd.DataFrame({
113	                    'Category': ['Standing Charge', 'Peak Usage Cost', 'Off-Peak Usage Cost'],
114	                    'Cost (£)': [total_standing_cost, df[~df['is_off_peak']]['cost'].sum(), df[df['is_off_peak']]['cost'].sum()]
115	                })
116	                st.dataframe(breakdown_df, hide_index=True, use_container_width=True)
117	                st.caption(f"Peak Usage: {peak_kwh:,.2f} kWh | Off-Peak Usage: {off_peak_kwh:,.2f} kWh")
118	            else:
119	                breakdown_df = pd.DataFrame({
120	                    'Category': ['Standing Charge', 'Usage Cost'],
121	                    'Cost (£)': [total_standing_cost, total_usage_cost]
122	                })
123	                st.dataframe(breakdown_df, hide_index=True, use_container_width=True)
124
125	        # Raw Data View
126	        with st.expander("🔍 View Cleaned Source Data"):
127	            st.dataframe(df[[time_col, usage_col, 'rate', 'cost']], use_container_width=True)
128
129	    except Exception as e:
130	        st.error(f"Error processing file: {e}")