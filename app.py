import streamlit as st
import fitz  # PyMuPDF
import re
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Optional, List
from datetime import datetime, date
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Company branding (customize as needed)
COMPANY_NAME = "Your Company Name"
COMPANY_COLOR = "#003399"  # Corporate blue
SECONDARY_COLOR = "#f0f8ff"  # Light blue background
FONT_STYLE = "Arial"

# Regex patterns for field extraction
FIELD_PATTERNS = {
    "account_number": r"(?:Account\s*(?:Number|#)?[:\s]*)([\d\-\w]+)",
    "service_address": r"(?:Service\s*Address|Address)[:\s]*(.*?)(?:\n|$)",
    "total_usage": r"(?:Total\s*(?:Usage|Consumption)[\s:]*)([\d,]+\.?\d*)\s*(kWh|CCF)",
    "total_cost": r"(?:Total\s*(?:Cost|Amount\s*Due)[\s:]*)\$?([\d,]+\.?\d*)",
    "billing_period": r"(?:Billing\s*Period|Period)[:\s]*(\d{1,2}/\d{1,2}/\d{2,4}\s*-\s*\d{1,2}/\d{1,2}/\d{2,4})",
    "due_date": r"(?:Due\s*Date|Payment\s*Due)[:\s]*(\d{1,2}/\d{1,2}/\d{2,4})",
    "energy_charge": r"(?:Energy\s*Charge)[\s:]*\$?([\d,]+\.?\d*)",
    "taxes": r"(?:Taxes|Tax)[\s:]*\$?([\d,]+\.?\d*)",
    "fees": r"(?:Fees|Service\s*Fee)[\s:]*\$?([\d,]+\.?\d*)"
}

# Utility Functions
@st.cache_data
def extract_text_from_pdf(pdf_file) -> str:
    """Extract text from a PDF file using PyMuPDF with caching for performance."""
    try:
        doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
        text = "".join(page.get_text() for page in doc)
        doc.close()
        return text
    except Exception as e:
        logger.error(f"PDF extraction failed: {e}")
        return ""

def extract_data(text: str) -> Dict[str, Optional[str]]:
    """Extract key fields from text using regex."""
    data = {}
    for field, pattern in FIELD_PATTERNS.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            value = match.group(1).strip()
            if field == "total_usage":
                data[field] = value.replace(",", "")
                data["usage_unit"] = match.group(2)
            elif field in ["total_cost", "energy_charge", "taxes", "fees"]:
                data[field] = value.replace(",", "")
            else:
                data[field] = value
        else:
            data[field] = None
    return data

def clean_data(data: Dict[str, Optional[str]]) -> Dict[str, Optional[str]]:
    """Clean and validate extracted data."""
    cleaned = data.copy()
    for field in ["total_usage", "total_cost", "energy_charge", "taxes", "fees"]:
        if cleaned.get(field):
            try:
                cleaned[field] = float(cleaned[field])
            except (ValueError, TypeError):
                cleaned[field] = None
    if cleaned.get("billing_period"):
        try:
            end_date = cleaned["billing_period"].split("-")[1].strip()
            cleaned["billing_date"] = datetime.strptime(end_date, "%m/%d/%Y").date()
        except (ValueError, IndexError):
            cleaned["billing_date"] = None
    return cleaned

def create_dataframe(data_list: List[Dict[str, Optional[str]]]) -> pd.DataFrame:
    """Convert list of extracted data to a DataFrame."""
    df = pd.DataFrame(data_list)
    if "billing_date" in df.columns:
        df = df.sort_values("billing_date")
    return df

# Dashboard Functions
def format_value(value, format_str: str) -> str:
    """Custom formatter to handle None or non-numeric values with user-friendly output."""
    if value is None or pd.isna(value):
        return "Data not available"
    try:
        return format_str.format(float(value))
    except (ValueError, TypeError):
        return str(value)

