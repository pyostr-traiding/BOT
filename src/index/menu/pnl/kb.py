from aiogram import types

from service.utils.kb import KBReturn


def kb_pnl() -> KBReturn:
    keyboard = [
        [types.KeyboardButton(text='Общий')],
        [types.KeyboardButton(text='Сегодня')],
        [types.KeyboardButton(text='Недельный')],
    ]
    reply = types.ReplyKeyboardMarkup(
        resize_keyboard=True,
        keyboard=keyboard,
    )
    return KBReturn.from_keyboard(reply)