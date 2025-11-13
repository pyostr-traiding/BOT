from aiogram import types


def kb_banks() -> types.ReplyKeyboardMarkup:
    keyboard = [
        [
            types.KeyboardButton(text='Тинк'),
            types.KeyboardButton(text='Яндекс'),
            types.KeyboardButton(text='Озон'),

        ],
    ]
    reply = types.ReplyKeyboardMarkup(
        resize_keyboard=True,
        keyboard=keyboard,
    )
    return reply

def kb_to_bank(
        bank_name: str
) -> types.ReplyKeyboardMarkup:
    keyboard = [
        [
            types.KeyboardButton(text='Тинк'),
            types.KeyboardButton(text='Сбер'),
        ],
        [
            types.KeyboardButton(text='Альфа'),
            types.KeyboardButton(text='Райф'),
        ],
    ]
    if bank_name == 'Тинк':
        keyboard = [
            [
                types.KeyboardButton(text='Тинк'),
                types.KeyboardButton(text='Сбер'),
            ],
            [
                types.KeyboardButton(text='Альфа'),
                types.KeyboardButton(text='Райф'),
            ],
            [
                types.KeyboardButton(text='Озон'),
            ],
        ]
    if bank_name == 'Озон':
        keyboard = [
            [
                types.KeyboardButton(text='Тинк'),
                types.KeyboardButton(text='Сбер'),
            ],
            [
                types.KeyboardButton(text='Альфа'),
                types.KeyboardButton(text='Озон'),
            ],
            [
                types.KeyboardButton(text='ОТП'),
            ],

        ]
    reply = types.ReplyKeyboardMarkup(
        resize_keyboard=True,
        keyboard=keyboard,
    )
    return reply

def kb_bank_skip_name() -> types.ReplyKeyboardMarkup:
    keyboard = [
        [
            types.KeyboardButton(text='Пропустить'),
        ],
    ]
    reply = types.ReplyKeyboardMarkup(
        resize_keyboard=True,
        keyboard=keyboard,
    )
    return reply
