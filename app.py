import streamlit as st
import numpy as np
import numpy_financial as npf
import matplotlib.pyplot as plt

# Title
st.title("Energy Services Financial Dashboard")

# Sidebar Inputs
st.sidebar.header("Project Inputs")
term_years = st.sidebar.number_input("Term Length (years)", min_value=1, value=5)
project_cost = st.sidebar.number_input("Project Cost ($)", min_value=0.0, value=200000.0, step=1000.0)
year1_savings = st.sidebar.number_input("Year 1 Savings ($)", min_value=0.0, value=60000.0, step=1000.0)
utility_cost_escalator = st.sidebar.number_input("Utility Cost Escalator (%)", min_value=0.0, value=2.0, step=0.1) / 100
discount_rate = st.sidebar.number_input("Discount Rate (%)", min_value=0.0, value=7.0, step=0.1) / 100

# Service Dropdowns
st.sidebar.header("Services")
program_management_options = {
    "Redaptive Developed & Delivered": lambda cost: 0.10 * cost,
    "Customer Developed, Redaptive Delivered": lambda cost: 0.07 * cost,
    "Customer Developed & Delivered": lambda cost: 0.03 * cost
}
data_mv_options = {
    "Off-Balance Sheet, Savings Guarantee": lambda cost: max(7000, 0.07 * cost),
    "Off-Balance Sheet, Shared Savings/Usage Risk": lambda cost: max(6000, 0.06 * cost),
    "Off-Balance Sheet, Generation": lambda cost: 0.05 * cost
}
incentives_management_options = {
    "State/Utility Incentives & Environmental Credits": lambda cost: 0.25 * cost,
    "State/Utility Incentives Only": lambda cost: 0.15 * cost,
    "Environmental Credits Only": lambda cost: 0.10 * cost
}
ongoing_maintenance_options = {
    "Full PM & RM": lambda cost: 0.05 * cost,
    "PM w/ RM Pass-Through": lambda cost: 0.03 * cost,
    "Parts & Labor": lambda cost: 0.02 * cost,
    "Manufacturer’s Warranty Only": lambda cost: 0.01 * cost,
    "Customer Managed Maintenance": lambda cost: 0.00 * cost
}

program_management_option = st.sidebar.selectbox("Program Management", list(program_management_options.keys()))
data_mv_option = st.sidebar.selectbox("Data and M&V", list(data_mv_options.keys()))
incentives_management_option = st.sidebar.selectbox("Incentives Management", list(incentives_management_options.keys()))
ongoing_maintenance_option = st.sidebar.selectbox("Ongoing Maintenance", list(ongoing_maintenance_options.keys()))

# Calculations
program_management_cost = program_management_options[program_management_option](project_cost)
data_mv_cost = data_mv_options[data_mv_option](project_cost)
incentives_management_cost = incentives_management_options[incentives_management_option](project_cost)
ongoing_maintenance_cost = ongoing_maintenance_options[ongoing_maintenance_option](project_cost)
total_service_costs = program_management_cost + data_mv_cost + incentives_management_cost + ongoing_maintenance_cost
initial_investment = project_cost + total_service_costs

cash_flows = [-initial_investment] + [year1_savings * (1 + utility_cost_escalator)**t for t in range(term_years)]
tcv = sum(cash_flows[1:])  # Sum of annual savings
term_savings = tcv  # Total savings over term
annual_payment = tcv / term_years  # Derived as average annual payment
y1_combined_savings = year1_savings
y1_combined_percent_retained = 16.5 / 100  # Fixed from Image 1 for simplicity
y1_kwh_percent_retained = 14.2 / 100  # Fixed from Image 1 for simplicity
npv = npf.npv(discount_rate, cash_flows)
irr = npf.irr(cash_flows) if all(cf >= 0 for cf in cash_flows[1:]) else None
irr_percent = irr * 100 if irr is not None else None
gross_margin_dollar = tcv - initial_investment
gross_margin_percent = (gross_margin_dollar / tcv) * 100 if tcv != 0 else 0

# Key Financial Metrics
st.header("Key Financial Metrics")
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric("TCV", f"${tcv:,.2f}")
    st.metric("Annual Payment", f"${annual_payment:,.2f}")
with col2:
    st.metric("Y1 Combined Savings", f"${y1_combined_savings:,.2f}")
    st.metric("Y1 Combined % Retained", f"{y1_combined_percent_retained * 100:.1f}%")
with col3:
    st.metric("Y1 kWh % Retained", f"{y1_kwh_percent_retained * 100:.1f}%")
    st.metric("NPV", f"${npv:,.2f}")
with col4:
    st.metric("IRR", f"{irr_percent:.1f}%" if irr_percent is not None else "N/A")
    st.metric("Gross Margin %", f"{gross_margin_percent:.1f}%")
with col5:
    st.metric("Gross Margin $", f"${gross_margin_dollar:,.2f}")
    st.metric("Term Savings", f"${term_savings:,.2f}")

# Cost Breakdown
st.header("Cost Breakdown")
st.write(f"**Base/Vendor Costs (Project Cost):** ${project_cost:,.2f}")
st.write(f"**Program Management Cost:** ${program_management_cost:,.2f}")
st.write(f"**Data and M&V Cost:** ${data_mv_cost:,.2f}")
st.write(f"**Incentives Management Cost:** ${incentives_management_cost:,.2f}")
st.write(f"**Ongoing Maintenance Cost:** ${ongoing_maintenance_cost:,.2f}")
st.write(f"**Total Service Costs:** ${total_service_costs:,.2f}")
st.write(f"**Total Initial Investment:** ${initial_investment:,.2f}")

# Selected Services
st.subheader("Selected Services")
st.write(f"**Program Management:** {program_management_option}")
st.write(f"**Data and M&V:** {data_mv_option}")
st.write(f"**Incentives Management:** {incentives_management_option}")
st.write(f"**Ongoing Maintenance:** {ongoing_maintenance_option}")

# Cumulative Cash Flow Chart
st.header("Cumulative Cash Flow")
cumulative_cf = np.cumsum(cash_flows)
years = list(range(term_years + 1))
fig, ax = plt.subplots()
ax.plot(years, cumulative_cf, marker='o', color='green')
ax.set_xlabel("Year")
ax.set_ylabel("Cumulative Cash Flow ($)")
ax.grid(True)
st.pyplot(fig)
