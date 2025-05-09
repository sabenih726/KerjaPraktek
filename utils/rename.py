import os
import re

def clean_filename(value):
    """Hilangkan karakter ilegal dari nama file."""
    value = re.sub(r"[\\/*?\"<>|]", "_", value)
    return value.strip().replace(" ", "_")

def generate_new_filename(original_name, data, use_name=False, use_passport=False):
    """Buat nama file baru berdasarkan opsi nama dan paspor."""
    base_name = os.path.splitext(original_name)[0]

    # Ambil nama atau paspor dari data, per dokumen
    name = data.get("Name") or data.get("Nama TKA") or ""
    passport = data.get("Passport No") or data.get("Passport Number") or data.get("Nomor Paspor") or ""

    parts = []
    if use_name and name:
        parts.append(clean_filename(name))
    if use_passport and passport:
        parts.append(clean_filename(passport))

    if parts:
        new_name = "_".join(parts) + ".pdf"
    else:
        new_name = base_name + ".pdf"

    return new_name
