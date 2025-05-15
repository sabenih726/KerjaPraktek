import streamlit as st
import pandas as pd
import sys
import os

# Add parent directory to path to import utils
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import utils

# Page configuration
st.set_page_config(
    page_title="User Management - GA Ticket Management System",
    page_icon="👥",
    layout="wide"
)

# Require login and admin access
if 'user' not in st.session_state or st.session_state.user is None:
    st.warning("Please login to access this page")
    st.button("Go to Login", on_click=lambda: st.switch_page("app.py"))
    st.stop()
elif st.session_state.user['role'] != 'admin':
    st.error("You don't have permission to access this page. Admin access required.")
    st.button("Go to Dashboard", on_click=lambda: st.switch_page("app.py"))
    st.stop()

# Title
st.title("User Management")
st.markdown("Manage system users")

# Display user list
users_df = utils.get_user_list()

if not users_df.empty:
    st.subheader("Current Users")
    st.dataframe(users_df, use_container_width=True, hide_index=True)
else:
    st.info("No users found in the system.")

# Form to add new user
st.subheader("Add New User")

with st.form("add_user_form"):
    new_username = st.text_input("Username", key="new_username")
    new_password = st.text_input("Password", type="password", key="new_password")
    full_name = st.text_input("Full Name")
    email = st.text_input("Email")
    role = st.selectbox("Role", options=["admin", "staff"])
    department = st.text_input("Department")
    
    submit_button = st.form_submit_button("Add User")
    
    if submit_button:
        if not (new_username and new_password and full_name and email and department):
            st.error("All fields are required. Please fill in all information.")
        else:
            user_data = {
                "username": new_username,
                "password": new_password,
                "full_name": full_name,
                "email": email,
                "role": role,
                "department": department
            }
            
            success, message = utils.add_user(user_data)
            if success:
                st.success(message)
                st.rerun()
            else:
                st.error(message)

# Button to return to dashboard
if st.button("Return to Dashboard"):
    st.switch_page("app.py")