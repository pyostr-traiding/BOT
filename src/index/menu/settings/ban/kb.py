from aiogram import types

from API.settings.ban.schema.ban import ListSettingsBanSchema
from service.utils.kb import KBReturn, chunk_list


def kb_settings() -> KBReturn:
    keyboard = [
        [
            types.KeyboardButton(text='Блокировки'),
            types.KeyboardButton(text='Тикеры')
         ],
        [
            types.KeyboardButton(text='<- Назад'),
        ],
    ]
    reply = types.ReplyKeyboardMarkup(
        resize_keyboard=True,
        keyboard=keyboard,
    )
    return KBReturn.from_keyboard(reply)



async def kb_settings_ban_list(
        data: ListSettingsBanSchema
) -> KBReturn:
    keyboard = chunk_list(
        lst=[types.KeyboardButton(text=f'{i.code}.{i.key}') for i in data.data],
        n=2,
    )
    keyboard.append(
        [
            types.KeyboardButton(text='<- Назад'),
        ]
    )
    reply = types.ReplyKeyboardMarkup(
        resize_keyboard=True,
        keyboard=keyboard,
    )
    return KBReturn.from_keyboard(reply)


def kb_settings_ban_edit(
        code: str,
        key: str,
) -> KBReturn:
    keyboard = [
        [
            types.InlineKeyboardButton(text='Изменить', callback_data=f'update_ban.{code}.{key}'),
        ],
    ]
    reply = types.InlineKeyboardMarkup(
        inline_keyboard=keyboard,
    )
    return KBReturn(reply=reply)