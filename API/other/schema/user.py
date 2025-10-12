from typing import Optional

from pydantic import BaseModel


class PermissionsSchema(BaseModel):
    main_menu: bool
    glaz_menu: bool
    receipt_menu: bool


class TGUserSchema(BaseModel):
    """
    Схема пользователя
    """
    chat_id: str
    username: Optional[str] = None
    balance: Optional[int] = None
    is_trader: Optional[bool] = False
    permissions: PermissionsSchema