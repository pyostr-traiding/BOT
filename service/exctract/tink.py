import os
import io
import uuid

import fitz  # PyMuPDF
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from service.exctract.read_csv import get_params
from service.exctract.scheame import DataSchema, AlphaSchema, TinkSchema


# ============================================================================
# === Пути ===
# ============================================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

font_path_regular = os.path.abspath(os.path.join(BASE_DIR, "fonts/tink", "TinkoffSans-Regular.ttf"))
font_path_bold    = os.path.abspath(os.path.join(BASE_DIR, "fonts/tink", "TinkoffSans-Medium.ttf"))
font_path_symbola = os.path.abspath(os.path.join(BASE_DIR, "fonts", "Symbola.ttf"))


# === Шаблоны Alpha ===
TEMPLATE_PATH_ALPHA = os.path.join(BASE_DIR, "alpha", "Выписка_по_счёту_чистый_header.pdf")


TEST = True


# ============================================================================
# === ReportLab — регистрация шрифтов
# ============================================================================

pdfmetrics.registerFont(TTFont("TINK", font_path_regular))
pdfmetrics.registerFont(TTFont("TINK-BOLD", font_path_bold))
pdfmetrics.registerFont(TTFont("Symb", font_path_symbola))


# ============================================================================
# === PyMuPDF — регистрация шрифтов внутри PDF
# ============================================================================
def normalize_font(f):
    if isinstance(f, (list, tuple)):
        return f[0]
    return f

def init_fonts_for_doc(doc: fitz.Document):

    # создаём страницу, которая останется
    if doc.page_count == 0:
        page = doc.new_page()
    else:
        page = doc[0]

    def load_font(path):
        path = os.path.abspath(path)  # <<<<<< ВАЖНО
        fid = page.insert_font(fontfile=path)
        return f"F{fid}"

    t_reg  = load_font(font_path_regular)
    t_bold = load_font(font_path_bold)
    symb   = load_font(font_path_symbola)

    print("REGISTERED:", t_reg, t_bold, symb)
    return t_reg, t_bold, symb






# ============================================================================
# === ReportLab версия Отрисовки ₽
# ============================================================================

def draw_with_ruble(c, x, y, text, main_font="TINK", main_size=9):
    cursor_x = x
    for ch in text:
        if ch == "₽":
            c.setFont("Symb", main_size)
            w = c.stringWidth(ch, "Symb", main_size)
            c.drawString(cursor_x, y, ch)
        else:
            c.setFont(main_font, main_size)
            w = c.stringWidth(ch, main_font, main_size)
            c.drawString(cursor_x, y, ch)
        cursor_x += w


# ============================================================================
# === PyMuPDF версия ₽
# ============================================================================

def draw_with_ruble_fitz(page, x, y, text, size, tink_reg, symb):
    cursor_x = x

    for ch in text:
        if ch == "₽":
            page.insert_text(
                (cursor_x, y),
                ch,
                fontsize=size,
                fontname=symb,
                color=(0, 0, 0)
            )
            w = page.get_text_length(ch, fontsize=size, fontname=symb)
        else:
            page.insert_text(
                (cursor_x, y),
                ch,
                fontsize=size,
                fontname=tink_reg,
                color=(0, 0, 0)
            )
            w = page.get_text_length(ch, fontsize=size, fontname=tink_reg)

        cursor_x += w



# ============================================================================
# === Координаты Alpha ===
# ============================================================================

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


# ============================================================================
# === Основная функция Alpha PDF ===
# ============================================================================

