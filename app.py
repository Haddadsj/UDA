import streamlit as st
import fitz  # PyMuPDF
import re
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Optional, List
from datetime import datetime
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
    "due_date": r"(?:Due\s*Date|Payment\s*Due)[:\s]*(\d{1,2}/\d{1,2}/\d{2,4})"
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
            elif field == "total_cost":
                data[field] = value.replace(",", "")
            else:
                data[field] = value
        else:
            data[field] = None
    return data

def clean_data(data: Dict[str, Optional[str]]) -> Dict[str, Optional[str]]:
    """Clean and validate extracted data."""
    cleaned = data.copy()
    for field in ["total_usage", "total_cost"]:
        if cleaned.get(field):
            try:
                cleaned[field] = float(cleaned[field])
            except (ValueError, TypeError):
                cleaned[field] = None
    return cleaned

def create_dataframe(data: Dict[str, Optional[str]]) -> pd.DataFrame:
    """Convert extracted data to a DataFrame."""
    return pd.DataFrame([data])

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
    """Display extracted data in a clean table with robust formatting."""
    st.subheader("Extracted Bill Details")
    styled_df = df.style.format({
        "total_usage": lambda x: format_value(x, "{:.2f}"),
        "total_cost": lambda x: format_value(x, "${:.2f}"),
        "account_number": str,
        "service_address": str,
        "billing_period": str,
        "due_date": str,
        "usage_unit": str
    }).hide(axis="index")
    st.dataframe(styled_df, use_container_width=True)

def plot_usage_vs_cost(df: pd.DataFrame) -> None:
    """Plot Usage vs Cost as a bar chart."""
    if df["total_usage"].notna().any() and df["total_cost"].notna().any():
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=["Usage", "Cost"],
            y=[df["total_usage"].iloc[0], df["total_cost"].iloc[0]],
            marker_color=["#1f77b4", "#ff7f0e"],
            text=[f"{df['total_usage'].iloc[0]:.2f} {df['usage_unit'].iloc[0]}", f"${df['total_cost'].iloc[0]:.2f}"],
            textposition="auto"
        ))
        fig.update_layout(
            title="Usage vs Cost",
            yaxis_title="Value",
            template="plotly_white",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Insufficient data to plot Usage vs Cost.")

def plot_mock_trends(df: pd.DataFrame) -> None:
    """Simulate historical trends if multiple bills were uploaded."""
    if df["total_usage"].notna().any() and df["total_cost"].notna().any():
        mock_df = pd.DataFrame({
            "Month": ["Jan", "Feb", "Mar"],
            "Usage": [df["total_usage"].iloc[0] * 0.9, df["total_usage"].iloc[0], df["total_usage"].iloc[0] * 1.1],
            "Cost": [df["total_cost"].iloc[0] * 0.95, df["total_cost"].iloc[0], df["total_cost"].iloc[0] * 1.05]
        })
        fig = px.line(mock_df, x="Month", y=["Usage", "Cost"], title="Usage and Cost Trends",
                      labels={"value": "Value", "variable": "Metric"},
                      template="plotly_white")
        fig.update_traces(mode="lines+markers")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Insufficient data to plot trends.")

# Main App
def main():
    st.set_page_config(page_title="Utility Bill Analyzer", layout="wide")
    st.title("📊 Utility Bill Analyzer Dashboard")
    st.markdown("Upload your utility bill (PDF) to extract and visualize key insights.")

    # File Upload
    uploaded_file = st.file_uploader("Upload a Utility Bill (PDF)", type="pdf")

    if uploaded_file:
        with st.spinner("Processing your bill..."):
            text = extract_text_from_pdf(uploaded_file)
            if not text:
                st.error("Could not extract text from the PDF. Please ensure it’s a valid, readable file.")
                return

            raw_data = extract_data(text)
            cleaned_data = clean_data(raw_data)
            df = create_dataframe(cleaned_data)

            # Dashboard Layout
            col1, col2 = st.columns([1, 2])

            with col1:
                display_extracted_data(df)

            with col2:
                plot_usage_vs_cost(df)
                plot_mock_trends(df)

            if not df["total_usage"].notna().any() or not df["total_cost"].notna().any():
                st.warning("Some key data (Usage or Cost) could not be extracted. Results may be incomplete.")

    else:
        st.info("Please upload a PDF to begin analyzing your utility bill.")

if __name__ == "__main__":
    main()
