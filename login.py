import streamlit as st
import utils
import pandas as pd
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Login - GA Ticket Management System",
    page_icon="🎫",
    layout="wide"
)

# Initialize session state for user if it doesn't exist
if 'user' not in st.session_state:
    st.session_state.user = None

# Function to handle login
def login(username, password):
    user_data = utils.authenticate_user(username, password)
    if user_data:
        st.session_state.user = user_data
        return True
    return False

# Function to logout
def logout():
    st.session_state.user = None

# Main content
if st.session_state.user is not None:
    # User is already logged in
    st.title("You are logged in")
    st.write(f"Welcome, {st.session_state.user['full_name']}!")
    st.write(f"Role: {st.session_state.user['role'].capitalize()}")
    
    if st.button("Go to Dashboard"):
        st.switch_page("app.py")
    
    if st.button("Logout"):
        logout()
        st.rerun()
else:
    # Login form
    st.title("Login to GA Ticket Management System")
    st.markdown("Please enter your credentials to access the system")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit_button = st.form_submit_button("Login")
        
        if submit_button:
            if login(username, password):
                st.success("Login successful!")
                st.switch_page("app.py")
            else:
                st.error("Invalid username or password. Please try again.")
    
    # Link to create new account
    st.markdown("---")
    st.markdown("Don't have an account? Register as a staff user:")
    
    with st.form("register_form"):
        st.subheader("Register New Account")
        new_username = st.text_input("Username", key="reg_username")
        new_password = st.text_input("Password", type="password", key="reg_password")
        full_name = st.text_input("Full Name")
        email = st.text_input("Email")
        department = st.text_input("Department")
        
        register_button = st.form_submit_button("Register")
        
        if register_button:
            if not (new_username and new_password and full_name and email and department):
                st.error("All fields are required. Please fill in all information.")
            else:
                # New users are always registered as 'staff' role
                user_data = {
                    "username": new_username,
                    "password": new_password,
                    "full_name": full_name,
                    "email": email,
                    "role": "staff",
                    "department": department
                }
                
                success, message = utils.add_user(user_data)
                if success:
                    st.success(f"{message}. You can now login with your credentials.")
                else:
                    st.error(message)