import streamlit as st
import pandas as pd
import sys
import os
from datetime import datetime

# Add parent directory to path to import utils
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import utils

# Page configuration
st.set_page_config(
    page_title="Admin Dashboard - GA Ticket Management System",
    page_icon="🎫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Check if user is logged in and is admin
if 'user' not in st.session_state or st.session_state.user is None:
    st.switch_page("app.py")
elif st.session_state.user['role'] != 'admin':
    st.error("You don't have permission to access this page. Admin access required.")
    if st.button("Return to Home"):
        st.switch_page("app.py")
    st.stop()

# Load tickets
if 'tickets_df' not in st.session_state:
    st.session_state.tickets_df = utils.load_tickets()

# Title and description
st.title("Admin Dashboard")
st.markdown(f"Manage tickets and system configuration | Logged in as: {st.session_state.user['full_name']} ({st.session_state.user['role'].capitalize()})")

# Sidebar user info
st.sidebar.header("User Information")
st.sidebar.write(f"**Name:** {st.session_state.user['full_name']}")
st.sidebar.write(f"**Role:** {st.session_state.user['role'].capitalize()}")
st.sidebar.write(f"**Department:** {st.session_state.user['department']}")

if st.sidebar.button("Logout"):
    st.session_state.user = None
    st.switch_page("app.py")

st.sidebar.markdown("---")

# Sidebar filters
st.sidebar.header("Filters")

# Get unique categories and statuses for filters
categories = ['All'] + sorted(st.session_state.tickets_df['category'].unique().tolist())
statuses = ['All'] + sorted(st.session_state.tickets_df['status'].unique().tolist())

# Category filter
selected_category = st.sidebar.selectbox("Category", categories)

# Status filter
selected_status = st.sidebar.selectbox("Status", statuses)

# Search by title or description
search_term = st.sidebar.text_input("Search tickets")

# Filter the dataframe based on selections
filtered_df = utils.filter_tickets(
    st.session_state.tickets_df, 
    selected_category, 
    selected_status, 
    search_term
)

# Display ticket statistics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Tickets", len(st.session_state.tickets_df))
    
with col2:
    pending_count = len(st.session_state.tickets_df[st.session_state.tickets_df['status'] == 'Pending'])
    st.metric("Pending Tickets", pending_count)
    
with col3:
    in_progress_count = len(st.session_state.tickets_df[st.session_state.tickets_df['status'] == 'In Progress'])
    st.metric("In Progress", in_progress_count)
    
with col4:
    completed_count = len(st.session_state.tickets_df[st.session_state.tickets_df['status'] == 'Completed'])
    st.metric("Completed Tickets", completed_count)

# Display tickets table
if not filtered_df.empty:
    # Prepare display dataframe
    display_df = filtered_df.copy()
    # Convert submit_date to a more readable format if it exists in the dataframe
    if 'submit_date' in display_df.columns:
        display_df['submit_date'] = pd.to_datetime(display_df['submit_date']).dt.strftime('%Y-%m-%d %H:%M')
    
    # Display the table
    st.subheader("Tickets")
    st.dataframe(
        display_df[['ticket_id', 'title', 'category', 'status', 'priority', 'requester_name', 'department', 'submit_date']],
        use_container_width=True,
        hide_index=True
    )
    
    # Select a ticket to view/edit
    selected_ticket_id = st.selectbox("Select a ticket to view/edit details", 
                                   filtered_df['ticket_id'].tolist(),
                                   index=None)
    
    if selected_ticket_id:
        selected_ticket = filtered_df[filtered_df['ticket_id'] == selected_ticket_id].iloc[0]
        
        # Display ticket details
        with st.expander("Ticket Details", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Ticket ID:** {selected_ticket['ticket_id']}")
                st.write(f"**Title:** {selected_ticket['title']}")
                st.write(f"**Category:** {selected_ticket['category']}")
                st.write(f"**Status:** {selected_ticket['status']}")
            with col2:
                st.write(f"**Priority:** {selected_ticket['priority']}")
                submit_date = pd.to_datetime(selected_ticket['submit_date']).strftime('%Y-%m-%d %H:%M')
                st.write(f"**Submitted:** {submit_date}")
                st.write(f"**Requester:** {selected_ticket['requester_name']}")
                st.write(f"**Department:** {selected_ticket['department']}")
            
            st.write(f"**Description:**")
            st.write(selected_ticket['description'])
            
            # Show update history if available
            st.subheader("Update History")
            if pd.isna(selected_ticket['update_notes']) or selected_ticket['update_notes'] == "":
                st.info("No updates have been recorded for this ticket.")
            else:
                for note in selected_ticket['update_notes'].split('\n'):
                    st.write(note)
            
            # Add status update section
            st.subheader("Update Ticket Status")
            
            # Get admin users for assignment
            admin_users = utils.get_admin_users()
            admin_options = [""] + admin_users['username'].tolist() if not admin_users.empty else [""]
            
            with st.form("update_ticket_form"):
                new_status = st.selectbox(
                    "New Status", 
                    options=["Pending", "In Progress", "Completed", "Rejected"],
                    index=["Pending", "In Progress", "Completed", "Rejected"].index(selected_ticket['status']) if selected_ticket['status'] in ["Pending", "In Progress", "Completed", "Rejected"] else 0
                )
                
                assigned_to = st.selectbox(
                    "Assign To", 
                    options=admin_options,
                    index=0 if 'assigned_to' not in selected_ticket or not selected_ticket['assigned_to'] else admin_options.index(selected_ticket['assigned_to']) if selected_ticket['assigned_to'] in admin_options else 0
                )
                
                update_notes = st.text_area("Update Notes", "")
                
                update_button = st.form_submit_button("Update Ticket")
            
            if update_button:
                if not update_notes:
                    st.error("Please provide update notes before updating the ticket.")
                else:
                    success = utils.update_ticket_status(selected_ticket_id, new_status, update_notes, assigned_to)
                    if success:
                        st.success("Ticket updated successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to update ticket. Please try again.")
else:
    st.info("No tickets found matching the selected filters.")

# Sidebar actions
st.sidebar.markdown("---")
st.sidebar.header("Admin Actions")

if st.sidebar.button("User Management"):
    st.switch_page("pages/user_management.py")

if st.sidebar.button("View Reports"):
    st.switch_page("pages/reports.py")

# Refresh button
if st.sidebar.button("Refresh Data"):
    st.session_state.tickets_df = utils.load_tickets()
    st.rerun()