def display_extracted_data(df: pd.DataFrame) -> None:
    """Display extracted data in a styled, interactive table."""
    st.subheader("Extracted Bill Details")
    styled_df = df.style.format({
        "total_usage": lambda x: format_value(x, "{:.2f}"),
        "total_cost": lambda x: format_value(x, "${:.2f}"),
        "energy_charge": lambda x: format_value(x, "${:.2f}"),
        "taxes": lambda x: format_value(x, "${:.2f}"),
        "fees": lambda x: format_value(x, "${:.2f}"),
        "account_number": str,
        "service_address": str,
        "billing_period": str,
        "due_date": str,
        "usage_unit": str,
        "billing_date": lambda x: x.strftime("%Y-%m-%d") if isinstance(x, date) else "Data not available"
    }).hide(axis="index").set_properties(**{
        'background-color': 'white',
        'border-color': COMPANY_COLOR,
        'border-style': 'solid',
        'border-width': '1px',
        'font-family': FONT_STYLE
    }).set_table_styles([
        {'selector': 'tr:nth-child(even)',
         'props': [('background-color', SECONDARY_COLOR)]},
        {'selector': 'th',
         'props': [('background-color', COMPANY_COLOR), ('color', 'white'), ('font-weight', 'bold')]}
    ])
    st.dataframe(styled_df, use_container_width=True)

    # Summary statistics
    if df["total_usage"].notna().any() and df["total_cost"].notna().any():
        st.markdown("### Summary Insights", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Average Usage", f"{df['total_usage'].mean():.2f} {df['usage_unit'].iloc[0]}")
        with col2:
            st.metric("Average Cost", f"${df['total_cost'].mean():.2f}")
        with col3:
            st.metric("Highest Usage", f"{df['total_usage'].max():.2f} {df['usage_unit'].iloc[0]}")

def plot_usage_vs_cost_trend(df: pd.DataFrame) -> None:
    """Dual Y-Axis Line Chart for Usage vs Cost Over Time with improvements."""
    if "billing_date" in df.columns and df["total_usage"].notna().any() and df["total_cost"].notna().any():
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df["billing_date"], y=df["total_usage"], name="Usage", line=dict(color="#1f77b4", dash="solid"), mode="lines+markers"))
        fig.add_trace(go.Scatter(x=df["billing_date"], y=df["total_cost"], name="Cost", yaxis="y2", line=dict(color="#ff7f0e", dash="solid"), mode="lines+markers"))
        fig.update_layout(
            title="Usage vs Cost Trend Over Time",
            xaxis_title="Billing Period",
            xaxis=dict(tickformat="%Y-%m", tickangle=-45),
            yaxis_title=f"Usage ({df['usage_unit'].iloc[0]})",
            yaxis=dict(range=[0, max(df["total_usage"].max() * 1.1, 1)]),  # Start at 0, slight padding
            yaxis2=dict(title="Cost ($)", overlaying="y", side="right", range=[0, df["total_cost"].max() * 1.1]),  # Start at 0, slight padding
            template="plotly_white",
            height=500,
            hovermode="x unified",
            plot_bgcolor=SECONDARY_COLOR,
            paper_bgcolor="white",
            font=dict(family=FONT_STYLE, size=12, color="black")
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Insufficient data for Usage vs Cost Trend.")

def plot_cost_breakdown(df: pd.DataFrame) -> None:
    """Stacked Bar Chart for Monthly Energy Cost Breakdown."""
    cost_cols = ["energy_charge", "taxes", "fees"]
    if "billing_date" in df.columns and any(df[col].notna().any() for col in cost_cols):
        breakdown_df = df[["billing_date"] + cost_cols].fillna(0)
        fig = px.bar(breakdown_df, x="billing_date", y=cost_cols, title="Monthly Energy Cost Breakdown",
                     labels={"value": "Cost ($)", "billing_date": "Billing Period"},
                     color_discrete_map={"energy_charge": "#1f77b4", "taxes": "#ff7f0e", "fees": "#2ca02c"},
                     template="plotly_white", height=500)
        fig.update_layout(
            barmode="stack",
            plot_bgcolor=SECONDARY_COLOR,
            paper_bgcolor="white",
            font=dict(family=FONT_STYLE, size=12, color="black")
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Insufficient cost breakdown data.")

def plot_blended_rate(df: pd.DataFrame) -> None:
    """Line Chart for Blended Rate Over Time."""
    if "billing_date" in df.columns and df["total_usage"].notna().any() and df["total_cost"].notna().any():
        df["blended_rate"] = df["total_cost"] / df["total_usage"]
        fig = px.line(df, x="billing_date", y="blended_rate", title="Blended Rate Over Time",
                      labels={"blended_rate": f"Rate ($/{df['usage_unit'].iloc[0]})", "billing_date": "Billing Period"},
                      template="plotly_white", height=500)
        fig.update_traces(line=dict(color=COMPANY_COLOR, dash="solid"), mode="lines+markers")
        fig.update_layout(
            plot_bgcolor=SECONDARY_COLOR,
            paper_bgcolor="white",
            font=dict(family=FONT_STYLE, size=12, color="black")
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Insufficient data for Blended Rate.")

def plot_usage_anomaly(df: pd.DataFrame) -> None:
    """Scatter Plot for Anomaly Detection in Usage with outlier highlighting."""
    if "billing_date" in df.columns and df["total_usage"].notna().any():
        # Calculate mean and std for anomaly detection
        mean_usage = df["total_usage"].mean()
        std_usage = df["total_usage"].std()
        df["is_anomaly"] = abs(df["total_usage"] - mean_usage) > 2 * std_usage  # Simple outlier detection

        fig = px.scatter(df, x="billing_date", y="total_usage", title="Usage Anomaly Detection",
                         labels={"total_usage": f"Usage ({df['usage_unit'].iloc[0]})", "billing_date": "Billing Period"},
                         color="is_anomaly", color_discrete_map={True: "#ff3333", False: "#1f77b4"},
                         template="plotly_white", height=500)
        fig.update_traces(marker=dict(size=12))
        fig.update_layout(
            plot_bgcolor=SECONDARY_COLOR,
            paper_bgcolor="white",
            font=dict(family=FONT_STYLE, size=12, color="black")
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Insufficient data for Usage Anomaly Detection.")

# Main App
def main():
    st.set_page_config(page_title=f"{COMPANY_NAME} Utility Bill Analyzer", layout="wide")
    
    # Custom CSS for branding
    st.markdown("""
    <style>
    .main {
        background-color: #ffffff;
        font-family: Arial, sans-serif;
    }
    .stButton>button {
        background-color: #003399;
        color: white;
        border-radius: 5px;
    }
    .stButton>button:hover {
        background-color: #002266;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #f0f8ff;
        border: 1px solid #003399;
        border-radius: 5px 5px 0 0;
        padding: 10px;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #e6f0ff;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background-color: #003399;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

    # Header with logo (replace with your logo URL or local path)
    st.image("https://via.placeholder.com/200x50.png?text=Your+Logo", width=200)
    st.title(f"📊 {COMPANY_NAME} Utility Bill Analyzer")
    st.markdown("Upload one or more utility bills (PDFs) to analyze trends and insights.")

    # Session state to store multiple bills
    if "bill_data" not in st.session_state:
        st.session_state.bill_data = []

    # File Upload with progress feedback
    uploaded_files = st.file_uploader("Upload Utility Bills (PDF)", type="pdf", accept_multiple_files=True)

    if uploaded_files:
        progress_bar = st.progress(0)
        total_files = len(uploaded_files)
        st.session_state.bill_data = []

        for i, uploaded_file in enumerate(uploaded_files, 1):
            with st.spinner(f"Processing {uploaded_file.name} ({i}/{total_files})..."):
                text = extract_text_from_pdf(uploaded_file)
                if not text:
                    st.error(f"Could not extract text from {uploaded_file.name}. Skipping this file.")
                    continue
                raw_data = extract_data(text)
                cleaned_data = clean_data(raw_data)
                st.session_state.bill_data.append(cleaned_data)
            progress_bar.progress(i / total_files)

        if st.session_state.bill_data:
            df = create_dataframe(st.session_state.bill_data)
            display_extracted_data(df)

            # Visualization Tabs
            tab1, tab2, tab3, tab4 = st.tabs(["Usage vs Cost", "Cost Breakdown", "Blended Rate", "Anomaly Detection"])
            with tab1:
                plot_usage_vs_cost_trend(df)
            with tab2:
                plot_cost_breakdown(df)
            with tab3:
                plot_blended_rate(df)
            with tab4:
                plot_usage_anomaly(df)

            if not df["total_usage"].notna().any() or not df["total_cost"].notna().any():
                st.warning("Some key data (Usage or Cost) is missing from one or more bills.")
        else:
            st.error("No valid data extracted from uploaded files.")
    else:
        st.info("Please upload PDFs to begin analyzing your utility bills.")

    # Help and Support Section
    st.markdown("### Need Help?")
    st.info("Contact [support@yourcompany.com](mailto:support@yourcompany.com) for assistance with file formats or data extraction issues.")

if __name__ == "__main__":
    main()