def render_alpha_pdf(header_data: dict, operations: list[dict],
                     template_path: str = TEMPLATE_PATH_ALPHA,
                     output_path: str = None):

    template = fitz.open(template_path)
    result = fitz.open()

    tink_reg, tink_bold, symb = init_fonts_for_doc(result)

    if output_path is None:
        if TEST:
            output_path = os.path.join(BASE_DIR, "alpha", "выписка_альфа_выход.pdf")
        else:
            output_path = os.path.join(
                BASE_DIR, "alpha", f"выписка_альфа_{uuid.uuid4().hex}.pdf"
            )

    chunks = [operations[:ROWS_FIRST]]
    for i in range(ROWS_FIRST, len(operations), ROWS_NEXT):
        chunks.append(operations[i:i + ROWS_NEXT])

    for page_index, chunk in enumerate(chunks):

        page = result.new_page(width=A4[0], height=A4[1])
        page.show_pdf_page(page.rect, template, 0 if page_index == 0 else 1)

        # === Шапка ===
        if page_index == 0:
            for key, (x, y) in HEADER_COORDS.items():
                if key not in header_data:
                    continue

                txt = str(header_data[key]).replace("\\n", "\n")
                fontsize = 7

                if key in ["address", "period"]:
                    rect = fitz.Rect(x, y - 5, x + 250, y + 40)
                elif key in ["balance_in", "income", "expense",
                             "balance_out", "limit", "balance_now"]:
                    rect = fitz.Rect(x - 80, y - 5, x, y + 10)
                else:
                    rect = fitz.Rect(x, y - 5, x + 200, y + 10)

                page.insert_textbox(
                    rect,
                    txt,
                    fontsize=fontsize,
                    fontname=tink_reg,
                    color=(0, 0, 0),
                    align=0
                )

        # === Таблица ===
        packet = io.BytesIO()
        c = canvas.Canvas(packet, pagesize=A4)

        y = Y_START_FIRST if page_index == 0 else Y_START_NEXT

        for op in chunk:
            font_name = "TINK"
            font_size = 8
            max_width = DESC_MAX_WIDTH

            raw_desc = op["desc"].replace("\r", "")
            paragraphs = raw_desc.split("\n")
            lines = []
            dummy = canvas.Canvas(io.BytesIO())

            for p in paragraphs:
                words = p.split(" ")
                line = ""
                for w in words:
                    test_line = (line + " " + w).strip()
                    if dummy.stringWidth(test_line, font_name, font_size) <= max_width:
                        line = test_line
                    else:
                        if line:
                            lines.append(line)
                        line = w
                if line:
                    lines.append(line)

            line_h = 10
            text_h = len(lines) * line_h
            block_h = text_h + 3

            y_top = y
            y_bottom = y_top - block_h

            if op.get("gray"):
                c.setFillColorRGB(0.93, 0.93, 0.93)
                c.rect(25, y_bottom - 0.6, 545, block_h + 8.6, stroke=0, fill=1)

            text_y = y_top - 3
            c.setFillColor(colors.black)

            c.setFont("TINK", 8)
            c.drawString(X_DATE, text_y, op["date"])
            c.drawString(X_CODE, text_y, op["code"])
            draw_with_ruble(c, X_AMT, text_y, op["amount"], main_size=8)

            dy = text_y
            for ln in lines:
                c.drawString(X_DESC, dy, ln)
                dy -= line_h

            c.setStrokeColor(colors.lightgrey)
            c.setLineWidth(0.5)
            c.line(25, y_bottom, 570, y_bottom)

            y = y_bottom - ROW_GAP

        c.setFont("TINK", 8)
        c.drawRightString(573, 25, f"Страница {page_index + 1} из {len(chunks)}")
        c.save()

        overlay = fitz.open("pdf", packet.getvalue())
        page.show_pdf_page(page.rect, overlay, 0)

    result.save(output_path)
    print(f"✅ Alpha PDF готов: {output_path}")
    return output_path

