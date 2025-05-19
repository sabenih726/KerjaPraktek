import streamlit as st
import pandas as pd
import os
import uuid
from datetime import datetime
import utils

# Page configuration
st.set_page_config(
    page_title="GA Ticket System",
    page_icon="🎫",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Hide pages from sidebar for regular users
# CSS to hide the sidebar links
hide_pages_style = """
<style>
    div[data-testid="stSidebarNav"] {display: none !important;}
</style>
"""
st.markdown(hide_pages_style, unsafe_allow_html=True)

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

# Page title
st.title("🎫 GA Ticket System")

# Create tabs for submission and tracking
tab1, tab2 = st.tabs(["Submit a Ticket", "Track Your Ticket"])

# Submit a Ticket tab
with tab1:
    st.header("Submit a New Support Ticket")
    
    # Ticket form
    with st.form("ticket_submission_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Name", placeholder="Enter your full name")
            email = st.text_input("Email", placeholder="Enter your email address")
            category = st.selectbox(
                "Category", 
                ["General Inquiry", "Technical Support", "Billing Issue", "Feature Request", "Bug Report", "Other"]
            )
        
        with col2:
            subject = st.text_input("Subject", placeholder="Brief summary of your issue")
            priority = st.selectbox("Priority", ["Low", "Medium", "High", "Critical"])
        
        description = st.text_area(
            "Description", 
            placeholder="Please provide detailed information about your issue",
            height=150
        )
        
        submit_button = st.form_submit_button("Submit Ticket")
        
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
    st.header("Track Your Ticket")
    ticket_id = st.text_input("Enter your Ticket ID", key="track_ticket_id").strip().upper()
    
    if st.button("Track Ticket"):
        if not ticket_id:
            st.error("Please enter a ticket ID.")
        else:
            ticket_info = utils.get_ticket_by_id(ticket_id, data_file)
            
            if ticket_info is not None:
                st.success(f"Ticket found: {ticket_id}")
                
                # Display ticket information in an organized way
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.subheader("Ticket Details")
                    st.markdown(f"**ID:** {ticket_info['ticket_id']}")
                    st.markdown(f"**Subject:** {ticket_info['subject']}")
                    st.markdown(f"**Category:** {ticket_info['category']}")
                    st.markdown(f"**Submitted by:** {ticket_info['name']}")
                
                with col2:
                    st.subheader("Status Information")
                    st.markdown(f"**Status:** {ticket_info['status']}")
                    st.markdown(f"**Priority:** {ticket_info['priority']}")
                    st.markdown(f"**Created:** {ticket_info['created_at']}")
                    st.markdown(f"**Last Updated:** {ticket_info['updated_at']}")
                
                with col3:
                    # Display status indicator
                    status = ticket_info['status']
                    if status == "Open":
                        st.markdown("### 🟢 Open")
                    elif status == "In Progress":
                        st.markdown("### 🟠 In Progress")
                    elif status == "Resolved":
                        st.markdown("### 🔵 Resolved")
                    elif status == "Closed":
                        st.markdown("### ⚫ Closed")
                    else:
                        st.markdown(f"### {status}")
                
                # Description and Resolution in separate containers
                st.subheader("Ticket Description")
                st.write(ticket_info['description'])
                
                if ticket_info['resolution']:
                    st.subheader("Resolution")
                    st.write(ticket_info['resolution'])
                else:
                    st.info("This ticket is still being processed. Check back later for updates.")
            else:
                st.error(f"No ticket found with ID: {ticket_id}")

# Footer
st.markdown("---")
st.markdown("© GA Ticket System • Need help? Contact support@gatickets.com")

# Small admin link at the bottom (accessible to those who know about it)
st.markdown("""
<div style="position: fixed; bottom: 5px; right: 5px; font-size: 10px;">
    <a href="/admin_dashboard" target="_self" style="color: #d3d3d3; text-decoration: none;">Admin</a>
</div>
""", unsafe_allow_html=True)
