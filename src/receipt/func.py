import re
import aiohttp

import src.receipt.kb as kb
from aiogram import types
from aiogram.fsm.context import FSMContext

from API.other.schema.user import TGUserSchema
from conf.conf import dp, client
from conf.settings import settings
from service.decorators.auth import PermissionKeys, auth_require
from src.receipt.state import ReceiptState


@auth_require([PermissionKeys.RECEIPT_MENU])
async def menu_receipt(
        message: types.Message,
        auth_user: TGUserSchema,
        state: FSMContext = None,
        text='Выберите от куда перевод',
):

    await client.send_message(
        chat_id=message.from_user.id,
        text=text,
        reply_markup=kb.kb_banks()
    )
    await state.set_state(ReceiptState.from_bank)

@dp.message(ReceiptState.from_bank)
async def menu_state_bank(
        message: types.Message,
        state: FSMContext = None,
):
    if message.text not in ['Тинк', 'Яндекс', 'Озон']:
        return await client.send_message(
            chat_id=message.from_user.id,
            text='Выберите на клавиатуре',
            reply_markup=kb.kb_banks(),
        )
    await client.send_message(
        chat_id=message.from_user.id,
        text='Выберите куда отправляете',
        reply_markup=kb.kb_to_bank(message.text),
    )
    await state.update_data(from_bank=message.text)
    await state.set_state(ReceiptState.bank)


@dp.message(ReceiptState.bank)
async def menu_state_bank(
        message: types.Message,
        state: FSMContext = None,
):
    if message.text not in ['Сбер', 'Тинк', 'Альфа', 'Райф', 'ОТП', 'Озон']:
        return await client.send_message(
            chat_id=message.from_user.id,
            text='Выберите на клавиатуре',
            reply_markup=kb.kb_banks(),
        )
    await client.send_message(
        chat_id=message.from_user.id,
        text='Введите телефон',
        reply_markup=types.ReplyKeyboardRemove(),
    )
    await state.update_data(bank=message.text)
    await state.set_state(ReceiptState.phone)


def format_phone_number(phone: str):
    # Удаляем всё кроме цифр
    digits = re.sub(r'\D', '', phone)

    # Обрезаем ведущую 8, если есть
    if digits.startswith('8') and len(digits) == 11:
        digits = '7' + digits[1:]
    elif len(digits) == 10:
        digits = '7' + digits

    # Проверяем длину
    if len(digits) != 11 or not digits.startswith('7'):
        return False

    # Форматируем
    return f"+7 ({digits[1:4]}) {digits[4:7]}-{digits[7:9]}-{digits[9:11]}"


@dp.message(ReceiptState.phone)
async def menu_state_phone(
        message: types.Message,
        state: FSMContext = None,
):
    phone_number = format_phone_number(message.text)
    if not phone_number:
        return await client.send_message(
            chat_id=message.from_user.id,
            text='Не верный формат',
            reply_markup=types.ReplyKeyboardRemove(),
        )
    await client.send_message(
        chat_id=message.from_user.id,
        text='Введите сумму перевода',
        reply_markup=types.ReplyKeyboardRemove(),
    )
    await state.update_data(phone=phone_number)
    await state.set_state(ReceiptState.amount)

def is_valid_number_string(s: str) -> bool:
    allowed_chars = set('0123456789., ')
    return all(c in allowed_chars for c in s)

@dp.message(ReceiptState.amount)
async def menu_state_amount(
        message: types.Message,
        state: FSMContext = None,
):
    if not is_valid_number_string(message.text):
        return await client.send_message(
            chat_id=message.from_user.id,
            text='Лишние символы в цифре'
        )
    await client.send_message(
        chat_id=message.from_user.id,
        text=(
            'Введите имя получателя\n'
            'Имя при переводе из Озон Банка не отобразиться'
        ),
        reply_markup=kb.kb_bank_skip_name()
    )
    await state.update_data(amount=message.text)
    await state.set_state(ReceiptState.name)


@dp.message(ReceiptState.name)
async def menu_state_name(
        message: types.Message,
        state: FSMContext = None,
):
    data = await state.get_data()
    name = message.text if message.text != 'Пропустить' else None
    payload = {
            "from_bank": data['from_bank'],
            "bank": data['bank'],
            "tg_id": str(message.from_user.id),
            "phone": data['phone'],
            "name": name,
            "text_1": data['amount'],
    }
    # url = 'http://localhost:8000/api/receipt/'
    url = f'{settings.BASE_API_URL}/receipt/'
    async with aiohttp.ClientSession() as session:
        async with session.post(
                url=url,
                json=payload
        ) as resp:
            if resp.status != 200:
                await client.send_message(
                    chat_id=message.from_user.id,
                    text='Что-то пошло не так.',
                    reply_markup=kb.kb_banks()
                )
    await client.send_message(
        chat_id=message.from_user.id,
        text='Выберите от куда перевод.',
        reply_markup=kb.kb_banks()
    )
    await state.set_state(ReceiptState.from_bank)
