# new_pos
from datetime import datetime

from aiogram import types
from aiogram.fsm.context import FSMContext

from API.other.schema.user import TGUserSchema
from API.positions.positions.api import get_position
from API.positions.positions.schema.position import PositionSchema
from conf.conf import dp, client
from service.utils.date import format_datetime
from service.utils.responses import ErrorResponse
from src.callbacks.positions.kb import kb_position

def get_position_text(
        position: PositionSchema,
) -> str:
    """
    Получить текст позиции
    """
    side = 'Лонг' if position.side == 'buy' else 'Шорт'
    is_test = '✅' if position.is_test else '❌'
    try:
        usdt = round(float(position.qty) * float(position.price), 2)
    except ValueError:
        usdt = 'Ошибка'

    text = (
        f'<code>{position.uuid}</code>\n'
        f'\n'
        f'Создан: {format_datetime(position.create_on)}\n'
        f'Тестовый: {is_test}\n'
        f'\n'
        f'Статус: {position.status}\n'
        f'Тикер: {position.symbol_name}\n'
        f'Категория: {position.category}\n'
        f'Тип: {position.orderType}\n'
        f'\n'
        f'Сторона: {side}\n'
        f'Сумма: {usdt} USDT\n'
        f'Кол-во: {position.qty}\n'
        f'Цена: {position.price}\n'
        f'\n'
        f'Тейк: {position.takeProfit}\n'
        f'Стоп: {position.stopLoss}\n'
        f'\n'
        f'Свеча: {position.kline_ms}\n'
        f'Сообщение: {format_datetime(str(datetime.now()))}\n'
    )
    return text

@dp.callback_query(lambda m: 'new_pos.' in m.data)
async def menu_position_show_info(
        callback: types.CallbackQuery,
        auth_user: TGUserSchema,
        state: FSMContext,
):
    """
    Запрос информации по позиции
    """
    uuid: str = callback.data.split('.')[-1]
    response = await get_position(uuid=uuid)

    if isinstance(response, ErrorResponse):
        await callback.answer(text=response.error_text(), show_alert=True)


    reply = kb_position(response.uuid)

    await client.send_message(
        chat_id=callback.from_user.id,
        text=get_position_text(response),
        reply_markup=reply.reply,
    )


@dp.callback_query(lambda m: 'update_pos.' in m.data)
async def menu_position_update_info(
        callback: types.CallbackQuery,
        auth_user: TGUserSchema,
        state: FSMContext,
):
    """
    Обновить информацию о позиции
    """
    uuid: str = callback.data.split('.')[-1]
    response = await get_position(uuid=uuid)

    if isinstance(response, ErrorResponse):
        await callback.answer(text=response.error_text(), show_alert=True)

    reply = kb_position(response.uuid)

    await client.edit_message_text(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        text=get_position_text(response),
        reply_markup=reply.reply,
    )


@dp.callback_query(lambda m: 'delete_pos.' in m.data)
async def menu_position_update_info(
        callback: types.CallbackQuery,
        auth_user: TGUserSchema,
        state: FSMContext,
):
    """
    Удалить позицию
    """
    uuid: str = callback.data.split('.')[-1]

    await callback.answer(
        text='Удаление не реализовано!',
        show_alert=True,
    )