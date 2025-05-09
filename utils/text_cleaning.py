def clean_text(text):
    return text.replace("\n", " ").replace("\xa0", " ").strip()

def split_birth_place_date(raw_text):
    import re
    match = re.match(r"(.+),\s*(\d{2}-\d{2}-\d{4})", raw_text)
    return (match.group(1), match.group(2)) if match else ("", "")
