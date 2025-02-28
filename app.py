import streamlit as st
import numpy as np
import numpy_financial as npf
import matplotlib.pyplot as plt

# Title
st.title("Project Financial Dashboard")

# Sidebar for Inputs
st.sidebar.header("Inputs")

# Project Cost
project_cost = st.sidebar.number_input("Project Cost ($)", min_value=0.0, value=200000.0, step=1000.0)

# Services Dropdown with Percentages
services = {
    "Lighting": 0.10,  # 10% of project cost
    "HVAC": 0.15,      # 15% of project cost
    "Solar": 0.20,     # 20% of project cost
    "Maintenance": 0.05 # 5% of project cost
}
selected_service = st.sidebar.selectbox("Select Service", list(services.keys()))
service_percentage = services[selected_service]

# Transfer Rate
transfer_rate = st.sidebar.number_input("Transfer Rate (%)", min_value=0.0, value=7.0, step=0.1) / 100

# Discount Rate (for NPV Margin)
discount_rate = st.sidebar.number_input("Discount Rate (%)", min_value=0.0, value=5.0, step=0.1) / 100

# Utility Cost Escalator
utility_cost_escalator = st.sidebar.number_input("Utility Cost Escalator (%)", min_value=0.0, value=2.0, step=0.1) / 100

# Assumptions
term_years = 5  # Fixed term of 5 years for simplicity
annual_savings = project_cost * service_percentage  # Savings based on service percentage

# Calculations
tcv = project_cost  # TCV assumed as project cost (adjustable)
cash_flows = [-project_cost] + [annual_savings * (1 + utility_cost_escalator)**t for t in range(term_years)]
npv = npf.npv(discount_rate, cash_flows)
irr = npf.irr(cash_flows)
irr_percent = irr * 100 if irr is not None else None
gross_margin_percent = (npv / tcv) * 100 if tcv != 0 else 0

# Main Display
st.header("Financial Summary")

# Key Metrics
st.subheader("Key Metrics")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Contract Value (TCV)", f"${tcv:,.2f}", delta_color="off")
with col2:
    st.metric("Net Present Value (NPV)", f"${npv:,.2f}", delta_color="normal")
with col3:
    st.metric("Internal Rate of Return (IRR)", f"{irr_percent:.1f}%" if irr_percent else "N/A", delta_color="normal")

# Service and Savings Details
st.subheader("Service Details")
st.write(f"**Selected Service:** {selected_service} ({service_percentage * 100:.0f}%)")
st.write(f"**Annual Savings (Year 1):** ${annual_savings:,.2f}")

# Cash Flow Chart
st.subheader("Cumulative Cash Flow")
years = list(range(term_years + 1))
cumulative_cf = np.cumsum(cash_flows)
fig, ax = plt.subplots(figsize=(6, 4))
ax.plot(years, cumulative_cf, marker='o', color='green', linewidth=2)
ax.set_xlabel("Year")
ax.set_ylabel("Cumulative Cash Flow ($)")
ax.grid(True, linestyle='--', alpha=0.7)
ax.set_title("Cash Flow Over Time")
plt.tight_layout()
st.pyplot(fig)

# Additional Info
st.subheader("Additional Metrics")
st.write(f"**Gross Margin (%):** {gross_margin_percent:.1f}%")
