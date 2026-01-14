import os
import uuid

import aiofiles
import aiohttp

from aiogram import types
from aiogram.fsm.context import FSMContext

from API.other.schema.user import TGUserSchema
from API.other.user import user_balance
from conf.conf import dp, client
from service.decorators.auth import auth_require, PermissionKeys
from src.glaz.parse import generate_html
from src.glaz.state import GlazState

@auth_require([PermissionKeys.GLAZ_MENU])
async def glaz_menu(
        message: types.Message,
        auth_user: TGUserSchema,
        state: FSMContext = None,
        text: str = 'Введите строку для поиска\n'
                    'Для поиска по номеру введите формат 79995002211.\n'
                    'Без семерки искать не будет!\n'
):
    balance = await user_balance(
        chat_id=str(message.from_user.id),
    )
    if not balance:
        return await client.send_message(
            chat_id=message.from_user.id,
            text='Ошибка запроса баланса'
        )
    if balance['balance'] <= 0:
        return await client.send_message(
            chat_id=message.from_user.id,
            text=f'Ваш баланс запросов: {balance['balance']}'
        )
    text += f'\n\nВаш баланс запросов: {balance['balance']}'
    await client.send_message(
        chat_id=message.from_user.id,
        text=text,
        reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(GlazState.string_input)

@dp.message(GlazState.string_input)
async def string_input_menu(
        message: types.Message,
        state: FSMContext = None,
):
    balance = await user_balance(
        chat_id=str(message.from_user.id),
        decries=True
    )
    if not balance:
        return await client.send_message(
            chat_id=message.from_user.id,
            text='Ошибка запроса баланса'
        )

    await client.send_message(
        chat_id=message.from_user.id,
        text='Начинаю поиск...',
    )
    url = 'https://api.usersbox.ru/v1/search'
    headers = {
        'Authorization': os.getenv('GLAZ_API_TOKEN')
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(
                url=url,
                headers=headers,
                params={
                    'q': message.text
                }
        ) as resp:
            if resp.status == 200:
                print(resp)
                data = await resp.json()
                if not data['data']['count']:
                    await client.send_message(
                        chat_id=message.from_user.id,
                        text='Ничего не найдено',
                    )
                    await state.clear()
                    return glaz_menu(
                        message,
                        state=state,
                    )
                html_output = generate_html(data)

                # Генерация уникального имени файла
                filename = f"{uuid.uuid4()}.html"
                file_path = f"{filename}"

                # Сохраняем файл
                async with aiofiles.open(file_path, "w", encoding="utf-8") as f:
                    await f.write(html_output)

                # Отправляем файл
                await client.send_document(
                    chat_id=message.chat.id,
                    document=types.FSInputFile(file_path),
                    caption="Результаты поиска"
                )

                # Удаляем файл
                os.remove(file_path)

                await state.clear()
                return await glaz_menu(
                    message,
                    state=state,
                    text='Введите новую строку для поиска'
                )
            else:
                await client.send_message('Ошибка запроса')
                await state.clear()