import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io

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

# Sidebar for user interaction
st.sidebar.header("Dashboard Options")
st.sidebar.write("Paste your utility bill data below to analyze it!")

# Text area for user input
st.sidebar.subheader("Paste Your Utility Bill Data")
user_input = st.sidebar.text_area("Enter data in the format: Start Date, End Date, Days, kWh Used, Total Charges ($), Blended Rate ($/kWh) per row, separated by tabs or commas", height=300)

def parse_utility_data(input_text):
    """Parse the user-input text into a DataFrame."""
    try:
        # Split the input into lines and remove empty lines
        lines = [line.strip() for line in input_text.split('\n') if line.strip()]
        
        # Initialize lists to store data
        dates, days, kwh, charges, rates = [], [], [], [], []
        
        for line in lines:
            # Split by tabs or commas (handle both formats)
            parts = [part.strip() for part in line.replace('\t', ',').split(',')]
            if len(parts) >= 6:  # Ensure we have all required fields
                dates.append(pd.to_datetime(parts[0], format="%m/%d/%Y"))
                days.append(int(parts[2]))
                kwh.append(int(parts[3].replace(',', '')))
                charges.append(float(parts[4].replace('$', '').replace(',', '')))
                rates.append(float(parts[5]))
        
        # Create DataFrame
        df = pd.DataFrame({
            "Start Date": dates,
            "End Date": [pd.to_datetime(parts[1], format="%m/%d/%Y") for parts in 
                         [line.replace('\t', ',').split(',') for line in lines if line.strip()] if len(parts) >= 6],
            "Days": days,
            "kWh Used": kwh,
            "Total Charges ($)": charges,
            "Blended Rate ($/kWh)": rates
        })
        df["Month"] = df["Start Date"].dt.strftime("%B %Y")
        return df
    except Exception as e:
        st.error(f"Error parsing data: {e}. Please ensure the format is correct (e.g., '4/10/2023\t5/9/2023\t29\t672490\t134973\t0.2007').")
        return None

# Parse the input when submitted
if user_input:
    df = parse_utility_data(user_input)
    if df is not None and not df.empty:
        # Main dashboard layout
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Summary Statistics")
            st.write(f"**Account Number:** Not specified (add in input if available)")
            st.write(f"**Service Address:** Not specified (add in input if available)")
            st.write(f"**Total kWh Used:** {df['kWh Used'].sum():,.0f} kWh")
            st.write(f"**Total Cost:** ${df['Total Charges ($)'].sum():,.2f}")
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
    else:
        st.error("No valid data provided. Please check the format and try again.")
else:
    st.info("Please paste your utility bill data in the sidebar to start the analysis. Use the format: 'Start Date\tEnd Date\tDays\tkWh Used\tTotal Charges ($)\tBlended Rate ($/kWh)' per line, with tabs or commas separating values.")

# Example placeholder in the main area
st.write("Paste your utility bill data in the sidebar to generate the analysis and visualizations. Here's an example format for a single row:")
st.code("4/10/2023\t5/9/2023\t29\t672490\t134973\t0.2007")
