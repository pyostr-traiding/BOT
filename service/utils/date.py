import datetime


def format_datetime(iso_str: str) -> str:
    # Разбираем ISO-дату
    dt = datetime.datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
    # Возвращаем в формате ДД.ММ.ГГ ЧЧ:ММ:СС
    return dt.strftime("%d.%m.%y %H:%M:%S")