import streamlit as st
import pdfplumber
import pandas as pd
import re
import tempfile
import os
import shutil
import zipfile
from datetime import datetime
from extract.sktt import extract_sktt
from extract.evln import extract_evln
from extract.itas import extract_itas
from extract.itk import extract_itk
from extract.notifikasi import extract_notifikasi
from utils.text_cleaning import clean_text
from utils.date_utils import format_date
from utils.rename import generate_new_filename

def extract_text_from_pdf(uploaded_file):
    text = ""
    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

def process_pdfs(uploaded_files, doc_type, use_name, use_passport):
    extracted_data = []
    renamed_files = []

    for uploaded_file in uploaded_files:
        # 1. Ekstrak teks dari PDF (pakai pdfplumber atau fitz)
        text = extract_text_from_pdf(uploaded_file)  # Anda harus punya fungsi ini

        # 2. Proses ekstraksi sesuai jenis dokumen
        if doc_type == "EVLN":
            data = extract_evln(text)
        elif doc_type == "SKTT":
            data = extract_sktt(text)
        elif doc_type == "ITAS":
            data = extract_itas(text)
        elif doc_type == "ITK":
            data = extract_itk(text)
        elif doc_type == "Notifikasi":
            data = extract_notifikasi(text)
        else:
            continue

        extracted_data.append(data)

        # 3. Rename file jika diminta
        new_filename = rename_file(uploaded_file.name, data, use_name, use_passport)
        renamed_files.append((uploaded_file, new_filename))

    # 4. Buat DataFrame dan file Excel + ZIP
    df = pd.DataFrame(extracted_data)
    excel_path = save_to_excel(df)
    zip_path = create_zip(renamed_files)

    return df, excel_path, renamed_files, zip_path
