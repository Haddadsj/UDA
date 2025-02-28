import streamlit as st
import numpy as np
import numpy_financial as npf
import matplotlib.pyplot as plt

# Title
st.title("Energy Services Financial Dashboard")

# Sidebar for Inputs
st.sidebar.header("Project Inputs")
project_cost = st.sidebar.number_input("Project Cost ($)", min_value=0.0, value=191345.0, step=1000.0)
transfer_rate = st.sidebar.number_input("Transfer Rate (%)", min_value=0.0, value=7.0, step=0.1) / 100
discount_rate = st.sidebar.number_input("Discount Rate (%)", min_value=0.0, value=7.0, step=0.1) / 100
utility_cost_escalator = st.sidebar.number_input("Utility Cost Escalator (%)", min_value=0.0, value=2.25, step=0.1) / 100

# Services Dropdown with Percentages
st.sidebar.header("Services")
services = {
    "Program Management": {
        "Redaptive Developed & Delivered": 0.10,
        "Customer Developed, Redaptive Delivered": 0.08,
        "Customer Developed & Delivered": 0.05
    },
    "Data and M&V": {
        "Off-Balance Sheet, Savings Guarantee": 0.07,
        "Off-Balance Sheet, Shared Savings/Usage Risk": 0.06,
        "Off-Balance Sheet, Generation": 0.05
    },
    "Incentives Management": {
        "State/Utility Incentives & Environmental Credits": 0.25,
        "State/Utility Incentives Only": 0.15,
        "Environmental Credits Only": 0.10
    },
    "Ongoing Maintenance": {
        "Full PM & RM": 0.05,
        "PM only / RM Pass-Through": 0.03,
        "Parts Only": 0.02,
        "Manufacturer’s Warranty Only": 0.01,
        "Customer Managed Maintenance": 0.00
    }
}

selected_services = {}
for service, options in services.items():
    selected_option = st.sidebar.selectbox(f"Select {service}", list(options.keys()))
    selected_services[service] = options[selected_option]

# Assumptions from Image Descriptions
term_years = 5  # Fixed term of 5 years
annual_payment = 59472.0  # Annual payment from the dashboard
y1_combined_savings = 69313.0  # Year 1 combined savings from the dashboard

# Calculations
tcv = annual_payment * term_years  # Total Contract Value
total_net_cost = project_cost  # Using project cost as total net cost
service_costs = sum([selected_services[service] * total_net_cost for service in selected_services])
initial_investment = total_net_cost + service_costs

# Cash Flows: Initial investment + annual savings adjusted by utility cost escalator
cash_flows = [-initial_investment] + [y1_combined_savings * (1 + utility_cost_escalator)**t for t in range(term_years)]

# NPV and IRR
npv = npf.npv(discount_rate, cash_flows)
irr = npf.irr(cash_flows)
irr_percent = irr * 100 if irr is not None else None

# Gross Margin
gross_margin_dollar = tcv - initial_investment
gross_margin_percent = (gross_margin_dollar / tcv) * 100 if tcv != 0 else 0

# Main Display
st.header("Financial Summary")

# Key Metrics
st.subheader("Key Metrics")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Contract Value (TCV)", f"${tcv:,.2f}")
with col2:
    st.metric("Net Present Value (NPV)", f"${npv:,.2f}")
with col3:
    st.metric("Internal Rate of Return (IRR)", f"{irr_percent:.1f}%" if irr_percent else "N/A")
with col4:
    st.metric("Gross Margin (%)", f"{gross_margin_percent:.1f}%")

# Service Details
st.subheader("Selected Services")
for service, percentage in selected_services.items():
    st.write(f"**{service}:** {percentage * 100:.0f}% of Project Cost")

# Cumulative Cash Flow Chart
st.subheader("Cumulative Cash Flow Over Time")
years = list(range(term_years + 1))
cumulative_cf = np.cumsum(cash_flows)
fig, ax = plt.subplots()
ax.plot(years, cumulative_cf, marker='o', color='green')
ax.set_xlabel("Year")
ax.set_ylabel("Cumulative Cash Flow ($)")
ax.set_title("Cumulative Cash Flow")
ax.grid(True)
st.pyplot(fig)

# Additional Info
st.subheader("Additional Metrics")
st.write(f"**Gross Margin ($):** ${gross_margin_dollar:,.2f}")
st.write(f"**Total Service Costs:** ${service_costs:,.2f}")
