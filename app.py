import streamlit as st
import numpy as np
import numpy_financial as npf
import matplotlib.pyplot as plt

# Title and description
st.title("Financial Model Calculator")
st.write("This app calculates key financial metrics for a project with an initial investment and constant annual cash flows over a specified number of years.")

# Sidebar for input parameters
st.sidebar.header("Input Parameters")
initial_investment = st.sidebar.number_input("Initial Investment ($)", min_value=0.0, value=100000.0, step=1000.0)
annual_cash_flow = st.sidebar.number_input("Annual Cash Flow ($)", min_value=0.0, value=20000.0, step=1000.0)
discount_rate = st.sidebar.number_input("Discount Rate (%)", min_value=0.0, value=5.0, step=0.1) / 100
years = st.sidebar.slider("Number of Years", min_value=1, max_value=30, value=10)

# Calculate cash flows
cash_flows = [-initial_investment] + [annual_cash_flow] * years

# Calculate NPV
npv = npf.npv(discount_rate, cash_flows)

# Calculate IRR
try:
    irr = npf.irr(cash_flows)
    irr_percent = irr * 100 if irr is not None else None
except:
    irr_percent = None

# Calculate payback period
if annual_cash_flow > 0:
    payback_period = initial_investment / annual_cash_flow
    if payback_period > years:
        payback_period = None
else:
    payback_period = None

# Display financial metrics
st.header("Financial Metrics")
st.write(f"Net Present Value (NPV): ${npv:,.2f}")
if irr_percent is not None:
    st.write(f"Internal Rate of Return (IRR): {irr_percent:.2f}%")
else:
    st.write("IRR cannot be calculated")
if payback_period is not None:
    st.write(f"Payback Period: {payback_period:.2f} years")
elif annual_cash_flow > 0:
    st.write("Payback period exceeds project duration")
else:
    st.write("Payback period cannot be calculated (annual cash flow <=0)")

# Plot cumulative cash flow
st.header("Cumulative Cash Flow Over Time")
years_list = list(range(years + 1))
cumulative_cf = np.cumsum(cash_flows)
fig, ax = plt.subplots()
ax.plot(years_list, cumulative_cf, marker='o')
ax.set_xlabel('Year')
ax.set_ylabel('Cumulative Cash Flow ($)')
ax.set_title('Cumulative Cash Flow')
ax.grid(True)
st.pyplot(fig)
