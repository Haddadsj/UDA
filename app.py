import streamlit as st
import numpy as np
import numpy_financial as npf
import matplotlib.pyplot as plt

# Title
st.title("Energy Services Financial Dashboard")

# Sidebar for Inputs
st.sidebar.header("Project Inputs")
term_months = st.sidebar.number_input("Term Length (Months)", min_value=1, value=60)
transfer_rate = st.sidebar.number_input("Transfer Rate (%)", min_value=0.0, value=7.0, step=0.1) / 100
total_nte = st.sidebar.number_input("Total NTE ($)", min_value=0.0, value=191345.0, step=1000.0)
cost_reduction = st.sidebar.number_input("Cost Reduction (%)", min_value=0.0, value=50.0, step=1.0) / 100
kwh_inflation = st.sidebar.number_input("kWh Utility Inflation Rate (%)", min_value=0.0, value=6.20, step=0.1) / 100
contingency_budget = st.sidebar.number_input("Contingency Budget ($)", min_value=0.0, value=3634.0, step=100.0)
meter_count = st.sidebar.number_input("Meter Count", min_value=1, value=3)
o_m_cost = st.sidebar.number_input("O&M Cost ($)", min_value=0.0, value=3634.0, step=100.0)
ecm_category = st.sidebar.selectbox("ECM Category", ["Lighting", "Solar", "HVAC"])
contract_type = st.sidebar.selectbox("Contract Type", ["EaaS", "Lease", "PPA"])
billing_type = st.sidebar.selectbox("Billing Type", ["Savings Based", "Fixed", "Variable"])
contract_unit = st.sidebar.selectbox("Contract Unit", ["kWh + Maintenance", "kWh Only"])

# Additional Financial Inputs
annual_payment = st.sidebar.number_input("Annual Payment ($)", min_value=0.0, value=59472.0, step=1000.0)
y1_combined_savings = st.sidebar.number_input("Y1 Combined Savings ($)", min_value=0.0, value=69313.0, step=1000.0)
y1_retained_savings_percent = st.sidebar.number_input("Y1 Combined % Retained Savings", min_value=0.0, value=16.5, step=0.1)

# Redaptive Services Options
st.sidebar.header("Redaptive Services")
program_management_options = {
    "Redaptive Developed & Delivered": {"price_basis": "10% Total Net Cost", "base_price": 0.10},
    "Customer Developed, Redaptive Delivered": {"price_basis": "7% Total Net Cost", "base_price": 0.07},
    "Customer Developed & Delivered": {"price_basis": "3% Total Net Cost", "base_price": 0.03}
}
data_mv_options = {
    "Off-Balance Sheet, Savings Guarantee": {"price_basis": "Max of $7,000 or 7% Total Net Cost", "base_price": 7000.0, "percent": 0.07},
    "Off-Balance Sheet, Shared Savings/Usage Risk": {"price_basis": "Max of $6,000 or 6% Total Net Cost", "base_price": 6000.0, "percent": 0.06},
    "Off-Balance Sheet, Generation": {"price_basis": "5% Total Net Cost", "base_price": 0.05}
}
incentives_management_options = {
    "State/Utility Incentives & Environmental Credits": {"price_basis": "25% Est. Incentives + Credits", "base_price": 0.25},
    "State/Utility Incentives Only": {"price_basis": "15% Est. Incentives", "base_price": 0.15},
    "Environmental Credits Only": {"price_basis": "10% Est. Credits", "base_price": 0.10}
}
ongoing_maintenance_options = {
    "Full PM & RM": {"price_basis": "5% Total Net Cost", "base_price": 0.05},
    "PM w/ RM Pass-Through": {"price_basis": "3% Total Net Cost", "base_price": 0.03},
    "Parts & Labor": {"price_basis": "2% Total Net Cost", "base_price": 0.02},
    "Parts Only": {"price_basis": "2% Total Net Cost", "base_price": 0.02},
    "Manufacturer’s Warranty Only": {"price_basis": "1% Total Net Cost", "base_price": 0.01},
    "Customer Managed Maintenance": {"price_basis": "0% Total Net Cost", "base_price": 0.0}
}

program_management_option = st.sidebar.selectbox("Program Management", list(program_management_options.keys()))
data_mv_option = st.sidebar.selectbox("Data and M&V", list(data_mv_options.keys()))
incentives_management_option = st.sidebar.selectbox("Incentives Management", list(incentives_management_options.keys()))
ongoing_maintenance_option = st.sidebar.selectbox("Ongoing Maintenance", list(ongoing_maintenance_options.keys()))

# Total Net Cost for Service Calculations
total_net_cost = st.sidebar.number_input("Total Net Cost ($)", min_value=0.0, value=205504.0, step=1000.0)

