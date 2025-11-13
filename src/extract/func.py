import os
from pprint import pprint

import boto3
from boto3.resources.base import ServiceResource
from dotenv import load_dotenv

import src.receipt.kb as kb

from aiogram import types
from aiogram.fsm.context import FSMContext

from API.other.schema.user import TGUserSchema
from conf.conf import client, s3_upload, dp
from service.exctract.alpha import render_alpha_pdf, render_tink_pdf
from service.exctract.read_csv import get_params
from service.exctract.scheame import DataSchema, AlphaSchema, TinkSchema
from src.extract.state import ExtractState

load_dotenv()

s3_client: ServiceResource = boto3.resource(
        service_name='s3',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        endpoint_url='https://s3.timeweb.com',
    )

async def menu_extract(
        message: types.Message,
        auth_user: TGUserSchema,
        state: FSMContext = None,
):

    await client.send_message(
        chat_id=message.chat.id,
        text='Загрузите csv файл с биржи',
        reply_markup=types.ReplyKeyboardRemove()
    )

    await state.set_state(ExtractState.input_file)

@dp.message(ExtractState.input_file)
async def menu_extract_input_file(
        message: types.Message,
        auth_user: TGUserSchema,
        state: FSMContext = None,
):
    # проверяем, что пользователь прислал файл
    if not message.document:
        await message.answer("Отправьте именно CSV файл.")
        return

    document: types.Document = message.document

    # проверка расширения
    if not document.file_name.lower().endswith(".csv"):
        await message.answer("Нужен файл в формате CSV. Попробуйте снова.")
        return

        # получаем file_id → file_path
    file_info = await client.get_file(document.file_id)
    file_path = file_info.file_path

    # создаём директорию, если нет
    save_dir = "service/exctract/csv"
    os.makedirs(save_dir, exist_ok=True)

    # путь сохранения
    local_path = os.path.join(save_dir, document.file_name)

    # скачиваем файл
    await client.download_file(file_path, local_path)

    # выводим путь в консоль
    print(f"CSV FILE SAVED: {local_path}")
    await state.update_data(local_path=local_path)
    text_filled = (
        "Для переноса в адресе теста используйте \\n \n\n"
        "Пример заполнения:\n\n"
        "Дата_выдачи=12.02.2025\n"
        "Дата_формирования=12.02.2026\n"
        "ФИО=Наебалов Биржов Мошенников\n\n"
        "Регистрация=454090, Россия, г. Челябинск, ул. Свободы, д. 77, кв. 12\n\n"
        "Дата_рождения=10.10.2001\n"
        "ФИО=Наебалов Биржов Мошенников\n"
        "Паспорт_серия=4020\n"
        "Паспорт_номер=700130\n"
        "Паспорт_дата_выдачи=21.03.2015\n"
        "Паспорт_код_подразделения=780-642\n"
        "Паспорт_кем_выдан=ОУФМС России по Челябинской обл. в г. Челябинске\n"
        "Паспорт_Регистрация=454090, Россия, г. Челябинск,\\n ул. Свободы, д. 77, кв. 12\n"
        "Дата_заключения_договора=10.02.2024\n"
        "Код_договора=ТИНК-0014578\n"
        "Номер_карты=0011\n\n\n"
        "Пустой шаблон далее..."
    )

    text_template = (
        "Дата_выдачи=\n"
        "Дата_формирования=\n"
        "ФИО=\n"
        "Регистрация=\n\n"
        "Дата_рождения=\n"
        "ФИО=\n"
        "Паспорт_серия=\n"
        "Паспорт_номер=\n"
        "Паспорт_дата_выдачи=\n"
        "Паспорт_код_подразделения=\n"
        "Паспорт_кем_выдан=\n"
        "Паспорт_Регистрация=\n"
        "Дата_заключения_договора=\n"
        "Код_договора=\n"
        "Номер_карты=\n"
    )

    await client.send_message(
        chat_id=message.from_user.id,
        text=text_filled,
    )
    await client.send_message(
        chat_id=message.from_user.id,
        text=text_template,
    )
    await state.set_state(ExtractState.input_text)




@dp.message(ExtractState.input_text)
async def menu_extract_input(
        message: types.Message,
        auth_user: TGUserSchema,
        state: FSMContext = None,
):
    def parse_input_text(text: str) -> DataSchema:
        data = {}
        for line in text.split("\n"):
            if "=" in line:
                key, value = line.split("=", 1)
                data[key.strip()] = value.strip()

        alpha = AlphaSchema(
            date_open=data.get("Дата_выдачи"),
            report_date=data.get("Дата_формирования"),
            client=data.get("ФИО"),
            address=data.get("Регистрация"),
        )

        tink = TinkSchema(
            date=data.get("Дата_рождения"),
            fio=data.get("ФИО"),
            series=data.get("Паспорт_серия"),
            number=data.get("Паспорт_номер"),
            date_issue=data.get("Паспорт_дата_выдачи"),
            code=data.get("Паспорт_код_подразделения"),
            issued_by=data.get("Паспорт_кем_выдан"),
            address=data.get("Паспорт_Регистрация"),
            contract_date=data.get("Дата_заключения_договора"),
            contract_number=data.get("Код_договора"),
            card_number=data.get("Номер_карты"),
        )

        return DataSchema(alpha=alpha, tink=tink)
    try:
        data_schema = parse_input_text(message.text)
    except Exception as e:
        await message.answer(f"Ошибка парсинга: {e}")
        return
    await client.send_message(
        chat_id=message.from_user.id,
        text='Создаем файлы...'
    )
    data = await state.get_data()
    # дальше — твоя логика
    print(data_schema)
    header_alpha, operations_alpha, header_tink, operations_tink = get_params(
        data_schema=data_schema,
        file_path=data['local_path']
    )
    path_alpha = render_alpha_pdf(header_alpha, operations_alpha)
    path_tink = render_tink_pdf(header_tink, operations_tink)


    file_alpha_input = types.FSInputFile(path_alpha)
    await client.send_document(
        chat_id=message.chat.id,
        document=file_alpha_input
    )

    file_alpha_tink = types.FSInputFile(path_tink)
    await client.send_document(
        chat_id=message.chat.id,
        document=file_alpha_tink
    )
    os.remove(path_alpha)
    os.remove(path_tink)
    os.remove(data['local_path'])

    await state.clear()

