import uuid

import fitz  # PyMuPDF
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import io

from service.exctract.read_csv import get_params
from service.exctract.scheame import DataSchema, AlphaSchema, TinkSchema
import os

# === База директории ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# === Шрифты ===
font_path = os.path.join(BASE_DIR, "fonts/tink", "TinkoffSans-Regular.ttf")
font_path_bold = os.path.join(BASE_DIR, "fonts/tink", "TinkoffSans-Medium.ttf")

pdfmetrics.registerFont(TTFont("DejaVu", font_path))
dejavu_font = fitz.Font(fontfile=font_path)

# === Параметры шаблона ===
TEMPLATE_PATH_ALPHA = os.path.join(
    BASE_DIR, "alpha", "Выписка_по_счёту_чистый_header.pdf"
)

OUTPUT_PATH_ALPHA = os.path.join(
    BASE_DIR, "alpha", "выписка_новая.pdf"
)

# === Tink шрифты ===
TINK_FONT = font_path
TINK_FONT_NAME = "TINK"

TINK_FONT_BOLD = font_path_bold
TINK_FONT_BOLD_NANE = "TINK-bold"

TEST = False

HEADER_COORDS = {
    "account": (155, 172),
    "date_open": (155, 182),
    "currency": (155, 193),
    "type": (155, 205),
    "report_date": (155, 216),
    "client": (155, 240),
    "address": (155, 253),
    "period": (311, 163),
    "balance_in": (567, 180),
    "income": (567, 197),
    "expense": (567, 213),
    "balance_out": (567, 231),
    "limit": (567, 248),
    "balance_now": (567, 287),
}


X_DATE, X_CODE, X_DESC, X_AMT = 27, 100, 190, 565
Y_START_FIRST, Y_START_NEXT = 442, 700
ROW_GAP, DESC_MAX_WIDTH = 8, 360
ROWS_FIRST, ROWS_NEXT = 9, 17


