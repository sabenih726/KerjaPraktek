import pandas as pd
import re
import hashlib
import os
from datetime import datetime

def add_ticket(ticket_data, file_path):
    """
    Add a new ticket to the CSV file
    """
    # Read existing file
    if os.path.exists(file_path):
        tickets_df = pd.read_csv(file_path)
    else:
        # Create a new DataFrame with appropriate columns if file doesn't exist
        tickets_df = pd.DataFrame(columns=[
            'ticket_id', 'created_at', 'updated_at', 'name', 'email', 
            'subject', 'category', 'priority', 'status', 'description', 'resolution'
        ])
    
    # Append new ticket
    new_ticket_df = pd.DataFrame([ticket_data])
    tickets_df = pd.concat([tickets_df, new_ticket_df], ignore_index=True)
    
    # Save to CSV
    tickets_df.to_csv(file_path, index=False)

def get_ticket_by_id(ticket_id, file_path):
    """
    Retrieve a ticket by its ID
    """
    if not os.path.exists(file_path):
        return None
    
    tickets_df = pd.read_csv(file_path)
    ticket = tickets_df[tickets_df['ticket_id'] == ticket_id]
    
    if len(ticket) == 0:
        return None
    
    return ticket.iloc[0].to_dict()

def update_ticket(ticket_id, updated_data, file_path):
    """
    Update an existing ticket
    """
    if not os.path.exists(file_path):
        return False
    
    tickets_df = pd.read_csv(file_path)
    
    # Find ticket by ID
    mask = tickets_df['ticket_id'] == ticket_id
    if not mask.any():
        return False
    
    # Update timestamp
    updated_data['updated_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Update fields
    for key, value in updated_data.items():
        if key in tickets_df.columns:
            tickets_df.loc[mask, key] = value
    
    # Save to CSV
    tickets_df.to_csv(file_path, index=False)
    return True

def delete_ticket(ticket_id, file_path):
    """
    Delete a ticket by ID
    """
    if not os.path.exists(file_path):
        return False
    
    tickets_df = pd.read_csv(file_path)
    
    # Find and remove ticket
    original_count = len(tickets_df)
    tickets_df = tickets_df[tickets_df['ticket_id'] != ticket_id]
    
    if len(tickets_df) == original_count:
        return False  # No ticket was removed
    
    # Save to CSV
    tickets_df.to_csv(file_path, index=False)
    return True

def get_all_tickets(file_path):
    """
    Get all tickets as a DataFrame
    """
    if not os.path.exists(file_path):
        # Return empty DataFrame with correct columns
        return pd.DataFrame(columns=[
            'ticket_id', 'created_at', 'updated_at', 'name', 'email', 
            'subject', 'category', 'priority', 'status', 'description', 'resolution'
        ])
    
    return pd.read_csv(file_path)

def is_valid_email(email):
    """
    Validate email format
    """
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None

def hash_password(password):
    """
    Create a SHA-256 hash of the password for basic security
    """
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(hashed_password, input_password):
    """
    Verify a password against its hash
    """
    return hashed_password == hash_password(input_password)

def get_ticket_stats(file_path):
    """
    Get ticket statistics for dashboard
    """
    if not os.path.exists(file_path):
        return {
            'total': 0,
            'open': 0,
            'in_progress': 0,
            'resolved': 0,
            'closed': 0,
            'by_category': {},
            'by_priority': {}
        }
    
    tickets_df = pd.read_csv(file_path)
    
    # Calculate stats
    total = len(tickets_df)
    
    if total == 0:
        return {
            'total': 0,
            'open': 0,
            'in_progress': 0,
            'resolved': 0,
            'closed': 0,
            'by_category': {},
            'by_priority': {}
        }
    
    open_tickets = len(tickets_df[tickets_df['status'] == 'Open'])
    in_progress = len(tickets_df[tickets_df['status'] == 'In Progress'])
    resolved = len(tickets_df[tickets_df['status'] == 'Resolved'])
    closed = len(tickets_df[tickets_df['status'] == 'Closed'])
    
    # By category and priority
    by_category = tickets_df['category'].value_counts().to_dict()
    by_priority = tickets_df['priority'].value_counts().to_dict()
    
    return {
        'total': total,
        'open': open_tickets,
        'in_progress': in_progress,
        'resolved': resolved,
        'closed': closed,
        'by_category': by_category,
        'by_priority': by_priority
    }

def initialize_admin_account(username, password):
    """
    Initialize admin account data
    """
    os.makedirs('data', exist_ok=True)
    admin_file = 'data/admin.csv'
    
    # Create admin file if it doesn't exist
    if not os.path.exists(admin_file):
        admin_df = pd.DataFrame(columns=['username', 'password', 'role'])
        admin_df = pd.concat([
            admin_df, 
            pd.DataFrame([{
                'username': username,
                'password': hash_password(password),
                'role': 'admin'
            }])
        ], ignore_index=True)
        admin_df.to_csv(admin_file, index=False)
        return True
    
    return False

def get_admin_user(username):
    """
    Get admin user details
    """
    admin_file = 'data/admin.csv'
    
    if not os.path.exists(admin_file):
        # Initialize default admin account if none exists
        initialize_admin_account('admin', 'admin123')
    
    admin_df = pd.read_csv(admin_file)
    user = admin_df[admin_df['username'] == username]
    
    if len(user) == 0:
        return None
    
    return user.iloc[0].to_dict()

def add_user(username, password, role):
    """
    Add a new user to the admin.csv file
    """
    os.makedirs('data', exist_ok=True)
    admin_file = 'data/admin.csv'
    
    if os.path.exists(admin_file):
        admin_df = pd.read_csv(admin_file)
        
        # Check if username already exists
        if username in admin_df['username'].values:
            return False
    else:
        admin_df = pd.DataFrame(columns=['username', 'password', 'role'])
    
    # Add new user
    new_user = pd.DataFrame([{
        'username': username,
        'password': hash_password(password),
        'role': role
    }])
    
    admin_df = pd.concat([admin_df, new_user], ignore_index=True)
    admin_df.to_csv(admin_file, index=False)
    
    return True

def get_all_users():
    """
    Get all admin users
    """
    admin_file = 'data/admin.csv'
    
    if not os.path.exists(admin_file):
        # Initialize default admin account if none exists
        initialize_admin_account('admin', 'admin123')
    
    admin_df = pd.read_csv(admin_file)
    # For security, don't return password hashes
    return admin_df[['username', 'role']]

def delete_user(username):
    """
    Delete a user by username
    """
    admin_file = 'data/admin.csv'
    
    if not os.path.exists(admin_file):
        return False
    
    admin_df = pd.read_csv(admin_file)
    
    # Prevent deleting all admin users
    if len(admin_df[admin_df['role'] == 'admin']) <= 1 and username in admin_df[admin_df['role'] == 'admin']['username'].values:
        return False
    
    # Find and remove user
    original_count = len(admin_df)
    admin_df = admin_df[admin_df['username'] != username]
    
    if len(admin_df) == original_count:
        return False  # No user was removed
    
    # Save to CSV
    admin_df.to_csv(admin_file, index=False)
    return True
