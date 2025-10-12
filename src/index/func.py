from aiogram import types
from aiogram.fsm.context import FSMContext

from API.other.schema.user import TGUserSchema
from conf.conf import client
from service.decorators.auth import auth_require, PermissionKeys
from src.index.kb import kb_index


@auth_require([PermissionKeys.MAIN_MENU])
async def start_menu(
        message: types.Message,
        auth_user: TGUserSchema,
        state: FSMContext,
):
    await state.clear()
    await client.send_message(
        chat_id=message.from_user.id,
        text='Выберите раздел',
        reply_markup=kb_index().reply
    )


