from aiogram import types, F
from aiogram.fsm.context import FSMContext

from API.settings.ban.api import get_settings_ban_list, get_settings_ban, update_settings_ban
from conf.conf import dp, client

from API.other.schema.user import TGUserSchema
from service.decorators.auth import auth_require, PermissionKeys
from service.decorators.validate import validate_keyboard
from service.utils.responses import ErrorResponse
from src.index.func import start_menu

from src.index.menu.settings.ban.kb import kb_settings, kb_settings_ban_list, kb_settings_ban_edit
from src.index.menu.settings.ban.state import SettingsState


@auth_require([PermissionKeys.MAIN_MENU])
@dp.message(F.text == 'Настройки')
async def menu_settings(
        message: types.Message,
        auth_user: TGUserSchema,
        state: FSMContext,
):
    reply = kb_settings()
    await client.send_message(
        chat_id=message.from_user.id,
        text='Выберите раздел',
        reply_markup=reply.reply
    )
    await state.update_data(valid_menu_settings_ban=reply.values)
    await state.set_state(SettingsState.input_choice)

@dp.message(SettingsState.input_choice)
@validate_keyboard('valid_menu_settings_ban')
async def menu_settings_choice(
        message: types.Message,
        auth_user: TGUserSchema,
        state: FSMContext,
        check_back: bool = True,
):
    """
    Получаем раздел настроек
    """
    if check_back and message.text == '<- Назад':
        return await start_menu(
            message=message,
            auth_user=auth_user,
            state=state,
        )

    if message.text == 'Блокировки':
        return await menu_settings_choice_ban(
            message=message,
            auth_user=auth_user,
            state=state,
        )
    if message.text == 'Тикеры':
        return await client.send_message(
            chat_id=message.from_user.id,
            text='Не реализованно'
        )

async def menu_settings_choice_ban(
        message: types.Message,
        auth_user: TGUserSchema,
        state: FSMContext,
):
    """
    Показываем все блокировки
    """
    settings_ban = await get_settings_ban_list()
    if isinstance(settings_ban, ErrorResponse):
        await message.answer(text=settings_ban.error_text(), show_alert=True)

    reply = await kb_settings_ban_list(settings_ban)
    await client.send_message(
        chat_id=message.from_user.id,
        text='Выберите блокировку',
        reply_markup=reply.reply
    )
    await state.update_data(valid_menu_settings_ban_values=reply.values)
    await state.set_state(SettingsState.input_choice_ban)


@dp.message(SettingsState.input_choice_ban)
@validate_keyboard('valid_menu_settings_ban_values')
async def menu_settings_choice(
        message: types.Message,
        auth_user: TGUserSchema,
        state: FSMContext,
        check_back: bool = True,
):
    """
    Получаем выбранную блокировку и показываем подробности
    """
    if check_back and message.text == '<- Назад':
        return await menu_settings(
            message=message,
            auth_user=auth_user,
            state=state,
        )
    code, key = message.text.split('.')
    settings_ban = await get_settings_ban(
        code=code,
        key=key
    )
    if isinstance(settings_ban, ErrorResponse):
        await message.answer(text=settings_ban.error_text(), show_alert=True)

    reply = kb_settings_ban_edit(
        code=code,
        key=key,
    )
    await client.send_message(
        chat_id=message.from_user.id,
        text=(
            f'Тип: {settings_ban.code}\n'
            f'Уровень: {settings_ban.key}\n'
            f'Значение в базе: {settings_ban.value}\n'
            f'Значение в Redis: {settings_ban.redis_value}\n\n'
            f'{settings_ban.caption}\n'
        ),
        reply_markup=reply.reply
    )


@dp.callback_query(lambda m: 'update_ban.' in m.data)
async def menu_settings_ban_edit(
        callback: types.CallbackQuery,
        auth_user: TGUserSchema,
        state: FSMContext,
):
    """
    Запрашиваем новое значние
    """
    action, code, key = callback.data.split('.')
    await state.update_data(edit_blocks=f'{code}.{key}')
    await client.send_message(
        chat_id=callback.message.chat.id,
        text='Введите число',
        reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(SettingsState.input_choice_ban_new_value)

@dp.message(SettingsState.input_choice_ban_new_value)
async def menu_settings_choice(
        message: types.Message,
        auth_user: TGUserSchema,
        state: FSMContext,
        check_back: bool = True,
):
    """
    Получаем новое значение для блокировки
    """
    if not message.text.isdigit():
        return await client.send_message(
            chat_id=message.from_user.id,
            text='Введите число!'
        )
    data = await state.get_data()
    code, key = data['edit_blocks'].split('.')
    settings_ban = await update_settings_ban(
        code=code,
        key=key,
        value=int(message.text)
    )
    if isinstance(settings_ban, ErrorResponse):
        await message.answer(text=settings_ban.error_text(), show_alert=True)

    reply = kb_settings_ban_edit(
        code=code,
        key=key,
    )
    await client.send_message(
        chat_id=message.from_user.id,
        text=(
            f'Успешно изменено!\n\n'
            f'Тип: {settings_ban.code}\n'
            f'Уровень: {settings_ban.key}\n'
            f'Значение в базе: {settings_ban.value}\n'
            f'Значение в Redis: {settings_ban.redis_value}\n\n'
            f'{settings_ban.caption}\n'
        ),
        reply_markup=reply.reply
    )

    await start_menu(
        message=message,
        auth_user=auth_user,
        state=state,
    )