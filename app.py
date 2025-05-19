import streamlit as st
import pandas as pd
import os
import uuid
from datetime import datetime
import utils

# Page configuration
st.set_page_config(
    page_title="Sistem Dukungan Trakindo",
    page_icon="🎫",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Hide pages from sidebar for regular users and apply custom styling
# Load custom CSS file
with open('.streamlit/style.css') as f:
    css = f.read()
    
# Add CSS to hide sidebar navigation
hide_pages_style = """
<style>
    div[data-testid="stSidebarNav"] {display: none !important;}
</style>
"""
# Apply both styles
st.markdown(f"""
{hide_pages_style}
<style>
{css}
</style>
""", unsafe_allow_html=True)

# Create data directory if it doesn't exist
os.makedirs('data', exist_ok=True)
data_file = 'data/tickets.csv'

# Initialize dataframe if file doesn't exist
if not os.path.exists(data_file):
    initial_df = pd.DataFrame(columns=[
        'ticket_id', 'created_at', 'updated_at', 'name', 'email', 
        'subject', 'category', 'priority', 'status', 'description', 'resolution'
    ])
    initial_df.to_csv(data_file, index=False)

# Page title with Trakindo CAT theme
st.markdown("""
<div style="text-align: center; padding: 1.5rem 0; margin-bottom: 2rem;">
    <div style="margin-bottom: 1rem; display: flex; justify-content: center; align-items: center;">
        <div style="background-color: #FFBB00; color: #000000; padding: 5px 15px; font-weight: bold; font-size: 1.8rem; border-radius: 4px;">
            Trakindo
        </div>
        <div style="background-color: #000000; color: white; padding: 5px 15px; font-weight: bold; font-size: 1.8rem; border-radius: 4px; margin-left: 5px;">
            CAT
        </div>
    </div>
    <h1 style="color: #000000; font-size: 2.5rem; font-weight: 700; margin-bottom: 0.5rem;">
        Sistem Dukungan
    </h1>
    <p style="color: #6b7280; font-size: 1rem;">Kirim dan lacak permintaan dukungan dengan mudah</p>
</div>
""", unsafe_allow_html=True)

# Create tabs for submission and tracking with improved styling
tab1, tab2 = st.tabs(["📝 Buat Tiket", "🔍 Lacak Tiket"])

# Submit a Ticket tab
with tab1:
    st.markdown("""
    <h2 style="color: #111827; font-weight: 600; margin-bottom: 1rem; padding-bottom: 0.5rem; border-bottom: 1px solid #e5e7eb;">
        📝 Buat Tiket Dukungan Baru
    </h2>
    """, unsafe_allow_html=True)
    
    # Card-like container for the form
    st.markdown("""
    <div style="background-color: white; border-radius: 0.5rem; padding: 1rem; margin-bottom: 1rem; box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24);">
        <p style="color: #6b7280; font-size: 0.875rem;">
            Silakan isi formulir di bawah ini untuk mengirimkan tiket dukungan baru. Semua kolom dengan tanda * wajib diisi.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Ticket form with modern styling
    with st.form("ticket_submission_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Nama Lengkap *", placeholder="Masukkan nama lengkap Anda")
            email = st.text_input("Alamat Email *", placeholder="Masukkan alamat email Anda")
            category = st.selectbox(
                "Kategori Tiket *", 
                ["Pertanyaan Umum", "Dukungan Teknis", "Masalah Penagihan", "Permintaan Fitur", "Laporan Bug", "Lainnya"]
            )
        
        with col2:
            subject = st.text_input("Subjek *", placeholder="Ringkasan singkat masalah Anda")
            priority = st.selectbox("Tingkat Prioritas *", ["Rendah", "Sedang", "Tinggi", "Kritis"],
                                  help="Pilih tingkat urgensi masalah Anda")
        
        description = st.text_area(
            "Deskripsi Detail *", 
            placeholder="Berikan informasi rinci tentang masalah Anda termasuk langkah-langkah untuk mereproduksi masalah jika ada",
            height=150
        )
        
        submit_button = st.form_submit_button("📤 Kirim Tiket")
        
        if submit_button:
            if not name or not email or not subject or not description:
                st.error("Mohon isi semua kolom yang wajib diisi.")
            elif not utils.is_valid_email(email):
                st.error("Mohon masukkan alamat email yang valid.")
            else:
                # Generate unique ticket ID
                ticket_id = str(uuid.uuid4())[:8].upper()
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # Create new ticket
                new_ticket = {
                    'ticket_id': ticket_id,
                    'created_at': timestamp,
                    'updated_at': timestamp,
                    'name': name,
                    'email': email,
                    'subject': subject,
                    'category': category,
                    'priority': priority,
                    'status': "Dibuka",
                    'description': description,
                    'resolution': ""
                }
                
                # Save to CSV
                utils.add_ticket(new_ticket, data_file)
                
                # Success message with ticket ID
                st.success(f"Tiket Anda telah berhasil dikirim!")
                st.info(f"ID Tiket Anda adalah: **{ticket_id}**")
                st.info("Harap simpan ID ini untuk melacak status tiket Anda.")

# Track Your Ticket tab
with tab2:
    st.markdown("""
    <h2 style="color: #111827; font-weight: 600; margin-bottom: 1rem; padding-bottom: 0.5rem; border-bottom: 1px solid #e5e7eb;">
        🔍 Lacak Tiket Anda
    </h2>
    """, unsafe_allow_html=True)
    
    # Card-like container for the tracking form
    st.markdown("""
    <div style="background-color: white; border-radius: 0.5rem; padding: 1rem; margin-bottom: 1.5rem; box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24);">
        <p style="color: #6b7280; font-size: 0.875rem;">
            Masukkan ID tiket Anda di bawah ini untuk memeriksa status permintaan dukungan Anda.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Modern tracking form
    col1, col2 = st.columns([3, 1])
    with col1:
        ticket_id = st.text_input("Masukkan ID Tiket Anda", key="track_ticket_id", placeholder="mis. A1B2C3D4").strip().upper()
    with col2:
        track_button = st.button("🔍 Lacak Tiket", type="primary", use_container_width=True)
    
    if track_button:
        if not ticket_id:
            st.error("Mohon masukkan ID tiket.")
        else:
            ticket_info = utils.get_ticket_by_id(ticket_id, data_file)
            
            if ticket_info is not None:
                st.success(f"Tiket ditemukan: {ticket_id}")
                
                # Status Card
                status = ticket_info['status']
                status_color = "#10B981" if status == "Dibuka" else "#F59E0B" if status == "Dalam Proses" else "#3B82F6" if status == "Selesai" else "#6B7280"
                status_icon = "🟢" if status == "Dibuka" else "🟠" if status == "Dalam Proses" else "🔵" if status == "Selesai" else "⚫"
                
                st.markdown(f"""
                <div style="background-color: white; border-radius: 0.5rem; padding: 1.5rem; margin-bottom: 1.5rem; box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24); border-left: 5px solid {status_color};">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                        <h3 style="margin: 0; color: #111827;">Tiket #{ticket_info['ticket_id']}</h3>
                        <span style="font-size: 1.25rem; background-color: {status_color}30; color: {status_color}; padding: 0.25rem 0.75rem; border-radius: 9999px; font-weight: 500;">
                            {status_icon} {status}
                        </span>
                    </div>
                    <h3 style="margin-top: 0; margin-bottom: 0.5rem; color: #111827;">{ticket_info['subject']}</h3>
                    <p style="color: #6B7280; margin-bottom: 0.25rem;">Diajukan oleh {ticket_info['name']} pada {ticket_info['created_at']}</p>
                    <p style="color: #6B7280; margin-bottom: 0.25rem;">Kategori: {ticket_info['category']} | Prioritas: {ticket_info['priority']}</p>
                    <p style="color: #6B7280; margin-bottom: 0;">Terakhir Diperbarui: {ticket_info['updated_at']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Ticket details in tabs
                details_tab, description_tab, resolution_tab = st.tabs(["📋 Detail", "📝 Deskripsi", "✅ Penyelesaian"])
                
                with details_tab:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("### Informasi Tiket")
                        st.markdown(f"**ID:** {ticket_info['ticket_id']}")
                        st.markdown(f"**Subjek:** {ticket_info['subject']}")
                        st.markdown(f"**Kategori:** {ticket_info['category']}")
                        st.markdown(f"**Diajukan oleh:** {ticket_info['name']}")
                    
                    with col2:
                        st.markdown("### Detail Status")
                        st.markdown(f"**Status Saat Ini:** {ticket_info['status']}")
                        st.markdown(f"**Tingkat Prioritas:** {ticket_info['priority']}")
                        st.markdown(f"**Dibuat Pada:** {ticket_info['created_at']}")
                        st.markdown(f"**Terakhir Diperbarui:** {ticket_info['updated_at']}")
                
                with description_tab:
                    st.markdown("### Deskripsi Tiket")
                    st.markdown("""
                    <div style="background-color: #f9fafb; border-radius: 0.375rem; padding: 1rem; border: 1px solid #e5e7eb;">
                        <p style="white-space: pre-wrap;">{}</p>
                    </div>
                    """.format(ticket_info['description']), unsafe_allow_html=True)
                
                with resolution_tab:
                    if ticket_info['resolution']:
                        st.markdown("### Detail Penyelesaian")
                        st.markdown("""
                        <div style="background-color: #f0fdf4; border-radius: 0.375rem; padding: 1rem; border: 1px solid #d1fae5;">
                            <p style="white-space: pre-wrap;">{}</p>
                        </div>
                        """.format(ticket_info['resolution']), unsafe_allow_html=True)
                    else:
                        st.info("Tiket ini masih dalam proses. Periksa kembali nanti untuk pembaruan.")
            else:
                st.error(f"Tidak ditemukan tiket dengan ID: {ticket_id}")

# Footer with Trakindo CAT theme
st.markdown("""
<div style="margin-top: 3rem; padding-top: 1.5rem; border-top: 1px solid #e5e7eb; text-align: center;">
    <p style="color: #6b7280; font-size: 0.875rem;">© 2025 Sistem Dukungan Trakindo • Butuh bantuan? <a href="mailto:support@trakindo.co.id" style="color: #FFBB00; text-decoration: none; font-weight: 500;">Hubungi Dukungan</a></p>
</div>

<div class="admin-link">
    <a href="/admin_dashboard" target="_self">Admin</a>
</div>
""", unsafe_allow_html=True)
