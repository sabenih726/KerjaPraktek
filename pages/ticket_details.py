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
    page_title="Ticket Details - GA Ticket Management System",
    page_icon="🎫",
    layout="wide"
)

# Check if user is logged in
if 'user' not in st.session_state or st.session_state.user is None:
    st.switch_page("app.py")

# Get ticket ID from query parameters if available
query_params = st.query_params
ticket_id = query_params.get("ticket_id", [None])[0]

# Title
st.title("Ticket Details")

# If no ticket ID is provided in query params, show a selector
if not ticket_id:
    # Load tickets dataframe if not in session state
    if 'tickets_df' not in st.session_state:
        st.session_state.tickets_df = utils.load_tickets()
    
    # Display ticket selector
    if not st.session_state.tickets_df.empty:
        ticket_options = st.session_state.tickets_df['ticket_id'].tolist()
        ticket_id = st.selectbox("Select a ticket to view details", ticket_options)
    else:
        st.info("No tickets found in the system.")
        if st.button("Return to Dashboard"):
            st.switch_page("app.py")
        st.stop()

# Get ticket details
ticket_data = utils.get_ticket_by_id(ticket_id)

if ticket_data:
    # Display ticket information
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**Ticket ID:** {ticket_data['ticket_id']}")
        st.write(f"**Title:** {ticket_data['title']}")
        st.write(f"**Category:** {ticket_data['category']}")
        st.write(f"**Status:** {ticket_data['status']}")
    
    with col2:
        st.write(f"**Priority:** {ticket_data['priority']}")
        submit_date = pd.to_datetime(ticket_data['submit_date']).strftime('%Y-%m-%d %H:%M')
        st.write(f"**Submitted:** {submit_date}")
        st.write(f"**Requester:** {ticket_data['requester_name']}")
        st.write(f"**Department:** {ticket_data['department']}")
    
    # Description
    st.subheader("Description")
    st.write(ticket_data['description'])
    
    # Update notes history
    st.subheader("Update History")
    if pd.isna(ticket_data['update_notes']) or ticket_data['update_notes'] == "":
        st.info("No updates have been recorded for this ticket.")
    else:
        for note in ticket_data['update_notes'].split('\n'):
            st.write(note)
    
    # Update ticket form
    st.subheader("Update Ticket")
    
    # Only admin can change ticket status
    is_admin = st.session_state.user['role'] == 'admin'
    
    # Get admin users for assignment
    admin_users = utils.get_admin_users()
    admin_options = [""] + admin_users['username'].tolist() if not admin_users.empty else [""]
    
    with st.form("update_ticket_form"):
        new_status = st.selectbox(
            "New Status", 
            options=["Pending", "In Progress", "Completed", "Rejected"],
            index=["Pending", "In Progress", "Completed", "Rejected"].index(ticket_data['status']) if ticket_data['status'] in ["Pending", "In Progress", "Completed", "Rejected"] else 0,
            disabled=not is_admin
        )
        
        # If admin, show option to assign ticket
        if is_admin:
            assigned_to = st.selectbox(
                "Assign To", 
                options=admin_options,
                index=0 if 'assigned_to' not in ticket_data or not ticket_data['assigned_to'] else admin_options.index(ticket_data['assigned_to']) if ticket_data['assigned_to'] in admin_options else 0
            )
        else:
            assigned_to = None
        
        update_notes = st.text_area("Update Notes", "", disabled=not is_admin)
        
        # Only show active update button to admin
        update_button = st.form_submit_button("Update Ticket", disabled=not is_admin)
    
    if update_button and is_admin:
        if not update_notes:
            st.error("Please provide update notes before updating the ticket.")
        else:
            success = utils.update_ticket_status(ticket_id, new_status, update_notes, assigned_to)
            if success:
                st.success("Ticket updated successfully!")
                # Refresh the page to show updated information
                st.rerun()
            else:
                st.error("Failed to update ticket. Please try again.")
    elif not is_admin:
        st.info("Only administrators can update ticket status. Please contact the General Affairs department for updates.")
else:
    st.error(f"Ticket with ID {ticket_id} not found.")

# Button to return to dashboard
if st.button("Return to Dashboard"):
    st.switch_page("app.py")
