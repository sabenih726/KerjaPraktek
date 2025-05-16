import streamlit as st
import pandas as pd
import os
from datetime import datetime
import utils

# Page configuration - Set sidebar to auto by default
st.set_page_config(
    page_title="Tiket Antri Faciltiy",
    page_icon="🎫",
    layout="wide",
    initial_sidebar_state="auto"
)

# Hide sidebar for regular users
hide_sidebar_css = """
<style>
    [data-testid="collapsedControl"] {display: none}
    section[data-testid="stSidebar"] {display: none}
    .stApp {
        margin-left: auto !important;
        margin-right: auto !important;
        max-width: 1200px !important;
    }
</style>
"""

if 'tickets_df' not in st.session_state:
    st.session_state.tickets_df = utils.load_tickets()

if 'user' not in st.session_state:
    st.session_state.user = None
    st.markdown(hide_sidebar_css, unsafe_allow_html=True)
    
tab1, tab2 = st.tabs(["Submit Ticket", "Admin Login"])

with tab1:
    if st.session_state.user is None:
        st.markdown(hide_sidebar_css, unsafe_allow_html=True)
    
    # --- BAGIAN MODIFIKASI: Tambah logo dan judul sejajar ---
    col_logo, col_title = st.columns([1, 8])
    with col_logo:
        # Ganti "logo.png" dengan path file logo kamu
        st.image("assets/logo trakindo.png", width=150)
    with col_title:
        st.title("Ticket Faciltiy")
    
    st.markdown("Submit a service request to the Facility")
    
    with st.form("ticket_submission_form"):
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
            requester_name = st.text_input("Your Name *", help="Name of the person requesting service")
            requester_email = st.text_input("Your Email *", help="Email address for follow-up communications")
            department = st.text_input("Department *", help="Your department or division")
        
        description = st.text_area(
            "Description *", 
            height=150,
            help="Provide detailed information about your request"
        )
        
        submit_button = st.form_submit_button("Submit Ticket")

    if submit_button:
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
            
            ticket_id = utils.save_ticket(ticket_data)
            
            st.success(f"Ticket submitted successfully! Your ticket ID is {ticket_id}")
            
            with st.expander("Ticket Details", expanded=True):
                st.write(f"**Ticket ID:** {ticket_id}")
                st.write(f"**Title:** {title}")
                st.write(f"**Category:** {category}")
                st.write(f"**Priority:** {priority}")
                st.write(f"**Status:** Pending")
                st.write(f"**Submitted by:** {requester_name}, {department}")
                st.write(f"**Description:**")
                st.write(description)
    
    st.markdown("---")
    st.subheader("Track Your Ticket")
    ticket_id_search = st.text_input("Enter your ticket ID to check status")
    if st.button("Check Status", key="check_status_btn") and ticket_id_search:
        ticket = utils.get_ticket_by_id(ticket_id_search)
        if ticket:
            with st.expander("Ticket Details", expanded=True):
                st.write(f"**Ticket ID:** {ticket['ticket_id']}")
                st.write(f"**Title:** {ticket['title']}")
                st.write(f"**Category:** {ticket['category']}")
                st.write(f"**Status:** {ticket['status']}")
                st.write(f"**Priority:** {ticket['priority']}")
                submit_date = pd.to_datetime(ticket['submit_date']).strftime('%Y-%m-%d %H:%M')
                st.write(f"**Submitted:** {submit_date}")
                st.write(f"**Description:**")
                st.write(ticket['description'])
                if 'update_notes' in ticket and ticket['update_notes'] and not pd.isna(ticket['update_notes']):
                    st.write("**Update History:**")
                    for note in ticket['update_notes'].split('\n'):
                        st.write(note)
        else:
            st.error(f"No ticket found with ID: {ticket_id_search}")
    
