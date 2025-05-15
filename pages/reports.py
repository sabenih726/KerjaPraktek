import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path to import utils
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import utils

# Page configuration
st.set_page_config(
    page_title="Reports - GA Ticket Management System",
    page_icon="📊",
    layout="wide"
)

# Check if user is logged in
if 'user' not in st.session_state or st.session_state.user is None:
    st.switch_page("app.py")

# Title
st.title("Ticket Reports & Analytics")
st.markdown("View statistics and reports about ticket activities")

# Check if user has permission for reports
if st.session_state.user['role'] != 'admin':
    st.warning("Reports are only available to administrators.")
    if st.button("Return to Dashboard"):
        st.switch_page("app.py")
    st.stop()

# Load tickets data
if 'tickets_df' not in st.session_state:
    st.session_state.tickets_df = utils.load_tickets()

tickets_df = st.session_state.tickets_df.copy()

# Check if we have data to work with
if tickets_df.empty:
    st.info("No ticket data available to generate reports.")
    if st.button("Return to Dashboard"):
        st.switch_page("app.py")
    st.stop()

# Convert date columns to datetime
tickets_df['submit_date'] = pd.to_datetime(tickets_df['submit_date'])
tickets_df['updated_date'] = pd.to_datetime(tickets_df['updated_date'])

# Time period selector
st.sidebar.header("Time Period")
date_options = ["All Time", "Last 7 Days", "Last 30 Days", "Last 90 Days", "Custom Range"]
selected_period = st.sidebar.selectbox("Select Time Period", date_options)

if selected_period == "Custom Range":
    # Calculate default start date (30 days ago)
    default_start_date = datetime.now() - timedelta(days=30)
    
    # Get the earliest date in the dataset
    if not tickets_df.empty:
        min_date = tickets_df['submit_date'].min().date()
    else:
        min_date = default_start_date.date()
    
    # Custom date range selector
    start_date = st.sidebar.date_input("Start Date", value=default_start_date, min_value=min_date)
    end_date = st.sidebar.date_input("End Date", value=datetime.now().date())
    
    # Ensure end date is not before start date
    if start_date > end_date:
        st.sidebar.error("End date must be after start date.")
        # Swap dates to prevent errors in filtering
        start_date, end_date = end_date, start_date
    
    # Filter data for the selected date range
    filtered_df = tickets_df[(tickets_df['submit_date'].dt.date >= start_date) & 
                             (tickets_df['submit_date'].dt.date <= end_date)]
elif selected_period == "Last 7 Days":
    date_threshold = datetime.now() - timedelta(days=7)
    filtered_df = tickets_df[tickets_df['submit_date'] >= date_threshold]
elif selected_period == "Last 30 Days":
    date_threshold = datetime.now() - timedelta(days=30)
    filtered_df = tickets_df[tickets_df['submit_date'] >= date_threshold]
elif selected_period == "Last 90 Days":
    date_threshold = datetime.now() - timedelta(days=90)
    filtered_df = tickets_df[tickets_df['submit_date'] >= date_threshold]
else:  # All Time
    filtered_df = tickets_df.copy()

# Display metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Tickets", len(filtered_df))

with col2:
    avg_resolution_time = "N/A"
    completed_tickets = filtered_df[filtered_df['status'] == 'Completed']
    
    if not completed_tickets.empty:
        # Calculate resolution time for completed tickets
        completed_tickets['resolution_time'] = (completed_tickets['updated_date'] - 
                                              completed_tickets['submit_date']).dt.total_seconds() / 3600 / 24  # in days
        avg_resolution_time = f"{completed_tickets['resolution_time'].mean():.1f} days"
    
    st.metric("Avg. Resolution Time", avg_resolution_time)

with col3:
    completion_rate = "N/A"
    if len(filtered_df) > 0:
        completion_rate = f"{len(completed_tickets) / len(filtered_df) * 100:.1f}%"
    
    st.metric("Completion Rate", completion_rate)

with col4:
    open_tickets = len(filtered_df[filtered_df['status'].isin(['Pending', 'In Progress'])])
    st.metric("Open Tickets", open_tickets)

# Visualizations
st.subheader("Ticket Distribution")

# Layout for charts
col1, col2 = st.columns(2)

with col1:
    # Tickets by Status
    status_counts = filtered_df['status'].value_counts().reset_index()
    status_counts.columns = ['Status', 'Count']
    
    fig1 = px.pie(status_counts, values='Count', names='Status', 
                 title='Tickets by Status',
                 color_discrete_sequence=px.colors.qualitative.Set3)
    fig1.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    # Tickets by Category
    category_counts = filtered_df['category'].value_counts().reset_index()
    category_counts.columns = ['Category', 'Count']
    
    fig2 = px.bar(category_counts, x='Category', y='Count', 
                 title='Tickets by Category',
                 color_discrete_sequence=px.colors.qualitative.Set2)
    fig2.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig2, use_container_width=True)

# Tickets by Priority
priority_order = ["Low", "Medium", "High", "Urgent"]
priority_counts = filtered_df['priority'].value_counts().reindex(priority_order, fill_value=0).reset_index()
priority_counts.columns = ['Priority', 'Count']

fig3 = px.bar(priority_counts, x='Priority', y='Count', 
             title='Tickets by Priority',
             color='Priority',
             color_discrete_map={'Low': 'green', 'Medium': 'blue', 'High': 'orange', 'Urgent': 'red'})
st.plotly_chart(fig3, use_container_width=True)

# Tickets over time
if not filtered_df.empty:
    # Group by day
    filtered_df['date'] = filtered_df['submit_date'].dt.date
    tickets_per_day = filtered_df.groupby('date').size().reset_index(name='count')
    
    # Ensure all dates in range are included
    if selected_period == "Custom Range":
        all_dates = pd.date_range(start=start_date, end=end_date, freq='D')
    elif selected_period == "Last 7 Days":
        all_dates = pd.date_range(start=datetime.now() - timedelta(days=7), end=datetime.now(), freq='D')
    elif selected_period == "Last 30 Days":
        all_dates = pd.date_range(start=datetime.now() - timedelta(days=30), end=datetime.now(), freq='D')
    elif selected_period == "Last 90 Days":
        all_dates = pd.date_range(start=datetime.now() - timedelta(days=90), end=datetime.now(), freq='D')
    else:  # All Time
        all_dates = pd.date_range(start=filtered_df['submit_date'].min().date(), 
                                end=filtered_df['submit_date'].max().date(), freq='D')
    
    # Create a dataframe with all dates
    all_dates_df = pd.DataFrame({'date': all_dates.date})
    
    # Merge with actual counts
    tickets_per_day = pd.merge(all_dates_df, tickets_per_day, on='date', how='left').fillna(0)
    
    fig4 = px.line(tickets_per_day, x='date', y='count', 
                  title='Tickets Created Over Time',
                  labels={'date': 'Date', 'count': 'Number of Tickets'})
    st.plotly_chart(fig4, use_container_width=True)

# Detailed Ticket Data Table
st.subheader("Detailed Ticket Data")
st.dataframe(
    filtered_df[['ticket_id', 'title', 'category', 'status', 'priority', 'submit_date']],
    use_container_width=True,
    hide_index=True
)

# Export data options
st.subheader("Export Data")
col1, col2 = st.columns(2)

with col1:
    if st.button("Export to CSV"):
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name=f"ticket_report_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

# Button to return to dashboard
if st.button("Return to Dashboard"):
    st.switch_page("app.py")
