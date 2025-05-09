def clean_text(text, is_name_or_pob=False):
    if is_name_or_pob:
        text = text.strip().title()
    else:
        text = text.strip()
    return text
