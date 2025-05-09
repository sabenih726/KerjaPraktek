import os
import tempfile
import shutil
import pandas as pd
from datetime import datetime
import fitz  # PyMuPDF

from extract.sktt import extract_sktt
from extract.evln import extract_evln
from extract.itas import extract_itas
from extract.itk import extract_itk
from extract.notifikasi import extract_notifikasi


def process_pdfs(files, doc_type, use_name, use_passport):
    extracted_data = []
    renamed_files = {}

    temp_dir = tempfile.mkdtemp()

    for file in files:
        file_name = file.name
        file_path = os.path.join(temp_dir, file_name)

        with open(file_path, "wb") as f:
            f.write(file.read())

        if doc_type == "SKTT":
            data, new_name = extract_sktt(file_path, use_name, use_passport)
        elif doc_type == "EVLN":
            data, new_name = extract_evln(file_path, use_name, use_passport)
        elif doc_type == "ITAS":
            data, new_name = extract_itas(file_path, use_name, use_passport)
        elif doc_type == "ITK":
            data, new_name = extract_itk(file_path, use_name, use_passport)
        elif doc_type == "Notifikasi":
            data, new_name = extract_notifikasi(file_path, use_name, use_passport)
        else:
            continue

        extracted_data.append(data)
        new_path = os.path.join(temp_dir, new_name)
        os.rename(file_path, new_path)
        renamed_files[file_name] = {"new_name": new_name}

    df = pd.DataFrame(extracted_data)
    excel_path = os.path.join(temp_dir, "Hasil_Ekstraksi.xlsx")
    df.to_excel(excel_path, index=False)

    zip_path = shutil.make_archive(os.path.join(temp_dir, "Renamed_Files"), "zip", temp_dir)

    return df, excel_path, renamed_files, zip_path, temp_dir