# === Универсальная функция отрисовки альфа ===
def render_alpha_pdf(header_data: dict, operations: list[dict],
                     template_path: str = TEMPLATE_PATH_ALPHA,
                     output_path: str = OUTPUT_PATH_ALPHA):
    """
    Отрисовывает PDF-выписку Alpha на основе шаблона и переданных данных.
    """
    template = fitz.open(template_path)
    result = fitz.open()
    if TEST:
        output_path = os.path.join(
            BASE_DIR, "alpha", f"выписка_альфа_выход.pdf"
        )
    else:
        unique_id = uuid.uuid4().hex
        output_path = os.path.join(
            BASE_DIR, "alpha", f"выписка_альфа_{unique_id}.pdf"
        )
    # разбиваем операции на страницы
    chunks = [operations[:ROWS_FIRST]]
    for i in range(ROWS_FIRST, len(operations), ROWS_NEXT):
        chunks.append(operations[i:i + ROWS_NEXT])

    for idx, chunk in enumerate(chunks):
        page = result.new_page(width=A4[0], height=A4[1])
        page.show_pdf_page(page.rect, template, 0 if idx == 0 else 1)

        # === ШАПКА ===
        if idx == 0:
            for key, (x, y) in HEADER_COORDS.items():
                if key in header_data:
                    txt = str(header_data[key])

                    # 🔹 если вдруг пришло "ОУФМС ... \\nобл. ..." — превратим в реальный перенос строки
                    print(txt)
                    txt = txt.replace("\\n", "\n")
                    print(txt)
                    fontsize, color = 7, (0, 0, 0)
                    if key in ["address", "period"]:
                        page.insert_textbox(
                            fitz.Rect(x, y - 5, x + 250, y + 40),
                            txt,
                            fontsize=fontsize,
                            fontfile=font_path,
                            fontname="DejaVu",
                            color=color,
                            align=0
                        )
                    elif key in ["balance_in", "income", "expense",
                                 "balance_out", "limit", "balance_now"]:
                        page.insert_textbox(
                            fitz.Rect(x - 80, y - 5, x, y + 10),
                            txt,
                            fontsize=fontsize,
                            fontfile=font_path,
                            fontname="DejaVu",
                            color=color,
                            align=2
                        )
                    else:
                        page.insert_textbox(
                            fitz.Rect(x, y - 5, x + 200, y + 10),
                            txt,
                            fontsize=fontsize,
                            fontfile=font_path,
                            fontname="DejaVu",
                            color=color,
                            align=0
                        )

        # === ТАБЛИЦА ===
        packet = io.BytesIO()
        c = canvas.Canvas(packet, pagesize=A4)
        y = Y_START_FIRST if idx == 0 else Y_START_NEXT

        for op in chunk:
            x_min, x_max = 25, 570
            font_name, font_size = "DejaVu", 8
            max_width = DESC_MAX_WIDTH

            # переносы строк
            raw_desc = op["desc"].replace("\r", "")
            paragraphs = raw_desc.split("\n")
            lines = []
            dummy = canvas.Canvas(io.BytesIO())
            for p in paragraphs:
                words = p.split(" ")
                line = ""
                for w in words:
                    t = (line + " " + w).strip()
                    if dummy.stringWidth(t, font_name, font_size) <= max_width:
                        line = t
                    else:
                        if line:
                            lines.append(line)
                        line = w
                if line:
                    lines.append(line)

            line_h = 10
            pad_top = 3
            text_h = len(lines) * line_h
            block_h = text_h + pad_top

            y_top = y
            y_bottom = y_top - block_h

            # фон для "gray" операций
            if op.get("gray", False):
                c.setFillColorRGB(0.93, 0.93, 0.93)
                c.rect(x_min, y_bottom - 0.6, x_max - x_min,
                       block_h + 8.6, stroke=0, fill=1)

            # текст
            c.setFillColor(colors.black)
            c.setFont(font_name, font_size)
            text_y = y_top - pad_top
            c.drawString(X_DATE, text_y, op["date"])
            c.drawString(X_CODE, text_y, op["code"])
            c.drawRightString(X_AMT, text_y, op["amount"])

            dy = text_y
            for ln in lines:
                c.drawString(X_DESC, dy, ln)
                dy -= line_h

            # разделитель
            c.setStrokeColor(colors.lightgrey)
            c.setLineWidth(0.5)
            c.line(x_min, y_bottom, x_max, y_bottom)

            y = y_bottom - ROW_GAP

        # Номер страницы
        c.setFont("DejaVu", 8)
        c.drawRightString(573, 25, f"Страница {idx + 1} из {len(chunks)}")
        c.save()

        overlay = fitz.open("pdf", packet.getvalue())
        page.show_pdf_page(page.rect, overlay, 0)

    result.save(output_path)
    print(f"✅ PDF для ALPHA готов: {output_path}")

    return output_path


