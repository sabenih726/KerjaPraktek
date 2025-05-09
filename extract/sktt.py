import re
import fitz
from utils.text_cleaning import clean_text
from utils.date_utils import format_date

def extract_sktt(file_path, use_name, use_passport):
    text = extract_text(file_path)

    name = re.search(r"Nama.*?:\s*(.+)", text)
    passport = re.search(r"No\\.? Paspor.*?:\s*(\S+)", text)
    validity = re.search(r"Berlaku.*?:\s*(\d{2}.\d{2}.\d{4})", text)

    data = {
        "Jenis Dokumen": "SKTT",
        "Nama": name.group(1).strip() if name else "",
        "Paspor": passport.group(1).strip() if passport else "",
        "Berlaku Sampai": format_date(validity.group(1)) if validity else "",
    }
    return data, generate_filename("SKTT", data, use_name, use_passport)

def extract_text(file_path):
    text = ""
    with fitz.open(file_path) as doc:
        for page in doc:
            text += page.get_text()
    return clean_text(text)

def generate_filename(prefix, data, use_name, use_passport):
    from datetime import datetime
    parts = [prefix]
    if use_name:
        parts.append(data["Nama"].replace(" ", "_"))
    if use_passport:
        parts.append(data["Paspor"])
    parts.append(datetime.now().strftime("%Y%m%d"))
    return "_".join(parts) + ".pdf"