# Calculations
term_years = term_months / 12
tcv = annual_payment * term_years  # Total Contract Value (customer-facing)
initial_investment = total_nte + contingency_budget  # Simplified assumption
cash_flows = [-initial_investment] + [annual_payment] * int(term_years)
npv = npf.npv(transfer_rate, cash_flows)
irr = npf.irr(cash_flows)
irr_percent = irr * 100 if irr is not None else None
gross_margin_dollar = tcv - initial_investment
gross_margin_percent = (gross_margin_dollar / tcv) * 100 if tcv != 0 else 0
term_savings = sum([y1_combined_savings * (1 + kwh_inflation)**t for t in range(int(term_years))])

# Service Costs
program_management_cost = total_net_cost * program_management_options[program_management_option]["base_price"]
data_mv_cost = max(data_mv_options[data_mv_option].get("base_price", 0), total_net_cost * data_mv_options[data_mv_option].get("percent", 0))
incentives_management_cost = total_net_cost * incentives_management_options[incentives_management_option]["base_price"]  # Placeholder: assumes total_net_cost as proxy
ongoing_maintenance_cost = total_net_cost * ongoing_maintenance_options[ongoing_maintenance_option]["base_price"]

# Main Display
st.header("Project Overview")

# Key Project Terms
st.subheader("Key Project Terms")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Term (years)", f"{term_years:.1f}")
with col2:
    st.metric("Annual Payment", f"${annual_payment:,.2f}")
with col3:
    st.metric("Y1 Combined Savings", f"${y1_combined_savings:,.2f}")
with col4:
    st.metric("Y1 Retained Savings", f"{y1_retained_savings_percent:.1f}%")

# Financial Metrics
st.subheader("Financial Metrics")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Contract Value (TCV)", f"${tcv:,.2f}")
with col2:
    st.metric("NPV", f"${npv:,.2f}")
with col3:
    st.metric("IRR", f"{irr_percent:.1f}%" if irr_percent is not None else "N/A")
with col4:
    st.metric("Gross Margin", f"{gross_margin_percent:.1f}%")
st.write(f"**Gross Margin ($):** ${gross_margin_dollar:,.2f}")

# Service Costs
st.subheader("Service Costs")
st.write(f"Program Management Cost: ${program_management_cost:,.2f}")
st.write(f"Data and M&V Cost: ${data_mv_cost:,.2f}")
st.write(f"Incentives Management Cost: ${incentives_management_cost:,.2f}")
st.write(f"Ongoing Maintenance Cost: ${ongoing_maintenance_cost:,.2f}")

# Project Details
st.subheader("Project Details")
st.write(f"**ECM Category:** {ecm_category}")
st.write(f"**Contract Type:** {contract_type}")
st.write(f"**Billing Type:** {billing_type}")
st.write(f"**Contract Unit:** {contract_unit}")
st.write(f"**Transfer Rate (Customer-facing):** {transfer_rate * 100:.2f}%")

# Environmental Metrics (Placeholders)
st.subheader("Environmental Metrics")
st.write("Y1 GHG: 57 MT CO2 (Placeholder)")
st.write("Term GHG: 284 MT CO2 (Placeholder)")
st.write("EUL GHG: 862 MT CO2 (Placeholder)")

# Savings Over Time
st.subheader("Savings Over Time")
st.write(f"Term Savings: ${term_savings:,.2f}")
st.write("EUL Combined Savings: Placeholder")

# Cost Breakdown (Placeholders)
st.subheader("Cost Breakdown")
st.write(f"Base/Vendor Costs: ${total_nte:,.2f}")
st.write("Redaptive Costs – Foundational: Placeholder")
st.write("Redaptive Costs – Services: Placeholder")

# Payment Details (Placeholders)
st.subheader("Payment Details")
st.write("Customer Price before Tax/Interest: Placeholder")
st.write("Upton Payment from Customer: Placeholder")
st.write("Principal Over Term: Placeholder")
st.write("Interest Over Term: Placeholder")
st.write("TCV (Internal): Placeholder")
st.write(f"Customer Monthly Payment: ${(tcv / term_months):,.2f}")
st.write("Sales Commission: Placeholder")

# Cumulative Cash Flow Chart
st.subheader("Cumulative Cash Flow Over Time")
years = list(range(int(term_years) + 1))
cumulative_cf = np.cumsum(cash_flows)
fig, ax = plt.subplots()
ax.plot(years, cumulative_cf, marker='o', color='blue')
ax.set_xlabel("Year")
ax.set_ylabel("Cumulative Cash Flow ($)")
ax.set_title("Cumulative Cash Flow")
ax.grid(True)
st.pyplot(fig)
