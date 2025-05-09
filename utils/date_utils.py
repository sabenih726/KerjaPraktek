from datetime import datetime

def format_date(date_str):
    try:
        return datetime.strptime(date_str, "%d.%m.%Y").strftime("%Y-%m-%d")
    except:
        return date_str
