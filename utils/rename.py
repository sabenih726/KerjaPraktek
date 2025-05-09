import os
import re

def clean_filename(value):
    value = re.sub(r"[\\/*?\"<>|]", "_", value)
    return value.strip().replace(" ", "_")

def rename_file(original_name, data, use_name, use_passport):
    base_name = os.path.splitext(original_name)[0]

    name = data.get("Name") or data.get("Nama TKA") or ""
    passport = data.get("Passport No") or data.get("Passport Number") or data.get("Nomor Paspor") or ""

    parts = []
    if use_name and name:
        parts.append(clean_filename(name))
    if use_passport and passport:
        parts.append(clean_filename(passport))

    return "_".join(parts).strip("_") + ".pdf" if parts else base_name + ".pdf"
