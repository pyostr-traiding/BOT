import datetime

from aiogram import types, F
from aiogram.fsm.context import FSMContext

from API.statistic.pnl.api import get_pnl
from conf.conf import dp, client
from API.other.schema.user import TGUserSchema
from service.decorators.auth import auth_require, PermissionKeys
from service.decorators.validate import validate_keyboard
from service.utils.responses import ErrorResponse
from src.index.menu.pnl.kb import kb_pnl
from src.index.menu.pnl.state import PNLState


@auth_require([PermissionKeys.MAIN_MENU])
@dp.message(F.text == 'P&L')
async def menu_pnl(
        message: types.Message,
        auth_user: TGUserSchema,
        state: FSMContext,
):
    reply = kb_pnl()
    await client.send_message(
        chat_id=message.from_user.id,
        text='Выберите раздел',
        reply_markup=reply.reply
    )
    await state.update_data(valid_menu_pnl=reply.values)
    await state.set_state(PNLState.input_pnl_period)


@dp.message(PNLState.input_pnl_period)
@validate_keyboard('valid_menu_pnl')
@auth_require([PermissionKeys.MAIN_MENU])
async def menu_pnl_input_period(
        message: types.Message,
        auth_user: TGUserSchema,
        state: FSMContext,
):
    """
    Получаем вариант P&L периода
    """
    PNL_period = None
    if message.text == 'Общий':
        PNL_period = 'Общий'
    if message.text == 'Сегодня':
        return await message.answer(
            text='Не реализовано!'
        )
    if message.text == 'Недельный':
        return await message.answer(
            text='Не реализовано!'
        )

    response = await get_pnl(PNL_period=PNL_period)
    if isinstance(response, ErrorResponse):
        return await message.answer(response.error_text())

    now = datetime.datetime.now()
    formatted_date = now.strftime("%d.%m.%Y %H:%M")

    text = (
        f'#PnL {formatted_date}\n\n'
        f'Общий P&L: {response.total:.2f}\n'
        f'Убыток: {response.loss:.2f}\n'
        f'Прибыль: {response.profit:.2f}\n'
    )

    await client.send_message(
        chat_id=message.from_user.id,
        text=text,
    )
