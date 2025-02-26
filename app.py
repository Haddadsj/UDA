import streamlit as st
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Custom CSS for styling with your color scheme
st.markdown("""
    <style>
        .main {
            background-color: #F5F5F5;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .title-container {
            background-color: #0068FF; /* Blue for title background */
            padding: 20px;
            border-radius: 10px 10px 0 0;
            color: white; /* White text for title */
        }
        .stButton>button {
            background-color: #0068FF; /* Blue */
            color: white;
            border-radius: 5px;
            padding: 10px 20px;
            border: none;
            cursor: pointer;
        }
        .stButton>button:hover {
            background-color: #0052CC;
        }
        .stTextInput, .stTextArea, .stSelectbox, .stMultiSelect {
            border: 1px solid #E7E6E6; /* Light Grey */
            border-radius: 5px;
            padding: 5px;
        }
        .stHeader {
            color: #434E5E; /* Dark Grey */
            font-size: 2em;
            font-weight: bold;
        }
        .stSubheader {
            color: #0068FF; /* Blue */
        }
    </style>
""", unsafe_allow_html=True)

# Title and description with custom styling
st.markdown('<div class="title-container"><h1 class="stHeader">4 Sales Docs Intake Form</h1>', unsafe_allow_html=True)
st.markdown('<p class="stSubheader">Please fill out the details below to help us understand your needs.</p></div>', unsafe_allow_html=True)
st.markdown('<div class="main">', unsafe_allow_html=True)

# Form
with st.form(key="sales_docs_form"):
    # Basic company information
    company_name = st.text_input("Company Name")
    company_contact = st.text_input("Company Contact")
    contact_email = st.text_input("Contact Email")
    company_address = st.text_area("Company Address")
    website_url = st.text_input("Website URL")

    # Descriptions
    company_description = st.text_area("Brief Company Description")
    service_product_description = st.text_area("Service/Product Description")
    usp = st.text_area("Unique Selling Proposition (USP)")

    # Multi-select for Target Audience
    target_audience = st.multiselect(
        "Target Audience / Primary Customer (Select All That Apply)",
        ["Individuals", "Small Businesses", "Medium Businesses", "Large Enterprises", "Non-Profits", "Government", "Other"]
    )

    # Challenges and goals
    customer_challenges = st.text_area("What are the main challenges or problems your customers face that your product/service solves?")
    sales_docs_goals = st.text_area("What do you hope to achieve by using 4 Sales Docs?")
    additional_comments = st.text_area("Additional Comments")

    # Multi-select for Biggest Sales Challenges
    sales_challenges = st.multiselect(
        "Biggest Sales Challenges (Please select all that apply)",
        ["Lead Generation", "Closing Deals", "Customer Retention", "Pricing Strategy", "Competition", "Sales Team Training", "Other"]
    )

    # Multi-select for Top Priorities (up to 3)
    top_priorities = st.multiselect(
        "What are your top priorities for the next year? (Select up to 3)",
        ["Increase Revenue", "Expand Market Share", "Improve Customer Satisfaction", "Launch New Products", "Optimize Operations", "Hire/Train Staff", "Other"],
        max_selections=3
    )

    # Additional questions
    additional_questions = st.text_area("Anything Additional you would like to know?")

    # File uploader for existing sales docs
    uploaded_files = st.file_uploader("Upload existing sales docs", accept_multiple_files=True, type=["pdf", "docx", "txt"])

    # Submit button
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