def render_tink_pdf(
        header_tink: dict,
        operations_tink: list[dict],
        template_path: str = None,
        output_path: str = None,
        base_path: str = None
):
    """
    Отрисовывает PDF-выписку Тинькофф:
    — корректные шрифты (TinkoffSans Regular / Medium)
    — символ ₽ отдельным шрифтом Symbola
    — корректные переносы
    — итоговая страница с суммами
    """

    # === Пути по умолчанию ===
    if template_path is None:
        template_path = os.path.join(BASE_DIR, "tink", "tink_clear.pdf")

    if base_path is None:
        base_path = os.path.join(BASE_DIR, "tink", "tink_base.pdf")

    if output_path is None:
        if TEST:
            output_path = os.path.join(BASE_DIR, "tink", "выписка_тинк_выход.pdf")
        else:
            output_path = os.path.join(BASE_DIR, "tink", f"выписка_тинк_{uuid.uuid4().hex}.pdf")

    # === Открываем шаблон и создаём PDF ===
    template = fitz.open(template_path)
    result = fitz.open()

    # === Регистрируем шрифты в документе ===
    tink_reg, tink_bold, symb = init_fonts_for_doc(result)

    # === Координаты шапки ===
    HEADER_COORDS_TINK = {
        "isx":      {"pos": (76.6, 122.4), "font": tink_bold, "size": 8.5},
        "date":     {"pos": (490, 122.4), "font": tink_reg,  "size": 8.5},
        "fio":      {"pos": (56.265, 145),"font": tink_bold, "size": 9},

        "series":    {"pos": (87, 181),  "font": tink_reg, "size": 8},
        "number":    {"pos": (210, 181), "font": tink_reg, "size": 8},
        "date_issue":{"pos": (352, 181), "font": tink_reg, "size": 8},
        "code":      {"pos": (500, 181), "font": tink_reg, "size": 8},
        "issued_by": {"pos": (125, 199), "font": tink_reg, "size": 8},
        "address":   {"pos": (140, 217), "font": tink_reg, "size": 8},

        "contract_date":   {"pos": (170, 266), "font": tink_reg, "size": 8},
        "account_number":  {"pos": (128, 284), "font": tink_reg, "size": 8},
        "contract_number": {"pos": (152, 302), "font": tink_reg, "size": 8},

        "period":          {"pos": (56.3, 322), "font": tink_bold, "size": 12},
    }

    # === Координаты таблицы ===
    X_OP_TIME = 55.88
    X_WRITE_OFF = 125
    X_SUM_OP = 198
    X_SUM_CARD = 293
    X_DESC = 389
    X_CARD = 500

    Y_START_FIRST, Y_START_NEXT = 463, 795
    ROW_H = 18
    ROWS_FIRST, ROWS_NEXT = 14, 25

    # === Разбиваем операции на страницы ===
    chunks = [operations_tink[:ROWS_FIRST]]
    for i in range(ROWS_FIRST, len(operations_tink), ROWS_NEXT):
        chunks.append(operations_tink[i:i + ROWS_NEXT])

    total_in = 0.0
    total_out = 0.0

    for idx, chunk in enumerate(chunks):

        page = result.new_page(width=A4[0], height=A4[1])
        # 0 — шапка, 1 — чистая страница для последующих
        page.show_pdf_page(page.rect, template, 0 if idx == 0 else 1)

        # === ШАПКА ===
        if idx == 0:
            for key, cfg in HEADER_COORDS_TINK.items():
                if key not in header_tink:
                    continue

                text = header_tink[key]
                x, y = cfg["pos"]
                size = cfg["size"]

                page.insert_text(
                    (x, y),
                    text,
                    fontsize=size,
                    fontname=cfg["font"],
                    color=(0, 0, 0)
                )

        # === Таблица — ReportLab overlay ===
        packet = io.BytesIO()
        c = canvas.Canvas(packet, pagesize=A4)
        c.setFont("TINK", 9)

        y = Y_START_FIRST if idx == 0 else Y_START_NEXT - 10

        for op in chunk:
            op_time = op["Дата и время операции"]
            write_off = op["Дата списания"]
            sum_op = op["Сумма в валюте операции"]
            sum_card = op["Сумма операции в валюте карты"]
            desc = op["Описание операции"]
            card = op["Номер карты"]

            # === плюс/минус суммы ===
            v = float(sum_op.replace("₽", "").replace(" ", "").replace(",", "."))
            if "-" in sum_op:
                total_out += abs(v)
            else:
                total_in += v

            op_time_lines = op_time.split("\n")
            write_off_lines = write_off.split("\n")

            # === перенос описания ===
            desc_lines = []
            words = desc.split(" ")
            line = ""
            dummy = canvas.Canvas(io.BytesIO())
            for w in words:
                test = (line + " " + w).strip()
                if dummy.stringWidth(test, "TINK", 9) <= 100:
                    line = test
                else:
                    desc_lines.append(line)
                    line = w
            if line:
                desc_lines.append(line)

            max_lines = max(
                len(op_time_lines),
                len(write_off_lines),
                len(desc_lines)
            )

            block_h = max_lines * (ROW_H / 1.6)
            text_y = y

            for i_line in range(max_lines):
                t_y = text_y - i_line * (ROW_H / 1.6)

                if i_line < len(op_time_lines):
                    c.drawString(X_OP_TIME, t_y, op_time_lines[i_line])

                if i_line < len(write_off_lines):
                    c.drawString(X_WRITE_OFF, t_y, write_off_lines[i_line])

                # суммы в 1-й строке
                if i_line == 0:
                    draw_with_ruble(c, X_SUM_OP, t_y - 4, sum_op, main_font="TINK", main_size=9)
                    draw_with_ruble(c, X_SUM_CARD, t_y - 4, sum_card, main_font="TINK", main_size=9)
                    c.drawString(X_CARD, t_y, card)

                if i_line < len(desc_lines):
                    c.drawString(X_DESC, t_y, desc_lines[i_line])

            # линия
            y -= block_h
            c.setStrokeColor('#171717')
            c.setLineWidth(1)
            c.line(X_OP_TIME, y + 7, 539.1, y + 7)

            y -= 4

        # номер страницы
        c.setFont("TINK", 8)
        c.drawRightString(570, 25, f"Страница {idx + 1} из {len(chunks) + 1}")
        c.save()

        overlay = fitz.open("pdf", packet.getvalue())
        page.show_pdf_page(page.rect, overlay, 0)

    # === ИТОГОВАЯ СТРАНИЦА ===
    clean = fitz.open(template_path)
    result.insert_pdf(clean, from_page=2, to_page=2)
    last_page = result[-1]

    text_in = f"{total_in:,.2f} ₽".replace(",", " ")
    text_out = f"{total_out:,.2f} ₽".replace(",", " ")

    draw_with_ruble_fitz(last_page, 120, 31, text_in, 9, tink_reg, symb)
    draw_with_ruble_fitz(last_page, 120, 46, text_out, 9, tink_reg, symb)

    result.save(output_path)
    print(f"✅ PDF для TINK готов: {output_path}")
    return output_path


# === Тестовый запуск ===
if __name__ == "__main__":
    data = DataSchema(
        alpha=AlphaSchema(
            date_open='10.10.2025',
            report_date='10.10.2025',
            client='Наебалов Биржов Мошенников',
            address='ОУФМС России по Челябинской \\n обл. в г. Челябинске'),
        tink=TinkSchema(
            date='10.10.2025',
            fio='Наебалов Биржов Мошенников',
            series='4020',
            number='720140',
            date_issue='10.10.2025',
            code='102-321',
            issued_by='ОУФМС России по Челябинской обл. в г. Челябинске',
            address='ОУФМС России по Челябинской обл. в г. Челябинске',
            contract_date='01.01.2000',
            contract_number='HK2371-2394F',
            card_number='1234'
        )
    )

    header_alpha, operations_alpha, header_tink, operations_tink = get_params(
        data_schema=data,
        file_path='p2p.csv'
    )

    # path_alpha = render_alpha_pdf(header_alpha, operations_alpha)
    path_tink = render_tink_pdf(header_tink, operations_tink)
