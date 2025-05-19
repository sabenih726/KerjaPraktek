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

# Page config
st.set_page_config(
    page_title="Reports - GA Ticket System",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# === Custom Styling ===
st.markdown("""
    <style>
    .stButton>button {
        background-color: #f7901e;
        color: white;
        font-weight: bold;
        border-radius: 8px;
    }
    .stRadio > div {
        color: #333;
    }
    .stMetric {
        background-color: #f7901e;
        color: white;
        border-radius: 8px;
    }
    .block-container {
        padding-top: 2rem;
    }
    h1, h2, h3, h4, h5 {
        color: #f7901e;
    }
    .stTabs [data-baseweb="tab-list"] button {
        background-color: #f7901e;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# Matplotlib Style
plt.style.use('seaborn-dark')

# File paths
data_dir = 'data'
tickets_file = os.path.join(data_dir, 'tickets.csv')

# Auth check
def check_authentication():
    if 'authenticated' not in st.session_state or not st.session_state.authenticated:
        st.warning("Please log in from the Admin Dashboard page first.")
        st.stop()

# Main report function
def generate_reports():
    st.title("📊 Ticket System Reports")
    st.markdown("---")

    if not os.path.exists(tickets_file):
        st.info("No ticket data available to generate reports.")
        return
    
    tickets_df = pd.read_csv(tickets_file)
    if tickets_df.empty:
        st.info("No tickets found in the system.")
        return

    tickets_df['created_at'] = pd.to_datetime(tickets_df['created_at'])
    tickets_df['updated_at'] = pd.to_datetime(tickets_df['updated_at'])

    # Sidebar
    st.sidebar.markdown("<h3 style='color:#f7901e;'>Report Filters</h3>", unsafe_allow_html=True)
    date_options = ["All Time", "Last 7 Days", "Last 30 Days", "Last 90 Days", "Custom Range"]
    date_filter = st.sidebar.selectbox("Select Period", date_options)

    if date_filter == "Custom Range":
        min_date = tickets_df['created_at'].min().date()
        max_date = tickets_df['created_at'].max().date()
        start_date = st.sidebar.date_input("Start Date", min_date)
        end_date = st.sidebar.date_input("End Date", max_date)
        start_datetime = pd.Timestamp(start_date)
        end_datetime = pd.Timestamp(end_date) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
        filtered_df = tickets_df[(tickets_df['created_at'] >= start_datetime) & (tickets_df['created_at'] <= end_datetime)]
    else:
        days_map = {
            "Last 7 Days": 7,
            "Last 30 Days": 30,
            "Last 90 Days": 90,
            "All Time": None
        }
        if days_map[date_filter] is not None:
            cutoff_date = datetime.now() - timedelta(days=days_map[date_filter])
            filtered_df = tickets_df[tickets_df['created_at'] >= cutoff_date]
        else:
            filtered_df = tickets_df

    # Filters
    all_categories = sorted(tickets_df['category'].unique())
    selected_categories = st.sidebar.multiselect("Categories", all_categories, default=all_categories)
    if selected_categories:
        filtered_df = filtered_df[filtered_df['category'].isin(selected_categories)]

    all_statuses = sorted(tickets_df['status'].unique())
    selected_statuses = st.sidebar.multiselect("Status", all_statuses, default=all_statuses)
    if selected_statuses:
        filtered_df = filtered_df[filtered_df['status'].isin(selected_statuses)]

    # Metrics
    st.markdown("<h4 style='color:#f7901e;'>Summary Metrics</h4>", unsafe_allow_html=True)
    if filtered_df.empty:
        st.warning("No tickets match the selected filters.")
        return

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Tickets", len(filtered_df))
    with col2:
        st.metric("Avg Response Time", "N/A")
    with col3:
        resolution_rate = f"{(filtered_df['status'] == 'Resolved').sum() / len(filtered_df):.1%}"
        st.metric("Resolution Rate", resolution_rate)
    with col4:
        st.metric("Mean Open Days", "N/A")

    # Charts
    st.markdown("<h4 style='color:#f7901e;'>Visualizations</h4>", unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs(["Status Distribution", "Category Distribution", "Tickets Over Time"])

    trakindo_color = "#f7901e"
    status_colors = ['#f7901e', '#f7b01e', '#ddd']

    with tab1:
        status_counts = filtered_df['status'].value_counts()
        buf = io.BytesIO()
        fig, ax = plt.subplots(figsize=(8, 5))
        status_counts.plot(kind='pie', autopct='%1.1f%%', ax=ax, colors=status_colors)
        ax.set_title('Ticket Status Distribution')
        ax.set_ylabel('')
        plt.tight_layout()
        plt.savefig(buf, format='png')
        buf.seek(0)
        st.image(buf)

    with tab2:
        category_counts = filtered_df['category'].value_counts()
        buf = io.BytesIO()
        fig, ax = plt.subplots(figsize=(10, 5))
        category_counts.plot(kind='bar', ax=ax, color=trakindo_color)
        ax.set_title('Ticket Category Distribution')
        ax.set_xlabel('Category')
        ax.set_ylabel('Number of Tickets')
        plt.tight_layout()
        plt.savefig(buf, format='png')
        buf.seek(0)
        st.image(buf)

    with tab3:
        filtered_df['date'] = filtered_df['created_at'].dt.date
        daily_counts = filtered_df.groupby('date').size()
        buf = io.BytesIO()
        fig, ax = plt.subplots(figsize=(10, 5))
        daily_counts.plot(kind='line', marker='o', ax=ax, color=trakindo_color)
        ax.set_title('Tickets Submitted Over Time')
        ax.set_xlabel('Date')
        ax.set_ylabel('Number of Tickets')
        plt.tight_layout()
        plt.savefig(buf, format='png')
        buf.seek(0)
        st.image(buf)

    # Raw Data
    st.markdown("<h4 style='color:#f7901e;'>Raw Data</h4>", unsafe_allow_html=True)
    display_cols = ['ticket_id', 'created_at', 'name', 'subject', 'category', 'priority', 'status']
    st.dataframe(filtered_df[display_cols])

    # Export
    st.markdown("<h4 style='color:#f7901e;'>Export Options</h4>", unsafe_allow_html=True)
    export_format = st.radio("Select Format", ["CSV", "Excel"], horizontal=True)

    if st.button("Generate Report"):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        if export_format == "CSV":
            csv = filtered_df.to_csv(index=False)
            st.download_button(
                label="Download CSV Report",
                data=csv,
                file_name=f"ticket_report_{timestamp}.csv",
                mime="text/csv"
            )
        else:
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                filtered_df.to_excel(writer, sheet_name='Ticket Data', index=False)
            st.download_button(
                label="Download Excel Report",
                data=output.getvalue(),
                file_name=f"ticket_report_{timestamp}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

# Execute
check_authentication()
generate_reports()
