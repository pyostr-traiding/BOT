from functools import wraps
from typing import Callable, List, Optional
from aiogram import types
from API.other.schema.user import TGUserSchema
from conf.conf import client


class PermissionKeys:
    MAIN_MENU = "main_menu"
    GLAZ_MENU = "glaz_menu"
    RECEIPT_MENU = "receipt_menu"


def auth_require(required_permissions: Optional[List[str]] = None):
    """
    Декоратор проверки прав пользователя.
    - required_permissions: список прав, которые нужны для доступа.
    Если пустой список или None, доступ даётся если is_trader=True
    """
    if required_permissions is None:
        required_permissions = []

    def decorator(handler: Callable):
        @wraps(handler)
        async def wrapper(message: types.Message, *args, **kwargs):
            auth_user: TGUserSchema = kwargs.get("auth_user")
            if not auth_user:
                return await client.send_message(
                    chat_id=message.from_user.id,
                    text="Ошибка авторизации! Попробуйте позже."
                )

            # Полный доступ для трейдера, игнорируем права
            if auth_user.is_trader:
                return await handler(message, *args, **kwargs)

            # Проверяем наличие нужных прав для обычного пользователя
            missing_permissions = [
                perm for perm in required_permissions
                if not getattr(auth_user.permissions, perm, False)
            ]

            if missing_permissions:
                return await message.reply(
                    text=f"У вас нет доступа к разделу! Отсутствуют права."
                )
            return await handler(message=message, *args, **kwargs)

        return wrapper
    return decorator
