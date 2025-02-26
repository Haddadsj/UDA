import streamlit as st
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Custom CSS for styling with your color scheme and enhanced design
st.markdown("""
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
    <style>
        .main {
            background: linear-gradient(135deg, #F5F5F5 0%, #E7E6E6 100%);
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
            animation: fadeIn 1.5s ease-in;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(-20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .title-container {
            background-color: #0068FF;
            padding: 20px;
            border-radius: 15px 15px 0 0;
            color: white;
            text-align: center;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }
        .stButton>button {
            background-color: #0068FF;
            color: white;
            border-radius: 10px;
            padding: 12px 24px;
            border: none;
            cursor: pointer;
            transition: background-color 0.3s, transform 0.2s;
        }
        .stButton>button:hover {
            background-color: #0052CC;
            transform: scale(1.05);
        }
        .stTextInput, .stTextArea, .stSelectbox, .stMultiSelect {
            border: 2px solid #E7E6E6;
            border-radius: 10px;
            padding: 10px;
            transition: border-color 0.3s;
        }
        .stTextInput:focus, .stTextArea:focus, .stSelectbox:focus, .stMultiSelect:focus {
            border-color: #0068FF;
            outline: none;
        }
        .stHeader {
            color: #434E5E;
            font-size: 2.5em;
            font-weight: bold;
            margin-bottom: 0;
        }
        .stSubheader {
            color: #0068FF;
            font-size: 1.2em;
            margin-top: 5px;
        }
        .form-group {
            margin-bottom: 15px;
        }
        .form-group label {
            color: #434E5E;
            font-weight: bold;
            margin-bottom: 5px;
        }
        .form-group i {
            color: #0068FF;
            margin-right: 10px;
        }
    </style>
""", unsafe_allow_html=True)

# Title and description with custom styling
st.markdown('<div class="title-container"><h1 class="stHeader">4 Sales Docs Intake Form</h1>', unsafe_allow_html=True)
st.markdown('<p class="stSubheader">Please fill out the details below to help us understand your needs.</p></div>', unsafe_allow_html=True)
st.markdown('<div class="main">', unsafe_allow_html=True)

# Form with unique keys for each widget
with st.form(key="sales_docs_form"):
    # Basic company information
    company_name = st.text_input("Company Name", key="company_name", help="Enter your company name")
    company_contact = st.text_input("Company Contact", key="company_contact", help="Enter the primary contact name")
    contact_email = st.text_input("Contact Email", key="contact_email", help="Enter the contact email")
    company_address = st.text_area("Company Address", key="company_address", height=100, help="Enter your company address")
    website_url = st.text_input("Website URL", key="website_url", help="Enter your company website")

    # Descriptions
    company_description = st.text_area("Brief Company Description", key="company_description", height=150, help="Describe your company briefly")
    service_product_description = st.text_area("Service/Product Description", key="service_product_description", height=150, help="Describe your service or product")
    usp = st.text_area("Unique Selling Proposition (USP)", key="usp", height=150, help="What makes your offering unique?")

    # Multi-select for Target Audience
    target_audience = st.multiselect(
        "Target Audience / Primary Customer (Select All That Apply)", 
        ["Individuals", "Small Businesses", "Medium Businesses", "Large Enterprises", "Non-Profits", "Government", "Other"],
        key="target_audience"
    )

    # Challenges and goals
    customer_challenges = st.text_area("What are the main challenges or problems your customers face that your product/service solves?", key="customer_challenges", height=150)
    sales_docs_goals = st.text_area("What do you hope to achieve by using 4 Sales Docs?", key="sales_docs_goals", height=150)
    additional_comments = st.text_area("Additional Comments", key="additional_comments", height=150)

    # Multi-select for Biggest Sales Challenges
    sales_challenges = st.multiselect(
        "Biggest Sales Challenges (Please select all that apply)",
        ["Lead Generation", "Closing Deals", "Customer Retention", "Pricing Strategy", "Competition", "Sales Team Training", "Other"],
        key="sales_challenges"
    )

    # Multi-select for Top Priorities (up to 3)
    top_priorities = st.multiselect(
        "What are your top priorities for the next year? (Select up to 3)",
        ["Increase Revenue", "Expand Market Share", "Improve Customer Satisfaction", "Launch New Products", "Optimize Operations", "Hire/Train Staff", "Other"],
        max_selections=3,
        key="top_priorities"
    )

    # Additional questions
    additional_questions = st.text_area("Anything Additional you would like to know?", key="additional_questions", height=150)

    # File uploader for existing sales docs
    uploaded_files = st.file_uploader("Upload existing sales docs", accept_multiple_files=True, type=["pdf", "docx", "txt"], key="uploaded_files")

    # Submit button (ensuring it’s properly included in the form)
    submit_button = st.form_submit_button(label="Submit Form")

    # On submit, display the data and send email
    if submit_button:
        if not company_name or not contact_email:  # Basic validation
            st.error("Please fill in the Company Name and Contact Email.")
        else:
            # Prepare data for display and email
            form_data = {
                "Company Name": company_name,
                "Company Contact": company_contact,
                "Contact Email": contact_email,
                "Company Address": company_address,
                "Website URL": website_url,
                "Brief Company Description": company_description,
                "Service/Product Description": service_product_description,
                "Unique Selling Proposition (USP)": usp,
                "Target Audience / Primary Customer": target_audience,
                "Customer Challenges": customer_challenges,
                "Goals with 4 Sales Docs": sales_docs_goals,
                "Additional Comments": additional_comments,
                "Biggest Sales Challenges": sales_challenges,
                "Top Priorities for Next Year": top_priorities,
                "Additional Questions": additional_questions,
                "Uploaded Files": [file.name for file in uploaded_files] if uploaded_files else "None"
            }
            
            st.success("Thank you for submitting! Here’s what you entered:")
            st.write(pd.DataFrame([form_data]))

            # Email setup (using Gmail as an example)
            sender_email = "your_gmail_account@gmail.com"  # Replace with your Gmail
            sender_password = "your_app_password"  # Replace with your Gmail App Password
            recipient_email = "samijhaddad@icloud.com"

            # Create email
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = recipient_email
            msg['Subject'] = "New 4 Sales Docs Intake Form Submission"

            # Format the form data as a string for the email body
            body = "New submission received:\n\n" + "\n".join([f"{key}: {value}" for key, value in form_data.items()])
            msg.attach(MIMEText(body, 'plain'))

            try:
                # Connect to Gmail's SMTP server and send the email
                with smtplib.SMTP('smtp.gmail.com', 587) as server:
                    server.starttls()
                    server.login(sender_email, sender_password)
                    server.send_message(msg)
                st.success("Submission has been emailed successfully to samijhaddad@icloud.com!")
            except Exception as e:
                st.error(f"Failed to send email: {str(e)}")

st.markdown('</div>', unsafe_allow_html=True)
