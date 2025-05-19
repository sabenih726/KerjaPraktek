import streamlit as st
import pandas as pd
import os
import sys
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import utils

st.set_page_config(
    page_title="Reports - GA Ticket System",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
:root {
  --primary: #f7901e;
  --background: #ffffff;
  --foreground: #000000;
  --card: #fff4e5;
  --card-foreground: #000000;
  --muted-foreground: #666666;
}

/* Global background and text */
html, body, [data-testid="stAppViewContainer"] {
  background-color: var(--background);
  color: var(--foreground);
  font-family: 'Segoe UI', sans-serif;
}

/* Headings */
h1, h2, h3, h4, h5 {
  color: var(--primary);
  font-weight: 700;
}

/* Sidebar */
[data-testid="stSidebar"] h3 {
  color: var(--primary);
  font-weight: 700;
}

/* Button */
.stButton>button {
  background-color: var(--primary);
  color: var(--foreground);
  font-weight: bold;
  border-radius: 6px;
  padding: 0.5rem 1.2rem;
  border: none;
}
.stButton>button:hover {
  background-color: #ffa940;
  color: var(--foreground);
}

/* Tabs */
.stTabs [role="tablist"] button {
  background-color: var(--primary);
  color: var(--foreground);
  font-weight: 700;
  border-radius: 4px 4px 0 0;
  margin-right: 0.2rem;
  border: none;
}
.stTabs [role="tablist"] button[aria-selected="true"] {
  background-color: #ffa940;
  border-bottom: 2px solid var(--primary);
}

/* Metric containers */
.stMetric > div {
  background-color: var(--card);
  color: var(--card-foreground);
  border-radius: 8px;
  padding: 1rem;
  font-weight: 700;
}

/* Table headers */
thead tr th {
  background-color: var(--primary) !important;
  color: var(--foreground) !important;
}

/* Sidebar select and multiselect */
[data-baseweb="select"] {
  color: var(--foreground);
}

/* Download buttons */
[data-testid="baseButton-secondary"] {
  background-color: var(--primary);
  color: var(--foreground);
  font-weight: 700;
}
</style>
""", unsafe_allow_html=True)

try:
    plt.style.use('seaborn-v0_8-dark')
except OSError:
    plt.style.use('ggplot')

data_dir = 'data'
tickets_file = os.path.join(data_dir, 'tickets.csv')

def check_authentication():
    if 'authenticated' not in st.session_state or not st.session_state.authenticated:
        st.warning("Please log in from the Admin Dashboard page first.")
        st.stop()

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

    # Sidebar Filters
    st.sidebar.header("Report Filters")
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

    all_categories = sorted(tickets_df['category'].unique())
    selected_categories = st.sidebar.multiselect("Categories", all_categories, default=all_categories)
    if selected_categories:
        filtered_df = filtered_df[filtered_df['category'].isin(selected_categories)]

    all_statuses = sorted(tickets_df['status'].unique())
    selected_statuses = st.sidebar.multiselect("Status", all_statuses, default=all_statuses)
    if selected_statuses:
        filtered_df = filtered_df[filtered_df['status'].isin(selected_statuses)]

    st.markdown("### Summary Metrics")
    if filtered_df.empty:
        st.warning("No tickets match the selected filters.")
        return

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Tickets", len(filtered_df))
    with col2:
        # Calculate average response time if possible
        if 'response_time_minutes' in filtered_df.columns:
            avg_response = filtered_df['response_time_minutes'].mean()
            st.metric("Avg Response Time", f"{avg_response:.1f} mins")
        else:
            st.metric("Avg Response Time", "N/A")
    with col3:
        resolution_rate = f"{(filtered_df['status'] == 'Resolved').sum() / len(filtered_df):.1%}"
        st.metric("Resolution Rate", resolution_rate)
    with col4:
        if 'created_at' in filtered_df.columns and 'updated_at' in filtered_df.columns:
            open_days = (filtered_df['updated_at'] - filtered_df['created_at']).dt.days.mean()
            st.metric("Mean Open Days", f"{open_days:.1f} days")
        else:
            st.metric("Mean Open Days", "N/A")

    st.markdown("### Visualizations")
    tab1, tab2, tab3 = st.tabs(["Status Distribution", "Category Distribution", "Tickets Over Time"])

    trakindo_orange = "#f7901e"
    status_colors = [trakindo_orange, "#f7a431", "#cccccc"]

    with tab1:
        status_counts = filtered_df['status'].value_counts()
        fig, ax = plt.subplots(figsize=(8, 5))
        status_counts.plot.pie(autopct='%1.1f%%', ax=ax, colors=status_colors)
        ax.set_title('Ticket Status Distribution')
        ax.set_ylabel('')
        st.pyplot(fig)

    with tab2:
        category_counts = filtered_df['category'].value_counts()
        fig, ax = plt.subplots(figsize=(10, 5))
        category_counts.plot.bar(ax=ax, color=trakindo_orange)
        ax.set_title('Ticket Category Distribution')
        ax.set_xlabel('Category')
        ax.set_ylabel('Number of Tickets')
        st.pyplot(fig)

    with tab3:
        filtered_df['date'] = filtered_df['created_at'].dt.date
        daily_counts = filtered_df.groupby('date').size()
        fig, ax = plt.subplots(figsize=(10, 5))
        daily_counts.plot.line(marker='o', ax=ax, color=trakindo_orange)
        ax.set_title('Tickets Submitted Over Time')
        ax.set_xlabel('Date')
        ax.set_ylabel('Number of Tickets')
        st.pyplot(fig)

    st.markdown("### Raw Data")
    display_cols = ['ticket_id', 'created_at', 'name', 'subject', 'category', 'priority', 'status']
    st.dataframe(filtered_df[display_cols], use_container_width=True)

    st.markdown("### Export Options")
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

check_authentication()
generate_reports()
