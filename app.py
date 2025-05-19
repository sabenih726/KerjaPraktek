import streamlit as st
import pandas as pd
import os
import uuid
from datetime import datetime
import utils
import base64

# Function to load and display logo
def get_image_base64(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return ""

# Page configuration
st.set_page_config(
    page_title="Trakindo Support System",
    page_icon="🎫",
    layout="wide",  # Using wide layout to match the screenshot
    initial_sidebar_state="collapsed"
)

# Define Trakindo colors
trakindo_yellow = "#FFBB00"
trakindo_black = "#000000"
trakindo_gray = "#F0F0F0"

# Try to load CSS from streamlit folder (without dot)
custom_css = ""
css_path = "streamlit/style.css"
if os.path.exists(css_path):
    with open(css_path) as f:
        custom_css = f.read()

# CSS to make the app look like Trakindo screenshot
trakindo_style = f"""
<style>
    /* Hide default sidebar navigation */
    div[data-testid="stSidebarNav"] {{display: none !important;}}
    
    /* Body styling */
    body {{
        font-family: Arial, sans-serif;
        margin: 0;
        padding: 0;
    }}
    
    /* Header styling to match Trakindo style */
    .trakindo-header {{
        background-color: {trakindo_yellow};
        width: 100%;
        display: flex;
        padding: 10px 20px;
        align-items: center;
        justify-content: space-between;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }}
    
    .trakindo-logo {{
        height: 40px;
    }}
    
    .trakindo-menu {{
        display: flex;
        gap: 15px;
        font-size: 12px;
        color: {trakindo_black};
    }}
    
    .trakindo-menu-item {{
        padding: 5px 10px;
        cursor: pointer;
        font-weight: 500;
    }}
    
    .user-profile {{
        display: flex;
        align-items: center;
        gap: 5px;
        font-size: 12px;
    }}
    
    .user-icon {{
        width: 24px;
        height: 24px;
        background-color: #ccc;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
    }}
    
    /* Content area */
    .content-container {{
        background-color: white;
        border-radius: 5px;
        margin-top: 20px;
        padding: 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.12);
    }}
    
    /* Form styling */
    .stForm {{
        border: 1px solid #e5e7eb;
        border-radius: 4px;
        padding: 20px;
        background-color: white;
        margin-bottom: 20px;
    }}
    
    /* Button styling to match Trakindo */
    button[kind="primaryButton"] {{
        background-color: {trakindo_yellow} !important;
        color: {trakindo_black} !important;
        font-weight: 600 !important;
        border-radius: 3px !important;
    }}
    
    button[kind="primaryButton"]:hover {{
        background-color: #E6A800 !important;
    }}
    
    /* Input fields to match screenshot */
    div.stTextInput > div > div > input, 
    div.stTextArea > div > div > textarea,
    div.stSelectbox > div > div > div {{
        border-radius: 3px;
        border: 1px solid #d1d5db;
    }}
    
    div.stTextInput > div > div > input:focus, 
    div.stTextArea > div > div > textarea:focus,
    div.stSelectbox > div > div > div:focus {{
        border-color: {trakindo_yellow};
        box-shadow: 0 0 0 2px rgba(255, 187, 0, 0.2);
    }}
    
    /* Tabs to match Trakindo style */
    div.stTabs [data-baseweb="tab-list"] {{
        background-color: {trakindo_gray};
        border-bottom: none;
        padding: 5px 5px 0 5px;
    }}
    
    div.stTabs [role="tab"] {{
        border-radius: 4px 4px 0 0;
        padding: 10px 16px;
        background-color: #e5e7eb;
        margin-right: 3px;
        font-size: 14px;
    }}
    
    div.stTabs [aria-selected="true"] {{
        background-color: white;
        border: none;
        font-weight: bold;
        color: {trakindo_black};
    }}
    
    /* Search section */
    .search-section {{
        display: flex;
        gap: 10px;
        align-items: center;
        margin-bottom: 20px;
    }}
    
    /* Admin link */
    .admin-link {{
        position: fixed;
        bottom: 10px;
        right: 10px;
        color: #d1d5db;
        font-size: 10px;
    }}
    
    /* Footer */
    .trakindo-footer {{
        margin-top: 30px;
        padding-top: 20px;
        border-top: 1px solid #e5e7eb;
        text-align: center;
        font-size: 12px;
        color: #6b7280;
    }}
</style>
"""

# Use custom CSS if available, otherwise use the Trakindo style
st.markdown(custom_css if custom_css else trakindo_style, unsafe_allow_html=True)

# Create data directory if it doesn't exist
os.makedirs('data', exist_ok=True)
data_file = 'data/tickets.csv'

# Initialize dataframe if file doesn't exist
if not os.path.exists(data_file):
    initial_df = pd.DataFrame(columns=[
        'ticket_id', 'created_at', 'updated_at', 'name', 'email', 
        'subject', 'category', 'priority', 'status', 'description', 'resolution'
    ])
    initial_df.to_csv(data_file, index=False)

# Try to load Trakindo logo
logo_path = "images/trakindo_logo.png"
logo_base64 = get_image_base64(logo_path)

# Trakindo header that looks like the screenshot
if logo_base64:
    header_logo = f'<img src="data:image/png;base64,{logo_base64}" alt="Trakindo CAT" class="trakindo-logo">'
else:
    # Fallback if logo file doesn't exist
    header_logo = f'<div style="background-color: {trakindo_yellow}; color: {trakindo_black}; padding: 5px 10px; font-weight: bold; font-size: 16px;">Trakindo CAT</div>'

# Create header that looks like the screenshot
st.markdown(f"""
<div class="trakindo-header">
    {header_logo}
    <div class="trakindo-menu">
        <div class="trakindo-menu-item">Home</div>
        <div class="trakindo-menu-item">Quick Search</div>
        <div class="trakindo-menu-item">Advanced Search</div>
        <div class="trakindo-menu-item">Shipment</div>
        <div class="trakindo-menu-item">Invoice CKB</div>
        <div class="trakindo-menu-item">Reports</div>
        <div class="trakindo-menu-item">User Manual</div>
        <div class="trakindo-menu-item">Viewer</div>
        <div class="trakindo-menu-item">Log Off</div>
    </div>
    <div class="user-profile">
        <div class="user-icon">U</div>
        <span>User</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Main content container to match the screenshot style
st.markdown("""
<div class="content-container">
    <h1 style="font-size: 24px; color: #333; margin-bottom: 20px;">Support Ticket System</h1>
</div>
""", unsafe_allow_html=True)

# Create tabs for submission and tracking with Trakindo styling
tab1, tab2 = st.tabs(["Submit a Ticket", "Track Your Ticket"])

# Submit a Ticket tab
with tab1:
    st.markdown("""
    <h2 style="font-size: 18px; color: #333; margin-bottom: 15px; padding-bottom: 10px; border-bottom: 1px solid #e5e7eb;">
        Submit a New Support Ticket
    </h2>
    """, unsafe_allow_html=True)
    
    # Ticket form with Trakindo styling
    with st.form("ticket_submission_form"):
        # Layout similar to the screenshot with label:field pattern
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Requester Name", placeholder="Enter your full name")
            email = st.text_input("Email Address", placeholder="Enter your email address")
            category = st.selectbox(
                "Request Category", 
                ["General Inquiry", "Technical Support", "Billing Issue", "Feature Request", "Bug Report", "Other"]
            )
        
        with col2:
            subject = st.text_input("Subject Line", placeholder="Brief summary of your issue")
            priority = st.selectbox("Priority Level", ["Low", "Medium", "High", "Critical"],
                                  help="Select the urgency of your issue")
        
        description = st.text_area(
            "Detailed Description", 
            placeholder="Please provide detailed information about your issue",
            height=150
        )
        
        submit_button = st.form_submit_button("Submit Request")
        
        if submit_button:
            if not name or not email or not subject or not description:
                st.error("Please fill in all required fields.")
            elif not utils.is_valid_email(email):
                st.error("Please enter a valid email address.")
            else:
                # Generate unique ticket ID
                ticket_id = str(uuid.uuid4())[:8].upper()
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # Create new ticket
                new_ticket = {
                    'ticket_id': ticket_id,
                    'created_at': timestamp,
                    'updated_at': timestamp,
                    'name': name,
                    'email': email,
                    'subject': subject,
                    'category': category,
                    'priority': priority,
                    'status': "Open",
                    'description': description,
                    'resolution': ""
                }
                
                # Save to CSV
                utils.add_ticket(new_ticket, data_file)
                
                # Success message with ticket ID similar to Trakindo alerts
                st.success(f"Your request has been submitted successfully!")
                st.info(f"Your reference number is: **{ticket_id}**. Please save this ID to track the status of your request.")

# Track Your Ticket tab
with tab2:
    st.markdown("""
    <h2 style="font-size: 18px; color: #333; margin-bottom: 15px; padding-bottom: 10px; border-bottom: 1px solid #e5e7eb;">
        Track Your Existing Ticket
    </h2>
    """, unsafe_allow_html=True)
    
    # Search section similar to the screenshot
    st.markdown("""
    <div style="background-color: #f9fafb; border-radius: 4px; padding: 15px; margin-bottom: 20px;">
        <p style="margin-bottom: 10px; font-weight: 500; font-size: 14px;">Enter your ticket ID below</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Layout similar to the screenshot search bar
    col1, col2 = st.columns([3, 1])
    with col1:
        ticket_id = st.text_input("Ticket ID", key="track_ticket_id", placeholder="e.g. A1B2C3D4").strip().upper()
    with col2:
        track_button = st.button("Search", type="primary", use_container_width=True)
    
    if track_button:
        if not ticket_id:
            st.error("Please enter a ticket ID.")
        else:
            ticket_info = utils.get_ticket_by_id(ticket_id, data_file)
            
            if ticket_info is not None:
                st.success(f"Ticket found: {ticket_id}")
                
                # Ticket details in a Trakindo-like table
                st.markdown("""
                <div style="background-color: white; border-radius: 4px; border: 1px solid #e5e7eb; margin-top: 20px;">
                    <div style="background-color: #f9fafb; padding: 10px 15px; border-bottom: 1px solid #e5e7eb; font-weight: 500;">
                        Ticket Details
                    </div>
                    <div style="padding: 15px;">
                """, unsafe_allow_html=True)
                
                # Status indicator with Trakindo styling
                status = ticket_info['status']
                status_color = "#10B981" if status == "Open" else "#F59E0B" if status == "In Progress" else "#3B82F6" if status == "Resolved" else "#6B7280"
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"""
                    <table style="width: 100%; border-collapse: collapse; font-size: 14px;">
                        <tr>
                            <td style="padding: 8px; border-bottom: 1px solid #eee; width: 35%; font-weight: 500;">Ticket ID</td>
                            <td style="padding: 8px; border-bottom: 1px solid #eee;">{ticket_info['ticket_id']}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px; border-bottom: 1px solid #eee; font-weight: 500;">Subject</td>
                            <td style="padding: 8px; border-bottom: 1px solid #eee;">{ticket_info['subject']}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px; border-bottom: 1px solid #eee; font-weight: 500;">Requester</td>
                            <td style="padding: 8px; border-bottom: 1px solid #eee;">{ticket_info['name']}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px; border-bottom: 1px solid #eee; font-weight: 500;">Email</td>
                            <td style="padding: 8px; border-bottom: 1px solid #eee;">{ticket_info['email']}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px; border-bottom: 1px solid #eee; font-weight: 500;">Category</td>
                            <td style="padding: 8px; border-bottom: 1px solid #eee;">{ticket_info['category']}</td>
                        </tr>
                    </table>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <table style="width: 100%; border-collapse: collapse; font-size: 14px;">
                        <tr>
                            <td style="padding: 8px; border-bottom: 1px solid #eee; width: 35%; font-weight: 500;">Status</td>
                            <td style="padding: 8px; border-bottom: 1px solid #eee;">
                                <span style="display: inline-block; padding: 4px 8px; border-radius: 4px; background-color: {status_color}20; color: {status_color}; font-weight: 500;">
                                    {status}
                                </span>
                            </td>
                        </tr>
                        <tr>
                            <td style="padding: 8px; border-bottom: 1px solid #eee; font-weight: 500;">Priority</td>
                            <td style="padding: 8px; border-bottom: 1px solid #eee;">{ticket_info['priority']}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px; border-bottom: 1px solid #eee; font-weight: 500;">Created On</td>
                            <td style="padding: 8px; border-bottom: 1px solid #eee;">{ticket_info['created_at']}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px; border-bottom: 1px solid #eee; font-weight: 500;">Last Updated</td>
                            <td style="padding: 8px; border-bottom: 1px solid #eee;">{ticket_info['updated_at']}</td>
                        </tr>
                    </table>
                    """, unsafe_allow_html=True)
                
                st.markdown("</div></div>", unsafe_allow_html=True)
                
                # Description and resolution sections
                st.markdown("""
                <div style="background-color: white; border-radius: 4px; border: 1px solid #e5e7eb; margin-top: 20px;">
                    <div style="background-color: #f9fafb; padding: 10px 15px; border-bottom: 1px solid #e5e7eb; font-weight: 500;">
                        Ticket Description
                    </div>
                    <div style="padding: 15px;">
                        <p style="white-space: pre-wrap; margin: 0;">{}</p>
                    </div>
                </div>
                """.format(ticket_info['description']), unsafe_allow_html=True)
                
                if ticket_info['resolution']:
                    st.markdown("""
                    <div style="background-color: white; border-radius: 4px; border: 1px solid #e5e7eb; margin-top: 20px;">
                        <div style="background-color: #f9fafb; padding: 10px 15px; border-bottom: 1px solid #e5e7eb; font-weight: 500;">
                            Resolution
                        </div>
                        <div style="padding: 15px;">
                            <p style="white-space: pre-wrap; margin: 0;">{}</p>
                        </div>
                    </div>
                    """.format(ticket_info['resolution']), unsafe_allow_html=True)
                else:
                    st.info("This request is still being processed. Check back later for updates.")
            else:
                st.error(f"No ticket found with ID: {ticket_id}")

# Footer with Trakindo CAT styling from screenshot
st.markdown("""
<div class="trakindo-footer">
    <p>© 2025 Trakindo Support System • Need help? <a href="mailto:support@trakindo.co.id" style="color: #FFBB00; text-decoration: none; font-weight: 500;">Contact Support</a></p>
</div>

<div class="admin-link">
    <a href="/admin_dashboard" target="_self">Admin</a>
</div>
""", unsafe_allow_html=True)
