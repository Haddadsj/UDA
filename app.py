import streamlit as st
import fitz  # PyMuPDF
import re
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Optional, List
from datetime import datetime, date
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Regex patterns for field extraction
FIELD_PATTERNS = {
    "account_number": r"(?:Account\s*(?:Number|#)?[:\s]*)([\d\-\w]+)",
    "service_address": r"(?:Service\s*Address|Address)[:\s]*(.*?)(?:\n|$)",
    "total_usage": r"(?:Total\s*(?:Usage|Consumption)[\s:]*)([\d,]+\.?\d*)\s*(kWh|CCF)",
    "total_cost": r"(?:Total\s*(?:Cost|Amount\s*Due)[\s:]*)\$?([\d,]+\.?\d*)",
    "billing_period": r"(?:Billing\s*Period|Period)[:\s]*(\d{1,2}/\d{1,2}/\d{2,4}\s*-\s*\d{1,2}/\d{1,2}/\d{2,4})",
    "due_date": r"(?:Due\s*Date|Payment\s*Due)[:\s]*(\d{1,2}/\d{1,2}/\d{2,4})",
    # Simplified cost breakdown (assumes basic categories; extend as needed)
    "energy_charge": r"(?:Energy\s*Charge)[\s:]*\$?([\d,]+\.?\d*)",
    "taxes": r"(?:Taxes|Tax)[\s:]*\$?([\d,]+\.?\d*)",
    "fees": r"(?:Fees|Service\s*Fee)[\s:]*\$?([\d,]+\.?\d*)"
}

# Utility Functions
def extract_text_from_pdf(pdf_file) -> str:
    """Extract text from a PDF file using PyMuPDF."""
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
    # Parse billing period to a single date (end date) for simplicity
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
    """Custom formatter to handle None or non-numeric values."""
    if value is None or pd.isna(value):
        return "N/A"
    try:
        return format_str.format(float(value))
    except (ValueError, TypeError):
        return str(value)

def display_extracted_data(df: pd.DataFrame) -> None:
    """Display extracted data in a clean table."""
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
        "billing_date": lambda x: x.strftime("%Y-%m-%d") if isinstance(x, date) else "N/A"
    }).hide(axis="index")
    st.dataframe(styled_df, use_container_width=True)

def plot_usage_vs_cost_trend(df: pd.DataFrame) -> None:
    """Dual Y-Axis Line Chart for Usage vs Cost Over Time."""
    if "billing_date" in df.columns and df["total_usage"].notna().any() and df["total_cost"].notna().any():
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df["billing_date"], y=df["total_usage"], name="Usage", line=dict(color="#1f77b4")))
        fig.add_trace(go.Scatter(x=df["billing_date"], y=df["total_cost"], name="Cost", yaxis="y2", line=dict(color="#ff7f0e")))
        fig.update_layout(
            title="Usage vs Cost Trend Over Time",
            xaxis_title="Billing Period",
            yaxis_title=f"Usage ({df['usage_unit'].iloc[0]})",
            yaxis2=dict(title="Cost ($)", overlaying="y", side="right"),
            template="plotly_white",
            height=500
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
                     template="plotly_white", height=500)
        fig.update_layout(barmode="stack")
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
        fig.update_traces(mode="lines+markers")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Insufficient data for Blended Rate.")

def plot_usage_anomaly(df: pd.DataFrame) -> None:
    """Scatter Plot for Anomaly Detection in Usage."""
    if "billing_date" in df.columns and df["total_usage"].notna().any():
        fig = px.scatter(df, x="billing_date", y="total_usage", title="Usage Anomaly Detection",
                         labels={"total_usage": f"Usage ({df['usage_unit'].iloc[0]})", "billing_date": "Billing Period"},
                         template="plotly_white", height=500)
        fig.update_traces(mode="markers", marker=dict(size=12))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Insufficient data for Usage Anomaly Detection.")

# Main App
def main():
    st.set_page_config(page_title="Utility Bill Analyzer", layout="wide")
    st.title("📊 Utility Bill Analyzer Dashboard")
    st.markdown("Upload one or more utility bills (PDFs) to analyze trends and insights.")

    # Session state to store multiple bills
    if "bill_data" not in st.session_state:
        st.session_state.bill_data = []

    # File Upload
    uploaded_files = st.file_uploader("Upload Utility Bills (PDF)", type="pdf", accept_multiple_files=True)

    if uploaded_files:
        with st.spinner("Processing your bills..."):
            for uploaded_file in uploaded_files:
                text = extract_text_from_pdf(uploaded_file)
                if not text:
                    st.error(f"Could not extract text from {uploaded_file.name}. Skipping this file.")
                    continue
                raw_data = extract_data(text)
                cleaned_data = clean_data(raw_data)
                st.session_state.bill_data.append(cleaned_data)

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

if __name__ == "__main__":
    main()