# === Заглушка для второй выписки (TINK) ===
def render_tink_pdf(
        header_tink: dict,
        operations_tink: list[dict],
        template_path: str = None,
        output_path: str = None,
        base_path: str = None
):
    """
    Отрисовывает PDF-выписку Tink в шаблон tink_clear.pdf.
    Добавляет итоговую страницу из чистой версии (tink_clear.pdf).
    """

    # === Абсолютные пути по умолчанию ===
    if template_path is None:
        template_path = os.path.join(BASE_DIR, "tink", "tink_clear.pdf")

    if output_path is None:
        unique_id = uuid.uuid4().hex
        output_path = os.path.join(BASE_DIR, "tink", f"выписка_тинк_{unique_id}.pdf")

    if base_path is None:
        base_path = os.path.join(BASE_DIR, "tink", "tink_base.pdf")

    pdfmetrics.registerFont(TTFont(TINK_FONT_NAME, TINK_FONT))
    if TEST:
        output_path = os.path.join(
            BASE_DIR, "tink", f"выписка_тинк_выход.pdf"
        )
    else:
        unique_id = uuid.uuid4().hex
        output_path = os.path.join(
            BASE_DIR, "tink", f"выписка_тинк_{unique_id}.pdf"
        )

    template = fitz.open(template_path)
    result = fitz.open()

    # === координаты шапки (можно будет подправить под макет) ===
    HEADER_COORDS_TINK = {
        "isx": {
            "pos": (76.6, 122.4),
            "font": TINK_FONT_BOLD_NANE,
            "size": 8.5,
            "bold": False,
        },

        "date": {
            "pos": (490, 122.4),
            "font": TINK_FONT,
            "size": 8.5,
            "bold": False,
        },
        "fio": {
            "pos": (56.265, 145),
            "font": TINK_FONT,
            "size": 8.5,
            "bold": True,
        },

        "series": {
            "pos": (87, 181),
            "font": TINK_FONT,
            "size": 8,
            "bold": False,
        },
        "number": {
            "pos": (210, 181),
            "font": TINK_FONT,
            "size": 8,
            "bold": False,
        },
        "date_issue": {
            "pos": (352, 181),
            "font": TINK_FONT,
            "size": 8,
            "bold": False,
        },
        "code": {
            "pos": (500, 181),
            "font": TINK_FONT,
            "size": 8,
            "bold": False,
        },
        "issued_by": {
            "pos": (125, 199),
            "font": TINK_FONT,
            "size": 8,
            "bold": False,
        },
        "address": {
            "pos": (140, 217),
            "font": TINK_FONT,
            "size": 8,
            "bold": False,
        },



        "contract_date": {
            "pos": (170, 266),
            "font": TINK_FONT,
            "size": 8,
            "bold": False,
        },
        "account_number": {
            "pos": (128, 284),
            "font": TINK_FONT,
            "size": 8,
            "bold": False,
        },
        "contract_number": {
            "pos": (152, 302),
            "font": TINK_FONT,
            "size": 8,
            "bold": False,
        },

        "period": {
            "pos": (56.3, 322),
            "font": TINK_FONT_BOLD,
            "size": 12,
            "bold": False,
        },
    }

    # === параметры таблицы ===
    X_OP_TIME = 55.88
    X_WRITE_OFF = 125
    X_SUM_OP = 198
    X_SUM_CARD = 293
    X_DESC = 389
    X_CARD = 500

    Y_START_FIRST, Y_START_NEXT = 463, 795
    ROW_H = 18
    ROWS_FIRST, ROWS_NEXT = 14, 25
    FONT_NAME, FONT_SIZE = "TINK", 9

    # === Разбиваем операции на страницы ===
    chunks = [operations_tink[:ROWS_FIRST]]
    for i in range(ROWS_FIRST, len(operations_tink), ROWS_NEXT):
        chunks.append(operations_tink[i:i + ROWS_NEXT])

    total_in = 0.0
    total_out = 0.0

    for idx, chunk in enumerate(chunks):
        page = result.new_page(width=A4[0], height=A4[1])
        page.show_pdf_page(page.rect, template, 0 if idx == 0 else 1)

        # === Отрисовка шапки (только на первой странице) ===
        if idx == 0:
            for key, cfg in HEADER_COORDS_TINK.items():
                if key in header_tink:
                    txt = header_tink[key]
                    x, y = cfg["pos"]
                    size = cfg.get("size", 9)
                    bold = cfg.get("bold", False)

                    # если жирный — другой файл и другое имя
                    if bold:
                        font_file = TINK_FONT_BOLD
                        font_name = TINK_FONT_BOLD_NANE
                    else:
                        font_file = TINK_FONT
                        font_name = TINK_FONT_NAME

                    page.insert_textbox(
                        fitz.Rect(x, y - 5, x + 300, y + 15),
                        txt,
                        fontsize=size,
                        fontfile=font_file,
                        fontname=font_name,
                        color=(0, 0, 0),
                        align=0
                    )

        # === Таблица ===
        packet = io.BytesIO()
        c = canvas.Canvas(packet, pagesize=A4)
        c.setFont(FONT_NAME, FONT_SIZE)

        y = Y_START_FIRST if idx == 0 else Y_START_NEXT - 10

        for op in chunk:
            op_time = op["Дата и время операции"]
            write_off = op["Дата списания"]
            sum_op = op["Сумма в валюте операции"]
            sum_card = op["Сумма операции в валюте карты"]
            desc = op["Описание операции"]
            card = op["Номер карты"]

            # учёт суммы
            value = float(sum_op.replace("₽", "").replace(" ", "").replace(",", "."))
            if "-" in sum_op:
                total_out += abs(value)
            else:
                total_in += value

            op_time_lines = op_time.split("\n")
            write_off_lines = write_off.split("\n")

            # перенос описания
            desc_lines = []
            words = desc.split(" ")
            line = ""
            max_width = 100
            dummy = canvas.Canvas(io.BytesIO())
            for w in words:
                t = (line + " " + w).strip()
                if dummy.stringWidth(t, FONT_NAME, FONT_SIZE) <= max_width:
                    line = t
                else:
                    if line:
                        desc_lines.append(line)
                    line = w
            if line:
                desc_lines.append(line)

            max_lines = max(len(op_time_lines), len(write_off_lines), len(desc_lines))
            block_height = max_lines * (ROW_H / 1.6)

            text_y = y
            for i_line in range(max_lines):
                t_y = text_y - i_line * (ROW_H / 1.6)
                c.setFillColorRGB(0.05, 0.05, 0.05)
                if i_line < len(op_time_lines):
                    c.drawString(X_OP_TIME, t_y, op_time_lines[i_line])
                if i_line < len(write_off_lines):
                    c.drawString(X_WRITE_OFF, t_y, write_off_lines[i_line])
                # вывод сумм (чуть ниже: -3 px)
                if i_line == 0:
                    px = 4.9
                    c.drawString(X_SUM_OP, t_y - px, sum_op)
                    c.drawString(X_SUM_CARD, t_y - px, sum_card)
                    c.drawString(X_CARD, t_y, card)
                if i_line < len(desc_lines):
                    c.drawString(X_DESC, t_y, desc_lines[i_line])

            # линия-разделитель
            y -= block_height

            top_padding = 7  # был 3, стало 4 (или больше)
            c.setStrokeColor('#171717')
            c.setLineWidth(1)
            c.line(X_OP_TIME, y + top_padding, 539.1, y + top_padding)

            bottom_padding = 4
            y -= bottom_padding

        c.setFont(FONT_NAME, 8)
        c.drawRightString(570, 25, f"Страница {idx + 1} из {len(chunks) + 1}")
        c.save()

        overlay = fitz.open("pdf", packet.getvalue())
        page.show_pdf_page(page.rect, overlay, 0)

    # === ДОБАВЛЯЕМ ПОСЛЕДНЮЮ СТРАНИЦУ ===
    clean = fitz.open(template_path)
    result.insert_pdf(clean, from_page=2, to_page=2)
    last_page = result[-1]

    text_in = f"{total_in:,.2f} Р".replace(",", " ")
    text_out = f"{total_out:,.2f} Р".replace(",", " ")
    last_page.insert_text((120, 31), text_in, fontsize=9, fontfile=TINK_FONT,
                          fontname=TINK_FONT_NAME, color=(0, 0, 0))
    last_page.insert_text((120, 46), text_out, fontsize=9, fontfile=TINK_FONT,
                          fontname=TINK_FONT_NAME, color=(0, 0, 0))

    result.save(output_path)
    print(f"✅ PDF для TINK готов: {output_path}")

    return output_path


# data = DataSchema(
#     alpha=AlphaSchema(
#         date_open='10.10.2025',
#         report_date='10.10.2025',
#         client='Наебалов Биржов Мошенников',
#         address='ОУФМС России по Челябинской \\n обл. в г. Челябинске'),
#     tink=TinkSchema(
#         date='10.10.2025',
#         fio='Наебалов Биржов Мошенников',
#         series='4020',
#         number='720140',
#         date_issue='10.10.2025',
#         code='102-321',
#         issued_by='ОУФМС России по Челябинской обл. в г. Челябинске',
#         address='ОУФМС России по Челябинской обл. в г. Челябинске',
#         contract_date='01.01.2000',
#         contract_number='HK2371-2394F',
#         card_number='1234'
#     )
# )
#
# header_alpha, operations_alpha, header_tink, operations_tink = get_params(
#         data_schema=data,
#         file_path='p2p.csv'
#     )
#
# # path_alpha = render_alpha_pdf(header_alpha, operations_alpha)
# path_tink = render_tink_pdf(header_tink, operations_tink)