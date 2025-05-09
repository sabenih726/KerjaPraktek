import os
import tempfile
import shutil
import pandas as pd
import fitz  # PyMuPDF
from extract.sktt import extract_sktt
from extract.evln import extract_evln
from extract.itas import extract_itas
from extract.itk import extract_itk
from extract.notifikasi import extract_notifikasi
from utils.rename import generate_new_filename

def read_pdf_text(file_path):
    text = ""
    with fitz.open(file_path) as doc:
        for page in doc:
            text += page.get_text()
    return text

def process_pdfs(uploaded_files, doc_type, use_name, use_passport):
    # Logika pemilihan fungsi ekstraksi berdasarkan jenis dokumen
    if doc_type == "SKTT":
        df, renamed_files = extract_sktt(uploaded_files, use_name, use_passport)
    elif doc_type == "EVLN":
        df, renamed_files = extract_evln(uploaded_files, use_name, use_passport)
    elif doc_type == "ITAS":
        df, renamed_files = extract_itas(uploaded_files, use_name, use_passport)
    elif doc_type == "ITK":
        df, renamed_files = extract_itk(uploaded_files, use_name, use_passport)
    elif doc_type == "Notifikasi":
        df, renamed_files = extract_notifikasi(uploaded_files, use_name, use_passport)

    # Proses file, simpan sebagai excel, rename, dan zip file
    excel_path = save_as_excel(df)
    zip_path = save_as_zip(renamed_files)

    return df, excel_path, renamed_files, zip_path
