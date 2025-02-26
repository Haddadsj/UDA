import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import fitz  # PyMuPDF for PDF parsing
import os
from fpdf import FPDF

def extract_text_from_pdf(pdf_file):
    """Extract text from an uploaded PDF file."""
    doc = fitz.open(pdf_file)
    text = ""
    for page in doc:
        text += page.get_text("text") + "\n"
    return text

def parse_utility_data(text):
    """Extract key details from utility bills."""
    # Sample Parsing - This will be customized based on real bill formats
    data = {
        "Account Number": "Unknown",
        "Service Address": "Unknown",
        "Total Usage (kWh)": 0,
        "Total Cost ($)": 0.0,
        "Blended Rate ($/kWh)": 0.0
    }
    
    for line in text.split("\n"):
        if "Account" in line:
            data["Account Number"] = line.split(":")[-1].strip()
        if "Service Address" in line:
            data["Service Address"] = line.split(":")[-1].strip()
        if "Billed kWh" in line:
            data["Total Usage (kWh)"] = int(line.split()[-1].replace(",", ""))
        if "Total Due" in line or "Total Amount" in line:
            data["Total Cost ($)"] = float(line.split()[-1].replace("$", "").replace(",", ""))
    
    if data["Total Usage (kWh)"] > 0:
        data["Blended Rate ($/kWh)"] = round(data["Total Cost ($)"] / data["Total Usage (kWh)"], 4)
    
    return data

def generate_report(data):
    """Generate a PDF summary report."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, "Utility Bill Analysis Report", ln=True, align="C")
    pdf.ln(10)
    pdf.set_font("Arial", "", 12)
    for key, value in data.items():
        pdf.cell(0, 10, f"{key}: {value}", ln=True)
    report_path = "Utility_Bill_Analysis_Report.pdf"
    pdf.output(report_path)
    return report_path

def main():
    st.title("📊 Utility Bill Analysis Tool")
    st.write("Upload utility bills (PDF) and analyze usage, costs, and trends.")
    
    uploaded_file = st.file_uploader("Upload Utility Bill (PDF)", type=["pdf"])
    
    if uploaded_file:
        with st.spinner("Extracting data from PDF..."):
            pdf_text = extract_text_from_pdf(uploaded_file)
            extracted_data = parse_utility_data(pdf_text)
            df = pd.DataFrame([extracted_data])
            
            st.success("Data Extracted Successfully!")
            st.write(df)
            
            # Visualization
            fig, ax = plt.subplots()
            ax.bar("Usage", extracted_data["Total Usage (kWh)"], color='blue')
            ax.set_ylabel("kWh")
            ax.set_title("Total Electricity Usage")
            st.pyplot(fig)
            
            # Generate PDF Report
            report_path = generate_report(extracted_data)
            with open(report_path, "rb") as file:
                st.download_button(label="📄 Download Report", data=file, file_name="Utility_Bill_Report.pdf")

if __name__ == "__main__":
    main()
