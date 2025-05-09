import re
import fitz
from utils.text_cleaning import clean_text
from utils.date_utils import format_date

def extract_evln(text: str) -> dict:
    data = {
        "Name": "",
        "Place of Birth": "",
        "Date of Birth": "",
        "Passport No": "",
        "Passport Expiry": "",
        "Jenis Dokumen": "EVLN"
    }

    for line in text.split("\n"):
        line = line.strip()
        if re.search(r"(?i)\bName\b|\bNama\b", line):
            parts = line.split(":")
            if len(parts) > 1:
                data["Name"] = clean_text(parts[1])

        elif re.search(r"(?i)\bPlace of Birth\b|\bTempat Lahir\b", line):
            parts = line.split(":")
            if len(parts) > 1:
                data["Place of Birth"] = clean_text(parts[1], is_name_or_pob=True)

        elif re.search(r"(?i)\bDate of Birth\b|\bTanggal Lahir\b", line):
            match = re.search(r"(\d{2}[/-]\d{2}[/-]\d{4})", line)
            if match:
                data["Date of Birth"] = format_date(match.group(1))

        elif re.search(r"(?i)\bPassport No\b", line):
            match = re.search(r"\b([A-Z0-9]+)\b", line)
            if match:
                data["Passport No"] = match.group(1)

        elif re.search(r"(?i)\bPassport Expiry\b", line):
            match = re.search(r"(\d{2}[/-]\d{2}[/-]\d{4})", line)
            if match:
                data["Passport Expiry"] = format_date(match.group(1))

    return data
