import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import fitz  # PyMuPDF for PDF parsing
import re
from fpdf import FPDF
import io

def extract_text_from_pdf(uploaded_file):
    """Extract text from an uploaded PDF file in Streamlit with error handling."""
    try:
        pdf_bytes = uploaded_file.read()
        doc = fitz.open("pdf", pdf_bytes)
        text = ""
        for page in doc:
            text += page.get_text("text") + "\n"
        return text
    except Exception as e:
        st.error(f"Error extracting text from PDF: {e}")
        return ""

def parse_utility_data(text):
    """Extract structured data from the utility bill text with error handling."""
    try:
        data = {
            "Account Number": "Unknown",
            "Service Address": "Unknown",
            "Total Usage (kWh)": 0,
            "Total Cost ($)": 0.0,
            "Blended Rate ($/kWh)": 0.0,
        }

        match = re.search(r"Account\s*Number[:\s]+(\d+)", text)
        if match:
            data["Account Number"] = match.group(1)

        match = re.search(r"Service Address[:\s]+([\w\s,]+)", text)
        if match:
            data["Service Address"] = match.group(1).strip()

        match = re.search(r"(?i)(?:Usage|Total\s*kWh)[:\s]+([\d,]+)", text)
        if match:
            data["Total Usage (kWh)"] = int(match.group(1).replace(",", ""))

        match = re.search(r"(?i)(?:Total\s*Due|Amount\s*Due|Total\s*Cost)[:\s]+\$?([\d,]+\.?\d*)", text)
        if match:
            data["Total Cost ($)"] = float(match.group(1).replace(",", ""))

        if data["Total Usage (kWh)"] > 0:
            data["Blended Rate ($/kWh)"] = round(data["Total Cost ($)"] / data["Total Usage (kWh)"], 4)
        
        return data
    except Exception as e:
        st.error(f"Error parsing utility data: {e}")
        return {}

def generate_report(data):
    """Create a well-structured PDF report with error handling."""
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(200, 10, "📄 Utility Bill Analysis Report", ln=True, align="C")
        pdf.ln(10)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Summary:", ln=True)
        pdf.set_font("Arial", "", 11)

        for key, value in data.items():
            safe_value = str(value).encode("latin-1", "ignore").decode("latin-1")
            pdf.cell(0, 10, f"{key}: {safe_value}", ln=True)

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
            if not pdf_text.strip():
                st.error("No text extracted from the PDF. Please try another file.")
                return
            extracted_data = parse_utility_data(pdf_text)
            if not extracted_data:
                st.error("Could not parse any meaningful data. Please check the file format.")
                return
            df = pd.DataFrame([extracted_data])
            
            st.success("✅ Data Extracted Successfully!")
            st.write(df)
            
            report_path = generate_report(extracted_data)
            if report_path:
                with open(report_path, "rb") as file:
                    st.download_button("📄 Download Report", data=file, file_name="Utility_Bill_Report.pdf")
            else:
                st.error("Failed to generate the report.")

if __name__ == "__main__":
    main()
