import streamlit as st
from pdf_convert import process_pdfs

st.title("PDF Dokumen Imigrasi Extractor")

uploaded_files = st.file_uploader("Unggah beberapa PDF", accept_multiple_files=True)
doc_type = st.selectbox("Pilih jenis dokumen", ["SKTT", "EVLN", "ITAS", "ITK", "Notifikasi"])
use_name = st.checkbox("Gunakan Nama untuk Rename", value=True)
use_passport = st.checkbox("Gunakan No. Paspor untuk Rename", value=True)

if st.button("Proses"):
    if uploaded_files and doc_type:
        df, excel_path, renamed_files, zip_path, temp_dir = process_pdfs(uploaded_files, doc_type, use_name, use_passport)

        st.success("Ekstraksi berhasil!")
        st.dataframe(df)

        with open(excel_path, "rb") as f:
            st.download_button("Download Excel", f, file_name="Hasil_Ekstraksi.xlsx")

        with open(zip_path, "rb") as z:
            st.download_button("Download File ZIP", z, file_name="Renamed_Files.zip")
