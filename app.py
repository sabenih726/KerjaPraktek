import streamlit as st
import pandas as pd
import os
import uuid
from datetime import datetime
import utils
import pytz

# Page configuration
st.set_page_config(
    page_title="Trakindo Facility Maintenance",
    page_icon="🎫",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Load and apply custom CSS
with open('streamlit/style.css') as f:
    css = f.read()

hide_sidebar_style = """
<style>
    div[data-testid="stSidebarNav"] {display: none !important;}
</style>
"""

st.markdown(f"""
{hide_sidebar_style}
<style>
{css}
</style>
""", unsafe_allow_html=True)

# Ensure data directory exists
os.makedirs('data', exist_ok=True)
data_file = 'data/tickets.csv'

# Create an empty tickets file if not exists
if not os.path.exists(data_file):
    initial_df = pd.DataFrame(columns=[
        'ticket_id', 'created_at', 'updated_at', 'name', 'email',
        'subject', 'category', 'priority', 'status', 'description', 'resolution'
    ])
    initial_df.to_csv(data_file, index=False)

# Trakindo CAT branding with consistent colors
st.markdown("""
<div style="text-align: center; padding: 1.5rem 0; margin-bottom: 2rem;">
    <div style="margin-bottom: 1rem; display: flex; justify-content: center; align-items: center;">
        <div style="background-color: #FFBB00; color: #000000; padding: 5px 15px; font-weight: 700; font-size: 1.8rem; border-radius: 4px;">
            Trakindo
        </div>
        <div style="background-color: #000000; color: white; padding: 5px 15px; font-weight: 700; font-size: 1.8rem; border-radius: 4px; margin-left: 5px;">
            CAT
        </div>
    </div>
    <h1 style="color: #000000; font-size: 2.5rem; font-weight: 700; margin-bottom: 0.5rem;">
        Trakindo Facility Maintenance
    </h1>
    <p style="color: #6b7280; font-size: 1rem;">Report and track your requirements</p>
</div>
""", unsafe_allow_html=True)

# Tabs: Submit Ticket and Track Ticket
tab1, tab2 = st.tabs(["📝 Submit Ticket", "🔍 Track Ticket"])

# Submit Ticket Tab
with tab1:
    st.markdown("""
    <h2 style="color: #111827; font-weight: 600; margin-bottom: 1rem; padding-bottom: 0.5rem; border-bottom: 2px solid #f7901e;">
        📝 Submit a New Ticket
    </h2>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="background-color: white; border-radius: 0.5rem; padding: 1rem; margin-bottom: 1rem; box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24); border-left: 5px solid #f7901e;">
        <p style="color: #6b7280; font-size: 0.875rem;">
            Please fill in the form below to report your requirements. All fields marked with * are required.
        </p>
    </div>
    """, unsafe_allow_html=True)

    with st.form("ticket_submission_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Full Name *", placeholder="Enter your full name")
            email = st.text_input("Email Address *", placeholder="Enter your email")
            category = st.selectbox(
                "Ticket Category *",
                ["General Inquiry", "Technical Support", "Billing Issue", "Feature Request", "Bug Report", "Other"]
            )
        with col2:
            subject = st.text_input("Subject *", placeholder="Brief summary of your issue")
            priority = st.selectbox("Priority Level *", ["Low", "Medium", "High", "Critical"],
                                    help="Choose how urgent your issue is")

        description = st.text_area(
            "Detailed Description *",
            placeholder="Provide detailed information about the issue, including steps to reproduce if applicable",
            height=150
        )

        submit_button = st.form_submit_button(
            "📤 Submit Ticket"
        )

        if submit_button:
            if not name or not email or not subject or not description:
                st.error("Please fill out all required fields.")
            elif not utils.is_valid_email(email):
                st.error("Please enter a valid email address.")
            else:
                ticket_id = str(uuid.uuid4())[:8].upper()
                tz = pytz.timezone("Asia/Jakarta")
                timestamp = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
                new_ticket = {
                    'ticket_id': ticket_id,
                    'created_at': timestamp,
                    'updated_at': timestamp,
                    'name': name,
                    'email': email,
                    'subject': subject,
                    'category': category,
                    'priority': priority,
                    'status': "Open",
                    'description': description,
                    'resolution': ""
                }
                utils.add_ticket(new_ticket, data_file)
                st.success("Your ticket has been submitted!")
                st.info(f"Your Ticket ID: **{ticket_id}**")
                st.info("Please save this ID to track your ticket status.")

# Track Ticket Tab
with tab2:
    st.markdown("""
    <h2 style="color: #111827; font-weight: 600; margin-bottom: 1rem; padding-bottom: 0.5rem; border-bottom: 2px solid #f7901e;">
        🔍 Track Your Ticket
    </h2>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="background-color: white; border-radius: 0.5rem; padding: 1rem; margin-bottom: 1.5rem; 
                box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24); border-left: 5px solid #f7901e;">
        <p style="color: #6b7280; font-size: 0.875rem;">
            Enter your Ticket ID below to check the status of your ticket request.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([3, 1])
    with col1:
        ticket_id = st.text_input("Enter Your Ticket ID", key="track_ticket_id", placeholder="e.g. A1B2C3D4").strip().upper()
    with col2:
        track_button = st.button("🔍 Track Ticket")

    if track_button:
        if not ticket_id:
            st.error("Please enter a ticket ID.")
        else:
            ticket_info = utils.get_ticket_by_id(ticket_id, data_file)
            if ticket_info is not None:
                st.success(f"Ticket found: {ticket_id}")

                status = ticket_info['status']
                status_color = (
                    "#10B981" if status == "Open" else
                    "#F59E0B" if status == "In Progress" else
                    "#3B82F6" if status == "Closed" else
                    "#6B7280"
                )
                status_icon = (
                    "🟢" if status == "Open" else
                    "🟠" if status == "In Progress" else
                    "🔵" if status == "Closed" else
                    "⚫"
                )

                st.markdown(f"""
                <div style="background-color: white; border-radius: 0.5rem; padding: 1.5rem; margin-bottom: 1.5rem; 
                            box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24); border-left: 5px solid {status_color};">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                        <h3 style="margin: 0; color: #111827;">Ticket #{ticket_info['ticket_id']}</h3>
                        <span style="font-size: 1.25rem; background-color: {status_color}30; color: {status_color}; padding: 0.25rem 0.75rem; border-radius: 9999px; font-weight: 500;">
                            {status_icon} {status}
                        </span>
                    </div>
                    <h3 style="margin-top: 0; margin-bottom: 0.5rem; color: #111827;">{ticket_info['subject']}</h3>
                    <p style="color: #6B7280; margin-bottom: 0.25rem;">Submitted by {ticket_info['name']} on {ticket_info['created_at']}</p>
                    <p style="color: #6B7280; margin-bottom: 0.25rem;">Category: {ticket_info['category']} | Priority: {ticket_info['priority']}</p>
                    <p style="color: #6B7280; margin-bottom: 0;">Last Updated: {ticket_info['updated_at']}</p>
                </div>
                """, unsafe_allow_html=True)

                details_tab, description_tab, resolution_tab = st.tabs(["📋 Details", "📝 Description", "✅ Resolution"])

                with details_tab:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("### Ticket Information")
                        st.markdown(f"**ID:** {ticket_info['ticket_id']}")
                        st.markdown(f"**Subject:** {ticket_info['subject']}")
                        st.markdown(f"**Category:** {ticket_info['category']}")
                        st.markdown(f"**Submitted By:** {ticket_info['name']}")
                    with col2:
                        st.markdown("### Status Details")
                        st.markdown(f"**Current Status:** {ticket_info['status']}")
                        st.markdown(f"**Priority Level:** {ticket_info['priority']}")
                        st.markdown(f"**Created At:** {ticket_info['created_at']}")
                        st.markdown(f"**Updated At:** {ticket_info['updated_at']}")

                with description_tab:
                    st.markdown(f"**Description:**\n\n{ticket_info['description']}")

                with resolution_tab:
                    resolution_text = ticket_info['resolution'] if ticket_info['resolution'] else "_No resolution provided yet._"
                    st.markdown(f"**Resolution:**\n\n{resolution_text}")

            else:
                st.error(f"No ticket found with ID: {ticket_id}")

# Footer
st.markdown("""
<footer style="margin-top: 3rem; text-align: center; font-size: 0.9rem; color: #FFBB00;">
    Powered by Trakindo Team &bull; 2025 &copy;
</footer>
""", unsafe_allow_html=True)
