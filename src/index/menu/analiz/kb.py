from aiogram import types

from service.utils.kb import KBReturn


def kb_analiz() -> KBReturn:
    keyboard = [
        [types.KeyboardButton(text='Общая сводка')],
        [types.KeyboardButton(text='<- Назад')],
    ]
    reply = types.ReplyKeyboardMarkup(
        resize_keyboard=True,
        keyboard=keyboard,
    )
    return KBReturn.from_keyboard(reply)