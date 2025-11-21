import csv
import random
from datetime import datetime, timedelta

from service.exctract.scheame import DataSchema


# ===== Вспомогательные функции =====

def random_phone() -> str:
    """Случайный номер телефона."""
    return f"+79{random.randint(100000000, 999999999)}"


def random_pan_tail() -> str:
    """Хвост карты (4 цифры)."""
    return f"{random.randint(1000, 9999)}"


def random_city() -> str:
    """Рандомный город для операции по карте."""
    return random.choice(["Moscow", "Saint Petersburg", "Kazan",])


def generate_ids(count: int, start: int = 163005250300000) -> list[str]:
    """Генерирует последовательность ID."""
    ids = []
    current = start
    for _ in range(count):
        current += random.randint(50, 1000)
        ids.append(f"C{current}")
    return ids


def parse_time(ts: str) -> datetime:
    """Парсинг ISO-строки из CSV."""
    return datetime.strptime(ts, "%Y-%m-%dT%H:%M:%S.%fZ")


# ===== Загрузка CSV =====

def load_csv_raw(file_path: str, encoding: str = "utf-8") -> list[dict]:
    """Загружает CSV в список словарей."""
    data = []
    with open(file_path, "r", encoding=encoding, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            clean_row = {k.strip(): v.strip() if isinstance(v, str) else v for k, v in row.items()}
            data.append(clean_row)
    # сортируем по дате
    data.sort(key=lambda r: parse_time(r["Creation Time"]))
    return data


# ===== Генерация описания операций =====

def make_operations(data: list[dict]) -> list[dict]:
    """Формирует список операций для PDF."""
    ids = generate_ids(len(data))
    out = []

    for idx, i in enumerate(data):
        dt = parse_time(i['Creation Time'])
        formatted = dt.strftime("%d.%m.%Y")
        ad_type = i['Ad Type'].upper()
        amount = float(i["Fiat Amount"])

        # --- определяем тип операции ---
        if ad_type == 'PURCHASE':  # доход
            sign = '+'
            gray = True
            desc = f'Перевод {ids[idx]} через Систему быстрых платежей\nна {random_phone()}. Без НДС.'

        elif ad_type == 'SALE':  # расход (основной)
            sign = '-'
            gray = False
            desc = f'Перевод {ids[idx]} через Систему быстрых платежей\nна {random_phone()}. Без НДС.'

        elif ad_type == 'CARD_PURCHASE':  # трата по карте
            sign = '-'
            gray = False
            desc = (
                f'Операция по карте: 220015++++++{random_pan_tail()}, \n'
                f'на сумму: {amount:.2f} RUR, дата совершения операции: {dt.strftime("%d.%m.%y")}, '
                f'место совершения операции: 57005136\\RU\\{random_city()}\\Отлично'
            )

        elif ad_type == 'CARD_TOPUP':  # пополнение картой
            sign = '+'
            gray = True
            desc = (
                f'Операция по карте: 220015++++++{random_pan_tail()}, \n'
                f'на сумму: {amount:.2f} RUR, дата совершения операции: {dt.strftime("%d.%m.%y")}'
            )

        else:
            continue

        out.append({
            "date": formatted,
            "code": ids[idx],
            "desc": desc,
            "amount": f"{sign} {amount:.2f}",
            "gray": gray,
        })

    return out


# ===== Основная логика =====

def get_params(data_schema: DataSchema, file_path) -> tuple[dict, list[dict], dict, list[dict]]:
    """
    Генерирует две выписки:
      1. Alpha — часть операций (банковские переводы / покупки)
      2. Tink  — другая часть (оплаты услуг и переводы)
    Обе имеют свои балансы и шапки.
    """
    data = load_csv_raw(file_path)
    if not data:
        raise ValueError("Файл p2p.csv пуст")

    # === базовые суммы и даты ===
    times = [parse_time(r["Creation Time"]) for r in data]
    start_date, end_date = min(times), max(times)

    income_total = sum(float(r["Fiat Amount"]) for r in data if r["Ad Type"].upper() == "PURCHASE")
    expense_total = sum(float(r["Fiat Amount"]) for r in data if r["Ad Type"].upper() == "SALE")
    balance_in_total = random.uniform(20000, 150000)
    balance_out_total = balance_in_total + income_total - expense_total

    # сортировка после вставок
    data.sort(key=lambda r: parse_time(r["Creation Time"]))

    # === РАЗДЕЛЕНИЕ НА ДВЕ ВЫПИСКИ ===
    alpha_rows, tink_rows = [], []
    for row in data:
        if random.random() < 0.5:
            alpha_rows.append(row)
        else:
            tink_rows.append(row)

    # гарантируем, что обе не пустые
    if not alpha_rows:
        alpha_rows.append(tink_rows.pop())
    elif not tink_rows:
        tink_rows.append(alpha_rows.pop())

    # === ДОРАБОТКА ВРЕМЕН ===
    def mutate_times(rows: list[dict]) -> list[dict]:
        new_rows = []
        for r in rows:
            dt = parse_time(r["Creation Time"])
            dt_op = dt + timedelta(minutes=random.randint(2, 7))
            dt_spis = dt_op + timedelta(seconds=random.randint(20, 76))
            new_rows.append({
                **r,
                "Operation Time": dt_op.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                "WriteOff Time": dt_spis.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            })
        return new_rows

    alpha_rows = mutate_times(alpha_rows)
    tink_rows = mutate_times(tink_rows)

    # === ПЕРЕСЧЁТ СУММ И БАЛАНСОВ ===

    def calc_balances(rows: list[dict], name: str) -> dict:
        inc = sum(float(r["Fiat Amount"]) for r in rows if r["Ad Type"].upper() == "PURCHASE" or "TOPUP" in r["Ad Type"].upper())
        exp = sum(float(r["Fiat Amount"]) for r in rows if r["Ad Type"].upper() in ("SALE", "CARD_PURCHASE"))
        bal_in = random.uniform(10000, 80000)
        bal_out = bal_in + inc - exp
        if bal_out < 0:
            bal_out = abs(bal_out) + random.uniform(1000, 5000)
        return {
            "account": f"4082081010997000{name[-2:].upper()}",
            "date_open": data_schema.alpha.date_open,
            "currency": "RUR",
            "type": "Текущий счёт",
            "report_date": data_schema.alpha.report_date,
            "client": data_schema.alpha.client,
            "address": data_schema.alpha.address,
            "period": f"За период с {start_date.strftime('%d.%m.%Y')} по {end_date.strftime('%d.%m.%Y')}",
            "balance_in": f"{bal_in:,.2f} RUR".replace(",", " "),
            "income": f"{inc:,.2f} RUR".replace(",", " "),
            "expense": f"{exp:,.2f} RUR".replace(",", " "),
            "balance_out": f"{bal_out:,.2f} RUR".replace(",", " "),
            "limit": f"{bal_out:,.2f} RUR".replace(",", " "),
            "balance_now": f"{bal_out:,.2f} RUR".replace(",", " "),
        }

    header_alpha = calc_balances(alpha_rows, "Alpha")
    header_tink = calc_balances(tink_rows, "Tink")

    # === ПОЛЯ ДЛЯ TINK ===
    tink_min_date = min(parse_time(r["Operation Time"]) for r in tink_rows)
    tink_max_date = max(parse_time(r["Operation Time"]) for r in tink_rows)
    isx_number = f"№ {random.getrandbits(32):08x}"

    header_tink.update({
        "isx": isx_number,
        "date": datetime.now().strftime("%d.%m.%Y"),
        "fio": data_schema.tink.fio,
        "series": data_schema.tink.series,
        "number": data_schema.tink.number,
        "date_issue": data_schema.tink.date_issue,
        "code": data_schema.tink.code,
        "issued_by": data_schema.tink.issued_by,
        "address": data_schema.tink.address,
        "contract_date": data_schema.tink.contract_date,
        "account_number": header_tink["account"],
        "contract_number": data_schema.tink.contract_number,
        "period": f"Движение средств за период с {tink_min_date.strftime('%d.%m.%Y')} по {tink_max_date.strftime('%d.%m.%Y')}",
    })

    # === ГЕНЕРАЦИЯ ОПИСАНИЙ TINK ===

    def make_tink_operations(rows: list[dict]) -> list[dict]:
        out = []
        ids = generate_ids(len(rows))
        for idx, r in enumerate(rows):
            dt_op = parse_time(r["Operation Time"])
            dt_spis = parse_time(r["WriteOff Time"])
            ad_type = r["Ad Type"].upper()
            amount = float(r["Fiat Amount"])

            if ad_type in ("PURCHASE", "CARD_TOPUP"):
                sign = "+"
                desc = "Пополнение. Система\n быстрых платежей"
            else:
                sign = "-"
                desc = "Перевод. Система\n быстрых платежей"

            amount_str = f"{sign} {amount:,.2f} ₽".replace(",", " ")

            out.append({
                "Дата и время операции": f'{dt_op.strftime("%d.%m.%Y")}\n{dt_op.strftime("%H:%M")}',
                "Дата списания": f'{dt_spis.strftime("%d.%m.%Y")}\n{dt_spis.strftime("%H:%M")}',
                "Сумма в валюте операции": amount_str,
                "Сумма операции в валюте карты": amount_str,
                "Описание операции": desc,
                "Номер карты": data_schema.tink.card_number,
                "code": ids[idx],
            })
        return out

    operations_alpha = make_operations(alpha_rows)
    operations_tink = make_tink_operations(tink_rows)

    return header_alpha, operations_alpha, header_tink, operations_tink
