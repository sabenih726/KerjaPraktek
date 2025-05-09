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

def process_pdfs(files, doc_type, use_name=False, use_passport=False):
    extracted_data = []
    renamed_files = {}

    temp_dir = tempfile.mkdtemp()

    for file in files:
        file_name = file.name
        file_path = os.path.join(temp_dir, file_name)

        with open(file_path, "wb") as f:
            f.write(file.read())

        text = read_pdf_text(file_path)

        # Ekstraksi berdasarkan jenis dokumen
        if doc_type == "SKTT":
            data = extract_sktt(text)
        elif doc_type == "EVLN":
            data = extract_evln(text)
        elif doc_type == "ITAS":
            data = extract_itas(text)
        elif doc_type == "ITK":
            data = extract_itk(text)
        elif doc_type == "Notifikasi":
            data = extract_notifikasi(text)
        else:
            continue

        # Penamaan baru berdasarkan preferensi
        new_name = generate_new_filename(file_name, data, use_name, use_passport)

        # Rename dan simpan
        new_path = os.path.join(temp_dir, new_name)
        os.rename(file_path, new_path)
        renamed_files[file_name] = {"new_name": new_name}
        extracted_data.append(data)

    # Simpan hasil ke Excel
    df = pd.DataFrame(extracted_data)
    excel_path = os.path.join(temp_dir, "Hasil_Ekstraksi.xlsx")
    df.to_excel(excel_path, index=False)

    # Kompres semua file hasil
    zip_path = shutil.make_archive(os.path.join(temp_dir, "Renamed_Files"), "zip", temp_dir)

    return df, excel_path, renamed_files, zip_path, temp_dir
