from aiogram import types

from service.utils.kb import KBReturn


def kb_index() -> KBReturn:
    keyboard = [
        [
            types.KeyboardButton(text='Позиции/Ордера'),
            types.KeyboardButton(text='Аналитика'),
        ],
        [
            types.KeyboardButton(text='P&L'),
            types.KeyboardButton(text='Настройки'),
        ],
    ]
    reply = types.ReplyKeyboardMarkup(
        resize_keyboard=True,
        keyboard=keyboard,
    )
    return KBReturn(reply=reply)