with tab2:
    # Admin login form
    if st.session_state.user is None:
        # Hide sidebar for login screen too
        st.markdown(hide_sidebar_css, unsafe_allow_html=True)
        
        st.title("Admin Login")
        st.markdown("Please enter your credentials to access the admin dashboard")
        
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit_button = st.form_submit_button("Login")
            
            if submit_button:
                user_data = utils.authenticate_user(username, password)
                if user_data:
                    st.session_state.user = user_data
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid username or password. Please try again.")
    else:
        # Show sidebar for logged in users
        st.success(f"Logged in as {st.session_state.user['full_name']} ({st.session_state.user['role']})")
        if st.button("Go to Admin Dashboard", key="admin_dashboard_btn"):
            # Continue to admin dashboard
            st.switch_page("pages/admin_dashboard.py")
        
        if st.button("Logout", key="logout_admin_tab_btn"):
            st.session_state.user = None
            st.rerun()
            
# Stop execution here for regular app.py if not logged in
if st.session_state.user is None:
    st.stop()

# Remove the sidebar hiding CSS for logged-in users by adding empty markdown
st.sidebar.markdown("", unsafe_allow_html=True)

# Title and description
st.title("General Affairs Ticket Management System")
st.markdown(f"Track and manage service requests for the General Affairs division | Logged in as: {st.session_state.user['full_name']} ({st.session_state.user['role'].capitalize()})")

# Main dashboard
st.header("Ticket Dashboard")

# Sidebar user info
st.sidebar.header("User Information")
st.sidebar.write(f"**Name:** {st.session_state.user['full_name']}")
st.sidebar.write(f"**Role:** {st.session_state.user['role'].capitalize()}")
st.sidebar.write(f"**Department:** {st.session_state.user['department']}")

if st.sidebar.button("Logout", key="logout_sidebar_btn"):
    st.session_state.user = None
    st.rerun()

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
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Tickets", len(st.session_state.tickets_df))
    
with col2:
    pending_count = len(st.session_state.tickets_df[st.session_state.tickets_df['status'] == 'Pending'])
    st.metric("Pending Tickets", pending_count)
    
with col3:
    completed_count = len(st.session_state.tickets_df[st.session_state.tickets_df['status'] == 'Completed'])
    st.metric("Completed Tickets", completed_count)

# Display tickets table
if not filtered_df.empty:
    # Prepare display dataframe
    display_df = filtered_df.copy()
    # Convert submit_date to a more readable format if it exists in the dataframe
    if 'submit_date' in display_df.columns:
        display_df['submit_date'] = pd.to_datetime(display_df['submit_date']).dt.strftime('%Y-%m-%d %H:%M')
    
    # Display the table with action buttons
    st.dataframe(
        display_df[['ticket_id', 'title', 'category', 'status', 'priority', 'submit_date']],
        use_container_width=True,
        hide_index=True
    )
    
    # Select a ticket to view/edit
    selected_ticket_id = st.selectbox("Select a ticket to view details", 
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
            
            # Add status update section
            st.subheader("Update Ticket Status")
            
            new_status = st.selectbox(
                "New Status", 
                options=["Pending", "In Progress", "Completed", "Rejected"],
                index=["Pending", "In Progress", "Completed", "Rejected"].index(selected_ticket['status']) if selected_ticket['status'] in ["Pending", "In Progress", "Completed", "Rejected"] else 0
            )
            
            update_notes = st.text_area("Update Notes", "")
            
            if st.button("Update Ticket", key="update_ticket_btn"):
                utils.update_ticket_status(selected_ticket_id, new_status, update_notes)
                st.success("Ticket updated successfully!")
                st.rerun()
else:
    st.info("No tickets found matching the selected filters.")

# Link to create a new ticket
st.sidebar.markdown("---")
st.sidebar.header("Actions")
if st.sidebar.button("Create New Ticket", key="create_ticket_btn"):
    st.switch_page("pages/submit_ticket.py")

if st.sidebar.button("View Reports", key="view_reports_btn"):
    st.switch_page("pages/reports.py")

# Admin-only actions
if st.session_state.user['role'] == 'admin':
    if st.sidebar.button("User Management", key="user_management_btn"):
        st.switch_page("pages/user_management.py")

# Refresh button
if st.sidebar.button("Refresh Data", key="refresh_data_btn"):
    st.session_state.tickets_df = utils.load_tickets()
    st.rerun()
