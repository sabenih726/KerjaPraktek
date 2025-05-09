import re
from utils.date_utils import format_date

def extract_notifikasi(text: str) -> dict:
    data = {
        "Nomor Keputusan": "",
        "Nama TKA": "",
        "Tempat/Tanggal Lahir": "",
        "Kewarganegaraan": "",
        "Alamat Tempat Tinggal": "",
        "Nomor Paspor": "",
        "Jabatan": "",
        "Lokasi Kerja": "",
        "Berlaku": "",
        "Jenis Dokumen": "Notifikasi"
    }

    def find(pattern: str) -> str:
        match = re.search(pattern, text, re.IGNORECASE)
        return match.group(1).strip() if match else ""

    # Nomor Keputusan
    nomor_keputusan_match = re.search(r"NOMOR\s+([A-Z0-9./-]+)", text, re.IGNORECASE)
    data["Nomor Keputusan"] = nomor_keputusan_match.group(1).strip() if nomor_keputusan_match else ""

    # Field lainnya
    data["Nama TKA"] = find(r"Nama TKA\s*:\s*(.*)")
    data["Tempat/Tanggal Lahir"] = find(r"Tempat/Tanggal Lahir\s*:\s*(.*)")
    data["Kewarganegaraan"] = find(r"Kewarganegaraan\s*:\s*(.*)")
    data["Alamat Tempat Tinggal"] = find(r"Alamat Tempat Tinggal\s*:\s*(.*)")
    data["Nomor Paspor"] = find(r"Nomor Paspor\s*:\s*(.*)")
    data["Jabatan"] = find(r"Jabatan\s*:\s*(.*)")
    data["Lokasi Kerja"] = find(r"Lokasi Kerja\s*:\s*(.*)")

    # Tanggal Berlaku
    valid_match = re.search(
        r"Berlaku\s*:?\s*(\d{2}[-/]\d{2}[-/]\d{4})\s*(?:s\.?d\.?|sampai dengan)?\s*(\d{2}[-/]\d{2}[-/]\d{4})",
        text, re.IGNORECASE
    )
    if not valid_match:
        valid_match = re.search(
            r"Tanggal Berlaku\s*:?\s*(\d{2}[-/]\d{2}[-/]\d{4})\s*s\.?d\.?\s*(\d{2}[-/]\d{2}[-/]\d{4})",
            text, re.IGNORECASE
        )

    if valid_match:
        start_date = format_date(valid_match.group(1))
        end_date = format_date(valid_match.group(2))
        data["Berlaku"] = f"{start_date} - {end_date}"

    return data
