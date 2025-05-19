import streamlit as st
import pandas as pd
import os
import sys
import uuid
from datetime import datetime

# Add parent directory to path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import utils

# Trakindo colors
TRAKINDO_ORANGE = "#f7901e"
TRAKINDO_BLACK = "#000000"
TRAKINDO_LIGHT_ORANGE = "#ffd1a3"  # lighter shade for backgrounds

# Page configuration
st.set_page_config(
    page_title="Admin Dashboard System",
    page_icon="🎫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS to style Streamlit components with Trakindo colors
st.markdown(
    f"""
    <style>
    /* Page background and font */
    .block-container {{
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        color: {TRAKINDO_BLACK};
    }}

    /* Title and headers */
    .stApp h1, .stApp h2, .stApp h3, .stApp h4 {{
        color: {TRAKINDO_ORANGE};
        font-weight: 700;
    }}

    /* Sidebar background and title */
    [data-testid="stSidebar"] {{
        background-color: {TRAKINDO_BLACK};
        color: white;
    }}
    [data-testid="stSidebar"] .css-1d391kg {{
        color: {TRAKINDO_ORANGE} !important;
        font-weight: 700;
        font-size: 1.25rem;
    }}

    /* Buttons style */
    div.stButton > button:first-child {{
        background-color: {TRAKINDO_ORANGE};
        color: {TRAKINDO_BLACK};
        font-weight: 700;
        border-radius: 5px;
        border: 2px solid {TRAKINDO_BLACK};
        padding: 8px 18px;
        transition: background-color 0.3s ease;
    }}
    div.stButton > button:first-child:hover {{
        background-color: {TRAKINDO_LIGHT_ORANGE};
        color: {TRAKINDO_BLACK};
        border-color: {TRAKINDO_ORANGE};
    }}

    /* Form inputs focus */
    input:focus, textarea:focus, select:focus {{
        border-color: {TRAKINDO_ORANGE} !important;
        box-shadow: 0 0 5px {TRAKINDO_ORANGE} !important;
        outline: none !important;
    }}

    /* Metrics */
    .stMetric > div > div:first-child {{
        color: {TRAKINDO_ORANGE} !important;
        font-weight: 700;
    }}

    /* Expander header */
    button[aria-expanded="false"], button[aria-expanded="true"] {{
        color: {TRAKINDO_ORANGE};
        font-weight: 700;
    }}

    /* Checkbox and radio buttons accent color */
    input[type="checkbox"]:checked + label::before, 
    input[type="radio"]:checked + label::before {{
        background-color: {TRAKINDO_ORANGE} !important;
        border-color: {TRAKINDO_ORANGE} !important;
    }}

    /* Error and success messages */
    .stError, .stWarning {{
        color: {TRAKINDO_ORANGE} !important;
        font-weight: 700;
    }}
    .stSuccess {{
        color: {TRAKINDO_ORANGE} !important;
        font-weight: 700;
    }}

    </style>
    """,
    unsafe_allow_html=True
)

# Data file paths
data_dir = 'data'
os.makedirs(data_dir, exist_ok=True)
tickets_file = os.path.join(data_dir, 'tickets.csv')
admin_file = os.path.join(data_dir, 'admin.csv')

# Initialize admin account if it doesn't exist
if not os.path.exists(admin_file):
    utils.initialize_admin_account('admin', 'admin123')

# Authentication function
def authenticate():
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.username = None
    
    if not st.session_state.authenticated:
        st.title("🔒 Admin Login")
        
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit_button = st.form_submit_button("Login")
            
            if submit_button:
                user = utils.get_admin_user(username)
                
                if user and utils.verify_password(user['password'], password):
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.rerun()
                else:
                    st.error("Invalid username or password")
                    
        # Display default credentials message
        st.info("Default admin credentials: username 'admin', password 'admin123'")
        # Exit function early if not authenticated
        return False
    
    return True

# Main dashboard function
def show_dashboard():
    st.title("🛠️ Admin Dashboard")
    st.write(f"Welcome, {st.session_state.username}!")
    
    # Logout button in the sidebar (styled with orange bg)
    if st.sidebar.button("Logout"):
        st.session_state.authenticated = False
        st.session_state.username = None
        st.rerun()
        
    # Get ticket statistics
    stats = utils.get_ticket_stats(tickets_file)
    
    # Dashboard metrics at the top
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total Tickets", stats['total'])
    col2.metric("Open", stats['open'])
    col3.metric("In Progress", stats['in_progress'])
    col4.metric("Resolved", stats['resolved'])
    col5.metric("Closed", stats['closed'])
    
    # Create tabs for different sections
    tab1, tab2 = st.tabs(["Manage Tickets", "Search Tickets"])
    
    # Manage Tickets Tab
    with tab1:
        st.header("Ticket Management")
        
        # Load tickets data
        tickets_df = utils.get_all_tickets(tickets_file)
        
        if len(tickets_df) == 0:
            st.info("No tickets found in the system.")
        else:
            # Status filter
            status_options = ["All"] + sorted(tickets_df['status'].unique().tolist())
            selected_status = st.selectbox("Filter by Status", status_options)
            
            # Apply filters
            filtered_df = tickets_df
            if selected_status != "All":
                filtered_df = filtered_df[filtered_df['status'] == selected_status]
            
            # Sort by created_at in descending order (newest first)
            filtered_df = filtered_df.sort_values('created_at', ascending=False)
            
            # Show results
            if len(filtered_df) == 0:
                st.info(f"No tickets with status '{selected_status}'")
            else:
                # Display tickets in a more compact format with expandable details
                for _, ticket in filtered_df.iterrows():
                    with st.expander(f"ID: {ticket['ticket_id']} - {ticket['subject']} ({ticket['status']})"):
                        # Layout ticket details in columns
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.markdown(f"**Submitted by:** {ticket['name']} ({ticket['email']})")
                            st.markdown(f"**Category:** {ticket['category']} | **Priority:** {ticket['priority']}")
                            st.markdown(f"**Created:** {ticket['created_at']} | **Updated:** {ticket['updated_at']}")
                            st.markdown("**Description:**")
                            st.write(ticket['description'])
                            
                            if ticket['resolution']:
                                st.markdown("**Resolution:**")
                                st.write(ticket['resolution'])
                        
                        with col2:
                            # Ticket update form
                            with st.form(f"update_ticket_{ticket['ticket_id']}"):
                                new_status = st.selectbox(
                                    "Status",
                                    ["Open", "In Progress", "Resolved", "Closed"],
                                    index=["Open", "In Progress", "Resolved", "Closed"].index(ticket['status'])
                                )
                                
                                new_priority = st.selectbox(
                                    "Priority",
                                    ["Low", "Medium", "High", "Critical"],
                                    index=["Low", "Medium", "High", "Critical"].index(ticket['priority'])
                                )
                                
                                resolution = st.text_area(
                                    "Resolution/Notes",
                                    value=ticket['resolution'],
                                    height=100
                                )
                                
                                update_button = st.form_submit_button("Update Ticket")
                                
                                if update_button:
                                    updates = {
                                        'status': new_status,
                                        'priority': new_priority,
                                        'resolution': resolution
                                    }
                                    
                                    if utils.update_ticket(ticket['ticket_id'], updates, tickets_file):
                                        st.success("Ticket updated successfully!")
                                        st.rerun()
                                    else:
                                        st.error("Failed to update ticket.")
                            
                            # Delete button outside the form
                            if st.button(f"Delete Ticket #{ticket['ticket_id']}", key=f"delete_{ticket['ticket_id']}"):
                                confirm = st.checkbox(f"Confirm deletion of ticket #{ticket['ticket_id']}?", key=f"confirm_{ticket['ticket_id']}")
                                
                                if confirm:
                                    if utils.delete_ticket(ticket['ticket_id'], tickets_file):
                                        st.success("Ticket deleted successfully!")
                                        st.rerun()
                                    else:
                                        st.error("Failed to delete ticket.")
    
    # Search Tickets Tab
    with tab2:
        st.header("Search Tickets")
        
        search_term = st.text_input("Search by ID, Name, Email, or Subject")
        
        if search_term:
            tickets_df = utils.get_all_tickets(tickets_file)
            
            if len(tickets_df) > 0:
                # Case-insensitive search across multiple columns
                mask = (
                    tickets_df['ticket_id'].str.contains(search_term, case=False, na=False) |
                    tickets_df['name'].str.contains(search_term, case=False, na=False) |
                    tickets_df['email'].str.contains(search_term, case=False, na=False) |
                    tickets_df['subject'].str.contains(search_term, case=False, na=False) |
                    tickets_df['description'].str.contains(search_term, case=False, na=False)
                )
                search_results = tickets_df[mask].sort_values('created_at', ascending=False)
                
                if len(search_results) > 0:
                    st.success(f"Found {len(search_results)} matching tickets.")
                    
                    # Display search results
                    for _, ticket in search_results.iterrows():
                        with st.expander(f"ID: {ticket['ticket_id']} - {ticket['subject']} ({ticket['status']})"):
                            col1, col2 = st.columns([3, 1])
                            
                            with col1:
                                st.markdown(f"**Submitted by:** {ticket['name']} ({ticket['email']})")
                                st.markdown(f"**Category:** {ticket['category']} | **Priority:** {ticket['priority']}")
                                st.markdown(f"**Created:** {ticket['created_at']} | **Updated:** {ticket['updated_at']}")
                                st.markdown("**Description:**")
                                st.write(ticket['description'])
                                
                                if ticket['resolution']:
                                    st.markdown("**Resolution:**")
                                    st.write(ticket['resolution'])
                            
                            with col2:
                                # Update form (same as in tab1)
                                with st.form(f"search_update_{ticket['ticket_id']}"):
                                    new_status = st.selectbox(
                                        "Status",
                                        ["Open", "In Progress", "Resolved", "Closed"],
                                        index=["Open", "In Progress", "Resolved", "Closed"].index(ticket['status']),
                                        key=f"search_status_{ticket['ticket_id']}"
                                    )
                                    
                                    new_priority = st.selectbox(
                                        "Priority",
                                        ["Low", "Medium", "High", "Critical"],
                                        index=["Low", "Medium", "High", "Critical"].index(ticket['priority']),
                                        key=f"search_priority_{ticket['ticket_id']}"
                                    )
                                    
                                    resolution = st.text_area(
                                        "Resolution/Notes",
                                        value=ticket['resolution'],
                                        height=100,
                                        key=f"search_resolution_{ticket['ticket_id']}"
                                    )
                                    
                                    update_button = st.form_submit_button("Update Ticket")
                                    
                                    if update_button:
                                        updates = {
                                            'status': new_status,
                                            'priority': new_priority,
                                            'resolution': resolution
                                        }
                                        
                                        if utils.update_ticket(ticket['ticket_id'], updates, tickets_file):
                                            st.success("Ticket updated successfully!")
                                            st.rerun()
                                        else:
                                            st.error("Failed to update ticket.")
                else:
                    st.warning(f"No tickets found matching '{search_term}'.")
            else:
                st.info("No tickets found in the system.")

# Main execution
if authenticate():
    show_dashboard()
