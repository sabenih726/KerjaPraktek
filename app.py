import streamlit as st
import pandas as pd
import os
import uuid
from datetime import datetime
import utils

# Page configuration
st.set_page_config(
    page_title="Trakindo Support System",
    page_icon="🎫",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Hide pages from sidebar for regular users and apply custom styling
# Load custom CSS file
with open('streamlit/style.css') as f:
    css = f.read()
    
# Add CSS to hide sidebar navigation
hide_pages_style = """
<style>
    div[data-testid="stSidebarNav"] {display: none !important;}
</style>
"""
# Apply both styles
st.markdown(f"""
{hide_pages_style}
<style>
{css}
</style>
""", unsafe_allow_html=True)

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

# Page title with Trakindo CAT theme
st.markdown("""
<div style="text-align: center; padding: 1.5rem 0; margin-bottom: 2rem;">
    <h1 style="color: #000000; font-size: 2.5rem; font-weight: 700; margin-bottom: 0.5rem;">
        <span style="color: #FFBB00;">🎫 Trakindo</span> Support System
    </h1>
    <p style="color: #6b7280; font-size: 1rem;">Submit and track support requests easily</p>
</div>
""", unsafe_allow_html=True)

# Create tabs for submission and tracking with improved styling
tab1, tab2 = st.tabs(["📝 Submit a Ticket", "🔍 Track Your Ticket"])

# Submit a Ticket tab
with tab1:
    st.markdown("""
    <h2 style="color: #111827; font-weight: 600; margin-bottom: 1rem; padding-bottom: 0.5rem; border-bottom: 1px solid #e5e7eb;">
        📝 Submit a New Support Ticket
    </h2>
    """, unsafe_allow_html=True)
    
    # Card-like container for the form
    st.markdown("""
    <div style="background-color: white; border-radius: 0.5rem; padding: 1rem; margin-bottom: 1rem; box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24);">
        <p style="color: #6b7280; font-size: 0.875rem;">
            Please fill out the form below to submit a new support ticket. All fields marked with * are required.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Ticket form with modern styling
    with st.form("ticket_submission_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Full Name *", placeholder="Enter your full name")
            email = st.text_input("Email Address *", placeholder="Enter your email address")
            category = st.selectbox(
                "Ticket Category *", 
                ["General Inquiry", "Technical Support", "Billing Issue", "Feature Request", "Bug Report", "Other"]
            )
        
        with col2:
            subject = st.text_input("Subject Line *", placeholder="Brief summary of your issue")
            priority = st.selectbox("Priority Level *", ["Low", "Medium", "High", "Critical"],
                                  help="Select the urgency of your issue")
        
        description = st.text_area(
            "Detailed Description *", 
            placeholder="Please provide detailed information about your issue including any steps to reproduce the problem",
            height=150
        )
        
        submit_button = st.form_submit_button("📤 Submit Ticket")
        
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
                
                # Success message with ticket ID
                st.success(f"Your ticket has been submitted successfully!")
                st.info(f"Your ticket ID is: **{ticket_id}**")
                st.info("Please save this ID to track the status of your ticket.")

# Track Your Ticket tab
with tab2:
    st.markdown("""
    <h2 style="color: #111827; font-weight: 600; margin-bottom: 1rem; padding-bottom: 0.5rem; border-bottom: 1px solid #e5e7eb;">
        🔍 Track Your Existing Ticket
    </h2>
    """, unsafe_allow_html=True)
    
    # Card-like container for the tracking form
    st.markdown("""
    <div style="background-color: white; border-radius: 0.5rem; padding: 1rem; margin-bottom: 1.5rem; box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24);">
        <p style="color: #6b7280; font-size: 0.875rem;">
            Enter your ticket ID below to check the status of your support request.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Modern tracking form
    col1, col2 = st.columns([3, 1])
    with col1:
        ticket_id = st.text_input("Enter your Ticket ID", key="track_ticket_id", placeholder="e.g. A1B2C3D4").strip().upper()
    with col2:
        track_button = st.button("🔍 Track Ticket", type="primary", use_container_width=True)
    
    if track_button:
        if not ticket_id:
            st.error("Please enter a ticket ID.")
        else:
            ticket_info = utils.get_ticket_by_id(ticket_id, data_file)
            
            if ticket_info is not None:
                st.success(f"Ticket found: {ticket_id}")
                
                # Status Card
                status = ticket_info['status']
                status_color = "#10B981" if status == "Open" else "#F59E0B" if status == "In Progress" else "#3B82F6" if status == "Resolved" else "#6B7280"
                status_icon = "🟢" if status == "Open" else "🟠" if status == "In Progress" else "🔵" if status == "Resolved" else "⚫"
                
                st.markdown(f"""
                <div style="background-color: white; border-radius: 0.5rem; padding: 1.5rem; margin-bottom: 1.5rem; box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24); border-left: 5px solid {status_color};">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                        <h3 style="margin: 0; color: #111827;">Ticket #{ticket_info['ticket_id']}</h3>
                        <span style="font-size: 1.25rem; background-color: {status_color}30; color: {status_color}; padding: 0.25rem 0.75rem; border-radius: 9999px; font-weight: 500;">
                            {status_icon} {status}
                        </span>
                    </div>
                    <h3 style="margin-top: 0; margin-bottom: 0.5rem; color: #111827;">{ticket_info['subject']}</h3>
                    <p style="color: #6B7280; margin-bottom: 0.25rem;">Submitted by {ticket_info['name']} on {ticket_info['created_at']}</p>
                    <p style="color: #6B7280; margin-bottom: 0.25rem;">Category: {ticket_info['category']} | Priority: {ticket_info['priority']}</p>
                    <p style="color: #6B7280; margin-bottom: 0;">Last Updated: {ticket_info['updated_at']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Ticket details in tabs
                details_tab, description_tab, resolution_tab = st.tabs(["📋 Details", "📝 Description", "✅ Resolution"])
                
                with details_tab:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("### Ticket Information")
                        st.markdown(f"**ID:** {ticket_info['ticket_id']}")
                        st.markdown(f"**Subject:** {ticket_info['subject']}")
                        st.markdown(f"**Category:** {ticket_info['category']}")
                        st.markdown(f"**Submitted by:** {ticket_info['name']}")
                    
                    with col2:
                        st.markdown("### Status Details")
                        st.markdown(f"**Current Status:** {ticket_info['status']}")
                        st.markdown(f"**Priority Level:** {ticket_info['priority']}")
                        st.markdown(f"**Created On:** {ticket_info['created_at']}")
                        st.markdown(f"**Last Updated:** {ticket_info['updated_at']}")
                
                with description_tab:
                    st.markdown("### Ticket Description")
                    st.markdown("""
                    <div style="background-color: #f9fafb; border-radius: 0.375rem; padding: 1rem; border: 1px solid #e5e7eb;">
                        <p style="white-space: pre-wrap;">{}</p>
                    </div>
                    """.format(ticket_info['description']), unsafe_allow_html=True)
                
                with resolution_tab:
                    if ticket_info['resolution']:
                        st.markdown("### Resolution Details")
                        st.markdown("""
                        <div style="background-color: #f0fdf4; border-radius: 0.375rem; padding: 1rem; border: 1px solid #d1fae5;">
                            <p style="white-space: pre-wrap;">{}</p>
                        </div>
                        """.format(ticket_info['resolution']), unsafe_allow_html=True)
                    else:
                        st.info("This ticket is still being processed. Check back later for updates.")
            else:
                st.error(f"No ticket found with ID: {ticket_id}")

# Footer with Trakindo CAT theme
st.markdown("""
<div style="margin-top: 3rem; padding-top: 1.5rem; border-top: 1px solid #e5e7eb; text-align: center;">
    <p style="color: #6b7280; font-size: 0.875rem;">© 2025 Trakindo Support System • Need help? <a href="mailto:support@trakindo.co.id" style="color: #FFBB00; text-decoration: none; font-weight: 500;">Contact Support</a></p>
</div>

<div class="admin-link">
    <a href="/admin_dashboard" target="_self">Admin</a>
</div>
""", unsafe_allow_html=True)
