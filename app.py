import streamlit as st
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Set page configuration to remove the default Streamlit header and use full width
st.set_page_config(page_title="4 Sales Docs Intake Form", layout="wide", initial_sidebar_state="collapsed")

# Custom CSS for styling with Tesla/Grok-inspired design and white text
st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
    <style>
        /* Hide the default Streamlit header/menu bar and set full-page styling */
        header, .stAppHeader, .css-1d391kg, .st-emotion-cache-1d391kg, .reportview-container .main .block-container, .stMarkdown, .stText, .stDataFrame {
            display: none !important;
        }
        body, html {
            margin: 0;
            padding: 0;
            background: linear-gradient(135deg, #1A1A2E 0%, #16213E 100%); /* Dark futuristic background */
            font-family: 'Montserrat', sans-serif;
            overflow-x: hidden;
            color: white; /* Default text color set to white */
        }
        .main {
            background: linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(231, 230, 230, 0.1) 100%), #16213E; /* Subtle overlay on dark background */
            padding: 30px;
            border-radius: 20px;
            box-shadow: 0 10px 30px rgba(0, 104, 255, 0.3); /* Blue glow shadow */
            animation: pulse 3s infinite ease-in-out;
            margin: 20px auto;
            max-width: 900px;
        }
        @keyframes pulse {
            0% { box-shadow: 0 10px 30px rgba(0, 104, 255, 0.3); }
            50% { box-shadow: 0 15px 40px rgba(0, 104, 255, 0.5); }
            100% { box-shadow: 0 10px 30px rgba(0, 104, 255, 0.3); }
        }
        .title-container {
            background: linear-gradient(45deg, #0068FF, #00D2FF); /* Neon blue gradient */
            padding: 30px;
            border-radius: 20px 20px 0 0;
            color: white; /* White text for title */
            text-align: center;
            box-shadow: 0 5px 15px rgba(0, 104, 255, 0.5);
            animation: slideIn 1s ease-out;
        }
        @keyframes slideIn {
            from { transform: translateY(-50px); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }
        .stButton>button {
            background: linear-gradient(45deg, #0068FF, #00D2FF);
            color: white; /* White text for button */
            border-radius: 15px;
            padding: 15px 30px;
            border: none;
            cursor: pointer;
            font-weight: bold;
            transition: transform 0.3s, background 0.3s;
            position: relative;
            overflow: hidden;
        }
        .stButton>button:hover {
            transform: scale(1.1);
            background: linear-gradient(45deg, #0052CC, #0099FF);
        }
        .stButton>button::after {
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            width: 0;
            height: 0;
            background: rgba(255, 255, 255, 0.2);
            border-radius: 50%;
            transform: translate(-50%, -50%);
            transition: width 0.6s, height 0.6s;
        }
        .stButton>button:hover::after {
            width: 200px;
            height: 200px;
        }
        .stTextInput, .stTextArea, .stSelectbox, .stMultiSelect, .stFileUploader {
            border: 2px solid #E7E6E6;
            border-radius: 15px;
            padding: 12px;
            background: rgba(255, 255, 255, 0.9);
            transition: border-color 0.3s, box-shadow 0.3s;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            color: #434E5E; /* Dark Grey for input text to contrast with white background */
        }
        .stTextInput:focus, .stTextArea:focus, .stSelectbox:focus, .stMultiSelect:focus, .stFileUploader:focus {
            border-color: #0068FF;
            box-shadow: 0 4px 20px rgba(0, 104, 255, 0.4);
            outline: none;
        }
        .stTextInput::placeholder, .stTextArea::placeholder {
            color: #A0A0A0; /* Light grey placeholder text for visibility */
        }
        .stHeader {
            color: white; /* White text for headers */
            font-size: 2.8em;
            font-weight: bold;
            text-shadow: 0 2px 5px rgba(0, 104, 255, 0.3);
            margin-bottom: 0;
        }
        .stSubheader {
            color: #00D2FF; /* Bright neon blue */
            font-size: 1.3em;
            margin-top: 5px;
            text-shadow: 0 1px 3px rgba(0, 104, 255, 0.3);
        }
        .form-group {
            margin-bottom: 20px;
        }
        .form-group label {
            color: white; /* White text for labels */
            font-weight: bold;
            margin-bottom: 8px;
            text-shadow: 0 1px 2px rgba(0, 104, 255, 0.2);
        }
        .form-group i {
            color: #00D2FF; /* Bright neon blue for icons */
            margin-right: 12px;
            animation: bounce 2s infinite;
        }
        @keyframes bounce {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-5px); }
        }
        /* Particle animation for extra fun */
        #particles-js {
            position: absolute;
            width: 100%;
            height: 100%;
            z-index: -1;
        }
    </style>
    <div id="particles-js"></div>
    <script src="https://cdn.jsdelivr.net/particles.js/2.0.0/particles.min.js"></script>
    <script>
        particlesJS('particles-js', {
            "particles": {
                "number": { "value": 80, "density": { "enable": true, "value_area": 800 } },
                "color": { "value": "#00D2FF" },
                "shape": { "type": "circle" },
                "opacity": { "value": 0.5, "random": true },
                "size": { "value": 3, "random": true },
                "line_linked": { "enable": true, "distance": 150, "color": "#00D2FF", "opacity": 0.4, "width": 1 },
                "move": { "enable": true, "speed": 2, "direction": "none", "random": true, "straight": false, "out_mode": "out" }
            },
            "interactivity": {
                "detect_on": "canvas",
                "events": { "onhover": { "enable": true, "mode": "repulse" }, "onclick": { "enable": true, "mode": "push" } },
                "modes": { "repulse": { "distance": 100, "duration": 0.4 } }
            }
        });
    </script>
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
