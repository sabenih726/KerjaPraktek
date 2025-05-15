import pandas as pd
import os
from datetime import datetime
import streamlit as st
import uuid
import hashlib

# File paths for data
TICKETS_FILE = "data/tickets.csv"
USERS_FILE = "data/users.csv"

def generate_ticket_id():
    """Generate a unique ticket ID"""
    return f"TICK-{str(uuid.uuid4())[:8].upper()}"

def load_tickets():
    """Load tickets from CSV file, creating the file if it doesn't exist"""
    if not os.path.exists("data"):
        os.makedirs("data")
    
    columns = [
        "ticket_id", "title", "description", "category", "priority", 
        "status", "requester_name", "requester_email", "department", 
        "submit_date", "updated_date", "update_notes", "assigned_to"
    ]
    
    if not os.path.exists(TICKETS_FILE):
        # Create empty dataframe with the columns
        df = pd.DataFrame({col: [] for col in columns})
        
        # Save the empty dataframe to CSV
        df.to_csv(TICKETS_FILE, index=False)
        return df
    
    try:
        # Load existing tickets
        return pd.read_csv(TICKETS_FILE)
    except Exception as e:
        st.error(f"Error loading ticket data: {e}")
        # Return empty dataframe with columns
        return pd.DataFrame({col: [] for col in columns})

def load_users():
    """Load users from CSV file, creating default admin if file doesn't exist"""
    if not os.path.exists("data"):
        os.makedirs("data")
    
    columns = [
        "username", "password", "full_name", "email", "role", "department"
    ]
    
    if not os.path.exists(USERS_FILE):
        # Create a default admin user
        default_admin = [{
            "username": "admin",
            "password": "admin123",  # In production, use hashed passwords
            "full_name": "Admin User",
            "email": "admin@example.com",
            "role": "admin",
            "department": "General Affairs"
        }]
        
        # Create dataframe with default admin
        df = pd.DataFrame(default_admin)
        
        # Save the dataframe to CSV
        df.to_csv(USERS_FILE, index=False)
        return df
    
    try:
        # Load existing users
        return pd.read_csv(USERS_FILE)
    except Exception as e:
        st.error(f"Error loading user data: {e}")
        # Return empty dataframe with columns
        return pd.DataFrame({col: [] for col in columns})

def save_ticket(ticket_data):
    """Save a new ticket to the CSV file"""
    # Load existing tickets
    tickets_df = load_tickets()
    
    # Generate ticket ID if not provided
    if 'ticket_id' not in ticket_data or not ticket_data['ticket_id']:
        ticket_data['ticket_id'] = generate_ticket_id()
    
    # Add submission timestamp
    ticket_data['submit_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    ticket_data['updated_date'] = ticket_data['submit_date']
    
    # Set initial status if not provided
    if 'status' not in ticket_data or not ticket_data['status']:
        ticket_data['status'] = 'Pending'
    
    # Create a dataframe for the new ticket
    new_ticket_df = pd.DataFrame([ticket_data])
    
    # Append to existing tickets
    tickets_df = pd.concat([tickets_df, new_ticket_df], ignore_index=True)
    
    # Save all tickets back to file
    tickets_df.to_csv(TICKETS_FILE, index=False)
    
    # Update session state
    st.session_state.tickets_df = tickets_df
    
    return ticket_data['ticket_id']

def update_ticket_status(ticket_id, new_status, update_notes="", assigned_to=None):
    """Update the status, assigned admin, and add notes to an existing ticket"""
    # Load existing tickets
    tickets_df = load_tickets()
    
    # Find the ticket by ID
    if ticket_id in tickets_df['ticket_id'].values:
        # Get index of the ticket
        idx = tickets_df[tickets_df['ticket_id'] == ticket_id].index[0]
        
        # Update the status and timestamp
        tickets_df.at[idx, 'status'] = new_status
        tickets_df.at[idx, 'updated_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Update assigned admin if provided
        if assigned_to:
            tickets_df.at[idx, 'assigned_to'] = assigned_to
            update_prefix = f"Status changed to {new_status} and assigned to {assigned_to}"
        else:
            update_prefix = f"Status changed to {new_status}"
        
        # Add update notes if provided
        if update_notes:
            current_notes = tickets_df.at[idx, 'update_notes']
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            if pd.isna(current_notes) or current_notes == "":
                new_notes = f"{timestamp} - {update_prefix}: {update_notes}"
            else:
                new_notes = f"{current_notes}\n{timestamp} - {update_prefix}: {update_notes}"
            
            tickets_df.at[idx, 'update_notes'] = new_notes
        
        # Save the updated dataframe
        tickets_df.to_csv(TICKETS_FILE, index=False)
        
        # Update session state
        st.session_state.tickets_df = tickets_df
        
        return True
    
    return False

def filter_tickets(df, category='All', status='All', search_term=''):
    """Filter tickets based on category, status and search term"""
    filtered_df = df.copy()
    
    # Filter by category if not 'All'
    if category != 'All':
        filtered_df = filtered_df[filtered_df['category'] == category]
    
    # Filter by status if not 'All'
    if status != 'All':
        filtered_df = filtered_df[filtered_df['status'] == status]
    
    # Filter by search term if provided
    if search_term:
        # Convert all searchable columns to string
        title_search = filtered_df['title'].astype(str).str.contains(search_term, case=False)
        desc_search = filtered_df['description'].astype(str).str.contains(search_term, case=False)
        req_search = filtered_df['requester_name'].astype(str).str.contains(search_term, case=False)
        
        # Combine search results
        filtered_df = filtered_df[title_search | desc_search | req_search]
    
    return filtered_df

def get_ticket_categories():
    """Return a list of predefined ticket categories"""
    return [
        "Facility Maintenance",
        "IT Support",
        "Office Supplies",
        "Meeting Room Booking",
        "Security",
        "Cleaning Services",
        "Transportation",
        "Catering",
        "Other"
    ]

def get_ticket_by_id(ticket_id):
    """Get a specific ticket by ID"""
    tickets_df = load_tickets()
    if ticket_id in tickets_df['ticket_id'].values:
        return tickets_df[tickets_df['ticket_id'] == ticket_id].iloc[0].to_dict()
    return None

def authenticate_user(username, password):
    """Authenticate a user with username and password"""
    users_df = load_users()
    
    # Check if user exists
    if username in users_df['username'].values:
        user_row = users_df[users_df['username'] == username].iloc[0]
        
        # Check password (in production, use hashed passwords)
        if user_row['password'] == password:
            # Return user data as dictionary without password
            user_data = user_row.to_dict()
            return user_data
    
    return None

def add_user(user_data):
    """Add a new user to the system"""
    users_df = load_users()
    
    # Check if username already exists
    if user_data['username'] in users_df['username'].values:
        return False, "Username already exists"
    
    # Create a dataframe for the new user
    new_user_df = pd.DataFrame([user_data])
    
    # Append to existing users
    users_df = pd.concat([users_df, new_user_df], ignore_index=True)
    
    # Save all users back to file
    users_df.to_csv(USERS_FILE, index=False)
    
    return True, "User added successfully"

def get_user_list():
    """Get list of all users"""
    users_df = load_users()
    # Return copy without password column for security
    return users_df.drop(columns=['password']).copy() if 'password' in users_df.columns else users_df.copy()

def get_admin_users():
    """Get list of admin users for ticket assignment"""
    users_df = load_users()
    admin_users = users_df[users_df['role'] == 'admin']
    return admin_users[['username', 'full_name']].copy() if not admin_users.empty else pd.DataFrame(columns=['username', 'full_name'])
