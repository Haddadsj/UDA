import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Set a sexy, modern theme for the dashboard
st.set_page_config(page_title="Utility Bill Dashboard", layout="wide", initial_sidebar_state="expanded")
st.markdown("""
    <style>
    .main {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    .stButton>button {
        background-color: #4a90e2;
        color: white;
        border-radius: 5px;
        padding: 10px 20px;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #357abd;
    }
    .stHeader {
        color: #2c3e50;
        font-size: 2.5em;
        font-weight: bold;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# Title of the dashboard
st.markdown('<h1 class="stHeader">Utility Bill Analysis Dashboard</h1>', unsafe_allow_html=True)

# Sample data from your input (Account No. 17558068023)
data = {
    "Start Date": ["4/10/2023", "5/10/2023", "6/9/2023", "7/11/2023", "8/9/2023", "9/8/2023", 
                   "10/10/2023", "11/8/2023", "12/9/2023", "1/9/2024", "2/8/2024", "3/11/2024", "4/10/2024"],
    "End Date": ["5/9/2023", "6/8/2023", "7/10/2023", "8/8/2023", "9/7/2023", "10/9/2023", 
                 "11/7/2023", "12/8/2023", "12/31/2023", "2/7/2024", "3/10/2024", "4/9/2024", "5/8/2024"],
    "Days": [29, 29, 31, 28, 29, 31, 28, 30, 22, 29, 31, 29, 28],
    "kWh Used": [672490, 689836, 728999, 699709, 735795, 785290, 724023, 704597, 666888, 679353, 716186, 689212, 700984],
    "Total Charges ($)": [134973, 141558, 171964, 195910, 206194, 199121, 177223, 167884, 162134, 187218, 178673, 168708, 173803],
    "Blended Rate ($/kWh)": [0.2007, 0.2052, 0.2359, 0.2800, 0.2802, 0.2536, 0.2448, 0.2383, 0.2431, 0.2756, 0.2495, 0.2448, 0.2479]
}

# Create a DataFrame
df = pd.DataFrame(data)
df["Start Date"] = pd.to_datetime(df["Start Date"], format="%m/%d/%Y")
df["End Date"] = pd.to_datetime(df["End Date"], format="%m/%d/%Y")
df["Month"] = df["Start Date"].dt.strftime("%B %Y")

# Sidebar for user interaction
st.sidebar.header("Dashboard Options")
account = st.sidebar.selectbox("Select Account", ["17558068023 (2411 Baumann Ave, San Lorenzo, CA)"])
st.sidebar.markdown("---")
st.sidebar.write("Analyze utility bills with interactive visualizations!")

# Main dashboard layout
col1, col2 = st.columns(2)

with col1:
    st.subheader("Summary Statistics")
    st.write(f"**Account Number:** {account}")
    st.write(f"**Service Address:** 2411 Baumann Ave, San Lorenzo, CA 94580")
    st.write(f"**Total Annual kWh Used:** {df['kWh Used'].sum():,.0f} kWh")
    st.write(f"**Total Annual Cost:** ${df['Total Charges ($)'].sum():,.2f}")
    st.write(f"**Average Blended Rate:** ${df['Blended Rate ($/kWh)'].mean():,.4f}/kWh")
    st.write(f"**Average Daily kWh Usage:** {df['kWh Used'].sum() / df['Days'].sum():,.2f} kWh/day")

with col2:
    st.subheader("Usage Trends Over Time")
    fig1 = plt.figure(figsize=(10, 6))
    sns.lineplot(data=df, x="Month", y="kWh Used", color="#4a90e2", marker="o")
    plt.xticks(rotation=45)
    plt.title("kWh Usage by Month", fontsize=14, pad=15)
    plt.xlabel("Month", fontsize=12)
    plt.ylabel("kWh Used", fontsize=12)
    st.pyplot(fig1)

# Interactive Plotly charts for a sexy, modern look
st.subheader("Detailed Visualizations")

# Line chart for kWh and Cost
fig2 = make_subplots(rows=1, cols=2, subplot_titles=("kWh Usage Over Time", "Total Charges Over Time"))

fig2.add_trace(
    go.Scatter(x=df["Month"], y=df["kWh Used"], mode="lines+markers", name="kWh Used", line=dict(color="#4a90e2")),
    row=1, col=1
)
fig2.add_trace(
    go.Scatter(x=df["Month"], y=df["Total Charges ($)"], mode="lines+markers", name="Total Charges ($)", line=dict(color="#e41a1c")),
    row=1, col=2
)

fig2.update_layout(
    title_text="Utility Usage and Cost Trends",
    height=600,
    width=1200,
    xaxis_title="Month",
    yaxis_title="kWh",
    xaxis2_title="Month",
    yaxis2_title="Total Charges ($)",
    showlegend=True,
    plot_bgcolor="#f0f2f6",
    paper_bgcolor="#f0f2f6",
    font=dict(color="#2c3e50")
)
st.plotly_chart(fig2, use_container_width=True)

# Bar chart for Blended Rates
st.subheader("Blended Rate Analysis")
fig3 = go.Figure()
fig3.add_trace(
    go.Bar(x=df["Month"], y=df["Blended Rate ($/kWh)"], marker_color="#4a90e2", name="Blended Rate ($/kWh)")
)
fig3.update_layout(
    title="Blended Electricity Rate by Month",
    xaxis_title="Month",
    yaxis_title="Blended Rate ($/kWh)",
    height=500,
    width=1000,
    plot_bgcolor="#f0f2f6",
    paper_bgcolor="#f0f2f6",
    font=dict(color="#2c3e50")
)
st.plotly_chart(fig3, use_container_width=True)

# Additional Analysis: Peak Usage and Cost Months
st.subheader("Peak Analysis")
peak_usage = df.loc[df["kWh Used"].idxmax()]
peak_cost = df.loc[df["Total Charges ($)"].idxmax()]
st.write(f"**Highest kWh Usage Month:** {peak_usage['Month']} ({peak_usage['kWh Used']:,} kWh, ${peak_usage['Total Charges ($)']:.2f})")
st.write(f"**Highest Cost Month:** {peak_cost['Month']} ({peak_cost['kWh Used']:,} kWh, ${peak_cost['Total Charges ($)']:.2f})")

# Optional: Add a download button for the data
st.subheader("Download Data")
csv = df.to_csv(index=False)
st.download_button(
    label="Download Data as CSV",
    data=csv,
    file_name="utility_bill_data.csv",
    mime="text/csv",
)

# Footer
st.markdown("---")
st.markdown('<p style="text-align: center; color: #7f8c8d;">Powered by Streamlit | Data Analysis by Your Utility Team</p>', unsafe_allow_html=True)
