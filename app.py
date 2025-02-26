import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import fitz  # PyMuPDF for PDF parsing
import re
import unicodedata
from fpdf import FPDF
import io

def extract_text_from_pdf(uploaded_file):
    """Extracts text from an uploaded PDF file in Streamlit with robust error handling."""
    try:
        pdf_bytes = uploaded_file.read()
        doc = fitz.open("pdf", pdf_bytes)
        text = ""
        for page in doc:
            text += page.get_text("text") + "\n"
        return text if text.strip() else "No readable text found"
    except Exception as e:
        st.error(f"Error extracting text from PDF: {e}")
        return ""

def parse_utility_data(text):
    """Extracts structured data from the utility bill text with error handling and pattern matching."""
    try:
        data = {
            "Account Number": "Unknown",
            "Service Address": "Unknown",
            "Total Usage (kWh or CCF)": "Unknown",
            "Total Cost ($)": "Unknown",
            "Billing Period": "Unknown",
            "Due Date": "Unknown",
        }

        # Search for Account Number
        match = re.search(r"Account\s*Number[:\s]+([\d\-]+)", text, re.IGNORECASE)
        if match:
            data["Account Number"] = match.group(1)

        # Search for Service Address
        match = re.search(r"Service\s*Address[:\s]+([\w\s,]+)", text, re.IGNORECASE)
        if match:
            data["Service Address"] = match.group(1).strip()

        # Search for Usage (kWh for electric, CCF for gas)
        match = re.search(r"(?:Total\s*Usage|Total\s*kWh|Total\s*CCF)[:\s]+([\d,]+)", text, re.IGNORECASE)
        if match:
            data["Total Usage (kWh or CCF)"] = match.group(1).replace(",", "")

        # Search for Total Cost
        match = re.search(r"(?:Total\s*Due|Amount\s*Due|Total\s*Cost)[:\s]+\$?([\d,]+\.\d{2})", text, re.IGNORECASE)
        if match:
            data["Total Cost ($)"] = match.group(1).replace(",", "")

        # Search for Billing Period
        match = re.search(r"Billing\s*Period[:\s]+([\w\d\s/-]+)", text, re.IGNORECASE)
        if match:
            data["Billing Period"] = match.group(1).strip()

        # Search for Due Date
        match = re.search(r"Due\s*Date[:\s]+([\w\d/-]+)", text, re.IGNORECASE)
        if match:
            data["Due Date"] = match.group(1).strip()

        return data
    except Exception as e:
        st.error(f"Error parsing utility data: {e}")
        return {}

def clean_text_for_pdf(text):
    """Removes emojis and unsupported characters for FPDF compatibility."""
    return ''.join(c for c in text if unicodedata.category(c)[0] != 'So')

def generate_report(data):
    """Creates a structured PDF report while preventing encoding errors."""
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(200, 10, clean_text_for_pdf("Utility Bill Analysis Report"), ln=True, align="C")
        pdf.ln(10)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Summary:", ln=True)
        pdf.set_font("Arial", "", 11)

        for key, value in data.items():
            safe_key = clean_text_for_pdf(str(key))
            safe_value = clean_text_for_pdf(str(value)).encode("latin-1", "ignore").decode("latin-1")
            pdf.cell(0, 10, f"{safe_key}: {safe_value}", ln=True)

        report_path = "Utility_Bill_Analysis_Report.pdf"
        pdf.output(report_path, "F")
        return report_path
    except Exception as e:
        st.error(f"Error generating PDF report: {e}")
        return ""

def main():
    st.title("📊 Utility Bill Analysis Tool")
    st.write("Upload utility bills (PDF) and get automated insights.")

    uploaded_file = st.file_uploader("📂 Upload Utility Bill (PDF)", type=["pdf"])
    
    if uploaded_file:
        with st.spinner("Extracting data..."):
            pdf_text = extract_text_from_pdf(uploaded_file)
            if "No readable text found" in pdf_text:
                st.error("No readable text extracted from the PDF. Please try another file.")
                return
            
            extracted_data = parse_utility_data(pdf_text)
            if not extracted_data or all(v == "Unknown" for v in extracted_data.values()):
                st.error("Could not extract meaningful data. Please check the file format.")
                return
            
            df = pd.DataFrame([extracted_data])
            st.success("✅ Data Extracted Successfully!")
            st.write(df)

            # Generate PDF report
            report_path = generate_report(extracted_data)
            if report_path:
                with open(report_path, "rb") as file:
                    st.download_button("📄 Download Report", data=file, file_name="Utility_Bill_Report.pdf")
            else:
                st.error("Failed to generate the report.")

if __name__ == "__main__":
    main()
