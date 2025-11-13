from aiogram import types

from API.other.schema.user import TGUserSchema
from src.extract.func import menu_extract
from src.glaz.func import glaz_menu
from src.index.func import start_menu
from src.receipt.func import menu_receipt


async def command_connect(
        message: types.Message,
        auth_user: TGUserSchema,
        state,
):
    """"""
    if message.text == '/receipt':
        return await menu_receipt(
            message=message,
            state=state,
            auth_user=auth_user,
        )
    if message.text == '/search':
        return await glaz_menu(
            message=message,
            state=state,
            auth_user=auth_user,
        )

    if message.text == '/start':
        return await start_menu(
            message=message,
            state=state,
            auth_user=auth_user
        )
    if message.text == '/extract':
        return await menu_extract(
            message=message,
            state=state,
            auth_user=auth_user
        )
