from aiogram import types

from service.utils.kb import KBReturn


def kb_position(uuid: str) -> KBReturn:
    keyboard = [
        [
            types.InlineKeyboardButton(text='Обновить', callback_data=f'update_pos.{uuid}'),
            types.InlineKeyboardButton(text='Удалить', callback_data=f'delete_pos.{uuid}'),
        ],
    ]
    reply = types.InlineKeyboardMarkup(
        inline_keyboard=keyboard,
    )
    return KBReturn(reply=reply)