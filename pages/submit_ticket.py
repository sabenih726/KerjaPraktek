import streamlit as st
import pandas as pd
from datetime import datetime
import sys
import os

# Add parent directory to path to import utils
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import utils

# Page configuration
st.set_page_config(
    page_title="Submit Ticket - GA Ticket Management System",
    page_icon="🎫",
    layout="wide"
)

# Check if user is logged in
if 'user' not in st.session_state or st.session_state.user is None:
    st.switch_page("app.py")

# Title and description
st.title("Submit a New Ticket")
st.markdown("Use this form to submit a new service request to the General Affairs division")

# Create a form for ticket submission
with st.form("ticket_submission_form"):
    # Basic ticket information
    col1, col2 = st.columns(2)
    
    with col1:
        title = st.text_input("Ticket Title *", help="Brief summary of the request")
        
        category = st.selectbox(
            "Category *",
            options=utils.get_ticket_categories(),
            help="Select the category that best fits your request"
        )
        
        priority = st.select_slider(
            "Priority *",
            options=["Low", "Medium", "High", "Urgent"],
            value="Medium",
            help="Select the priority level for this request"
        )
    
    with col2:
        # Use the logged-in user's information
        requester_name = st.text_input("Your Name *", 
                                    value=st.session_state.user['full_name'],
                                    help="Name of the person requesting service")
        
        requester_email = st.text_input("Your Email *", 
                                     value=st.session_state.user['email'],
                                     help="Email address for follow-up communications")
        
        department = st.text_input("Department *", 
                                value=st.session_state.user['department'],
                                help="Your department or division")
    
    # Description
    description = st.text_area(
        "Description *", 
        height=150,
        help="Provide detailed information about your request"
    )
    
    # Submit button
    submit_button = st.form_submit_button("Submit Ticket")

# Processing form submission
if submit_button:
    # Validate required fields
    required_fields = {
        'title': title,
        'category': category,
        'priority': priority,
        'requester_name': requester_name,
        'requester_email': requester_email,
        'department': department,
        'description': description
    }
    
    missing_fields = [field for field, value in required_fields.items() if not value]
    
    if missing_fields:
        st.error(f"Please fill in the following required fields: {', '.join(missing_fields)}")
    else:
        # Prepare ticket data
        ticket_data = {
            'ticket_id': utils.generate_ticket_id(),
            'title': title,
            'description': description,
            'category': category,
            'priority': priority,
            'status': 'Pending',
            'requester_name': requester_name,
            'requester_email': requester_email,
            'department': department,
            'submit_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'updated_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'update_notes': ''
        }
        
        # Save ticket
        ticket_id = utils.save_ticket(ticket_data)
        
        # Show success message
        st.success(f"Ticket submitted successfully! Your ticket ID is {ticket_id}")
        
        # Display ticket details
        with st.expander("Ticket Details", expanded=True):
            st.write(f"**Ticket ID:** {ticket_id}")
            st.write(f"**Title:** {title}")
            st.write(f"**Category:** {category}")
            st.write(f"**Priority:** {priority}")
            st.write(f"**Status:** Pending")
            st.write(f"**Submitted by:** {requester_name}, {department}")
            st.write(f"**Description:**")
            st.write(description)
        
        # Provide button to go back to main dashboard
        if st.button("Return to Dashboard"):
            st.switch_page("app.py")

# Button to return to dashboard
if st.button("Cancel and Return to Dashboard"):
    st.switch_page("app.py")
