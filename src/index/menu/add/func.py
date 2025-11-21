import datetime

from aiogram import types, F
from aiogram.fsm.context import FSMContext

from API.actions.api import get_general_analiz
from API.other.user import user_add_permissions
from conf.conf import dp, client
from API.other.schema.user import TGUserSchema
from service.decorators.auth import auth_require, PermissionKeys
from service.decorators.validate import validate_keyboard
from src.index.func import start_menu
from src.index.menu.add.state import AddState
from src.index.menu.analiz.kb import kb_analiz
from src.index.menu.analiz.state import AnalizState


@auth_require([PermissionKeys.MAIN_MENU])
async def add_menu(
        message: types.Message,
        auth_user: TGUserSchema,
        state: FSMContext,
):
    if message.from_user.id not in [
        790285153,
        572982939,
    ]:
        return await client.send_message(
            chat_id=message.from_user.id,
            text='Запрещено.'
        )
    await client.send_message(
        chat_id=message.from_user.id,
        text='Введите ник в формате @username',
        reply_markup=types.ReplyKeyboardRemove()
    )

    await state.set_state(AddState.input_username)

@dp.message(AddState.input_username)
async def add_menu_input(
        message: types.Message,
        auth_user: TGUserSchema,
        state: FSMContext,
):
    if message.from_user.id not in [
        790285153,
        572982939,
    ]:
        return await client.send_message(
            chat_id=message.from_user.id,
            text='Запрещено.'
        )
    res = await user_add_permissions(username=message.text)
    if res == 200:
        await client.send_message(
            chat_id=message.from_user.id,
            text='Успешно выданы права'
        )
        await state.clear()
        return
    if res == 404:
        await client.send_message(
            chat_id=message.from_user.id,
            text='Пользователь не найден в базе'
        )
        await state.clear()
        return

    await client.send_message(
        chat_id=message.from_user.id,
        text='Ошибка запроса'
    )
    await state.clear()
    return
