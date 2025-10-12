import datetime

from aiogram import types, F
from aiogram.fsm.context import FSMContext

from API.actions.api import get_general_analiz
from conf.conf import dp, client
from API.other.schema.user import TGUserSchema
from service.decorators.auth import auth_require, PermissionKeys
from service.decorators.validate import validate_keyboard
from src.index.func import start_menu
from src.index.menu.analiz.kb import kb_analiz
from src.index.menu.analiz.state import AnalizState


@auth_require([PermissionKeys.MAIN_MENU])
@dp.message(F.text == 'Аналитика')
async def menu_analiz(
        message: types.Message,
        auth_user: TGUserSchema,
        state: FSMContext,
):
    reply = kb_analiz()
    await client.send_message(
        chat_id=message.from_user.id,
        text='Выберите отчет',
        reply_markup=reply.reply
    )
    await state.update_data(valid_menu_analiz=reply.values)
    await state.set_state(AnalizState.input_choice_action)


@dp.message(AnalizState.input_choice_action)
@validate_keyboard('valid_menu_analiz')
@auth_require([PermissionKeys.MAIN_MENU])
async def menu_analiz_input_choice_action(
        message: types.Message,
        auth_user: TGUserSchema,
        state: FSMContext,
        check_back: bool = True,
):
    """
    Получаем выбранное действие
    """
    if check_back and message.text == '<- Назад':
        return await start_menu(
            message=message,
            auth_user=auth_user,
            state=state,
        )

    result = await get_general_analiz(tg_id=str(message.from_user.id))
    if not result:
        return await client.send_message(
            chat_id=message.from_user.id,
            text='Ошибка запроса',
        )
    await client.send_message(
        chat_id=message.from_user.id,
        text='Запрос отправлен, ожидайте!',
    )
    return await start_menu(
        message=message,
        auth_user=auth_user,
        state=state,
    )