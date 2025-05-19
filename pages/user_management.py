import streamlit as st
import pandas as pd
import os
import sys

# Add parent directory to path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import utils

# Page configuration
st.set_page_config(
    page_title="User Management - GA Ticket System",
    page_icon="👥",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Data file paths
data_dir = 'data'
os.makedirs(data_dir, exist_ok=True)
admin_file = os.path.join(data_dir, 'admin.csv')

# Initialize admin account if it doesn't exist
if not os.path.exists(admin_file):
    utils.initialize_admin_account('admin', 'admin123')

# Authentication check
def check_authentication():
    if 'authenticated' not in st.session_state or not st.session_state.authenticated:
        st.warning("Please log in from the Admin Dashboard page first.")
        st.stop()

# User management function
def manage_users():
    st.title("👥 User Management")
    
    # Get current user
    current_username = st.session_state.username
    
    # Add User section
    st.header("Add New User")
    
    with st.form("add_user_form"):
        new_username = st.text_input("Username")
        new_password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        
        role_options = ["admin", "support"]
        new_role = st.selectbox("Role", role_options)
        
        submit_button = st.form_submit_button("Add User")
        
        if submit_button:
            if not new_username or not new_password:
                st.error("Username and password are required.")
            elif new_password != confirm_password:
                st.error("Passwords do not match.")
            else:
                if utils.add_user(new_username, new_password, new_role):
                    st.success(f"User '{new_username}' added successfully.")
                else:
                    st.error(f"Username '{new_username}' already exists.")
    
    # Manage Existing Users section
    st.header("Manage Existing Users")
    
    # Get all users
    users_df = utils.get_all_users()
    
    if len(users_df) == 0:
        st.info("No users found.")
    else:
        # Display users in a table
        st.dataframe(users_df)
        
        # Delete user section
        st.subheader("Delete User")
        
        # Get list of usernames excluding current user
        usernames = users_df['username'].tolist()
        delete_options = [u for u in usernames if u != current_username]
        
        if len(delete_options) == 0:
            st.info("No other users available to delete.")
        else:
            delete_username = st.selectbox("Select User to Delete", delete_options)
            
            if st.button("Delete User"):
                confirm = st.checkbox(f"Confirm deletion of user '{delete_username}'?")
                
                if confirm:
                    if utils.delete_user(delete_username):
                        st.success(f"User '{delete_username}' deleted successfully.")
                    else:
                        st.error("Failed to delete user. Cannot delete the only admin user.")
    
    # Change Password section
    st.header("Change Your Password")
    
    with st.form("change_password_form"):
        current_password = st.text_input("Current Password", type="password")
        new_password = st.text_input("New Password", type="password", key="new_pwd")
        confirm_new_password = st.text_input("Confirm New Password", type="password")
        
        change_button = st.form_submit_button("Change Password")
        
        if change_button:
            if not current_password or not new_password:
                st.error("All fields are required.")
            elif new_password != confirm_new_password:
                st.error("New passwords do not match.")
            else:
                # Get current user data
                user_data = utils.get_admin_user(current_username)
                
                if user_data and utils.verify_password(user_data['password'], current_password):
                    # Update password
                    admin_df = pd.read_csv(admin_file)
                    admin_df.loc[admin_df['username'] == current_username, 'password'] = utils.hash_password(new_password)
                    admin_df.to_csv(admin_file, index=False)
                    
                    st.success("Password changed successfully.")
                else:
                    st.error("Current password is incorrect.")

# Main execution
check_authentication()
manage_users()
