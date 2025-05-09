import streamlit as st
from pdf_convert import process_pdfs
import shutil

def main():
    if not st.session_state.logged_in:
        login_page()
    else:
        with st.sidebar:
            st.markdown('<div class="sidebar-header">PT LAMAN DAVINDO BAHMAN</div>', unsafe_allow_html=True)
            st.markdown(f'<p style="font-weight: 600; font-size: 1.2rem;">{get_greeting()}</p>', unsafe_allow_html=True)
            st.markdown('<div class="alert-warning">⚠️ Please Pay the Bill</div>', unsafe_allow_html=True)
            st.button("Transfer", type="primary")
            st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
            
            with st.expander("📋 Main Menu"):
                st.markdown("- 🏠 Home")
                st.markdown("- 📄 Document")
                st.markdown("- 👥 Client")
                st.markdown("- ⚙️ Settings")
            
            if st.button("Logout", type="secondary", use_container_width=True):
                logout()
                st.rerun()
            
            st.caption("© 2025 PT Laman Davindo Bahman")

        st.markdown('<div class="header"><h1 style="margin-bottom: 0.5rem;">📑 Extraction of Immigration Documents</h1><p style="opacity: 0.8;">Upload the PDF file and the system will extract the data automatically</p></div>', unsafe_allow_html=True)

        st.markdown('<div class="container">', unsafe_allow_html=True)
        st.markdown('<h2>Document Upload</h2>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            uploaded_files = st.file_uploader("Upload File PDF", type=["pdf"], accept_multiple_files=True)

        with col2:
            doc_type = st.selectbox(
                "Select Document Type",
                ["SKTT", "EVLN", "ITAS", "ITK", "Notifikasi"]
            )
            use_name = st.checkbox("Use Name to Rename Files", value=True)
            use_passport = st.checkbox("Use Passport Number to Rename Files", value=True)

        st.markdown('</div>', unsafe_allow_html=True)

        if uploaded_files:
            st.markdown('<div class="container">', unsafe_allow_html=True)

            st.markdown('<h3>Uploaded Files</h3>', unsafe_allow_html=True)
            file_info_cols = st.columns(len(uploaded_files) if len(uploaded_files) <= 3 else 3)

            for i, uploaded_file in enumerate(uploaded_files):
                col_idx = i % 3
                with file_info_cols[col_idx]:
                    st.markdown(f'''
                    <div style="background-color: #f8fafc; border-radius: 0.5rem; padding: 0.75rem; margin-bottom: 0.75rem;">
                        <div style="display: flex; align-items: center;">
                            <div style="background-color: #e2e8f0; border-radius: 0.375rem; padding: 0.5rem; margin-right: 0.75rem;">
                                📄
                            </div>
                            <div>
                                <p style="margin: 0; font-weight: 600; font-size: 0.9rem;">{uploaded_file.name}</p>
                                <p style="margin: 0; color: #64748b; font-size: 0.8rem;">PDF Document</p>
                            </div>
                        </div>
                    </div>
                    ''', unsafe_allow_html=True)

            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                process_button = st.button(f"Proses {len(uploaded_files)} File PDF", type="primary", use_container_width=True)

            st.markdown('</div>', unsafe_allow_html=True)

            if process_button:
                progress_placeholder = st.empty()
                progress_placeholder.markdown('''
                <div style="background-color: #f1f5f9; border-radius: 0.5rem; padding: 1.5rem; text-align: center;">
                    <div style="margin-bottom: 1rem;">
                        <img src="https://via.placeholder.com/50x50?text=⚙️" width="50" height="50" style="margin: 0 auto;">
                    </div>
                    <h3 style="margin-bottom: 0.5rem;">Processing Documents</h3>
                    <p style="color: #64748b;">Please wait a moment while we extract the information from your document...</p>
                    <div style="margin-top: 1rem; height: 0.5rem; background-color: #e2e8f0; border-radius: 1rem; overflow: hidden;">
                        <div style="width: 75%; height: 100%; background: linear-gradient(90deg, #0ea5e9, #3b82f6); border-radius: 1rem; animation: progress 2s infinite;"></div>
                    </div>
                </div>
                ''', unsafe_allow_html=True)

                # Proses file
                df, excel_path, renamed_files, zip_path = process_pdfs(
                    uploaded_files, doc_type, use_name, use_passport
                )

                progress_placeholder.empty()

                st.markdown('<div class="container">', unsafe_allow_html=True)
                st.markdown('''
                <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                    <div style="background-color: #d1fae5; color: #047857; border-radius: 50%; width: 2rem; height: 2rem; display: flex; align-items: center; justify-content: center; margin-right: 0.75rem;">
                        ✓
                    </div>
                    <h2 style="margin: 0;">Proses Berhasil</h2>
                </div>
                ''', unsafe_allow_html=True)

                tab1, tab2, tab3 = st.tabs(["💾 Extraction Result", "📊 Excel File", "📁 File Rename"])

                with tab1:
                    st.subheader("Extraction Result Data")
                    st.markdown('<div style="overflow-x: auto;">', unsafe_allow_html=True)
                    st.dataframe(df, use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)

                with tab2:
                    st.subheader("Download File Excel")
                    with open(excel_path, "rb") as f:
                        excel_data = f.read()
                    st.download_button(label="Download Excel", data=excel_data, file_name="Hasil_Ekstraksi.xlsx")

                with tab3:
                    st.subheader("File yang Telah di-Rename")
                    st.markdown('<div style="background-color: #f8fafc; border-radius: 0.5rem; padding: 1rem;">', unsafe_allow_html=True)
                    for original_name, file_info in renamed_files.items():
                        st.markdown(f'''
                        <div style="display: flex; align-items: center; padding: 0.75rem; border-bottom: 1px solid #e2e8f0;">
                            <div style="flex: 1;">
                                <p style="margin: 0; color: #64748b; font-size: 0.85rem;">Nama Asli:</p>
                                <p style="margin: 0; font-weight: 600;">{original_name}</p>
                            </div>
                            <div style="margin: 0 1rem;">
                                <span style="color: #64748b;">→</span>
                            </div>
                            <div style="flex: 1;">
                                <p style="margin: 0; color: #64748b; font-size: 0.85rem;">Nama Baru:</p>
                                <p style="margin: 0; font-weight: 600; color: #0369a1;">{file_info['new_name']}</p>
                            </div>
                        </div>
                        ''', unsafe_allow_html=True)

                    st.markdown('</div>', unsafe_allow_html=True)

                    with open(zip_path, "rb") as f:
                        zip_data = f.read()

                    st.download_button(label="Download All PDF (ZIP) Files", data=zip_data, file_name="Renamed_Files.zip")
                    shutil.rmtree(temp_dir)

                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown('''
            <div class="alert-info">
                <h3 style="margin-top: 0;">Mulai Ekstraksi</h3>
                <p>Please upload PDF files of immigration documents to start the automatic extraction process.</p>
                <ul style="margin-bottom: 0;">
                    <li>Make sure the files are in PDF format</li>
                    <li>Choose the appropriate document type</li>
                    <li>Customise the file naming options if required</li>
                </ul>
            </div>
            ''', unsafe_allow_html=True)
     
        with st.expander("Help"):
            st.write("""
            **How to Use the Application:**
            1. Upload one or more PDF files of immigration documents
            2. Select the appropriate document type (SKTT, EVLN, ITAS, ITK, Notification)
            3. Specify whether to include the name and/or passport number in the file name
            4. Click the ‘Process PDF’ button to start extracting data
            5. View and download the extracted results in Excel format and renamed PDF files.
            """)
