from pydantic import BaseModel
from typing import List


class SettingsBanSchema(BaseModel):
    """
    Схема блокировки
    """
    code: str
    key: str
    value: int
    caption: str
    redis_value: str

class ListSettingsBanSchema(BaseModel):
    """
    Схема списка блокировок
    """
    data: List[SettingsBanSchema]

class UpdateSettingsBanSchema(BaseModel):
    """
    Схема обновления блокировки
    """
    code: str = 'GLOBAL'
    key: str = 'BAN'
    value: int
