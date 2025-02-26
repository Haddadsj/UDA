import streamlit as st
import fitz  # PyMuPDF
import re
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
import unicodedata
import logging
import os
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Utility functions
def normalize_text(text):
    """Normalize text by removing emojis and special characters."""
    return unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii').strip()

@st.cache_data
def extract_text_from_pdf(pdf_file):
    """Extract text from a PDF file using PyMuPDF."""
    try:
        doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text("text")
        return normalize_text(text)
    except Exception as e:
        logger.error(f"Failed to extract text from PDF: {e}")
        return None

def parse_bill_data(text):
    """Extract key fields from utility bill text using regex."""
    patterns = {
        "account_number": r"(?:Account\s*(?:Number|No\.?|#)\s*[:\-\s]*)([A-Za-z0-9\-]+)",
        "service_address": r"(?:Service\s*Address|Address\s*[:\-\s]*)([\w\s,]+?)(?=\n|\s{2,}|$)",
        "total_usage": r"(?:Total\s*(?:Usage|Consumption|Quantity)\s*[:\-\s]*)([\d,\.]+)\s*(kWh|CCF)",
        "total_cost": r"(?:Total\s*(?:Amount|Cost|Due)\s*[:\-\s]*)\$?([\d,\.]+)",
        "billing_period": r"(?:Billing\s*Period|Period\s*[:\-\s]*)([\w\s\d\-]+)",
        "due_date": r"(?:Due\s*Date|Payment\s*Due\s*[:\-\s]*)([\w\s\d,]+)"
    }
    
    extracted_data = {}
    if not text:
        return extracted_data
    
    for key, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            value = match.group(1).strip()
            if key == "total_usage":
                extracted_data[key] = value
                extracted_data["usage_unit"] = match.group(2)
            elif key == "total_cost":
                extracted_data[key] = float(value.replace(",", ""))
            else:
                extracted_data[key] = value
    return extracted_data

def validate_data(data):
    """Validate extracted data and return a status message."""
    required_fields = ["total_usage", "total_cost"]
    missing_fields = [field for field in required_fields if field not in data or not data[field]]
    return f"Warning: Missing {', '.join(missing_fields)}." if missing_fields else "Extraction successful."

def generate_charts(data):
    """Generate interactive usage and cost trend charts."""
    if "total_usage" not in data or "total_cost" not in data:
        return None, None
    
    df = pd.DataFrame([data])
    df["total_usage"] = df["total_usage"].str.replace(",", "").astype(float)
    df["total_cost"] = df["total_cost"].astype(float)
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    ax1.bar(["Bill"], df["total_usage"], label="Usage", color="blue")
    ax1.set_ylabel(f"Usage ({data.get('usage_unit', 'Unknown')})", color="blue")
    ax1.tick_params(axis="y", labelcolor="blue")
    ax1_twin = ax1.twinx()
    ax1_twin.plot(["Bill"], df["total_cost"], color="green", marker="o", label="Cost")
    ax1_twin.set_ylabel("Cost ($)", color="green")
    ax1_twin.tick_params(axis="y", labelcolor="green")
    ax1.set_title("Usage vs Cost")
    
    ax2.bar(["Current Bill"], df["total_cost"], color="purple")
    ax2.set_title("Monthly Cost")
    ax2.set_ylabel("Cost ($)")
    
    plt.tight_layout()
    return fig, df

def generate_pdf_report(data, output_path="report.pdf"):
    """Generate a PDF report summarizing the extracted data."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    pdf.cell(200, 10, txt="Utility Bill Analysis Report", ln=True, align="C")
    pdf.ln(10)
    
    for key, value in data.items():
        if key != "usage_unit":
            pdf.cell(200, 10, txt=f"{key.replace('_', ' ').title()}: {value}", ln=True)
    
    pdf.output(output_path)
    return output_path

# Streamlit App
st.set_page_config(page_title="Utility Bill Analyzer", layout="wide")

# Custom CSS for better UI
st.markdown("""
    <style>
    .main { padding: 20px; }
    .stButton>button { background-color: #4CAF50; color: white; }
    </style>
""", unsafe_allow_html=True)

st.title("Utility Bill Analyzer")
st.markdown("Upload your utility bill (PDF) to analyze usage, costs, and generate a report.")

# File uploader
uploaded_file = st.file_uploader("Choose a PDF file", type="pdf", help="Supports electricity/gas bills.")

if uploaded_file:
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Step 1: Extract text
    status_text.text("Extracting text from PDF...")
    text = extract_text_from_pdf(uploaded_file)
    progress_bar.progress(25)
    
    if not text:
        st.error("Couldn’t extract text. Please ensure the PDF is readable.")
    else:
        # Step 2: Parse data
        status_text.text("Parsing bill details...")
        bill_data = parse_bill_data(text)
        validation_message = validate_data(bill_data)
        st.info(validation_message)
        progress_bar.progress(50)
        
        if bill_data:
            # Step 3: Display extracted data
            st.subheader("Extracted Details")
            st.dataframe(pd.DataFrame([bill_data]), use_container_width=True)
            progress_bar.progress(75)
            
            # Step 4: Generate and display charts
            status_text.text("Generating insights...")
            fig, df = generate_charts(bill_data)
            if fig:
                st.subheader("Insights")
                st.pyplot(fig)
            
            # Step 5: Generate and provide report
            status_text.text("Creating report...")
            report_path = generate_pdf_report(bill_data)
            with open(report_path, "rb") as f:
                st.download_button(
                    label="Download Report",
                    data=f,
                    file_name=f"bill_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf"
                )
            os.remove(report_path)  # Clean up
            progress_bar.progress(100)
            status_text.text("Analysis complete!")
        else:
            st.warning("No data found. Check the PDF format.")
else:
    st.info("Upload a bill to start.")

# Footer
st.markdown("---")
st.caption("Built with ❤️ by xAI | Powered by Streamlit")
