import streamlit as st
import pandas as pd
import os
import sys
import matplotlib.pyplot as plt
import io
from datetime import datetime, timedelta

# Add parent directory to path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import utils

# Page configuration
st.set_page_config(
    page_title="Reports - GA Ticket System",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Data file paths
data_dir = 'data'
tickets_file = os.path.join(data_dir, 'tickets.csv')

# Authentication check
def check_authentication():
    if 'authenticated' not in st.session_state or not st.session_state.authenticated:
        st.warning("Please log in from the Admin Dashboard page first.")
        st.stop()

# Generate reports
def generate_reports():
    st.title("📊 Ticket System Reports")
    
    # Load tickets data
    if not os.path.exists(tickets_file):
        st.info("No ticket data available to generate reports.")
        return
    
    tickets_df = pd.read_csv(tickets_file)
    
    if len(tickets_df) == 0:
        st.info("No tickets found in the system.")
        return
    
    # Convert date columns to datetime for filtering
    tickets_df['created_at'] = pd.to_datetime(tickets_df['created_at'])
    tickets_df['updated_at'] = pd.to_datetime(tickets_df['updated_at'])
    
    # Sidebar filters
    st.sidebar.header("Report Filters")
    
    # Date range filter
    st.sidebar.subheader("Date Range")
    date_options = ["All Time", "Last 7 Days", "Last 30 Days", "Last 90 Days", "Custom Range"]
    date_filter = st.sidebar.selectbox("Select Period", date_options)
    
    if date_filter == "Custom Range":
        min_date = tickets_df['created_at'].min().date()
        max_date = tickets_df['created_at'].max().date()
        
        start_date = st.sidebar.date_input("Start Date", min_date)
        end_date = st.sidebar.date_input("End Date", max_date)
        
        # Convert to datetime for filtering
        start_datetime = pd.Timestamp(start_date)
        end_datetime = pd.Timestamp(end_date) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
        
        filtered_df = tickets_df[(tickets_df['created_at'] >= start_datetime) & 
                               (tickets_df['created_at'] <= end_datetime)]
    else:
        if date_filter == "Last 7 Days":
            cutoff_date = datetime.now() - timedelta(days=7)
        elif date_filter == "Last 30 Days":
            cutoff_date = datetime.now() - timedelta(days=30)
        elif date_filter == "Last 90 Days":
            cutoff_date = datetime.now() - timedelta(days=90)
        else:  # All Time
            cutoff_date = tickets_df['created_at'].min()
        
        filtered_df = tickets_df[tickets_df['created_at'] >= cutoff_date]
    
    # Category filter (multiselect)
    all_categories = sorted(tickets_df['category'].unique())
    selected_categories = st.sidebar.multiselect("Categories", all_categories, default=all_categories)
    
    if selected_categories:
        filtered_df = filtered_df[filtered_df['category'].isin(selected_categories)]
    
    # Status filter (multiselect)
    all_statuses = sorted(tickets_df['status'].unique())
    selected_statuses = st.sidebar.multiselect("Status", all_statuses, default=all_statuses)
    
    if selected_statuses:
        filtered_df = filtered_df[filtered_df['status'].isin(selected_statuses)]
    
    # Display metrics
    st.subheader("Summary Metrics")
    
    if len(filtered_df) == 0:
        st.warning("No tickets match the selected filters.")
        return
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Tickets", len(filtered_df))
    
    with col2:
        avg_response_time = "N/A"  # In a real system, you'd calculate this
        st.metric("Avg Response Time", avg_response_time)
    
    with col3:
        resolution_rate = f"{len(filtered_df[filtered_df['status'] == 'Resolved']) / len(filtered_df):.1%}" if len(filtered_df) > 0 else "0%"
        st.metric("Resolution Rate", resolution_rate)
    
    with col4:
        mean_open_days = "N/A"  # In a real system, you'd calculate this
        st.metric("Mean Open Days", mean_open_days)
    
    # Charts
    st.subheader("Visualizations")
    
    tab1, tab2, tab3 = st.tabs(["Status Distribution", "Category Distribution", "Tickets Over Time"])
    
    with tab1:
        # Status distribution
        status_counts = filtered_df['status'].value_counts()
        
        # Create a buffer to hold the chart
        buf = io.BytesIO()
        
        # Create a figure and axis
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Plot the data
        status_counts.plot(kind='pie', autopct='%1.1f%%', ax=ax)
        ax.set_title('Ticket Status Distribution')
        ax.set_ylabel('')
        
        # Save the figure to the buffer
        plt.tight_layout()
        plt.savefig(buf, format='png')
        buf.seek(0)
        
        # Display the figure
        st.image(buf)
    
    with tab2:
        # Category distribution
        category_counts = filtered_df['category'].value_counts()
        
        # Create a buffer to hold the chart
        buf = io.BytesIO()
        
        # Create a figure and axis
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Plot the data
        category_counts.plot(kind='bar', ax=ax)
        ax.set_title('Ticket Category Distribution')
        ax.set_xlabel('Category')
        ax.set_ylabel('Number of Tickets')
        
        # Save the figure to the buffer
        plt.tight_layout()
        plt.savefig(buf, format='png')
        buf.seek(0)
        
        # Display the figure
        st.image(buf)
    
    with tab3:
        # Tickets over time (daily)
        filtered_df['date'] = filtered_df['created_at'].dt.date
        daily_counts = filtered_df.groupby('date').size()
        
        # Create a buffer to hold the chart
        buf = io.BytesIO()
        
        # Create a figure and axis
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Plot the data
        daily_counts.plot(kind='line', marker='o', ax=ax)
        ax.set_title('Tickets Submitted Over Time')
        ax.set_xlabel('Date')
        ax.set_ylabel('Number of Tickets')
        
        # Save the figure to the buffer
        plt.tight_layout()
        plt.savefig(buf, format='png')
        buf.seek(0)
        
        # Display the figure
        st.image(buf)
    
    # Raw data and export options
    st.subheader("Raw Data")
    
    # Display simplified dataframe
    display_cols = ['ticket_id', 'created_at', 'name', 'subject', 'category', 'priority', 'status']
    st.dataframe(filtered_df[display_cols])
    
    # Export options
    st.subheader("Export Options")
    
    export_format = st.radio("Select Format", ["CSV", "Excel"], horizontal=True)
    
    if st.button("Generate Report"):
        if export_format == "CSV":
            csv = filtered_df.to_csv(index=False)
            filename = f"ticket_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            st.download_button(
                label="Download CSV Report",
                data=csv,
                file_name=filename,
                mime="text/csv"
            )
        else:  # Excel
            # Generate Excel file
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                filtered_df.to_excel(writer, sheet_name='Ticket Data', index=False)
            
            filename = f"ticket_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            
            st.download_button(
                label="Download Excel Report",
                data=output.getvalue(),
                file_name=filename,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

# Main execution
check_authentication()
generate_reports()
